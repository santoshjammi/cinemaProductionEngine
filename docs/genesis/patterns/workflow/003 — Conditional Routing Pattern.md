Genesis Pattern (GP)
GP-WF-003 — Conditional Routing Pattern

Document ID: GP-WF-003
Title: Conditional Routing Pattern
Version: 1.0.0
Status: Pattern
Authority: Derived from GFS-005 Agent Constitution, GWS-001

1. Purpose

The Conditional Routing Pattern defines how Genesis selects the next agent or workflow branch based on the state of the Production Knowledge Graph rather than a fixed sequence. Routing is data-driven: the Production Orchestrator evaluates declared conditions against PKG facts and dispatches the branch whose predicate holds.

In Genesis, conditional routing is used when a single workflow must serve productions with divergent shapes — a documentary routes to the Archival Research Agent, a narrative routes to the Story Architect Agent, a devotional production routes to the Devotional Coherence Validator. Hard-coding every variant would explode the workflow registry; conditional routing keeps one workflow polymorphic.

2. When to Apply

Apply this pattern when:

- A workflow must branch based on production type, genre, territory, or declared constraint.
- A validation result determines the next step (pass → advance, fail → revise, critical fail → escalate).
- An agent's output determines whether a downstream agent runs at all (e.g. Music Composer runs only if the Narrative Subgraph declares a music motif).
- A revision loop must select the correct upstream agent based on the failure class.

Do not apply this pattern when the next agent is strictly determined by the predecessor's completion (use Sequential, GP-WF-001) or when branches are independent and should run together (use Parallel Fan-Out, GP-WF-002).

3. Structure

A conditional route is modeled as:

    Input state ─→ Router ─┬─ condition A? ─→ Branch A
                           ├─ condition B? ─→ Branch B
                           └─ condition C? ─→ Branch C

The route declares:

- Input state — the PKG snapshot the router reads.
- Condition set — ordered predicates evaluated against the input state.
- Branch map — agent ID (GAS-NNN) per condition.
- Default branch — the branch taken when no condition holds.
- Re-join policy — whether branches converge to a common next stage or terminate independently.

4. Condition Specification

Each condition is a typed predicate over the PKG:

- Subject — a PKG node or query result.
- Predicate — a registered operator (equals, exists, has_cardinality, classified_as, confidence_above, status_is).
- Object — the comparison value.
- Negated — optional negation flag.

Conditions are evaluated in declared order. The first condition that holds selects its branch. If none hold, the default branch runs. The default branch is mandatory — a router without a default is invalid.

Conditions may be composed with AND / OR. Nested composition is allowed but must be normalized to disjunctive normal form for auditability.

5. Workflow

5.1 Declare the Route

The Production Orchestrator commits the route specification to the PKG before evaluation. The specification lists conditions, branches, and the default. Runtime conditions are forbidden — the route is fixed at declaration time.

5.2 Snapshot the Input State

Read a consistent snapshot of the PKG. Conditions evaluate against the snapshot, not the live PKG, so that all predicates see the same world.

5.3 Evaluate Conditions

Evaluate predicates in order. The router emits a Routing Decision Record naming: the snapshot ID, each condition's result (true / false / indeterminate), and the selected branch.

5.4 Dispatch the Branch

Invoke the selected branch agent with its declared input contract. The branch runs as a normal agent invocation — it may itself be a sequential workflow, a fan-out, or another conditional route.

5.5 Re-Join or Terminate

After the branch completes, the router applies the re-join policy:

- Converge — all branches flow into a common next stage. The next stage starts.
- Terminate — the branch's completion ends the workflow for this path. No common next stage.
- Conditional re-join — a second route selects the next stage based on the branch's output.

6. Use Inside Genesis

- Genre routing — Documentary → Archival Research Agent; Narrative → Story Architect Agent; Devotional → Devotional Coherence Validator.
- Validation routing — Structural pass → Semantic Validator; Structural fail → Revision Agent with the failing agent as target.
- Confidence routing — abductive conclusion confidence ≥ 0.85 → advance; 0.6–0.85 → Research Agent clarification; < 0.6 → Governance Agent review.
- Asset routing — music motif declared → Music Composer Agent; no motif → skip music stage.

7. Worked Example

Stage 2 routing after the Production Brief is parsed:

Input state: production_type = "devotional", territory = "bhakti", audience = "temple congregation".

Conditions (in order):
1. production_type equals "documentary" → Archival Research Agent
2. production_type equals "narrative" AND territory not equals "devotional" → Story Architect Agent
3. production_type equals "devotional" OR territory equals "devotional" → Devotional Coherence Validator then Story Architect Agent
4. default → Story Architect Agent

Evaluation: condition 1 false, condition 2 false, condition 3 true.

Branch: Devotional Coherence Validator runs first; on pass, Story Architect Agent runs. On fail, Revision Agent is dispatched to the Production Brief Parser.

Re-join: all branches converge to Stage 3 (Screenplay Generation).

8. Anti-Patterns

- Declaring a route without a default branch.
- Evaluating conditions against the live PKG — use a snapshot.
- Letting the router mutate the PKG — routers only read and dispatch.
- Adding conditions at runtime — the route is fixed at declaration.
- Routing to an unregistered agent — all branch targets must exist in the Agent Registry.
- Skipping the Routing Decision Record — every dispatch must be auditable.

9. Exit Criteria

A conditional route is complete when:

- The route specification is committed to the PKG.
- The input snapshot is taken and identified.
- Conditions are evaluated in order with results recorded.
- The selected branch is dispatched.
- The Routing Decision Record is committed with snapshot ID, condition results, and branch ID.
- The re-join policy is applied and the next stage (if any) is invoked or the workflow is terminated.