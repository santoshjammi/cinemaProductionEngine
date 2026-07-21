Genesis Specification (GSPEC)
GSPEC-031 — Ontology Compiler Specification

Document ID: GSPEC-031
Title: Ontology Compiler Specification
Version: 1.0.0
Status: Specification
Authority: Derived from GFS-009, GO-001, GSS-401, GSS-205

1. Purpose

This Specification defines the Ontology Compiler — the component that transforms
Genesis ontology source files (OWL, SHACL, YAML, Markdown tables) into runtime
artifacts: typed Python dataclasses, TypeScript interfaces, JSON Schemas, SHACL
shapes, and a Graph Database DDL.

The Compiler guarantees that every runtime representation of an ontology is
derived from a single source of truth, satisfying the Fifth Principle: Knowledge
is canonical, files are not.

2. Inputs

The Compiler consumes:

- `ontology/**/*.md` — domain ontologies (GO-NNN)
- `schemas/owl/*.md` — OWL ontology sources (GSS-401, GSS-402)
- `schemas/shacl/*.md` — SHACL shape sources (GSS-201, GSS-205)
- `schemas/yaml-schema/*.md` — YAML authoring schemas (GSS-101..103)
- `schemas/json-schema/*.md` — JSON Schemas (GSS-001, GSS-002)

Each source declares its Document ID, Version, and Authority. The Compiler
rejects sources with missing or inconsistent headers.

3. Outputs

For each ontology domain, the Compiler produces:

1. `dist/ontology/{domain}.py` — typed dataclasses with Pydantic validators
2. `dist/ontology/{domain}.ts` — TypeScript interfaces with zod validators
3. `dist/schema/{domain}.json` — JSON Schema (Draft 2020-12)
4. `dist/shacl/{domain}.ttl` — SHACL shapes graph (Turtle)
5. `dist/rdf/{domain}.ttl` — OWL/RDF serialization (Turtle)
6. `dist/ddl/{domain}.cypher` — Neo4j constraints and indexes
7. `dist/ddl/{domain}.sql` — PostgreSQL DDL (for fallback relational store)

4. Compilation Pipeline

Stage 1 — Parse
  Markdown sources are parsed into an intermediate Ontology IR (OIR). Each
  entity, property, relationship, and constraint is extracted with source
  location metadata.

Stage 2 — Resolve
  Cross-references between ontologies are resolved. Unresolved references are
  fatal. Version mismatches between sources produce warnings unless
  `--strict-versions` is set, in which case they are fatal.

Stage 3 — Validate
  OIR is validated against the SHACL Ontology Constraints (GSS-205) and the
  Ontology Specification Standard (GSPEC-041). Violations are fatal.

Stage 4 — Optimize
  Redundant constraints are deduplicated. Inheritance hierarchies are flattened
  where the target representation does not support polymorphism.

Stage 5 — Emit
  Code generators run per target language. Each generator is isolated and may
  fail independently without corrupting other outputs.

Stage 6 — Verify
  Emitted artifacts are re-parsed and compared to OIR. Round-trip drift is
  fatal. Generated JSON Schemas are validated against the canonical test
  corpus in `tests/ontology/`.

5. Ontology IR (OIR)

OIR is an in-memory directed graph with the following node types:

- Ontology — root, carries id, version, authority
- Class — equivalent to owl:Class
- Property — equivalent to owl:DatatypeProperty or owl:ObjectProperty
- Relationship — named edge type
- Enumeration — closed set of literal values
- Constraint — SHACL-like predicate plus parameters
- Provenance — source file, line, Document ID

OIR is serialized to `dist/ir/{domain}.json` for debugging and tooling.

6. Code Generation Rules

- Every emitted class MUST carry a `__genesis_document_id__` attribute.
- Every emitted property MUST preserve cardinality and confidence metadata.
- Generators MUST NOT invent fields absent from OIR.
- Generators MUST emit deprecation markers when source marks a field deprecated.
- Python dataclasses use `pydantic v2`; TypeScript interfaces use `zod v3`.
- SHACL output reuses the shapes from GSS-201/GSS-205 without modification.

7. Versioning

The Compiler version is independent of ontology versions. Each emitted artifact
records both the Compiler version and the source ontology version in its header
or metadata block. A mismatch between Compiler version and runtime expectations
is a non-fatal warning unless `--strict-compiler-version` is set.

8. CLI

genesis-ontology compile \
  --source ./ontology \
  --schemas ./schemas \
  --output ./dist \
  --targets python,typescript,jsonschema,shacl,owl,neo4j,postgres \
  [--strict-versions] \
  [--strict-compiler-version] \
  [--domain core,narrative]

Exit codes:
  0 — success
  1 — parse or resolve error
  2 — validation error
  3 — emit error
  4 — round-trip drift

9. Caching

The Compiler caches OIR per source file keyed on content hash. Unchanged
sources skip Parse and Resolve. Cache invalidation is automatic when any
upstream Document ID version changes.

10. Observability

Every compilation run emits:
- a structured log to `dist/logs/compile-{timestamp}.jsonl`
- a manifest at `dist/manifest.json` listing sources, outputs, hashes, versions
- a metrics summary to stdout (entities, properties, constraints, elapsed_ms)

11. Dependencies

- Python 3.11+
- rdflib >= 7.0
- pydantic >= 2.0
- jsonschema >= 4.20
- TypeScript 5.x (for TS emit)
- zod >= 3.22

12. Cross-References

- Ontology Specification Standard: GSPEC-041
- Ontology Extension Specification: GSPEC-042
- SHACL constraints: GSS-201, GSS-205
- OWL ontologies: GSS-401, GSS-402