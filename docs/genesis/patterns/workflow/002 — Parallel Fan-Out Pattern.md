Genesis Pattern (GP)
GP-WF-002 — Parallel Fan-Out Pattern

Document ID: GP-WF-002
Title: Parallel Fan-Out Pattern
Version: 1.0.0
Status: Pattern
Authority: Derived from GFS-005 Agent Constitution, GWS-001

1. Purpose

The Parallel Fan-Out Pattern defines how Genesis runs multiple agents simultaneously when their work is independent, then merges their results into a coherent PKG update. Parallelism is the engine of throughput: when three agents can each populate a separate subgraph of the PKG without reading each other's output, running them sequentially would waste time without improving quality.

In Genesis, fan-out is disciplined. Independence is verified at the contract level, not assumed. Merge is governed: conflicts are detected, classified, and resolved according to the governance constitution. Parallelism without a merge plan produces a fractured PKG.

2. When to Apply

Apply this pattern when:

- Multiple agents produce disjoint PKG subgraphs (e.g. Story Architect → Narrative Subgraph, Character Manager → Character Subgraph, Environment Manager → World Subgraph).
- Multiple evaluators must independently assess the same production (the seven evaluators in Stage 7).
- Multiple generators can produce independent assets (Image, Voice, Music, SFX in Stage 5).
- The cost of waiting outweighs the cost of merging.

Do not apply this pattern when one agent's output materially shapes another's input (use Sequential, GP-WF-001) or when the next agent depends on a condition the parallel agents produce (use Conditional Routing, GP-WF-003).

3. Structure

A parallel fan-out is modeled as:

           ┌─→ Agent A ─→ Output A ─┐
Input set ─┼─→ Agent B ─→ Output B ─┼─→ Merge → PKG update
           └─→ Agent C ─→ Output C ─┘

The fan-out declares:

- Shared input set — read-only inputs all parallel agents consume.
- Branch list — agent IDs (GAS-NNN) that execute concurrently.
- Output contracts — each branch's typed output.
- Merge specification — how outputs combine and how conflicts resolve.
- Barrier — the synchronization point at which all branches must complete before merge.

4. Independence Verification

Before fan-out, the Production Orchestrator Agent verifies that:

- No branch reads another branch's output contract.
- No branch writes to a subgraph another branch writes to.
- No branch's side effects (e.g. asset generation) collide on file paths.
- All branches share the same read-only input snapshot — they cannot read each other's in-flight writes.

If any of these fail, the agents are not independent and must run sequentially or with a different fan-out decomposition.

5. Workflow

5.1 Snapshot Inputs

Take a read-only snapshot of the PKG at fan-out time. All branches consume the snapshot, never the live PKG.

5.2 Dispatch Branches

Dispatch all branches concurrently. Each branch runs in its own execution context with its own thread ID. Branches emit output contracts into staging buffers, not into the live PKG.

5.3 Barrier

Wait until all branches complete or fail. The barrier does not advance on partial completion.

5.4 Conflict Detection

At merge time, the Merge Agent (or the Production Orchestrator acting as merge) checks each output for:

- Reference conflicts — two branches reference the same PKG node with conflicting values.
- Type conflicts — two branches produce inconsistent typing for a shared node.
- Structural conflicts — two branches create edges that violate ontology cardinality after merge.
- Semantic conflicts — two branches assert contradictory facts (e.g. a character is both shy and outgoing in the same scene).

5.5 Conflict Resolution

Each conflict class has a resolution policy:

- Reference conflict — last-writer-wins is forbidden. The Merge Agent rewinds to the responsible branch and requests a re-execution with a constraint that the other branch's value is fixed.
- Type conflict — the ontology wins; the branch that violates the type must re-execute.
- Structural conflict — ontology cardinality wins; the offending branch re-executes.
- Semantic conflict — escalate to the Governance Agent. Semantic conflicts are not auto-resolved.

5.6 Commit

If no unresolved conflicts remain, merge all outputs into the live PKG atomically. Emit a merge event. If any conflict is unresolved, hold the merge and dispatch the Revision Agent.

6. Use Inside Genesis

- Stage 2 Creative Design — Story Architect, Character Manager, Environment Manager run in parallel.
- Stage 5 Production Execution — Image, Voice, Music, SFX generators run in parallel.
- Stage 7 Evaluation — seven evaluators run in parallel and merge into a combined evaluation report.
- Learning fan-out — multiple learning agents train on disjoint production corpora.

7. Worked Example

Stage 2 Creative Design:

Input snapshot: Production Brief, Research findings.
Branches:
- Story Architect → Narrative Subgraph
- Character Manager → Character Subgraph
- Environment Manager → World Subgraph

Independence check:
- Narrative Subgraph nodes: Act, Sequence, Scene, Beat. Character Subgraph nodes: Character, Persona, Core Fear. World Subgraph nodes: World, Environment, Location. No write overlap.

Dispatch all three concurrently. Wait at barrier. Merge:

- Each subgraph is disjoint — no reference conflicts.
- Cross-references (Scene references Character) are created only after merge by the Production Orchestrator using a post-merge link step.

If the Story Architect's Narrative Subgraph references a character that the Character Manager did not create, that is a post-merge reference conflict. The Production Orchestrator dispatches the Revision Agent to either create the missing character or remove the reference.

8. Anti-Patterns

- Letting branches write to the live PKG directly. Branches write to staging only.
- Advancing the barrier on partial completion. Barriers are all-or-nothing.
- Auto-resolving semantic conflicts. They require governance.
- Skipping the independence check. Hidden dependencies produce inconsistent merges.
- Reading another branch's in-flight output. Use the snapshot.
- Fan-out without a documented merge specification.

9. Exit Criteria

A parallel fan-out is complete when:

- All branches have completed or explicitly failed.
- The barrier has been satisfied.
- Conflicts have been detected, classified, and resolved.
- The merged PKG update is committed atomically.
- A merge event with branch identifiers and conflict resolutions is recorded in the PKG.