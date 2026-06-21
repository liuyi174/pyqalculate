"""Mathematical expression renderer using matplotlib.

Converts calculator output strings to properly rendered mathematical
notation using matplotlib's mathtext engine. Supports fractions,
superscripts, subscripts, radicals, Greek letters, and more.
"""

from __future__ import annotations

import re
from typing import Any, Final, Optional

import matplotlib
matplotlib.use("Agg")
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from PIL import Image, ImageTk

# Unicode superscript and subscript digit mappings
_SUPERSCRIPTS: Final = "⁰¹²³⁴⁵⁶⁷⁸⁹"
_SUBSCRIPTS: Final = "₀₁₂₃₄₅₆₇₈₉"

# Operator replacements: Unicode → mathtext command
_OPERATOR_MAP: Final[dict[str, str]] = {
    "×": r"\times ",
    "÷": r"\div ",
    "·": r"\cdot ",
    "π": r"\pi ",
    "∞": r"\infty ",
    "±": r"\pm ",
    "≤": r"\leq ",
    "≥": r"\geq ",
    "≠": r"\neq ",
    "≈": r"\approx ",
}


class MathRenderer:
    """Renders mathematical expressions as images using matplotlib.

    Uses matplotlib's mathtext engine to typeset expressions with proper
    mathematical notation (fractions, radicals, superscripts, etc.).
    Caches rendered images keyed by (text, font_size, color).
    """

    def __init__(self, dpi: int = 100) -> None:
        self._dpi = dpi
        self._cache: dict[str, ImageTk.PhotoImage] = {}

    def _convert_to_mathtext(self, text: str) -> str:
        """Convert calculator output to matplotlib mathtext format.

        Handles Unicode math symbols, superscript/subscript digits,
        and simple square root notation.
        """
        for old, new in _OPERATOR_MAP.items():
            text = text.replace(old, new)

        for i, ch in enumerate(_SUPERSCRIPTS):
            text = text.replace(ch, f"^{{{i}}}")

        for i, ch in enumerate(_SUBSCRIPTS):
            text = text.replace(ch, f"_{{{i}}}")

        # √2 → \sqrt{2}, √(x+1) → \sqrt{x+1}
        text = re.sub(r"√(\d+)", r"\\sqrt{\1}", text)
        text = re.sub(r"√\(([^)]+)\)", r"\\sqrt{\1}", text)

        return text

    def render(
        self,
        text: str,
        font_size: int = 14,
        color: str = "black",
        master: Any | None = None,
    ) -> Optional[ImageTk.PhotoImage]:
        """Render a mathematical expression as a tkinter-compatible image.

        Args:
            text: Expression string to render.
            font_size: Font size in points.
            color: Text color.
            master: Tk widget to associate the image with (ensures correct
                interpreter in test environments with multiple Tk roots).

        Returns None if rendering fails (caller should fall back to plain text).
        """
        cache_key = f"{text}_{font_size}_{color}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            mathtext = self._convert_to_mathtext(text)
            photo = self._to_photo(f"${mathtext}$", font_size, color, master)
            if photo is not None:
                self._cache[cache_key] = photo
            return photo
        except Exception:  # noqa: BLE001 — graceful fallback for any mathtext error
            return None

    def render_plain(
        self,
        text: str,
        font_size: int = 14,
        color: str = "black",
        master: Any | None = None,
    ) -> Optional[ImageTk.PhotoImage]:
        """Render plain text as an image (fallback when mathtext fails)."""
        try:
            return self._to_photo(text, font_size, color, master)
        except Exception:  # noqa: BLE001
            return None

    def _to_photo(
        self, display_text: str, font_size: int, color: str, master: Any | None
    ) -> Optional[ImageTk.PhotoImage]:
        """Render display_text to an ImageTk.PhotoImage with tight sizing."""
        fig = Figure(dpi=self._dpi)
        fig.patch.set_alpha(0)

        text_obj = fig.text(
            0.0, 0.5, display_text,
            fontsize=font_size, color=color,
            ha="left", va="center",
        )

        # First pass: measure bounding box
        canvas = FigureCanvasAgg(fig)
        canvas.draw()
        bbox = text_obj.get_window_extent(canvas.get_renderer())

        # Resize figure to tightly fit text
        w_inch = bbox.width / self._dpi + 0.1
        h_inch = bbox.height / self._dpi + 0.2
        fig.set_size_inches(w_inch, h_inch)

        # Second pass: render at final size
        canvas = FigureCanvasAgg(fig)
        canvas.draw()

        # Copy buffer to own the pixel data before clearing the figure
        buf = canvas.buffer_rgba()
        image = Image.frombytes("RGBA", canvas.get_width_height(), bytes(buf))
        photo = ImageTk.PhotoImage(image, master=master)

        fig.clear()
        return photo

    def clear_cache(self) -> None:
        """Clear the image cache."""
        self._cache.clear()
