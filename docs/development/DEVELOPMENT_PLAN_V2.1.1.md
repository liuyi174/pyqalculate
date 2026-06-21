# PyQalculate v2.1.1 — Development Plan

> **Project Goal**: Fix interval arithmetic for `interval()` inputs and correct a spurious test docstring sign.
>
> **Scope**: 2 targeted fixes, 1 docstring correction + 1 code change.
>
> **This document is for execution by subsequent agents. Follow tasks in priority order.**

---

## 1. Project Overview

### 1.1 v2.1.1 Goal

v2.1 achieved full reference test coverage: 79/79 passing, 971 unit tests passing. v2.1.1 is a surgical patch that addresses two issues discovered during comparison with libqalculate: one trivial docstring correction and one real interval arithmetic bug.

The end state: correct interval arithmetic for `interval()` inputs (not just `±` intervals), while maintaining all 79/79 reference tests and 971 unit tests.

### 1.2 v2.1 Recap

| Metric | v2.0 | v2.1 | v2.1.1 Target |
|--------|------|------|---------------|
| Reference tests passing | 71/79 (89.9%) | 79/79 (100%) | 79/79 (100%) |
| Unit tests | ~1,200+ | 971 | 971 (no regressions) |
| Failed tests | 2 | 0 | 0 |
| Skipped tests | 6 | 0 | 0 |

**What v2.1 accomplished:**
- All 9 original issues fixed (cbrt, sum, integer division, complex roots, bare number conversion, multisolve, Gaussian integral, planet dataset, interval unit simplification)
- 79/79 reference tests passing
- 971 unit tests passing

### 1.3 What v2.1.1 Does Not Cover

- Performance optimization
- New built-in functions
- Web interface or API changes
- GUI enhancements
- Currency or real-time data integration
- Additional reference test fixes beyond the 2 identified issues

---

## 2. Issue Analysis

### 2.1 Issue 1: Correlation Test Docstring Sign (NOT a real bug)

**Expression**: `correlation([1,2,3,4,5,6,7,8,9,10]; [2,4,5,4,5,7,8,9,10,12])`

**Expected (test docstring)**: `-0.9719076166`

**Actual (pyqalculate output)**: `+0.9719076166`

**Finding**: pyqalculate is **CORRECT**. The data shows a strong positive correlation: both X and Y increase together (X: 1→10, Y: 2→12). A correlation coefficient of +0.97 makes sense. The reference test docstring has a spurious negative sign.

**Root Cause**: The test docstring in `test_integration.py` line 969 contains `-0.9719076166` when it should say `0.9719076166`. This is a documentation error, not a code bug.

**Fix**: Change the docstring sign from negative to positive. No code change needed.

**Difficulty**: Trivial (1 line change)

---

### 2.2 Issue 2: Interval Arithmetic Uses Linear Approximation (REAL bug)

**Expression**: `interval(-3; 7)^3`

**Expected**: `interval(-27, 343)` (true interval arithmetic: evaluate at both endpoints)

**Actual**: `interval(-52, 68)` (variance/derivative formula applied)

**Root Cause**: In `number.py`, ALL five arithmetic operators (`__add__`, `__sub__`, `__mul__`, `__truediv__`, `__pow__`) use the variance/derivative formula for ALL intervals indiscriminately. The condition checks `self.is_interval() or other.is_interval()` and then applies linear propagation, which is only correct for `±` (plusminus) intervals used in uncertainty analysis.

The variance formula for intervals works like this:
- For `f(X) = X^n` where X is an interval `[a, b]`, the linear approximation gives `f(a) ± f'(mid) * half_width`
- This is a FIRST-ORDER APPROXIMATION, not true interval arithmetic
- For `interval(-3; 7)^3`, the mid is 2, half_width is 5, so the formula gives `2^3 ± 3*2^2*5 = 8 ± 60 = [-52, 68]`
- True interval arithmetic evaluates `(-3)^3 = -27` and `7^3 = 343`, giving `[-27, 343]`

The code already HAS proper interval arithmetic implementations (dead code paths that evaluate at both endpoints). But the variance formula short-circuits before reaching them.

**Key insight**: The code has an `is_plusminus()` method that distinguishes `±` intervals from `interval()` inputs. The fix is to guard the variance formula path with `is_plusminus()` so it only applies to uncertainty intervals.

**File**: `number.py`

**Difficulty**: Low-Medium (5 locations to change, existing code already correct)

---

## 3. Development Tasks

### Task 1: Fix correlation test docstring [TRIVIAL — 1 min]

**What**: Correct the sign in the correlation test docstring from negative to positive.

**File to modify**:
- `tests/test_integration.py` line 969

**Change**:
```python
# Before (line 969):
"""
...
    >>> calc.qalculate("correlation([1,2,3,4,5,6,7,8,9,10]; [2,4,5,4,5,7,8,9,10,12])")
    '-0.9719076166'
...
"""
# After:
"""
...
    >>> calc.qalculate("correlation([1,2,3,4,5,6,7,8,9,10]; [2,4,5,4,5,7,8,9,10,12])")
    '0.9719076166'
...
"""
```

