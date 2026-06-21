# qalculate-gtk Dialog and Menu System Analysis

Generated from source analysis of qalculate-gtk/src/

---

## 1. Menubar (menubar.h / menubar.cc)

### Purpose
The central menu bar controller for qalculate-gtk. It manages the entire application menu system: File, Edit, Mode, and Help menus. It dynamically builds hierarchical menus for functions, variables, units, and prefixes from the libqalculate engine, manages recent items (5-item LRU cache), handles keyboard accelerators/shortcuts, and synchronizes menu check-item state with the Calculator evalops, printops, and mode settings.

### Lines of Code
| File | Lines |
|------|-------|
| menubar.h | 66 |
| menubar.cc | 2,709 |
| **Total** | **2,775** |

### Key Functions

#### Menu Construction
| Function | Description |
|----------|-------------|
| create_menubar() | Entry point. Sets initial mode, wires callbacks from GtkBuilder UI. |
| create_fmenu() | Builds Functions menu by walking function_cats tree. |
| create_vmenu() | Builds Variables menu by walking variable_cats tree. |
| create_umenu() | Builds Units menu from unit_cats tree plus user units and prefixes. |
| create_umenu2() | Builds Edit > Result Units sub-menu for unit conversion of results. |
| create_pmenu(item) | Generates prefixes sub-menu (decimal/binary prefix names with exponents). |
| create_pmenu2() | Generates Edit > Result Prefixes sub-menu with No/Optimal Prefix. |

#### Mode Synchronization (Calculator to Menu)
| Function | Description |
|----------|-------------|
| set_mode_items(mode, initial) | Master sync: sets all menu check-items from a mode_struct. |
| update_menu_base() | Syncs base display radio items (binary/octal/decimal/hex/etc.). |
| update_menu_approximation() | Syncs approximation radio items (exact/try exact/approximate). |
| update_menu_numerical_display() | Syncs numerical display mode and prefix settings. |
| update_menu_fraction() | Syncs fraction format radio items. |
| update_menu_angle() | Syncs angle unit radio items. |
| update_menu_calculator_mode() | Syncs autocalc/chain/RPN mode. |
| update_assumptions_items() | Syncs type/sign assumption items. |
| add_custom_angles_to_menus() | Dynamically adds/removes custom angle unit entries. |

#### Calculator Interaction (Menu to Calculator)
| Function | Calculator API Used |
|----------|---------------------|
| on_menu_item_*_activate handlers | Directly modify evalops.*, printops.*, CALCULATOR->*. |
| on_menu_item_factorize_activate | executeCommand(COMMAND_FACTORIZE) |
| on_menu_item_simplify_activate | executeCommand(COMMAND_EXPAND) |
| convert_to_unit | convert_result_to_unit(u) |
| on_menu_item_interval_arithmetic_activate | CALCULATOR->useIntervalArithmetic(b) |

#### Recent Items Management
| Function | Description |
|----------|-------------|
| add_recent_function/variable/unit | LRU: removes duplicates, caps at 5 items, prepends to menu. |
| remove_from_recent_*() | Removes from tracking lists and destroys GtkWidgets. |
| recreate_recent_*() | Rebuilds all recent menu items from scratch. |

### Calculator Interaction Pattern
User clicks menu item -> on_menu_item_*_activate() -> Sets global state: evalops.*, printops.*, CALCULATOR->* -> Calls expression_calculation_updated() or result_format_updated() -> Triggers re-evaluation/re-rendering

### Architecture Notes
- Uses GtkBuilder from main_builder (loaded from UI file)
- Signal handlers are blocked/unblocked around programmatic menu updates to prevent loops
- All menus use hierarchical tree_struct iterators to walk category trees
- create_menubar() registers ~130+ callback symbols via gtk_builder_add_callback_symbols()
- Modes can be saved/loaded/deleted via mode_struct system (supports user-defined modes)

---

