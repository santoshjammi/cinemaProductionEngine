Genesis Master Specification
03 — GFS Overview

Document ID: GMS-003
Title: Genesis Master Specification — GFS Overview
Version: 1.0.0
Status: Master Specification
Authority: Derived from GFS-000 through GFS-009

1. Purpose

This document summarizes all ten Genesis Foundational Standards (GFS-000 through GFS-009) with their purpose, scope, and key principles. It is the index for the constitutional layer.

For the full text, see `constitutions/`.

2. Standard Index

| ID | Title | Authority |
|----|-------|-----------|
| GFS-000 | Constitutional Charter | Supreme |
| GFS-001 | Identity Constitution | Derived |
| GFS-002 | Reasoning Constitution | Derived |
| GFS-003 | Knowledge Constitution | Derived |
| GFS-004 | Discovery Constitution | Derived |
| GFS-005 | Agent Constitution | Derived |
| GFS-006 | Validation Constitution | Derived |
| GFS-007 | Governance Constitution | Derived |
| GFS-008 | Constitutional Meta-Model | Derived |
| GFS-009 | Constitutional Ontology Framework | Derived |

3. GFS-000 — Constitutional Charter

Purpose: Establish the supreme authority, value system, and invariants of Genesis.
Scope: The entire platform and every downstream consumer.
Key principles: Knowledge precedes production; the PKG is canonical; constitutional supremacy; separation from media generation; implementation independence; provenance mandatory; confidence explicit; validation continuous; governance binding; reversibility.

4. GFS-001 — Identity Constitution

Purpose: Define what Genesis is and is not.
Scope: System identity, boundaries, naming.
Key principles: Genesis is a reasoning system, not a generator; medium-agnostic; provider-agnostic; implementation-agnostic; pre-production only.

5. GFS-002 — Reasoning Constitution

Purpose: Define how agents reason over the PKG.
Scope: All agents in the Agent Layer.
Key principles: Agents are stateless reasoners over a stateful PKG; every assertion defensible from evidence; speculation recorded as UNKNOWN; reasoning reproducible from provenance; conservative by default.

6. GFS-003 — Knowledge Constitution

Purpose: Define how knowledge is stored, versioned, and traced.
Scope: The PKG, Provenance Ledger, Confidence Registry.
Key principles: PKG is the single source of truth; every mutation creates a new immutable revision; provenance mandatory; confidence explicit; revisions reversible without overwriting history.

7. GFS-004 — Discovery Constitution

Purpose: Define how creative intent is decomposed.
Scope: Intake, discovery, decomposition workflows.
Key principles: Intent decomposed into structured subproblems; gaps recorded as explicit Unknown nodes; missing knowledge is first-class state; conservative default over invention.

8. GFS-005 — Agent Constitution

Purpose: Define agent contracts and supervision.
Scope: All agents (GAS-001..027 + learning/publishers).
Key principles: Agents conform to the common agent contract; agents do not call each other directly; agents supervised by the Governance Engine; violations suspend write privileges; agents are observable through the same audit mechanisms.

9. GFS-006 — Validation Constitution

Purpose: Define validation rules and findings.
Scope: The Validation Engine and all validators.
Key principles: Validation is continuous; findings are first-class PKG nodes; severities are blocking, major, minor, info; no blocking finding may remain open at certification; validation produces findings, not silent corrections.

10. GFS-007 — Governance Constitution

Purpose: Define approval, certification, and handoff.
Scope: The Governance Engine, the Pre-Production Gate.
Key principles: No production certified without governance approval; approval signed and auditable; PKP read-only once certified; revisions require a new PKP version; governance records part of the PKP.

11. GFS-008 — Constitutional Meta-Model

Purpose: Define how constitutions are written and amended.
Scope: The GFS family itself.
Key principles: Constitutions versioned; amendments require governance approval; invariants may not be amended without a constitutional convention; additive evolution preferred over breaking changes.

12. GFS-009 — Constitutional Ontology Framework

Purpose: Define how ontologies conform to the constitution.
Scope: The GO family.
Key principles: Every ontology derives from GO-001; domain ontologies extend but do not contradict Core; specialized ontologies derive from domain ontologies; conflicts escalate to Core, not to engineering discretion.

13. Derived Standards

Derived standards (GFS-010+) may be issued by the Governance Engine to extend the constitutional layer without amending the core ten. They are registered in the constitution registry and are subordinate to GFS-000..009.

14. Conflict Resolution

When two GFS standards appear to conflict:
- GFS-000 prevails.
- If neither is GFS-000, the more specific standard prevails.
- If specificity is equal, the Governance Engine adjudicates.

15. Approval

This overview is binding as an index. For any conflict, the full text of the relevant GFS standard prevails.