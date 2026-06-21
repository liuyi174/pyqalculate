# History View - qalculate-gtk Analysis

**Files:**
- `D:\1\1tmp\qalculate-gtk\src\historyview.h` (81 lines)
- `D:\1\1tmp\qalculate-gtk\src\historyview.cc` (3717 lines)
- **Total: 3798 lines**

## What It Does

The history view module implements the **calculation history panel** - a scrollable `GtkTreeView`-based list that stores and displays all past calculations, results, errors, warnings, and bookmarks. It provides two critical built-in Calculator functions (`answer()` and `expression()`) that allow referencing historical results and expressions.

## Architecture

### Key Global State (File-scope Variables)

| Variable | Type | Purpose |
|----------|------|---------|
| `historyview` | `GtkWidget*` | The tree view widget |
| `historystore` | `GtkListStore*` | Data model for the tree view |
| `inhistory` | `deque<string>` | Raw history text data |
| `inhistory_type` | `deque<int>` | Type of each history entry |
| `inhistory_value` | `deque<int>` | Expression counter value |
| `inhistory_time` | `deque<time_t>` | Timestamps |
| `inhistory_protected` | `deque<bool>` | Protected entries (not deleted on clear) |
| `history_parsed` | `vector<MathStructure*>` | Parsed MathStructure for each expression |
| `history_answer` | `vector<MathStructure*>` | Answer MathStructure for each expression |
| `history_bookmarks` | `vector<string>` | Bookmarked entry titles |
| `current_inhistory_index` | `int` | Index of the current expression group |
| `history_index` | `int` | Position in the GtkListStore |
| `nr_of_new_expressions` | `int` | Counter of expressions in session |
| `f_answer` | `MathFunction*` | Built-in answer() function |
| `f_expression` | `MathFunction*` | Built-in expression() function |

### History Entry Types (enum)

| Type | Value | Description |
|------|-------|-------------|
| `QALCULATE_HISTORY_EXPRESSION` | 0 | User-typed expression |
| `QALCULATE_HISTORY_TRANSFORMATION` | 1 | Transformation label |
| `QALCULATE_HISTORY_RESULT` | 2 | Exact result |
| `QALCULATE_HISTORY_RESULT_APPROXIMATE` | 3 | Approximate result |
| `QALCULATE_HISTORY_PARSE_WITHEQUALS` | 4 | Parsed expression (old format) |
| `QALCULATE_HISTORY_PARSE` | 5 | Parsed expression |
| `QALCULATE_HISTORY_PARSE_APPROXIMATE` | 6 | Parsed approximate expression |
| `QALCULATE_HISTORY_WARNING` | 7 | Warning message |
| `QALCULATE_HISTORY_ERROR` | 8 | Error message |
| `QALCULATE_HISTORY_OLD` | 9 | Legacy format entry |
| `QALCULATE_HISTORY_REGISTER_MOVED` | 10 | RPN register move |
| `QALCULATE_HISTORY_RPN_OPERATION` | 11 | RPN operation |
| `QALCULATE_HISTORY_BOOKMARK` | 12 | Bookmark label |
| `QALCULATE_HISTORY_MESSAGE` | 13 | Informational message |

### GtkListStore Columns

| Column | Purpose |
|--------|---------|
| 0 | Pango markup text (displayed) |
| 1 | inhistory index (-1 for separator rows) |
| 2 | Expression number string |
| 3 | Expression counter value |
| 4 | Vertical padding |
| 5 | Scroll width |
| 6 | Scale factor |
| 7 | Text alignment (LEFT for expressions, RIGHT for results) |

### Built-in Functions

#### AnswerFunction (answer(index))
- **Lines 108-168**
- Registered as Calculator function: `answer(1)`, `answer(-1)` (last), `answer(1,2,3)` (multiple)
- Returns MathStructure from `history_answer[index-1]`
- Special handling: extracts solution values from equations
- Supports negative indices (counting from end)

#### ExpressionFunction (expression(index))
- **Lines 169-194**
- Registered as Calculator function: `expression(1)`, `expression(-1)`
- Returns parsed MathStructure from `history_parsed[index-1]`
- Supports multiple indices via vector argument

### Key Functions

