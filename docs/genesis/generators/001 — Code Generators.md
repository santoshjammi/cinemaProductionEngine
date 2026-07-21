Genesis Generator (GGEN)
GGEN-001 — Code Generators

Document ID: GGEN-001
Title: Code Generators
Version: 1.0.0
Status: Active
Authority: Derived from GFS-000

1. Purpose

Catalogs the code generators shipped with Genesis. Generators produce derived
artifacts — Pydantic models, JSON Schemas, documentation — from canonical
sources (ontologies, specifications, PKGs). Generators never produce canonical
content; they materialize views of it.

2. Scope

- Lists every generator, its inputs, outputs, and invocation.
- Generators run via `genesis generate` (GTOOL-001) or the automation scripts (GTOOL-002).
- Does not list the compiler (GCMP-001), which is a separate component even
  though it shares some emit logic.

3. Generator Catalog

### GEN-PYDANTIC — Pydantic models from ontology

- Input: GO-NNN ontology files (compiled by GCMP-001).
- Output: one Python module per ontology with Pydantic models for each class.
- Use: runtime validation of PKG assertions in Python services.
- Invocation:
  ```
  genesis generate --kind pydantic --from ontology --output dist/ontology/
  ```
- Conventions:
  - Black-formatted, type-annotated.
  - Each model has a docstring pointing to the source ontology.
  - Classification tiers become a shared `Classification` enum.
  - Confidence is a `float` field with `ge=0.0, le=1.0`.

### GEN-SCHEMA — JSON Schema from specifications

- Input: GSPEC-NNN specification files.
- Output: one JSON Schema file per specification.
- Use: structural validation of documents claiming conformance to a spec.
- Invocation:
  ```
  genesis generate --kind schema --from spec --output dist/schemas/
  ```
- Conventions:
  - `genesis://` URIs for `$id` and `$ref`.
  - `additionalProperties: false` by default.
  - Every field carries a `description`.
  - Classification enums are exactly the five canonical tiers.

### GEN-DOCS — Documentation from PKG

- Input: an assembled PKG directory.
- Output: Markdown documentation for each major PKG artifact.
- Use: human-readable views for review and handoff.
- Invocation:
  ```
  genesis generate --kind docs --from pkg --pkg <dir> --output dist/docs/
  ```
- Conventions:
  - GitHub-flavored Markdown, 120-char line limit.
  - One H1 per file.
  - Header marks the file as generated with source hash and timestamp.
  - No content is invented; every sentence traces to a PKG node.

### GEN-DOCS-ONTOLOGY — Ontology reference docs

- Input: GO-NNN ontology files.
- Output: Markdown reference doc + Mermaid class diagram per ontology.
- Use: human-readable ontology reference.
- Invocation:
  ```
  genesis generate --kind docs --from ontology --output dist/docs/ontology/
  ```

### GEN-HANDOFF — Movie OS handoff manifest

- Input: a certified PKG.
- Output: a JSON handoff manifest for Movie OS Studio Engine.
- Use: the bridge between Genesis and the Studio Engine (GINT-003).
- Invocation:
  ```
  genesis generate --kind handoff --pkg <dir> --output dist/handoff/
  ```
- Conventions:
  - Manifest is schema-valid against GSS-NNN (handoff schema).
  - Manifest lists every PKG artifact the Studio Engine may consume.
  - Manifest includes the Production Readiness Certificate.

### GEN-GRAPH — Graph loader payload

- Input: GO-NNN ontology files (compiled) or a PKG.
- Output: JSON payload for Neo4j (GINT-001).
- Use: seed the graph metamodel or load a PKG into the graph.
- Invocation:
  ```
  genesis generate --kind graph --from ontology --output dist/graph/
  genesis generate --kind graph --from pkg --pkg <dir> --output dist/graph/
  ```

4. Common Generator Rules

- Every generator emits a manifest listing source hash, generator version, and
  output hash for each file.
- Every generated file is marked as derived in its header.
- Generators are deterministic: identical inputs produce identical outputs.
- Generators never write to canonical source directories.
- Generators never mutate the PKG; they only read it.

5. Extension

New generators are added by:
1. Defining the generator in this document (bump GGEN-001 version).
2. Implementing it under `generators/` with a clear input/output contract.
3. Adding a `--kind` option to `genesis generate` (GTOOL-001).
4. Adding test fixtures to GTEST-002 or GTEST-004 as appropriate.

6. Dependencies

- Compiler: GCMP-001 (compiles ontologies before code generation)
- CLI: GTOOL-001 (entry point)
- Schemas: GSS-NNN set (output targets)
- Integrations: GINT-001 (graph), GINT-003 (handoff)