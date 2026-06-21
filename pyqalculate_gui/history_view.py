"""History view widget for browsing past calculations.

Provides a scrollable list of past calculations with:
- Click to recall expression
- answer(N) support for referencing past results
- Visual distinction between expressions, results, errors
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass, field
from typing import Callable


# ---------------------------------------------------------------------------
# History entry types
# ---------------------------------------------------------------------------

class HistoryType:
    """Types of history entries."""
    EXPRESSION = "expression"
    RESULT = "result"
    RESULT_APPROX = "result_approx"
    ERROR = "error"
    INFO = "info"


@dataclass
class HistoryEntry:
    """A single history entry."""
    entry_type: str
    text: str
    expression_number: int = 0  # 1-based, for answer(N)


class HistoryView(ttk.Frame):
    """Scrollable history of past calculations.

    Signals:
        on_recall(expression: str) - fired when user clicks an expression
    """

    _MAX_ENTRIES = 300

    def __init__(
        self,
        parent: tk.Misc,
        on_recall: Callable[[str], None] | None = None,
    ) -> None:
        super().__init__(parent)
        self._on_recall = on_recall
        self._entries: list[HistoryEntry] = []
        self._expression_counter: int = 0  # counts calculation groups
        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        """Build the history view layout."""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Header
        header = ttk.Frame(self)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 2))

        ttk.Label(header, text="History", font=("TkDefaultFont", 10, "bold")).pack(
            side=tk.LEFT
        )

        self._count_var = tk.StringVar(value="")
        ttk.Label(header, textvariable=self._count_var, foreground="#888").pack(
            side=tk.RIGHT
        )

        # Listbox with scrollbar
        list_frame = ttk.Frame(self)
        list_frame.grid(row=1, column=0, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._listbox = tk.Listbox(
            list_frame,
            font=("Consolas", 10),
            activestyle="underline",
            selectmode=tk.SINGLE,
            exportselection=False,
            relief=tk.FLAT,
            highlightthickness=0,
        )
        self._listbox.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(
            list_frame, orient=tk.VERTICAL, command=self._listbox.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self._listbox.config(yscrollcommand=scrollbar.set)

        # Configure listbox item colors
        self._listbox.configure(
            selectbackground="#3498db",
            selectforeground="white",
        )

        # Click to recall
        self._listbox.bind("<Double-Button-1>", self._on_item_double_click)

        # Action buttons
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=2, column=0, sticky="ew", pady=(4, 0))

        ttk.Button(
            btn_frame, text="Insert answer(N)", command=self._insert_answer
        ).pack(side=tk.LEFT)

        ttk.Button(
            btn_frame, text="Clear", command=self.clear
        ).pack(side=tk.RIGHT)

    # ------------------------------------------------------------------
    # History management
    # ------------------------------------------------------------------

    def add_expression(self, expression: str) -> None:
        """Record a new expression (before calculation).

        Args:
            expression: The expression text.
        """
        self._expression_counter += 1
        entry = HistoryEntry(
            entry_type=HistoryType.EXPRESSION,
            text=expression,
            expression_number=self._expression_counter,
        )
        self._add_entry(entry)

    def add_result(self, result: str, *, exact: bool = True) -> None:
        """Record a calculation result.

        Args:
            result: The formatted result string.
            exact: Whether the result is exact.
        """
        entry = HistoryEntry(
            entry_type=HistoryType.RESULT if exact else HistoryType.RESULT_APPROX,
            text=result,
            expression_number=self._expression_counter,
        )
        self._add_entry(entry)

    def add_error(self, error: str) -> None:
        """Record an error message.

        Args:
            error: The error text.
        """
        entry = HistoryEntry(
            entry_type=HistoryType.ERROR,
            text=error,
            expression_number=self._expression_counter,
        )
        self._add_entry(entry)

    def add_info(self, message: str) -> None:
        """Record an informational message.

        Args:
            message: The info text.
        """
        entry = HistoryEntry(
            entry_type=HistoryType.INFO,
            text=message,
            expression_number=0,
        )
        self._add_entry(entry)

    def _add_entry(self, entry: HistoryEntry) -> None:
        """Add an entry to the history and update display."""
        self._entries.append(entry)

        # Trim old entries
        if len(self._entries) > self._MAX_ENTRIES:
            self._entries = self._entries[-self._MAX_ENTRIES:]

        # Format display line
        if entry.entry_type == HistoryType.EXPRESSION:
            prefix = f"[{entry.expression_number}] >"
            display = f"{prefix} {entry.text}"
        elif entry.entry_type in (HistoryType.RESULT, HistoryType.RESULT_APPROX):
            prefix = f"[{entry.expression_number}] "
            display = f"{prefix}  = {entry.text}"
        elif entry.entry_type == HistoryType.ERROR:
            prefix = f"[{entry.expression_number}] "
            display = f"{prefix}  ! {entry.text}"
        else:
            display = f"   {entry.text}"

        self._listbox.insert(tk.END, display)

        # Color-code by type
        idx = self._listbox.size() - 1
        if entry.entry_type == HistoryType.EXPRESSION:
            self._listbox.itemconfigure(idx, fg="#1a5276")
        elif entry.entry_type == HistoryType.RESULT:
            self._listbox.itemconfigure(idx, fg="#1e8449")
        elif entry.entry_type == HistoryType.RESULT_APPROX:
            self._listbox.itemconfigure(idx, fg="#7d6608")
        elif entry.entry_type == HistoryType.ERROR:
            self._listbox.itemconfigure(idx, fg="#c0392b")
        else:
            self._listbox.itemconfigure(idx, fg="#7f8c8d")

        # Auto-scroll to bottom
        self._listbox.see(tk.END)

        # Update count
        n_expr = sum(
            1 for e in self._entries if e.entry_type == HistoryType.EXPRESSION
        )
        self._count_var.set(f"{n_expr} calculations")

    # ------------------------------------------------------------------
    # Interaction
    # ------------------------------------------------------------------

    def _on_item_double_click(self, event: tk.Event) -> None:
        """Recall the expression from a double-clicked history entry."""
        sel = self._listbox.curselection()
        if not sel:
            return

        idx = sel[0]
        if idx >= len(self._entries):
            return

        entry = self._entries[idx]

        # If clicking on a result, find the corresponding expression
        if entry.entry_type in (
            HistoryType.RESULT,
            HistoryType.RESULT_APPROX,
            HistoryType.ERROR,
        ):
            # Look backwards for the matching expression
            for i in range(idx - 1, -1, -1):
                if (
                    self._entries[i].entry_type == HistoryType.EXPRESSION
                    and self._entries[i].expression_number == entry.expression_number
                ):
                    entry = self._entries[i]
                    break

        if entry.entry_type == HistoryType.EXPRESSION and self._on_recall:
            self._on_recall(entry.text)

    def _insert_answer(self) -> None:
        """Insert answer(N) for the most recent expression."""
        if self._expression_counter > 0 and self._on_recall:
            self._on_recall(f"answer({self._expression_counter})")

    # ------------------------------------------------------------------
    # answer(N) support
    # ------------------------------------------------------------------

    def get_answer(self, index: int) -> str | None:
        """Return the result text for a given expression number.

        Args:
            index: 1-based expression number. Negative counts from end.

        Returns:
            The result string, or None if not found.
        """
        if index == 0:
            return None

        if index > 0:
            # Find by expression_number
            for entry in reversed(self._entries):
                if (
                    entry.entry_type
                    in (HistoryType.RESULT, HistoryType.RESULT_APPROX)
                    and entry.expression_number == index
                ):
                    return entry.text
        else:
            # Negative index: count from end
            results = [
                e
                for e in self._entries
                if e.entry_type in (HistoryType.RESULT, HistoryType.RESULT_APPROX)
            ]
            abs_idx = abs(index)
            if abs_idx <= len(results):
                return results[-abs_idx].text

        return None

    def get_expression_text(self, index: int) -> str | None:
        """Return the expression text for a given expression number.

        Args:
            index: 1-based expression number.

        Returns:
            The expression string, or None if not found.
        """
        for entry in self._entries:
            if (
                entry.entry_type == HistoryType.EXPRESSION
                and entry.expression_number == index
            ):
                return entry.text
        return None

    @property
    def last_expression_number(self) -> int:
        """Return the most recent expression number."""
        return self._expression_counter

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def clear(self) -> None:
        """Clear all history entries."""
        self._entries.clear()
        self._listbox.delete(0, tk.END)
        self._expression_counter = 0
        self._count_var.set("")
