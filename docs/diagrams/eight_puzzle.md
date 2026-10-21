# 8-Puzzle Diagram

Matches `outputs/eight_puzzle.json`. States are flat lists, `0` = blank. Initial = S0, goal = S6. The solid path S0→S6 is an optimal 6-move path. Dashed nodes are other legal moves from S0. The edge S1→S0 shows a repeated state, which BFS skips.

```mermaid
flowchart LR
    S0["S0 initial<br/>[1,2,3,7,0,5,8,4,6]"]
    S1["S1<br/>[1,2,3,7,4,5,8,0,6]"]
    S2["S2<br/>[1,2,3,7,4,5,0,8,6]"]
    S3["S3<br/>[1,2,3,0,4,5,7,8,6]"]
    S4["S4<br/>[1,2,3,4,0,5,7,8,6]"]
    S5["S5<br/>[1,2,3,4,5,0,7,8,6]"]
    S6["S6 goal<br/>[1,2,3,4,5,6,7,8,0]"]
    U["U<br/>[1,0,3,7,2,5,8,4,6]"]
    L["L<br/>[1,2,3,0,7,5,8,4,6]"]
    R["R<br/>[1,2,3,7,5,0,8,4,6]"]

    S0 -->|"move blank down"| S1
    S1 -->|"move blank left"| S2
    S2 -->|"move blank up"| S3
    S3 -->|"move blank right"| S4
    S4 -->|"move blank right"| S5
    S5 -->|"move blank down"| S6
    S0 -.->|"move blank up"| U
    S0 -.->|"move blank left"| L
    S0 -.->|"move blank right"| R
    S1 -.->|"move blank up (repeated state S0)"| S0
```