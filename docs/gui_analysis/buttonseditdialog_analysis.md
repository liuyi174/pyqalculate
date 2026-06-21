# Buttons Edit Dialog Analysis (buttonseditdialog.cc/h)

## Purpose
The buttons edit dialog provides a preferences dialog for customizing the 49 keypad buttons. It allows users to reassign left-click, right-click, and middle-click actions for any keypad button, and to change button labels. It is the configuration UI for the custom_buttons[] system managed in keypad.cc.

## Files
- buttonseditdialog.cc: 521 lines
- buttonseditdialog.h: 19 lines
- Total: 540 lines

## Key Data Structures

### Dialog Widgets (lazily created)
- buttonsedit_builder (GtkBuilder*): Builder loaded from buttonsedit.ui
- tButtonsEdit (GtkWidget*): Main tree view listing all 49 customizable buttons
- tButtonsEdit_store (GtkListStore*): 5-column store: index(int), label(string), left-click(string), right-click(string), middle-click(string)
- tButtonsEditType (GtkWidget*): Action type selection tree view (sub-dialog)
- tButtonsEditType_store (GtkListStore*): 2-column store: action_name(string), type_code(int)

### External Reference
- custom_buttons (vector<custom_button>): The shared configuration array with keypad.cc

## Key Functions

### Dialog Lifecycle
- get_buttons_edit_dialog() (403-507): Lazy singleton factory. Creates dialog from UI file on first call. Initializes both tree views. Populates button list (custom 29-33 first, then standard 0-28, then custom 34-48). Populates action type list. Connects signal handlers
- edit_buttons(GtkWindow* parent) (509-521): Public API. Creates or shows dialog, sets transient parent, presents it

### Button List Display
- update_custom_buttons_edit() (341-402): Iterates tButtonsEdit_store and populates columns from custom_buttons[] state. Uses SET_BUTTONS_EDIT_ITEM macros for formatting
- on_tButtonsEdit_update_selection() (136-161): Updates editing panel on selection change: shows action button tooltips, populates label entry, enables/disables edit box

### Button Action Assignment
- on_buttonsedit_button_x_clicked(int b_i) (165-298): Core editing flow. Opens sub-dialog for assigning action to click type (0=left, 1=right, 2=middle). Handles Default option for custom buttons. On accept, validates value per action type. Shows error for invalid values. Writes to custom_buttons[i] and refreshes keypad
- on_buttons_edit_button_1_clicked() through _3_clicked() (299-307): Wrappers for on_buttonsedit_button_x_clicked(0/1/2)
- on_buttons_edit_button_defaults_clicked() (308-324): Resets selected button to defaults

### Label Editing
- on_buttons_edit_entry_label_changed() (124-135): Real-time label update: writes to custom_buttons[i].text, refreshes keypad and dialog

### Action Type Selection
- on_tButtonsEditType_selection_changed() (64-113): Shows/hides value entry vs combo box. Enables/disables value field based on whether action requires value

### Validation (in on_buttonsedit_button_x_clicked)
- FUNCTION / FUNCTION_WITH_DIALOG: CALCALATOR->getActiveFunction() must return non-null
- VARIABLE: CALCULATOR->getActiveVariable() must return non-null
- UNIT: CALCULATOR->getActiveUnit() checked, falls back to CompositeUnit construction
- META_MODE: mode_index() must return valid index
- TO_NUMBER_BASE / INPUT_BASE / OUTPUT_BASE: base_from_string() must produce valid base
- PRECISION: Must be >= 2 (or -1)
- MIN_DECIMALS / MAX_DECIMALS / MINMAX_DECIMALS: Must be numeric, >= -1
- COPY_RESULT: Combo index 0-7, no text entry
- TEXT: No validation

### Available Action Types
All SHORTCUT_TYPE_* constants from 0 to SHORTCUT_TYPE_QUIT, plus subtypes:
- SMART_PARENTHESES, CHAIN_MODE, INSERT_RESULT, HISTORY_CLEAR
- ALWAYS_ON_TOP, DO_COMPLETION, ACTIVATE_FIRST_COMPLETION
- PRECISION, MIN_DECIMALS, MAX_DECIMALS, MINMAX_DECIMALS
- "None" (type -2) at top for custom buttons only

## Calculator Interaction
- Uses CALCULATOR->getActiveFunction() to validate function names
- Uses CALCULATOR->getActiveVariable() to validate variable names
- Uses CALCULATOR->getActiveUnit() and CompositeUnit to validate units
- Does NOT directly perform calculations -- only validates names and stores config
- Configuration consumed by custom_buttons[] at runtime in keypad.cc