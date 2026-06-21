# Keyboard Shortcuts Specification

> **Source**: pyQalculate `qalculate-gtk` (`src/callbacks.cc`, `src/interface.cc`, `src/keyvalueparser.cc`)
> **Purpose**: Complete technical specification of the keyboard shortcut system, from the shortcut data structure through default bindings, hardcoded expression-edit shortcuts, custom rebinding, conflict resolution, and a Tkinter implementation guide.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Shortcut Struct Definition](#2-shortcut-struct-definition)
3. [Complete Shortcut Type Enum](#3-complete-shortcut-type-enum)
4. [Default Key Bindings](#4-default-key-bindings)
5. [Expression Edit Shortcuts (Hardcoded)](#5-expression-edit-shortcuts-hardcoded)
6. [Main Window Shortcuts](#6-main-window-shortcuts)
7. [Keypad Shortcuts](#7-keypad-shortcuts)
8. [Mode Shortcuts](#8-mode-shortcuts)
9. [Custom Shortcuts](#9-custom-shortcuts)
10. [Conflict Resolution](#10-conflict-resolution)
11. [Tkinter Implementation Guide](#11-tkinter-implementation-guide)

---

## 1. Overview

The keyboard shortcut system maps key combinations to calculator actions. There are three layers:

1. **Hardcoded shortcuts**: Expression-edit keys (Ctrl+Z/Y, Ctrl+A, Enter, Escape, etc.) that are always active when the expression entry has focus. These cannot be rebound.
2. **Default configurable shortcuts**: Application-level shortcuts (Ctrl+B for base dialog, F1 for help, etc.) that have defaults but can be rebound.
3. **Custom shortcuts**: User-defined bindings that override defaults.

The shortcut system is initialized at startup from the config file. Changes are saved immediately.

---

## 2. Shortcut Struct Definition

```c
typedef struct {
    guint key;              // GDK keyval (e.g., GDK_KEY_b, GDK_KEY_F1)
    guint modifier;         // GDK modifier mask (GDK_CONTROL_MASK, GDK_MOD1_MASK, etc.)
    ShortcutType type;      // The action type (enum)
    gchar *value;           // Optional string value (e.g., expression text for CUSTOM_TYPE)
} Shortcut;
```

### 2.1 Fields

| Field | Type | Description |
|---|---|---|
| `key` | `guint` | The GDK key symbol. For letter keys: `GDK_KEY_a` through `GDK_KEY_z`. For function keys: `GDK_KEY_F1` through `GDK_KEY_F12`. For special keys: `GDK_KEY_Return`, `GDK_KEY_Escape`, `GDK_KEY_Left`, etc. |
| `modifier` | `guint` | Bitmask of modifiers: `GDK_CONTROL_MASK` (Ctrl), `GDK_MOD1_MASK` (Alt), `GDK_SHIFT_MASK` (Shift), `GDK_SUPER_MASK` (Super/Win). Combined with bitwise OR. |
| `type` | `ShortcutType` | Enum identifying the action to perform. See Section 3. |
| `value` | `gchar *` | For `CUSTOM_TYPE` shortcuts, this is the expression text or command string to insert/execute. For other types, this is `NULL`. |

### 2.2 Default Shortcuts Array

```c
#define MAX_SHORTCUTS 80

Shortcut key_shortcuts[MAX_SHORTCUTS];
gint key_shortcuts_count = 0;
```

The array is populated at startup from the config file. Unset entries use default values.

---

## 3. Complete Shortcut Type Enum

```c
typedef enum {
    SHORTCUT_TYPE_NONE = 0,

    // Expression editing
    SHORTCUT_TYPE_UNDO,                 // "Undo"
    SHORTCUT_TYPE_REDO,                 // "Redo"
    SHORTCUT_TYPE_SELECT_ALL,           // "Select All"
    SHORTCUT_TYPE_CLEAR,                // "Clear Expression"
    SHORTCUT_TYPE_CLEAR_HISTORY,        // "Clear History"

    // Evaluation
    SHORTCUT_TYPE_EVALUATE,             // "Evaluate Expression"
    SHORTCUT_TYPE_EVALUATE_TO,          // "Evaluate and Convert To..."
    SHORTCUT_TYPEEXECUTE,               // "Execute Expression (without evaluation)"

    // Navigation
    SHORTCUT_TYPE_PREV_EXPRESSION,      // "Previous Expression (History)"
    SHORTCUT_TYPE_NEXT_EXPRESSION,      // "Next Expression (History)"
    SHORTCUT_TYPE_COMPLETE,             // "Autocomplete"
    SHORTCUT_TYPE_FUNCTION_LIST,        // "Show Function List"
    SHORTCUT_TYPE_VARIABLE_LIST,        // "Show Variable List"
    SHORTCUT_TYPE_UNIT_LIST,            // "Show Unit List"
    SHORTCUT_TYPE_CONSTANT_LIST,        // "Show Constant List"
    SHORTCUT_TYPE_DATASET_LIST,         // "Show Data Sets"

    // Dialogs
    SHORTCUT_TYPE_PREFERENCES,          // "Open Preferences"
    SHORTCUT_TYPE_BASE_DIALOG,          // "Open Base Conversion"
    SHORTCUT_TYPE_PLOT_DIALOG,          // "Open Plot Dialog"
    SHORTCUT_TYPE_PERIODIC_DIALOG,      // "Open Periodic Table"
    SHORTCUT_TYPE_PRECISION_DIALOG,     // "Open Precision Dialog"
    SHORTCUT_TYPE_SHORTCUTS_DIALOG,     // "Open Keyboard Shortcuts"
    SHORTCUT_TYPE_HELP_DIALOG,          // "Open Help"

    // Mode toggles
    SHORTCUT_TYPE_RPN_MODE,             // "Toggle RPN Mode"
    SHORTCUT_TYPE_BASE16,               // "Switch to Hexadecimal"
    SHORTCUT_TYPE_BASE10,               // "Switch to Decimal"
    SHORTCUT_TYPE_BASE8,                // "Switch to Octal"
    SHORTCUT_TYPE_BASE2,                // "Switch to Binary"
    SHORTCUT_TYPE Hexatrigesimal,              // "Switch to Base 36"
    SHORTCUT_TYPE_ANGLE_DEG,            // "Switch to Degrees"
    SHORTCUT_TYPE_ANGLE_RAD,            // "Switch to Radians"
    SHORTCUT_TYPE_ANGLE_GRAD,           // "Switch to Gradians"
    SHORTCUT_TYPE_EXACT_MODE,           // "Toggle Exact Mode"
    SHORTCUT_TYPE_LOCAL_ENCODING,       // "Toggle Local Number Encoding"

    // Clipboard
    SHORTCUT_TYPE_COPY,                 // "Copy Result"
    SHORTCUT_TYPE_COPY_RESULT,          // "Copy Result as Text"
    SHORTCUT_TYPE_COPY_RESULT_FORMATTED, // "Copy Result (Formatted)"
    SHORTCUT_TYPE_COPY_EXPRESSION,      // "Copy Expression"
    SHORTCUT_TYPE_COPY_UNICODE,         // "Copy Result as Unicode"
    SHORTCUT_TYPE_COPY_LATIN,           // "Copy Result as Latin"
    SHORTCUT_TYPE_PASTE,                // "Paste"
    SHORTCUT_TYPE_PASTE_CLIPBOARD,      // "Paste from Clipboard"
    SHORTCUT_TYPE_COPY_ASCII,           // "Copy as ASCII"
    SHORTCUT_TYPE_COPY_LATIN1,          // "Copy as Latin-1"
    SHORTCUT_TYPE_COPY_HTML,            // "Copy as HTML"
    SHORTCUT_TYPE_COPY_LATEX,           // "Copy as LaTeX"
    SHORTCUT_TYPE_COPY_MATHML,          // "Copy as MathML"

    // Insert
    SHORTCUT_TYPE_INSERT_TEXT,           // "Insert Text"
    SHORTCUT_TYPE_INSERT_FUNCTION,      // "Insert Function"
    SHORTCUT_TYPE_INSERT_VARIABLE,      // "Insert Variable"
    SHORTCUT_TYPE_INSERT_UNIT,          // "Insert Unit"
    SHORTCUT_TYPE_INSERT_MATRIX,        // "Insert Matrix"
    SHORTCUT_TYPE_INSERT_DATE,          // "Insert Date"
    SHORTCUT_TYPE_INSERT_PI,            // "Insert π"
    SHORTCUT_TYPE_INSERT_E,             // "Insert e"
    SHORTCUT_TYPE_INSERT_I,             // "Insert i"

    // Calculation
    SHORTCUT_TYPECALCULATE,              // "Calculate"
    SHORTCUT_TYPECALCULATE_TO,           // "Calculate and Convert To"
    SHORTCUT_TYPE_SIMPLIFY,              // "Simplify Expression"
    SHORTCUT_TYPE_EXPAND,                // "Expand Expression"
    SHORTCUT_TYPE_FACTORIZE,             // "Factorize Expression"
    SHORTCUT_TYPE_PARTIAL_FRACTIONS,     // "Partial Fractions"
    SHORTCUT_TYPE_CANCEL,                // "Cancel Calculation"

    // Display
    SHORTCUT_TYPE_RESULT_TO_CLIPBOARD,   // "Result to Clipboard"
    SHORTCUT_TYPE_SHOW_RESULT_STATUS,    // "Toggle Result Status Bar"
    SHORTCUT_TYPE_SHOW_EXPRESSION_STATUS, // "Toggle Expression Status Bar"
    SHORTCUT_TYPE_SHOW_HISTORY,          // "Toggle History"
    SHORTCUT_TYPE_SHOW_KEYPAD,           // "Toggle Keypad"
    SHORTCUT_TYPE_RECALCULATE,           // "Recalculate"
    SHORTCUT_TYPE_UPDATE_RESULT,         // "Update Result"

    // Application
    SHORTCUT_TYPE_QUIT,                 // "Quit Application"
    SHORTCUT_TYPE_NEW_WINDOW,           // "New Window"
    SHORTCUT_TYPE_FULL_SCREEN,          // "Toggle Full Screen"
    SHORTCUT_TYPE_MINIMIZE,             // "Minimize Window"

    // Custom
    SHORTCUT_TYPE_CUSTOM,               // "Custom Action" (uses value field)

    // Special
    SHORTCUT_TYPE_DO_NOT_USE,           // Reserved / disabled

    SHORTCUT_TYPE_COUNT                 // Total: ~75 types
} ShortcutType;
```

---

## 4. Default Key Bindings

| Key Combo | Type | Action |
|---|---|---|
| `Ctrl+Z` | UNDO | Undo last edit in expression entry |
| `Ctrl+Y` | REDO | Redo last undo |
| `Ctrl+A` | SELECT_ALL | Select all text in expression entry |
| `Ctrl+N` | CLEAR | Clear the expression entry |
| `Ctrl+H` | CLEAR_HISTORY | Clear the calculation history |
| `Enter` | EVALUATE | Evaluate the current expression |
| `Ctrl+Enter` | EVALUATE_TO | Evaluate and open "Convert To" dialog |
| `F1` | HELP_DIALOG | Open the help dialog |
| `Ctrl+Q` | QUIT | Quit the application |
| `Ctrl+B` | BASE_DIALOG | Open base conversion dialog |
| `Ctrl+P` | PREFERENCES | Open preferences dialog |
| `Ctrl+L` | FUNCTION_LIST | Open function list dialog |
| `Ctrl+Shift+V` | VARIABLE_LIST | Open variable list dialog |
| `Ctrl+U` | UNIT_LIST | Open unit list dialog |
| `Ctrl+D` | CONSTANT_LIST | Open constant list dialog |
| `Ctrl+Alt+C` | COPY_RESULT | Copy result to clipboard |
| `Ctrl+Shift+C` | COPY_EXPRESSION | Copy expression to clipboard |
| `Ctrl+V` | PASTE | Paste from clipboard |
| `Ctrl+G` | PLOT_DIALOG | Open plot dialog |
| `Ctrl+I` | PERIODIC_DIALOG | Open periodic table |
| `Ctrl+F` | SHORTCUTS_DIALOG | Open shortcuts dialog |
| `Escape` | CANCEL | Cancel ongoing calculation |
| `Ctrl+E` | EXACT_MODE | Toggle exact/approximate mode |
| `Ctrl+R` | RPN_MODE | Toggle RPN input mode |
| `Up` | PREV_EXPRESSION | Navigate to previous expression in history |
| `Down` | NEXT_EXPRESSION | Navigate to next expression in history |
| `F2` | BASE16 | Switch to hexadecimal |
| `F3` | BASE10 | Switch to decimal |
| `F4` | BASE8 | Switch to octal |
| `F5` | BASE2 | Switch to binary |
| `Ctrl+M` | INSERT_MATRIX | Insert matrix dialog |
| `Ctrl+Insert` | INSERT_DATE | Insert current date |
| `Ctrl+Shift+P` | PRECISION_DIALOG | Open precision dialog |

> Note: Not all of these are active by default. Some are defined but assigned to `SHORTCUT_TYPE_NONE` until the user configures them. The table above shows the canonical defaults.

---

## 5. Expression Edit Shortcuts (Hardcoded)

These shortcuts are handled directly in the expression entry's key-press event handler. They cannot be rebound or disabled.

### 5.1 Text Editing

| Key | Action | Behavior |
|---|---|---|
| `Ctrl+Z` | Undo | `gtk_editable_undo()` |
| `Ctrl+Y` | Redo | `gtk_editable_redo()` |
| `Ctrl+A` | Select All | `gtk_editable_select_region(0, -1)` |
| `Ctrl+X` | Cut | Standard GTK cut |
| `Ctrl+C` | Copy | Standard GTK copy |
| `Ctrl+V` | Paste | Standard GTK paste |

### 5.2 Operator Keys

| Key | Inserted Text | Behavior |
|---|---|---|
| `+` | `+` | Insert operator with spacing |
| `-` | `-` | Insert operator with spacing |
| `*` | `*` | Insert multiplication |
| `/` | `/` | Insert division |
| `^` | `^` | Insert exponentiation |
| `=` | `=` | Insert equality (for equations) |
| `<` | `<` | Insert less-than |
| `>` | `>` | Insert greater-than |
| `!` | `!` | Insert factorial |
| `(` | `(` | Insert with auto-matching `)` |
| `)` | `)` | Insert; skip over existing `)` if present |
| `[` | `[` | Insert matrix/vector bracket |
| `]` | `]` | Insert closing bracket |

### 5.3 Special Keys

| Key | Action | Behavior |
|---|---|---|
| `Escape` | Clear/Cancel | If expression has text: clear it. If empty: cancel calculation. |
| `Enter` | Evaluate | Evaluate the expression. If completion popup is visible: insert selected item instead. |
| `Up` | History prev | If completion popup visible: move selection up in popup. Else: previous expression from history. |
| `Down` | History next | If completion popup visible: move selection down in popup. Else: next expression from history. |
| `Home` | Start of line | Move cursor to beginning of expression |
| `End` | End of line | Move cursor to end of expression |
| `Backspace` | Delete backward | Standard; special behavior: deletes matching parenthesis pair if cursor is between `()` |
| `Delete` | Delete forward | Standard; special behavior: deletes matching parenthesis pair if cursor is between `()` |
| `Tab` | Autocomplete | If popup visible: insert selected item. Else: trigger autocomplete. |
| `Page_Up` | Scroll up | Scroll expression entry if multi-line |
| `Page_Down` | Scroll down | Scroll expression entry if multi-line |

### 5.4 Hardcoded Override Rule

```c
gboolean on_expression_key_press(GtkWidget *widget, GdkEventKey *event, gpointer data) {
    // Check hardcoded shortcuts FIRST
    if(event->state & GDK_CONTROL_MASK) {
        switch(event->keyval) {
            case GDK_KEY_z: do_undo(); return TRUE;   // consumed
            case GDK_KEY_y: do_redo(); return TRUE;   // consumed
            case GDK_KEY_a: select_all(); return TRUE; // consumed
            // ... etc
        }
    }

    // If not consumed by hardcoded, check configurable shortcuts
    for(gint i = 0; i < key_shortcuts_count; i++) {
        if(event->keyval == key_shortcuts[i].key &&
           (event->state & key_shortcuts[i].modifier)) {
            execute_shortcut(&key_shortcuts[i]);
            return TRUE;
        }
    }

    return FALSE;  // let GTK handle it normally
}
```

---

## 6. Main Window Shortcuts

These shortcuts are handled at the main window level (not the expression entry). They fire when any widget in the main window has focus.

| Key Combo | Action |
|---|---|
| `Ctrl+Q` | Quit application |
| `Ctrl+N` | New window |
| `F11` | Toggle full screen |
| `Ctrl+comma` | Toggle keypad visibility |
| `Ctrl+H` | Toggle history pane |
| `Ctrl+F` | Open keyboard shortcuts dialog |
| `Ctrl+P` | Open preferences |

---

## 7. Keypad Shortcuts

The on-screen keypad buttons have optional keyboard equivalents. These are not standard keyboard shortcuts but rather key-to-button mappings that can be configured.

| Key | Keypad Button | Category |
|---|---|---|
| `0`-`9` | Digit buttons | Numbers |
| `.` or `,` | Decimal separator | Numbers |
| `+` | Addition | Operators |
| `-` | Subtraction | Operators |
| `*` | Multiplication | Operators |
| `/` | Division | Operators |
| `^` | Power | Operators |
| `(` | Left parenthesis | Grouping |
| `)` | Right parenthesis | Grouping |
| `Enter` | Equals / Evaluate | Action |

> Note: These overlap with the hardcoded expression-edit shortcuts. The keypad shortcuts are only active when the keypad widget has focus (which is rare since focus usually stays in the expression entry).

---

## 8. Mode Shortcuts

Mode shortcuts change the calculator's operating mode:

| Key Combo | Mode Change | Side Effects |
|---|---|---|
| `F2` | Base → Hexadecimal | Updates base indicator badge, reformats result |
| `F3` | Base → Decimal | Updates base indicator badge |
| `F4` | Base → Octal | Updates base indicator badge |
| `F5` | Base → Binary | Updates base indicator badge |
| `Ctrl+E` | Toggle Exact/Approx | Switches between exact and approximate evaluation |
| `Ctrl+R` | Toggle RPN Mode | Switches input mode, changes keypad layout |
| `Ctrl+Shift+A` | Angle → Degrees | Updates angle unit |
| `Ctrl+Shift+B` | Angle → Radians | Updates angle unit |
| `Ctrl+Shift+G` | Angle → Gradians | Updates angle unit |

---

## 9. Custom Shortcuts

### 9.1 Rebinding

Users can rebind any configurable shortcut through the Keyboard Shortcuts dialog:

1. Open shortcuts dialog (`Ctrl+F`).
2. Select the action in the list.
3. Click the "Key" cell to edit.
4. Press the desired key combination.
5. The new binding is stored in the config file immediately.

### 9.2 Multi-Action Shortcuts

Custom shortcuts (`SHORTCUT_TYPE_CUSTOM`) can execute arbitrary expression text:

```
Shortcut: Ctrl+Shift+M
Type: CUSTOM
Value: "to hex"
```

When triggered, the value string is inserted into the expression entry and (optionally) evaluated.

### 9.3 Config Persistence

Custom shortcuts are saved in the `[SHORTCUTS]` section of the config file:

```ini
[SHORTCUTS]
# Format: action_index = keyval,modifier[,value]
0 = 122,4       # Ctrl+Z → Undo (keyval=0x007a, modifier=GDK_CONTROL_MASK=4)
1 = 121,4       # Ctrl+Y → Redo
42 = 98,4       # Ctrl+B → Base Dialog
# Custom shortcut:
75 = 109,5,1,0  # Ctrl+Shift+M → Custom "to hex" (type=75=CUSTOM, value="to hex")
```

### 9.4 Reading from Config

```c
void load_shortcuts_from_config(GKeyFile *config) {
    key_shortcuts_count = 0;
    gchar **keys = g_key_file_get_keys(config, "SHORTCUTS", NULL, NULL);
    if(!keys) {
        set_default_shortcuts();
        return;
    }
    for(gint i = 0; keys[i]; i++) {
        gint idx = atoi(keys[i]);
        if(idx < 0 || idx >= MAX_SHORTCUTS) continue;
        gchar *val = g_key_file_get_string(config, "SHORTCUTS", keys[i], NULL);
        if(!val) continue;
        // Parse: "keyval,modifier[,value]"
        gchar **parts = g_strsplit(val, ",", -1);
        key_shortcuts[idx].key = atoi(parts[0]);
        key_shortcuts[idx].modifier = atoi(parts[1]);
        key_shortcuts[idx].type = idx_to_type(idx);
        if(parts[2]) key_shortcuts[idx].value = g_strdup(parts[2]);
        g_strfreev(parts);
        g_free(val);
    }
    g_strfreev(keys);
}
```

---

## 10. Conflict Resolution

### 10.1 Conflict Detection

When the user assigns a new key combination, the system checks for conflicts:

```c
gboolean shortcut_conflict(guint key, guint modifier, gint exclude_index) {
    for(gint i = 0; i < key_shortcuts_count; i++) {
        if(i == exclude_index) continue;
        if(key_shortcuts[i].key == key &&
           key_shortcuts[i].modifier == modifier) {
            return TRUE;  // conflict found
        }
    }
    return FALSE;
}
```

### 10.2 Resolution Strategies

| Strategy | Behavior |
|---|---|
| **Last-write-wins** (default) | The new binding replaces the old one. The previous action becomes unbound. |
| **Warn and confirm** | If a conflict is detected, show a dialog: "This key is already bound to [Action]. Rebind?" |
| **Auto-swap** | Swap the two bindings: new action gets the key, old action gets whatever the new action had before. |

The default strategy is **last-write-wins** with a warning dialog.

### 10.3 Protected Bindings

Some bindings cannot be overridden:
- `Ctrl+Z` (Undo) — hardcoded in expression entry
- `Ctrl+C` (Copy) — system clipboard
- `Ctrl+V` (Paste) — system clipboard
- `Ctrl+A` (Select All) — hardcoded in expression entry

If the user attempts to bind one of these, the system shows: "This key combination is reserved and cannot be reassigned."

---

## 11. Tkinter Implementation Guide

### 11.1 Shortcut Data Structure

```python
from dataclasses import dataclass, field
from typing import Optional, Callable

@dataclass
class Shortcut:
    key: str              # Tkinter key name: "z", "F1", "Return", etc.
    modifier: str         # Modifier string: "Control", "Alt", "Shift", or combo "Control-Alt"
    type: str             # Action type string matching ShortcutType enum name
    value: Optional[str] = None  # For CUSTOM type

    @property
    def binding_string(self) -> str:
        """Returns Tkinter bind format: <Control-Alt-z>"""
        parts = []
        if "Control" in self.modifier: parts.append("Control")
        if "Alt" in self.modifier: parts.append("Alt")
        if "Shift" in self.modifier: parts.append("Shift")
        parts.append(self.key)
        return "<" + "-".join(parts) + ">"
```

### 11.2 Default Shortcuts

```python
DEFAULT_SHORTCUTS = [
    Shortcut("z", "Control", "UNDO"),
    Shortcut("y", "Control", "REDO"),
    Shortcut("a", "Control", "SELECT_ALL"),
    Shortcut("n", "Control", "CLEAR"),
    Shortcut("Return", "", "EVALUATE"),
    Shortcut("Return", "Control", "EVALUATE_TO"),
    Shortcut("F1", "", "HELP_DIALOG"),
    Shortcut("q", "Control", "QUIT"),
    Shortcut("b", "Control", "BASE_DIALOG"),
    Shortcut("p", "Control", "PREFERENCES"),
    Shortcut("l", "Control", "FUNCTION_LIST"),
    Shortcut("v", "Control-Shift", "VARIABLE_LIST"),
    Shortcut("u", "Control", "UNIT_LIST"),
    Shortcut("d", "Control", "CONSTANT_LIST"),
    Shortcut("c", "Control-Alt", "COPY_RESULT"),
    Shortcut("c", "Control-Shift", "COPY_EXPRESSION"),
    Shortcut("g", "Control", "PLOT_DIALOG"),
    Shortcut("i", "Control", "PERIODIC_DIALOG"),
    Shortcut("Escape", "", "CANCEL"),
    Shortcut("e", "Control", "EXACT_MODE"),
    Shortcut("r", "Control", "RPN_MODE"),
    Shortcut("F2", "", "BASE16"),
    Shortcut("F3", "", "BASE10"),
    Shortcut("F4", "", "BASE8"),
    Shortcut("F5", "", "BASE2"),
    Shortcut("m", "Control", "INSERT_MATRIX"),
    Shortcut("Insert", "Control", "INSERT_DATE"),
    Shortcut("p", "Control-Shift", "PRECISION_DIALOG"),
    # ... more defaults
]
```

### 11.3 Shortcut Manager

```python
class ShortcutManager:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.shortcuts: dict[str, Shortcut] = {}  # binding_string → Shortcut
        self.handlers: dict[str, Callable] = {}    # type → handler function
        self._load_from_config()

    def register_handler(self, action_type: str, handler: Callable):
        """Register a handler function for an action type."""
        self.handlers[action_type] = handler

    def bind_shortcut(self, shortcut: Shortcut):
        """Bind a shortcut to the root window."""
        binding = shortcut.binding_string
        # Remove existing binding for this key combo
        self.root.unbind_all(binding)
        # Bind new
        self.root.bind_all(binding, lambda e: self._execute(shortcut))
        self.shortcuts[binding] = shortcut

    def _execute(self, shortcut: Shortcut):
        """Execute the action for a shortcut."""
        handler = self.handlers.get(shortcut.type)
        if handler:
            if shortcut.value:
                handler(shortcut.value)
            else:
                handler()

    def rebind(self, old_shortcut: Shortcut, new_key: str, new_modifier: str):
        """Rebind a shortcut to a new key combination."""
        # Check for conflicts
        new_binding = Shortcut(new_key, new_modifier, "").binding_string
        existing = self.shortcuts.get(new_binding)
        if existing and existing.type != "DO_NOT_USE":
            if not self._confirm_conflict(existing):
                return False

        # Remove old binding
        old_binding = old_shortcut.binding_string
        if old_binding in self.shortcuts:
            self.root.unbind_all(old_binding)
            del self.shortcuts[old_binding]

        # Apply new binding
        old_shortcut.key = new_key
        old_shortcut.modifier = new_modifier
        self.bind_shortcut(old_shortcut)
        self._save_to_config()
        return True

    def _confirm_conflict(self, existing: Shortcut) -> bool:
        """Show conflict dialog, return True if user confirms rebinding."""
        from tkinter import messagebox
        return messagebox.askyesno(
            "Shortcut Conflict",
            f"This key is already bound to '{existing.type}'. Rebind?"
        )

    def _load_from_config(self):
        """Load shortcuts from config file."""
        import configparser
        config = configparser.ConfigParser()
        config.read("qalculate-tk.conf")

        if "SHORTCUTS" in config:
            for key, value in config["SHORTCUTS"].items():
                idx = int(key)
                parts = value.split(",")
                s = Shortcut(parts[0], parts[1], DEFAULT_SHORTCUTS[idx].type,
                             parts[2] if len(parts) > 2 else None)
                self.bind_shortcut(s)
        else:
            for s in DEFAULT_SHORTCUTS:
                self.bind_shortcut(s)

    def _save_to_config(self):
        """Save current shortcuts to config file."""
        import configparser
        config = configparser.ConfigParser()
        config.read("qalculate-tk.conf")

        if not config.has_section("SHORTCUTS"):
            config.add_section("SHORTCUTS")

        for binding, shortcut in self.shortcuts.items():
            idx = self._type_to_index(shortcut.type)
            val = f"{shortcut.key},{shortcut.modifier}"
            if shortcut.value:
                val += f",{shortcut.value}"
            config.set("SHORTCUTS", str(idx), val)

        with open("qalculate-tk.conf", "w") as f:
            config.write(f)
```

### 11.4 Expression Edit Hardcoded Shortcuts

```python
class ExpressionEdit:
    def __init__(self, parent):
        self.entry = tk.Entry(parent, font=("Georgia", 14))
        self.entry.bind("<KeyPress>", self._on_key)

        # Hardcoded bindings (always active, cannot be rebound)
        self.entry.bind("<Control-z>", lambda e: self._undo())
        self.entry.bind("<Control-y>", lambda e: self._redo())
        self.entry.bind("<Control-a>", lambda e: self._select_all())
        self.entry.bind("<Escape>", lambda e: self._clear_or_cancel())
        self.entry.bind("<Return>", lambda e: self._evaluate())
        self.entry.bind("<Up>", lambda e: self._history_prev())
        self.entry.bind("<Down>", lambda e: self._history_next())
        self.entry.bind("<Home>", lambda e: self._go_to_start())
        self.entry.bind("<End>", lambda e: self._go_to_end())
        self.entry.bind("<Tab>", lambda e: self._autocomplete())
        self.entry.bind("<BackSpace>", lambda e: self._smart_backspace())
        self.entry.bind("<Delete>", lambda e: self._smart_delete())

        # Operator shortcuts (insert with spacing)
        for op, text in [("+", " + "), ("-", " - "), ("*", " * "),
                          ("/", " / "), ("^", "^"), ("=", " = "),
                          ("<", " < "), (">", " > "), ("!", "!")]:
            self.entry.bind(op, lambda e, t=text: self._insert_operator(t))

        # Parentheses with auto-match
        self.entry.bind("(", lambda e: self._insert_paired("(", ")"))
        self.entry.bind(")", lambda e: self._skip_or_insert(")"))

    def _on_key(self, event):
        """Master key handler: hardcoded first, then configurable."""
        # Hardcoded shortcuts are already bound above
        # This handler catches everything else
        pass
```

### 11.5 Config Persistence

```python
# Config file format (INI):
# [SHORTCUTS]
# 0 = z,Control,
# 1 = y,Control,
# 4 = b,Control,
# 25 = Return,,EVALUATE
# 75 = m,Control-Shift,to hex  # custom shortcut

def load_shortcuts_config(path="qalculate-tk.conf"):
    import configparser
    config = configparser.ConfigParser()
    config.read(path)
    shortcuts = []
    if "SHORTCUTS" in config:
        for idx_str, val in config["SHORTCUTS"].items():
            idx = int(idx_str)
            parts = val.split(",", 2)
            key = parts[0]
            modifier = parts[1] if len(parts) > 1 else ""
            value = parts[2] if len(parts) > 2 else None
            action_type = INDEX_TO_TYPE.get(idx, "NONE")
            shortcuts.append(Shortcut(key, modifier, action_type, value))
    return shortcuts
```

---

*End of Keyboard Shortcuts Specification*
