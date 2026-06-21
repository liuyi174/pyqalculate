# Autocomplete System Specification

> **Source**: pyQalculate `qalculate-gtk` (`src/callbacks.cc`, `src/interface.cc`)
> **Purpose**: Complete technical specification of the autocomplete/completion popup system, from data model through UI rendering, including a Tkinter reimplementation blueprint.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Global State](#2-global-state)
3. [Data Model](#3-data-model)
4. [Population Logic](#4-population-logic)
5. [Current Object Detection](#5-current-object-detection)
6. [Timer-Based Trigger Mechanism](#6-timer-based-trigger-mechanism)
7. [Core Matching Algorithm](#7-core-matching-algorithm)
8. [Popup UI](#8-popup-ui)
9. [Selection Handling](#9-selection-handling)
10. [Name Formatting and Display](#10-name-formatting-and-display)
11. [Integration Points](#11-integration-points)
12. [Tkinter Reimplementation Blueprint](#12-tkinter-reimplementation-blueprint)

---

## 1. Overview

The autocomplete system provides real-time, cursor-aware suggestions as the user types into the expression edit (`GtkEntry`). It surfaces functions, variables, units, prefixes, and conversion keywords ranked by a scoring algorithm. The popup appears below the entry, repositions as the user navigates, and supports mouse click, keyboard, and Tab-based selection.

Key source files:
- `src/callbacks.cc` — `completion_sort_func`, `on_completion_match_selected`, `update_completion`, `completion_insert`
- `src/interface.cc` — popup creation, `GtkTreeView` setup, `GtkListStore` model

---

## 2. Global State

| Variable | Type | Default | Description |
|---|---|---|---|
| `enable_completion` | `gboolean` | `TRUE` | Master switch for the entire autocomplete system. Read from `ENABLE_COMPLETION` setting. |
| `completion_min` | `gint` | `1` | Minimum number of typed characters before the popup triggers. Setting to `0` means completion fires on every keystroke. |
| `completion_delay` | `gint` | `250` (ms) | Delay after the last keystroke before the popup is computed and shown. Prevents lag during rapid typing. |
| `completion_show_disabled` | `gboolean` | `FALSE` | Whether to include items from disabled feature sets in the results. |

These are persisted in the application settings file (`~/.config/qalculate/qalculate-gtk.conf` or equivalent).

---

## 3. Data Model

### 3.1 GtkListStore Columns

The completion popup uses a `GtkListStore` with **10 columns**:

| Index | Column Name | C Type | Description |
|---|---|---|---|
| 0 | `COL_NAME` | `gchar *` | Display name of the item (formatted, may include parentheses for functions) |
| 1 | `COL_NAME_BOLD` | `gchar *` | Bold-formatted name substring for matched portion |
| 2 | `COL_DESCRIPTION` | `gchar *` | Short description / category label (e.g. "function", "variable", "unit") |
| 3 | `COL_ITEM` | `gpointer` | Pointer to the underlying `MathStructure *` or `ExpressionItem *` |
| 4 | `COL_OBJECT_TYPE` | `gint` | Object type enum (`OPTION_TYPE_FUNCTION`, `OPTION_TYPE_VARIABLE`, `OPTION_TYPE_UNIT`, etc.) |
| 5 | `COL_TITLE` | `gchar *` | Title / localized display name |
| 6 | `COL_NAMES` | `gchar *` | All comma-separated names/aliases |
| 7 | `COL_COUNTRY` | `gchar *` | Country-of-origin tag (used for currency units) |
| 8 | `COL_NAMES_LOW` | `gchar *` | Lowercased version of `COL_NAMES` for fast matching |
| 9 | `COL_TITLE_LOW` | `gchar *` | Lowercased version of `COL_TITLE` for fast matching |

### 3.2 Filter/Sort Chain

1. **Population**: All eligible items are added to the list store once (at startup or when settings change).
2. **Visible Filter**: A `GtkTreeModelFilter` wraps the store, hiding rows that do not match the current query.
3. **Sort Model**: A `GtkTreeModelSort` wraps the filter, ordering by the `score` column (descending) then by name (ascending).
4. **Popup View**: A `GtkTreeView` reads from the sort model.

The chain is: `GtkListStore → GtkTreeModelFilter → GtkTreeModelSort → GtkTreeView`.

---

## 4. Population Logic

At startup (or when the settings dialog changes completion preferences), the list store is populated:

### 4.1 Functions
```
for each registered function:
    if !function.isHidden() || completion_show_disabled:
        add to list store
        COL_OBJECT_TYPE = OPTION_TYPE_FUNCTION
```

### 4.2 Variables
```
for each registered variable:
    if !variable.isHidden() || completion_show_disabled:
        add to list store
        COL_OBJECT_TYPE = OPTION_TYPE_VARIABLE
```

### 4.3 Units
```
for each registered unit:
    if !unit.isHidden() || completion_show_disabled:
        add to list store
        COL_OBJECT_TYPE = OPTION_TYPE_UNIT
```

### 4.4 Prefixes
```
for each registered prefix:
    add to list store
    COL_OBJECT_TYPE = OPTION_TYPE_PREFIX
```

### 4.5 Conversion Keywords
The hardcoded string `"to"` (and localized equivalents) is added as a special conversion keyword entry.

**COL_NAMES** for each item is constructed by joining all registered names (primary + aliases) with commas. **COL_NAMES_LOW** and **COL_TITLE_LOW** are pre-lowercased copies for case-insensitive matching.

---

## 5. Current Object Detection

The function `get_current_object_start(GtkEntry *entry)` determines what word the cursor is currently on:

1. Get the cursor position from `gtk_editable_get_position()`.
2. Walk backward from the cursor position, character by character.
3. Stop at: whitespace, opening/closing parentheses, comma, semicolon, operators (`+`, `-`, `*`, `/`, `^`, `=`, `<`, `>`, `!`, `|`, `&`, `%`, `²`, `³`).
4. The position where the backward walk stops is `object_start`.
5. The substring `[object_start, cursor_pos)` is the **current object prefix** (what the user has typed so far).

This prefix is passed to the matching algorithm.

```c
gint get_current_object_start(GtkEditable *editable) {
    gint pos = gtk_editable_get_position(editable);
    gunichar c;
    while(pos > 0) {
        c = gtk_editable_get_chars(editable, pos - 1, pos);
        if(c == ' ' || c == '(' || c == ')' || c == ',' || c == ';' ||
           c == '+' || c == '-' || c == '*' || c == '/' || c == '^' ||
           c == '=' || c == '<' || c == '>' || c == '!' || c == '|' ||
           c == '&' || c == '%' || c == 0xB2 || c == 0xB3) {
            break;
        }
        pos--;
    }
    return pos;
}
```

---

## 6. Timer-Based Trigger Mechanism

Keystrokes in the expression entry do not immediately fire completion. Instead:

1. `on_expression_entry_changed()` fires on every text change.
2. It calls `g_source_remove(completion_timeout_id)` to cancel any pending timer.
3. It starts a new timer: `completion_timeout_id = g_timeout_add(completion_delay, completion_timeout, NULL)`.
4. When the timer fires (`completion_timeout()`):
   a. Check `enable_completion`.
   b. Compute `object_start` and `prefix`.
   c. If `strlen(prefix) >= completion_min`, call `update_completion()`.
   d. Otherwise, hide the popup.

**Edge cases**:
- Typing a space, operator, or parenthesis immediately hides the popup (cancels timer, hides popup directly).
- If the expression entry loses focus, the popup hides.
- If `completion_delay == 0`, the timer fires immediately (effectively synchronous).

---

## 7. Core Matching Algorithm

### 7.1 `completion_sort_func(GtkTreeModel *model, GtkTreeIter *a, GtkTreeIter *b, gpointer data)`

Compares two items for sorting. Primary sort is by score (descending), secondary by name (ascending).

### 7.2 Scoring

For each item, a score from **0 to 6** is computed against the user's typed prefix:

| Score | Meaning | Description |
|---|---|---|
| 6 | Exact name match | `name == prefix` (case-insensitive) |
| 5 | Name starts with prefix | `name.startswith(prefix)` (case-insensitive) |
| 4 | Title starts with prefix | `title.startswith(prefix)` (case-insensitive) |
| 3 | Name contains prefix | `name.contains(prefix)` (case-insensitive) |
| 2 | Title contains prefix | `title.contains(prefix)` (case-insensitive) |
| 1 | Country contains prefix | `country.contains(prefix)` (case-insensitive, for currencies) |
| 0 | No match | Item is filtered out (not shown in popup) |

### 7.3 Matching Functions

```c
gint name_matches(const gchar *name, const gchar *prefix) {
    // Returns score if name matches prefix, 0 otherwise
    // Case-insensitive via g_ascii_strdown or similar
    gint score = 0;
    gchar *name_low = g_ascii_strdown(name, -1);
    gchar *prefix_low = g_ascii_strdown(prefix, -1);
    if(strcmp(name_low, prefix_low) == 0) score = 6;
    else if(g_str_has_prefix(name_low, prefix_low)) score = 5;
    else if(strstr(name_low, prefix_low) != NULL) score = 3;
    g_free(name_low);
    g_free(prefix_low);
    return score;
}

gint title_matches(const gchar *title, const gchar *prefix) {
    // Similar logic, scores 4 (starts with) or 2 (contains)
}

gint country_matches(const gchar *country, const gchar *prefix) {
    // Returns 1 if contains, 0 otherwise (currencies only)
}
```

### 7.4 Filter Function

The `GtkTreeModelFilter` visible function checks `score > 0` for the current prefix. Items with score 0 are hidden.

---

## 8. Popup UI

### 8.1 Construction

The popup is a `GtkWindow` of type `GTK_WINDOW_POPUP` (no title bar, no decorations):

```c
completion_window = gtk_window_new(GTK_WINDOW_POPUP);
GtkWidget *scrolled = gtk_scrolled_window_new(NULL, NULL);
gtk_scrolled_window_set_policy(GTK_SCROLLED_WINDOW(scrolled),
    GTK_POLICY_NEVER, GTK_POLICY_AUTOMATIC);
completion_view = gtk_tree_view_new_with_model(GTK_TREE_MODEL(completion_sort));
// Add columns...
gtk_container_add(GTK_CONTAINER(completion_window), scrolled);
```

### 8.2 Columns in TreeView

| Column | Render Cell | Property |
|---|---|---|
| 0 (Name) | `GtkCellRendererText` | `text` = `COL_NAME`, weight may be bold for matched portion |
| 1 (Description) | `GtkCellRendererText` | `text` = `COL_DESCRIPTION`, foreground = gray |

### 8.3 Positioning

```
x = entry_window_x + cursor_x_in_entry
y = entry_window_y + entry_height
```

The popup appears directly below the entry, aligned to the cursor's horizontal position. If it would overflow the screen right edge, it shifts left. If it would overflow the bottom, it appears above the entry.

### 8.4 Sizing

- **Width**: Natural width of the widest visible row, clamped to a maximum (~400px).
- **Height**: `min(num_visible_rows * row_height, 200px)`, with vertical scrollbar if needed.
- **Row height**: Determined by the tree view's row-height (typically ~20-24px).

### 8.5 Show/Hide

```c
void show_completion() {
    if(completion_count == 0) { hide_completion(); return; }
    gtk_widget_show_all(completion_window);
    // Reposition based on entry cursor
}

void hide_completion() {
    gtk_widget_hide(completion_window);
    completion_count = 0;
}
```

---

## 9. Selection Handling

### 9.1 Mouse Click

`on_completion_match_selected(GtkTreeView *tree_view, GtkTreePath *path, ...)`
1. Get the selected row's `COL_ITEM` and `COL_OBJECT_TYPE`.
2. Call `completion_insert(item, type)`.
3. Hide the popup.

### 9.2 Enter Key

Enter in the expression entry checks if the popup is visible:
- If visible and an item is selected, insert it (same as mouse click).
- If visible but nothing selected, hide the popup and evaluate the expression.
- If not visible, evaluate the expression.

### 9.3 Up/Down Arrow Keys

When the popup is visible:
- Up/Down move the selection within the `GtkTreeView` (not the cursor in the entry).
- The entry cursor position is preserved.

When the popup is hidden:
- Up/Down move the cursor within the entry (history navigation or line movement).

### 9.4 Tab Cycling

Tab behavior:
1. If the popup is visible, Tab selects the current item and inserts it.
2. If multiple items share the same prefix, repeated Tab presses cycle through them (re-sorting or re-filtering to bring the next match to the top).
3. Shift+Tab cycles in reverse.

This is implemented by re-running the completion with a modified query or by tracking a cycle index.

### 9.5 `completion_insert()`

```c
void completion_insert(ExpressionItem *item, ObjectType type) {
    // Get cursor position and object_start
    gint start = get_current_object_start(expression_edit);
    gint end = gtk_editable_get_position(GTK_EDITABLE(expression_edit));

    // Delete the typed prefix
    gtk_editable_delete_text(GTK_EDITABLE(expression_edit), start, end);

    // Get the item's name
    const gchar *name = item->getName();

    // If function, append "("
    if(type == OPTION_TYPE_FUNCTION) {
        gchar *insert = g_strdup_printf("%s(", name);
        gtk_editable_insert_text(GTK_EDITABLE(expression_edit), insert, -1, &start);
        g_free(insert);
    } else {
        gtk_editable_insert_text(GTK_EDITABLE(expression_edit), name, -1, &start);
    }
}
```

---

## 10. Name Formatting and Display

- **Functions** are displayed as `name()` — the parentheses signal they are callable.
- **Variables and units** are displayed as plain `name`.
- **Matched portions** are displayed in bold in the `COL_NAME_BOLD` column (using Pango markup `<b>prefix</b>remainder`).
- **Descriptions** show the item type: "function", "variable", "unit", "prefix", or a more specific category.
- **Localized names** are used when available; the user's locale determines which name variant is shown.

---

## 11. Integration Points

| Component | Integration |
|---|---|
| **Expression Entry** | `on_expression_entry_changed()` triggers the completion timer. Key-press events for Tab, Enter, Up/Down, Escape are intercepted. |
| **Settings Dialog** | `ENABLE_COMPLETION`, `COMPLETION_MIN`, `COMPLETION_DELAY` toggles/spinners. Changing these calls `populate_completion_list()` to rebuild the store. |
| **Main Window** | The popup is a child of the main window for proper z-ordering and focus management. |
| **Calculator Engine** | Completion items reference `ExpressionItem *` objects from `Calculator`. Inserted text is then parsed by the calculator on evaluation. |
| **Unit Conversion** | The special `"to"` keyword is a completion item. Selecting it inserts ` to ` with surrounding spaces. |

---

## 12. Tkinter Reimplementation Blueprint

### 12.1 State

```python
self.enable_completion = True
self.completion_min = 1
self.completion_delay = 250  # ms
self.completion_timeout_id = None
self.completion_items = []  # [{name, bold, desc, item, obj_type, title, names, country, names_low, title_low}]
```

### 12.2 Data Population

```python
def populate_completion(self):
    self.completion_items = []
    for func in CALCULATOR.functions():
        self.completion_items.append(self._make_entry(func, "function"))
    for var in CALCULATOR.variables():
        self.completion_items.append(self._make_entry(var, "variable"))
    for unit in CALCULATOR.units():
        self.completion_items.append(self._make_entry(unit, "unit"))
    # prefixes, conversion keywords...
```

### 12.3 Timer Trigger

```python
def on_expression_change(self, event=None):
    if self.completion_timeout_id:
        self.root.after_cancel(self.completion_timeout_id)
    self.completion_timeout_id = self.root.after(
        self.completion_delay, self._fire_completion)

def _fire_completion(self):
    if not self.enable_completion:
        return
    prefix = self._get_current_prefix()
    if len(prefix) >= self.completion_min:
        self._update_popup(prefix)
    else:
        self._hide_popup()
```

### 12.4 Matching and Scoring

```python
def _score_item(self, item, prefix):
    p = prefix.lower()
    name_l = item["name_low"]
    title_l = item["title_low"]
    if name_l == p: return 6
    if name_l.startswith(p): return 5
    if title_l.startswith(p): return 4
    if p in name_l: return 3
    if p in title_l: return 2
    if p in item.get("country", "").lower(): return 1
    return 0
```

### 12.5 Popup (Toplevel + Treeview)

```python
def _create_popup(self):
    self.popup = tk.Toplevel(self.root)
    self.popup.wm_overrideredirect(True)
    self.popup.wm_attributes("-topmost", True)

    frame = tk.Frame(self.popup, relief="solid", bd=1)
    frame.pack(fill="both", expand=True)

    self.tree = ttk.Treeview(frame, columns=("name", "desc"),
                              show="headings", height=8)
    self.tree.heading("name", text="Name")
    self.tree.heading("desc", text="Description")
    self.tree.column("name", width=250)
    self.tree.column("desc", width=150)

    scrollbar = ttk.Scrollbar(frame, orient="vertical",
                               command=self.tree.yview)
    self.tree.configure(yscrollcommand=scrollbar.set)

    self.tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    self.tree.bind("<ButtonRelease-1>", self._on_completion_click)
    self.tree.bind("<Return>", self._on_completion_enter)
```

### 12.6 Positioning

```python
def _position_popup(self):
    # Get entry widget position
    x = self.entry.winfo_rootx() + self._cursor_x_offset()
    y = self.entry.winfo_rooty() + self.entry.winfo_height()

    # Clamp to screen
    sw = self.root.winfo_screenwidth()
    sh = self.root.winfo_screenheight()
    pw = self.popup.winfo_reqwidth()
    ph = self.popup.winfo_reqheight()

    if x + pw > sw: x = sw - pw
    if y + ph > sh: y = self.entry.winfo_rooty() - ph

    self.popup.wm_geometry(f"+{x}+{y}")
```

### 12.7 Selection

```python
def _on_completion_click(self, event=None):
    sel = self.tree.selection()
    if sel:
        item = self.tree.item(sel[0])
        self._insert_completion(item["values"][0])
        self._hide_popup()

def _on_completion_enter(self, event=None):
    self._on_completion_click(event)

def _on_expression_key(self, event):
    if event.keysym == "Escape":
        self._hide_popup()
        return "break"
    if event.keysym == "Tab":
        if self._popup_visible:
            self._on_completion_enter()
            return "break"
    if event.keysym in ("Up", "Down"):
        if self._popup_visible:
            # Move selection in treeview, not entry cursor
            self._tree_navigate(event.keysym)
            return "break"
```

### 12.8 Bold Matching via Treeview Tags

```python
def _insert_match(self, name, prefix, score, desc):
    tag = "matched" if score >= 3 else "normal"
    self.tree.insert("", "end", values=(name, desc),
                      tags=(tag,))
    # For true bold prefix, use a custom ttk style or
    # fall back to displaying the full name in bold
    # (ttk.Treeview doesn't natively support per-cell markup)
    # Alternative: use a Listbox with tk.Text for rich text
```

> **Note**: `ttk.Treeview` does not support Pango-style markup. For bold prefix rendering, consider using a `tk.Canvas`-based list or a `tk.Text` widget styled as a dropdown. The `tk.Text` approach supports embedded tags for bold/normal segments within each row.

---

*End of Autocomplete System Specification*
