Genesis Workflow Specification (GWS)
GWS-012 — Governance Workflow

Document ID: GWS-012
Title: Governance Workflow
Version: 1.0.0
Status: Workflow Specification
Authority: Derived from GFS-000, GFS-007

1. Purpose

This workflow defines how governance decisions are made in the Genesis Engine. It covers proposals, reviews, approvals, amendments, waivers, and escalations. Governance is the mechanism by which the constitutional hierarchy is maintained and by which the engine evolves without violating its own principles.

2. Scope

Governance applies to:
- Constitutional documents (GFS-NNN).
- Ontology documents (GO-NNN).
- Specification documents (GSPEC-NNN).
- Workflow documents (GWS-NNN).
- Schema documents (GSS-NNN).
- Agent specifications (GAS-NNN).
- Reference documents (GREF-NNN) where they declare binding standards.
- Individual production decisions escalated by the Governance Agent.

3. Roles

- Proposer — Any agent or human who submits a proposal.
- Reviewer — A constitutional reviewer agent or designated human reviewer.
- Approver — The Governance Agent, or a human governor for constitutional amendments.
- Archivist — The Documentation Publisher Agent, which records decisions in the audit trail.

4. Proposal Lifecycle

4.1 Stage G0: Proposal Submission

Actor: Proposer
Input: Proposal document
Output: Proposal record

A proposal contains:
- Proposal ID.
- Target document and proposed change.
- Rationale (why the change reduces ambiguity or improves consistency).
- Affected documents (downstream impact).
- Risk classification (low, medium, high, constitutional).

4.2 Stage G1: Triage

Actor: Governance Agent
Input: Proposal record
Output: Triage decision

The Governance Agent categorizes the proposal:
- Editorial — typo, formatting, wording clarification. Low risk.
- Substantive — semantic change to a non-constitutional document. Medium risk.
- Structural — change to an ontology, schema, or workflow affecting downstream documents. High risk.
- Constitutional — change to a GFS-NNN document. Highest risk.

Editorial proposals may be approved at this stage. All others proceed to review.

4.3 Stage G2: Review

Actor: Reviewer(s)
Input: Triage decision, proposal
Output: Review report

The number of reviewers scales with risk:
- Substantive: one reviewer.
- Structural: two reviewers from different domains.
- Constitutional: three reviewers including at least one human governor.

Reviewers assess:
- Conformance with the Constitutional Charter.
- Downstream impact on other documents.
- Backward compatibility with existing PKGs.
- Test coverage for the change.

Reviewers may request changes. The proposer revises and resubmits; review restarts.

4.4 Stage G3: Approval

Actor: Approver
Input: Review report
Output: Approval decision

- Substantive: Governance Agent may approve.
- Structural: Governance Agent approves after both reviewers sign off.
- Constitutional: Human governor required. The Charter (GFS-000) requires unanimous governor approval for amendments to itself.

Approval is recorded with: approver identity, timestamp, conditions, and effective version.

4.5 Stage G4: Amendment

Actor: Archivist
Input: Approval decision
Output: Amended document, version bump

The Documentation Publisher Agent:
- Applies the change to the target document.
- Bumps the document version per the versioning policy.
- Updates the registry digest.
- Writes an ADR (GDEC-NNN) capturing the decision.
- Notifies downstream document owners to re-validate their documents.

4.6 Stage G5: Propagation

Actor: Genesis Compiler
Input: Amended document
Output: Compiled artifacts

The compiler recompiles any schemas, ontologies, or workflows affected by the amendment. Compilation failure rolls back the amendment and returns the proposal to Stage G3.

4.7 Stage G6: Closure

Actor: Archivist
Input: Propagation result
Output: Closed proposal

The proposal is marked closed. The audit trail is updated. If the amendment affected existing PKGs, those PKGs are flagged for migration review.

5. Waivers

A waiver is an approved exception to a constitutional rule for a specific production. It does not amend the constitution.

- A waiver is proposed by the Production Orchestrator Agent when a production cannot proceed without violating a rule.
- A waiver is reviewed and approved by the Governance Agent.
- A waiver applies to exactly one production session.
- A waiver does not set precedent. Repeated waiver requests for the same rule trigger a structural proposal to amend the rule.

6. Escalations

An escalation routes an unrecoverable issue from a runtime agent to the Governance Agent.

- Escalations are submitted with full provenance of the failing decision.
- The Governance Agent may resolve by waiver, by revision request, or by terminating the session.
- Escalations that reveal a constitutional defect are converted into proposals.

7. Versioning Policy

- Editorial change: patch version bump (1.0.0 → 1.0.1).
- Substantive change: minor version bump (1.0.0 → 1.1.0).
- Structural change: minor or major version bump depending on backward compatibility.
- Constitutional change: always a major version bump for the affected GFS document.

8. Conflict Resolution

- If a proposal conflicts with the Constitutional Charter, the Charter prevails and the proposal is rejected.
- If two proposals conflict, the earlier-submitted proposal is reviewed first; the later proposal must reconcile with the first.
- If a runtime decision conflicts with a specification, the specification prevails unless a waiver is granted.

9. Auditability

Every governance decision is recorded in an immutable audit trail:
- Proposal record.
- Triage decision.
- Review reports.
- Approval decision.
- Amendment record.
- Propagation result.
- Closure record.

The audit trail is part of the PKP for any production affected by the decision.

10. Cross-References

- GFS-000 — Constitutional Charter (section 17: Constitutional Hierarchy)
- GFS-007 — Governance Constitution
- GDEC-NNN — Architecture Decision Records
- GWS-010 — Publication Workflow
- GWS-011 — Deployment Workflow