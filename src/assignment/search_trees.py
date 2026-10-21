"""Search-tree state models: 8-Puzzle, Missionaries and Cannibals, toy workforce scheduling.

Executable search is NOT an assignment requirement; `bfs` is an optional extra with
repeated-state detection. States are tuples in code and lists in JSON.

Evidence graph schema: {"initial": S, "goal": S, "states": [S...],
                        "edges": [{"from": S, "to": S, "action": str}...]}

State encodings
  8-Puzzle:  flat 9-tuple, row-major, 0 = blank; goal (1,2,3,4,5,6,7,8,0).
  Missionaries/Cannibals: (missionaries_left, cannibals_left, boat_left), boat_left 1 = boat on
             left bank; 3 missionaries, 3 cannibals, boat capacity 2; initial (3,3,1), goal (0,0,0).
  Workforce (STUDENT-INVENTED toy model): 4-tuple, one entry per day, an employee id or "-".
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import deque
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

State = Tuple[Any, ...]
Moves = Callable[[State], List[Tuple[str, State]]]


def bfs(initial: Sequence[Any], goal: Sequence[Any], moves: Moves) -> Optional[List[Tuple[str, State]]]:
    """Breadth-first search; returns [(action, state), ...] from initial to goal, or None.

    Repeated states are skipped via the `parent` table. BFS returns a path with the
    fewest transitions when every transition has equal cost.
    """
    start, target = tuple(initial), tuple(goal)
    if start == target:
        return []
    parent: Dict[State, Optional[Tuple[State, str]]] = {start: None}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        for action, nxt in moves(current):
            if nxt in parent:
                continue
            parent[nxt] = (current, action)
            if nxt == target:
                steps: List[Tuple[str, State]] = []
                node = nxt
                while parent[node] is not None:
                    prev, act = parent[node]
                    steps.append((act, node))
                    node = prev
                return steps[::-1]
            queue.append(nxt)
    return None


def _action_between(moves: Moves, src: State, dst: State) -> Optional[str]:
    for action, nxt in moves(src):
        if nxt == dst:
            return action
    return None


# ----------------------------------------------------------------- 8-Puzzle
EIGHT_GOAL: State = (1, 2, 3, 4, 5, 6, 7, 8, 0)
EIGHT_DEMO_INITIAL: State = (1, 2, 3, 7, 0, 5, 8, 4, 6)
_EIGHT_DIRECTIONS = (("up", -3), ("down", 3), ("left", -1), ("right", 1))


def is_valid_eight_state(state: Sequence[Any]) -> bool:
    return (len(state) == 9 and all(type(t) is int for t in state)
            and set(state) == set(range(9)))


def is_solvable_eight_puzzle(state: Sequence[int]) -> bool:
    """Reachable from the goal iff the tile permutation (blank excluded) has even inversions."""
    tiles = [t for t in state if t != 0]
    inversions = sum(1 for i in range(len(tiles)) for j in range(i + 1, len(tiles)) if tiles[i] > tiles[j])
    return inversions % 2 == 0


def eight_puzzle_moves(state: Sequence[int]) -> List[Tuple[str, State]]:
    """Legal blank moves in fixed order up, down, left, right."""
    state = tuple(state)
    blank = state.index(0)
    row, col = divmod(blank, 3)
    result = []
    for name, delta in _EIGHT_DIRECTIONS:
        if (name == "up" and row == 0) or (name == "down" and row == 2) \
                or (name == "left" and col == 0) or (name == "right" and col == 2):
            continue
        target = blank + delta
        cells = list(state)
        cells[blank], cells[target] = cells[target], cells[blank]
        result.append((f"move blank {name}", tuple(cells)))
    return result


def eight_puzzle_legal_action(src: State, dst: State) -> Optional[str]:
    """Action label if dst follows from src by one legal blank move, else None."""
    return _action_between(eight_puzzle_moves, src, dst)


# ------------------------------------------------- Missionaries and Cannibals
MC_TOTAL_M, MC_TOTAL_C, MC_CAPACITY = 3, 3, 2
MC_INITIAL: State = (3, 3, 1)
MC_GOAL: State = (0, 0, 0)
_MC_LOADS = tuple((dm, dc) for dm in range(MC_CAPACITY + 1) for dc in range(MC_CAPACITY + 1)
                  if 1 <= dm + dc <= MC_CAPACITY)


def _bank_safe(missionaries: int, cannibals: int) -> bool:
    return missionaries == 0 or missionaries >= cannibals


def mc_is_valid_state(state: Sequence[Any]) -> bool:
    """Population bounds, boat flag in {0,1}, and safety on both banks."""
    if len(state) != 3 or not all(type(x) is int for x in state):
        return False
    m, c, boat = state
    if not (0 <= m <= MC_TOTAL_M and 0 <= c <= MC_TOTAL_C and boat in (0, 1)):
        return False
    return _bank_safe(m, c) and _bank_safe(MC_TOTAL_M - m, MC_TOTAL_C - c)


def mc_moves(state: Sequence[int]) -> List[Tuple[str, State]]:
    """Legal crossings: 1..2 passengers move with the boat; the result must be a valid state."""
    m, c, boat = state
    result = []
    for dm, dc in _MC_LOADS:
        if boat == 1:
            new, direction = (m - dm, c - dc, 0), "left to right"
        else:
            new, direction = (m + dm, c + dc, 1), "right to left"
        if mc_is_valid_state(new):
            result.append((f"cross {dm}M {dc}C {direction}", new))
    return result


def mc_legal_action(src: State, dst: State) -> Optional[str]:
    return _action_between(mc_moves, src, dst)


# ---------------------------------------- Rotating workforce (toy, invented)
WORKFORCE_EMPLOYEES = ("E1", "E2")
WORKFORCE_DAYS = 4
WORKFORCE_MAX_DAYS = 2          # student assumption A3
WORKFORCE_MAX_CONSECUTIVE = 2   # student assumption A2
UNASSIGNED = "-"
WORKFORCE_INITIAL: State = (UNASSIGNED,) * WORKFORCE_DAYS
WORKFORCE_GOAL: State = ("E1", "E1", "E2", "E2")


def workforce_violations(state: Sequence[Any]) -> List[str]:
    """Violations of the toy constraints (partial schedules are allowed)."""
    if len(state) != WORKFORCE_DAYS or any(x not in WORKFORCE_EMPLOYEES + (UNASSIGNED,) for x in state):
        return [f"state needs {WORKFORCE_DAYS} entries, each one of {WORKFORCE_EMPLOYEES} or '-'"]
    errors = []
    for emp in WORKFORCE_EMPLOYEES:
        total = sum(1 for x in state if x == emp)
        if total > WORKFORCE_MAX_DAYS:
            errors.append(f"{emp} works {total} days (max {WORKFORCE_MAX_DAYS})")
        run = best = 0
        for x in state:
            run = run + 1 if x == emp else 0
            best = max(best, run)
        if best > WORKFORCE_MAX_CONSECUTIVE:
            errors.append(f"{emp} works {best} consecutive days (max {WORKFORCE_MAX_CONSECUTIVE})")
    return errors


def is_workforce_state(state: Sequence[Any]) -> bool:
    return not workforce_violations(state)


def is_workforce_goal(state: Sequence[Any]) -> bool:
    return is_workforce_state(state) and UNASSIGNED not in state


def workforce_moves(state: Sequence[Any]) -> List[Tuple[str, State]]:
    """Assign the first unassigned day to each employee whose assignment keeps the toy rules."""
    state = tuple(state)
    if UNASSIGNED not in state:
        return []
    day = state.index(UNASSIGNED)
    result = []
    for emp in WORKFORCE_EMPLOYEES:
        new = state[:day] + (emp,) + state[day + 1:]
        if is_workforce_state(new):
            result.append((f"assign day {day + 1} to {emp}", new))
    return result


def workforce_legal_action(src: State, dst: State) -> Optional[str]:
    return _action_between(workforce_moves, src, dst)


# ------------------------------------------------------------- graph checks
def _as_state(value: Any) -> Optional[State]:
    if isinstance(value, list) and all(isinstance(x, (int, str)) for x in value):
        return tuple(value)
    return None


def validate_graph(data: Any, is_state: Callable[[State], bool],
                   legal_action: Callable[[State, State], Optional[str]]) -> List[str]:
    """Check schema, state validity, edge endpoints, edge legality/labels and goal reachability."""
    if not isinstance(data, dict):
        return ["top-level JSON value must be an object"]
    missing = [k for k in ("initial", "goal", "states", "edges") if k not in data]
    if missing:
        return [f"missing keys: {', '.join(missing)}"]
    if not isinstance(data["states"], list) or not isinstance(data["edges"], list):
        return ["'states' and 'edges' must be lists"]
    errors: List[str] = []
    states = set()
    for i, raw in enumerate(data["states"]):
        state = _as_state(raw)
        if state is None or not is_state(state):
            errors.append(f"states[{i}] is not a valid state: {raw!r}")
        elif state in states:
            errors.append(f"duplicate state {raw!r}")
        else:
            states.add(state)
    endpoints = {}
    for key in ("initial", "goal"):
        state = _as_state(data[key])
        if state is None or not is_state(state):
            errors.append(f"'{key}' is not a valid state: {data[key]!r}")
        elif state not in states:
            errors.append(f"'{key}' {data[key]!r} does not occur in states")
        else:
            endpoints[key] = state
    adjacency: Dict[State, List[State]] = {}
    for i, edge in enumerate(data["edges"]):
        if not isinstance(edge, dict) or not {"from", "to", "action"} <= set(edge):
            errors.append(f"edges[{i}] must be an object with 'from', 'to' and 'action'")
            continue
        src, dst = _as_state(edge["from"]), _as_state(edge["to"])
        if src is None or dst is None:
            errors.append(f"edges[{i}]: endpoints must be state lists")
            continue
        unknown = [name for name, s in (("from", src), ("to", dst)) if s not in states]
        if unknown:
            errors.append(f"edges[{i}]: unknown state in {', '.join(unknown)}")
            continue
        action = legal_action(src, dst)
        if action is None:
            errors.append(f"edges[{i}]: illegal transition {list(src)} -> {list(dst)}")
        elif action != edge["action"]:
            errors.append(f"edges[{i}]: action {edge['action']!r} should be {action!r}")
        adjacency.setdefault(src, []).append(dst)
    if not errors and len(endpoints) == 2:
        seen, stack = {endpoints["initial"]}, [endpoints["initial"]]
        while stack:
            for nxt in adjacency.get(stack.pop(), []):
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        if endpoints["goal"] not in seen:
            errors.append("goal is not reachable from initial along the listed edges")
    return errors


def validate_eight_puzzle_graph(data: Any) -> List[str]:
    errors = validate_graph(data, is_valid_eight_state, eight_puzzle_legal_action)
    if not errors:
        if tuple(data["goal"]) != EIGHT_GOAL:
            errors.append("goal is not the conventional goal [1,2,3,4,5,6,7,8,0]")
        if not is_solvable_eight_puzzle(data["initial"]):
            errors.append("initial state is not solvable")
    return errors


def validate_missionaries_graph(data: Any) -> List[str]:
    errors = validate_graph(data, mc_is_valid_state, mc_legal_action)
    if not errors and (tuple(data["initial"]) != MC_INITIAL or tuple(data["goal"]) != MC_GOAL):
        errors.append("initial/goal must be [3,3,1] and [0,0,0] for the 3-missionary, 3-cannibal example")
    return errors


def validate_workforce_graph(data: Any) -> List[str]:
    errors = validate_graph(data, is_workforce_state, workforce_legal_action)
    if not errors and not is_workforce_goal(tuple(data["goal"])):
        errors.append("goal must be a complete schedule satisfying the toy constraints")
    return errors


_PROBLEMS = {
    "eight": (EIGHT_DEMO_INITIAL, EIGHT_GOAL, eight_puzzle_moves, validate_eight_puzzle_graph),
    "missionaries": (MC_INITIAL, MC_GOAL, mc_moves, validate_missionaries_graph),
    "workforce": (WORKFORCE_INITIAL, WORKFORCE_GOAL, workforce_moves, validate_workforce_graph),
}


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Search-tree demos and evidence validation")
    parser.add_argument("problem", choices=sorted(_PROBLEMS))
    parser.add_argument("--validate", metavar="JSON_FILE", help="validate a saved graph instead of running BFS")
    args = parser.parse_args(argv)
    initial, goal, moves, validator = _PROBLEMS[args.problem]
    if args.validate:
        with open(args.validate, encoding="utf-8") as handle:
            errors = validator(json.load(handle))
        print("OK" if not errors else "\n".join(errors))
        return 0 if not errors else 1
    path = bfs(initial, goal, moves)
    if path is None:
        print("goal not reachable")
        return 1
    print(f"start: {list(initial)}")
    for action, state in path:
        print(f"{action} -> {list(state)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())