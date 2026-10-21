"""Tests for assignment.search_trees (state models, graph validation, optional BFS)."""
import copy
import json
from pathlib import Path

import pytest

from assignment import search_trees as st

OUT = Path(__file__).resolve().parents[1] / "outputs"


def load(name):
    return json.loads((OUT / name).read_text(encoding="utf-8"))


# ---------------------------------------------------------------- saved evidence
def test_saved_graphs_are_valid():
    assert st.validate_eight_puzzle_graph(load("eight_puzzle.json")) == []
    assert st.validate_missionaries_graph(load("missionaries_cannibals.json")) == []
    assert st.validate_workforce_graph(load("rotating_workforce.json")) == []


# ---------------------------------------------------------------- graph structure
def test_missing_keys_and_wrong_top_level_type():
    assert any("missing keys" in e for e in st.validate_eight_puzzle_graph({"initial": []}))
    assert st.validate_eight_puzzle_graph([]) != []


def test_unknown_state_reference():
    data = load("eight_puzzle.json")
    data["edges"].append({"from": data["initial"], "to": [9] * 9, "action": "x"})
    assert any("unknown state" in e for e in st.validate_eight_puzzle_graph(data))


def test_edge_missing_field():
    data = load("eight_puzzle.json")
    data["edges"].append({"from": data["initial"], "to": data["goal"]})
    assert any("must be an object" in e for e in st.validate_eight_puzzle_graph(data))


def test_duplicate_state_and_unreachable_goal():
    data = load("eight_puzzle.json")
    dup = copy.deepcopy(data)
    dup["states"].append(dup["states"][0])
    assert any("duplicate state" in e for e in st.validate_eight_puzzle_graph(dup))
    cut = copy.deepcopy(data)
    cut["edges"].pop()  # removes the final move into the goal
    assert any("not reachable" in e for e in st.validate_eight_puzzle_graph(cut))


def test_wrong_action_label():
    data = load("eight_puzzle.json")
    data["edges"][0]["action"] = "move blank sideways"
    assert any("should be" in e for e in st.validate_eight_puzzle_graph(data))


# ---------------------------------------------------------------- 8-Puzzle
def test_eight_puzzle_illegal_transitions():
    start = (1, 2, 3, 7, 0, 5, 8, 4, 6)
    assert st.eight_puzzle_legal_action(start, (2, 1, 3, 7, 0, 5, 8, 4, 6)) is None   # tile swap
    assert st.eight_puzzle_legal_action(start, st.EIGHT_GOAL) is None                 # teleport
    assert st.eight_puzzle_legal_action(start, start) is None                         # no move


def test_illegal_edge_in_graph_is_reported():
    data = load("eight_puzzle.json")
    data["edges"].append({"from": data["initial"], "to": data["goal"], "action": "jump"})
    assert any("illegal transition" in e for e in st.validate_eight_puzzle_graph(data))


def test_eight_puzzle_no_wraparound():
    state = (1, 2, 0, 4, 5, 3, 7, 8, 6)  # blank in top-right corner
    assert [a for a, _ in st.eight_puzzle_moves(state)] == ["move blank down", "move blank left"]
    assert len(st.eight_puzzle_moves((1, 2, 3, 4, 0, 5, 6, 7, 8))) == 4


def test_eight_puzzle_state_validity_and_solvability():
    assert st.is_valid_eight_state(st.EIGHT_GOAL)
    assert not st.is_valid_eight_state((1, 1, 2, 3, 4, 5, 6, 7, 0))
    assert not st.is_valid_eight_state((1, 2, 3))
    assert st.is_solvable_eight_puzzle(st.EIGHT_DEMO_INITIAL)
    assert not st.is_solvable_eight_puzzle((1, 2, 3, 4, 5, 6, 8, 7, 0))


def test_eight_puzzle_graph_contains_repeated_state_edge():
    data = load("eight_puzzle.json")
    s0, s1 = data["states"][0], data["states"][1]
    assert any(e["from"] == s1 and e["to"] == s0 for e in data["edges"])


