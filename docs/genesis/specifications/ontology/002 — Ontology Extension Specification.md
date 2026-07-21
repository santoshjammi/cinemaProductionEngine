Genesis Specification (GSPEC)
GSPEC-042 — Ontology Extension Specification

Document ID: GSPEC-042
Title: Ontology Extension Specification
Version: 1.0.0
Status: Specification
Authority: Derived from GFS-009, GO-001, GSPEC-041

1. Purpose

This Specification defines how the Genesis ontology set is extended — by
adding new domain ontologies, new classes/properties to existing domains, or
new constraints — without breaking the canonical core or invalidating existing
Production Knowledge Graphs.

Extensions are how Genesis adapts to new genres, formats, and production
cultures while preserving the Fifth Principle (knowledge is canonical).

2. Extension Categories

### Category A — New Domain Ontology
A brand-new ontology under `ontology/{domain}/` that derives from GO-001. Does
not modify any existing ontology.

### Category B — Additive Extension
Adds new classes, properties, relationships, or enumeration values to an
existing Stable ontology. Strictly additive; no removals, no renames, no
constraint tightening.

### Category C — Constraint Extension
Adds new SHACL shapes or business rules to an existing ontology without
modifying the class/property declarations.

### Category D — Deprecating Extension
Marks existing elements deprecated and provides replacements. Requires a
major version bump of the parent ontology and a migration path.

3. Authoring Requirements

Every extension MUST:
- Follow the Ontology Specification Standard (GSPEC-041).
- Declare its category (A/B/C/D) in the document header.
- Reference its parent ontology in `Authority`.
- Include a `Migration` section for Category B/C/D extensions.
- Include a `Backward Compatibility` section proving no breaking change for
  Category A/B/C.
- Pass Ontology Compiler validation (GSPEC-031 §4 Stage 3).

4. Versioning Impact

| Category | Parent version impact | Extension version |
|----------|----------------------|-------------------|
| A        | none                 | 1.0.0             |
| B        | minor bump           | 1.0.0             |
| C        | patch bump           | 1.0.0             |
| D        | major bump           | 1.0.0             |

The extension's own version is independent of the parent's bump.

5. Approval Process

1. Draft the extension under `ontology/{domain}/` or `ontology/extensions/`.
2. Compile and run the test corpus.
3. Open an ADR in `decisions/` describing the extension, rationale,
   alternatives considered, and confidence impact.
4. Submit to the Governance Board.
5. On approval, merge and update the Ontology Compiler manifest so downstream
   runtimes pick up the extension.

6. Migration

Category D extensions MUST include:
- A mapping table from deprecated element → replacement element.
- A migration script in `db/migrations/` that rewrites existing PKG data.
- A deprecation period of at least one release cycle (minimum 6 months).
- A validation rule that flags usage of deprecated elements in new productions.

7. Backward Compatibility Proof

The extension author MUST demonstrate, via the Ontology Compiler round-trip
check (GSPEC-031 §4 Stage 6), that existing PKG documents validate against the
extended ontology. The test corpus MUST include at least three productions
authored under the previous ontology version.

8. Namespace and Identifiers

Extensions MUST use a namespaced URI to avoid collisions:
`https://genesis.movieos.dev/ontology/{extension-domain}/{name}`

Extension domain names are kebab-case and unique in the registry.

9. Registration

Approved extensions are registered in `registry/ontology-extensions.yaml` with:
- Document ID
- Version
- Category
- Parent ontology
- Status
- Approval ADR reference

The Ontology Compiler reads this registry to determine the active ontology set
for a runtime.

10. Conflict Resolution

When two extensions define the same element:
- The Governance Board arbitrates.
- The first-approved extension keeps the identifier.
- The second extension MUST rename or be rejected.
- No two extensions may produce conflicting SHACL constraints on the same
  property.

11. Withdrawal

An extension may be withdrawn by its author. Withdrawal follows the
deprecation process of GSPEC-041 §11. Withdrawn extensions remain in the
registry with `Status: Withdrawn` and a reference to any successor.

12. Cross-References

- Ontology Specification Standard: GSPEC-041
- Ontology Compiler: GSPEC-031
- Governance: GSPEC-061 §6
- SHACL constraints: GSS-205
- ADR process: `decisions/README.md`