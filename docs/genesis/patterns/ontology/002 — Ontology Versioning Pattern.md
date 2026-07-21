Genesis Pattern (GP)
GP-ONT-002 — Ontology Versioning Pattern

Document ID: GP-ONT-002
Title: Ontology Versioning Pattern
Version: 1.0.0
Status: Pattern
Authority: Derived from GFS-000, GFS-009, GO-001

1. Purpose

Ontologies in Genesis are durable. A registered ontology may outlive every implementation, model, and rendering technology used by a production. The Versioning Pattern defines how an ontology evolves without invalidating the productions, PKG instances, and downstream agents that depend on it.

Versioning here is semantic and constitutional: it governs how meaning may extend, how compatibility is preserved, how migrations are announced, and how deprecated concepts are retired. An ontology that silently changes meaning breaks the First Principle — knowledge precedes production — because prior productions would silently lose their foundation.

2. Version Scheme

Every ontology follows Semantic Versioning with a constitutional twist:

MAJOR.MINOR.PATCH

- MAJOR — meaning of an existing concept changed in a way that is not backward compatible. Requires a Migration Record.
- MINOR — additive: new concepts, new relationships, new SHACL shapes that do not break existing instances. Backward compatible.
- PATCH — clarifications, documentation, examples, typo fixes, non-semantic SHACL tightening that existing instances already satisfy. Backward compatible.

The version is recorded in the Ontology Registry and in the ontology header block. The first Published version of any ontology is 1.0.0.

3. What Constitutes a Breaking Change

A change is MAJOR when any of the following hold:

- A Published concept is removed.
- A concept's Canonical Name is renamed (renaming the human-friendly name is allowed; renaming the canonical name is not).
- A relationship's predicate is changed.
- A relationship's cardinality is tightened below what existing instances satisfy (e.g. 1:N → 1:1).
- A concept's semantic definition is altered so that an instance valid under vN is invalid under vN+1.
- An inheritance parent is replaced (e.g. Character ← Thing becomes Character ← Actor — forbidden).
- A SHACL shape becomes unsatisfiable by previously valid PKG instances.

A change is MINOR when it adds concepts, relationships, predicates, or optional SHACL constraints. A change is PATCH when it alters only documentation, examples, or descriptions without affecting validation.

4. Backward Compatibility Contract

- A PKG instance valid under ontology vN.x.y must remain valid under vN.(x+1).z and vN.x.(y+1).
- A PKG instance valid under vN.x.y must remain parseable under v(N+1).0.0 — it may not be semantically valid without migration, but it must not be unreadable.
- Agents compiled against vN.x.y must continue to function against vN.(x+1).z without modification.
- Agents compiled against vN.x.y are not guaranteed to function against v(N+1).0.0 and must be migrated.

5. Migration Record

Every MAJOR bump must produce a Migration Record containing:

- Affected concept identifiers.
- Old and new semantic definitions side by side.
- The reason for the breaking change.
- A SHACL diff showing what previously valid instances now fail.
- An automated migration script or a documented manual procedure.
- A list of dependent agents and ontologies that must be updated.
- A target retirement date for the prior MAJOR version.

The Migration Record is stored alongside the ontology under decisions/ as an Architecture Decision Record referencing the ontology ID.

6. Deprecation Lifecycle

Deprecated concepts follow a multi-stage lifecycle:

Published → Deprecated → Sunset → Archived

- Published — concept is active and may be referenced.
- Deprecated — concept still works, but a replacement is announced. Agents must emit a warning when emitting instances. New ontologies must not reference deprecated concepts.
- Sunset — concept is no longer accepted by default validation. PKG instances referencing it must declare an explicit compatibility flag.
- Archived — concept is removed from the active ontology and held in an archive file for historical reference only.

A concept must remain Deprecated for at least one full MAJOR cycle before moving to Sunset. This protects long-running productions from abrupt breakage.

7. Version Registration

Each version bump updates registry/001 — Ontology Registry.md with:

- Ontology ID
- New version
- Bump type (MAJOR / MINOR / PATCH)
- Date
- Owner
- Migration Record reference (for MAJOR)
- Backward compatibility statement
- Approving Governance Agent

An unregistered version does not exist constitutionally. Agents may not consume it.

8. Worked Examples

8.1 MINOR Bump

GO-104 Character Ontology v1.2.0 adds the concept Expression Range and the relationship Character → has → Expression Range. Existing PKG instances are unaffected. Agents gain a new optional field. Registry entry updated. No migration required.

8.2 MAJOR Bump

GO-101 Narrative Ontology v2.0.0 changes the cardinality of Scene → has → Beat from 1:N to 1:N with minimum 1 (a scene must have at least one beat). Productions with empty scenes must migrate. Migration Record narrates the change, ships a migration script that inserts a placeholder Beat labeled UNKNOWN into empty scenes, and lists Screenplay Writer Agent and Scene Planner Agent as affected. The prior v1.x remains Sunset for one MAJOR cycle.

8.3 PATCH Bump

GO-001 Core Ontology v1.0.1 clarifies the description of Knowledge Object with an additional example. No semantic change. No agent action required. Registry entry updated.

9. Anti-Patterns

- Bumping MAJOR without producing a Migration Record.
- Renaming a Canonical Name as a "PATCH".
- Reusing an archived concept identifier for a new concept — identifiers are permanent.
- Skipping the Deprecated stage and jumping straight to Sunset.
- Allowing an agent to consume a Sunset ontology without an explicit compatibility flag.
- Failing to update the registry when a version is published.

10. Exit Criteria

Versioning is complete when:

- The bump type is correctly classified.
- The registry entry is updated.
- For MAJOR bumps, a Migration Record exists and dependent agents have been notified.
- For deprecations, the replacement concept is named and the deprecation date is recorded.
- Governance Agent has signed off on the version transition.