## 2. Plot Dialog (plotdialog.h / plotdialog.cc)

### Purpose
Provides a complete function/vector plotting interface backed by Gnuplot. Users can plot mathematical expressions, vectors, and paired data. Supports configuring appearance (line style, smoothing, legend, grid, log axes), x-range, sampling rate, and exporting plots to file (PNG, PDF, SVG, EPS, etc.).

### Lines of Code
| File | Lines |
|------|-------|
| plotdialog.h | 25 |
| plotdialog.cc | 885 |
| **Total** | **910** |

### Key Functions

#### Dialog Lifecycle
| Function | Description |
|----------|-------------|
| get_plot_dialog() | Lazy-initializes from plot.ui, sets up GtkTreeView and callbacks. |
| show_plot_dialog(parent, text) | Opens dialog, pre-fills expression. Shows Gnuplot-not-found error if unavailable. |
| hide_plot_dialog() | Hides the dialog. |
| is_plot_dialog(w) | Checks if a window is the plot dialog. |

#### Plot Data Management
| Function | Description |
|----------|-------------|
| generate_plot_series(x_vec, y_vec, type, str, str_x) | Core: uses CALCULATOR->expressionToPlotVector() or CALCULATOR->calculate(). |
| generate_plot(pp, y_vectors, x_vectors, pdps) | Collects tree store entries into PlotParameters and PlotDataParameters. |

#### Actions
| Function | Description |
|----------|-------------|
| on_plot_button_add_clicked | Validates, generates series, adds to GtkListStore, calls update_plot(). |
| on_plot_button_modify_clicked | Updates existing entry with new expression/settings. |
| on_plot_button_remove_clicked | Removes entry, frees MathStructure vectors, calls update_plot(). |
| update_plot() | Calls CALCULATOR->plotVectors() with current parameters. |
| on_plot_button_save_clicked | File chooser, then CALCULATOR->plotVectors() to save to file. |
| on_plot_button_range_apply_clicked | Re-generates all series with current min/max/step. |

### Calculator Interaction
generate_plot_series() -> CALCULATOR->expressionToPlotVector() or CALCULATOR->calculate()
update_plot()/save -> CALCULATOR->plotVectors() + CALCULATOR->closeGnuplot()

### Default Settings (persisted globally)
- default_plot_style = PLOT_STYLE_LINES
- default_plot_smoothing = PLOT_SMOOTHING_NONE
- default_plot_legend_placement = PLOT_LEGEND_TOP_RIGHT
- default_plot_sampling_rate = 1001
- default_plot_linewidth = 2
- max_plot_time = 5 seconds (configurable 1-600s)
- Range: min=0, max=10, step=1, variable=x

### Architecture Notes
- Uses GtkListStore (10 columns) as model for plot function list
- Three data types: function (type 0), vector (type 1), paired (type 2)
- Matrix results can be auto-split into multiple plot series
- Plot data (MathStructure pointers) stored in list store, freed on hide/remove
- Requires Gnuplot installed separately (checked via CALCULATOR->canPlot())

---

## 3. Import CSV Dialog (importcsvdialog.h / importcsvdialog.cc)

### Purpose
Provides a dialog for importing CSV files as variables (matrices or vectors) into the calculator variable store. Supports configurable delimiters, first-row header detection, and categorization.

### Lines of Code
| File | Lines |
|------|-------|
| importcsvdialog.h | 19 |
| importcsvdialog.cc | 201 |
| **Total** | **220** |

### Key Functions
| Function | Description |
|----------|-------------|
| get_csv_import_dialog() | Lazy-initializes from csvimport.ui, populates category combo. |
| import_csv_file(parent) | Main workflow: validates inputs, calls CALCULATOR->importCSV(), refreshes variable menu. |
| on_csv_import_button_file_clicked | Opens file chooser. Auto-populates name from filename. |
| on_csv_import_combobox_delimiter_changed | Enables/disables the other delimiter entry field. |

