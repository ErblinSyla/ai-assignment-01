# AI Assignment 01 — Uninformed Search Techniques

Course: Artificial Intelligence, academic year 2026–2027. Language: Python 3.

## Overview
Four areas: (1) Social Golfers, (2) Sudoku, (3) Latin Square, (4) Search Trees
(8-Puzzle, Missionaries and Cannibals, Rotating Workforce Scheduling).
Saved evidence lives in `outputs/`; source, tests and docs support it.

## Structure
```text
src/assignment/   social_golfers.py, sudoku.py, latin_square.py, search_trees.py
outputs/          saved evidence (JSON / CSV)
tests/            pytest tests
docs/             formulation, algorithms, search-space analysis, testing, references, diagrams/
```

## Python version
Python 3.9 or newer. No third-party runtime dependencies; `pytest` is needed only for tests.

## Install and test (run these yourself)
```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python -m pytest
```
`pyproject.toml` sets `pythonpath = ["src"]`, so `python -m pytest` also works without installing.

## Running the solvers
```bash
# Social Golfers: DFS/backtracking, prints JSON; or validate a saved file
python -m assignment.social_golfers --groups 3 --group-size 3 --weeks 4
python -m assignment.social_golfers --validate outputs/social_golfers.json

# Sudoku: solve a clue CSV (prints solved CSV); or check a solution against its clues
python -m assignment.sudoku outputs/sudoku/easy_sudoku_clues.csv
python -m assignment.sudoku outputs/sudoku/easy_sudoku_solution.csv --check outputs/sudoku/easy_sudoku_clues.csv

# Latin Square: backtracking solve, cyclic construction, or validate a CSV
python -m assignment.latin_square --order 5
python -m assignment.latin_square --order 5 --cyclic
python -m assignment.latin_square --validate outputs/latin_square.csv

# Search trees: BFS demo path, or validate a saved graph
python -m assignment.search_trees eight
python -m assignment.search_trees missionaries
python -m assignment.search_trees workforce
python -m assignment.search_trees eight --validate outputs/eight_puzzle.json
```

## Evidence files
| File | Content |
|---|---|
| `outputs/social_golfers.json` | 9 golfers, 3 groups of 3, 4 weeks (keys `n, groups, group_size, weeks, schedule`) |
| `outputs/sudoku/{easy,medium,hard}_sudoku_{clues,solution}.csv` | 9×9 matrices, `0` = empty in clue files |
| `outputs/latin_square.csv` | Order-5 cyclic Latin square (equals `cyclic_square(5)`) |
| `outputs/eight_puzzle.json` | Search-tree graph (`initial, goal, states, edges`), flat 9-int states |
| `outputs/missionaries_cannibals.json` | Same schema; state `[missionaries_left, cannibals_left, boat_left]` |
| `outputs/rotating_workforce.json` | Same schema; toy student-made model |

## Assumptions and limitations
- The assignment config (32 golfers, 8 groups of 4) leaves the number of weeks unspecified. The saved evidence uses a smaller demo (9/3/3, 4 weeks). It is not a solution for the 32-golfer configuration and proves nothing about that instance.
- Finding a valid schedule for a given number of weeks is not the same as proving the maximum number of weeks (see `docs/algorithms.md`).
- Sudoku puzzles are student-created. Easy/Medium/Hard labels are illustrative, not instructor-provided.
- Search-tree executable search is not an assignment requirement; the BFS here is an optional extra.
- Rotating workforce scheduling uses a toy model with **student-invented** constraints (`docs/problem_formulation.md`). Real constraints must come from the instructor or problem owner. Passing the toy model says nothing about real staffing feasibility.
- Tests and commands are provided for you to run; this README makes no claim that they have been run.