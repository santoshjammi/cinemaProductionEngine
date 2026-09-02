Genesis Master Specification
07 — Compiler

Document ID: GMS-007
Title: Genesis Master Specification — Compiler
Version: 1.0.0
Status: Master Specification
Authority: Derived from GFS-009, GARCH-003

1. Purpose

This document describes the Genesis Ontology Compiler: how it parses ontology sources, validates them, generates code, generates schemas, and generates documentation. The compiler is the bridge between human-authored ontology specifications and the machine-readable artifacts the runtime consumes.

2. Compiler Inputs

The compiler consumes:

- Hand-authored ontology specifications (GO-001..119, GO-201+, GO-301+) in Markdown.
- Schema specifications (GSS-NNN) in JSON Schema or YAML Schema.
- Format and protocol specifications (GSPEC-NNN).
- Production manifests (per-PKG schemas).
- Pattern library entries (GWS-013).
- External standard mappings (GREF-002).

3. Compiler Outputs

The compiler produces:

- Generated ontologies (GO-200+) registered in the Generated Ontology Registry.
- JSON Schemas for every ontology concept.
- YAML Schemas for configuration and manifests.
- RDF/OWL representations for interop.
- GraphQL schemas for the API surface.
- TypeScript type definitions for the runtime.
- Python Pydantic models for the runtime.
- Markdown documentation projections.

4. Compilation Pipeline

4.1 Parse
The compiler parses each source document into an intermediate representation (IR). The IR is a normalized graph of concepts, properties, relationships, and constraints. Parsing fails on malformed headers, missing IDs, or non-conforming structure.

4.2 Validate
The IR is validated against:
- GO-001 Core Ontology (every concept must derive from a Core or Domain concept).
- GO-002 Semantic Relationship Catalog (every relationship must be drawn from the catalog or descend from it).
- GO-003 State and Lifecycle (every concept must follow the canonical lifecycle).
- GO-004 Confidence and Provenance (every assertion-shaped construct must carry both).
- Naming conventions (PascalCase concepts, camelCase properties, snake_case relationships, UPPER_SNAKE_CASE enumerations).

Validation failures produce structured errors and halt compilation.

4.3 Generate Code
The compiler emits TypeScript and Python type definitions for every concept. These definitions are consumed by the runtime and by agents. Code generation is deterministic; the same input always yields the same output.

4.4 Generate Schemas
The compiler emits JSON Schema and YAML Schema for every concept. These schemas are used by the Validation Engine to check PKG writes at runtime.

4.5 Generate Docs
The compiler emits Markdown documentation projections: concept catalogs, relationship catalogs, lifecycle diagrams, inheritance trees. These projections are materialized views and may be regenerated at any time.

4.6 Register Generated Ontologies
For non-ontology sources (schemas, specifications, manifests), the compiler produces a generated ontology (GO-200+) and registers it in the Generated Ontology Registry with its source, digest, parent ontology, and status.

5. Compilation Rules

- Every concept must have a unique GO-NNN identifier.
- Every concept must declare `derives_from` pointing to a parent concept.
- Every property must have a type drawn from the Core type system or another concept.
- Every relationship must reference GO-002.
- Every enumeration must list its values explicitly.
- No concept may redefine a Core property.
- No concept may invert a Core relationship's semantics.

6. Inheritance Resolution

The compiler resolves inheritance at compile time. A domain concept inherits all properties of its parent Core concept. A specialized concept inherits all properties of its parent domain concept. Conflicts are flagged as validation errors.

7. Schema Emission

For every concept, the compiler emits a JSON Schema with:
- `$id` derived from the GO-NNN identifier.
- `type` set to `object`.
- `properties` drawn from the concept's own and inherited properties.
- `required` listing the mandatory properties.
- `additionalProperties: false` to enforce closed schemas.

8. Code Emission

TypeScript emission produces:
- An interface per concept.
- A union type per enumeration.
- A type per relationship.
- A registry object mapping GO-NNN IDs to interfaces.

Python emission produces:
- A Pydantic model per concept.
- An Enum per enumeration.
- A typed relationship per relationship.
- A registry mapping GO-NNN IDs to models.

9. Documentation Emission

Markdown emission produces:
- A concept catalog grouped by ontology.
- A relationship catalog grouped by source concept.
- A lifecycle diagram per concept.
- An inheritance tree per ontology tier.

10. Determinism

Compilation is deterministic. The same inputs produce the same outputs byte-for-byte. This enables reproducible builds and audit.

11. Idempotence

Re-running the compiler over the same inputs regenerates identical outputs. Generated ontologies are not duplicated in the registry; re-runs update the `Generated At` timestamp and digest.

12. Approval

This document is the consolidated compiler reference. For any conflict, the compiler specification in `compiler/` prevails.