# Result View - qalculate-gtk Analysis

**Files:**
- `D:\1\1tmp\qalculate-gtk\src\resultview.h` (66 lines)
- `D:\1\1tmp\qalculate-gtk\src\resultview.cc` (1392 lines)
- **Total: 1458 lines**

## What It Does

The result view module implements the **calculation result display area** - a custom Cairo-rendered widget that displays mathematical results as high-quality typeset output (similar to LaTeX rendering). It handles scaling, auto-sizing, copy/export, and an extensive right-click context menu for format conversion.

## Architecture

### Key Global State (File-scope Variables)

| Variable | Type | Purpose |
|----------|------|---------|
| `resultview` | `GtkWidget*` | The main drawing area widget |
| `surface_result` | `cairo_surface_t*` | Pre-rendered result image |
| `surface_parsed` | `cairo_surface_t*` | Pre-rendered parsed expression image |
| `tmp_surface` | `cairo_surface_t*` | Temporary surface during rendering |
| `displayed_mstruct` | `MathStructure*` | Currently displayed result as MathStructure |
| `displayed_parsed_mstruct` | `MathStructure*` | Currently displayed parsed expression |
| `displayed_printops` | `PrintOptions` | Print options used for current display |
| `parsed_printops` | `PrintOptions` | Print options for parsed expression |
| `scale_n` | `int` | Current render scale level (0, 1, 2, 3) |
| `result_too_long` | `bool` | Whether result exceeded display limits |
| `result_display_overflow` | `bool` | Whether result overflows the scroll area |
| `display_aborted` | `bool` | Whether rendering was aborted |
| `show_parsed_instead_of_result` | `bool` | Toggle: show parsed form instead of result |
| `first_draw_of_result` | `bool` | Whether this is the first draw (triggers auto-scale) |
| `b_busy_draw` | `bool` | Prevents recursive draws during calculator busy |
| `custom_result_height` | `int` | User-configured result height (-1 = auto) |
| `binary_x_diff`, `binary_y_diff` | `int` | Offset for click coordinate translation |

### Key Functions

#### Lifecycle
| Function | Lines | Purpose |
|----------|-------|---------|
| `create_result_view()` | 1364-1392 | CSS providers, margins, font, connects signal handlers |
| `result_view_widget()` | 75-78 | Returns the drawing area widget |
| `result_view_clear()` | 132-155 | Clears all surfaces and displayed data |
| `result_view_empty()` | 178-180 | Checks if anything is displayed |

#### Drawing Pipeline
| Function | Lines | Purpose |
|----------|-------|---------|
| `draw_result_pre()` | 413-430 | Clears surfaces, resets scale, disables save-as |
| `draw_result_temp()` | 434-456 | Draws intermediate/temporary result during calculation |
| `draw_result_check()` | 457-476 | Checks if draw was aborted |
| `draw_result()` | 491-519 | **Main draw**: renders MathStructure to Cairo surface via `draw_structure()` |
| `draw_result_failure()` | 520-548 | Renders failure messages ("too long", "aborted") |
| `draw_result_finalize()` | 477-490 | Sets surface_result, triggers widget redraw |
| `draw_parsed()` | 190-200 | Renders parsed expression to surface_parsed |
| `draw_result_backup()` / `draw_result_restore()` | 390-404 | Save/restore surface during operations |

#### The Main Draw Callback
| Function | Lines | Purpose |
|----------|-------|---------|
| `on_resultview_draw()` | 206-356 | **Core rendering loop**: (1) Renders MathStructure to Cairo surface, (2) Auto-scales if result doesn't fit (scale_n 0->1->2->3), (3) Centers result, (4) Handles overflow with scrollbars, (5) Shows first-time help |

#### Auto-Scaling Logic
```
scale_n = 0: Full resolution render
scale_n = 1: Slightly reduced
scale_n = 2: More reduced  
scale_n = 3: Fully reduced to fit width
```
Loop increases scale_n until result fits within scroll window. Special case: >1.44x overflow jumps to scale 3.

#### Display Control
| Function | Lines | Purpose |
|----------|-------|---------|
| `display_parsed_instead_of_result()` | 113-127 | Toggles between showing result and parsed form |
| `result_display_updated()` | 595-607 | Updates display when print options change |
| `redraw_result()` | 385-387 | Triggers widget redraw |
| `update_displayed_printops()` | 371-376 | Syncs print options with current settings |
| `result_did_not_fit()` | 364-366 | Returns whether result overflowed |

#### Spinner Control
| Function | Lines | Purpose |
|----------|-------|---------|
| `start_result_spinner()` | 358-360 | Starts calculation spinner |
| `stop_result_spinner()` | 361-363 | Stops spinner |

#### Context Menu System (410 lines)
| Function | Lines | Purpose |
|----------|-------|---------|
| `update_resultview_popup()` | 761-1171 | Dynamically shows/hides menu items based on result type |
| `on_popup_menu_item_copy_activate()` | 747-749 | Copy result to clipboard |
| `on_resultview_button_press_event()` | 1180-1211 | Right-click popup, left-click copies or toggles binary |

#### Format Conversion Handlers
| Handler | Purpose |
|---------|---------|
| `on_popup_menu_item_display_normal/engineering/scientific_activate` | Display notation |
| `on_popup_menu_item_binary/octal/decimal/hexadecimal_activate` | Number base |
| `on_popup_menu_item_complex_rectangular/exponential/polar_activate` | Complex form |
| `on_popup_menu_item_fraction_decimal/combined/fraction_activate` | Fraction format |
| `convert_to_unit_noprefix` / `convert_to_currency` | Unit conversion |

#### Font Management
| Function | Lines | Purpose |
|----------|-------|---------|
| `update_result_font()` | 1223-1251 | Updates CSS font for result area |
| `set_result_font()` | 1252-1263 | Sets custom font |
| `set_result_size_request()` | 1292-1327 | Calculates minimum height by rendering test expression |

#### Image Export
| Function | Lines | Purpose |
|----------|-------|---------|
| `save_as_image()` | 549-591 | File chooser, renders to PNG via cairo_surface_write_to_png() |

#### Settings
| Function | Lines | Purpose |
|----------|-------|---------|
| `read_result_view_settings_line()` | 80-92 | Reads: custom font, custom height |
| `write_result_view_settings()` | 93-97 | Writes settings |

## Calculator Interaction

1. **`draw_structure()`** (from `drawstructure.cc`) - Converts `MathStructure` to Cairo surface using `PrintOptions`
2. **`PrintOptions`** - Controls rendering: number base, complex form, fractions, unit prefixes
3. **`evalops`** - Evaluation options affecting what gets displayed
4. **`CALCULATOR->aborted()`** - Checked after every draw for cancellation
5. **`current_result()`** - Returns current MathStructure result
6. **`parsed_in_result`** - Flag controlling whether parsed expression overlays result
7. **`can_display_unicode_string_function()`** - Font capability checks

## Rendering Pipeline

```
Calculation completes
  -> draw_result_pre()          // Clear old surface
  -> draw_result(mstruct)       // Render via draw_structure() -> Cairo surface
    -> draw_result_check()      // Handle abort
  -> draw_result_finalize()     // Set surface_result, trigger redraw

GTK draw signal fires
  -> on_resultview_draw()
    -> Check if auto-scale needed
    -> If yes: increase scale_n, re-render
    -> Center result in widget
    -> cairo_set_source_surface() + cairo_paint()
```
