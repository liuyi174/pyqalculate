"""PyQalculate Demo - subprocess-based command runner.

Reads commands from scripts/demo_commands.txt, executes each via the
pyqalc CLI, and writes consolidated output to scripts/demo_output/.

Plot commands (plot, plot_parametric, plot_implicit) are handled via
the Plotter API since pyqalc does not expose them on the CLI.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import TextIO

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_DIR = _SCRIPT_DIR.parent
_COMMANDS_FILE = _SCRIPT_DIR / "demo_commands.txt"
_OUTPUT_DIR = _SCRIPT_DIR / "demo_output"
_PLOT_DIR = _OUTPUT_DIR / "plots"
_RESULTS_FILE = _OUTPUT_DIR / "demo_results.txt"

# Resolve pyqalc executable inside the venv
_VENV_BIN = _PROJECT_DIR / ".venv" / ("Scripts" if os.name == "nt" else "bin")
_PYQALC = _VENV_BIN / ("pyqalc.exe" if os.name == "nt" else "pyqalc")


# ---------------------------------------------------------------------------
# Plot command parsing
# ---------------------------------------------------------------------------

# plot(expr, filename.png)
_RE_PLOT = re.compile(r"^plot\((.+),\s*(\S+\.png)\)$")

# plot_parametric(x_expr, y_expr, filename.png)
_RE_PARAMETRIC = re.compile(
    r"^plot_parametric\((.+?),\s*(.+?),\s*(\S+\.png)\)$"
)

# plot_implicit(expr, filename.png)
_RE_IMPLICIT = re.compile(r"^plot_implicit\((.+?),\s*(\S+\.png)\)$")


def _run_plot(expr: str, filename: str, out: TextIO) -> None:
    """Plot a standard y=f(x) expression."""
    from pyqalculate.plot import Plotter

    path = str(_PLOT_DIR / filename)
    plotter = Plotter()
    result = plotter.plot(expr, filename=path)
    size = os.path.getsize(result) if result and os.path.exists(result) else 0
    out.write(f"  -> saved {filename} ({size} bytes)\n")
    print(f"  [PLOT] {filename} ({size} bytes)")


def _run_parametric(x_expr: str, y_expr: str, filename: str, out: TextIO) -> None:
    """Plot a parametric curve x(t), y(t)."""
    from pyqalculate.plot import Plotter

    path = str(_PLOT_DIR / filename)
    plotter = Plotter()
    result = plotter.plot_parametric(x_expr, y_expr, filename=path)
    size = os.path.getsize(result) if result and os.path.exists(result) else 0
    out.write(f"  -> saved {filename} ({size} bytes)\n")
    print(f"  [PARAMETRIC] {filename} ({size} bytes)")


def _run_implicit(expr: str, filename: str, out: TextIO) -> None:
    """Plot an implicit equation f(x,y) = 0."""
    from pyqalculate.plot import Plotter

    path = str(_PLOT_DIR / filename)
    plotter = Plotter()
    result = plotter.plot_implicit(expr, filename=path)
    size = os.path.getsize(result) if result and os.path.exists(result) else 0
    out.write(f"  -> saved {filename} ({size} bytes)\n")
    print(f"  [IMPLICIT] {filename} ({size} bytes)")


# ---------------------------------------------------------------------------
# CLI subprocess execution
# ---------------------------------------------------------------------------


def _run_cli(expression: str, out: TextIO) -> None:
    """Execute a single expression via the pyqalc CLI subprocess."""
    cmd = [str(_PYQALC), "-t", expression]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(_PROJECT_DIR),
        )
        output = result.stdout.strip()
        if output:
            out.write(f"  {output}\n")
            print(f"  {output}")
        if result.returncode != 0 and result.stderr.strip():
            err = result.stderr.strip()
            out.write(f"  [stderr] {err}\n")
            print(f"  [ERR] {err}")
    except subprocess.TimeoutExpired:
        out.write("  [TIMEOUT after 30s]\n")
        print("  [TIMEOUT]")
    except FileNotFoundError:
        out.write(f"  [ERROR] pyqalc not found at {_PYQALC}\n")
        print(f"  [ERROR] pyqalc not found at {_PYQALC}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    # Ensure output directories exist
    _OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    _PLOT_DIR.mkdir(parents=True, exist_ok=True)

    # Read commands
    if not _COMMANDS_FILE.exists():
        print(f"Error: commands file not found: {_COMMANDS_FILE}")
        sys.exit(1)

    lines = _COMMANDS_FILE.read_text(encoding="utf-8").splitlines()

    total = 0
    plots = 0
    errors = 0

    with open(_RESULTS_FILE, "w", encoding="utf-8") as out:
        out.write("PyQalculate Demo Results\n")
        out.write("=" * 60 + "\n\n")

        for raw_line in lines:
            line = raw_line.strip()

            # Skip empty lines and comments
            if not line or line.startswith("#"):
                # Echo section headers
                if line.startswith("# =="):
                    out.write(f"\n{line}\n")
                    print(f"\n{line}")
                elif line.startswith("#"):
                    out.write(f"{line}\n")
                    print(line)
                continue

            total += 1
            out.write(f"\n>> {line}\n")
            print(f"\n>> {line}")

            # --- plot(expr, file.png) ---
            m = _RE_PLOT.match(line)
            if m:
                try:
                    _run_plot(m.group(1), m.group(2), out)
                    plots += 1
                except Exception as e:
                    out.write(f"  [PLOT ERROR] {e}\n")
                    print(f"  [PLOT ERROR] {e}")
                    errors += 1
                continue

            # --- plot_parametric(x_expr, y_expr, file.png) ---
            m = _RE_PARAMETRIC.match(line)
            if m:
                try:
                    _run_parametric(m.group(1), m.group(2), m.group(3), out)
                    plots += 1
                except Exception as e:
                    out.write(f"  [PARAMETRIC ERROR] {e}\n")
                    print(f"  [PARAMETRIC ERROR] {e}")
                    errors += 1
                continue

            # --- plot_implicit(expr, file.png) ---
            m = _RE_IMPLICIT.match(line)
            if m:
                try:
                    _run_implicit(m.group(1), m.group(2), out)
                    plots += 1
                except Exception as e:
                    out.write(f"  [IMPLICIT ERROR] {e}\n")
                    print(f"  [IMPLICIT ERROR] {e}")
                    errors += 1
                continue

            # --- Regular calculator command via CLI subprocess ---
            _run_cli(line, out)

        out.write(f"\n{'=' * 60}\n")
        out.write(f"Total commands: {total}\n")
        out.write(f"Plots generated: {plots}\n")
        out.write(f"Errors: {errors}\n")

    print(f"\n{'=' * 60}")
    print(f"Done! {total} commands, {plots} plots, {errors} errors")
    print(f"Results: {_RESULTS_FILE}")
    print(f"Plots:   {_PLOT_DIR}")


if __name__ == "__main__":
    main()
