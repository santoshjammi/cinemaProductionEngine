# GIR Canonical Examples — Phase 1: The "Golden Set"

## Purpose
These examples are not merely stress tests; they are the **living specification** of GIR semantics. They define how GIR *should* work by showing its successful application across different narrative geometries.

- If a new story cannot be modeled using these nodes, edges, and states without modification, **GIR needs an update**.
- If the resulting causality graph is ambiguous or fails to convey the intended subtext, **the ontology is flawed**.

## The Golden Set (v0.1)
We begin with three structural pillars that cover the widest possible semantic range:

1.  **`01_human_withdrawal.yaml`** (The Anchor): Based on our current project ("The Space Between Us"). Tests `Intent Paradox`, `Psychological Constraints`, and `Relational State Machines`.
2.  **`02_sci_fi_survival.yaml`** (The Physical Stress Test): A procedural survival scenario. Tests `Resource Management`, `Physical World State`, and `Conflict of Necessity`.
3.  **`03_multi_character_betrayal.yaml`** (The Complexity Test): Introduces a third party and shifting alliances to test graph scaling.

## How to Read GIR Examples
- **Nodes:** The events, actions, and intents in the graph.
- **Edges:** The causal links (`causes`, `enables`, `prevents`) between nodes.
- **States:** The initial (Start) and final (End) values of World, Character, and Relationship maps.
- **Intents:** The orthogonal drivers that sit outside the timeline but force action.

## Implementation Order
These examples will serve as the primary input for **Phase 2: Validator**. The validator must strictly pass these documents before we attempt to compile them down to any backend (video, literary, etc.).
