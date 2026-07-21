Genesis Master Specification
08 — Generators

Document ID: GMS-008
Title: Genesis Master Specification — Generators
Version: 1.0.0
Status: Master Specification
Authority: Derived from GARCH-003, GMS-007

1. Purpose

This document catalogs the generators shipped with Genesis. Generators are the components that materialize the PKG and its ontologies into concrete artifacts: documentation, schemas, code, manifests, and interop formats.

Generators are projections. They never store canonical truth; they only emit derived views of the PKG or the ontology registry.

2. Generator Catalog

Genesis ships the following generators:

| ID | Generator | Input | Output |
|----|-----------|-------|--------|
| GEN-MD | Markdown | Ontology / PKG subgraph | Markdown documents |
| GEN-JSON-SCHEMA | JSON Schema | Ontology concept | JSON Schema files |
| GEN-YAML | YAML | Ontology concept / manifest spec | YAML schemas |
| GEN-RDF | RDF | Ontology | RDF/OWL triples |
| GEN-GRAPHQL | GraphQL | Ontology / PKG surface | GraphQL schema |
| GEN-TS | TypeScript | Ontology concept | TypeScript interfaces and unions |
| GEN-PY | Python Pydantic | Ontology concept | Pydantic models and enums |

3. GEN-MD — Markdown Generator

Input: an ontology or a PKG subgraph.
Output: Markdown documents — concept catalogs, relationship catalogs, lifecycle diagrams, inheritance trees, production bibles, screenplays, shot lists.
Use: human-readable documentation and handoff materialization.
Discipline: outputs are projections; they may be invalidated and rebuilt at any time.

4. GEN-JSON-SCHEMA — JSON Schema Generator

Input: an ontology concept.
Output: a JSON Schema file with `$id`, `type: object`, `properties`, `required`, `additionalProperties: false`.
Use: runtime validation of PKG writes by the Validation Engine.
Discipline: schemas are closed; unknown properties are rejected.

5. GEN-YAML — YAML Generator

Input: an ontology concept or a manifest specification.
Output: a YAML schema file used for configuration and manifest validation.
Use: PKP manifest, deliverable index, view index, governance record.
Discipline: YAML schemas are paired with JSON Schemas; both must agree.

6. GEN-RDF — RDF/OWL Generator

Input: an ontology.
Output: RDF triples and OWL axioms expressing the ontology in standard semantic web form.
Use: interop with external knowledge graphs and reasoning engines.
Discipline: RDF output is a derivative; the Markdown ontology remains canonical.

7. GEN-GRAPHQL — GraphQL Generator

Input: an ontology and the PKG query surface.
Output: a GraphQL schema with types, queries, and subscriptions.
Use: the REST/GraphQL API surface for programmatic consumers.
Discipline: the GraphQL schema is generated, not hand-written. Manual edits are overwritten on the next run.

8. GEN-TS — TypeScript Generator

Input: an ontology concept.
Output: TypeScript interfaces, union types for enumerations, typed relationships, and a registry object mapping GO-NNN IDs to interfaces.
Use: the runtime and agent implementations in TypeScript environments.
Discipline: emission is deterministic and reproducible.

9. GEN-PY — Python Pydantic Generator

Input: an ontology concept.
Output: Pydantic models, Enum classes, typed relationships, and a registry mapping GO-NNN IDs to models.
Use: the runtime and agent implementations in Python environments.
Discipline: emission is deterministic and reproducible.

10. Generator Discipline

- Generators are read-only over their inputs. They never write back to the PKG or the ontology registry.
- Generators are deterministic. The same input yields the same output byte-for-byte.
- Generators are idempotent. Re-running produces identical outputs.
- Generators are versioned. Each generator declares its version and the schema version of its output.
- Generators emit a digest of every output for audit.

11. Invocation

Generators are invoked by:
- The compiler during ontology compilation.
- The Materialization Service on demand for PKG projections.
- The CLI for ad hoc generation.
- The API for programmatic generation.

12. Extension Policy

New generators may be added only through:
- A generator specification in `generators/`.
- Governance approval.
- Registration in the generator registry.
- Conformance to the generator discipline above.

13. Non-Goals

Generators do not:
- Modify the PKG.
- Modify the ontology registry.
- Make creative decisions.
- Replace human-authored ontologies.
- Produce media assets.

14. Approval

This document is the consolidated generators reference. For any conflict, the individual generator specifications in `generators/` prevail.