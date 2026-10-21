# Missionaries and Cannibals Diagram

Matches `outputs/missionaries_cannibals.json`. State = `[missionaries_left, cannibals_left, boat_left]` (boat 1 = left bank). Initial `[3,3,1]`, goal `[0,0,0]`, boat capacity 2. The main path has 11 crossings. Dashed nodes are the other two legal first moves (the remaining first moves, 1M or 2M alone, leave an unsafe bank).

```mermaid
flowchart TD
    A0["[3,3,1] initial"]
    A1["[3,1,0]"]
    A2["[3,2,1]"]
    A3["[3,0,0]"]
    A4["[3,1,1]"]
    A5["[1,1,0]"]
    A6["[2,2,1]"]
    A7["[0,2,0]"]
    A8["[0,3,1]"]
    A9["[0,1,0]"]
    A10["[0,2,1]"]
    A11["[0,0,0] goal"]
    B1["[3,2,0]"]
    B2["[2,2,0]"]

    A0 -->|"cross 0M 2C left to right"| A1
    A1 -->|"cross 0M 1C right to left"| A2
    A2 -->|"cross 0M 2C left to right"| A3
    A3 -->|"cross 0M 1C right to left"| A4
    A4 -->|"cross 2M 0C left to right"| A5
    A5 -->|"cross 1M 1C right to left"| A6
    A6 -->|"cross 2M 0C left to right"| A7
    A7 -->|"cross 0M 1C right to left"| A8
    A8 -->|"cross 0M 2C left to right"| A9
    A9 -->|"cross 0M 1C right to left"| A10
    A10 -->|"cross 0M 2C left to right"| A11
    A0 -.->|"cross 0M 1C left to right"| B1
    A0 -.->|"cross 1M 1C left to right"| B2
```