#### History Entry Management
| Function | Lines | Purpose |
|----------|-------|---------|
| `add_result_to_history_pre()` | 1445-1515 | Pre-calculation: sets up history entry, inserts expression |
| `add_result_to_history()` | 1530-1732 | Post-calculation: inserts result/parse, handles duplicates, ellipsizes |
| `add_message_to_history()` | 1733-1757 | Adds error/warning/info message |
| `history_display_errors()` | 797-903 | Iterates Calculator messages, adds color-coded entries |

#### History Display
| Function | Lines | Purpose |
|----------|-------|---------|
| `reload_history()` | 1267-1441 | Rebuilds GtkListStore from inhistory data, handles all types, Pango markup |
| `add_line_breaks()` | 904-1244 | 340-line word-wrap: Pango measurement, HTML-aware, smart break points |
| `improve_result_text()` | 708-774 | Post-processes: quoted vars to italic, subscript/superscript |

#### History Selection Processing
| Function | Lines | Purpose |
|----------|-------|---------|
| `process_history_selection()` | 1877-1925 | Converts GTK selection to index list with type classification |

#### History Operations (Buttons)
| Function | Lines | Purpose |
|----------|-------|---------|
| `history_operator()` | 1926-2020 | Core operator handler: builds expression from selected items |
| `on_button_history_insert_value_clicked()` | 2070-2103 | Inserts answer(N) or expression(N) |
| `on_button_history_insert_text_clicked()` | 2104-2114 | Inserts raw text from history |
| `on_button_history_sqrt_clicked()` | 2037-2069 | Wraps selection in sqrt() |
| `history_copy()` | 2126-2113 | Copies with proper formatting |

#### History Management
| Function | Lines | Purpose |
|----------|-------|---------|
| `history_clear()` | 2222-2244 | Clears (preserves protected/bookmarked) |
| `on_popup_menu_item_history_delete_activate()` | 2365+ | Deletes selected entries |
| `on_popup_menu_item_history_movetotop_activate()` | 2246-2364 | Moves entries to top |

#### String Processing Utilities
| Function | Lines | Purpose |
|----------|-------|---------|
| `fix_history_string()` / `fix_history_string2()` | 691-702 | HTML-escapes &, <, > |
| `fix_history_string_new()` / `fix_history_string_new2()` | 673-689 | HTML classes to Pango |
| `unfix_history_string()` | 703-707 | Reverses escaping |
| `remove_italic()` | 1245-1266 | Strips markup, superscripts to Unicode |
| `ellipsize_result()` | 648-671 | Truncates with ellipsis |

#### Color/Font Management
| Function | Lines | Purpose |
|----------|-------|---------|
| `update_history_colors()` | 1778-1834 | Generates error (red), warning (blue), bookmark (green), parse (gray) |
| `update_history_font()` | 1838-1856 | Updates CSS font |

#### Settings
| Function | Lines | Purpose |
|----------|-------|---------|
| `read_history_settings_line()` | 196-212 | Reads: clear_on_exit, max_lines, expression_type, font |
| `read_history_line()` | 224-363 | 140-line parser with version compatibility |
| `write_history()` | 365-644 | 280-line writer with protection/bookmarking/truncation |

## Calculator Interaction

1. **`DECLARE_BUILTIN_FUNCTION`** - Registers answer()/expression() as Calculator functions
2. **`history_answer[i]`** / **`history_parsed[i]`** - Stores MathStructure copies of results/expressions
3. **`CALCULATOR->message()`** / `CALCULATOR->nextMessage()` - Iterates messages
4. **`current_result()`** / `current_parsed_result()` - Gets current results for storage
5. **`evalops.parse_options.functions_enabled`** - Affects expression index generation
6. **`printops`** - Controls result formatting in history

## History Data Model

A typical calculation group:
```
[index N]   QALCULATE_HISTORY_EXPRESSION  "sin(45)"
[index N+1] QALCULATE_HISTORY_PARSE       "sin(45)"     (if differs)
[index N+2] QALCULATE_HISTORY_RESULT      "= 0.707..."  (or RESULT_APPROXIMATE)
[index N+3] QALCULATE_HISTORY_WARNING     "..."          (optional)
```

The inhistory_value field links all entries in a group to the same expression counter.

## History Persistence Format

```
history_expression=sin(45)
history_parse=sin(45)
history_result= 0.707106781...
history_time=1718000000
history_bookmark=My Calculations
```
- Protected entries: `history_expression*=...`
- Continuation lines: `history_continued=...`
- Max 300 lines by default
- Bookmarked/protected entries survive clear_history_on_exit
