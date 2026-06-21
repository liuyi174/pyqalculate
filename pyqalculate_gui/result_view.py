"""Result display widget with formatting and copy support.

Shows calculation results with expression echo, exact/approximate
indication, and clipboard integration.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable


class ResultView(ttk.Frame):
    """Display area for calculation results.

    Shows expression echo and result with formatting. Supports copy-to-
    clipboard and clear operations.
    """

    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent)
        self._last_result: str = ""
        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        """Build the result display layout."""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Scrollable text area
        text_frame = ttk.Frame(self)
        text_frame.grid(row=0, column=0, sticky="nsew")
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        self._text = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=("Consolas", 11),
            state=tk.DISABLED,
            bg="#fafafa",
            relief=tk.FLAT,
            padx=10,
            pady=6,
            spacing1=2,
            spacing3=2,
        )
        self._text.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(
            text_frame, orient=tk.VERTICAL, command=self._text.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self._text.config(yscrollcommand=scrollbar.set)

        # Configure text tags
        self._text.tag_configure(
            "expression", foreground="#1a5276", font=("Consolas", 11, "bold")
        )
        self._text.tag_configure(
            "result", foreground="#1e8449", font=("Consolas", 12, "bold")
        )
        self._text.tag_configure(
            "result_approx", foreground="#7d6608", font=("Consolas", 11, "italic")
        )
        self._text.tag_configure(
            "error", foreground="#c0392b", font=("Consolas", 11)
        )
        self._text.tag_configure(
            "separator", foreground="#d5d8dc"
        )
        self._text.tag_configure(
            "info", foreground="#7f8c8d", font=("Consolas", 10, "italic")
        )

        # Action buttons
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=1, column=0, sticky="ew", pady=(4, 0))

        self._copy_btn = ttk.Button(
            btn_frame, text="Copy Result", command=self._copy_result
        )
        self._copy_btn.pack(side=tk.RIGHT)

        self._clear_btn = ttk.Button(
            btn_frame, text="Clear", command=self.clear
        )
        self._clear_btn.pack(side=tk.RIGHT, padx=(0, 6))

    # ------------------------------------------------------------------
    # Display methods
    # ------------------------------------------------------------------

    def show_result(
        self,
        expression: str,
        result: str,
        *,
        exact: bool = True,
    ) -> None:
        """Display an expression and its result.

        Args:
            expression: The input expression.
            result: The formatted result string.
            exact: Whether the result is exact (True) or approximate (False).
        """
        self._text.config(state=tk.NORMAL)

        # Separator between entries
        content = self._text.get("1.0", tk.END).strip()
        if content:
            self._text.insert(tk.END, "\n" + "\u2500" * 56 + "\n", "separator")

        # Expression echo
        self._text.insert(tk.END, f"> {expression}\n", "expression")

        # Result
        tag = "result" if exact else "result_approx"
        self._text.insert(tk.END, f"  = {result}\n", tag)

        self._text.config(state=tk.DISABLED)
        self._text.see(tk.END)

        self._last_result = result

    def show_error(self, expression: str, error: str) -> None:
        """Display an expression and its error.

        Args:
            expression: The input expression.
            error: The error message.
        """
        self._text.config(state=tk.NORMAL)

        content = self._text.get("1.0", tk.END).strip()
        if content:
            self._text.insert(tk.END, "\n" + "\u2500" * 56 + "\n", "separator")

        self._text.insert(tk.END, f"> {expression}\n", "expression")
        self._text.insert(tk.END, f"  Error: {error}\n", "error")

        self._text.config(state=tk.DISABLED)
        self._text.see(tk.END)

        self._last_result = ""

    def show_info(self, message: str) -> None:
        """Display an informational message."""
        self._text.config(state=tk.NORMAL)
        self._text.insert(tk.END, f"{message}\n", "info")
        self._text.config(state=tk.DISABLED)
        self._text.see(tk.END)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _copy_result(self) -> None:
        """Copy the last result to clipboard."""
        if self._last_result:
            self.clipboard_clear()
            self.clipboard_append(self._last_result)

    def clear(self) -> None:
        """Clear all displayed results."""
        self._text.config(state=tk.NORMAL)
        self._text.delete("1.0", tk.END)
        self._text.config(state=tk.DISABLED)
        self._last_result = ""

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    def get_last_result(self) -> str:
        """Return the last result string."""
        return self._last_result
