Genesis Guide (GDE)
GDE-003 — Ontology Modeling Guide

Document ID: GDE-003
Title: Ontology Modeling Guide
Version: 1.0.0
Status: Guide
Authority: Derived from GO-001, GFS-009, GMM-002

1. Purpose

This guide tells a contributor how to create a new ontology inside Genesis.
It defines the derivation procedure, the required sections, the registration
steps, and the validation an ontology must pass before it may be referenced
by any other document.

Every ontology in Genesis derives from the Core Ontology (GO-001). A new
ontology may extend GO-001 directly or extend another domain ontology that
itself extends GO-001. An ontology may never redefine a concept that already
exists in a parent. This rule is a constitutional invariant (GO-001 §24).

2. When to Create a New Ontology

Create a new ontology when:

- A coherent family of concepts is needed that is not covered by any
  existing ontology.
- The family is reusable across multiple productions or domains.
- The family can be defined independently of implementation technology.

Do not create a new ontology when:

- A single new concept is needed. Add it to the most specific existing
  ontology that can hold it.
- The concept is implementation-specific (a rendering format, a tool
  config). Implementation details belong in specifications, not ontologies.
- The concept duplicates an existing concept under a new name. Map the
  new name as a synonym in the Vocabulary Registry (GKR-003) instead.

3. The Derivation Procedure

3.1 Identify the Parent

Pick the parent ontology:

- If the family is universal and domain-independent, the parent is GO-001.
- If the family belongs to an existing domain (narrative, character,
  world, experience, execution), extend the most specific domain
  ontology that already covers that domain.
- If the family belongs to a new domain, extend GO-001 directly and
  declare the new domain in the Ontology Registry.

3.2 Declare the Derivation

The new ontology must open with a Derivation section stating:

- The parent ontology ID.
- The concepts that are inherited unchanged.
- The concepts that are specialized (subclassed) from parent concepts.
- The concepts that are introduced new (composition of parent concepts).

3.3 Define Classes

For each class, declare:

- Stable Identifier (the canonical name, immutable).
- Human-Friendly Name.
- Description (one paragraph).
- Semantic Definition (formal: "X is a Y that...").
- Synonyms (if any).
- Examples (at least two).
- Parent class (from this ontology or a parent ontology).
- Properties (see §3.4).
- Relationships (see §3.5).
- Lifecycle states (Proposed → Reviewed → Validated → Approved →
  Published → Deprecated → Archived, per GO-001 §20).

3.4 Define Properties

For each property:

- Name (canonical, stable).
- Type (from the canonical type set: string, integer, float, boolean,
  enum, reference, URI, UUID, timestamp).
- Cardinality (required, optional, multi-valued).
- Constraints (range, allowed values, regex, reference target).
- Inheritance (declared on the parent class, inherited by subclasses).
- Confidence classification (does this property hold Explicit,
  Inferred, Confirmed, Assumed, or Unknown values?).

3.5 Define Relationships

Relationships come from the Semantic Relationship Catalog (GO-002). Do
not invent new relationship verbs. If a needed verb is missing, propose
an addition to GO-002 in a separate PR first.

For each relationship declared on a class:

- Relationship type (from GO-002).
- Target class.
- Cardinality (one, many, optional).
- Directionality (one-way, two-way).
- Confidence classification.
- Inverse relationship (if any).

3.6 Define Invariants

State the invariants the ontology enforces. Examples:

- A Character always has exactly one CharacterDNA.
- A Scene occurs in exactly one Environment.
- A Beat supports at least one Theme.

Invariants are constitutional within the ontology. They may not be
violated by any PKG instance.

4. Required Sections

Every ontology document must include:

1. Purpose
2. Derivation (parent ontology and inherited concepts)
3. Scope (what is in, what is explicitly out)
4. Classes (with the fields listed in §3.3)
5. Properties (with the fields listed in §3.4)
6. Relationships (with the fields listed in §3.5)
7. Invariants
8. Lifecycle (or a reference to GO-001 §20 if unchanged)
9. Extensibility (how this ontology may be extended)
10. Evolution Policy (additive versioning, backward compatibility)
11. Compliance (what validators must check)

5. Registration

After drafting the ontology:

1. Place it in `ontology/<domain>/NNN — Title.md` with the next free
   `GO-NNN` number.
2. Add an entry to the Ontology Registry under `ontology/registry/`
   with: ID, title, domain, parent, version, status.
3. Add an entry to the Ontology Evolution Framework (GMM-002) describing
   the versioning policy and deprecation rules specific to this ontology.
4. Add any new canonical terms to the Vocabulary Registry (GKR-003).

6. Validation

Before the ontology may be referenced by any other document, it must
pass:

- Structural validation: every class has a stable identifier, a
  description, and a parent.
- Derivation validation: every class's parent resolves to a class in
  this ontology or a parent ontology.
- Relationship validation: every relationship type resolves to an entry
  in GO-002.
- Invariant validation: every invariant is expressible as a graph
  constraint (SHACL or equivalent).
- Naming validation: no canonical name duplicates a name already used
  in another ontology (check via the Vocabulary Registry).

7. Worked Example (Sketched)

Suppose a contributor needs an ontology for "Cinematic Pacing."

1. Parent: GO-101 Narrative Ontology (pacing is a narrative concern).
2. New classes: PacingPattern, PacingBeat, ModulationPoint.
3. Specialized classes: PacingBeat subclasses Beat (from GO-101).
4. New relationships: go:modulates (PacingPattern → Scene), go:peaksAt
   (PacingPattern → ModulationPoint). Both must already exist in GO-002
   or be proposed there first.
5. Invariants: every PacingPattern has at least one ModulationPoint.
6. Register in `ontology/narrative/` (or a new `pacing/` domain), update
   the registry, the vocabulary, and GMM-002.

8. Common Mistakes

- Inventing a new relationship verb instead of proposing it to GO-002.
- Redefining a parent concept under a new name.
- Declaring an invariant that cannot be expressed as a graph constraint.
- Omitting the Evolution Policy section.
- Failing to register the ontology and its terms.

9. Lifecycle of an Ontology

An ontology moves through the concept lifecycle from GO-001 §20:
Proposed → Reviewed → Validated → Approved → Published → (Deprecated) →
(Archived). An ontology is only referenceable by other documents once it
reaches Published. A Deprecated ontology remains referenceable for
audit, but new documents must not depend on it.