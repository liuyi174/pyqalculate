# Dialogs Inventory

> **Source**: pyQalculate `qalculate-gtk` (`src/interface.cc`, `src/callbacks.cc`, `src/dialogs.cc`, `data/ui/*.ui`)
> **Purpose**: Complete inventory of all 28 dialogs in the qalculate-gtk application, including source location, purpose, key widgets, functions, settings persistence, calculator interaction, and geometry.

---

## Table of Contents

1. [Dialog Inventory (28 Dialogs)](#1-dialog-inventory-28-dialogs)
2. [Settings Persistence Matrix](#2-settings-persistence-matrix)
3. [UI Builder Files List](#3-ui-builder-files-list)
4. [Dialog Architecture Patterns](#4-dialog-architecture-patterns)

---

## 1. Dialog Inventory (28 Dialogs)

### 1.1 Preferences Dialog

| Field | Value |
|---|---|
| **Source** | `src/interface.cc`: `create_preferences_dialog()` |
| **Purpose** | Master settings dialog for all application preferences |
| **Key Widgets** | GtkNotebook (tabs: General, Display, Expression, etc.), GtkSpinButton, GtkCheckButton, GtkComboBox |
| **Key Functions** | `preferences_dialog_response()`, `on_preferences_dialog_close()` |
| **Settings Persisted** | enable_completion, completion_min, completion_delay, display_expression_status, display_result, display_units, always_raise, decimal_comma, etc. |
| **Calculator Interaction** | Calls `CALCULATOR->set...()` methods to update calculator state |
| **Size/Geometry** | ~600x500, centered on main window |

### 1.2 Functions Dialog

| Field | Value |
|---|---|
| **Source** | `src/interface.cc`: `create_functions_dialog()` |
| **Purpose** | Browse, search, edit, and manage all registered mathematical functions |
| **Key Widgets** | GtkTreeView (function list), GtkSearchEntry, GtkButton (New, Edit, Delete), GtkPopover (details) |
| **Key Functions** | `on_function_selected()`, `on_function_new()`, `on_function_edit()`, `on_function_delete()` |
| **Settings Persisted** | Window position/size, selected function |
| **Calculator Interaction** | Reads `CALCULATOR->functions()`, inserts selected function into expression edit |
| **Size/Geometry** | ~500x400, non-modal (modeless) |

### 1.3 Variables Dialog

| Field | Value |
|---|---|
| **Source** | `src/interface.cc`: `create_variables_dialog()` |
| **Purpose** | Browse, search, edit, and manage all registered variables |
| **Key Widgets** | GtkTreeView (variable list), GtkSearchEntry, GtkButton (New, Edit, Delete) |
| **Key Functions** | `on_variable_selected()`, `on_variable_new()`, `on_variable_edit()`, `on_variable_delete()` |
| **Settings Persisted** | Window position/size |
| **Calculator Interaction** | Reads `CALCULATOR->variables()`, inserts selected variable into expression edit |
| **Size/Geometry** | ~500x400, modeless |

### 1.4 Units Dialog

| Field | Value |
|---|---|
| **Source** | `src/interface.cc`: `create_units_dialog()` |
| **Purpose** | Browse, search, edit, and manage all registered units |
| **Key Widgets** | GtkTreeView (unit list), GtkSearchEntry, GtkButton (New, Edit, Delete) |
| **Key Functions** | `on_unit_selected()`, `on_unit_new()`, `on_unit_edit()`, `on_unit_delete()` |
| **Settings Persisted** | Window position/size |
| **Calculator Interaction** | Reads `CALCULATOR->units()`, inserts selected unit into expression edit |
| **Size/Geometry** | ~500x400, modeless |

### 1.5 Constants Dialog

| Field | Value |
|---|---|
| **Source** | `src/interface.cc`: `create_constants_dialog()` |
| **Purpose** | Browse and manage predefined and user-defined constants |
| **Key Widgets** | GtkTreeView (constants list), GtkSearchEntry, GtkButton (New, Edit, Delete) |
| **Key Functions** | `on_constant_selected()`, `on_constant_new()`, `on_constant_edit()` |
| **Settings Persisted** | Window position/size |
| **Calculator Interaction** | Reads `CALCULATOR->constants()`, inserts selected constant into expression edit |
| **Size/Geometry** | ~500x400, modeless |

### 1.6 Function Edit Dialog

| Field | Value |
|---|---|
| **Source** | `src/interface.cc`: `create_function_edit_dialog()` |
| **Purpose** | Create or edit a custom function (name, arguments, expression, description) |
| **Key Widgets** | GtkEntry (name), GtkTextView (expression), GtkTreeView (argument list), GtkComboBox (argument types) |
| **Key Functions** | `on_function_edit_save()`, `on_function_edit_test()`, `on_function_edit_cancel()` |
| **Settings Persisted** | None (edits are saved to calculator on "Save") |
| **Calculator Interaction** | Modifies `MathFunction` properties, calls `CALCULATOR->addFunction()` for new functions |
| **Size/Geometry** | ~550x450, modal |

### 1.7 Variable Edit Dialog

| Field | Value |
|---|---|
| **Source** | `src/interface.cc`: `create_variable_edit_dialog()` |
| **Purpose** | Create or edit a user-defined variable |
| **Key Widgets** | GtkEntry (name), GtkTextView (value expression), GtkComboBox (type) |
| **Key Functions** | `on_variable_edit_save()`, `on_variable_edit_cancel()` |
| **Settings Persisted** | None (edits saved to calculator) |
| **Calculator Interaction** | Modifies `Variable` properties, calls `CALCULATOR->addVariable()` for new |
| **Size/Geometry** | ~450x300, modal |

### 1.8 Unit Edit Dialog

| Field | Value |
|---|---|
| **Source** | `src/interface.cc`: `create_unit_edit_dialog()` |
| **Purpose** | Create or edit a custom unit |
| **Key Widgets** | GtkEntry (name, title), GtkComboBox (unit type: base, conversion, etc.), GtkTextView (conversion expression), GtkComboBox (reference unit) |
| **Key Functions** | `on_unit_edit_save()`, `on_unit_edit_test()`, `on_unit_edit_cancel()` |
| **Settings Persisted** | None |
| **Calculator Interaction** | Modifies `Unit` properties, calls `CALCULATOR->addUnit()` for new |
| **Size/Geometry** | ~500x400, modal |

### 1.9 Constants Edit Dialog

| Field | Value |
|---|---|
| **Source** | `src/interface.cc`: `create_constants_edit_dialog()` |
| **Purpose** | Create or edit a user-defined constant |
| **Key Widgets** | GtkEntry (name), GtkTextView (value expression), GtkComboBox (category), GtkTextView (description) |
| **Key Functions** | `on_constant_edit_save()`, `on_constant_edit_cancel()` |
| **Settings Persisted** | None |
| **Calculator Interaction** | Modifies `Constant` properties, calls `CALCULATOR->addConstant()` for new |
| **Size/Geometry** | ~450x350, modal |

### 1.10 Data Sets Dialog

| Field | Value |
|---|---|
| **Source** | `src/interface.cc`: `create_datasets_dialog()` |
| **Purpose** | Browse and search bundled data sets (countries, currencies, etc.) |
| **Key Widgets** | GtkTreeView (dataset list), GtkSearchEntry, GtkTreeView (data rows), GtkButton (Add to expression) |
| **Key Functions** | `on_dataset_selected()`, `on_dataset_row_selected()`, `on_dataset_add()` |
| **Settings Persisted** | Window position/size |
| **Calculator Interaction** | Reads `CALCULATOR->datasets()`, inserts data references into expression edit |
| **Size/Geometry** | ~600x450, modeless |

### 1.11 Plot Dialog

| Field | Value |
|---|---|
| **Source** | `src/interface.cc`: `create_plot_dialog()` |
| **Purpose** | Configure and display function plots |
| **Key Widgets** | GtkEntry (expression), GtkSpinButton (range: x_min, x_max, y_min, y_max), GtkComboBox (color, line style), GtkDrawingArea (plot canvas), GtkButton (Plot, Export) |
| **Key Functions** | `on_plot_clicked()`, `on_plot_export()`, `on_plot_range_changed()` |
| **Settings Persisted** | Plot ranges, colors, line styles, window size |
| **Calculator Interaction** | Evaluates the expression at sampled points, renders the plot |
| **Size/Geometry** | ~700x500, modeless |

### 1.12 Precision Dialog

| Field | Value |
|---|---|
| **Source** | `src/interface.cc`: `create_precision_dialog()` (inline popover or dialog) |
| **Purpose** | Set the calculator's precision (significant digits) |
| **Key Widgets** | GtkSpinButton (precision value, 2-64), GtkLabel (current value) |
| **Key Functions** | `on_precision_changed()` |
| **Settings Persisted** | `CALCULATOR->setPrecision()` |
| **Calculator Interaction** | `CALCULATOR->setPrecision(n)` |
| **Size/Geometry** | ~250x100, modal popover |

### 1.13 Base Conversion Dialog

| Field | Value |
|---|---|
| **Source** | `src/interface.cc`: `create_base_dialog()` |
| **Purpose** | Display the current result in multiple bases (binary, octal, decimal, hexadecimal) |
| **Key Widgets** | GtkLabel x4 (BIN, OCT, DEC, HEX displays), GtkEntry (editable input for base conversion) |
| **Key Functions** | `on_base_input_changed()`, `update_base_dialog()` |
| **Settings Persisted** | Window position/size |
| **Calculator Interaction** | Evaluates the expression and displays in each base |
| **Size/Geometry** | ~400x250, modeless |

### 1.14 Periodic Table Dialog

| Field | Value |
|---|---|
| **Source** | `src/interface.cc`: `create_periodic_dialog()` |
| **Purpose** | Interactive periodic table for element lookup and unit insertion |
| **Key Widgets** | GtkGrid (element buttons, color-coded by category), GtkLabel (element details) |
| **Key Functions** | `on_element_clicked()`, `update_element_info()` |
| **Settings Persisted** | Window position/size |
| **Calculator Interaction** | Inserts element symbol or atomic number into expression edit |
| **Size/Geometry** | ~700x450, modeless |

### 1.15 Dataset Edit Dialog

| Field | Value |
|---|---|
| **Source** | `src/interface.cc`: `create_dataset_edit_dialog()` |
| **Purpose** | Edit properties of a data set (name, description, columns, data) |
| **Key Widgets** | GtkEntry (name, title), GtkTextView (description), GtkTreeView (column definitions), GtkTextView (CSV data editor) |
| **Key Functions** | `on_dataset_edit_save()`, `on_dataset_edit_cancel()`, `on_dataset_edit_test()` |
| **Settings Persisted** | None (edits saved to calculator) |
| **Calculator Interaction** | Modifies `DataSet` properties |
| **Size/Geometry** | ~600x500, modal |

### 1.16 Calculate With Dialog

| Field | Value |
|---|---|
| **Source** | `src/interface.cc`: `create_calculate_with_dialog()` |
| **Purpose** | Evaluate the expression with a specific variable substituted (what-if analysis) |
| **Key Widgets** | GtkComboBox (variable selector), GtkEntry (value input), GtkButton (Calculate), GtkLabel (result) |
| **Key Functions** | `on_calculate_with()`, `on_calculate_with_response()` |
| **Settings Persisted** | None |
| **Calculator Interaction** | `CALCULATOR->calculate()` with substitution map |
| **Size/Geometry** | ~400x200, modal |

### 1.17 Simplify Dialog

| Field | Value |
|---|---|
| **Source** | `src/interface.cc`: `create_simplify_dialog()` |
| **Purpose** | Advanced expression simplification options |
| **Key Widgets** | GtkCheckButton (simplification options), GtkButton (Simplify), GtkLabel (result) |
| **Key Functions** | `on_simplify_clicked()` |
| **Settings Persisted** | Last simplification options |
| **Calculator Interaction** | `CALCULATOR->simplify()` with selected options |
| **Size/Geometry** | ~400x250, modal |

### 1.18 Number Bases Dialog

| Field | Value |
|---|---|
| **Source** | `src/interface.cc`: (may be same as base dialog or separate) |
| **Purpose** | Convert numbers between different bases with interactive bit display |
| **Key Widgets** | GtkEntry (input), GtkLabel (output in each base), GtkToggleButton (bit toggles for binary) |
| **Key Functions** | `on_base_input_changed()`, `on_bit_toggled()` |
| **Settings Persisted** | Window position |
| **Calculator Interaction** | Base conversion calculations |
| **Size/Geometry** | ~400x300, modeless |

### 1.19 Floating Point Dialog

| Field | Value |
|---|---|
| **Source** | `src/interface.cc`: `createFloatingPointDialog()` |
| **Purpose** | Display IEEE 754 floating-point representation of a number |
| **Key Widgets** | GtkLabel (binary representation, sign/exponent/mantissa fields), GtkEntry (input number) |
| **Key Functions** | `on_floating_point_input()` |
| **Settings Persisted** | Window position |
| **Calculator Interaction** | Converts number to IEEE 754 format |
| **Size/Geometry** | ~450x250, modeless |

### 1.20 Unknown Variables Dialog

| Field | Value |
|---|---|
| **Source** | `src/interface.cc`: `create_unknown_dialog()` |
| **Purpose** | Define unknown variables for equation solving |
| **Key Widgets** | GtkEntry (variable name), GtkComboBox (type: real, complex, etc.), GtkButton (Add, Remove), GtkTreeView (list of unknowns) |
| **Key Functions** | `on_unknown_add()`, `on_unknown_remove()`, `on_unknown_changed()` |
| **Settings Persisted** | List of unknown variables |
| **Calculator Interaction** | Sets `ASSUMPTIONS` for the variables |
| **Size/Geometry** | ~400x300, modal |

### 1.21 Modifiers Dialog

| Field | Value |
|---|---|
| **Source** | `src/interface.cc`: `create_modifiers_dialog()` |
| **Purpose** | Apply modifiers to the result (e.g., assume positive, expand, factor) |
| **Key Widgets** | GtkCheckButton (modifier options), GtkButton (Apply) |
| **Key Functions** | `on_modifier_apply()` |
| **Settings Persisted** | Last used modifiers |
| **Calculator Interaction** | `CALCULATOR->calculate()` with modifier flags |
| **Size/Geometry** | ~350x250, modal |

### 1.22 Insert Text Color Dialog

| Field | Value |
|---|---|
| **Source** | `src/interface.cc`: (inline in expression formatting) |
| **Purpose** | Choose a color for text formatting in the expression |
| **Key Widgets** | GtkColorChooser, GtkButton (OK, Cancel) |
| **Key Functions** | `on_color_chosen()` |
| **Settings Persisted** | None |
| **Calculator Interaction** | None (formatting only) |
| **Size/Geometry** | ~300x250, modal |

### 1.23 Insert Text Background Dialog

| Field | Value |
|---|---|
| **Source** | `src/interface.cc`: (inline in expression formatting) |
| **Purpose** | Choose a background color for text formatting |
| **Key Widgets** | GtkColorChooser, GtkButton (OK, Cancel) |
| **Key Functions** | `on_bg_color_chosen()` |
| **Settings Persisted** | None |
| **Calculator Interaction** | None (formatting only) |
| **Size/Geometry** | ~300x250, modal |

### 1.24 Insert Text Size Dialog

| Field | Value |
|---|---|
| **Source** | `src/interface.cc`: (inline in expression formatting) |
| **Purpose** | Set text size (font size) for expression formatting |
| **Key Widgets** | GtkComboBox (size: small, normal, large, etc.), GtkButton (OK) |
| **Key Functions** | `on_text_size_chosen()` |
| **Settings Persisted** | None |
| **Calculator Interaction** | None (formatting only) |
| **Size/Geometry** | ~250x150, modal |

### 1.25 Keyboard Shortcuts Dialog

| Field | Value |
|---|---|
| **Source** | `src/interface.cc`: `create_shortcuts_dialog()` |
| **Purpose** | View and customize keyboard shortcuts |
| **Key Widgets** | GtkTreeView (shortcut list: action, key, modifier), GtkCellRenderer (editable), GtkButton (Reset to Default) |
| **Key Functions** | `on_shortcut_edited()`, `on_shortcut_reset()` |
| **Settings Persisted** | `SHORTCUTS` section in config file |
| **Calculator Interaction** | Modifies `key_shortcuts` array |
| **Size/Geometry** | ~500x400, modal |

### 1.26 Help Dialog

| Field | Value |
|---|---|
| **Source** | `src/interface.cc`: `create_help_dialog()` |
| **Purpose** | Display application help / about information |
| **Key Widgets** | GtkLabel (version, credits), GtkTextView (license), GtkLinkButton (website) |
| **Key Functions** | `on_help_response()` |
| **Settings Persisted** | None |
| **Calculator Interaction** | None |
| **Size/Geometry** | ~450x350, modal |

### 1.27 Insert Function Dialog

| Field | Value |
|---|---|
| **Source** | `src/interface.cc`: `create_insert_function_dialog()` |
| **Purpose** | Guided function insertion with argument-by-argument input |
| **Key Widgets** | GtkTreeView (function list), GtkEntry (argument fields, dynamic count), GtkButton (Insert), GtkLabel (description, syntax) |
| **Key Functions** | `on_insert_function_selected()`, `on_insert_function_insert()`, `on_insert_function_arg_changed()` |
| **Settings Persisted** | Window position, last selected function |
| **Calculator Interaction** | Reads function metadata, builds expression string |
| **Size/Geometry** | ~550x450, modal |

### 1.28 Insert Matrix/Vector Dialog

| Field | Value |
|---|---|
| **Source** | `src/interface.cc`: `create_insert_matrix_dialog()` |
| **Purpose** | Create and insert matrices or vectors |
| **Key Widgets** | GtkSpinButton (rows, columns), GtkGrid (cell entry fields), GtkComboBox (type: matrix, vector, column vector), GtkButton (Insert) |
| **Key Functions** | `on_matrix_dimensions_changed()`, `on_matrix_insert()`, `on_matrix_cancel()` |
| **Settings Persisted** | Last dimensions, type |
| **Calculator Interaction** | Builds matrix expression string, inserts into expression edit |
| **Size/Geometry** | ~450x400, modal |

---

## 2. Settings Persistence Matrix

| Dialog | Persists Settings? | Config Section | Key Settings |
|---|---|---|---|
| Preferences | Yes | `[GTK]` | All application preferences |
| Functions | No | - | Window position only |
| Variables | No | - | Window position only |
| Units | No | - | Window position only |
| Constants | No | - | Window position only |
| Function Edit | No | - | None (saves to calculator) |
| Variable Edit | No | - | None (saves to calculator) |
| Unit Edit | No | - | None (saves to calculator) |
| Constants Edit | No | - | None (saves to calculator) |
| Data Sets | No | - | Window position only |
| Plot | Yes | `[PLOT]` | Ranges, colors, line styles |
| Precision | Yes | `[GTK]` | Precision value |
| Base Conversion | No | - | Window position only |
| Periodic Table | No | - | Window position only |
| Dataset Edit | No | - | None (saves to calculator) |
| Calculate With | No | - | None |
| Simplify | Yes | `[GTK]` | Last simplification options |
| Number Bases | No | - | Window position only |
| Floating Point | No | - | Window position only |
| Unknown Variables | Yes | `[GTK]` | Unknown variable list |
| Modifiers | Yes | `[GTK]` | Last modifier flags |
| Text Color | No | - | None |
| Text Background | No | - | None |
| Text Size | No | - | None |
| Keyboard Shortcuts | Yes | `[SHORTCUTS]` | All shortcut bindings |
| Help | No | - | None |
| Insert Function | No | - | Window position only |
| Insert Matrix | No | - | Last dimensions, type |

---

## 3. UI Builder Files List

All UI definitions are in `data/ui/` (GtkBuilder XML format):

| File | Dialog(s) |
|---|---|
| `preferences_dialog.ui` | Preferences Dialog |
| `functions_dialog.ui` | Functions Dialog |
| `variables_dialog.ui` | Variables Dialog |
| `units_dialog.ui` | Units Dialog |
| `constants_dialog.ui` | Constants Dialog |
| `function_edit_dialog.ui` | Function Edit Dialog |
| `variable_edit_dialog.ui` | Variable Edit Dialog |
| `unit_edit_dialog.ui` | Unit Edit Dialog |
| `constants_edit_dialog.ui` | Constants Edit Dialog |
| `datasets_dialog.ui` | Data Sets Dialog |
| `dataset_edit_dialog.ui` | Dataset Edit Dialog |
| `plot_dialog.ui` | Plot Dialog |
| `periodic_dialog.ui` | Periodic Table Dialog |
| `base_dialog.ui` | Base Conversion Dialog |
| `floating_point_dialog.ui` | Floating Point Dialog |
| `shortcuts_dialog.ui` | Keyboard Shortcuts Dialog |
| `help_dialog.ui` | Help Dialog |
| `insert_function_dialog.ui` | Insert Function Dialog |
| `insert_matrix_dialog.ui` | Insert Matrix/Vector Dialog |
| `unknown_dialog.ui` | Unknown Variables Dialog |
| `main_window.ui` | Main Window (not a dialog, but included for completeness) |

> Note: Some smaller dialogs (Precision, Simplify, Modifiers, text formatting) are constructed programmatically in `src/interface.cc` without a separate UI file.

---

## 4. Dialog Architecture Patterns

### 4.1 Lazy Singleton Pattern

Most dialogs follow a lazy singleton pattern: the dialog widget is created on first access and reused thereafter.

```c
GtkWidget *functions_dialog = NULL;  // file-level static

GtkWidget *get_functions_dialog() {
    if(!functions_dialog) {
        functions_dialog = create_functions_dialog();
        g_signal_connect(functions_dialog, "response",
                         G_CALLBACK(functions_dialog_response), NULL);
    }
    return functions_dialog;
}

void show_functions_dialog() {
    GtkWidget *dlg = get_functions_dialog();
    gtk_widget_show_all(dlg);
    gtk_window_present(GTK_WINDOW(dlg));
}
```

### 4.2 Modal vs Modeless

| Pattern | Dialogs | Behavior |
|---|---|---|
| **Modal** | Function Edit, Variable Edit, Unit Edit, Constants Edit, Dataset Edit, Calculate With, Simplify, Modifiers, Text Color, Text Background, Text Size, Insert Function, Insert Matrix, Unknown Variables, Help, Keyboard Shortcuts | Blocks interaction with the main window. Uses `gtk_window_set_modal(GTK_WINDOW(dlg), TRUE)`. |
| **Modeless** | Functions, Variables, Units, Constants, Data Sets, Plot, Base Conversion, Periodic Table, Number Bases, Floating Point | Can interact with the main window while open. Uses `gtk_window_present()` for focus. |

### 4.3 Tree/List Pattern

Dialogs that browse a collection (Functions, Variables, Units, Constants, Data Sets) share this structure:

```
GtkBox (vertical)
  ├─ GtkSearchEntry (filter)
  ├─ GtkScrolledWindow
  │   └─ GtkTreeView (list of items)
  └─ GtkBox (horizontal, button bar)
      ├─ GtkButton (New / Add)
      ├─ GtkButton (Edit)
      └─ GtkButton (Delete)
```

Selection in the TreeView updates a detail panel or enables/disables the Edit/Delete buttons.

### 4.4 Editor Pattern

Dialogs that create/edit items (Function Edit, Variable Edit, Unit Edit, Constants Edit, Dataset Edit) share this structure:

```
GtkDialog
  ├─ GtkBox (content area)
  │   ├─ GtkEntry (name)
  │   ├─ GtkEntry (title / description)
  │   ├─ GtkTextView (expression / data)
  │   └─ ... (type-specific fields)
  └─ GtkBox (action area)
      ├─ GtkButton (Test / Preview)
      ├─ GtkButton (Save)
      └─ GtkButton (Cancel)
```

The "Save" button validates input, constructs the appropriate calculator object, and calls `CALCULATOR->add...()` or `->set...()`.

### 4.5 Dialog Lifecycle

```
First show:  create_xxx_dialog() → gtk_widget_show_all() → gtk_window_present()
Subsequent:  gtk_widget_show_all() → gtk_window_present()
Close:       gtk_widget_hide() (widget is NOT destroyed, just hidden)
Destroy:     Only on application exit: gtk_widget_destroy()
```

### 4.6 Response Codes

Modal dialogs use standard GtkDialog response codes:

| Code | Constant | Meaning |
|---|---|---|
| -1 | `GTK_RESPONSE_DELETE_EVENT` | User closed via window manager |
| -4 | `GTK_RESPONSE_HELP` | Help button clicked |
| -5 | `GTK_RESPONSE_APPLY` | Apply/Save button clicked |
| -6 | `GTK_RESPONSE_ACCEPT` | OK/Accept button clicked |
| -7 | `GTK_RESPONSE_REJECT` | Cancel button clicked |
| -8 | `GTK_RESPONSE_YES` | Yes button clicked |
| -9 | `GTK_RESPONSE_NO` | No button clicked |

---

*End of Dialogs Inventory*
