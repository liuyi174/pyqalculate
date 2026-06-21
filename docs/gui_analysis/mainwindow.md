# Qalculate-GTK Main Window Analysis

> **Files analyzed**: `mainwindow.cc` (9,300 lines), `mainwindow.h` (214 lines)
> **Project**: qalculate-gtk (GTK UI for libqalculate)
> **Copyright**: 2003-2024 Hanna Knutsson
> **License**: GPLv2+

---

## 1. Overall Architecture

The main window module is the **central orchestrator** of the entire Qalculate! GTK desktop calculator application. It is not a single class but rather a **large procedural C++ module** (approximately 9,300 lines of implementation) that coordinates all calculator functionality through global functions and shared state.

### What the Main Window Contains

```
┌─────────────────────────────────────────────────────────────────┐
│  GtkApplication (io.github.Qalculate)                          │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  main_window (GtkWindow from main.ui)                      ││
│  │  ┌───────────────────────────────────────────────────────┐  ││
│  │  │  Menu Bar (menubar.h/cc)                              │  ││
│  │  ├───────────────────────────────────────────────────────┤  ││
│  │  │  Top Frame (topframebox)                              │  ││
│  │  │  ┌─────────────────────────────────────────────────┐  │  ││
│  │  │  │  Expression Edit (expressionedit.h/cc)          │  │  ││
│  │  │  │  - GtkTextView for math expression input        │  │  ││
│  │  │  │  - Auto-completion popup                         │  │  ││
│  │  │  │  - Undo/Redo history                             │  │  ││
│  │  │  │  - Expression status icons (spinner, stop, info) │  │  ││
│  │  │  └─────────────────────────────────────────────────┘  │  ││
│  │  │  ┌─────────────────────────────────────────────────┐  │  ││
│  │  │  │  Expression Status Bar (expressionstatus.h/cc)  │  │  ││
│  │  │  │  - Parsed expression display                    │  │  ││
│  │  │  │  - Approximation indicator                      │  │  ││
│  │  │  │  - Angle unit / base display                    │  │  ││
│  │  │  └─────────────────────────────────────────────────┘  │  ││
│  │  │  ┌─────────────────────────────────────────────────┐  │  ││
│  │  │  │  Message Bar (GtkInfoBar + GtkRevealer)         │  │  ││
│  │  │  │  - Errors, warnings, information                │  │  ││
│  │  │  └─────────────────────────────────────────────────┘  │  ││
│  │  └───────────────────────────────────────────────────────┘  ││
│  │  ┌───────────────────────────────────────────────────────┐  ││
│  │  │  Result View (resultview.h/cc)                        │  ││
│  │  │  - Cairo-rendered math result (drawstructure.h/cc)    │  ││
│  │  │  - Parsed expression in result area                   │  ││
│  │  │  - Result overlay for minimal mode                    │  ││
│  │  └───────────────────────────────────────────────────────┘  ││
│  │  ┌───────────────────────────────────────────────────────┐  ││
│  │  │  Expandable Panels (GtkExpander-based):               │  ││
│  │  │  ┌─────────────┬──────────────┬───────────────────┐   │  ││
│  │  │  │  Keypad     │  History     │  Stack            │   │  ││
│  │  │  │  (keypad.h) │  (historyview│  (stackview.h)    │   │  ││
│  │  │  │             │  .h/cc)      │                   │   │  ││
│  │  │  ├─────────────┴──────────────┴───────────────────┤   │  ││
│  │  │  │  Conversion View (conversionview.h/cc)          │   │  ││
│  │  │  └─────────────────────────────────────────────────┘   │  ││
│  │  │  Note: Keypad & History/Stack are mutually exclusive   │  ││
│  │  │  in non-persistent mode (shown in GtkNotebook tabs)   │  ││
│  │  └───────────────────────────────────────────────────────┘  ││
│  │  ┌───────────────────────────────────────────────────────┐  ││
│  │  │  Notification Overlay (overlaybox)                     │  ││
│  │  │  - Floating notifications with rounded border-radius  │  ││
│  │  └───────────────────────────────────────────────────────┘  ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### Architectural Style

The application follows a **procedural C-with-classes** pattern rather than object-oriented design:

- **No MainWindow class** - the main window is a collection of global functions and global variables in `mainwindow.cc`
- **Global state** - `CALCULATOR` (the libqalculate Calculator singleton), `mstruct`, `parsed_mstruct`, `result_text`, `printops`, `evalops`, etc. are all module-level globals
- **UI defined in Glade** - `main.ui` is loaded via `GtkBuilder`, with widgets accessed by string ID
- **Sub-components are modular** - each panel (keypad, history, result, etc.) has its own `.h/.cc` pair
- **Threading** - Two background threads (`ViewThread`, `CommandThread`) for non-blocking computation

---

## 2. Key Classes and Their Responsibilities

### ViewThread (line 172-175, run at 2485-2624)

```cpp
class ViewThread : public Thread {
    virtual void run();
};
```

**Responsibility**: Formats and renders calculation results on a background thread.

- Receives `MathStructure` pointers via a thread-safe queue (`read()`/`write()`)
- Calls `MathStructure::format(printops)` and `MathStructure::print()` to convert results to text
- Handles matrix element-by-element formatting
- Applies complex angle form, time format conversions
- Generates both short `result_text` and long `result_text_long` forms
- Sets `b_busy = false` when done, signaling the main thread

### CommandThread (line 177-180, run at 2990-3068)

```cpp
class CommandThread : public Thread {
    virtual void run();
};
```

**Responsibility**: Executes long-running mathematical transformations on a background thread.

Supported commands (via `executeCommand()`):
| Command | Description |
|---------|-------------|
| `COMMAND_FACTORIZE` | Integer factorization / algebraic factorization |
| `COMMAND_EXPAND` | Expand algebraic expressions |
| `COMMAND_EXPAND_PARTIAL_FRACTIONS` | Partial fraction decomposition |
| `COMMAND_TRANSFORM` | Unit conversion via conversion view |
| `COMMAND_CONVERT_STRING` | Convert to unit string |
| `COMMAND_CONVERT_UNIT` | Convert to specific unit |
| `COMMAND_CONVERT_OPTIMAL` | Convert to optimal unit |
| `COMMAND_CONVERT_BASE` | Convert to base units |
| `COMMAND_CONVERT_MIXED` | Convert to mixed units |
| `COMMAND_CALCULATE` | Sub-calculation without function evaluation |
| `COMMAND_EVAL` | Full evaluation |

### SetTitleFunction (line 252-261)

A built-in `MathFunction` subclass registered with CALCULATOR:
```cpp
class SetTitleFunction : public MathFunction {
    // "settitle(text)" - allows expressions to set the window title
    int calculate(MathStructure&, const MathStructure &vargs, const EvaluationOptions&);
};
```

### Global State Objects

| Global Variable | Type | Purpose |
|----------------|------|---------|
| `mstruct` | `MathStructure*` | Current calculation result |
| `parsed_mstruct` | `MathStructure*` | Parsed expression structure |
| `parsed_tostruct` | `MathStructure*` | Parsed "to" conversion target |
| `matrix_mstruct` | `MathStructure*` | Current matrix result |
| `mbak_convert` | `MathStructure` | Backup for unit conversion |
| `result_text` | `string` | Formatted result string |
| `parsed_text` | `string` | Formatted parsed expression |
| `result_text_long` | `string` | Long-form result text |
| `printops` | `PrintOptions` | Current print/formatting options |
| `evalops` | `EvaluationOptions` | Current evaluation options |
| `vans[5]` | `KnownVariable*[5]` | Answer variables (ans, ans2-5) |
| `v_memory` | `KnownVariable*` | Memory variable (MR/MC) |
| `f_title` | `MathFunction*` | SetTitle function |
| `CALCULATOR` | `Calculator*` | The libqalculate Calculator singleton |
| `main_builder` | `GtkBuilder*` | Builder for main.ui |
| `mainwindow` | `GtkWindow*` | The main window widget |

---

## 3. Connection to libqalculate Calculator

### Initialization Chain (main.cc -> mainwindow.cc)

```
main() 
  → gtk_application_new("io.github.Qalculate")
  → qalculate_activate() 
    → create_application()
      → new Calculator(ignore_locale)           // Create CALCULATOR singleton
      → load_preferences()                       // Load settings → sets printops, evalops
      → create_main_window()                     // Build UI
      → CALCULATOR->loadExchangeRates()          // Load exchange rates
      → CALCULATOR->loadGlobalDefinitions()      // Load unit/function definitions
      → initialize_variables_and_functions()     // Create ans1-5, memory, settitle
      → CALCULATOR->loadLocalDefinitions()       // Load user definitions
      → definitions_loaded()                     // Build menu trees