### Calculator Interaction
import_csv_file() -> CALCULATOR->importCSV(filename, first_row, has_headers, delimiter, as_matrix, name, description, category) -> display_errors() -> update_vmenu()

### Dialog Fields
- File path (with file chooser)
- Variable name (auto-populated from filename)
- Description (optional)
- Category (combo from existing variable categories)
- First row (spin button for header row)
- Delimiter (comma/tab/semicolon/space/other)
- Headers checkbox
- Output format (matrix vs. vectors)

### Architecture Notes
- Uses goto run_csv_import_dialog for validation loops
- Category combo built using hash table deduplication
- CALCULATOR->variableNameTaken() offers to overwrite existing variables

---

## 4. Export CSV Dialog (exportcsvdialog.h / exportcsvdialog.cc)

### Purpose
Provides a dialog for exporting matrix/vector data from the calculator to CSV files. Supports exporting either the current result or a named variable, with configurable delimiters.

### Lines of Code
| File | Lines |
|------|-------|
| exportcsvdialog.h | 21 |
| exportcsvdialog.cc | 203 |
| **Total** | **224** |

### Key Functions
| Function | Description |
|----------|-------------|
| get_csv_export_dialog() | Lazy-initializes from csvexport.ui. |
| export_csv_file(win, v) | Main workflow: validates, resolves source matrix, calls CALCULATOR->exportCSV(). |
| on_csv_export_button_file_clicked | Opens save-file chooser dialog. |
| on_csv_export_radiobutton_current_toggled | Toggles between current-result and named-variable source. |

### Calculator Interaction
export_csv_file() -> CALCULATOR->startControl(600000) -> CALCULATOR->exportCSV(matrix_struct, filename, delimiter) -> CALCULATOR->stopControl()

### Data Source Options
1. Current result - uses current_result() if it is a vector
2. Named variable - looks up a KnownVariable by name
3. Pre-selected variable - when called with KnownVariable* parameter

### Architecture Notes
- When called from variables dialog, UI elements are locked
- Uses startControl()/stopControl() for long-running export (600s timeout)
- Same goto validation loop pattern as import dialog

---

## 5. Preferences Dialog (preferencesdialog.h / preferencesdialog.cc)

