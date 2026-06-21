# qalculate-gtk GUI Analysis: Keypad, Conversion View, and Button Editing

## Overview
This analysis covers three interconnected modules that form the button-based input and unit conversion UI of qalculate-gtk.

## Module Summary

| Module | Files | Total Lines | Role |
|--------|-------|-------------|------|
| Keypad | keypad.cc/h | 3,846 | Calculator button keypad (versatile + programming modes) |
| Conversion View | conversionview.cc/h | 561 | Unit conversion tab with category/unit browsing |
| Buttons Edit Dialog | buttonseditdialog.cc/h | 540 | Preferences dialog for customizing button actions |
| **TOTAL** | **6 files** | **4,947** | |

## Architecture Diagram

`
+---------------------------+
| buttonseditdialog.cc/h    |  User edits button assignments
| (Preferences Dialog)      |  Writes to custom_buttons[]
+---------------------------+
            |
            v
+---------------------------+
| keypad.cc/h               |  Reads custom_buttons[] at runtime
| (On-screen Keypad)        |  49 buttons with left/right/middle click
| - Versatile mode          |  Each button inserts text/functions/operators
| - Programming mode        |  into expression_edit
| - Custom buttons (C1-C20) |
+---------------------------+
            |
            | insert_text / insert_button_function / insert_unit
            v
+---------------------------+
| expressionedit.cc/h       |  Expression entry widget
+---------------------------+
            |
            | execute_expression()
            v
+---------------------------+
| CALCULATOR (libqalculate) |  Core calculation engine
+---------------------------+
            |
            | current_result()
            v
+---------------------------+
| conversionview.cc/h       |  Converts result to target unit
| (Unit Conversion Tab)     |  Category tree + unit list + entry field
|                           |  Calls convert_result_to_unit_expression()
+---------------------------+
`

## Key Design Patterns

### 1. Multi-click Buttons
Every keypad button supports up to 3 click types: left-click (default action), right-click (secondary), and middle-click (tertiary). This is managed through the custom_button struct with type[3]/value[3] arrays. The DO_CUSTOM_BUTTONS macro intercepts button events before default behavior.

### 2. Lazy Dialog Creation
The buttons edit dialog uses a lazy singleton pattern -- it is only built from the UI file on first open, and reused thereafter.

### 3. Calculator as Single Source of Truth
All three modules read state from the global CALCULATOR object, evalops, and printops. The keypad syncs its toggle buttons to these globals, and the conversion view queries CALCULATOR for unit listings and conversion.

### 4. Settings Persistence
All three modules implement read_*_settings_line() and write_*_settings() for config file serialization.

## Files Created
- D:\1\1tmp\pyqalculate\docs\gui_analysis\keypad_analysis.md
- D:\1\1tmp\pyqalculate\docs\gui_analysis\conversionview_analysis.md
- D:\1\1tmp\pyqalculate\docs\gui_analysis\buttonseditdialog_analysis.md
- D:\1\1tmp\pyqalculate\docs\gui_analysis\README.md (this file)