Genesis Pattern (GP)
GP-GOV-002 — Escalation Pattern

Document ID: GP-GOV-002
Title: Escalation Pattern
Version: 1.0.0
Status: Pattern
Authority: Derived from GFS-000, GFS-009, GO-001

1. Purpose

The Escalation Pattern defines how Genesis raises a decision to a higher authority when the current level cannot resolve it. Escalation is the safety valve of the approval chain (GP-GOV-001): when an approver cannot decide, when SLA is breached, when a conflict spans multiple concerns, or when a defect exceeds the current agent's scope, the matter is escalated to a named higher authority with a typed escalation record.

In Genesis, escalation is never implicit. An agent that "feels stuck" does not escalate by default — it emits a typed Escalation Request that the Production Orchestrator or the Governance Agent routes. Escalation is a knowledge artifact, not an exception.

2. When to Apply

Apply this pattern when:

- An approver in an approval chain cannot reach a verdict within their declared scope.
- An SLA on an approval link is breached and the link has not responded.
- A semantic conflict in a parallel merge (see GP-WF-002) requires human or governance judgment.
- A defect detected by validation exceeds the responsible agent's scope and requires a higher agent's input.
- A constitutional question arises that the current level cannot answer.
- A production readiness certification has an unresolved Weak element that governance must accept or reject.

Do not apply this pattern for routine failures that the Revision Agent can handle — escalation is for matters that exceed the normal revision loop.

3. Escalation Levels

Genesis defines four escalation levels:

- L1 — Responsible Agent. The agent that produced the defect. Default target for revision.
- L2 — Domain Owner. The agent that owns the ontology domain (e.g. Character Manager owns GO-104).
- L3 — Governance Agent. Owns constitutional compliance and approval chains.
- L4 — Chief Architect (human). Final authority for constitutional questions and unresolvable semantic conflicts.

Escalation always moves upward. An L1 matter may be escalated to L2, then L3, then L4. Skipping levels requires a stated reason; downward escalation (de-escalation) is forbidden — once a matter is at L3, it cannot return to L1 except through a fresh revision dispatch.

4. Escalation Record

Every escalation is recorded as:

- Escalation ID — stable identifier.
- Escalation Level — L1 / L2 / L3 / L4.
- Subject — the PKG node or decision the escalation concerns.
- Reason — typed from the Escalation Reason Catalog (see §5).
- Originating agent — the agent that emitted the escalation.
- Target authority — the role that receives the escalation.
- Evidence — links to Decision Records, Validation Reports, or prior Approval Records.
- Confidence — the originating agent's confidence in the need to escalate.
- Trace ID — propagated from the originating workflow.
- SLA — the maximum time the target has before further escalation.

Escalations without a typed reason are invalid. Escalations without evidence are treated as assertions.

5. Escalation Reason Catalog

Registered reasons include:

- SLA Breach — an approval link has not responded within its SLA.
- Scope Exceedance — the matter exceeds the current approver's declared scope.
- Unresolvable Conflict — a semantic conflict that auto-resolution cannot handle (see GP-WF-002 §5.5).
- Constitutional Question — a question that requires Charter interpretation.
- Insufficient Evidence — the current level lacks the evidence to decide.
- Confidence Below Threshold — an abductive conclusion's margin is at threshold and disambiguation is required.
- Repeated Revision Failure — the same defect has been revised N times without resolution.
- Waiver Request — a required element cannot be satisfied and governance acceptance is requested.

New reasons are added through the same governance process as ontologies.

6. Workflow

6.1 Detect the Trigger

The originating agent detects an escalation trigger — an SLA breach, a scope exceedance, an unresolvable conflict, or any other registered reason.

6.2 Emit Escalation Request

The agent emits an Escalation Request with the typed reason, evidence, and target authority. The Production Orchestrator (or the Governance Agent if L3+) receives the request.

6.3 Route to Target

The router dispatches the request to the named target authority. The target receives the request with full provenance.

6.4 Target Decision

The target authority records a verdict:

- Resolve — the target decides the matter and emits a Decision Record. The originating workflow resumes.
- Reject — the target declines to decide; the request is escalated to the next level.
- Defer — the target requests more evidence. The originating agent is dispatched to gather it; the SLA clock pauses.

6.5 SLA Enforcement

If the target does not respond within the SLA, the router auto-escalates to the next level and emits an SLA Breach event.

6.6 Audit

Every escalation and its resolution is recorded in the PKG. The Governance Agent can reconstruct any escalation chain by walking the escalation records backward.

7. Use Inside Genesis

- A semantic conflict in Stage 2 merge that auto-resolution cannot handle is escalated to L3 (Governance Agent).
- An ontology publication approval that breaches SLA is escalated from L2 (Ontology Owner) to L3 (Governance Agent).
- A character Core Fear that the Character Manager cannot derive with confidence above threshold is escalated to L2 (Domain Owner — Character) for guidance, not L1.
- A production readiness waiver request is escalated to L3 (Governance Agent) for acceptance or rejection.
- A constitutional question about whether a devotional production may waive the antagonist requirement is escalated to L4 (Chief Architect).

8. Worked Example

Stage 2 merge conflict:

- Story Architect asserts the protagonist's Core Fear is "Loss of mentor."
- Character Manager asserts the protagonist's Core Fear is "Fear of unworthiness."

Auto-resolution: semantic conflict. Both values are Explicit, high-confidence. Neither can be auto-resolved.

Escalation Request emitted:
- Level: L3.
- Reason: Unresolvable Conflict.
- Subject: Protagonist Core Fear.
- Evidence: Decision Records D-2207 (Story Architect), D-2210 (Character Manager).
- Target authority: Governance Agent.
- SLA: 4 hours.

Governance Agent verdict: Request Changes to Story Architect — the Character Subgraph is the canonical owner of Core Fear. The Story Architect must align its Narrative Subgraph to the Character Subgraph's value.

Decision Record committed. Originating workflow resumes from the merge step.

9. Anti-Patterns

- Escalating without a typed reason — escalations are knowledge artifacts.
- Escalating without evidence — the target cannot decide in a vacuum.
- Skipping levels without a stated reason — level skipping is exceptional.
- De-escalating from L3 to L1 — escalation is monotonic upward.
- Auto-resolving a matter that should be escalated — unresolvable conflicts must not be silently merged.
- Treating escalation as failure — escalation is the system working as designed.
- Letting the originating agent choose the target — the router chooses, not the originator.

10. Exit Criteria

An escalation is complete when:

- The Escalation Request is committed with a typed reason and evidence.
- The target authority has been routed to.
- The target has recorded a verdict (Resolve / Reject / Defer).
- For Resolve, a Decision Record is committed and the originating workflow resumes.
- For Reject, the request is escalated to the next level with the prior verdict as evidence.
- For Defer, evidence-gathering is dispatched and the SLA clock is paused.
- The escalation chain is fully recorded in the PKG audit log.