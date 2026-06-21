# Expression Edit - qalculate-gtk Analysis

**Files:**
- `D:\1\1tmp\qalculate-gtk\src\expressionedit.h` (109 lines)
- `D:\1\1tmp\qalculate-gtk\src\expressionedit.cc` (1970 lines)
- **Total: 2079 lines**

## What It Does

The expression edit module implements the **mathematical expression input field** - the primary user input area where users type mathematical expressions before evaluation. It is a GTK `GtkTextView`-based editor with rich functionality beyond simple text input.

## Architecture

### Key Global State (File-scope Variables)

| Variable | Type | Purpose |
|----------|------|---------|
| `expressiontext` | `GtkWidget*` | The main text view widget |
| `expressionbuffer` | `GtkTextBuffer*` | The underlying text buffer |
| `expression_par_tag` / `expression_par_u_tag` | `GtkTextTag*` | Tags for parenthesis highlighting (matched/unmatched) |
| `expression_lines` | `int` | Configurable line height (-1 = default 3 lines) |
| `expression_undo_buffer` | `deque<string>` | Undo/redo stack (max 100 entries) |
| `undo_index` | `size_t` | Current position in undo buffer |
| `expression_history` | `vector<string>` | Up/Down arrow history (max 100 entries) |
| `expression_history_index` | `int` | Current position in expression history |
| `previous_expression` | `string` | Stores last expression for restore |
| `replace_expression` | `int` | Behavior on new calculation (KEEP_EXPRESSION) |
| `highlight_background` | `bool` | Whether to use background color for parenthesis highlight |
| `rtl_input` | `bool` | Right-to-left input mode flag |
| `sdot`, `saltdot`, `sdiv`, `sslash`, `stimes`, `sminus` | `string` | Unicode operator symbols |

### Key Functions

#### Core Text Operations
| Function | Lines | Purpose |
|----------|-------|---------|
| `create_expression_edit()` | 1879-1970 | **Initialization**: margins, CSS providers, fonts, keyboard shortcuts, signal handlers, completion |
| `get_expression_text()` | 201-209 | Extracts full expression text from buffer |
| `get_selected_expression_text()` | 231-246 | Extracts selected text (or all if no selection) |
| `set_expression_text()` | 275-288 | Sets buffer text, handles RTL, records undo |
| `clear_expression_text()` | 296-300 | Clears the buffer (respects RTL) |
| `overwrite_expression_selection()` | 256-273 | Replaces selection or inserts at cursor, handles overwrite mode |
| `insert_text()` | 289-295 | High-level insert: blocks completion, inserts, refocuses |

#### Undo/Redo System
| Function | Lines | Purpose |
|----------|-------|---------|
| `add_expression_to_undo()` | 247-254 | Pushes current state to undo deque (max 100) |
| `expression_undo()` | 1352-1356 | Decrement index, apply state |
| `expression_redo()` | 1357-1361 | Increment index, apply state |
| `expression_set_from_undo_buffer()` | 1242-1351 | Smart diff-based restore: minimal edits instead of full text replacement |
| `block_undo()` / `unblock_undo()` | 213-218 | Reference-counted block to prevent undo recording during programmatic edits |

#### Expression History (Up/Down arrows)
| Function | Lines | Purpose |
|----------|-------|---------|
| `add_to_expression_history()` | 307-320 | Adds expression to history, deduplicates, max 100 entries |
| `expression_history_up()` | 336-351 | Navigate up in history |
| `expression_history_down()` | 321-335 | Navigate down in history, restores current editing |

#### Syntax Highlighting
| Function | Lines | Purpose |
|----------|-------|---------|
| `highlight_parentheses()` | 573-643 | Finds matching parentheses at cursor, applies green/red tags |
| `update_expression_colors()` | 1667-1772 | Creates/updates parenthesis tag colors based on theme |

#### Keyboard Handling
| Function | Lines | Purpose |
|----------|-------|---------|
| `on_expressiontext_key_press_event()` | 948-1240 | **Main key handler**: Enter=execute, Escape=clear/close, operators, Up/Down=history, Ctrl+Z/Y=undo/redo, Ctrl+C=copy result, Tab=completion |
| `wrap_expression_selection()` | 151-200 | Wraps selected text in parentheses |
| `brace_wrap()` | 481-571 | Smart parenthesis insertion: determines what to wrap based on context |

