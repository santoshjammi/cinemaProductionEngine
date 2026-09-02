Genesis Ontology (GO)
GO-001 — Core Ontology Specification

Document ID: GO-001-S
Title: Core Ontology Specification
Version: 1.0.0
Status: Ontology Specification
Authority: Derived from GFS-000 through GFS-009 and GO-001 Core Ontology

1. Purpose

This document is the canonical specification for the Core Ontology of the Genesis Engine. It defines the universal vocabulary from which every domain ontology, every PKG instance, and every reasoning operation is constructed.

The Core Ontology is intentionally independent of medium, genre, technology, and platform. It defines the *shape* of creative knowledge, not any particular creative content.

2. Foundational Rule

Every concept in Genesis shall derive from the Core Ontology. Domain ontologies (GO-101+) may extend Core concepts but may not contradict or redefine them. Specialized ontologies (GO-201+) derive from domain ontologies and inherit Core through them.

3. Core Concept Families

The Core Ontology is organized into six root families, referenced across the platform as GO-001 through GO-006:

3.1 GO-001 — Universal Concepts
Thing, Concept, Agent, Event, State, Relationship, Property, Assertion. These are the top-level types from which every other concept descends.

3.2 GO-002 — Semantic Relationship Catalog
The canonical set of relationships that may exist between concepts: depends_on, supports, evokes, contradicts, derives_from, part_of, instance_of, references, implies, refines. Every relationship used anywhere in Genesis must be drawn from this catalog or descend from it.

3.3 GO-003 — State and Lifecycle
The canonical state machine for every concept: Draft → Proposed → Validated → Approved → Certified → Superseded. Lifecycle transitions are governed by the Validation and Governance Engines.

3.4 GO-004 — Confidence and Provenance
The confidence classifications (EXPLICIT, CONFIRMED, INFERRED, ASSUMED, UNKNOWN) and the provenance schema (agent, source, evidence, timestamp, prior revision). Every assertion carries both.

3.5 GO-005 — Creative Intent
The root concept for human-supplied creative input: Intent, Brief, Synopsis, Constraint, Goal, Audience. Creative intent is the seed from which the PKG grows.

3.6 GO-006 — Production Readiness
The root concept for certification: Readiness, Gate, Approval, Signature, Handoff. These are the concepts that govern the PKP boundary.

4. Inheritance Rules

- A domain concept may extend a Core concept via `derives_from`.
- A domain concept may add properties but may not remove or rename Core properties.
- A domain concept may narrow a Core relationship but may not invert its semantics.
- A specialized concept (GO-201+) may extend a domain concept following the same rules.

5. Concept Lifecycle

Every concept instance in the PKG follows the lifecycle defined in GO-003:

1. Draft — created by an agent, not yet validated.
2. Proposed — submitted to validation.
3. Validated — passed validation rules.
4. Approved — passed governance review.
5. Certified — included in a certified PKP.
6. Superseded — replaced by a newer revision; retained for audit.

Transitions are recorded in the Provenance Ledger. Illegal transitions are rejected by the Knowledge Layer.

6. Relationship Discipline

Relationships are typed through GO-002. Every relationship in the PKG must:

- Have a source and target concept.
- Carry a confidence classification.
- Carry provenance.
- Conform to the cardinality constraints declared in GO-002.

Untyped or unprovenanced relationships are rejected at write time.

7. Vocabulary Discipline

Concept names are PascalCase, singular, and English. Property names are camelCase. Relationship names are snake_case. Enumerations are UPPER_SNAKE_CASE. These rules are enforced by the Ontology Compiler.

8. Extension Policy

New Core concepts require a constitutional amendment. New domain concepts require a domain ontology specification and governance approval. New specialized concepts require a specialized ontology specification and a derivation chain back to a domain concept.

9. Conflict With Domain Ontologies

When a domain ontology appears to conflict with the Core Ontology, the Core Ontology prevails. The conflict is recorded as a validation finding and routed to the Governance Engine for resolution.

10. Relationship to Other Specifications

This specification is the parent of:
- GO-101 Narrative Ontology and the rest of the GO-101..119 domain family.
- GO-201+ specialized ontologies.
- The PKG schema (GARCH-008), which types every assertion against a concept defined here.
- The Validation Engine rules, which evaluate PKG contents against the constraints declared here.

11. Provenance Schema

Every assertion typed against a Core concept must carry a provenance record with the following fields:

- `agent` — the GAS-NNN identifier of the asserting agent.
- `source` — the URI or reference from which the assertion was derived.
- `evidence` — a list of supporting evidence references (may be empty for EXPLICIT intent).
- `timestamp` — ISO8601 timestamp of the assertion.
- `priorRevision` — the revision number of the prior assertion this one supersedes (null for first revision).

Assertions missing any required provenance field are rejected by the Knowledge Layer at write time.

12. Confidence Semantics

The five confidence classifications carry the following operational semantics:

- EXPLICIT — directly supplied by human creative intent. No inference.
- CONFIRMED — verified by external evidence or cross-agent agreement.
- INFERRED — derived by an agent from other assertions. Carries uncertainty.
- ASSUMED — adopted without evidence to unblock downstream work. Must be flagged for review.
- UNKNOWN — the assertion is recorded as a gap. Downstream consumers must treat it as absent.

No assertion may be promoted to a higher confidence class without a recorded provenance event explaining the promotion.

13. Relationship Cardinality

GO-002 declares cardinality constraints for every relationship. The Core Ontology enforces:

- `derives_from` — many-to-one (a concept derives from exactly one parent).
- `part_of` — many-to-many with acyclicity (no concept may be part of itself transitively).
- `instance_of` — many-to-one (an instance is of exactly one concept type).
- `references` — many-to-many, unbounded.
- `contradicts` — symmetric (if A contradicts B, B contradicts A).

Violations of cardinality are detected by the Validation Engine and recorded as findings.

14. Approval

This specification is binding for every ontology, every PKG instance, and every reasoning operation in Genesis.