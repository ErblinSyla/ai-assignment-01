"""9x9 Sudoku: CSV parsing, validation and a backtracking solver.

Board representation: list of 9 rows, each a list of 9 ints; 0 means empty.

Error policy:
  * malformed input (wrong shape, non-integers, values outside 0..9) -> ValueError
  * well-formed but contradictory clues, or no solution -> `solve` returns None
"""
from __future__ import annotations

import argparse
import sys
from typing import Iterator, List, Optional, Sequence, Tuple

Board = List[List[int]]
SIZE = 9


def check_shape(board: Sequence[Sequence[int]]) -> Board:
    """Return a copied board, or raise ValueError if it is not a 9x9 grid of ints 0..9."""
    if not isinstance(board, (list, tuple)) or len(board) != SIZE:
        raise ValueError("board must have 9 rows")
    out: Board = []
    for r, row in enumerate(board, start=1):
        if not isinstance(row, (list, tuple)) or len(row) != SIZE:
            raise ValueError(f"row {r} must have 9 cells")
        for value in row:
            if type(value) is not int or not 0 <= value <= 9:
                raise ValueError(f"row {r}: cell values must be integers 0-9, got {value!r}")
        out.append(list(row))
    return out


def parse_csv(text: str) -> Board:
    """Parse nine lines of nine comma-separated integers."""
    board: Board = []
    for r, line in enumerate((ln for ln in text.splitlines() if ln.strip()), start=1):
        try:
            board.append([int(cell.strip()) for cell in line.split(",")])
        except ValueError:
            raise ValueError(f"row {r}: non-integer entry") from None
    return check_shape(board)


def load_csv(path: str) -> Board:
    with open(path, encoding="utf-8") as handle:
        return parse_csv(handle.read())


def format_csv(board: Sequence[Sequence[int]]) -> str:
    return "\n".join(",".join(str(v) for v in row) for row in board) + "\n"


def count_empty(board: Sequence[Sequence[int]]) -> int:
    return sum(1 for row in board for v in row if v == 0)


def _units(board: Board) -> Iterator[Tuple[str, List[int]]]:
    for i in range(SIZE):
        yield f"row {i + 1}", list(board[i])
    for i in range(SIZE):
        yield f"column {i + 1}", [board[r][i] for r in range(SIZE)]
    for br in range(3):
        for bc in range(3):
            yield (f"subgrid {br * 3 + bc + 1}",
                   [board[r][c] for r in range(3 * br, 3 * br + 3) for c in range(3 * bc, 3 * bc + 3)])


def find_conflicts(board: Sequence[Sequence[int]]) -> List[str]:
    """Report duplicate non-zero digits in any row, column or subgrid (empty cells ignored)."""
    grid = check_shape(board)
    errors = []
    for label, values in _units(grid):
        dups = sorted({v for v in values if v and values.count(v) > 1})
        if dups:
            errors.append(f"{label}: duplicate digits {dups}")
    return errors


def validate_solution(board: Sequence[Sequence[int]],
                      clues: Optional[Sequence[Sequence[int]]] = None) -> List[str]:
    """Return errors for a completed board; optionally check every clue is preserved."""
    try:
        grid = check_shape(board)
    except ValueError as exc:
        return [str(exc)]
    errors = []
    for label, values in _units(grid):
        if sorted(values) != list(range(1, 10)):
            errors.append(f"{label}: must contain digits 1-9 exactly once, found {values}")
    if clues is not None:
        try:
            given = check_shape(clues)
        except ValueError as exc:
            return errors + [f"clues: {exc}"]
        for r in range(SIZE):
            for c in range(SIZE):
                if given[r][c] and given[r][c] != grid[r][c]:
                    errors.append(f"clue {given[r][c]} at row {r + 1}, column {c + 1} not preserved")
    return errors


def is_valid_solution(board: Sequence[Sequence[int]],
                      clues: Optional[Sequence[Sequence[int]]] = None) -> bool:
    return not validate_solution(board, clues)


def solve(puzzle: Sequence[Sequence[int]]) -> Optional[Board]:
    """Backtracking with minimum-remaining-values cell choice. Input is not modified.

    Returns the first solution found, or None if clues conflict or no solution exists.
    Raises ValueError for malformed input. Uniqueness of the solution is not checked.
    """
    board = check_shape(puzzle)
    if find_conflicts(board):
        return None
    rows, cols, boxes = [0] * SIZE, [0] * SIZE, [0] * SIZE
    for r in range(SIZE):
        for c in range(SIZE):
            v = board[r][c]
            if v:
                bit = 1 << v
                rows[r] |= bit
                cols[c] |= bit
                boxes[3 * (r // 3) + c // 3] |= bit

    def search() -> bool:
        best = None
        best_mask, best_count = 0, 10
        for r in range(SIZE):
            for c in range(SIZE):
                if board[r][c] == 0:
                    used = rows[r] | cols[c] | boxes[3 * (r // 3) + c // 3]
                    avail = ~used & 0x3FE  # bits 1..9
                    count = bin(avail).count("1")
                    if count == 0:
                        return False
                    if count < best_count:
                        best, best_mask, best_count = (r, c), avail, count
        if best is None:
            return True
        r, c = best
        b = 3 * (r // 3) + c // 3
        for v in range(1, 10):
            bit = 1 << v
            if best_mask & bit:
                board[r][c] = v
                rows[r] |= bit
                cols[c] |= bit
                boxes[b] |= bit
                if search():
                    return True
                board[r][c] = 0
                rows[r] ^= bit
                cols[c] ^= bit
                boxes[b] ^= bit
        return False

    return board if search() else None


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Sudoku solver / checker")
    parser.add_argument("csv_file")
    parser.add_argument("--check", metavar="CLUES_CSV",
                        help="treat csv_file as a solution and check it against these clues")
    args = parser.parse_args(argv)
    try:
        board = load_csv(args.csv_file)
        if args.check:
            errors = validate_solution(board, load_csv(args.check))
            print("OK" if not errors else "\n".join(errors))
            return 0 if not errors else 1
        solved = solve(board)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}")
        return 2
    if solved is None:
        print("No solution (contradictory clues or unsolvable puzzle).")
        return 1
    print(format_csv(solved), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())