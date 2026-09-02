Genesis Test (GTEST)
GTEST-002 — Schema Conformance Tests

Document ID: GTEST-002
Title: Schema Conformance Tests
Version: 1.0.0
Status: Active
Authority: Derived from GFS-000

1. Purpose

Test cases that every Genesis schema (GSS-NNN) and every document claiming to
conform to a GSS-NNN schema must pass. These tests operationalize the rules in
the Schema specifications and the PKG Validator (GVAL-001).

2. Scope

- Applies to all files in `schemas/json/` and `schemas/yaml/`.
- Applies to any artifact (Production Brief, Character DNA, Scene Spec, PKG
  manifest) that declares conformance to a GSS-NNN schema.
- Does not test ontology semantics (covered by GTEST-001).

3. Test Cases

T001 — Schema header present
- Given: a schema file
- When: parsed
- Then: $schema, $id, title, description, type fields are present and non-empty
- Severity: Block

T002 — $id uses genesis:// scheme
- Given: a schema file
- When: parsed
- Then: $id starts with `genesis://schemas/`
- Severity: Block

T003 — Strict by default
- Given: a schema file
- When: parsed
- Then: additionalProperties is false unless an explicit comment explains the relaxation
- Severity: Block

T004 — Every property has a description
- Given: a schema file
- When: parsed
- Then: every property object contains a non-empty description
- Severity: Warn

T005 — Enums are closed
- Given: a schema with an enum
- When: parsed
- Then: enum field is a non-empty array and no enum is left as an open set
- Severity: Block

T006 — Classification enum is canonical
- Given: a schema with a classification field
- When: parsed
- Then: the enum is exactly ["Explicit", "Inferred", "Confirmed", "Assumed", "Unknown"]
- Severity: Block

T007 — $ref resolves within Genesis schema set
- Given: a schema with a $ref
- When: resolved
- Then: the target exists in the Genesis schema registry (genesis://schemas/...)
- Severity: Block

T008 — Document conforms to declared schema
- Given: a document with a declared schema_id
- When: validated against that schema
- Then: validation succeeds with zero errors
- Severity: Block

T009 — Required fields populated
- Given: a document conforming to a schema
- When: validated
- Then: all fields listed in schema `required` are present and non-null
- Severity: Block

T010 — No unexpected fields
- Given: a document conforming to a strict schema
- When: validated
- Then: no field outside the schema's properties is present
- Severity: Block

T011 — Type correctness
- Given: a document conforming to a schema
- When: validated
- Then: each field value matches its declared JSON Schema type
- Severity: Block

T012 — String length and format constraints
- Given: a document with string fields
- When: validated
- Then: minLength, maxLength, and format constraints are satisfied
- Severity: Block

T013 — Array bounds respected
- Given: a document with array fields
- When: validated
- Then: minItems and maxItems constraints are satisfied
- Severity: Block

T014 — Numeric ranges respected
- Given: a document with numeric fields
- When: validated
- Then: minimum and maximum constraints are satisfied
- Severity: Block

T015 — Schema version compatibility
- Given: a schema with $id containing a version
- When: a new version of the schema is published
- Then: any breaking change results in a new GSS-NNN number, not an in-place edit
- Severity: Block

4. Fixtures

- `tests/fixtures/schema/valid-production-brief.json`
- `tests/fixtures/schema/invalid-unknown-field.json` — fails T010
- `tests/fixtures/schema/invalid-bad-classification.json` — fails T006
- `tests/fixtures/schema/valid-character-dna.yaml`

5. Execution

```
genesis test --suite schema
genesis validate --path <document> --schema <GSS-NNN>
```

6. Exit Criteria

- All Block-severity tests pass.
- Warn-severity tests pass or are waived.
- Output is a JSON report at `tests/reports/GTEST-002-<timestamp>.json`.
- Every validation error includes the schema $id, the JSON path, and a human message.