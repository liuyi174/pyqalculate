# DESIGN_GUIDE.md — PyQalculate GUI Rebuild Reference

## Architecture Overview

### Core Pattern: C-Style Modular Monolith

qalculate-gtk has **NO OOP in the GUI layer**. Each module is a `.cc/.h` pair with **free functions only** and **file-scope global variables**. There are no widget classes. All widgets are globals accessed through accessor functions.

### Startup Sequence

```
main()
  ├── Parse locale/language from qalculate-gtk.cfg
  ├── gtk_application_new("io.github.Qalculate")
  │
qalculate_activate() → create_application()
  ├── new Calculator(ignore_locale)
  ├── load_preferences()
  ├── create_main_window()
  │   ├── new MathStructure() x4
  │   ├── getBuilder("main.ui")
  │   ├── Create CSS providers
  │   ├── Create 4 GtkExpanders
  │   ├── create_keypad()
  │   ├── create_history_view()
  │   ├── create_conversion_view()
  │   ├── create_stack_view()
  │   ├── create_result_view()
  │   ├── create_expression_edit()
  │   ├── create_expression_status()
  │   ├── create_menubar()
  │   └── gtk_widget_show(main_window)
  │
Post-show:
  ├── CALCULATOR->loadExchangeRates()
  ├── CALCULATOR->loadGlobalDefinitions()
  ├── CALCULATOR->loadLocalDefinitions()
  ├── definitions_loaded()
  ├── view_thread->start()
  │
Deferred (g_timeout_add 50ms):
  └── create_menus_etc()
```

## Widget Architecture

### 2.1 Expression Edit (expressionedit.cc — 1,970 lines)

**GTK Widget**: `GtkTextView` with `GtkTextBuffer`

**Key globals**:
- `expressiontext` — Main widget
- `expressionbuffer` — Text content
- `expression_par_tag` — Parenthesis highlight
- `expression_undo_buffer` — Deque, max 100 entries
- `expression_history` — Previous expressions

**Key functions**:
- `create_expression_edit()` — Init margins, CSS, signals
- `get_expression_text()` — Get full text
- `set_expression_text()` — Replace all text
- `insert_text()` — Insert at cursor
- `expression_undo/redo()` — Navigate undo buffer
- `expression_history_up/down()` — Navigate history

**Signals**:
- `expressionbuffer::changed` → auto-calculate
- `expressiontext::key-press-event` → keyboard handling
- `expressiontext::populate-popup` → context menu

### 2.2 Result View (resultview.cc — 1,392 lines)

**GTK Widget**: `GtkDrawingArea` inside `GtkScrolledWindow`

**Key globals**:
- `surface_result` — Rendered Cairo surface
- `displayed_mstruct` — Currently displayed result
- `scale_n` — Zoom level (0-3)

**Rendering pipeline**:
1. `draw_result_pre()` — Lock for rendering
2. `draw_result_post()` — Process ViewThread result
3. `on_resultview_draw()` — Paint surface to widget

**Auto-scaling**: Starts at full size, scales down if exceeds viewport (0.75x → 0.5x → fits-width)

### 2.3 Keypad (keypad.cc — 3,775 lines)

**Two modes**: Versatile (standard) and Programming (hex, bitwise)

**Custom button structure**:
```cpp
struct custom_button {
    int type[3];       // Normal/shifted/ctrl
    string value[3];   // Value per binding
    string text;       // Custom label
};
```

**Button groups**:
- Numbers: 0-9, dot, exp
- Operators: +, -, ×, ÷, xy, √
- Functions: sin/cos/tan with dropdowns
- Control: AC, DEL, Ans, =
- Programming: A-F, AND/OR/XOR/NOT
- Custom: 49 buttons in 5 groups

### 2.4 History View (historyview.cc — 3,717 lines)

**GTK Widget**: `GtkTreeView` with `GtkListStore` (8 columns)

**Parallel deques**:
- `inhistory` — Text content
- `inhistory_protected` — Edit protection
- `inhistory_type` — Entry type
- `history_parsed` — Parsed structures
- `history_answer` — Answer values

**Built-in functions**:
- `answer(N)` — History answer at index N
- `expression(N)` — History expression at index N

### 2.5 Conversion View (conversionview.cc — 530 lines)

**Two-panel layout**: Category tree + unit list

**Data flow**: Select category → populate units → select unit → convert

### 2.6 Expression Status (expressionstatus.cc — 1,537 lines)

