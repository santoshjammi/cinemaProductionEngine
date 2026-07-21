Genesis Compiler (GCMP)
GCMP-001 — Ontology Compiler

Document ID: GCMP-001
Title: Ontology Compiler
Version: 1.0.0
Status: Active
Authority: Derived from GFS-000

1. Purpose

The Ontology Compiler parses Genesis ontology files (GO-NNN, GOX-NNN),
validates them against the Core Ontology metamodel (GO-001), resolves
inheritance and references across the ontology set, and emits machine-usable
representations: Pydantic models, JSON Schemas, and graph loader payloads.

2. Scope

- Compiles ontology source files into runtime artifacts.
- Resolves cross-ontology references and inheritance chains.
- Does not validate PKG assertions (that is GVAL-002's job, though GVAL-002
  uses the compiler's output).
- Does not generate documentation (that is GGEN-001's job).

3. Inputs

- `--ontology <dir>`: the ontology root directory.
- `--output <dir>`: where to emit artifacts (default `dist/ontology/`).
- `--format <pydantic|schema|graph|all>`: emit target (default `all`).

4. Outputs

For `--format pydantic`:
- One Python module per ontology: `dist/ontology/<domain>/go_NNN.py`.
- Each class becomes a Pydantic model with properties as fields.
- Each relationship becomes a typed field with the appropriate cardinality.
- Classification tags become an enum shared across all modules.

For `--format schema`:
- One JSON Schema file per ontology: `dist/ontology/<domain>/go_NNN.schema.json`.
- Each class becomes a `$def`; the root is an `oneOf` of all classes.
- Schemas use `genesis://` URIs and `additionalProperties: false`.

For `--format graph`:
- One graph loader payload per ontology: `dist/ontology/<domain>/go_NNN.graph.json`.
- Nodes are classes; edges are parent relationships and declared relationships.
- Used by the Neo4j integration (GINT-001) to seed the metamodel.

5. Compilation Stages

### Stage 1: Parse

- Walk the ontology directory.
- Parse each file into an intermediate representation (IR).
- Reject files that fail GTEST-001 T001 (header block).

### Stage 2: Validate

- Run the Ontology Validator (GVAL-002) on every parsed file.
- Fail fast on any Block-severity rule violation.
- Emit a validation report alongside the compiled output.

### Stage 3: Resolve

- Resolve parent class references across files.
- Resolve relationship Domain and Range references.
- Resolve extension Parent ontology references.
- Fail on any unresolved reference.

### Stage 4: Flatten

- For each class, compute the full property set including inherited properties.
- For each class, compute the full rule set including inherited rules.
- Detect and report any rule conflicts introduced by inheritance.

### Stage 5: Emit

- Generate the requested output format(s).
- Write a manifest at `dist/ontology/manifest.json` listing every emitted file,
  its source ontology, and a content hash.
- Mark every emitted file as derived (header comment / $comment field).

6. Caching

- The compiler hashes each source ontology and compares against the previous
  manifest. Unchanged ontologies are not recompiled.
- A `--force` flag bypasses the cache.

7. Error Handling

- Parse errors: reported with file path and line number; compilation aborts.
- Validation errors: reported via the GVAL-002 report; compilation aborts.
- Resolution errors: reported with the unresolved reference; compilation aborts.
- Conflicts during flatten: reported with both rules; compilation aborts.

8. Execution

```
genesis compile --ontology ontology/ --output dist/ontology/ --format all
```

9. Dependencies

- Core Ontology: GO-001 (metamodel)
- Ontology Validator: GVAL-002
- Tests: GTEST-001
- Generators: GGEN-001 (delegates to compiler for ontology→code)
- Integrations: GINT-001 (consumes graph output)