def test_eight_puzzle_bfs_path_has_no_repeated_states():
    path = st.bfs(st.EIGHT_DEMO_INITIAL, st.EIGHT_GOAL, st.eight_puzzle_moves)
    assert path is not None and len(path) == 6
    states = [s for _, s in path]
    assert states[-1] == st.EIGHT_GOAL
    assert len(set(states)) == len(states)


def test_bfs_trivial_case():
    assert st.bfs(st.EIGHT_GOAL, st.EIGHT_GOAL, st.eight_puzzle_moves) == []


# ---------------------------------------------------------------- Missionaries and Cannibals
def test_mc_state_validity():
    assert st.mc_is_valid_state((3, 3, 1))
    assert st.mc_is_valid_state((2, 2, 0))
    assert not st.mc_is_valid_state((1, 2, 1))   # left bank unsafe
    assert not st.mc_is_valid_state((2, 1, 1))   # right bank unsafe
    assert not st.mc_is_valid_state((4, 0, 1))   # population bound
    assert not st.mc_is_valid_state((3, 3, 2))   # boat flag


def test_mc_initial_moves():
    moves = st.mc_moves(st.MC_INITIAL)
    assert {s for _, s in moves} == {(3, 1, 0), (3, 2, 0), (2, 2, 0)}


def test_mc_illegal_crossings():
    assert st.mc_legal_action((3, 3, 1), (1, 3, 0)) is None   # unsafe bank
    assert st.mc_legal_action((3, 3, 1), (0, 3, 0)) is None   # three passengers
    assert st.mc_legal_action((3, 3, 1), (3, 2, 1)) is None   # boat did not cross
    assert st.mc_legal_action((3, 3, 1), (3, 3, 0)) is None   # empty boat
    assert st.mc_legal_action((3, 3, 1), (3, 1, 0)) == "cross 0M 2C left to right"


def test_mc_illegal_edge_in_graph_is_reported():
    data = load("missionaries_cannibals.json")
    data["states"].append([0, 3, 0])
    data["edges"].append({"from": [3, 3, 1], "to": [0, 3, 0], "action": "cross 3M 0C left to right"})
    assert any("illegal transition" in e for e in st.validate_missionaries_graph(data))


def test_mc_wrong_initial_state_is_reported():
    data = load("missionaries_cannibals.json")
    data["initial"] = [3, 2, 0]
    assert st.validate_missionaries_graph(data) != []


def test_mc_bfs_finds_eleven_crossings():
    path = st.bfs(st.MC_INITIAL, st.MC_GOAL, st.mc_moves)
    assert path is not None and len(path) == 11
    assert path[-1][1] == st.MC_GOAL


# ---------------------------------------------------------------- Rotating workforce (toy)
def test_workforce_violations():
    assert st.workforce_violations(("E1", "E2", "E1", "E2")) == []
    assert any("days" in e for e in st.workforce_violations(("E1", "E1", "E1", "-")))
    assert st.workforce_violations(("E1", "E1")) != []          # wrong length
    assert st.workforce_violations(("E3", "-", "-", "-")) != []  # employee outside the model


def test_workforce_moves_respect_toy_constraints():
    assert st.workforce_moves(("E1", "E1", "-", "-")) == [("assign day 3 to E2", ("E1", "E1", "E2", "-"))]
    assert st.workforce_moves(st.WORKFORCE_GOAL) == []


def test_workforce_goal_requires_complete_schedule():
    assert st.is_workforce_goal(st.WORKFORCE_GOAL)
    assert not st.is_workforce_goal(("E1", "E1", "-", "-"))


def test_workforce_bfs_reaches_goal():
    path = st.bfs(st.WORKFORCE_INITIAL, st.WORKFORCE_GOAL, st.workforce_moves)
    assert path is not None and len(path) == 4


def test_workforce_toy_model_is_not_a_real_staffing_model():
    # Reaching the goal only shows consistency with invented rules (2 employees, 4 days,
    # max 2 days each). It says nothing about skills, shifts, rest rules or demand.
    assert (len(st.WORKFORCE_EMPLOYEES), st.WORKFORCE_DAYS) == (2, 4)
    assert st.is_workforce_goal(("E2", "E1", "E1", "E2"))  # also "feasible" under the toy rules
    assert st.workforce_violations(("E1", "E2", "E3", "-")) != []  # no model of extra staff