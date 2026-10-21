"""Tests for assignment.sudoku."""
from pathlib import Path

import pytest

from assignment import sudoku

OUT = Path(__file__).resolve().parents[1] / "outputs" / "sudoku"
LEVELS = ["easy", "medium", "hard"]


def load(level, kind):
    return sudoku.load_csv(str(OUT / f"{level}_sudoku_{kind}.csv"))


@pytest.mark.parametrize("level", LEVELS)
def test_saved_solution_is_valid_and_preserves_clues(level):
    assert sudoku.validate_solution(load(level, "solution"), load(level, "clues")) == []


@pytest.mark.parametrize("level", LEVELS)
def test_solver_solves_saved_puzzle(level):
    clues = load(level, "clues")
    solved = sudoku.solve(clues)
    assert solved is not None
    assert sudoku.is_valid_solution(solved, clues)


def test_solve_does_not_modify_input():
    clues = load("easy", "clues")
    copy = [row[:] for row in clues]
    sudoku.solve(clues)
    assert clues == copy


def test_empty_board_is_solvable():
    solved = sudoku.solve([[0] * 9 for _ in range(9)])
    assert solved is not None and sudoku.is_valid_solution(solved)


def test_csv_round_trip():
    board = load("medium", "clues")
    assert sudoku.parse_csv(sudoku.format_csv(board)) == board


@pytest.mark.parametrize("text", [
    "1,2,3\n" * 9,                              # wrong row length
    ("0," * 8 + "0\n") * 8,                     # only 8 rows
    ("0," * 8 + "x\n") * 9,                     # non-integer
    ("0," * 8 + "10\n") * 9,                    # out of range
])
def test_malformed_csv_raises(text):
    with pytest.raises(ValueError):
        sudoku.parse_csv(text)


def test_solve_rejects_malformed_board():
    with pytest.raises(ValueError):
        sudoku.solve([[0] * 9 for _ in range(8)])
    with pytest.raises(ValueError):
        sudoku.solve([[0] * 9] * 8 + [[0] * 8 + [-1]])


def test_contradictory_clues_duplicate_in_row():
    board = [[0] * 9 for _ in range(9)]
    board[0][0] = board[0][1] = 5
    assert sudoku.find_conflicts(board)
    assert sudoku.solve(board) is None


def test_contradictory_clues_without_direct_duplicate():
    # Cell (0,8) has no candidate: row 0 holds 1-8 and column 8 already holds 9.
    board = [[0] * 9 for _ in range(9)]
    board[0][:8] = [1, 2, 3, 4, 5, 6, 7, 8]
    board[1][8] = 9
    assert sudoku.find_conflicts(board) == []
    assert sudoku.solve(board) is None


def test_invalid_row_detected():
    board = load("easy", "solution")
    board[0][0] = 3
    errors = sudoku.validate_solution(board)
    assert any(e.startswith("row 1") for e in errors)


def test_invalid_columns_detected_but_rows_ok():
    board = load("easy", "solution")
    board[0][0], board[0][1] = board[0][1], board[0][0]
    errors = sudoku.validate_solution(board)
    assert any(e.startswith("column 1") for e in errors)
    assert not any(e.startswith("row") for e in errors)


def test_invalid_subgrids_detected_but_rows_and_columns_ok():
    board = [[(i + j) % 9 + 1 for j in range(9)] for i in range(9)]
    errors = sudoku.validate_solution(board)
    assert any(e.startswith("subgrid") for e in errors)
    assert not any(e.startswith(("row", "column")) for e in errors)


def test_incomplete_board_is_not_a_valid_solution():
    assert not sudoku.is_valid_solution(load("easy", "clues"))


def test_clue_not_preserved_detected():
    errors = sudoku.validate_solution(load("medium", "solution"), load("easy", "clues"))
    assert any("not preserved" in e for e in errors)


def test_count_empty():
    assert sudoku.count_empty([[0] * 9 for _ in range(9)]) == 81
    assert sudoku.count_empty(load("easy", "solution")) == 0