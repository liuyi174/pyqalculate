# PyQalculate v2.1.2 — Development Plan

> **Project Goal**: Integrate the existing Plotter into the calculator so `plot(x^2, -5, 5)` generates an image file.
>
> **Scope**: 3 targeted changes: new PlotFunction class, calculator wiring, and integration tests.
>
> **This document is for execution by subsequent agents. Follow tasks in priority order.**

---

## 1. Project Overview

### 1.1 v2.1.2 Goal

v2.1.1 delivered correct interval arithmetic and a 79/79 reference test pass rate. The test code audit that followed revealed a gap: plot functionality exists in `pyqalculate/plot.py` (a complete matplotlib-based Plotter class), but nothing connects it to the calculator's evaluation pipeline. Typing `plot(x^2, -5, 5)` today returns the expression as a string, unchanged.

v2.1.2 bridges this gap. The Plotter is already built. The work is wiring it up and proving it works end-to-end.

The end state: `calc.calculate_and_print("plot(x^2, -5, 5)")` generates a PNG file, with all 79 reference tests and 972 unit tests still passing.

### 1.2 v2.1.1 Recap

| Metric | v2.0 | v2.1 | v2.1.1 |
|--------|------|------|--------|
| Reference tests passing | 71/79 (89.9%) | 79/79 (100%) | 79/79 (100%) |
| Unit tests | ~1,200+ | 971 | 972 |
| Failed tests | 2 | 0 | 0 |
| Skipped tests | 6 | 0 | 2 |

**What v2.1.1 accomplished:**
- Interval arithmetic fix: `interval(-3; 7)^3` now returns `interval(-27, 343)` instead of the wrong `interval(-52, 68)`
- Correlation test docstring corrected
- All 79/79 reference tests passing
- 972 unit tests passing, 2 skipped

### 1.3 What v2.1.2 Does Not Cover

- New mathematical functions beyond `plot`
- Performance optimization or benchmarking
- Web interface or API changes
- GUI enhancements
- Currency or real-time data integration
- Plot styling or customization options (the Plotter already supports those; v2.1.2 just wires up the basic path)

---

## 2. Issue Analysis

### 2.1 The Plot Integration Gap

**Expression**: `plot(x^2, -5, 5)`

**Expected**: A PNG file generated at the working directory (or specified path).

**Actual**: Returns the literal string `plot(x^2, -5, 5)` unevaluated.

**Root Cause — three broken links in the chain:**

**Link 1: No PlotFunction class exists.**
`pyqalculate/builtin_functions.py` defines `FUNCTION_ID_PLOT = 2690` (line ~2690 region), but there is no corresponding `PlotFunction(MathFunction)` class anywhere in the file. The ID is allocated but unused.

**Link 2: The Plotter is disconnected from the Calculator.**
`pyqalculate/plot.py` contains a complete `Plotter` class (322 lines, matplotlib-based) with methods for single-function plots, multi-function plots, data plots, and raw data generation. But `pyqalculate/calculator.py` never imports `plot.py` and has no reference to the Plotter.

**Link 3: The parser creates a symbolic node that goes nowhere.**
When the parser encounters `plot(x^2, -5, 5)`, it creates a `FUNCTION` AST node with name `plot`. During evaluation, this node is passed to SymPy, which has no concept of a `plot` function. The expression passes through unchanged and gets printed as-is.

**How libqalculate handles this (for reference):**
libqalculate implements plot as a Calculator-level command (`Calculator-plot.cc`), not as a MathFunction. It intercepts the plot call before it reaches the symbolic evaluation engine. pyqalculate can take a different approach: implement it as a MathFunction that calls the Plotter from within its `calculate()` method, since the Plotter is already complete.

### 2.2 The Existing Plotter API

The Plotter in `pyqalculate/plot.py` already supports everything needed:

```python
from pyqalculate.plot import Plotter

plotter = Plotter(calculator=calc)

# Single function
plotter.plot("x^2", x_min=-5, x_max=5, filename="plot.png")

# Multiple functions
plotter.plot_multi(["sin(x)", "cos(x)"], x_min=0, x_max=6.28)

# Raw data
plotter.plot_data(x_values, y_values)

# Data generation without rendering
plotter.generate_data("x^2", x_min=-5, x_max=5)
```

