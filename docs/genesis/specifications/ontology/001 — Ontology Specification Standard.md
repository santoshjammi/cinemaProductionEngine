Genesis Specification (GSPEC)
GSPEC-041 — Ontology Specification Standard

Document ID: GSPEC-041
Title: Ontology Specification Standard
Version: 1.0.0
Status: Specification
Authority: Derived from GFS-009, GO-001

1. Purpose

This Specification defines the standard for authoring, structuring, and
maintaining ontologies within the Genesis Engine. It establishes the
required sections, metadata, validation rules, and lifecycle of every
ontology document so that ontologies remain machine-compilable, human-
reviewable, and constitutionally conformant.

2. Scope

This Standard applies to:
- Core ontologies (`ontology/core/`, GO-001..006)
- Domain ontologies (`ontology/{domain}/`, GO-101+)
- OWL sources (`schemas/owl/`, GSS-401+)
- SHACL shape sources (`schemas/shacl/`, GSS-201+)
- Any ontology extension proposed under GSPEC-042

3. Required Document Metadata

Every ontology document MUST begin with:

Genesis Ontology (GO) or Genesis Schema Specification (GSS)
GO-NNN / GSS-NNN — Title

Document ID: GO-NNN (or GSS-NNN)
Title: ...
Version: 1.0.0
Status: Draft | Reviewed | Stable | Deprecated
Authority: Derived from {parent document ids}

`Status` lifecycle: Draft → Reviewed → Stable → (Deprecated | Superseded).
A Stable ontology MAY be patched (semver patch) without re-review. Minor or
major version bumps require Governance Board review (GSPEC-061 §6).

4. Required Sections

Every ontology document MUST include the following sections, in order:

1. **Purpose** — one paragraph explaining the ontology's responsibility.
2. **Scope** — what is in scope and explicitly out of scope.
3. **Classes** — enumerated class definitions with names, descriptions, and
   superclasses.
4. **Properties** — datatype properties with type, cardinality, and confidence
   semantics.
5. **Relationships** — object properties (edge types) with domain, range, and
   cardinality.
6. **Constraints** — SHACL shapes or equivalent constraints referencing the
   classes/properties above.
7. **Enumerations** — closed value sets with stable identifiers.
8. **Provenance** — how entities in this ontology record their origin
   (consistent with GSS-302).
9. **Validation Rules** — integrity rules the Validation Service enforces.
10. **Cross-References** — links to parent ontologies, related schemas, and
    dependent specifications.

5. Naming Conventions

- Class names: `UpperCamelCase`, singular (e.g. `Character`, `SceneBeat`).
- Property names: `snake_case` (e.g. `motivation`, `scene_number`).
- Relationship names: `UPPER_SNAKE_CASE` (e.g. `APPEARS_IN`, `MOTIVATES`).
- Enumeration values: `UPPER_SNAKE_CASE`.
- Identifiers in RDF: `https://genesis.movieos.dev/ontology/{domain}/{name}`.

6. Versioning

- Ontologies use semantic versioning.
- A new class, property, or relationship is a minor bump.
- Removing or renaming is a major bump.
- Tightening a constraint (cardinality, type) is a major bump.
- Loosening a constraint is a minor bump.
- Documentation-only changes are patch bumps.

7. Confidence Model

Every property and relationship declaration MUST state its default confidence
semantics:

- **Explicit** — value is read directly from source material.
- **Inferred** — value is derived by an agent.
- **Confirmed** — inferred value later verified by a human or second agent.
- **Assumed** — value is a working assumption pending confirmation.
- **Unknown** — value is missing and must be discovered.

8. Composition Rules

- Every domain ontology MUST derive from the Core Ontology (GO-001).
- Multiple domain ontologies MAY compose; composition is documented in the
  `Cross-References` section.
- Circular dependencies between ontologies are forbidden.
- An ontology MUST NOT redefine classes or properties declared in a parent;
  it may extend them.

9. Validation by the Compiler

The Ontology Compiler (GSPEC-031) enforces this Standard at Stage 3
(Validate). Failures are fatal. The Compiler emits a structured report
listing every violated rule with the source location.

10. Authoring Workflow

1. Draft the ontology under `ontology/{domain}/` following this Standard.
2. Compile with `genesis ontology compile --domain {domain}`.
3. Run the test corpus in `tests/ontology/{domain}/`.
4. Submit to the Governance Board for review.
5. On approval, set Status to `Stable` and update the CHANGELOG.

11. Deprecation

A deprecated ontology remains available for one release cycle. Its document
header MUST set `Status: Deprecated` and reference the superseding document
in `Authority`. The Compiler emits warnings when a deprecated ontology is
referenced.

12. Cross-References

- Ontology Extension Specification: GSPEC-042
- Ontology Compiler: GSPEC-031
- SHACL constraints: GSS-205
- Provenance vocabulary: GSS-302
- Documentation Standards: GSTD-003