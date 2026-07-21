Genesis Pattern (GP)
GP-WF-001 — Sequential Workflow Pattern

Document ID: GP-WF-001
Title: Sequential Workflow Pattern
Version: 1.0.0
Status: Pattern
Authority: Derived from GFS-005 Agent Constitution, GWS-001

1. Purpose

The Sequential Workflow Pattern defines how Genesis agents run in strict order, where each agent depends on the complete output of its predecessor. Sequential execution is the simplest orchestration form: it is deterministic, auditable, and easy to reason about. It is the default for creative production stages where one agent's output materially shapes the next agent's input.

In Genesis, sequential workflows are used when an upstream decision constrains a downstream decision so strongly that parallel execution would produce wasted work or contradictory results.

2. When to Apply

Apply this pattern when:

- A downstream agent's reasoning depends on the full output of an upstream agent (e.g. Screenplay Writer depends on the Story Architect's complete Narrative Subgraph).
- A validation must complete before the next creative step may begin.
- A revision loop must fully resolve before the production advances.
- A governance approval is required before downstream agents may start.

Do not apply this pattern when agents are independent (use Parallel Fan-Out, GP-WF-002) or when the next agent depends on a condition rather than a strict predecessor (use Conditional Routing, GP-WF-003).

3. Structure

A sequential workflow is modeled as an ordered list of agent invocations:

Stage i → Stage i+1 → Stage i+2 → ... → Stage n

Each stage declares:

- Agent ID (GAS-NNN)
- Input contract — exactly the union of upstream outputs required.
- Output contract — the typed PKG subgraph or artifact produced.
- Entry condition — must include the predecessor's completion signal.
- Exit condition — the output contract is satisfied and validation passes.

The workflow specification commits the order in a Workflow Manifest; runtime reordering is forbidden.

4. Execution Rules

- Strict ordering — stage i+1 may not start before stage i emits its completion signal.
- Monotonic progress — the PKG may only gain knowledge during a sequential workflow; agents may not delete prior stages' outputs without a Revision Agent dispatch.
- Failure propagation — a failure in stage i blocks stage i+1. The Production Orchestrator Agent decides between retry, fallback, or escalation.
- Validation gate — each stage's output must pass the Structural Validation Pattern (GP-VAL-001) before the next stage begins.
- Checkpoint — each stage boundary is a checkpoint. If the session restarts, execution resumes from the last completed stage.

5. Workflow

5.1 Manifest Declaration

The Production Orchestrator Agent declares the ordered stages with their agent IDs, input contracts, and output contracts. The manifest is committed to the PKG before execution begins.

5.2 Stage Execution

For each stage in order:

1. Verify entry condition (predecessor completion signal present, PKG valid).
2. Invoke the agent with its declared inputs.
3. Capture the agent's output and merge into the PKG.
4. Run structural validation on the merged result.
5. If validation fails: dispatch the Revision Agent, do not advance.
6. If validation passes: emit the stage completion signal.

5.3 Stage Failure Handling

- If the agent errors: Production Orchestrator decides to retry (same stage), fall back (alternative agent), or escalate (Governance Agent). The next stage never starts until the failure resolves.
- If validation fails: Revision Agent identifies the responsible upstream agent. If the failure is the current stage's, retry. If the failure is upstream, rewind to the responsible stage and re-execute downstream stages from there.

5.4 Completion

The workflow is complete when the final stage emits its completion signal and the PKG passes final validation. The Production Orchestrator emits a workflow completion event.

6. Use Inside Genesis

- Creative Production stage (Psychology Reviewer → Screenplay Writer → Dialogue Writer) — the screenplay cannot begin until psychology validation completes, and dialogue cannot begin until the screenplay exists.
- Production Planning stage (Scene Planner → Shot Planner → Music Composer → Prompt Builder) — each planner builds on its predecessor's plan.
- Post-Production stage (Audio Mixing → Subtitle → Video Composer) — each step consumes the previous step's artifact.
- Certification stage (Governance Agent review → Production Readiness Certificate) — strictly last.

7. Worked Example

Stage 3 of the Full Production Workflow (GWS-001):

Stage 3.1: Psychology Reviewer Agent
  Input: Narrative Subgraph, Character Subgraph
  Output: Psychological Validation Report
  Entry: Stage 2 complete.

Stage 3.2: Screenplay Writer Agent
  Input: Narrative Subgraph, Character Subgraph, Validation Report
  Output: Screenplay Document
  Entry: Stage 3.1 complete and Validation Report has no critical issues.

Stage 3.3: Dialogue Writer Agent
  Input: Screenplay Document, Character Subgraph
  Output: Dialogue Script
  Entry: Stage 3.2 complete.

If Stage 3.1 reports critical issues, Stage 3.2 is blocked. The Revision Agent rewinds to the Story Architect Agent (Stage 2) and re-executes from there.

8. Anti-Patterns

- Starting the next stage before validation of the prior stage passes.
- Letting downstream agents read partial outputs of an upstream agent.
- Reordering stages at runtime.
- Skipping the checkpoint between stages.
- Treating a failure as a warning and continuing — sequential workflows require hard gates.

9. Exit Criteria

A sequential workflow is complete when:

- Every stage has executed in order.
- Every stage boundary has a committed checkpoint.
- Every stage output passed structural validation.
- The final stage emitted its completion signal.
- The Production Orchestrator recorded the workflow completion event in the PKG.