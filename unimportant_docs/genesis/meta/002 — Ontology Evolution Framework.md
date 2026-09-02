Genesis Meta-Model (GMM)
GMM-002 — Ontology Evolution Framework

Document ID: GMM-002
Title: Ontology Evolution Framework
Version: 1.0.0
Status: Meta-Model
Authority: Derived from GFS-009, GO-001 §25, GMM-001

1. Purpose

This framework defines how ontologies evolve over time inside Genesis.
It covers versioning, migration, backward compatibility, deprecation,
and the approval process for ontology changes. The goal is to allow
Genesis to grow without breaking existing productions or invalidating
past PKG instances.

Every ontology in Genesis is governed by this framework. The Core
Ontology (GO-001) is governed more strictly because every domain
ontology derives from it.

2. Evolution Principles

- Additive by default. Ontologies grow by adding concepts, not by
  changing existing ones.
- Identity is immutable. A concept's canonical name and identifier
  never change once Published.
- Meaning is stable. A concept's semantic definition does not change
  across versions; a new meaning requires a new concept.
- Deprecation is public. A deprecated concept remains in the ontology
  with a notice and a replacement pointer.
- Backward compatibility is the default. A new version of an ontology
  must not break any PKG instance that was valid under the previous
  version.

3. Versioning

Every ontology carries a version: MAJOR.MINOR.PATCH.

3.1 MAJOR

A MAJOR version bump is required when:

- A concept is removed (concepts are never removed; this is reserved
  for the rare case of a constitutional amendment that forces it).
- An invariant is tightened in a way that invalidates previously valid
  PKG instances.
- A class's parent is changed.

A MAJOR bump requires an Architecture Decision Record and governance
approval. Existing productions remain on their MAJOR version until
explicitly migrated.

3.2 MINOR

A MINOR version bump is required when:

- A new class is added.
- A new property is added to an existing class.
- A new relationship is added.
- A new invariant is added that does not invalidate existing instances.

A MINOR bump is additive and backward-compatible. Existing PKG
instances remain valid. New instances may use the new features.

3.3 PATCH

A PATCH version bump is required when:

- A description is clarified without changing semantics.
- A synonym is added.
- An example is added or corrected.
- A typo is fixed.

A PATCH bump is always backward-compatible.

4. Migration

4.1 When Migration Is Required

Migration is required only on a MAJOR version bump. MINOR and PATCH
bumps do not require migration.

4.2 Migration Procedure

A MAJOR bump must ship with a migration guide that includes:

- The list of changes.
- The list of affected classes and properties.
- A mapping from old concepts to new concepts.
- A script or procedure to upgrade an existing PKG instance.
- A validation step that confirms the upgraded PKG is valid under the
  new version.

4.3 Migration Window

Productions in the `ready` state are never migrated. They remain on
the version they were certified under. Productions in earlier states
may be migrated at the orchestrator's discretion.

5. Backward Compatibility

Backward compatibility is enforced at three levels:

5.1 Structural Compatibility

A PKG instance valid under version N must be syntactically valid under
version N+1 (MINOR) and N+1.PATCH. This means:

- No required property is added to an existing class without a default.
- No class's parent is removed.
- No relationship type used in the PKG is removed from GO-002.

5.2 Semantic Compatibility

A PKG instance valid under version N must remain semantically valid
under version N+1 (MINOR). This means:

- No invariant is tightened in a way that the instance violates it.
- No existing concept's semantic definition is changed.

5.3 Tooling Compatibility

Validators that target version N must continue to pass on instances
of version N+1 (MINOR). This means validators must be additive in what
they accept.

6. Deprecation

6.1 When to Deprecate

A concept is deprecated when:

- A better concept supersedes it.
- The concept is no longer used in practice.
- The concept's semantic definition is ambiguous and a clearer
  replacement exists.

6.2 Deprecation Procedure

1. The concept's Status is changed to Deprecated in the ontology.
2. A Deprecation Notice section is added to the ontology with:
   - The reason for deprecation.
   - The replacement concept (if any).
   - The sunset date (the MAJOR version after which the concept may be
     removed in a constitutional amendment).
3. The Vocabulary Registry (GKR-003) is updated.
4. A changelog entry is added.

6.3 After Deprecation

- A deprecated concept remains referenceable for audit.
- New documents must not depend on a deprecated concept.
- The linter emits a warning (not an error) when a deprecated concept
  is referenced.
- At the sunset date, the concept may be removed via a MAJOR bump and
  a constitutional amendment.

7. Core Ontology Special Rules

GO-001 is the root ontology. Its evolution is more constrained:

- GO-001 may only receive a MAJOR bump via a constitutional amendment
  (GFS-009).
- GO-001 may receive MINOR bumps for additive concepts.
- GO-001 may receive PATCH bumps for clarifications.
- A deprecated GO-001 concept has a sunset date of at least one MAJOR
  cycle in the future.
- No concept in GO-001 may be removed without a successor that
  preserves the meaning of existing PKG instances.

8. Domain Ontology Rules

Domain ontologies (GO-101+) follow the standard rules in this document
with one addition: a domain ontology must declare which Core Ontology
concepts it specializes. If a domain ontology's parent concept is
deprecated in GO-001, the domain ontology must update its derivation
within one release cycle.

9. Approval Process

An ontology change PR must include:

- The version bump (MAJOR, MINOR, or PATCH).
- The changelog entry.
- The migration guide (MAJOR only).
- The deprecation notice (if any).
- The validation results from `tooling/check-ontology-derivation.sh`.
- For a MAJOR bump, an ADR.
- For a Core Ontology MAJOR bump, a constitutional amendment.

Reviewer assignment:

- PATCH: one maintainer.
- MINOR: one maintainer plus a domain reviewer.
- MAJOR (domain): two maintainers plus a domain reviewer.
- MAJOR (GO-001): two maintainers plus governance approval per GFS-009.

10. Audit Trail

Every ontology change is recorded in the ontology's changelog section
with: version, date, summary, contributor, reviewer, ADR reference (if
any). The changelog is part of the ontology document and is preserved
across versions for auditability.

11. Relationship to the PKG

A PKG instance declares the ontology version it was built under. This
declaration is mandatory and is validated at certification. A
production's PKG is only valid against the ontology version it
declares; it is never silently re-validated against a newer version.

This rule preserves the integrity of historical productions: a PKG
certified under GO-101 v1.2.0 remains valid forever, even after GO-101
reaches v2.0.0.