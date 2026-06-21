# Draw Structure Engine Specification

> **Source**: pyQalculate `qalculate-gtk` (`src/callbacks.cc`, `src/resultview.cc`)
> **Purpose**: Complete technical specification of the draw_structure rendering engine that converts `MathStructure` trees into `cairo_surface_t` images for display in the result view. Includes a Python/tkinter implementation blueprint.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Key Function Signature](#2-key-function-signature)
3. [Rendering Pipeline](#3-rendering-pipeline)
4. [Auto-Scaling Algorithm](#4-auto-scaling-algorithm)
5. [Format Handling](#5-format-handling)
6. [Parentheses Logic](#6-parentheses-logic)
7. [Color Coding](#7-color-coding)
8. [Binary Grouping](#8-binary-grouping)
9. [Integration with Result View](#9-integration-with-result-view)
10. [Python/Tkinter Implementation Specification](#10opythontkinter-implementation-specification)

---

## 1. Overview

The draw_structure engine is a recursive tree renderer. Given a `MathStructure` (the parsed and evaluated result), it produces a `cairo_surface_t` (or a series of draw calls) that renders the mathematical expression with proper typography: fractions with horizontal bars, superscripts for exponents, radical signs for roots, matrix brackets, and correctly sized parentheses.

The engine does NOT use font-based math rendering (like MathJax). Instead, it draws each element positionally, computing bounding boxes and stacking elements vertically (for fractions, superscripts) or horizontally (for terms, products).

Key source files:
- `src/callbacks.cc` — `draw_result`, `draw_result_pre`, `draw_result_finalize`
- `src/resultview.cc` — `on_resultview_draw`, cairo rendering callbacks

---

## 2. Key Function Signature

```c
void draw_structure(
    MathStructure *mps,
    cairo_t *cr,                    // Cairo context to draw into
    gint *x_offset,                 // Current x position (updated as drawing proceeds)
    gint *y_offset,                 // Current y baseline (updated for vertical stacking)
    gint *w,                        // Output: total width of drawn structure
    gint *h,                        // Output: total height of drawn structure
    gint *yw,                       // Output: y offset for superscripts/subscripts
    gint *yih,                      // Output: y offset for fraction numerators
    gint max_width,                 // Maximum available width before wrapping
    gint top_y,                     // Top y coordinate of the drawing area
    PangoLayout *layout,            // Shared PangoLayout for text measurement
    bool &hidden,                   // Whether the element should be hidden
    int scale_n,                    // Current auto-scale level (0-3)
    bool register_index = false,    // Whether to register hit-test indices
    int *point = NULL               // For binary grouping hit-testing
);
```

### 2.1 Parameters Explained

| Parameter | Purpose |
|---|---|
| `mps` | The MathStructure node to render |
| `cr` | Cairo drawing context |
| `x_offset` | Horizontal cursor; updated as elements are drawn left-to-right |
| `y_offset` | Vertical baseline; used for stacking fractions, superscripts |
| `w`, `h` | Total bounding box of the rendered element |
| `yw` | Height above baseline (for superscripts to attach to) |
| `yih` | Height of numerator section in fractions |
| `max_width` | Before rendering, check if element exceeds this width; if so, trigger auto-scale |
| `top_y` | Y origin for the entire result |
| `layout` | Reusable PangoLayout for measuring/drawing text strings |
| `hidden` | Set true if the element is empty or should not render |
| `scale_n` | Auto-scale level: 0 = full size, 1-3 = progressively smaller |
| `register_index` | Whether to store bounding boxes for hit-testing (binary grouping click) |
| `point` | Pointer to the digit-grouping hit-test index array |

---

## 3. Rendering Pipeline

The full rendering pipeline from parse to screen:

### 3.1 `draw_result_pre()`

Called before rendering. Prepares the cairo surface and computes the initial bounding box.

```
1. Create or clear cairo_surface_t
2. Set up cairo context with antialiasing
3. Set font options (hinting, subpixel rendering)
4. Initialize x_offset = 0, y_offset = top_y
5. Call draw_structure(mps, ...) for the root MathStructure
6. Store total w, h for centering
```

### 3.2 `draw_result()`

The main entry point. Calls `draw_result_pre()`, then `draw_result_finalize()`.

```
draw_result(mps, cr, top_y):
    draw_result_pre(mps, cr, top_y)
    draw_result_finalize(cr, total_w, total_h)
```

### 3.3 `draw_result_finalize()`

Post-rendering adjustments:

```
1. Center the result horizontally if total_w < max_width
2. Apply vertical centering if total_h < available_height
3. Handle right-to-left layout if needed
4. Flush cairo operations: cairo_surface_flush(surface)
```

### 3.4 `on_resultview_draw()`

GTK draw callback for the result view widget. Called by GTK when the widget needs painting.

```
on_resultview_draw(widget, cr, user_data):
    1. Get the allocated size
    2. If result_structure is not NULL:
        draw_result(result_structure, cr, top_y)
    3. If displaying error: draw error text in red
    4. If result is empty: draw placeholder or nothing
    5. Return TRUE (handled)
```

### 3.5 Pipeline Diagram

```
User types expression
    → parse()
    → calculate()
    → result MathStructure ready
    → on_resultview_draw() triggered (GTK expose event)
        → draw_result_pre()
            → draw_structure(root)  [recursive]
                → for each child: draw_structure(child)
                → compute bounding boxes
                → draw to cairo surface
        → draw_result_finalize()
            → center, flush
        → GTK displays the cairo surface
```

---

## 4. Auto-Scaling Algorithm

When the result is too wide for the display area, the engine automatically reduces font size through 4 scale levels.

### 4.1 Scale Levels

| `scale_n` | Scale Factor | Font Size (base 20pt) | When Used |
|---|---|---|---|
| 0 | 1.0 | 20pt | Default, fits within max_width |
| 1 | 0.85 | 17pt | First overflow: result wider than max_width |
| 2 | 0.75 | 15pt | Still too wide after scale 1 |
| 3 | 0.65 | 13pt | Maximum reduction; if still too wide, horizontal scroll is enabled |

### 4.2 Scaling Logic

```c
void draw_result_pre(MathStructure *mps, cairo_t *cr, gint top_y) {
    gint x = 0, y = top_y, w = 0, h = 0;
    gint yw = 0, yih = 0;
    gint max_w = result_view_width;
    bool hidden = false;

    // First pass: measure without drawing (dry run)
    for(int scale = 0; scale <= 3; scale++) {
        x = 0;
        draw_structure(mps, cr, &x, &y, &w, &h, &yw, &yih,
                        max_w, top_y, layout, hidden, scale);
        if(w <= max_w) break;  // fits at this scale
    }

    // Second pass: actual drawing at the chosen scale
    x = 0;
    y = top_y;
    draw_structure(mps, cr, &x, &y, &w, &h, &yw, &yih,
                    max_w, top_y, layout, hidden, chosen_scale, true);
}
```

### 4.3 Scale Application

All text sizes, spacing, and line widths are multiplied by the scale factor:

```
effective_font_size = base_font_size * scale_factor
effective_line_width = base_line_width * scale_factor
effective_spacing = base_spacing * scale_factor
```

---

## 5. Format Handling

Each MathStructure type has its own rendering logic inside `draw_structure()`:

### 5.1 Numbers

```
Number structure:
  1. Convert to display string based on current base (decimal, hex, oct, bin)
  2. Apply digit grouping (see Binary Grouping section)
  3. Draw text using PangoLayout
  4. For approximate results, append "~" or use italic font
  5. Special: repeating decimals shown with vinculum (overline)
```

### 5.2 Fractions

```
Fraction (num / den):
  1. Render numerator above, denominator below
  2. Draw horizontal fraction bar between them
  3. Bar width = max(numerator_width, denominator_width) + padding
  4. Vertical spacing: numerator above bar, bar in middle, denominator below
  5. y_offset adjusts: numerator.y = bar_y - numerator_height - gap
                          bar.y = bar_y
                          denominator.y = bar_y + gap
  6. Total height = numerator_height + bar_thickness + denominator_height + 2*gap
  7. For simple fractions (small numerator and denominator), consider inline format: "1/2"
```

### 5.3 Powers / Superscripts

```
Power (base ^ exponent):
  1. Render base at normal position
  2. Render exponent at superscript position:
     exp_x = base_x + base_width + superscript_offset_x
     exp_y = base_y - superscript_offset_y (above baseline)
  3. Exponent font size = base_font_size * 0.7
  4. Total width = base_width + superscript_offset_x + exponent_width
  5. Total height = max(base_height, exponent_y + exponent_height)
  6. Special: ² and ³ use Unicode superscript glyphs at full size
```

### 5.4 Root Signs (Radicals)

```
Square root:
  1. Draw radical sign (√) on the left
  2. Draw vinculum (horizontal bar) extending over the radicand
  3. Render radicand below the vinculum
  4. Radical sign height = radicand_height + descender
  5. Vinculum width = radicand_width + padding
  6. Tick mark at bottom-left of radical sign

nth root:
  1. Same as square root but with index number in the "notch"
  2. Index positioned at top-left of radical sign
  3. Index font size = base_font_size * 0.7
```

### 5.5 Matrices

```
Matrix:
  1. Render each element in a grid
  2. Column widths = max(element_width) per column
  3. Row heights = max(element_height) per row
  4. Draw matrix brackets on left and right:
     - Square brackets: vertical bars with small horizontal caps
     - Parentheses: curved lines
     - Pipe: single vertical line (determinant)
  5. Bracket height = total_matrix_height + vertical_padding
  6. Horizontal spacing between columns = consistent gap
  7. Semicolons in source separate columns, newlines separate rows
```

### 5.6 Functions

```
Function call (sin, log, etc.):
  1. Draw function name in roman (upright) font
  2. Draw opening parenthesis
  3. Render each argument, separated by commas
  4. Draw closing parenthesis
  5. Parentheses scale to match argument height (see Parentheses Logic)
  6. Special functions: "ln" uses italic "l" + roman "n"; "log" uses subscript base
```

### 5.7 Multiplication

```
Multiplication:
  1. Implicit multiplication (juxtaposition): no symbol, just spacing
     - e.g., "2x" is rendered as "2x" with a thin space
  2. Explicit multiplication: draw "·" (middle dot) or "×" (cross)
  3. Cross product: draw "×" with appropriate spacing
  4. Dot product: draw "·" at baseline
  5. Asterisk: draw "*" character
```

### 5.8 Addition and Subtraction

```
Addition/Subtraction:
  1. Render terms separated by "+" or "-" operators
  2. Operator spacing: thin space on each side
  3. Negative terms: "-" sign, no space between "-" and the number
  4. All terms share the same baseline
  5. Total width = sum of all term widths + operator widths + spacing
```

### 5.9 Comparisons

```
Comparison (==, <, >, <=, >=, !=):
  1. Render left side
  2. Draw comparison operator
  3. Render right side
  4. Same spacing rules as addition operators
  5. Unicode symbols used: ≤, ≥, ≠
```

### 5.10 Units

```
Unit:
  1. Draw unit name in roman font
  2. If unit has an exponent: draw superscript after unit name
  3. Unit conversion: draw "→" arrow followed by target unit
  4. Multiplication between number and unit: thin space
  5. Division in units: draw horizontal fraction bar or "/" separator
```

### 5.11 Variables

```
Variable:
  1. Draw variable name in italic font (math convention)
  2. Special variables: π, e, i drawn in their Unicode form
  3. Named constants (c, g, h) also italic
  4. User-defined variables: italic name
```

---

## 6. Parentheses Logic

### 6.1 When to Draw Parentheses

Parentheses are drawn in these cases:

| Case | Reason |
|---|---|
| Function arguments | Always: `f(x)` |
| Grouped subexpressions | When the MathStructure has explicit parentheses |
| Nested fractions in numerator/denominator | To clarify precedence |
| Matrix delimiters | Always: `[1 2; 3 4]` |
| Absolute value | Pipe characters `|x|` |

### 6.2 How to Draw

```
Parenthesis rendering:
  1. Measure the height of the content inside
  2. If content height > single-line height:
     - Scale the parenthesis glyph vertically to match content height
     - Use 3 segments: top cap, vertical stem, bottom cap
  3. If content height <= single-line height:
     - Use standard glyph from font
  4. Horizontal padding inside parentheses = font_size * 0.15
  5. Drawing order: left paren, content, right paren
```

### 6.3 Special Bracket Types

| Type | Glyph | Height Behavior |
|---|---|---|
| Round `()` | `(` `)` | Stretches to content height |
| Square `[]` | `[` `]` | Stretches to content height |
| Curly `{}` | `{` `}` | Stretches; middle bump at center |
| Angle `⟨⟩` | `⟨` `⟩` | Stretches; pointed at center |
| Absolute `\|x\|` | `\|` `\|` | Stretches; simple vertical bars |
| Floor `⌊x⌋` | `⌊` `⌋` | Stretches; caps at bottom only |
| Ceiling `⌈x⌉` | `⌈` `⌉` | Stretches; caps at top only |

---

## 7. Color Coding

### 7.1 Single Color Policy

The draw_structure engine uses a **single color** for all rendered elements. There is no per-element coloring (no colored operators, no colored variables, no colored units). Everything is drawn in the current foreground color (typically black on light themes, white on dark themes).

```c
// All drawing uses the same color
cairo_set_source_rgb(cr, fg_r, fg_g, fg_b);
// or from CSS theme:
GdkRGBA fg_color;
gtk_widget_get_style_context(result_view);
gtk_style_context_get_color(context, GTK_STATE_NORMAL, &fg_color);
cairo_set_source_rgba(cr, fg_color.red, fg_color.green,
                       fg_color.blue, fg_color.alpha);
```

### 7.2 Exceptions

The only color variations:
- **Error text**: Red foreground for error messages in the result view.
- **Approximate results**: Some implementations use a slightly different shade or italic style, but not a different color.
- **Hyperlinks** (if present): Blue for clickable URLs in help text.

---

## 8. Binary Grouping

### 8.1 Digit Grouping

Numbers are rendered with digit grouping separators (spaces, commas, or dots depending on locale):

```
1234567.89  →  1 234 567.89  (locale: space grouping)
1234567.89  →  1,234,567.89  (locale: comma grouping)
1234567.89  →  1.234.567,89  (locale: German)
```

### 8.2 Implementation

```c
void draw_number_with_grouping(cairo_t *cr, const gchar *number_str,
                                gint *x, gint y, PangoLayout *layout) {
    // Insert grouping characters every 3 digits (or per locale)
    gchar *grouped = format_with_grouping(number_str, grouping_char);

    // For hit-testing: store bounding boxes of each digit group
    if(register_index) {
        // Store x ranges for each group of 3 digits
        // This allows clicking on a digit group to highlight it
        for each group:
            store_group_hitbox(group_start_x, group_end_x, y, y + height);
    }

    // Draw the grouped number
    pango_layout_set_text(layout, grouped, -1);
    cairo_move_to(cr, *x, y);
    pango_cairo_show_layout(cr, layout);
    *x += pango_layout_get_pixel_size(layout, NULL, NULL);

    g_free(grouped);
}
```

### 8.3 Hit Testing

When `register_index` is true, the engine stores bounding rectangles for each digit group. These are used when the user clicks on a number in the result view to highlight or interact with specific digit groups (e.g., for precision inspection).

```
Hit test structure:
  struct digit_group {
      gint x_start;
      gint x_end;
      gint y_start;
      gint y_end;
      gint digit_start_index;  // index into the number string
      gint digit_end_index;
  };
```

---

## 9. Integration with Result View

### 9.1 Result View Widget

The result view is a `GtkDrawingArea` (or custom widget) that:
- Receives the `draw` signal → calls `on_resultview_draw()`
- Stores the current `MathStructure *result_structure`
- Handles mouse clicks on the result (delegating to hit-test data)
- Supports context menu (copy as text, copy as image, copy as LaTeX)

### 9.2 Calculator Integration

```
Calculator.calculate(expression)
    → returns MathStructure *result
    → stored as result_structure
    → triggers result view redraw:
        gtk_widget_queue_draw(result_view)
    → on_resultview_draw() called by GTK
        → draw_result(result_structure, cr, top_y)
```

### 9.3 Resize Handling

When the result view is resized (window resize):
1. `on_resultview_draw()` is called with the new allocation.
2. `draw_result_pre()` recomputes auto-scaling for the new width.
3. The result is re-rendered at the appropriate scale.

---

## 10. Python/Tkinter Implementation Specification

### 10.1 Architecture

```python
class DrawStructure:
    """Recursive renderer: MathStructure → tkinter Canvas operations"""

    def __init__(self, canvas: tk.Canvas, base_font_size: int = 20):
        self.canvas = canvas
        self.base_font_size = base_font_size
        self.scale_factor = 1.0
        self.scale_level = 0  # 0-3
        self.fg_color = "#000000"
        self.hit_boxes = []  # for binary grouping click detection

    @property
    def font_size(self):
        return int(self.base_font_size * self.scale_factor)

    @property
    def small_font_size(self):
        return int(self.font_size * 0.7)
```

### 10.2 Font Tiers

```python
FONT_TIERS = {
    "normal":   lambda s: ("Georgia", s),       # serif for numbers, operators
    "italic":   lambda s: ("Georgia", s, "italic"),  # variables
    "roman":    lambda s: ("Arial", s),          # function names, units
    "small":    lambda s: ("Georgia", int(s * 0.7)),  # exponents, indices
    "tiny":     lambda s: ("Georgia", int(s * 0.5)),  # nested superscripts
}
```

### 10.3 Compositing Helpers

```python
class CompositingHelper:
    """Manages bounding-box arithmetic for recursive element placement."""

    @staticmethod
    def measure_fraction(num_bbox, den_bbox, bar_thickness=2, gap=4):
        """Returns total bbox for a fraction."""
        w = max(num_bbox[2], den_bbox[2]) + 8  # padding
        h = num_bbox[3] + bar_thickness + den_bbox[3] + 2 * gap
        return (0, 0, w, h)

    @staticmethod
    def measure_superscript(base_bbox, exp_bbox, offset_x=2, offset_y_ratio=0.35):
        """Returns total bbox for base^exponent."""
        exp_y_offset = -int(base_bbox[3] * offset_y_ratio)
        w = base_bbox[2] + offset_x + exp_bbox[2]
        h = max(base_bbox[3], abs(exp_y_offset) + exp_bbox[3])
        return (0, 0, w, h)

    @staticmethod
    def measure_root(radicand_bbox, index_bbox=None, tick_size=8):
        """Returns total bbox for a radical."""
        vinculum_overhang = 4
        w = tick_size + vinculum_overhang + radicand_bbox[2] + vinculum_overhang
        h = radicand_bbox[3] + tick_size
        if index_bbox:
            w += index_bbox[2]
            h = max(h, index_bbox[3] + radicand_bbox[3])
        return (0, 0, w, h)

    @staticmethod
    def measure_matrix(elements, cols, rows, col_gap=8, row_gap=4, bracket_overhead=12):
        """Returns total bbox for a matrix."""
        col_widths = [max(elements[r * cols + c][2] for r in range(rows))
                      for c in range(cols)]
        row_heights = [max(elements[r * cols + c][3] for c in range(cols))
                       for r in range(rows)]
        w = sum(col_widths) + (cols - 1) * col_gap + 2 * bracket_overhead
        h = sum(row_heights) + (rows - 1) * row_gap
        return (0, 0, w, h)
```

### 10.4 Canvas Drawing Functions

```python
def draw_fraction(self, num_node, den_node, x, y):
    """Draw a fraction on the canvas."""
    num_bbox = self._measure(num_node)
    den_bbox = self._measure(den_node)
    bar_w = max(num_bbox[2], den_bbox[2]) + 8
    bar_y = y + num_bbox[3] + self.gap

    # Draw numerator
    self._draw(num_node, x + (bar_w - num_bbox[2]) // 2, y)

    # Draw bar
    self.canvas.create_line(
        x, bar_y, x + bar_w, bar_y,
        fill=self.fg_color, width=max(1, int(2 * self.scale_factor))
    )

    # Draw denominator
    self._draw(den_node, x + (bar_w - den_bbox[2]) // 2,
               bar_y + self.gap + 1)

    return (x, y, bar_w, num_bbox[3] + self.gap + 1 + self.gap + den_bbox[3])


def draw_superscript(self, base_node, exp_node, x, y):
    """Draw base^exponent on the canvas."""
    base_bbox = self._draw(base_node, x, y)

    exp_x = x + base_bbox[2] + int(2 * self.scale_factor)
    exp_y = y - int(base_bbox[3] * 0.35)
    exp_bbox = self._draw(exp_node, exp_x, exp_y, font_tier="small")

    total_w = exp_x + exp_bbox[2] - x
    total_h = max(base_bbox[3], y - exp_y + exp_bbox[3])
    return (x, y, total_w, total_h)


def draw_radical(self, radicand_node, index_node=None, x, y):
    """Draw a square root or nth root."""
    rad_bbox = self._measure(radicand_node)
    tick = int(8 * self.scale_factor)

    # Draw radical sign (left tick + ascending stroke)
    sign_bottom = y + rad_bbox[3]
    sign_top = y - tick // 2
    self.canvas.create_line(
        x, sign_bottom, x + tick, sign_bottom,
        x + tick // 2, sign_top,
        fill=self.fg_color, width=max(1, int(1.5 * self.scale_factor))
    )

    # Draw vinculum
    vinc_x = x + tick
    vinc_w = rad_bbox[2] + int(4 * self.scale_factor)
    vinc_y = sign_top
    self.canvas.create_line(
        vinc_x, vinc_y, vinc_x + vinc_w, vinc_y,
        fill=self.fg_color, width=max(1, int(1.5 * self.scale_factor))
    )

    # Draw radicand
    self._draw(radicand_node, vinc_x + int(2 * self.scale_factor), vinc_y + int(2 * self.scale_factor))

    # Draw index (if nth root)
    if index_node:
        idx_bbox = self._measure(index_node)
        self._draw(index_node, x + 1, sign_top - idx_bbox[3], font_tier="small")

    return (x, y, tick + vinc_w, rad_bbox[3] + tick)


def draw_parentheses(self, content_node, x, y, left_char="(", right_char=")"):
    """Draw content wrapped in parentheses."""
    content_bbox = self._measure(content_node)
    pad = int(self.font_size * 0.15)

    # Draw left paren
    self.canvas.create_text(
        x, y + content_bbox[3] // 2,
        text=left_char, font=FONT_TIERS["normal"](self.font_size),
        fill=self.fg_color, anchor="center"
    )

    # Draw content
    content_x = x + int(self.font_size * 0.4)
    self._draw(content_node, content_x, y)

    # Draw right paren
    right_x = content_x + content_bbox[2] + int(self.font_size * 0.4)
    self.canvas.create_text(
        right_x, y + content_bbox[3] // 2,
        text=right_char, font=FONT_TIERS["normal"](self.font_size),
        fill=self.fg_color, anchor="center"
    )

    return (x, y, right_x + int(self.font_size * 0.4) - x, content_bbox[3])
```

### 10.5 Auto-Scaling on Canvas

```python
def render(self, mstructure, max_width=None):
    """Render a MathStructure to the canvas with auto-scaling."""
    if max_width is None:
        max_width = self.canvas.winfo_width()

    # Try each scale level
    for level in range(4):
        self.scale_level = level
        self.scale_factor = [1.0, 0.85, 0.75, 0.65][level]

        bbox = self._measure(mstructure)
        if bbox[2] <= max_width:
            break

    # Clear canvas
    self.canvas.delete("all")

    # Center horizontally
    x_offset = max(0, (max_width - bbox[2]) // 2)
    self._draw(mstructure, x_offset, 10)
```

### 10.6 Text Drawing with Grouping

```python
def draw_number(self, number_str, x, y):
    """Draw a number with digit grouping."""
    grouped = self._apply_grouping(number_str)

    item = self.canvas.create_text(
        x, y, text=grouped,
        font=FONT_TIERS["normal"](self.font_size),
        fill=self.fg_color, anchor="nw"
    )

    bbox = self.canvas.bbox(item)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]

    if self.register_hits:
        self.hit_boxes.append({
            "x_start": x, "x_end": x + w,
            "y_start": y, "y_end": y + h,
            "text": number_str
        })

    return (x, y, w, h)

def _apply_grouping(self, s):
    """Insert locale-appropriate digit grouping."""
    # Simple: space every 3 digits from the right
    parts = s.split(".")
    int_part = parts[0]
    grouped = ""
    for i, c in enumerate(reversed(int_part)):
        if i > 0 and i % 3 == 0:
            grouped = " " + grouped
        grouped = c + grouped
    if len(parts) > 1:
        grouped += "." + parts[1]
    return grouped
```

---

*End of Draw Structure Engine Specification*