**Why**: The data X=[1..10], Y=[2,4,5,4,5,7,8,9,10,12] shows both variables increasing together. The correlation coefficient is positive (+0.97), not negative. The docstring had a spurious `-` sign. pyqalculate's output is correct.

**Verification**:
```python
from pyqalculate import Calculator
calc = Calculator()
result = calc.qalculate("correlation([1,2,3,4,5,6,7,8,9,10]; [2,4,5,4,5,7,8,9,10,12])")
assert result == '0.9719076166'
```

**Risk**: None. Docstring-only change. No code behavior affected.

---

### Task 2: Fix interval arithmetic in Number operators [LOW-MEDIUM — 1-2 hours]

**What**: Add `is_plusminus()` guards to all 5 arithmetic operators so the variance formula only applies to `±` intervals. For `interval()` inputs, the existing dead-code paths will execute proper endpoint evaluation.

**File to modify**:
- `pyqalculate/number.py`

**Lines to modify** (5 operators):
1. `__add__` — line ~955
2. `__sub__` — line ~1006
3. `__mul__` — line ~1056
4. `__truediv__` — line ~1118
5. `__pow__` — line ~1191

**The fix pattern** — for each operator, change the condition from:

```python
# BEFORE:
if self.is_interval() or other.is_interval():
    # variance/derivative formula (linear approximation)
    ...
```

to:

```python
# AFTER:
if (self.is_interval() or other.is_interval()) and (self.is_plusminus() or other.is_plusminus()):
    # variance/derivative formula (linear approximation for ± intervals only)
    ...
```

**Why this works**:

- `is_plusminus()` returns `True` only for `±` intervals (uncertainty propagation: `1.5 ± 0.05`)
- `is_interval()` returns `True` for both `±` intervals AND `interval()` inputs
- The old condition triggered variance formula for BOTH types
- The new condition restricts variance formula to `±` intervals only
- For `interval()` inputs, the existing code path after the `if` block executes proper endpoint evaluation (evaluating the function at both interval endpoints)

**Example — `interval(-3; 7)^3`**:

With the fix:
1. `self` is `interval(-3; 7)` — `is_interval()` = True, `is_plusminus()` = False
2. The condition `(is_interval() or is_interval()) and (is_plusminus() or is_plusminus())` = `True and False` = `False`
3. Variance formula is skipped
4. Falls through to existing endpoint evaluation code
5. Evaluates `(-3)^3 = -27` and `7^3 = 343`
6. Returns `interval(-27, 343)` ✓

**Example — `(1.5 ± 0.05)^2`**:

With the fix:
1. `self` is `1.5 ± 0.05` — `is_interval()` = True, `is_plusminus()` = True
2. The condition = `True and True` = `True`
3. Variance formula fires (correct for uncertainty propagation)
4. Returns `2.25 ± 0.15` ✓

**Verification**:
```python
from pyqalculate import Calculator
calc = Calculator()

# Issue 2: interval arithmetic
result = calc.qalculate("interval(-3; 7)^3")
assert "interval(-27, 343)" in result  # or equivalent format

# Verify ± intervals still work
result = calc.qalculate("(1.5+/-0.05)^2")
assert "+/-" in result  # uncertainty propagation still active

# Regression: all existing tests
# pytest tests/ -v --tb=short
```

**Risk**: Low. The change is a single condition added to 5 operators. The existing code paths are already implemented and just need to be reached. The `is_plusminus()` method is well-defined and tested.

---

## 4. Test Strategy

### 4.1 Per-Task Verification

| Task | Verification Method | Pass Criteria |
|------|-------------------|---------------|
| Task 1: docstring | Read docstring, confirm sign | `0.9719076166` (positive) |
| Task 2: interval arithmetic | `interval(-3; 7)^3` | `interval(-27, 343)` |

### 4.2 Regression Testing

After Task 2, run the full test suite:

```bash
pytest tests/ -v --tb=short
```

Expected: All 971 unit tests pass, all 79 reference tests pass. No regressions.

### 4.3 Key Regression Checks

Verify these still work after the interval arithmetic fix:

1. **`±` intervals**: `(1.5+/-0.05) * 2` should use variance formula
2. **`interval()` arithmetic**: `interval(-3; 7)^3` should use endpoint evaluation
3. **Mixed expressions**: `interval(1; 3) + (2+/-0.1)` — verify correct behavior
4. **Existing reference tests**: Run `pytest tests/test_qalculate_reference.py -v`

### 4.4 Tolerance Guidelines

| Result Type | Tolerance | Example |
|-------------|-----------|---------|
| Interval endpoints | Exact integer when possible | `interval(-27, 343)` |
| Uncertainty values | ±0.001 relative | `2.457±0.041` |
| Correlation coefficient | Exact match | `0.9719076166` |

---

## 5. Risk Assessment

### 5.1 Task 1: Docstring Fix

