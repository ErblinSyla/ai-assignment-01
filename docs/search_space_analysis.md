# Search-Space Analysis

Raw bounds count assignments before constraints. They are not numbers of solutions, reachable states or explored nodes. No timing or node-count measurements are reported here because none were taken.

## Latin Square (order n)
- Raw unconstrained assignments: `n^(n²)`. For n = 5: 5^25 ≈ 2.98 × 10^17.
- Rows as permutations: `(n!)^n`. For n = 5: 120^5 ≈ 2.49 × 10^10.
- Actual number of Latin squares (OEIS A002860): n=1..6 gives 1, 2, 12, 576, 161280, 812851200. For n = 5 only 161 280 of 2.98 × 10^17 raw assignments are valid.

## Sudoku
- With `e` empty cells: `9^e` raw assignments before filtering. Saved files have 45 / 34 / 26 clues (easy / medium / hard), so `e` = 36 / 47 / 55, giving ≈ 2.3 × 10^34, 7.1 × 10^44 and 3.0 × 10^52.
- Valid completed 9×9 grids total ≈ 6.67 × 10^21 (Felgenhauer & Jarvis). A given puzzle usually admits far fewer completions (ideally one); that was not verified for these puzzles.
- Backtracking explores only a tiny fraction of `9^e` because row/column/box constraints and MRV prune early.

## Social Golfers
- One week as a partition of `n = g·p` golfers into `g` unlabelled groups of `p`: `n! / ((p!)^g · g!)`.
  - 9/3/3: 9!/(6³·3!) = 280.
  - 32/8/4: 32!/(24⁸·8!) ≈ 5.9 × 10^19.
- A `w`-week schedule is at most that count to the power `w` before the no-repeated-pair constraint. This is an upper bound, not the number of valid schedules.
- Counting bound on weeks: each week uses `g·C(p,2)` of the `C(n,2)` pairs, so `weeks ≤ ⌊(n−1)/(p−1)⌋`. 9/3/3 gives 4 (attained by the saved schedule). 32/8/4 gives 10 as an upper bound only; no claim is made about whether 10 is attainable.

## 8-Puzzle
- Arrangements: 9! = 362 880. Exactly half (181 440) are reachable from any given solvable state (parity of inversions).
- Branching factor: 2 (blank in a corner), 3 (edge), 4 (centre); average over blank positions (4·2 + 4·3 + 4)/9 ≈ 2.67.
- A tree search without repeated-state checks can grow like `b^d`; graph search is bounded by the 181 440 reachable states. The saved example is a 10-state fragment, not the full space.

## Missionaries and Cannibals (3, 3, capacity 2)
- Raw encodings: 4 × 4 × 2 = 32. Valid states (population bounds and both banks safe): `(m,c)` ∈ {(0,0),(0,1),(0,2),(0,3),(3,0),(3,1),(3,2),(3,3),(1,1),(2,2)} × 2 boat positions = 20 (derived by hand).
- Not all valid states are reachable from `[3,3,1]`. The saved graph lists 14 states, which is a fragment, not an exhaustive enumeration. The 11-crossing path is the length BFS should find, but no execution trace is claimed.

## Rotating workforce (toy model)
- Raw day assignments: 3⁴ = 81 (including partial); complete schedules 2⁴ = 16. With at most 2 days per employee, only the 6 schedules in which each employee works exactly 2 days remain. This describes the invented model only and has no real-world meaning.