"""Tests for assignment.latin_square."""
from pathlib import Path

import pytest

from assignment import latin_square as ls

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("order", [1, 2, 3, 4, 5, 6])
def test_solver_produces_valid_square(order):
    square = ls.solve(order)
    assert square is not None
    assert ls.is_latin_square(square, order)


@pytest.mark.parametrize("order", [1, 4, 7, 10])
def test_cyclic_square_is_valid(order):
    assert ls.is_latin_square(ls.cyclic_square(order), order)


def test_saved_evidence_matches_cyclic_order_5():
    square = ls.load_csv(str(ROOT / "outputs" / "latin_square.csv"))
    assert len(square) == 5
    assert ls.validate_latin_square(square) == []
    assert square == ls.cyclic_square(5)


def test_prefilled_entries_are_preserved():
    prefilled = [[0] * 4 for _ in range(4)]
    prefilled[0][0] = 2
    prefilled[1][1] = 4
    result = ls.solve(4, prefilled)
    assert result is not None and ls.is_latin_square(result, 4)
    assert result[0][0] == 2 and result[1][1] == 4


def test_conflicting_prefilled_returns_none():
    assert ls.solve(3, [[1, 1, 0], [0, 0, 0], [0, 0, 0]]) is None
    assert ls.solve(3, [[1, 0, 0], [1, 0, 0], [0, 0, 0]]) is None


@pytest.mark.parametrize("args", [(0,), (-2,), (3, [[0, 0], [0, 0]]), (2, [[0, 3], [0, 0]])])
def test_solve_rejects_bad_arguments(args):
    with pytest.raises(ValueError):
        ls.solve(*args)


def test_duplicate_in_row():
    errors = ls.validate_latin_square([[1, 1], [2, 2]])
    assert any(e.startswith("row 1") for e in errors)


def test_duplicate_in_column():
    errors = ls.validate_latin_square([[1, 2], [1, 2]])
    assert any(e.startswith("column 1") for e in errors)


def test_wrong_dimensions():
    assert any("expected 3 rows" in e for e in ls.validate_latin_square([[1, 2, 3], [2, 3, 1]], order=3))
    assert any("expected 2 columns" in e for e in ls.validate_latin_square([[1, 2, 3], [2, 3, 1]]))
    assert ls.validate_latin_square([]) != []


def test_symbols_outside_domain():
    assert any("outside" in e for e in ls.validate_latin_square([[1, 2], [2, 3]]))
    assert any("outside" in e for e in ls.validate_latin_square([[0, 1], [1, 0]]))
    assert any("outside" in e for e in ls.validate_latin_square([[1, "2"], [2, 1]]))


def test_order_argument_mismatch():
    assert not ls.is_latin_square(ls.cyclic_square(3), order=4)