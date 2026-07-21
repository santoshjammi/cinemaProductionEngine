Genesis Knowledge Reference (GKR)
GKR-002 — Taxonomy Catalog

Document ID: GKR-002
Title: Taxonomy Catalog
Version: 1.0.0
Status: Foundational Knowledge Reference
Authority: Derived from GFS-000, GO-001, GO-003, GFS-005, GFS-006

1. Purpose

This catalog lists every taxonomy used inside Genesis. A taxonomy is a
controlled, finite vocabulary for a single dimension. Every taxonomy is
canonical: agents, validators, and workflows must use these terms
exactly. Introducing a new value in a taxonomy requires a constitutional
amendment or an ontology evolution step (GMM-002).

2. Taxonomy Index

- T-001 Confidence Levels
- T-002 Agent Roles (Constitutional Classes)
- T-003 Production States
- T-004 Readiness Levels
- T-005 Error Categories
- T-006 Knowledge Provenance Sources
- T-007 Concept Lifecycle States
- T-008 Document Statuses
- T-009 Validation Outcomes
- T-010 Defect Severities

3. T-001 Confidence Levels

Used on every node and edge in the PKG (GFS-000 §10, GFS-010 §3).

| Value | Meaning |
|-------|---------|
| EXPLICIT | Stated in the source material or by the creator. |
| INFERRED | Derived by an agent from PKG evidence. |
| CONFIRMED | Validated by a validator agent or by the creator. |
| ASSUMED | Adopted without evidence; flagged for review. |
| UNKNOWN | Gap detected; the discovery loop must resolve this. |

Rule: a PKG may not be certified while any critical-path node carries
UNKNOWN. ASSUMED must be resolved to CONFIRMED or INFERRED before
certification.

4. T-002 Agent Roles (Constitutional Classes)

Used in every agent spec (GFS-005).

| Value | Responsibility |
|-------|----------------|
| Orchestrator | Top-level coordinator; dispatches other agents. |
| Architect | Designs specifications from knowledge. |
| Engineer | Generates artifacts from specifications. |
| Validator | Scores outputs against specifications. |
| Reviewer | Reviews creative or psychological quality. |
| Researcher | Gathers external knowledge. |
| Governance | Manages canonical subgraphs and policy. |
| Learning | Updates registries and models from outcomes. |
| Publisher | Prepares materialized views for handoff. |
| Shared | Cross-cutting role used by multiple phases. |

5. T-003 Production States

Used by the lifecycle state machine (GO-003, GD-004).

| Value | Meaning |
|-------|---------|
| initiated | Brief received; no work begun. |
| discovering | Agents extracting and inferring knowledge. |
| designing | Architects producing specifications. |
| producing | Engineers generating artifacts. |
| evaluating | Validators scoring outputs. |
| certifying | Governance reviewing and signing off. |
| ready | PKP sealed; handoff to Studio Engine. |
| failed | Unrecoverable defect or veto; terminal. |

6. T-004 Readiness Levels

Used by the Production Readiness assessment (GFS-000 §14, GAS-023).

| Value | Meaning |
|-------|---------|
| NOT_READY | Mandatory subgraphs missing or critical UNKNOWN present. |
| PARTIAL | Subgraphs present but validators have not all passed. |
| CONDITIONAL | Validators pass with documented assumptions awaiting creator confirmation. |
| READY | All validators pass, governance signed, PKP sealed. |

7. T-005 Error Categories

Used by validators and the Revision Agent (GAS-027) to route repair work.

| Value | Meaning |
|-------|---------|
| STRUCTURAL | Missing node, dangling edge, schema violation. |
| SEMANTIC | Contradictory relationship, broken invariant. |
| COMPLETENESS | Required subgraph or node count not met. |
| CONFIDENCE | Critical path carries UNKNOWN or ASSUMED. |
| QUALITY | Validator score below threshold (creative quality). |
| CONSISTENCY | Cross-subgraph contradiction. |
| POLICY | Governance policy violation. |
| TIMEOUT | Agent did not return within budget. |
| UNRECOVERABLE | Repair budget exhausted; escalation required. |

8. T-006 Knowledge Provenance Sources

Used on the provenance field of every node and edge (GFS-010 §3).

| Value | Meaning |
|-------|---------|
| CREATOR | Stated by the human creator. |
| AGENT | Produced by a Genesis agent. |
| VALIDATOR | Confirmed by a validator agent. |
| GOVERNANCE | Confirmed by a governance agent. |
| IMPORTED | Imported from an external knowledge source. |
| DERIVED | Computed by a reasoning pass over the PKG. |

9. T-007 Concept Lifecycle States

Used for ontology concepts (GO-001 §20).

| Value | Meaning |
|-------|---------|
| Proposed | Drafted; not yet reviewed. |
| Reviewed | Reviewed by an architect; not yet validated. |
| Validated | Passed structural and semantic validation. |
| Approved | Approved by governance. |
| Published | Referenceable by other documents. |
| Deprecated | Superseded; remains for audit. |
| Archived | Removed from active use; retained for history. |

10. T-008 Document Statuses

Used in the header block of every document.

| Value | Meaning |
|-------|---------|
| Foundational | Constitution-tier document. |
| Core Ontology | GO-001 only. |
| Agent Specification | Agent spec (GAS). |
| Foundational Standard | Derived GFS spec. |
| Specification | GSPEC document. |
| Workflow | GWS document. |
| Guide | GDE document. |
| Reference Diagram | GD document. |
| Reference | GREF document. |
| Template | GTMP document. |
| Draft | Work in progress; not referenceable. |
| Deprecated | Superseded; retained for audit. |

11. T-009 Validation Outcomes

Used by validators in their reports.

| Value | Meaning |
|-------|---------|
| PASS | Output meets the specification. |
| PASS_WITH_NOTES | Output meets the spec; minor notes recorded. |
| CONDITIONAL_PASS | Output meets the spec only under stated assumptions. |
| FAIL | Output does not meet the spec; repairable. |
| HARD_FAIL | Output does not meet the spec; not repairable within budget. |
| BLOCKED | Validator could not run; missing input. |

12. T-010 Defect Severities

Used by validators and the Revision Agent to prioritize repair.

| Value | Meaning |
|-------|---------|
| INFO | Cosmetic; does not affect certification. |
| MINOR | Affects quality; does not block certification. |
| MAJOR | Affects a subgraph; blocks certification until fixed. |
| CRITICAL | Breaks an invariant; blocks certification; high-priority repair. |
| BLOCKER | Breaks a constitutional invariant; may force failed state. |

13. Using the Catalog

- Every agent spec, validator report, and workflow document must use
  the values in this catalog verbatim.
- A new taxonomy value is introduced via the Ontology Evolution
  Framework (GMM-002) and registered here.
- The catalog is the single source of truth for controlled vocabularies.
  The Vocabulary Registry (GKR-003) covers domain terms; this catalog
  covers the structural taxonomies.