**Two labels**:
- `label_status_left` — Parse status, function hints
- `label_status_right` — Mode indicators (DEG, HEX)

### 2.7 Draw Structure (drawstructure.cc — ~3,000 lines)

**Core rendering**: Converts `MathStructure` to `cairo_surface_t`

Handles: fractions, super/subscript, integrals, matrices, units, parentheses, RTL, color coding

## Layout System

```
┌──────────────────────────────────────────────────┐
│ MenuBar                                          │
├──────────────────────────────────────────────────┤
│ Result Area (GtkScrolledWindow)                  │
│ ┌──────────────────────────────────────────────┐ │
│ │ resultport (GtkDrawingArea)                  │ │
│ │ Cairo-rendered mathematical expression       │ │
│ └──────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────┤
│ Expression Area                                  │
│ ┌──────────────────┐ ┌──────┐ ┌──────────────┐  │
│ │ expressiontext   │ │icons │ │ = btn        │  │
│ └──────────────────┘ └──────┘ └──────────────┘  │
├──────────────────────────────────────────────────┤
│ Status Bar                                       │
├──────────────────────────────────────────────────┤
│ Tab Panel / Keypad (mutually exclusive or split) │
│ Notebook pages: [History][Stack][Convert]        │
└──────────────────────────────────────────────────┘
```

## Event Flow

### Execute Expression → Result Shown

```
execute_expression()
  → Get expression text
  → add_to_expression_history()
  → Parse comments (//comment)
  → Handle /commands
  → CALCULATOR->calculateAndParse(mstruct, str, evalops)
  → setResult()
  → display_errors()
  → focus_expression()
```

### Set Result → Display Update

```
setResult()
  → Start ViewThread
  → add_result_to_history_pre()
  → draw_result_pre()
  → view_thread->write(mstruct)
  → draw_result_post()
  → add_result_to_history()
```

## State Management

### mode_struct (Full State Snapshot)

```cpp
struct mode_struct {
    PrintOptions po;
    EvaluationOptions eo;
    AssumptionType at;
    AssumptionSign as;
    Number custom_output_base, custom_input_base;
    int precision;
    bool rpn_mode, interval;
    int keypad;
    bool autocalc, chain_mode;
};
```

### Blocking Mechanisms

- `block_expression_execution` — Prevents execute_expression()
- `block_result_update` — Prevents setResult()
- `block_error_timeout` — Prevents display_errors()

## Dialog Inventory (28 dialogs)

| Dialog | Purpose |
|--------|---------|
| Preferences | All settings (10 tabs) |
| Plot | Function plotting |
| Functions List | Browse functions |
| Function Editor | Edit functions |
| Variables List | Browse variables |
| Variable Editor | Edit variables |
| Units List | Browse units |
| Unit Editor | Edit units |
| Datasets | Browse datasets |
| Number Bases | All bases display |
| Floating Point | IEEE 754 |
| Calendar | Calendar conversion |
| Percentage | Percentage tool |
| Periodic Table | Elements |
| Shortcuts | Edit shortcuts |
| Matrix | Matrix input |

## Threading Model

**ViewThread**: Renders MathStructure → cairo_surface_t in background

**CommandThread**: Executes long commands (factorize, expand)

**Timers**: Error checking (1s), auto-calculate (2s)

## Rebuild Checklist

### Phase 1: Core Window
- [ ] Main window with menu bar
- [ ] Expression text area
- [ ] Result display area (Canvas)
- [ ] Status bar
- [ ] Keyboard handling

### Phase 2: Calculator Integration
- [ ] Wrap Calculator class
- [ ] Expression parsing/evaluation
- [ ] Result formatting
- [ ] Error handling

### Phase 3: Keypad
- [ ] Button grid layout
- [ ] Number/operator/function buttons
- [ ] Button click → insert/execute

### Phase 4: History
- [ ] Scrollable history list
- [ ] Entry types
- [ ] Double-click restore
- [ ] Persistence

### Phase 5: Unit Conversion
- [ ] Category tree + unit list
- [ ] Convert button
- [ ] Continuous conversion

### Phase 6: Advanced
- [ ] RPN mode
- [ ] Programming keypad
- [ ] Custom buttons
- [ ] Keyboard shortcuts
- [ ] Auto-completion

### Phase 7: Dialogs
- [ ] Preferences
- [ ] Function/Variable/Unit management
- [ ] Plot dialog
- [ ] Number bases

### Phase 8: Polish
- [ ] Theme support
- [ ] Window persistence
- [ ] Minimal mode
- [ ] i18n