```

### Calculator Usage Patterns

**1. Expression Execution** (`execute_expression()`, line 4284-5658):

The central calculation function. Flow:
```
User presses Enter / auto-calc triggers
  → execute_expression()
    → Strips comments, detects /commands (set, save, store, etc.)
    → CALCULATOR->parse(str, parsed_mstruct, evalops.parse_options)
    → Handles "to" conversions, temperature units, percentage parsing
    → CALCULATOR->calculate(&mstruct, str, evalops)
    → setResult() → sends to ViewThread for formatting
```

**2. Auto-calculation** (`do_auto_calc()`, line 1290-2037):

Real-time calculation as the user types:
```
Expression text modified
  → handle_expression_modified()
    → do_auto_calc()
      → CALCULATOR->parse() + CALCULATOR->calculate() 
      → setResult(update_history=false) for instant preview
```

**3. Result Formatting** (ViewThread::run(), line 2485-2624):

```
ViewThread receives MathStructure*
  → m.format(printops)              // Apply formatting options
  → m.print(po, true)              // Generate result_text string
  → draw_result_temp(m)            // Render via Cairo (drawstructure.cc)
```

**4. Command Execution** (`executeCommand()`, line 3070-3233):

```
User clicks Factorize/Expand/etc.
  → executeCommand(COMMAND_FACTORIZE)
    → Creates copy of mstruct
    → command_thread->write(type + mfactor)
    → CommandThread applies transformation
    → setResult() with the modified structure