The Plotter uses matplotlib for rendering. It parses the function string through the calculator's own evaluation engine, evaluates it over a range of x values, and plots the results. None of this needs to be rewritten.

---

## 3. Development Tasks

### Task 1: Create PlotFunction class [MEDIUM — 2-4 hours]

**What**: Implement a `PlotFunction(MathFunction)` class that bridges the parser and the Plotter.

**File to modify**: `pyqalculate/builtin_functions.py`

**Class structure**:

```python
class PlotFunction(MathFunction):
    """plot(function, x_min, x_max [, filename]) — plot a function."""

    def __init__(self):
        MathFunction.__init__(self)
        self._name = "plot"
        self._title = TRANSLATE("plot function")
        self._description = TRANSLATE("Plot a function over a given range.")

    def id(self):
        return FUNCTION_ID_PLOT

    def calculate(self, arguments, precision, options, *kwargs):
        # 1. Extract function string from first argument
        # 2. Extract x_min and x_max from second and third arguments
        # 3. Extract optional filename (fourth argument)
        # 4. Import and create Plotter(calculator=self.parent)
        # 5. Call plotter.plot(function_str, x_min, x_min, filename=filename)
        # 6. Return MathStructure containing the filename string
```

**Argument parsing details**:
- Argument 0: function string (e.g., `"x^2"`)
- Argument 1: x_min (number)
- Argument 2: x_max (number)
- Argument 3 (optional): filename (string, defaults to `"plot.png"`)

**Register in `get_default_registry()`**:
Add `PlotFunction()` to the list of functions returned by the default registry. Follow the pattern of other function registrations in the same file.

**Key decisions**:
- The `calculate()` method should catch matplotlib errors (e.g., missing display) and return an error MathStructure instead of crashing
- The filename should be resolved relative to the current working directory
- If matplotlib is not installed, the function should return a descriptive error message

**Verification**:
```python
from pyqalculate import Calculator
calc = Calculator()
# After implementation, plot() should no longer pass through unevaluated
result = calc.calculate_and_plot("plot(x^2, -5, 5)")
# Should generate a file, not return the expression string
```

**Risk**: Low-medium. The Plotter works. The challenge is argument extraction from MathStructure objects, which requires following existing patterns in the codebase.

---

### Task 2: Add calculator integration [MEDIUM — 1-2 hours]

**What**: Wire the Plotter into the Calculator so PlotFunction can access it.

**File to modify**: `pyqalculate/calculator.py`

**Changes**:

1. **Import the plot module**:
   ```python
   from pyqalculate.plot import Plotter
   ```

2. **Add a `_plotter` property** for lazy initialization:
   ```python
   @property
   def plotter(self):
       if self._plotter is None:
           self._plotter = Plotter(calculator=self)
       return self._plotter
   ```

3. **Initialize `_plotter = None` in `__init__`**.

4. **Add a convenience method** (optional but useful):
   ```python
   def plot(self, function_str, x_min=-10, x_max=10, filename="plot.png"):
       """Plot a function string over the given range."""
       return self.plotter.plot(function_str, x_min=x_min, x_max=x_max, filename=filename)
   ```

**Why lazy initialization**: The Plotter imports matplotlib, which is a heavy import. Initializing it only when needed keeps calculator startup fast for non-plot use cases.

**Verification**:
```python
from pyqalculate import Calculator
calc = Calculator()
# Verify plotter property works
assert hasattr(calc, 'plotter')
assert calc.plotter is not None
```

**Risk**: Low. Adding a property and an import doesn't affect existing functionality.

---

### Task 3: Add tests [EASY — 30 min]

**What**: Create integration tests that prove `plot()` works through the calculator.

**File to create**: `tests/test_plot.py`

**Test cases**:

