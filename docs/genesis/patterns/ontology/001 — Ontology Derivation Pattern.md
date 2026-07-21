Genesis Pattern (GP)
GP-ONT-001 — Ontology Derivation Pattern

Document ID: GP-ONT-001
Title: Ontology Derivation Pattern
Version: 1.0.0
Status: Pattern
Authority: Derived from GFS-000, GFS-009, GO-001

1. Purpose

The Ontology Derivation Pattern defines the canonical procedure for deriving a new domain ontology from the Genesis Core Ontology (GO-001). Every domain ontology — Narrative, Character, World, Psychological Cinema, Communication, Production, Governance — must follow this procedure so that the resulting vocabulary remains coherent with the constitutional semantic foundation.

Derivation is not freeform authoring. It is a constrained, traceable act of specialization: the domain ontology inherits meaning from the Core, narrows it for a specific creative territory, and registers itself in the Ontology Registry (see GP-ONT-002). A derived ontology that contradicts the Core is constitutionally invalid.

2. When to Apply

Apply this pattern when:

- A new creative medium requires vocabulary the Core does not cover (e.g. cinematic staging, devotional storytelling).
- An existing domain needs formalization — vocabulary has emerged organically in PKG instances and now must be promoted to an ontology.
- A downstream engine requires a typed contract with the PKG.
- A vertical extension (e.g. GO-201 Psychological Cinema) must layer above an existing domain ontology (e.g. GO-101 Narrative).

Do not apply this pattern for ad-hoc vocabulary inside a single production — that belongs as PKG instances, not as ontology.

3. Roles

- Ontology Owner — accountable for the ontology across versions.
- Ontology Architect — drafts the structure and concept catalog.
- Core Reviewer — verifies inheritance from GO-001 is preserved.
- Governance Agent — approves promotion to Published status.

4. Inputs

- GO-001 Genesis Core Ontology (mandatory).
- The parent domain ontology, if deriving a vertical extension (e.g. GO-101 → GO-201).
- A domain boundary statement: what territory this ontology covers and explicitly excludes.
- A set of production-side examples where the new vocabulary has already appeared informally.

5. Derivation Steps

5.1 Define the Domain Boundary

State precisely what the ontology covers and what it does not. Boundary statements must be affirmative AND exclusionary.

Example:

GO-104 Character Ontology covers intentional participants, identity, motivation, arc, transformation, and relationships. It excludes casting, actor likeness, voice timbre physiology, and wardrobe logistics.

5.2 Select Inherited Concepts

Enumerate the Core concepts the domain specializes. Every selected concept becomes an inheritance edge in the registry.

Example:

Character inherits from Thing → Creative Thing → Narrative Thing → Character → Protagonist.

5.3 Define Domain Concepts

For each new concept, supply the seven canonical attributes from GO-001 §20:

- Stable Identifier (GO-NNN-CCC)
- Canonical Name
- Human-Friendly Name
- Description
- Semantic Definition
- Synonyms
- Examples

5.4 Bind Relationships

For every concept, declare relationships using only predicates from GO-002 Genesis Semantic Relationship Catalog. Foreign predicates are prohibited.

5.5 Assign Cardinality and Directionality

Each relationship must declare direction (subject → object), cardinality (1:1, 1:N, N:M), transitivity, symmetry, and lifecycle implications.

5.6 Compose, Do Not Duplicate

Prefer composition (Character = Identity + Motivation + Relationships + Transformation + Goals) over monolithic concepts. If a new concept duplicates an existing one, refactor instead.

5.7 Classify Every Concept by Lifecycle

Mark each concept Proposed → Reviewed → Validated → Approved → Published. Only Published concepts may be referenced by downstream agents and the PKG.

5.8 Produce Validation SHACL

For every relationship cardinality and inheritance edge, emit a SHACL shape. The ontology is not complete until it is machine-validatable.

6. Validation Gate

Before registration, the Ontology Architect must demonstrate:

- Every concept has a traceable parent in GO-001 or a registered parent ontology.
- No concept contradicts a Core invariant (GO-001 §24).
- Every relationship uses a GO-002 predicate.
- SHACL shapes pass against three representative PKG fixtures.
- The domain boundary is unambiguous.

The Core Reviewer signs the Derivation Record only when all five hold.

7. Registration

Upon validation, the ontology is recorded in registry/001 — Ontology Registry.md with:

- Ontology ID (GO-NNN)
- Title
- Version (see GP-ONT-002)
- Owner
- Status
- Parent ontology
- Derivation date
- SHACL artifact path

An ontology that is not registered does not exist constitutionally. Agents are forbidden from referencing unregistered ontologies.

8. Anti-Patterns

- Re-defining a Core concept under a new name to bypass inheritance.
- Borrowing predicates from external vocabularies (schema.org, Dublin Core) without mapping them to GO-002.
- Defining concepts without examples — examples are mandatory.
- Registering the ontology before SHACL validation passes.
- Using the ontology in PKG instances before it reaches Published status.

9. Worked Example

Deriving GO-104 Character Ontology from GO-001:

1. Boundary: intentional participants; excludes casting and voice physiology.
2. Inherits: Character ← Narrative Thing ← Creative Thing ← Thing.
3. New concepts: Persona, Core Fear, Transformation Vector, Expression Range.
4. Relationships: Character has Core Fear; Core Fear opposes Goal; Transformation Vector evolves_from Conflict.
5. SHACL: Character → has exactly one Core Fear; Transformation Vector → evolves_from at least one Conflict.
6. Validation: tested against three PKG fixtures from prior productions.
7. Registered: GO-104, v1.0.0, Owner — Character Manager Agent.

10. Exit Criteria

The pattern is complete when:

- The Derivation Record is signed.
- The ontology is registered.
- SHACL shapes are committed under schemas/.
- At least one downstream agent references it in its spec.
- Governance Agent has approved Published status.