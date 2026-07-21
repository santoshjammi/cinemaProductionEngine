Genesis Architecture Decision Record (ADR)

ADR-NNN — <Decision Title>

Document ID: ADR-NNN
Title: <Decision Title>
Version: 1.0.0
Status: <Proposed | Accepted | Superseded | Deprecated>
Authority: Derived from GFS-000 Constitutional Charter and GFS-006 Governance Constitution

Date: <YYYY-MM-DD>
Decision Maker: <Role or Body>
Reviewer: <Role or Body>
Supersedes: <ADR-IDs or none>
Superseded By: <ADR-IDs or none>
Related Documents: <IDs of related ADRs, constitutions, ontologies, or specifications>

1. Context

Describe the problem space that demanded a decision. This section must answer:

- What force or situation gave rise to this decision?
- What constraints were in effect at the time?
- What prior decisions, if any, shaped the context?
- What would happen if no decision were made?

The Context section must be self-contained. A reader who has not read the rest of the repository should understand the problem from this section alone. Cite relevant constitutional principles, ontology concepts, and prior ADRs by ID.

Do not include the decision in this section. Context is only the situation, not the resolution.

2. Decision

State the decision clearly and unambiguously in a single paragraph at the top of this section. Then elaborate.

The decision statement must be:
- Specific enough to be implemented without further clarification
- General enough to outlive a single implementation
- Aligned with the constitutional principles in GFS-000

The elaboration must cover:
- What was chosen
- What was explicitly rejected
- The scope of the decision (what it governs and what it does not)
- The entity or body that owns the decision going forward

If the decision introduces new vocabulary, define the terms here and reference the ontology concepts they derive from.

3. Status

Record the current lifecycle state of this ADR.

Allowed states:
- Proposed — drafted, not yet reviewed
- Accepted — reviewed and approved by the governing body
- Superseded — replaced by a later ADR (reference the replacing ADR)
- Deprecated — no longer in force but retained for historical context
- Rejected — considered and not adopted (retained for the record)

When the status changes, update this section, the Date, and the Superseded By field as appropriate. Do not delete prior states; append a state-change record with date and authority.

4. Consequences

Describe what the decision produces, both positive and negative.

4.1 Positive Consequences
List the benefits the decision creates. Be specific: name the subsystems, agents, workflows, or properties improved. Avoid vague claims such as "better" or "cleaner." State exactly what becomes possible that was not possible before, and what becomes simpler, faster, safer, or more auditable.

4.2 Negative Consequences
List the costs, constraints, or risks introduced by the decision. No decision is free. Honest enumeration of negative consequences is required for the ADR to be trustworthy. Cover:
- New complexity added
- New invariants that must be defended
- Performance or operational costs
- Migration burden
- Risks if the decision is later violated

4.3 Neutral Consequences
List side effects that are neither positive nor negative but must be acknowledged because they shape future decisions. Examples: new vocabulary that future ADRs must use, new boundaries that future features must respect, new dependencies that future work must carry.

5. Alternatives

Enumerate the alternatives that were considered and rejected. For each alternative, record:

5.N Alternative N: <Name>
- Description: One paragraph summary of the alternative
- Advantages: What it offered
- Disadvantages: Why it was rejected
- Rejection Rationale: The specific reason it was not chosen

At least two alternatives must be recorded. A decision made without considered alternatives is not a decision; it is a default. If only one option was available, state that explicitly and explain why no alternatives existed.

Do not strawman alternatives. Present them fairly. The value of this section is to prevent the same rejected alternative from being re-proposed in the future without new context.

6. Compliance

Describe how compliance with this decision is verified and maintained.

6.1 Validation Rules
List the concrete rules that the Validation Engine (S3 per GARCH-002) enforces to ensure this decision is respected. Rules should be expressed as invariants over the PKG, the agent registry, the workflow definitions, or the materialized views.

Example:
- "No node of type MediaAsset may exist in the PKG."
- "Every node must carry a confidence value drawn from the five-level enumeration."
- "Every workflow must declare its baseline as GWS-001 or a derivative."

6.2 Governance Gates
List the governance gates (per S4) that enforce this decision. Identify which approval must be granted before a change consistent with this ADR may proceed, and which approval must be granted before a change that would violate this ADR may even be considered.

6.3 Audit Checks
List the audit queries that should surface violations. These are queries against the Provenance Ledger or the PKG that detect drift from the decision.

6.4 Amendment Process
Describe how this decision may be revised. Most ADRs are amended only by superseding ADRs approved through the Governance Constitution. State explicitly whether this ADR may be amended in place or only by supersession.

7. References

List the IDs of all documents this ADR depends on, contradicts, or influences. Include:
- Constitutional Charters and Constitutions (GFS-NNN)
- Ontology documents (GO-NNN)
- Architecture documents (GARCH-NNN)
- Agent specifications (GAS-NNN)
- Workflow specifications (GWS-NNN)
- Other ADRs (ADR-NNN)

8. Notes

Optional section for any additional commentary that does not fit the structured sections above. Use this section sparingly. Structured sections are preferred because they are machine-queryable; free-form notes are not.

9. Sign-off

| Role | Name | Date | Signature |
|------|------|------|----------|
| Decision Maker | | | |
| Reviewer | | | |
| Governance Agent | | | |

A signed ADR is part of the Provenance Ledger. Unsigned ADRs are advisory only.