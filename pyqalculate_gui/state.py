"""Centralized state management for the pyqalculate GUI.

All mutable GUI state lives in one AppState instance. Components subscribe
as observers to reactively update when fields change.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


class StateObserver(Protocol):
    """Interface for objects that observe state changes."""

    def on_state_changed(self, field: str, value: Any) -> None: ...


@dataclass
class AppState:
    """Single source of truth for all GUI state."""

    expression: str = ""
    result: str = ""
    exact_mode: bool = True
    history_entries: list[str] = field(default_factory=list)
    show_keypad: bool = True
    show_history: bool = True
    show_conversion: bool = False
    status_text: str = ""

    _observers: list[StateObserver] = field(default_factory=list, repr=False)

    def add_observer(self, observer: StateObserver) -> None:
        """Register an observer for state change notifications."""
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: StateObserver) -> None:
        """Unregister a previously registered observer."""
        try:
            self._observers.remove(observer)
        except ValueError:
            pass

    def notify(self, field: str, value: Any) -> None:
        """Notify all observers of a field change."""
        for observer in self._observers:
            observer.on_state_changed(field, value)

    def update(self, **kwargs: Any) -> None:
        """Update one or more fields and notify observers of each change."""
        for name, value in kwargs.items():
            if hasattr(self, name):
                setattr(self, name, value)
                self.notify(name, value)
