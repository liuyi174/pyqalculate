# Expression Status Bar Specification

> **Source**: pyQalculate `qalculate-gtk` (`src/callbacks.cc`, `src/interface.cc`)
> **Purpose**: Complete technical specification of the expression status bar, the two-part horizontal strip below the expression entry that shows function hints, parse status, error messages, and mode indicators.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Key State Variables](#2-key-state-variables)
3. [Display Logic](#3-display-logic)
4. [Function Argument Hints](#4-function-argument-hints)
5. [Error Display](#5-error-display)
6. [Mode Indicators](#6-mode-indicators)
7. [Integration Points](#7-integration-points)
8. [Tkinter Implementation Specification](#8-tkinter-implementation-specification)

---

## 1. Overview

The expression status bar sits directly below the expression entry widget. It is split into two visual regions:

- **Left side**: Textual status messages (function hints, parse status, error descriptions, current result preview).
- **Right side**: Mode indicator badges showing calculator state (exact/approx mode, RPN/CHN mode, base, angle unit, precision, disabled features).

The status bar is a `GtkEventBox` containing a `GtkLabel` (left) and a horizontal box of `GtkLabel` badges (right). It updates in real time as the user types.

---

## 2. Key State Variables

| Variable | Type | Description |
|---|---|---|
| `current_status_struct` | `MathStructure *` | The parsed structure of the current expression. Used to detect which function is being typed and its argument position. |
| `mfunc` | `MathFunction *` | Pointer to the function currently being edited (detected from cursor position). `NULL` if not inside a function call. |
| `current_function` | `MathFunction *` | Alias/copy of `mfunc` used for hint display. May differ if the user is editing a nested function. |
| `current_function_index` | `gint` | The 1-based index of the argument the cursor is currently inside. Used to highlight which parameter the hint describes. |
| `status_error` | `gboolean` | Whether the current display shows an error (controls red color). |
| `status_text` | `gchar *` | The current left-side text content. |
| `prev_status_text` | `gchar *` | Previous text, used to avoid unnecessary redraws when the text hasn't changed. |

---

## 3. Display Logic

### 3.1 `set_status_text(const gchar *text)`

Low-level setter. Sets the label's text and foreground color.

```c
void set_status_text(const gchar *text) {
    if(!text) text = "";
    if(strcmp(text, prev_status_text) == 0) return;  // skip redundant updates
    gtk_label_set_text(GTK_LABEL(status_label), text);
    g_free(prev_status_text);
    prev_status_text = g_strdup(text);
}
```

### 3.2 `update_status_text()`

Called after every expression change. Orchestrates what to display:

1. Check if the cursor is inside a function call → call `display_function_hint()`.
2. If not inside a function, call `display_parse_status()`.
3. If an error was detected, call `display_error_status()`.

### 3.3 `display_parse_status()`

Shows a summary of the current parse state:

```
If expression is empty:
    "Ready" or localized equivalent
If expression has been parsed successfully:
    Show abbreviated result preview (first ~80 chars of the result string)
If expression is being parsed (async):
    "Parsing..."
If parse failed:
    Delegates to error display
```

### 3.4 Update Trigger Chain

```
expression entry changed
    → on_expression_entry_changed()
        → update_expression_intext()
            → parse expression
                → on_expression_parsed()
                    → update_status_text()
                    → update_result()
```

The status bar is updated after every successful parse. During typing, the previous status text persists until the new parse completes.

---

## 4. Function Argument Hints

### 4.1 `display_function_hint()`

Algorithm to show which argument the cursor is currently editing:

```
1. Walk backward from cursor position in the expression text
2. Track parenthesis depth and comma count
3. When we find a function name followed by "(", count commas to determine argument index
4. Set current_function_index = number_of_commas + 1
5. Look up the function's argument definitions:
   - Number of required args
   - Number of optional args
   - Name and description of each arg
6. Format the hint string:
   "function_name(arg1_name, [arg2_name], arg3_name) — arg_index of N"
   with the current argument highlighted or bolded
```

### 4.2 Hint Format

Example for `integrate(x, a, b)` with cursor on the second argument:

```
integrate(expression, [from], to) — argument 2 of 3
```

- Required arguments are shown without brackets.
- Optional arguments are shown in `[brackets]`.
- The current argument is indicated by position (2 of 3).

### 4.3 Argument Detection Edge Cases

- **Nested functions**: Only the innermost function is shown. The walk tracks depth.
- **String arguments**: Commas inside quoted strings are not counted.
- **Matrix arguments**: Commas inside matrix brackets `[1, 2; 3, 4]` are not counted.
- **No function detected**: If the cursor is not inside a function call, return to `display_parse_status()`.

---

## 5. Error Display

### 5.1 Color Application

When an error occurs during parsing:

```c
void display_error_status(const gchar *error_msg) {
    gtk_label_set_text(GTK_LABEL(status_label), error_msg);
    // Apply red foreground color
    gtk_widget_modify_fg(status_label, GTK_STATE_NORMAL, &color_red);
    status_error = TRUE;
}
```

When the error is cleared (successful parse or expression cleared):

```c
void clear_error_status() {
    status_error = FALSE;
    // Restore default foreground color
    gtk_widget_modify_fg(status_label, GTK_STATE_NORMAL, NULL);
}
```

### 5.2 Auto-Color Derivation

The error color is derived from the current GTK theme:

```c
GdkColor color_red;
// Method 1: Hardcoded
gdk_color_parse("#CC0000", &color_red);

// Method 2: Derived from theme's "error" or "destructive" color
// (GTK3+: use CSS class; GTK2: parse named color)
```

The normal (non-error) color is the widget's default foreground, which comes from the GTK theme. Setting `modify_fg` to `NULL` restores the theme default.

### 5.3 Error Message Content

The error message is typically:
- A short description from `MathStructure::print()` or `Calculator::error()`.
- First 120 characters are shown; full error is available via tooltip or the status bar context menu.
- Error codes are not shown to the user.

---

## 6. Mode Indicators

The right side of the status bar shows small badge labels for calculator modes. Each badge is a `GtkLabel` with a colored background.

### 6.1 Indicators

| Badge | Visible When | Text | Color |
|---|---|---|---|
| **EXACT** | `CALCULATOR->usesIntervalArithmetic()` or exact mode | `"EXACT"` | Blue |
| **APPROX** | Approximate mode active | `"APPROX"` | Orange |
| **RPN** | RPN input mode active | `"RPN"` | Green |
| **CHN** | CHN (chain) input mode active | `"CHN"` | Green |
| **Base** | Non-decimal base active | `"HEX"`, `"OCT"`, `"BIN"`, `"DEC"` | Gray |
| **Angle** | Non-decimal angle unit | `"DEG"`, `"RAD"`, `"GRAD"` | Gray |
| **Precision** | Precision changed from default | `"P:15"` (or current value) | Gray |
| **Disabled** | Features disabled (e.g., unit conversion off) | Strikethrough or dimmed | Red-tint |

### 6.2 Badge Styling

```c
// GTK2 approach
GtkWidget *badge = gtk_label_new("EXACT");
PangoAttrList *attrs = pango_attr_list_new();
pango_attr_list_insert(attrs, pango_attr_weight_new(PANGO_WEIGHT_BOLD));
pango_attr_list_insert(attrs, pango_attr_size_new(PANGO_SCALE_SMALL));
gtk_label_set_attributes(GTK_LABEL(badge), attrs);
// Apply colored background via GtkEventBox or GtkMisc styling

// GTK3 approach via CSS
gtk_widget_set_name(badge, "status-badge-exact");
// CSS: #status-badge-exact { background-color: #3584e4; color: white; padding: 2px 6px; border-radius: 3px; }
```

### 6.3 Update Logic

```c
void update_mode_indicators() {
    // EXACT/APPROX
    gtk_widget_set_visible(badge_exact, CALCULATOR->usesIntervalArithmetic());
    gtk_widget_set_visible(badge_approx, !CALCULATOR->usesIntervalArithmetic());

    // Base
    if(evalops.base == 16) gtk_label_set_text(GTK_LABEL(badge_base), "HEX");
    else if(evalops.base == 8) gtk_label_set_text(GTK_LABEL(badge_base), "OCT");
    else if(evalops.base == 2) gtk_label_set_text(GTK_LABEL(badge_base), "BIN");
    else gtk_label_set_text(GTK_LABEL(badge_base), "DEC");
    gtk_widget_set_visible(badge_base, evalops.base != 10);

    // Angle
    switch(evalops.angle_unit) {
        case ANGLE_UNIT_DEGREES: gtk_label_set_text(..., "DEG"); break;
        case ANGLE_UNIT_RADIANS: gtk_label_set_text(..., "RAD"); break;
        case ANGLE_UNIT_GRADIANS: gtk_label_set_text(..., "GRAD"); break;
    }

    // Precision
    if(CALCULATOR->getPrecision() != 15) {
        gchar buf[16];
        snprintf(buf, sizeof(buf), "P:%d", CALCULATOR->getPrecision());
        gtk_label_set_text(GTK_LABEL(badge_precision), buf);
        gtk_widget_set_visible(badge_precision, TRUE);
    } else {
        gtk_widget_set_visible(badge_precision, FALSE);
    }
}
```

---

## 7. Integration Points

| Component | Integration |
|---|---|
| **Expression Entry** | `on_expression_entry_changed()` triggers `update_status_text()`. Cursor movement triggers `display_function_hint()`. |
| **Main Window** | Status bar is packed below the expression entry in the main VBox. Minimum height matches the entry height for visual alignment. |
| **Calculator Engine** | `CALCULATOR->parse()` and `CALCULATOR->calculate()` results feed into `display_parse_status()`. Error messages come from `CALCULATOR->error()`. |
| **Settings Dialog** | Mode changes (exact/approx, base, angle, precision) trigger `update_mode_indicators()`. |
| **Keypad Buttons** | Button clicks that change mode (e.g., base buttons) immediately update the indicators. |
| **Expression History** | When navigating history with Up/Down, the status bar updates to reflect the parsed status of the recalled expression. |

---

## 8. Tkinter Implementation Specification

### 8.1 Widget Structure

```python
class ExpressionStatusBar:
    def __init__(self, parent):
        self.frame = tk.Frame(parent, relief="sunken", bd=1)

        # Left: status text
        self.status_label = tk.Label(
            self.frame, text="Ready", anchor="w",
            font=("Segoe UI", 9), fg="#333333"
        )
        self.status_label.pack(side="left", fill="x", expand=True, padx=4)

        # Right: mode indicator badges
        self.badge_frame = tk.Frame(self.frame)
        self.badge_frame.pack(side="right", padx=4)

        self.badges = {}
        for name, default_text in [
            ("exact", "EXACT"), ("approx", "APPROX"),
            ("rpn", "RPN"), ("chn", "CHN"),
            ("base", "DEC"), ("angle", "DEG"),
            ("precision", "")
        ]:
            label = tk.Label(
                self.badge_frame, text=default_text,
                font=("Segoe UI", 8, "bold"),
                padx=4, pady=1
            )
            label.pack(side="left", padx=1)
            self.badges[name] = label
```

### 8.2 Badge Styling

```python
BADGE_STYLES = {
    "exact":    {"bg": "#3584e4", "fg": "#ffffff"},
    "approx":   {"bg": "#e5a50a", "fg": "#ffffff"},
    "rpn":      {"bg": "#2ec27e", "fg": "#ffffff"},
    "chn":      {"bg": "#2ec27e", "fg": "#ffffff"},
    "base":     {"bg": "#77767b", "fg": "#ffffff"},
    "angle":    {"bg": "#77767b", "fg": "#ffffff"},
    "precision":{"bg": "#77767b", "fg": "#ffffff"},
    "disabled": {"bg": "#e01b24", "fg": "#ffffff"},
}

def _apply_badge_style(self, name, visible=True):
    badge = self.badges[name]
    if visible:
        style = BADGE_STYLES[name]
        badge.configure(bg=style["bg"], fg=style["fg"])
        badge.pack(side="left", padx=1)
    else:
        badge.pack_forget()
```

### 8.3 Error Display

```python
def set_error(self, message):
    self.status_label.configure(
        text=message[:120],
        fg="#CC0000",
        font=("Segoe UI", 9, "italic")
    )
    self._is_error = True

def clear_error(self, message="Ready"):
    self.status_label.configure(
        text=message,
        fg="#333333",
        font=("Segoe UI", 9)
    )
    self._is_error = False
```

### 8.4 Function Hint Display

```python
def display_function_hint(self, func_name, args, current_index, total_args):
    parts = []
    for i, arg in enumerate(args):
        arg_str = arg["name"]
        if arg.get("optional"):
            arg_str = f"[{arg_str}]"
        if i == current_index - 1:
            arg_str = f">>{arg_str}<<"  # visual indicator
        parts.append(arg_str)

    hint = f"{func_name}({', '.join(parts)}) — argument {current_index} of {total_args}"
    self.status_label.configure(text=hint)
```

### 8.5 Debounced Updates

```python
def schedule_update(self):
    if self._update_after_id:
        self.frame.after_cancel(self._update_after_id)
    self._update_after_id = self.frame.after(100, self._do_update)

def _do_update(self):
    self.update_mode_indicators()
    self.update_parse_status()
```

---

*End of Expression Status Bar Specification*
