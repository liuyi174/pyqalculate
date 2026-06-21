"""Engine wrapper for pyqalculate Calculator.

Provides a clean, error-safe public API over the raw Calculator engine
for use by the GUI layer.
"""

from __future__ import annotations

from dataclasses import dataclass

from pyqalculate.calculator import Calculator
from pyqalculate.types import EvaluationOptions, PrintOptions


@dataclass(frozen=True, slots=True)
class CalculationResult:
    """Result of a calculator expression evaluation."""

    expression: str
    result: str
    exact: bool
    error: str | None


class CalculatorService:
    """Thin wrapper around pyqalculate.Calculator with typed error handling."""

    def __init__(self) -> None:
        self._calc = Calculator()
        self._calc.load_definitions()
        self._calc.load_global_definitions()

    def calculate(
        self,
        expression: str,
        eo: EvaluationOptions | None = None,
        po: PrintOptions | None = None,
    ) -> CalculationResult:
        """Evaluate *expression* and return a typed result."""
        if eo is None:
            eo = EvaluationOptions()
        if po is None:
            po = PrintOptions()

        try:
            result = self._calc.calculate_and_print(expression, 0, eo, po)
            return CalculationResult(
                expression=expression,
                result=result,
                exact=not eo.approximation,
                error=None,
            )
        except Exception as exc:
            return CalculationResult(
                expression=expression,
                result="",
                exact=False,
                error=str(exc),
            )

    def convert(self, value: str, from_unit: str, to_unit: str) -> str:
        """Convert *value* between units and return the formatted string."""
        result = self.calculate(f"{value} {from_unit} to {to_unit}")
        return result.result

    def get_units(self) -> list[str]:
        """Return sorted list of available unit names."""
        return sorted(self._calc._units.keys())

    def get_functions(self) -> list[str]:
        """Return sorted list of available function names."""
        return sorted(self._calc._functions.keys())

    def get_variables(self) -> list[str]:
        """Return sorted list of available variable names."""
        return sorted(self._calc._variables.keys())

    def get_unit_categories(self) -> dict[str, list[str]]:
        """Return mapping of category name → list of unit keys.

        Category names have the ``!units!`` prefix stripped and are
        normalized to display-friendly form (e.g. ``Length``,
        ``Electricity/Capacitance``).
        """
        categories: dict[str, list[str]] = {}
        for key, unit in self._calc._units.items():
            raw_cat = unit.category()
            if not raw_cat:
                raw_cat = "General"
            # Strip the internal !units! prefix
            cat = raw_cat
            if cat.startswith("!units!"):
                cat = cat[len("!units!"):]
            categories.setdefault(cat, []).append(key)
        return categories

    def get_unit_display_name(self, key: str) -> str:
        """Return a human-friendly display name for a unit key.

        Format: ``"name (abbreviation)"`` when they differ, else just
        the name.
        """
        unit = self._calc.get_unit(key)
        if unit is None:
            return key
        name = unit.name()
        abbrev = unit.abbreviation()
        if abbrev and abbrev != name:
            return f"{name} ({abbrev})"
        return name
