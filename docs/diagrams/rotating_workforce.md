# Rotating Workforce Diagram (toy model)

Matches `outputs/rotating_workforce.json`. **All constraints are student-invented** (2 employees, 4 days, at most 2 days per employee, at most 2 consecutive days) and are not official requirements. Each entry is the employee for days 1–4, `-` = unassigned. From `[E1,E1,-,-]` assigning E1 to day 3 is not an edge because it would give E1 three days. Real workforce scheduling needs the instructor's or problem owner's actual constraints.

```mermaid
flowchart TD
    W0["[-,-,-,-] initial"]
    W1["[E1,-,-,-]"]
    W2["[E1,E1,-,-]"]
    W3["[E1,E1,E2,-]"]
    W4["[E1,E1,E2,E2] goal"]
    W5["[E2,-,-,-]"]
    W6["[E1,E2,-,-]"]

    W0 -->|"assign day 1 to E1"| W1
    W1 -->|"assign day 2 to E1"| W2
    W2 -->|"assign day 3 to E2"| W3
    W3 -->|"assign day 4 to E2"| W4
    W0 -.->|"assign day 1 to E2"| W5
    W1 -.->|"assign day 2 to E2"| W6
```