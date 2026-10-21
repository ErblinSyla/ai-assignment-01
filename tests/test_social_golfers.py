"""Tests for assignment.social_golfers."""
from pathlib import Path

import pytest

from assignment import social_golfers as sg

ROOT = Path(__file__).resolve().parents[1]
GOOD = [
    [[0, 1, 2], [3, 4, 5], [6, 7, 8]],
    [[0, 3, 6], [1, 4, 7], [2, 5, 8]],
]


def test_solve_returns_valid_schedule():
    schedule = sg.solve(3, 3, 4)
    assert schedule is not None and len(schedule) == 4
    assert sg.is_valid_schedule(schedule, 9, 3, 3)


def test_solve_small_instance_and_exhaustive_none():
    assert sg.is_valid_schedule(sg.solve(2, 2, 3), 4, 2, 2)
    # 4 golfers have 6 pairs; each week uses 2 pairs, so 4 weeks is impossible.
    assert sg.solve(2, 2, 4) is None


@pytest.mark.parametrize("args", [(0, 3, 1), (3, 0, 1), (3, 3, 0), (3, -1, 2)])
def test_solve_rejects_bad_parameters(args):
    with pytest.raises(ValueError):
        sg.solve(*args)


def test_valid_schedule_has_no_errors():
    assert sg.validate_schedule(GOOD, 9, 3, 3) == []


def test_repeated_pair_detected():
    bad = [GOOD[0], [[0, 1, 3], [2, 4, 6], [5, 7, 8]]]
    errors = sg.validate_schedule(bad, 9, 3, 3)
    assert any("meets again" in e for e in errors)


def test_invalid_group_size():
    bad = [[[0, 1], [2, 3, 4, 5], [6, 7, 8]]]
    assert any("size" in e for e in sg.validate_schedule(bad, 9, 3, 3))


def test_wrong_number_of_groups():
    bad = [[[0, 1, 2, 3, 4], [5, 6, 7, 8]]]
    assert any("expected 3 groups" in e for e in sg.validate_schedule(bad, 9, 3, 3))


def test_missing_golfer_and_duplicate_in_group():
    bad = [[[0, 1, 2], [3, 4, 5], [6, 7, 7]]]
    errors = sg.validate_schedule(bad, 9, 3, 3)
    assert any("duplicate golfer" in e for e in errors)
    assert any("missing [8]" in e for e in errors)


def test_golfer_in_two_groups_same_week():
    bad = [[[0, 1, 2], [2, 3, 4], [5, 6, 7]]]
    errors = sg.validate_schedule(bad, 9, 3, 3)
    assert any("more than one group" in e for e in errors)


def test_golfer_id_out_of_range():
    bad = [[[0, 1, 2], [3, 4, 5], [6, 7, 9]]]
    assert any("outside" in e for e in sg.validate_schedule(bad, 9, 3, 3))


def test_inconsistent_parameters():
    errors = sg.validate_schedule(GOOD, 10, 3, 3)
    assert any("inconsistent parameters" in e for e in errors)


def test_validate_data_declared_weeks_mismatch():
    data = sg.schedule_to_json(GOOD, 3, 3)
    data["weeks"] = 3
    assert any("declared weeks" in e for e in sg.validate_data(data))


def test_validate_data_missing_keys_and_wrong_type():
    assert any("missing keys" in e for e in sg.validate_data({"n": 9}))
    assert sg.validate_data([]) != []


def test_saved_evidence_file_is_valid_and_consistent():
    path = ROOT / "outputs" / "social_golfers.json"
    assert sg.validate_file(str(path)) == []
    import json
    data = json.loads(path.read_text(encoding="utf-8"))
    assert (data["n"], data["groups"], data["group_size"], data["weeks"]) == (9, 3, 3, 4)