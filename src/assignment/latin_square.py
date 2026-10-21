"""Latin Square of order n: backtracking solver, cyclic construction and validator.

A Latin square of order n is an n x n grid over symbols 1..n in which every symbol
occurs exactly once in each row and each column. Square representation: list of rows.
`solve` is plain cell-by-cell backtracking and is intended for modest n (roughly <= 7);
recursion depth is n*n.
"""
from __future__ import annotations

import argparse
import csv
import sys
from typing import List, Optional, Sequence

Square = List[List[int]]


def validate_latin_square(square: Sequence[Sequence[int]], order: Optional[int] = None) -> List[str]:
    """Return error messages; an empty list means a valid Latin square (of `order` if given)."""
    if not isinstance(square, (list, tuple)) or len(square) == 0:
        return ["square must be a non-empty list of rows"]
    n = len(square) if order is None else order
    errors: List[str] = []
    if len(square) != n:
        errors.append(f"expected {n} rows, found {len(square)}")
    for r, row in enumerate(square, start=1):
        if not isinstance(row, (list, tuple)) or len(row) != n:
            errors.append(f"row {r}: expected {n} columns")
    if errors:
        return errors
    for r, row in enumerate(square, start=1):
        for c, value in enumerate(row, start=1):
            if type(value) is not int or not 1 <= value <= n:
                errors.append(f"row {r}, column {c}: symbol {value!r} outside 1..{n}")
    if errors:
        return errors
    for r, row in enumerate(square, start=1):
        if len(set(row)) != n:
            errors.append(f"row {r}: symbols are not unique")
    for c in range(n):
        if len({square[r][c] for r in range(len(square))}) != n:
            errors.append(f"column {c + 1}: symbols are not unique")
    return errors


def is_latin_square(square: Sequence[Sequence[int]], order: Optional[int] = None) -> bool:
    return not validate_latin_square(square, order)


def cyclic_square(order: int) -> Square:
    """Deterministic construction: cell (i, j) = (i + j) mod n + 1 (always valid)."""
    if type(order) is not int or order < 1:
        raise ValueError("order must be a positive integer")
    return [[(i + j) % order + 1 for j in range(order)] for i in range(order)]


def solve(order: int, prefilled: Optional[Sequence[Sequence[int]]] = None) -> Optional[Square]:
    """Backtracking solver; `prefilled` uses 0 for empty cells.

    Returns the first completion found in row-major / ascending-symbol order, or None
    if the prefilled entries conflict or cannot be completed. Raises ValueError for
    malformed arguments.
    """
    if type(order) is not int or order < 1:
        raise ValueError("order must be a positive integer")
    square: Square = [[0] * order for _ in range(order)]
    row_used = [set() for _ in range(order)]
    col_used = [set() for _ in range(order)]
    if prefilled is not None:
        if len(prefilled) != order or any(len(row) != order for row in prefilled):
            raise ValueError(f"prefilled must be {order} x {order}")
        for r in range(order):
            for c in range(order):
                v = prefilled[r][c]
                if type(v) is not int or not 0 <= v <= order:
                    raise ValueError(f"prefilled entry {v!r} outside 0..{order}")
                if v:
                    if v in row_used[r] or v in col_used[c]:
                        return None
                    square[r][c] = v
                    row_used[r].add(v)
                    col_used[c].add(v)
    cells = [(r, c) for r in range(order) for c in range(order) if square[r][c] == 0]

    def fill(i: int) -> bool:
        if i == len(cells):
            return True
        r, c = cells[i]
        for v in range(1, order + 1):
            if v not in row_used[r] and v not in col_used[c]:
                square[r][c] = v
                row_used[r].add(v)
                col_used[c].add(v)
                if fill(i + 1):
                    return True
                square[r][c] = 0
                row_used[r].discard(v)
                col_used[c].discard(v)
        return False

    return [row[:] for row in square] if fill(0) else None


def format_csv(square: Sequence[Sequence[int]]) -> str:
    return "\n".join(",".join(str(v) for v in row) for row in square) + "\n"


def load_csv(path: str) -> Square:
    """Read a comma-separated integer matrix; raises ValueError on non-integers."""
    with open(path, newline="", encoding="utf-8") as handle:
        return [[int(cell) for cell in row] for row in csv.reader(handle) if row]


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Latin square solver / validator")
    parser.add_argument("--order", type=int, default=5)
    parser.add_argument("--cyclic", action="store_true", help="print the cyclic construction")
    parser.add_argument("--validate", metavar="CSV_FILE", help="validate a saved square")
    args = parser.parse_args(argv)
    try:
        if args.validate:
            errors = validate_latin_square(load_csv(args.validate))
            print("OK" if not errors else "\n".join(errors))
            return 0 if not errors else 1
        square = cyclic_square(args.order) if args.cyclic else solve(args.order)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}")
        return 2
    if square is None:
        print("No Latin square found.")
        return 1
    print(format_csv(square), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())