```python
import os
import pytest
from pyqalculate import Calculator


class TestPlotIntegration:
    """Integration tests for the plot() function."""

    def setup_method(self):
        self.calc = Calculator()

    def test_plot_generates_file(self, tmp_path):
        """plot(x^2, -5, 5) should generate a PNG file."""
        filename = str(tmp_path / "test_plot.png")
        self.calc.calculate_and_plot("plot(x^2, -5, 5)")
        assert os.path.exists(filename) or os.path.exists("plot.png")

    def test_plot_with_custom_filename(self, tmp_path):
        """plot(x^2, -5, 5, 'my_plot.png') should use the given filename."""
        filename = str(tmp_path / "my_plot.png")
        self.calc.calculate_and_plot(f"plot(x^2, -5, 5, '{filename}')")
        assert os.path.exists(filename)

    def test_plot_sin(self, tmp_path):
        """plot(sin(x), 0, 6.28) should generate a file."""
        self.calc.calculate_and_plot("plot(sin(x), 0, 6.28)")
        # Verify some output file was created
        assert os.path.exists("plot.png") or any(
            f.endswith(".png") for f in os.listdir(tmp_path)
        )

    def test_plot_invalid_range(self):
        """plot(x^2, 5, -1) with x_min > x_max should handle gracefully."""
        # Should not raise, just produce an error or empty plot
        try:
            self.calc.calculate_and_plot("plot(x^2, 5, -1)")
        except Exception:
            pass  # Acceptable to raise on invalid range

    def test_plot_returns_filename(self):
        """plot() should return the filename as the result string."""
        result = self.calc.qalculate("plot(x^2, -5, 5)")
        # Result should mention the filename, not the raw expression
        assert "plot" in result.lower() or ".png" in result.lower()
```

**Verification**:
```bash
pytest tests/test_plot.py -v
```

**Risk**: None. Tests only. If they fail, the implementation needs fixing, not the tests.

---

## 4. Test Strategy

### 4.1 Per-Task Verification

| Task | Verification Method | Pass Criteria |
|------|-------------------|---------------|
| Task 1: PlotFunction class | Instantiate class, verify id() returns 2690 | `FUNCTION_ID_PLOT` returned |
| Task 2: Calculator integration | `calc.plotter` returns a Plotter instance | No import errors, property works |
| Task 3: Integration tests | `pytest tests/test_plot.py -v` | All 5 tests pass |

### 4.2 Regression Testing

After Task 2, run the full test suite:

```bash
pytest tests/ -v --tb=short
```

Expected: All 972 unit tests pass, all 79 reference tests pass. No regressions.

### 4.3 Key Regression Checks

Verify these still work after the plot integration:

1. **All reference tests**: `pytest tests/test_qalculate_reference.py -v` — 79/79 passing
2. **All unit tests**: `pytest tests/ -v` — 972 passing, 2 skipped
3. **Calculator instantiation**: `Calculator()` creates without errors
4. **Existing function calls**: `calc.qalculate("2+2")` still returns `"4"`
5. **Mathematica compatibility**: `calc.qalculate("N[Sin[1], 50]")` still works

### 4.4 Matplotlib Dependency Handling

The Plotter requires matplotlib. If matplotlib is not installed:
- `PlotFunction.calculate()` should catch the `ImportError` and return a descriptive error message
- The calculator should not crash or become unusable
- All non-plot tests should pass regardless of matplotlib availability

---

## 5. Risk Assessment

### 5.1 Task 1: PlotFunction Class

| Aspect | Assessment |
|--------|------------|
| Risk | Low-medium |
| Blast radius | `builtin_functions.py` only |
| Regression potential | Low (new class, no existing code modified) |
| Mitigation | Follow existing MathFunction patterns exactly |

**Why risk is low-medium**:
1. The Plotter is already complete and tested in isolation
2. The PlotFunction class is new code, not a modification of existing behavior
3. The main risk is incorrect argument extraction from MathStructure objects, but this follows well-established patterns in the codebase

### 5.2 Task 2: Calculator Integration

| Aspect | Assessment |
|--------|------------|
| Risk | Low |
| Blast radius | `calculator.py` — one import, one property, one method |
| Regression potential | Negligible |
| Mitigation | Lazy initialization prevents side effects |

**Why risk is low**:
1. Adding an import doesn't change existing code paths
2. Lazy initialization means the Plotter is only created when accessed
3. The convenience method is additive, not modifying existing methods

### 5.3 Task 3: Tests