```

**5. Preferences and Options**:

The Calculator is configured through two libqalculate option structs:
- `printops` (PrintOptions): output base, decimal places, multiplication sign, Unicode, fraction format, etc.
- `evalops` (EvaluationOptions): approximation mode, angle unit, complex form, parsing mode, etc.

These are set by `load_preferences()`, `set_option()` (for /commands), and menu callbacks.

---

## 4. UI Components

### Created in `create_main_window()` (line 8916-9175)

| Component | Creation Function | Widget Type | Source File |
|-----------|------------------|-------------|-------------|
| Expression Input | `create_expression_edit()` | `GtkTextView` + completion popup | `expressionedit.cc` |
| Expression Status | `create_expression_status()` | `GtkBox` with parse info, approx indicator | `expressionstatus.cc` |
| Result Display | `create_result_view()` | `GtkOverlay` with Cairo drawing area | `resultview.cc` |
| Keypad | `create_keypad()` | `GtkGrid` with calculator buttons | `keypad.cc` |
| History | `create_history_view()` | `GtkTextView` (rich text history) | `historyview.cc` |
| RPN Stack | `create_stack_view()` | `GtkTreeView` | `stackview.cc` |
| Conversion | `create_conversion_view()` | `GtkBox` with unit selector | `conversionview.cc` |
| Menu Bar | `create_menubar()` | `GtkMenuBar` | `menubar.cc` |

### GTK Widget Hierarchy (from main.ui)

```
main_window (GtkWindow)
├── menubar (GtkMenuBar)
├── topframe (GtkFrame)
│   └── topframebox (GtkBox, vertical)
│       ├── statusframe / expressionbox (configurable order via expression_pos)
│       ├── expression_box (GtkBox, horizontal)
│       │   ├── expression_edit (GtkTextView)
│       │   ├── expression_button_stack (GtkStack)
│       │   │   ├── stop_button
│       │   │   ├── spinner_button
│       │   │   ├── info_icon
│       │   │   └── message_tooltip_icon
│       │   └── message_revealer → message_bar (GtkInfoBar)
│       └── resultoverlay → result area (GtkOverlay)
├── tabs (GtkNotebook)
│   ├── history tab (history_view_widget)
│   ├── stack tab (stack view)  [RPN mode]
│   └── convert tab (conversion_view)
├── expander_keypad → keypad_widget
├── expander_history → tabs
├── expander_stack → tabs (RPN)
└── expander_convert → tabs
```

### Expandable Panel System

The bottom panels use a custom show/hide mechanism:

- **Non-persistent mode** (default): Panels shown via GtkExpander, appear in a GtkNotebook
  - Keypad OR tabs (history/stack/convert) are shown, not both
- **Persistent mode**: Keypad and tabs shown simultaneously
- Panel state tracked by: `show_keypad`, `show_history`, `show_stack`, `show_convert`, `persistent_keypad`

### Dialog Windows (28 .ui files)

Each managed by its own .cc module:

| Dialog | Purpose |
|--------|---------|
| `preferences.ui` | Application preferences |
| `functions.ui` | Function browser/selector |
| `variables.ui` | Variable browser/selector |
| `units.ui` | Unit browser/selector |
| `datasets.ui` | Dataset browser/selector |
| `functionedit.ui` | Create/edit functions |
| `variableedit.ui` | Create/edit variables |
| `unitedit.ui` | Create/edit units |
| `matrix.ui` / `matrixedit.ui` | Matrix creation/editing |
| `plot.ui` | Plotting/graphing |
| `nbases.ui` | Number base conversion |
| `floatingpoint.ui` | Floating point details |
| `percentage.ui` | Percentage calculator |
| `calendarconversion.ui` | Calendar conversion |
| `periodictable.ui` | Periodic table |
| `shortcuts.ui` | Keyboard shortcuts |
| `buttonsedit.ui` | Custom keypad buttons |
| `precision.ui` | Set precision |
| `decimals.ui` | Set decimal places |
| `setbase.ui` | Set number base |
| `namesedit.ui` | Edit names/aliases |
| `unknownedit.ui` | Edit unknowns |
| `datasetedit.ui` | Edit datasets |
| `csvimport.ui` / `csvexport.ui` | CSV import/export |

### Styling

- CSS providers: `topframe_provider`, `app_provider`, `app_provider_theme`, `color_provider`
- Theme support: Adwaita, Adwaita-Dark, HighContrast, HighContrast-Inverse
- Custom app font, result font, history font, keypad font
- Country flag icons loaded from GResource at startup, scaled to font metrics

---

## 5. Lines of Code

| File | Lines |
|------|-------|
| `mainwindow.cc` | **9,300** |
| `mainwindow.h` | **214** |
| **Total** | **9,514** |

### Function Count in mainwindow.cc

- **~198 function definitions** (including callbacks, helpers, and core functions)
- Largest functions:
  - `execute_expression()` - ~1,374 lines (4284-5658)
  - `do_auto_calc()` - ~747 lines (1290-2037)
  - `load_preferences()` - ~599 lines (5961-6560)
  - `set_result()` - ~361 lines (2629-2990)
  - `executeCommand()` - ~164 lines (3070-3234)
  - `create_main_window()` - ~259 lines (8916-9175)
  - `set_option()` - ~833 lines (3408-4241)
  - `save_preferences()` - ~255 lines (6629-6884)

### Key Architectural Metrics

| Metric | Value |
|--------|-------|
| Global variables | ~80+ |
| External dependencies | libqalculate, GTK 3, GDK, GLib |
| Background threads | 2 (ViewThread, CommandThread) |
| Dialog types | ~28 |
| Keyboard shortcut types | ~70+ (defined in settings.h) |
| Answer history slots | 5 (ans, ans2-5) |
| UI files referenced | 28 |

---

## 6. Key Architectural Patterns

### Threading Model

```
Main Thread (GTK event loop)
    │
    ├── ViewThread (formatting/rendering)
    │   ├── Receives: MathStructure*, PrintOptions
    │   ├── Produces: result_text, parsed_text, Cairo surfaces
    │   └── Communication: thread-safe queue (read/write)
    │
    └── CommandThread (transformations)
        ├── Receives: command_type, MathStructure*
        ├── Performs: factorize, expand, convert, etc.
        └── Communication: thread-safe queue (read/write)
