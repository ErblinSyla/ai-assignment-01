# Algorithms

## Social Golfers: DFS / backtracking (`social_golfers.solve`)
Builds the schedule group by group. Each group contains the smallest golfer not yet placed in that week, with the other members chosen in ascending order (symmetry breaking within a week). A candidate group is rejected if any of its pairs has already met; otherwise its pairs are marked and the search recurses. On failure the pairs are unmarked and the next candidate is tried.
- **Completeness:** the search is exhaustive, so `None` means no schedule exists for the requested weeks. Symmetries between weeks and golfer relabelling are not removed, so some equivalent branches are repeated.
- **Termination:** recursion depth is at most `weeks × groups`, and each level has finitely many candidates.
- **Complexity:** exponential in the worst case. One week of 9/3/3 has 280 partitions; the pair constraint prunes later weeks.
- **Valid schedule vs maximum weeks:** a successful `solve(g, p, w)` only shows that `w` weeks are achievable (a lower bound on the maximum). A maximum needs a proof that `w+1` is impossible, e.g. an exhaustive `None` or the counting bound `⌊(n−1)/(p−1)⌋`. If `w` weeks exist, so do `w−1` (drop a week). For 9/3/3 the bound is 4 and the saved 4-week schedule meets it. The code does not search for the maximum for 32/8/4 and nothing here claims to.
- **Saved evidence:** `outputs/social_golfers.json` is the affine plane of order 3 (rows, columns and two diagonal classes of a 3×3 grid), checked with `validate_file`. It is not claimed to be the schedule `solve` would print.

## Sudoku: backtracking with MRV (`sudoku.solve`)
Bitmasks track digits used per row, column and box. At each step the empty cell with the fewest candidates is chosen. A cell with zero candidates triggers backtracking, and candidates are tried in ascending order.
- **Completeness/termination:** at most 81 levels, 9 digits each, so the search terminates. It returns a solution if one exists and `None` otherwise. Input clue conflicts are detected before searching.
- **Complexity:** worst case `O(9^e)` for `e` empty cells; MRV pruning makes typical puzzles fast. Only the first solution found is returned, and uniqueness is not checked.

## Latin Square: backtracking (`latin_square.solve`)
Fills cells row-major, trying symbols `1..n` not used in the cell's row or column; `prefilled` entries are respected.
- **Completeness/termination:** exhaustive over a finite tree of depth `n²`. Worst case `O(n^{n²})`, but pruning keeps small orders fast; intended for modest `n`.
- `cyclic_square(n)` is a direct construction used for the saved evidence and for larger orders.

## Search-tree representations (`search_trees`)
- Each problem provides a state validity check and a move function. `validate_graph` checks schema, state validity, endpoint membership, legality and label of every edge, and goal reachability along the listed edges.
- **Optional BFS** (`bfs`): implemented as an extra, not an assignment requirement. It keeps a `parent` table, so a state is never enqueued twice (repeated-state handling). It is complete on finite state spaces and returns a minimum-length path under unit costs; time and memory are `O(|V|+|E|)` over reachable states.
- **Repeated states:** in 8-Puzzle, moving the blank back recreates the previous state, so a tree search without a visited set would revisit states. `outputs/eight_puzzle.json` includes the back-edge `S1 → S0` to illustrate this; BFS skips it.
- Missionaries/Cannibals and the workforce toy model use the same BFS and graph checks. Workforce transitions are student-invented and unofficial.
- Not implemented: DFS/IDS over the state graphs, A*, and any solver for the real workforce constraints.