#### Operator Symbols
| Function | Lines | Purpose |
|----------|-------|---------|
| `set_expression_operator_symbols()` | 353-365 | Maps Unicode symbols based on font capabilities |
| `expression_times_sign()` | 374-379 | Returns appropriate multiplication sign |
| `expression_divide_sign()` | 380-384 | Returns appropriate division sign |

#### Auto-calc Selection
| Function | Lines | Purpose |
|----------|-------|---------|
| `on_expressionbuffer_cursor_position_notify()` | 678-710 | On cursor move: re-highlights parens, shows parse status, schedules auto-calc |
| `do_autocalc_selection_timeout()` | 646-676 | Timer callback: evaluates selected text and shows result in status bar |

#### Expression Button Management
| Function | Lines | Purpose |
|----------|-------|---------|
| `update_expression_icons()` | 894-936 | Manages button state: equals/clear/stop/spinner/info icons |
| `showhide_expression_button()` | 881-884 | Shows/hides button based on empty state |

#### Insert Operations
| Function | Lines | Purpose |
|----------|-------|---------|
| `expression_insert_date()` | 1421-1454 | Date picker dialog, inserts formatted date |
| `expression_insert_matrix()` | 1455-1470 | Matrix editor dialog |
| `expression_insert_vector()` | 1471-1486 | Vector editor dialog |

#### Popup Menu
| Function | Lines | Purpose |
|----------|-------|---------|
| `on_expressiontext_populate_popup()` | 1508-1607 | Right-click menu: Clear, Undo/Redo, Completion Mode, Parsing Mode, Number Base, Meta Modes, Insert |

#### Settings
| Function | Lines | Purpose |
|----------|-------|---------|
| `read_expression_edit_settings_line()` | 91-107 | Reads: expression_lines, custom font, replace_expression, highlight |
| `write_expression_edit_settings()` | 108-115 | Writes settings |
| `read_expression_history_line()` / `write_expression_history()` | 116-130 | Persists expression history |

## Calculator Interaction

1. **`CALCULATOR->unlocalizeExpression()`** - Converts localized expression to canonical form
2. **`CALCULATOR->parseSigns()`** - Parses sign characters for context-aware wrapping
3. **`CALCULATOR->calculateAndPrint()`** - Used in auto-calc selection preview
4. **`CALCULATOR->getActiveFunction()`** - Detects function names for smart wrapping
5. **`CALCULATOR->separateToExpression()`** - Isolates current expression for insert operations
6. **`evalops`** (global) - Passed to Calculator for parsing context
7. **`CALCULATOR->getDecimalPoint()`** - Locale-aware separator input

## Signal Handlers

| Signal | Handler | Widget |
|--------|---------|--------|
| `key-press-event` | `on_expressiontext_key_press_event` | expressiontext |
| `changed` | `on_expressionbuffer_changed` | expressionbuffer |
| `cursor-position-notify` | `on_expressionbuffer_cursor_position_notify` | expressionbuffer |
| `paste-done` | `on_expressionbuffer_paste_done` | expressionbuffer |
| `button-press-event` | `on_expressiontext_button_press_event` | expressiontext |
| `focus-out-event` | `on_expressiontext_focus_out_event` | expressiontext |
| `populate-popup` | `on_expressiontext_populate_popup` | expressiontext |
| `button-press-event` | `on_expression_button_button_press_event` | expression_button |

## Data Flow

```
User types text
  -> on_expressionbuffer_changed()
    -> set_expression_modified()
      -> handle_expression_modified() [mainwindow.cc]
        -> If auto_calculate: triggers calculation
      -> add_completion_timeout()
      -> highlight_parentheses()
      -> update_expression_icons()

User presses Enter
  -> on_expressiontext_key_press_event()
    -> execute_expression() [mainwindow.cc]
      -> CALCULATOR->calculateAndPrint()
        -> resultview displays result
        -> historyview adds entry
```