```

Both threads use `CALCULATOR->startControl()` / `CALCULATOR->stopControl()` for thread-safe calculator access.

### Calculation Flow

```
User Input → expression_edit → expression_modified signal
    │
    ├── Auto-calc mode → do_auto_calc() → CALCULATOR->calculate() → setResult()
    │
    └── Manual mode → Enter key → execute_expression() → CALCULATOR->calculate() → setResult()
                                                                    │
                                                            ┌───────┴───────┐
                                                            │  setResult()  │
                                                            └───────┬───────┘
                                                                    │
                                                    ┌───────────────┴───────────────┐
                                                    │  ViewThread::run()            │
                                                    │  m.format() + m.print()       │
                                                    │  draw_result_temp() → Cairo   │
                                                    └───────────────────────────────┘
```

### Blocking/Synchronization

The codebase uses a counter-based blocking system:
- `block_expression_execution` / `block_result_update` / `block_error_timeout`
- `b_busy`, `b_busy_command`, `b_busy_result`, `b_busy_expression` flags
- During busy state, UI widgets are disabled and a spinner is shown

### Preferences Persistence

Settings stored in `~/.local/share/qalculate/qalculate-gtk.cfg`:
- Mode (printops, evalops, assumptions, precision, etc.)
- Window geometry, panel visibility
- Keyboard shortcuts (stored in `keyboard_shortcuts` map)
- History, recent items
- Custom buttons
- Expression font, result font, etc.

---

## 7. Notable Design Decisions

1. **Procedural architecture**: The 9,300-line file is a monolithic procedural module rather than an object-oriented design. This is characteristic of early 2000s GTK applications.

2. **No abstraction over CALCULATOR**: The libqalculate `Calculator` singleton is accessed directly throughout the code, creating tight coupling between UI and engine.

3. **String-based widget lookup**: Widgets are retrieved via `gtk_builder_get_object(main_builder, "widget_name")` rather than cached pointers, which is slow but flexible.

4. **Dual clipboard support**: On Windows, uses native `OpenClipboard`/`SetClipboardData` with HTML format; on Linux, uses `gtk_clipboard_set_with_data`.

5. **Minimal mode**: A compact mode that hides the menu bar, tabs, and keypad, showing only the expression and result.

6. **Chain mode**: Allows continuing calculations by automatically inserting the result as the first operand of the next operation.

7. **RPN mode**: Full Reverse Polish Notation support with stack operations, shown in a dedicated stack view tab.
