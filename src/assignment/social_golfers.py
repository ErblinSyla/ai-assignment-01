"""Social Golfers Problem: DFS/backtracking solver and schedule validator.

n = groups * group_size golfers play for several weeks. Each week the golfers are
partitioned into `groups` groups of `group_size`; no two golfers may share a group
more than once over the whole schedule.

Schedule representation: schedule[week][group] -> list of golfer ids (0..n-1).

`solve` decides whether a schedule with the requested number of weeks exists and
returns the first one found (or None after exhausting the search). It does NOT
prove a maximum number of weeks by itself.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from itertools import combinations
from typing import Any, Dict, List, Optional, Sequence

Schedule = List[List[List[int]]]
REQUIRED_KEYS = ("n", "groups", "group_size", "weeks", "schedule")


def check_parameters(groups: int, group_size: int) -> int:
    """Return n = groups * group_size, or raise ValueError for bad parameters."""
    for name, value in (("groups", groups), ("group_size", group_size)):
        if type(value) is not int or value < 1:
            raise ValueError(f"{name} must be a positive integer, got {value!r}")
    return groups * group_size


def solve(groups: int, group_size: int, weeks: int) -> Optional[Schedule]:
    """Depth-first search for a valid schedule with exactly `weeks` weeks.

    Symmetry breaking: in each week the group containing the smallest unassigned
    golfer is built next, and members are chosen in ascending order. The search is
    exhaustive, so None means no schedule exists for these parameters.
    """
    n = check_parameters(groups, group_size)
    if type(weeks) is not int or weeks < 1:
        raise ValueError(f"weeks must be a positive integer, got {weeks!r}")

    met = [[False] * n for _ in range(n)]
    schedule: Schedule = []

    def mark(group: Sequence[int], value: bool) -> None:
        for a, b in combinations(group, 2):
            met[a][b] = met[b][a] = value

    def place_group(week_groups: List[List[int]], unassigned: List[int]) -> bool:
        if not unassigned:
            return finish_week(week_groups)
        first, rest = unassigned[0], unassigned[1:]
        for combo in combinations(rest, group_size - 1):
            group = (first,) + combo
            if any(met[a][b] for a, b in combinations(group, 2)):
                continue
            mark(group, True)
            week_groups.append(list(group))
            remaining = [g for g in rest if g not in combo]
            if place_group(week_groups, remaining):
                return True
            week_groups.pop()
            mark(group, False)
        return False

    def finish_week(week_groups: List[List[int]]) -> bool:
        schedule.append([list(g) for g in week_groups])
        if len(schedule) == weeks:
            return True
        if place_group([], list(range(n))):
            return True
        schedule.pop()
        return False

    return schedule if place_group([], list(range(n))) else None


def _is_golfer(value: Any, n: int) -> bool:
    return type(value) is int and 0 <= value < n


def validate_schedule(schedule: Sequence[Sequence[Sequence[int]]], n: int,
                      groups: int, group_size: int) -> List[str]:
    """Return a list of error messages; an empty list means the schedule is valid."""
    errors: List[str] = []
    if n != groups * group_size:
        errors.append(f"inconsistent parameters: n={n} but groups*group_size={groups * group_size}")
    if len(schedule) == 0:
        errors.append("schedule contains no weeks")
    first_met: Dict[tuple, int] = {}
    for w, week in enumerate(schedule, start=1):
        if len(week) != groups:
            errors.append(f"week {w}: expected {groups} groups, found {len(week)}")
        seen: Counter = Counter()
        for gi, group in enumerate(week, start=1):
            if len(group) != group_size:
                errors.append(f"week {w}, group {gi}: size {len(group)}, expected {group_size}")
            if len(set(group)) != len(group):
                errors.append(f"week {w}, group {gi}: duplicate golfer inside group")
            ids = [g for g in group if _is_golfer(g, n)]
            if len(ids) != len(group):
                errors.append(f"week {w}, group {gi}: golfer id outside 0..{n - 1}")
            seen.update(set(ids))
            for pair in combinations(sorted(set(ids)), 2):
                if pair in first_met:
                    errors.append(f"pair {pair} meets again in week {w} (first met in week {first_met[pair]})")
                else:
                    first_met[pair] = w
        missing = [g for g in range(n) if seen[g] == 0]
        repeated = sorted(g for g, c in seen.items() if c > 1)
        if missing:
            errors.append(f"week {w}: golfers missing {missing}")
        if repeated:
            errors.append(f"week {w}: golfers appear in more than one group {repeated}")
    return errors


def is_valid_schedule(schedule: Sequence[Sequence[Sequence[int]]], n: int,
                      groups: int, group_size: int) -> bool:
    """True iff `validate_schedule` reports no errors."""
    return not validate_schedule(schedule, n, groups, group_size)


def schedule_to_json(schedule: Schedule, groups: int, group_size: int) -> Dict[str, Any]:
    """Build the evidence dictionary (keys n, groups, group_size, weeks, schedule)."""
    return {"n": groups * group_size, "groups": groups, "group_size": group_size,
            "weeks": len(schedule), "schedule": schedule}


def _shape_ok(schedule: Any) -> bool:
    return (isinstance(schedule, list)
            and all(isinstance(w, list) and all(isinstance(g, list) for g in w) for w in schedule))


def validate_data(data: Any) -> List[str]:
    """Validate a parsed evidence dictionary, including declared-vs-actual parameters."""
    if not isinstance(data, dict):
        return ["top-level JSON value must be an object"]
    missing = [k for k in REQUIRED_KEYS if k not in data]
    if missing:
        return [f"missing keys: {', '.join(missing)}"]
    errors = [f"'{k}' must be a positive integer" for k in ("n", "groups", "group_size", "weeks")
              if type(data[k]) is not int or data[k] < 1]
    if errors:
        return errors
    if not _shape_ok(data["schedule"]):
        return ["schedule must be nested lists: weeks -> groups -> golfer ids"]
    if data["weeks"] != len(data["schedule"]):
        errors.append(f"declared weeks={data['weeks']} but schedule has {len(data['schedule'])} weeks")
    return errors + validate_schedule(data["schedule"], data["n"], data["groups"], data["group_size"])


def validate_file(path: str) -> List[str]:
    """Load a JSON evidence file and validate it."""
    with open(path, encoding="utf-8") as handle:
        return validate_data(json.load(handle))


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Social Golfers solver / validator")
    parser.add_argument("--groups", type=int, default=3)
    parser.add_argument("--group-size", type=int, default=3)
    parser.add_argument("--weeks", type=int, default=4)
    parser.add_argument("--validate", metavar="JSON_FILE", help="validate a saved schedule instead of solving")
    args = parser.parse_args(argv)
    if args.validate:
        errors = validate_file(args.validate)
        print("OK" if not errors else "\n".join(errors))
        return 0 if not errors else 1
    result = solve(args.groups, args.group_size, args.weeks)
    if result is None:
        print("No schedule exists for these parameters.")
        return 1
    print(json.dumps(schedule_to_json(result, args.groups, args.group_size)))
    return 0


if __name__ == "__main__":
    sys.exit(main())