### Purpose
The comprehensive application preferences dialog. Manages all user-configurable settings: appearance (fonts, colors, themes), calculator behavior (decimal comma, temperature calculation, exchange rates), expression editing (completion, parsing mode), display options (unicode signs, multiplication/division signs, digit grouping, two's complement), history management, and system integration (system tray, multiple instances).

### Lines of Code
| File | Lines |
|------|-------|
| preferencesdialog.h | 35 |
| preferencesdialog.cc | 1,228 |
| **Total** | **1,263** |

### Key Functions

#### Dialog Management
| Function | Description |
|----------|-------------|
| get_preferences_dialog() | Lazy-initializes from preferences.ui. Sets up all widgets. Registers ~80+ callbacks. |
| edit_preferences(parent, tab) | Shows dialog, optionally navigating to specific tab. |

#### State Synchronization (bidirectional)
| Function | Description |
|----------|-------------|
| preferences_update_twos_complement(initial) | Syncs two's complement checkbox state. |
| preferences_update_temperature_calculation(initial) | Syncs temperature calculation mode. |
| preferences_update_dot(initial) | Syncs decimal comma/point/dot-as-separator. |
| preferences_update_persistent_keypad() | Syncs persistent keypad toggle. |
| preferences_update_keep_above() | Syncs always-on-top toggle. |
| preferences_update_expression_status() | Syncs expression status display. |
| preferences_update_exchange_rates() | Syncs exchange rates frequency. |
| preferences_update_completion(initial) | Syncs completion settings. |
| preferences_rpn_mode_changed() | Updates parsed-in-result sensitivity. |
| preferences_parsing_mode_changed() | Updates RPN keys sensitivity. |

#### Callback Categories

Appearance (~20 callbacks):
- Font selection: result, expression, status, keypad, history, app
- Color selection: text, status error, status warning
- Theme: Adwaita/Light/Dark/HighContrast/HighContrastInverse
- Expression highlight background, cursor blinking

Calculator Behavior (~15 callbacks):
- Decimal comma toggle, dot/comma as separator
- Binary prefixes, local currency conversion
- Temperature calculation mode (absolute/relative/hybrid)
- Save defs/mode on exit, exchange rates frequency
- Custom digit grouping (separator + group size)

Display Options (~20 callbacks):
- Unicode signs toggle
- Multiplication sign (dot/alt-dot/x/asterisk)
- Division sign (slash/division-slash/division)
- E notation (uppercase E/lowercase E/power of 10)
- Two's complement (output + input, binary + hex)
- Binary bit width, imaginary j toggle
- Lower case numbers, duodecimal symbols
- Repeating decimal overline, spell out logical operators

Expression and History (~10 callbacks):
- Display expression status, parsed-in-result
- Expression position (top/bottom)
- Autocalc history delay (cubic scale: 0-10s)
- History expression type, replace expression mode
- Copy ASCII, copy ASCII without units

System (~5 callbacks):
- Language selection (15 languages), ignore locale
- Title bar format
- System tray icon, hide on startup
- Allow multiple instances, close with Escape
- Remember position, always on top

### Calculator Interaction
CALCULATOR->useDecimalComma(), useDecimalPoint(), useBinaryPrefixes(), setLocalCurrency(), setTemperatureCalculationMode(), v_i->addName('j'), evalops.parse_options.*, printops.*

### Architecture Notes
- Dialog uses GtkNotebook (tabbed interface)
- Callback registration is single massive gtk_builder_add_callback_symbols() with ~80+ pairs
- Uses signal blocking/unblocking extensively to prevent infinite update loops
- Theme switching uses GTK CSS providers
- Language change requires application restart
- Custom digit grouping saves/restores locale-specific settings

---

## Summary Table

| Component | Header LOC | Source LOC | Total LOC | Calculator API Entry Points |
|-----------|-----------|-----------|-----------|----------------------------|
| Menubar | 66 | 2,709 | **2,775** | CALCULATOR->*, evalops.*, printops.*, executeCommand(), convert_result_to_unit() |
| Plot Dialog | 25 | 885 | **910** | expressionToPlotVector(), plotVectors(), calculate(), canPlot(), closeGnuplot() |
| Import CSV | 19 | 201 | **220** | importCSV(), variableNameTaken(), getActiveVariable() |
| Export CSV | 21 | 203 | **224** | exportCSV(), startControl()/stopControl(), getActiveVariable() |
| Preferences | 35 | 1,228 | **1,263** | useDecimalComma(), useDecimalPoint(), useBinaryPrefixes(), setLocalCurrency(), setTemperatureCalculationMode() |
| **TOTAL** | **166** | **5,226** | **5,392** | |

---

## Architectural Patterns

1. **Lazy Initialization**: All dialogs use get_*_dialog() pattern -- singleton widgets created on first use via GtkBuilder.
2. **GtkBuilder UI**: All dialogs defined in .ui XML files and loaded via getBuilder().
3. **Signal Block/Unblock**: Used pervasively to prevent infinite callback loops when programmatically updating widget state.
4. **Global State**: Calculator settings live in global variables (evalops, printops) and CALCULATOR->* methods, not in the dialog.
5. **Callback Registration**: Each dialog registers callbacks in a single massive gtk_builder_add_callback_symbols() call.
6. **Settings Persistence**: Dialogs implement read_*_settings_line() / write_*_settings() for config file serialization.
7. **Validation Loops**: Import/export dialogs use goto run_*_dialog for re-showing on validation failure.
8. **Category Tree Walking**: Menubar uses tree_struct reverse iterators to build hierarchical menus from category trees.
