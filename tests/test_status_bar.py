"""Tests for StatusBar widget."""

from __future__ import annotations

import tkinter as tk

from pyqalculate_gui.event_bus import MODE_CHANGED, EventBus
from pyqalculate_gui.status_bar import StatusBar
from pyqalculate_gui.theme import DARK, LIGHT

# Single module-level root avoids Tcl flake from rapid Tk() creation/teardown.
_root: tk.Tk | None = None


def _get_root() -> tk.Tk:
    global _root
    if _root is None:
        _root = tk.Tk()
        _root.withdraw()
    return _root


def _bar(**kwargs: object) -> StatusBar:
    """Create a StatusBar inside the shared root."""
    return StatusBar(_get_root(), **kwargs)  # type: ignore[arg-type]


def teardown_module() -> None:
    global _root
    if _root is not None:
        _root.destroy()
        _root = None


# --- Constructor ---


class TestConstructor:
    def test_default_theme(self) -> None:
        bar = _bar()
        assert bar._theme is LIGHT
        assert bar._event_bus is None

    def test_custom_theme(self) -> None:
        bar = _bar(theme=DARK)
        assert bar._theme is DARK

    def test_event_bus_subscribes_to_mode_changed(self) -> None:
        bus = EventBus()
        bar = _bar(event_bus=bus)
        assert MODE_CHANGED in bus._subscribers

    def test_no_event_bus(self) -> None:
        bar = _bar(event_bus=None)
        assert bar._event_bus is None


# --- update_stats ---


class TestUpdateStats:
    def test_default_stats(self) -> None:
        bar = _bar()
        assert bar._stats_var.get() == "Functions: 0 | Units: 0 | Variables: 0"

    def test_update_stats(self) -> None:
        bar = _bar()
        bar.update_stats(5, 12, 3)
        assert bar._stats_var.get() == "Functions: 5 | Units: 12 | Variables: 3"

    def test_update_stats_zeroes(self) -> None:
        bar = _bar()
        bar.update_stats(0, 0, 0)
        assert bar._stats_var.get() == "Functions: 0 | Units: 0 | Variables: 0"


# --- set_mode ---


class TestSetMode:
    def test_default_mode(self) -> None:
        bar = _bar()
        assert bar._mode_var.get() == "Approximate"

    def test_set_exact(self) -> None:
        bar = _bar()
        bar.set_mode(True)
        assert bar._mode_var.get() == "Exact"

    def test_set_approximate(self) -> None:
        bar = _bar()
        bar.set_mode(True)
        bar.set_mode(False)
        assert bar._mode_var.get() == "Approximate"


# --- EventBus integration ---


class TestEventBusModeChanged:
    def test_mode_changed_exact(self) -> None:
        bus = EventBus()
        bar = _bar(event_bus=bus)
        bus.emit(MODE_CHANGED, True)
        assert bar._mode_var.get() == "Exact"

    def test_mode_changed_approximate(self) -> None:
        bus = EventBus()
        bar = _bar(event_bus=bus)
        bus.emit(MODE_CHANGED, False)
        assert bar._mode_var.get() == "Approximate"

    def test_mode_changed_toggles(self) -> None:
        bus = EventBus()
        bar = _bar(event_bus=bus)
        bus.emit(MODE_CHANGED, True)
        bus.emit(MODE_CHANGED, False)
        bus.emit(MODE_CHANGED, True)
        assert bar._mode_var.get() == "Exact"
