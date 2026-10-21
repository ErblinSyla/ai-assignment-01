# Testing and Evidence

No test result is claimed here; the tests are provided to be run by the student:

```bash
pip install -e ".[dev]"
python -m pytest
```

## Tests
| File | Checks |
|---|---|
| `tests/test_social_golfers.py` | solver output validity; exhaustive `None` on a tiny impossible case; bad parameters; repeated pairs, wrong group size/count, missing/duplicate/out-of-range golfers, inconsistent `n`, declared-vs-actual weeks; saved JSON validity |
| `tests/test_sudoku.py` | saved solutions valid and clue-preserving; solver result valid on all three puzzles; input not mutated; malformed CSV/boards raise `ValueError`; contradictory clues give `None`; invalid row/column/subgrid detection; clue-preservation failure |
| `tests/test_latin_square.py` | solver for orders 1–6; cyclic construction for orders up to 10; saved CSV valid and equal to `cyclic_square(5)`; prefilled entries; duplicates, wrong dimensions, out-of-domain symbols |
| `tests/test_search_trees.py` | saved graphs pass validators; missing keys, unknown state references, missing edge fields, wrong labels, duplicates, unreachable goal; illegal 8-Puzzle and Missionaries/Cannibals transitions; BFS paths; workforce toy rules and its limitations |

## How evidence relates to code
- The saved files are the primary evidence. Each can be re-checked with the matching CLI (`--validate` or `--check`, see README), and the tests load and validate them.
- Source files own all validation logic (`validate_*`, `*_legal_action`); tests and CLI call them rather than duplicating them.
- The saved Sudoku solutions are not claimed to equal solver output where a puzzle might have several solutions; tests check validity and clue preservation instead.

## What the external reviewer can and cannot establish
- It reads the files statically and does not execute source code or pytest, so passing tests cannot be established by it.
- It can check Social Golfers schedules, Sudoku/Latin Square matrices and search-tree structure and transitions (8-Puzzle, Missionaries and Cannibals).
- Workforce constraints are not officially configured, so that file needs manual review and only shows internal consistency with student-invented rules.
- AST evidence does not prove an algorithm is correct or complete. The reviewer does not assign an official grade or establish plagiarism.