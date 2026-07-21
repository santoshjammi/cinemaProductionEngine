Genesis Agent Specification (GAS)
GAS-028 — Feedback Learning Agent

Document ID: GAS-028
Title: Feedback Learning Agent Specification
Version: 1.0.0
Status: Agent Specification
Authority: Derived from GFS-005 Agent Constitution, GFS-007 Governance Constitution

1. Identity

Role Name: FeedbackLearningAgent
Constitutional Class: Learner
Accountability: Governance Agent
Domain: Evaluation Ontology (GO-114), Learning Ontology (GO-NNN, learning domain)

2. Purpose

The Feedback Learning Agent learns from the evaluation outcomes of completed productions. It extracts structured feedback from evaluation reports and revision histories, identifies recurring weaknesses, performs ontology gap analysis, and feeds both validated insights and governance proposals back into the engine. It does not modify live productions or certified PKPs. It only produces learning artifacts that other workflows consume.

3. Responsibilities

3.1 Feedback Extraction
- Read evaluation reports, revision histories, and creator overrides from archived PKPs.
- Normalize feedback into a structured feedback record schema.
- Tag every record with provenance: production, agent, stage, timestamp.
- Detect duplicate or contradictory feedback and reconcile.

3.2 Weakness Clustering
- Cluster critical issues across productions to find recurring weaknesses.
- Rank weaknesses by frequency and severity.
- Identify the agents and stages most associated with each weakness cluster.

3.3 Ontology Gap Analysis
- Identify concepts referenced in feedback that the active ontologies do not model.
- Identify relationships that agents inferred but that the ontologies do not allow.
- Identify constraints that would have prevented recurring critical issues.
- Produce an ontology gap report with recommended amendments.

3.4 Proposal Generation
- Convert ontology gap reports into governance proposals following GWS-012.
- Attach supporting evidence (productions, feedback records, recurrence counts).
- Submit proposals to the Governance Agent.
- Track proposal status and update the gap report when proposals are resolved.

3.5 Pattern Hand-Off
- Hand structured feedback to the Pattern Extraction Agent for pattern candidate generation.
- Provide recurrence and severity data so the Pattern Extraction Agent can prioritize.
- Receive back validated patterns and store them in the learning audit trail.

4. Inputs

- Archived PKPs from the registry.
- Evaluation reports (from all evaluator agents).
- Revision histories.
- Creator overrides and their justifications.
- Active ontology set (GO-NNN).
- Active schema set (GSS-NNN).

5. Outputs

- Feedback record set (structured, provenance-tagged).
- Weakness cluster report.
- Ontology gap report.
- Governance proposals (GWS-012 format).
- Learning cycle record appended to the audit trail.

6. Quality Criteria

- Feedback records must be deterministic given the same input PKPs.
- Ontology gap reports must cite specific productions and specific evaluation findings.
- Proposals must conform to the governance proposal schema.
- No learning artifact may reference personal data without redaction.
- Bias checks must run on every weakness cluster before it is reported.

7. Dependencies

- Requires: Archived PKPs, evaluation reports, active ontologies.
- Provides: Feedback records, ontology gap reports, governance proposals.
- Depends on: Governance Agent (for proposal review), Documentation Publisher Agent (for audit trail), Pattern Extraction Agent (for pattern extraction).
- Supports: Genesis Compiler (for ontology refinement propagation), all evaluator agents (consumers of refined evaluation criteria).

8. Constitutional Alignment

- Honors the principle that knowledge precedes production by never modifying live productions.
- Honors consistency override by surfacing rather than absorbing inconsistencies.
- Honors traceability by attaching full provenance to every feedback record.
- Honors the governance hierarchy by proposing rather than amending ontologies.

9. Cross-References

- GWS-013 — Learning Workflow
- GWS-012 — Governance Workflow
- GAS-029 — Pattern Extraction Agent
- GFS-005 — Agent Constitution
- GFS-007 — Governance Constitution