# qalculate-gtk GUI Component Analysis Overview

## Summary

This document provides an architectural overview of three core GUI components in qalculate-gtk: the expression input, result display, and history view. Together, they form the primary user interaction loop.

## Files Analyzed

| Component | Header | Implementation | Total Lines |
|-----------|--------|----------------|-------------|
| Expression Edit | expressionedit.h (109) | expressionedit.cc (1970) | **2079** |
| Result View | resultview.h (66) | resultview.cc (1392) | **1458** |
| History View | historyview.h (81) | historyview.cc (3717) | **3798** |
| **Total** | **256** | **7079** | **7335** |

## Architecture Diagram

```
+-------------------+
|   Expression Edit |  GtkTextView + GtkTextBuffer
|   (2079 lines)    |
+--------+----------+
         |
         | get_expression_text() / set_expression_text()
         | on_expressionbuffer_changed()
         |
         v
+-------------------+     +-------------------+
| Calculator Engine |     |   Expression      |
| (libqalculate)    |<--->|   Completion      |
|                   |     |   (separate cc)   |
+--------+----------+     +-------------------+
         |
         | current_result() / current_parsed_result()
         |
    +----+----+
    |         |
    v         v
+--------+ +-----------+
| Result | | History   |
| View   | | View      |
|(1458)  | | (3798)    |
+--------+ +-----------+
```

## Data Flow

### 1. User Types Expression
```
Expression Edit -> on_expressionbuffer_changed()
  -> set_expression_modified()
    -> handle_expression_modified() [mainwindow.cc]
      -> auto_calculate triggers CALCULATOR->calculateAndPrint()
    -> add_completion_timeout() [autocomplete]
    -> highlight_parentheses()
```

### 2. User Executes (Enter or Button)
```
Expression Edit -> execute_expression() [mainwindow.cc]
  -> CALCULATOR->calculateAndPrint()
    -> [Calculation happens]
  -> Result View: draw_result_pre() + draw_result() + draw_result_finalize()
  -> History View: add_result_to_history_pre() + add_result_to_history()
  -> Expression Edit: add_to_expression_history()
```

### 3. History Interaction
```
History View: user selects entries + clicks operator button
  -> history_operator()
    -> Builds expression: answer(3) + answer(5)
    -> insert_text() into Expression Edit
    -> execute_expression()
```

## Calculator Integration Points

| Component | Calculator APIs Used |
|-----------|---------------------|
| Expression Edit | unlocalizeExpression(), parseSigns(), calculateAndPrint(), getActiveFunction(), separateToExpression(), hasToExpression(), getDecimalPoint() |
| Result View | draw_structure() via PrintOptions, aborted(), f_interval, f_sqrt, can_display_unicode_string_function() |
| History View | answer(N) / expression(N) functions, message()/nextMessage(), getActiveExpressionItem(), getFunctionById() |

## Key Design Patterns

1. **Block/Unblock Pattern**: Reference-counted blocking for undo, modification, icon updates, completion - prevents recursive event handling during programmatic edits.

2. **Surface-based Rendering**: Results rendered to cairo_surface_t off-screen, then painted. Enables efficient re-rendering and scaling without recalculating.

3. **Parallel Data Stores**: History maintains parallel deques (inhistory, inhistory_type, inhistory_time, inhistory_protected, inhistory_value) - C-style data management.

4. **Dynamic Popup Menus**: Both result view and expression edit have context menus that dynamically show/hide items based on current result type.

5. **MathStructure Bridge**: MathStructure pointers in history_parsed/history_answer allow answer()/expression() functions to reference exact historical values without re-parsing.

## Cross-Component Dependencies

```
expressionedit.cc
  includes: historyview.h, stackview.h, keypad.h, preferencesdialog.h,
            insertfunctiondialog.h, expressionstatus.h, expressioncompletion.h

resultview.cc
  includes: expressionedit.h, expressionstatus.h, drawstructure.h

historyview.cc
  includes: expressionedit.h, insertfunctiondialog.h, keypad.h
```

All three modules share settings.h for global state (evalops, printops, rpn_mode, auto_calculate, parsed_in_result, etc.) and mainwindow.h for main_window(), execute_expression(), current_result().

## Detailed Analysis Files

- [expression_edit.md](expression_edit.md) - Expression input field analysis
- [result_view.md](result_view.md) - Result display area analysis
- [history_view.md](history_view.md) - History panel analysis
