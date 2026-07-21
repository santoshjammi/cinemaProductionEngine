Genesis Master Specification
02 — Constitution

Document ID: GMS-002
Title: Genesis Master Specification — Constitution Summary
Version: 1.0.0
Status: Master Specification
Authority: Derived from GFS-000 through GFS-009

1. Purpose

This document consolidates the ten Genesis Foundational Standards (GFS-000 through GFS-009) into a single reference. It is the quick-reference constitution for any agent, engineer, or reviewer who needs to know what Genesis is permitted and forbidden to do.

For the full text of each standard, see `constitutions/`.

2. Constitutional Hierarchy

The Constitutional Charter (GFS-000) is the supreme authority. Every other document — ontologies, specifications, workflows, agents, implementations — must conform to it. If a lower-level document conflicts with the Charter, the Charter prevails.

The remaining GFS standards (GFS-001..009) derive from the Charter and govern specific domains. They may not override the Charter.

3. GFS-000 — Constitutional Charter

Purpose: Define the value system, invariants, and supreme authority of Genesis.
Scope: All of Genesis and every downstream consumer.
Key principles:
- Genesis is the Pre-Production Intelligence System of Movie OS.
- Genesis produces knowledge, not media.
- Knowledge precedes production.
- The PKG is canonical.
- Constitutional supremacy outranks engineering convenience.
- Every assertion carries confidence and provenance.
- No subsystem outside Genesis may write to the PKG.

4. GFS-001 — Identity Constitution

Purpose: Define what Genesis is and is not.
Scope: System identity, boundaries, naming.
Key principles:
- Genesis is a reasoning system, not a generator.
- Genesis is medium-agnostic.
- Genesis is provider-agnostic.
- Genesis is implementation-agnostic.

5. GFS-002 — Reasoning Constitution

Purpose: Define how agents reason over the PKG.
Scope: All agents in the Agent Layer.
Key principles:
- Agents are stateless reasoners over a stateful PKG.
- Every assertion must be defensible from evidence.
- Speculation is recorded as UNKNOWN confidence, not as fact.
- Reasoning is reproducible from provenance.

6. GFS-003 — Knowledge Constitution

Purpose: Define how knowledge is stored, versioned, and traced.
Scope: The PKG, Provenance Ledger, Confidence Registry.
Key principles:
- The PKG is the single source of truth.
- Every mutation creates a new immutable revision.
- Provenance is mandatory; unprovenanced writes are rejected.
- Confidence is explicit on every assertion.

7. GFS-004 — Discovery Constitution

Purpose: Define how creative intent is decomposed.
Scope: Intake, discovery, decomposition workflows.
Key principles:
- Intent is decomposed into structured subproblems.
- Gaps are recorded as explicit Unknown nodes.
- Missing knowledge is a first-class state.
- Conservative by default: record uncertainty rather than invent detail.

8. GFS-005 — Agent Constitution

Purpose: Define agent contracts and supervision.
Scope: All agents (GAS-001..027 + learning/publishers).
Key principles:
- Agents conform to the common agent contract (GARCH-005).
- Agents do not call each other directly.
- Agents are supervised by the Governance Engine.
- Violations trigger suspension of write privileges.

9. GFS-006 — Validation Constitution

Purpose: Define validation rules and findings.
Scope: The Validation Engine and all validators.
Key principles:
- Validation is continuous, not a final gate.
- Findings are first-class PKG nodes.
- Findings have severity: blocking, major, minor, info.
- No blocking finding may remain open at certification.

10. GFS-007 — Governance Constitution

Purpose: Define approval, certification, and handoff.
Scope: The Governance Engine, the Pre-Production Gate.
Key principles:
- No production may be certified without governance approval.
- Approval is signed and auditable.
- The PKP is read-only once certified.
- Revisions require a new PKP version.

11. GFS-008 — Constitutional Meta-Model

Purpose: Define how constitutions are written and amended.
Scope: The GFS family itself.
Key principles:
- Constitutions are versioned.
- Amendments require governance approval.
- Invariants may not be amended without a constitutional convention.
- Additive evolution is preferred over breaking changes.

12. GFS-009 — Constitutional Ontology Framework

Purpose: Define how ontologies conform to the constitution.
Scope: The GO family.
Key principles:
- Every ontology derives from GO-001 Core Ontology.
- Domain ontologies extend but do not contradict Core.
- Specialized ontologies derive from domain ontologies.
- Conflicts escalate to the Core Ontology, not to engineering discretion.

13. Cross-Cutting Invariants

The following invariants appear across multiple GFS standards and may not be amended piecemeal:

- The PKG is canonical.
- Provenance is mandatory.
- Confidence is explicit.
- Genesis produces no media.
- The Studio Engine may not write back to the live PKG.
- Constitutional supremacy outranks every other layer.

14. Amendment Process

Amendments to any GFS standard require:
- A proposed amendment document.
- Governance Engine review.
- A recorded vote or approval event.
- A new version of the affected standard.
- Update of all dependent documents.

Invariants require a constitutional convention and may not be amended through the normal process.

15. Approval

This summary is binding as a quick reference. For any conflict, the full text of the relevant GFS standard prevails.