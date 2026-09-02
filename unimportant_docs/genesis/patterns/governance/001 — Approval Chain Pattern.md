Genesis Pattern (GP)
GP-GOV-001 — Approval Chain Pattern

Document ID: GP-GOV-001
Title: Approval Chain Pattern
Version: 1.0.0
Status: Pattern
Authority: Derived from GFS-000, GFS-009, GO-001

1. Purpose

The Approval Chain Pattern defines how Genesis decisions are authorized before they take effect. An approval chain is an ordered list of approvers, each with a defined scope, who must sign off in sequence before a decision is committed. Without a complete approval chain, a decision is a proposal, not a decision.

In Genesis, approval is constitutional (Charter, Eighth Principle). Every significant decision — ontology publication, agent registration, production readiness, revision acceptance — must be traceable to a complete approval chain. A decision with a broken chain is constitutionally invalid and may not be referenced downstream.

2. When to Apply

Apply this pattern when:

- An ontology is being promoted from Validated to Published.
- An agent is being registered in the Agent Registry.
- A workflow is being committed to the Workflow Registry.
- A production is being certified for readiness.
- A revision is being accepted as the resolution of a defect.
- A constitutional amendment is being proposed.

Do not apply this pattern for routine agent invocations within a workflow — those are governed by the workflow's own gates, not by an approval chain.

3. Chain Structure

An approval chain is an ordered list:

    Proposal → Approver 1 → Approver 2 → ... → Approver N → Decision

Each link declares:

- Approver — a role (not a person): Core Reviewer, Ontology Owner, Governance Agent, Chief Architect.
- Scope — what the approver is approving (technical correctness, semantic consistency, constitutional compliance, business readiness).
- Required — whether the link is mandatory or optional.
- Condition — when the link is invoked (e.g. "always" vs. "only for MAJOR bumps").
- SLA — the maximum time the approver has before escalation (see GP-GOV-002).

The chain is fixed at declaration time. Runtime addition or removal of approvers is forbidden.

4. Approval Lifecycle

A decision moves through:

    Proposed → In Review → Approved (all links) → Committed

Or:

    Proposed → In Review → Rejected (any link) → Returned

- Proposed — the proposal is committed to the PKG with the chain declared.
- In Review — each approver in order receives the proposal and records a verdict (Approve / Reject / Request Changes).
- Approved — every mandatory link has approved. The decision is committed.
- Returned — any link rejected. The proposal is returned to the proposer with the rejecting link's reason.

A Request Changes verdict is not a reject — it returns the proposal to the proposer for revision and restarts the chain.

5. Workflow

5.1 Declare the Chain

The proposer commits the proposal with the chain declaration. The chain is drawn from a registered Chain Template (see §6) — ad-hoc chains are forbidden.

5.2 Dispatch to First Approver

The first approver receives the proposal. The approver evaluates only their declared scope — an approver may not approve outside their scope.

5.3 Record Verdict

The approver records a verdict with: approver role, scope evaluated, verdict, reason (for reject or request changes), and provenance to the evidence they used.

5.4 Advance or Return

If approved, the proposal advances to the next link. If rejected, the proposal is returned. If request changes, the proposal returns to the proposer.

5.5 Commit

When the final mandatory link approves, the decision is committed. An Approval Record is created with: the chain, each link's verdict, the final decision, and a stable Decision ID.

6. Chain Templates

Registered chain templates include:

- Ontology Publication — Core Reviewer → Ontology Owner → Governance Agent.
- Agent Registration — Agent Owner → Core Reviewer → Governance Agent.
- Workflow Publication — Workflow Owner → Production Orchestrator → Governance Agent.
- Production Readiness — Structural Validator → Semantic Validator → Completeness Validator → Governance Agent → Chief Architect.
- Revision Acceptance — Responsible Agent → Validator (for the failing layer) → Governance Agent.
- Constitutional Amendment — Chief Architect → Governance Agent → Founder (human).

New templates are added through the same governance process as ontologies.

7. Use Inside Genesis

- GO-104 Character Ontology v1.3.0 publication uses the Ontology Publication chain.
- GAS-008 Music Composer Agent registration uses the Agent Registration chain.
- Production readiness certification for production P-0421 uses the Production Readiness chain.
- A revision to fix Arjuna's missing Core Fear uses the Revision Acceptance chain.

8. Worked Example

Production P-0421 readiness certification:

Chain: Structural Validator → Semantic Validator → Completeness Validator → Governance Agent → Chief Architect.

- Structural Validator: Approve (all SHACL shapes pass).
- Semantic Validator: Approve (coherence score 0.91, no Errors).
- Completeness Validator: Request Changes (Antagonist missing).
- Proposal returned. Character Manager Agent dispatched; Antagonist added.
- Chain restarts.
- Structural Validator: Approve.
- Semantic Validator: Approve.
- Completeness Validator: Approve (all dimensions complete).
- Governance Agent: Approve.
- Chief Architect: Approve.

Decision committed: Production Readiness Certificate P-0421-CERT issued.

9. Anti-Patterns

- Skipping a mandatory link under time pressure.
- Letting an approver approve outside their declared scope.
- Reordering the chain at runtime.
- Using an ad-hoc chain not drawn from a registered template.
- Treating Request Changes as a silent reject — it must be explicit.
- Committing a decision without a complete Approval Record.
- Allowing the proposer to be an approver in their own chain.

10. Exit Criteria

An approval chain is complete when:

- The chain is drawn from a registered template.
- Every mandatory link has recorded a verdict with provenance.
- Every verdict is Approve.
- The Approval Record is committed with a stable Decision ID.
- The decision is committed to the PKG.