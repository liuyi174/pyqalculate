# Keypad Module Analysis (keypad.cc/h)

## Purpose
The keypad module implements the calculator on-screen button keypad -- both the versatile (general-purpose) keypad and the programming keypad. It handles all button click/right-click/middle-click events, custom button configuration, expression editing via buttons, number base switching, result base display, and the complex set of contextual menus (SI units, currencies, trig functions, etc.).

## Files
- keypad.cc: 3,775 lines
- keypad.h: 71 lines
- Total: 3,846 lines

## Key Data Structures

### custom_button (keypad.h:25-29)
A struct with type[3] (action type for left/right/middle click, -1=default), value[3] (argument for each), and text (custom label). 49 buttons (indices 0-48) stored in vector<custom_button> custom_buttons.

- Buttons 0-1: navigation (cursor movement, history)
- Buttons 2-28: standard calculator buttons (%, paren, digits, operators, =)
- Buttons 29-48: user-configurable custom buttons (C1-C20)

### Global State Variables
- visible_keypad: Bitmask (PROGRAMMING_KEYPAD=1, HIDE_LEFT_KEYPAD=2, HIDE_RIGHT_KEYPAD=4)
- programming_inbase / programming_outbase: Saved number base on keypad switch
- versatile_exact: Exact mode state saved when entering programming mode
- latest_button_unit / latest_button_currency: Most recently used SI unit and currency
- result_bases, result_bin/oct/dec/hex: Multi-base result display state

## Key Functions

### Initialization
- create_keypad() (3603-3775): Main initialization -- CSS providers, signal handlers, button styling, custom button visibility
- create_button_menus() (674-1031): Builds all context menus: trig, factorial, log, mod, stats, SI units, currencies, base ops, solve/simplify, pi, store
- initialize_custom_buttons() (123-134): Initializes 49 custom button slots to defaults
- set_custom_buttons() (639-672): Restores latest SI unit/currency button labels

### Button Click Handlers
- on_button_zero_clicked() through on_button_nine_clicked(): Insert digits with superscript/power Unicode
- on_button_add_clicked() through on_button_divide_clicked(): Arithmetic with RPN and chain mode
- on_button_execute_clicked(): Calls execute_expression()
- on_button_ac_clicked(): Clears expression entry
- on_button_del_clicked(): Deletes character or selection
- on_button_xy_clicked(): Power operator
- on_button_to_clicked(): Inserts conversion arrow

### Multi-click Button Logic
- on_keypad_button_button_event(): Core event handler -- left-click with 500ms long-press timeout, right-click, middle-click dispatch
- on_keypad_button_alt(): Dispatches right-click (b2=false) and middle-click (b2=true) for ALL buttons
- keypad_long_press_timeout(): 500ms timer fires on_keypad_button_alt() for long-press

### Programming Keypad
- on_button_programmers_keypad_toggled(): Switches keypads, saves/restores number bases
- on_button_bin_toggled() through on_button_hex_toggled(): Set input+output base
- update_keypad_programming_base(): Syncs toggle button states, underlines active bases, enables hex A-F
- set_result_bases(): Computes bin/oct/dec/hex strings for multi-base display
- update_result_bases(): Formats multi-base result label with overflow to 2 rows

### Custom Button System
- update_custom_buttons(): Updates labels/tooltips/visibility for all 49 buttons
- DO_CUSTOM_BUTTONS(i) macro: Checks custom action before default button behavior
- read_keypad_settings_line() / write_keypad_settings(): Settings persistence

### State Synchronization
- update_keypad_state(): Syncs toggle buttons with calculator state
- update_keypad_exact(): Syncs exact toggle with evalops.approximation
- update_keypad_fraction(): Syncs fraction toggle with printops.number_fraction_format
- update_keypad_angle(): Syncs trig angle unit menus
- update_keypad_base(): Syncs output base combo with printops.base
- keypad_rpn_mode_changed(): Changes = button to ENTER in RPN mode

### Assumption Menus (x, y, z)
set_[xyz]_assumptions_items() plus ~30 on_menu_item_[xyz]_*_activate() handlers manage type (boolean/integer/rational/real/complex/number) and sign (positive/nonnegative/negative/nonpositive/nonzero/unknown) of unknown variables via CALCULATOR->getActiveVariable().

### Popup Menus
- update_mb_fx_menu(): User functions + recent functions
- update_mb_sto_menu(): User variables + memory operations (MC/MR/MS/M+/M-)
- update_mb_units_menu(): Recent + SI base units + prefixes
- update_mb_pi_menu(): Pi, euler, golden ratio + recent + physical constants
- update_mb_to_menu(): Completion-based conversion menu with currency flags

## Calculator Interaction
- Uses global CALCULATOR for function/variable/unit lookup and formatting
- Uses global evalops for parsing state (base, angle, approximation, structuring)
- Uses global printops for display state (base, unicode, fractions, notation)
- Delegates to expression edit: insert_text(), insert_button_function(), insert_variable(), insert_unit()
- Delegates to calculation: execute_expression(), executeCommand(), calculateRPN()
- Memory: memory_clear/recall/store/add/subtract