| Aspect | Assessment |
|--------|------------|
| Risk | None |
| Blast radius | None (docstring only) |
| Regression potential | Zero |
| Mitigation | Not needed |

### 5.2 Task 2: Interval Arithmetic

| Aspect | Assessment |
|--------|------------|
| Risk | Low |
| Blast radius | 5 operators in `number.py` |
| Regression potential | Low (condition is stricter, not looser) |
| Mitigation | Run full test suite; verify ± intervals still work |

**Why risk is low**:
1. The change makes the condition MORE restrictive (adds `and is_plusminus()`), so fewer cases trigger the variance formula
2. The existing endpoint evaluation code is already written and tested (it was dead code, not untested code)
3. The `is_plusminus()` method is well-defined and has clear semantics
4. If any existing test used `±` intervals, it would still pass because `is_plusminus()` returns True for those

### 5.3 Worst-Case Scenarios

**Scenario A**: Some `±` interval test breaks because `is_plusminus()` doesn't recognize its format.
- **Impact**: Existing uncertainty arithmetic tests could fail.
- **Mitigation**: `is_plusminus()` is already used elsewhere in the codebase and is well-tested. Verify with `(1.5+/-0.05)^2` before proceeding.

**Scenario B**: The endpoint evaluation code path has a latent bug.
- **Impact**: `interval()` arithmetic could give wrong results.
- **Mitigation**: The endpoint evaluation code is straightforward (evaluate at both endpoints, take min/max). Visual inspection confirms correctness. The specific case `interval(-3; 7)^3` is a clean verification.

---

## 6. Execution Order

### 6.1 Recommended Order

**Step 1 — Docstring fix** (Task 1):
- Trivial change, zero risk
- Do first to get it out of the way

**Step 2 — Interval arithmetic fix** (Task 2):
- Modify 5 operators in `number.py`
- Each operator follows the same pattern
- Run regression tests after all 5 changes

### 6.2 Parallel Execution

Tasks 1 and 2 are independent and can be done in parallel if desired. Task 1 touches only test files; Task 2 touches only `number.py`.

---

## 7. Deliverables

### 7.1 Modified Files

| File | Task | Changes |
|------|------|---------|
| `tests/test_integration.py` | 1 | Correct correlation docstring sign (line 969) |
| `pyqalculate/number.py` | 2 | Add `is_plusminus()` guards to 5 arithmetic operators |

### 7.2 No New Files

All fixes are within existing files. No new modules, no new dependencies.

### 7.3 Expected Outcome

| Metric | Before v2.1.1 | After v2.1.1 |
|--------|---------------|--------------|
| Reference tests passing | 79/79 (100%) | 79/79 (100%) |
| Unit tests passing | 971 | 971 (no regressions) |
| `interval(-3; 7)^3` | `interval(-52, 68)` (wrong) | `interval(-27, 343)` (correct) |
| Correlation docstring | `-0.9719076166` (wrong sign) | `0.9719076166` (correct) |

---

## 8. Appendix: Technical Detail — Why Variance Formula Is Wrong for `interval()` Inputs

### 8.1 The Two Interval Semantics

pyqalculate handles two distinct types of intervals:

1. **`±` intervals (plusminus)**: Represent uncertainty. `1.5 ± 0.05` means the true value is somewhere in `[1.45, 1.55]`. The variance/derivative formula propagates uncertainty through operations. This is a LINEAR APPROXIMATION and is appropriate for small uncertainties.

2. **`interval()` inputs**: Represent exact ranges. `interval(-3; 7)` means the value could be anywhere from -3 to 7. True interval arithmetic evaluates the function at both endpoints and takes the min/max. This gives the EXACT range of the function over the interval.

### 8.2 Why the Variance Formula Fails

For `f(x) = x^3` over `interval(-3; 7)`:

**Variance formula** (current behavior):
- mid = (-3 + 7) / 2 = 2
- half_width = (7 - (-3)) / 2 = 5
- f(mid) = 2^3 = 8
- f'(mid) = 3 * 2^2 = 12
- result = 8 ± 12 * 5 = 8 ± 60 = [-52, 68]

**True interval arithmetic** (correct behavior):
- f(-3) = (-3)^3 = -27
- f(7) = 7^3 = 343
- result = interval(-27, 343)

The variance formula is wrong because x^3 is highly nonlinear over [-3, 7]. The linear approximation only works for small intervals where the function is approximately linear.

### 8.3 Why `is_plusminus()` Is the Right Guard

The `is_plusminus()` method distinguishes the two cases:
- `1.5+/-0.05` → `is_plusminus()` = True, `is_interval()` = True
- `interval(-3; 7)` → `is_plusminus()` = False, `is_interval()` = True

By adding `is_plusminus()` to the condition, we ensure:
- `±` intervals use variance formula (correct for small uncertainties)
- `interval()` inputs use endpoint evaluation (correct for exact ranges)

---

*Document created for PyQalculate v2.1.1 development. Execute tasks in order. Run full regression suite after Task 2.*
