"""Run all expressions from qalculate_output through pyqalculate and save results."""

import os
import re
import sys
import time
from pathlib import Path
from dataclasses import dataclass, field

# Input/output directories
INPUT_DIR = Path(r"D:\1\1tmp\qalculate_output")
OUTPUT_DIR = Path(r"D:\1\1tmp\pyqalculate_output")

# File list
FILES = [
    "01_basic_operations.txt",
    "02_unit_conversions.txt",
    "03_physical_constants.txt",
    "04_uncertainty_interval.txt",
    "05_algebra_equations.txt",
    "06_calculus.txt",
    "07_matrices_vectors.txt",
    "08_statistics.txt",
    "09_time_date.txt",
    "10_number_bases.txt",
]


@dataclass
class Expression:
    """A parsed expression from the input files."""
    category: str          # e.g. "1. BASIC OPERATIONS & FUNCTIONS"
    number: str            # e.g. "1.1"
    description: str       # e.g. "Nested roots: sqrt(32) + cbrt(-27) + log2(256)"
    expression: str        # e.g. "sqrt(32) + cbrt(-27) + log2(256)"
    original_result: str   # e.g. "10.65685425"


@dataclass
class ComparisonResult:
    """Comparison between original and pyqalculate result."""
    expr: Expression
    pyqalculate_result: str
    match: bool
    error: str = ""


def parse_input_file(filepath: Path) -> list[Expression]:
    """Parse a qalculate_output file and extract expressions."""
    expressions = []
    lines = filepath.read_text(encoding="utf-8").splitlines()
    
    current_category = ""
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Match category header: === N. CATEGORY ===
        cat_match = re.match(r'^===\s*(\d+\.\s*.+?)\s*===$', line)
        if cat_match:
            current_category = cat_match.group(1)
            i += 1
            continue
        
        # Match expression entry: N.M Description: expression
        entry_match = re.match(r'^(\d+\.\d+)\s+(.+?):\s*(.+)$', line)
        if entry_match:
            number = entry_match.group(1)
            description = entry_match.group(2)
            expr_hint = entry_match.group(3)
            
            # Next line is the actual expression
            i += 1
            if i < len(lines):
                expression = lines[i].strip()
                
                # Skip blank lines and find the => result
                i += 1
                while i < len(lines) and lines[i].strip() == "":
                    i += 1
                
                original_result = ""
                if i < len(lines) and lines[i].strip().startswith("=>"):
                    original_result = lines[i].strip()[2:].strip()
                
                expressions.append(Expression(
                    category=current_category,
                    number=number,
                    description=description,
                    expression=expression,
                    original_result=original_result,
                ))
        
        i += 1
    
    return expressions


def run_pyqalculate(expression: str, calculator) -> str:
    """Run a single expression through pyqalculate and return the result string."""
    try:
        from pyqalculate.types import (
            EvaluationOptions, PrintOptions, ApproximationMode,
        )
        
        eo = EvaluationOptions()
        eo.approximation = ApproximationMode.APPROXIMATE
        eo.allow_complex = True
        eo.allow_infinite = True
        eo.calculate_functions = True
        eo.sync_units = True
        
        po = PrintOptions()
        po.approximate = True
        po.use_unicode_signs = True
        po.abbreviate_names = True
        po.use_prefixes_for_all_units = True
        
        result = calculator.calculate_and_print(expression, eo=eo, po=po)
        return result
    except Exception as e:
        return f"ERROR: {e}"


def create_output_file(filepath: Path, category: str, results: list[tuple[Expression, str]]):
    """Create an output file in the same format as the original."""
    lines = []
    lines.append(f"=== {category} ===")
    lines.append("")
    
    for expr, result in results:
        lines.append(f"{expr.number} {expr.description}: {expr.expression}")
        lines.append(expr.expression)
        lines.append(f"=> {result}")
        lines.append("")
        lines.append("")
    
    filepath.write_text("\n".join(lines), encoding="utf-8")


def compare_results(results: list[ComparisonResult]) -> dict:
    """Compare original and pyqalculate results."""
    total = len(results)
    matches = sum(1 for r in results if r.match)
    differs = sum(1 for r in results if not r.match)
    errors = sum(1 for r in results if r.error)
    
    return {
        "total": total,
        "matches": matches,
        "differs": differs,
        "errors": errors,
        "match_rate": matches / total * 100 if total > 0 else 0,
    }


def normalize_result(result: str) -> str:
    """Normalize a result string for comparison."""
    # Remove whitespace
    result = result.strip()
    # Remove trailing zeros in decimal numbers
    result = re.sub(r'(\d+)\.0+(?=\D|$)', r'\1', result)
    return result