| Aspect | Assessment |
|--------|------------|
| Risk | None |
| Blast radius | New test file only |
| Regression potential | Zero |
| Mitigation | Not needed |

### 5.4 Worst-Case Scenarios

**Scenario A**: matplotlib is not installed in the test environment.
- **Impact**: Plot tests would fail with ImportError.
- **Mitigation**: The PlotFunction should catch ImportError and return a graceful error. Tests can be marked with `@pytest.mark.skipif` if matplotlib is unavailable.

**Scenario B**: Argument extraction from MathStructure fails for edge cases.
- **Impact**: `plot()` might not parse all input formats correctly.
- **Mitigation**: Handle the standard case first (`plot(func, min, max)`), then add optional argument support. The Plotter API is flexible and handles various input styles.

**Scenario C**: The Plotter's `plot()` method signature has changed.
- **Impact**: PlotFunction might call it incorrectly.
- **Mitigation**: Read the actual Plotter source before implementing. The API documented in section 2.2 should be verified against the current code.

---

## 6. Execution Order

### 6.1 Recommended Order

**Step 1 — PlotFunction class** (Task 1):
- Create the class in `builtin_functions.py`
- This is the core change and should be done first
- Verify it registers correctly before proceeding

**Step 2 — Calculator integration** (Task 2):
- Wire up the Calculator to use the Plotter
- This depends on Task 1 being complete
- Verify the property and convenience method work

**Step 3 — Tests** (Task 3):
- Write and run integration tests
- This validates the entire chain end-to-end
- Should be done last since it exercises both Task 1 and Task 2

### 6.2 Parallel Execution

Task 2 can be started in parallel with Task 1 since they modify different files. Task 3 depends on both and should wait.

---

## 7. Deliverables

### 7.1 Modified Files

| File | Task | Changes |
|------|------|---------|
| `pyqalculate/builtin_functions.py` | 1 | Add `PlotFunction(MathFunction)` class, register in `get_default_registry()` |
| `pyqalculate/calculator.py` | 2 | Import Plotter, add `_plotter` property, add convenience `plot()` method |
| `tests/test_plot.py` | 3 | New file with 5 integration tests |

### 7.2 No New Dependencies

The Plotter already depends on matplotlib. No new package dependencies are introduced. The integration just uses what already exists.

### 7.3 Expected Outcome

| Metric | Before v2.1.2 | After v2.1.2 |
|--------|---------------|--------------|
| Reference tests passing | 79/79 (100%) | 79/79 (100%) |
| Unit tests passing | 972 | 972 (no regressions) |
| `plot(x^2, -5, 5)` | Returns expression string unchanged | Generates PNG file |
| Plot integration tests | 0 | 5 (all passing) |

---

## 8. Appendix: Why MathFunction Instead of Calculator-Level Command

### 8.1 The Two Approaches

**Approach A (libqalculate style)**: Intercept `plot()` in the calculator's evaluation pipeline, before it reaches the symbolic engine. This is how libqalculate does it in `Calculator-plot.cc`.

**Approach B (pyqalculate style, chosen)**: Implement `plot()` as a `MathFunction` subclass, just like `sin()`, `factorial()`, or `integral()`. The function gets registered, parsed, and evaluated like any other. Its `calculate()` method calls the Plotter.

### 8.2 Why Approach B Works Here

1. **The Plotter is already complete**. We don't need to intercept early. We just need to call it from somewhere.
2. **MathFunction is the established pattern** in pyqalculate. Every function is a MathFunction subclass. Adding plot as anything else would be inconsistent.
3. **Argument parsing is already handled**. The parser will split `plot(x^2, -5, 5)` into three arguments automatically. We just extract them in `calculate()`.
4. **Error handling follows existing patterns**. If the Plotter fails, we return an error MathStructure, same as any other function that fails.

### 8.3 When Approach A Would Be Better

If the Plotter needed to be called BEFORE symbolic evaluation (e.g., to intercept the expression before SymPy sees it), Approach A would be necessary. But since the Plotter takes a function string and evaluates it independently, there's no timing issue.

---

*Document created for PyQalculate v2.1.2 development. Execute tasks in order. Run full regression suite after Task 2.*
