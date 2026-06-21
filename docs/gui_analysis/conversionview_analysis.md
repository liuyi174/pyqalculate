# Conversion View Module Analysis (conversionview.cc/h)

## Purpose
The conversion view implements the Unit Conversion tab in qalculate-gtk. It provides a two-panel interface: a category tree on the left for browsing unit categories (Length, Mass, Time, Currency, etc.) and a unit list on the right showing units within the selected category. Users can type a target unit in an entry field and convert the current result to that unit.

## Files
- conversionview.cc: 530 lines
- conversionview.h: 31 lines
- Total: 561 lines

## Key Data Structures

### Global Widgets
- tUnitSelectorCategories (GtkWidget*): Category tree view (left panel)
- tUnitSelector (GtkWidget*): Unit list view (right panel)
- tUnitSelector_store (GtkListStore*): 4-column store: name(string), Unit*(pointer), flag_surface(cairo_surface_t*), visible(boolean)
- tUnitSelector_store_filter (GtkTreeModel*): Filtered view for search
- tUnitSelectorCategories_store (GtkTreeStore*): 2-column hierarchical store: display_name(string), full_path(string)

### State Variables
- selected_unit_selector_category (string): Currently selected category path
- continuous_conversion (bool, default true): Auto-convert on selection change
- set_missing_prefixes (bool, default false): Auto-add ? prefix for best metric prefix
- block_unit_selector_convert (bool): Prevents conversion during category repopulation
- block_conversion_category_switch (int): Counter to prevent category auto-switching
- keep_unit_selection (bool): Preserves unit selection during programmatic entry changes
- convert_category_map (unordered_map<string, GtkTreeIter>): Fast path-to-iterator lookup

## Key Functions

### View Creation
- create_conversion_view() (491-530): Initializes both tree views, creates stores with sort/filter, sets up cell renderers (flag column for currencies, name column), connects all signal handlers

### Category Navigation
- update_unit_selector_tree() (75-142): Rebuilds entire category tree from unit_cats (tree_struct hierarchy). Adds All root and Uncategorized leaf. Restores previous selection
- on_tUnitSelectorCategories_selection_changed() (158-237): Repopulates unit list when category changes. Iterates CALCULATOR->units[] matching category via string prefix. Shows/hides flag column for currencies. Implements accordion expand-collapse
- on_convert_treeview_category_row_expanded() (264-277): Collapses sibling rows (accordion)

### Unit Selection and Conversion
- on_tUnitSelector_selection_changed() (239-262): Sets entry text to selected unit name, triggers conversion if continuous mode enabled
- setUnitSelectorTreeItem() (144-153): Adds unit to list store with optional flag for currencies
- convert_from_convert_entry_unit() (412-423): Reads entry, adds ? prefix if needed, calls convert_result_to_unit_expression()
- update_conversion_view_selection() (452-474): Auto-selects category for result unit via CALCULATOR->findMatchingUnit()
- current_conversion_expression() (478-488): Returns conversion expression string

### Search/Filter
- on_convert_entry_search_changed() (379-411): Real-time filter: sets row visibility based on name_matches/title_matches/country_matches. Auto-selects first match

### Context Menu
- on_convert_treeview_unit_button_press_event() (327-367): Middle-click inserts unit; right-click opens context menu
- on_popup_menu_convert_insert_activate() (295-302): Insert unit into expression
- on_popup_menu_convert_convert_activate() (303-326): Set unit as conversion target

### Toggle Buttons and Entry
- on_convert_button_continuous_conversion_toggled(): Toggle continuous conversion
- on_convert_button_set_missing_prefixes_toggled(): Toggle auto-prefix mode
- on_convert_button_convert_clicked(): Manual convert button
- on_convert_entry_unit_changed(): Updates clear icon, unselects unit on manual edit
- on_convert_entry_unit_activate(): Enter key triggers conversion

### Settings Persistence
- read_conversion_view_settings_line() / write_conversion_view_settings(): Read/write continuous_conversion and set_missing_prefixes

## Calculator Interaction
- Iterates CALCULATOR->units[] for unit list (checking isActive, isHidden, isCurrency)
- Uses CALCULATOR->findMatchingUnit() for auto-detection of result unit
- Uses Unit::title(), preferredInputName(), category(), subtype(), referenceName() for display
- Uses CompositeUnit::print() for composite unit display (e.g., km/h)
- Calls convert_result_to_unit_expression() (resultview.cc) which calls CALCULATOR->convert()
- Uses flag_surfaces map for country flag icons next to currencies
- Uses CALCULATOR->getLocalCurrency() as fallback currency