def results_match(original: str, pyqalculate: str) -> bool:
    """Check if two results match (allowing for formatting differences)."""
    if not original or not pyqalculate:
        return False
    
    # Normalize both
    orig_norm = normalize_result(original)
    pyq_norm = normalize_result(pyqalculate)
    
    # Exact match
    if orig_norm == pyq_norm:
        return True
    
    # Try numeric comparison
    try:
        # Extract numbers from both
        orig_nums = re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', orig_norm)
        pyq_nums = re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', pyq_norm)
        
        if len(orig_nums) == len(pyq_nums):
            for o, p in zip(orig_nums, pyq_nums):
                if abs(float(o) - float(p)) > 1e-6 * max(abs(float(o)), 1e-10):
                    return False
            return True
    except (ValueError, TypeError):
        pass
    
    return False


def main():
    """Main function to run all expressions through pyqalculate."""
    print("Initializing pyqalculate...")
    
    # Import and initialize calculator
    from pyqalculate.calculator import Calculator
    
    calculator = Calculator()
    calculator.load_definitions()
    calculator.load_global_definitions()
    
    print(f"Loaded {calculator.count_functions()} functions, "
          f"{calculator.count_variables()} variables, "
          f"{calculator.count_units()} units")
    
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Process each file
    all_comparisons: list[ComparisonResult] = []
    file_summaries: list[dict] = []
    
    for filename in FILES:
        input_path = INPUT_DIR / filename
        output_path = OUTPUT_DIR / filename
        
        if not input_path.exists():
            print(f"WARNING: Input file not found: {input_path}")
            continue
        
        print(f"\nProcessing {filename}...")
        expressions = parse_input_file(input_path)
        
        results_for_file: list[tuple[Expression, str]] = []
        comparisons_for_file: list[ComparisonResult] = []
        
        for expr in expressions:
            print(f"  {expr.number} {expr.description}...", end=" ", flush=True)
            
            pyq_result = run_pyqalculate(expr.expression, calculator)
            match = results_match(expr.original_result, pyq_result)
            
            results_for_file.append((expr, pyq_result))
            comparisons_for_file.append(ComparisonResult(
                expr=expr,
                pyqalculate_result=pyq_result,
                match=match,
            ))
            
            if match:
                print("[OK]")
            else:
                print("[DIFF]")
                print(f"    Original:    {expr.original_result}")
                print(f"    PyQalculate: {pyq_result}")
        
        # Create output file
        create_output_file(output_path, expressions[0].category if expressions else "", results_for_file)
        
        # Calculate file summary
        file_matches = sum(1 for c in comparisons_for_file if c.match)
        file_total = len(comparisons_for_file)
        file_summaries.append({
            "filename": filename,
            "total": file_total,
            "matches": file_matches,
            "differs": file_total - file_matches,
            "match_rate": file_matches / file_total * 100 if file_total > 0 else 0,
        })
        
        all_comparisons.extend(comparisons_for_file)
    
    # Generate comparison summary
    summary_path = OUTPUT_DIR / "comparison_summary.txt"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("PYQALCULATE COMPARISON SUMMARY\n")
        f.write("=" * 60 + "\n\n")
        
        f.write("FILE-BY-FILE RESULTS:\n")
        f.write("-" * 60 + "\n")
        
        for summary in file_summaries:
            f.write(f"{summary['filename']}: "
                    f"{summary['matches']}/{summary['total']} matches "
                    f"({summary['match_rate']:.1f}%)\n")
        
        f.write("\n" + "=" * 60 + "\n")
        f.write("OVERALL STATISTICS:\n")
        f.write("-" * 60 + "\n")
        
        overall = compare_results(all_comparisons)
        f.write(f"Total expressions: {overall['total']}\n")
        f.write(f"Matches: {overall['matches']}\n")
        f.write(f"Differs: {overall['differs']}\n")
        f.write(f"Errors: {overall['errors']}\n")
        f.write(f"Match rate: {overall['match_rate']:.1f}%\n")
        
        f.write("\n" + "=" * 60 + "\n")
        f.write("DIFFERENCES:\n")
        f.write("-" * 60 + "\n")
        
        for comp in all_comparisons:
            if not comp.match:
                f.write(f"\n{comp.expr.number} {comp.expr.description}\n")
                f.write(f"  Expression: {comp.expr.expression}\n")
                f.write(f"  Original:    {comp.expr.original_result}\n")
                f.write(f"  PyQalculate: {comp.pyqalculate_result}\n")
                if comp.error:
                    f.write(f"  Error: {comp.error}\n")
    
    print(f"\n{'=' * 60}")
    print("SUMMARY:")
    print(f"{'=' * 60}")
    print(f"Total expressions: {overall['total']}")
    print(f"Matches: {overall['matches']}")
    print(f"Differs: {overall['differs']}")
    print(f"Errors: {overall['errors']}")
    print(f"Match rate: {overall['match_rate']:.1f}%")
    print(f"\nResults saved to: {OUTPUT_DIR}")
    print(f"Comparison summary: {summary_path}")


if __name__ == "__main__":
    main()
