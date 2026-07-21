Genesis Validator (GVAL)
GVAL-002 — Ontology Validator

Document ID: GVAL-002
Title: Ontology Validator
Version: 1.0.0
Status: Active
Authority: Derived from GFS-000

1. Purpose

The Ontology Validator verifies that every ontology file (GO-NNN) and every
ontology extension (GOX-NNN) conforms to the Core Ontology metamodel (GO-001),
and that every assertion in a PKG conforms to its governing ontology. It is
invoked by the PKG Validator (GVAL-001) and by `genesis validate --ontology`.

2. Scope

- Validates ontology source files in `ontology/` and `ontology/*/extensions/`.
- Validates assertions inside a PKG against their declared governing ontology.
- Does not validate schema structure (covered by GTEST-002).
- Does not evaluate readiness thresholds (covered by GVAL-003).

3. Inputs

- `--ontology <file|dir>`: an ontology file or a directory of ontologies.
- `--pkg <dir>`: a PKG whose assertions should be validated against their governing ontologies.
- `--config <file>`: optional override.

4. Outputs

- JSON report with fields:
  - `ontology_id`, `validated_at`, `validator_version`
  - `checks`: array of `{id, severity, passed, message, path, class?, relationship?}`
  - `summary`: `{block_passed, block_failed, warn_passed, warn_failed}`
- Exit 0 only if all Block-severity checks pass.

5. Validation Rules

### Metamodel Conformance

R001 — Header block present and complete
- Document ID, Title, Version, Status, Authority are present and non-empty.
- Severity: Block

R002 — Document ID matches filename and prefix
- GO-NNN for ontologies, GOX-NNN for extensions.
- Severity: Block

R003 — Authority traces to GO-001
- Directly or through a chain of Derived-from references.
- Severity: Block

R004 — Classes section present
- At least one class is defined.
- Severity: Block

R005 — Every class has Name and Description
- Severity: Block

R006 — Parent class resolves
- Parent is None or resolves to a class in this or a parent ontology.
- Severity: Block

R007 — No duplicate class names within file
- Severity: Block

R008 — No duplicate relationship names within file
- Severity: Block

R009 — Relationship Domain and Range resolve
- Severity: Block

R010 — Cardinality is one of {1:1, 1:N, M:N}
- Severity: Block

### Parent Compatibility (for extensions)

R011 — No parent class removed or narrowed
- Severity: Block

R012 — No parent relationship removed or reversed
- Severity: Block

R013 — No parent rule negated
- Severity: Block

R014 — No name collision with parent
- Severity: Block

R015 — Backward Compatibility section present
- Severity: Block

### Assertion Conformance (PKG mode)

R016 — Every assertion's class exists in the governing ontology
- Severity: Block

R017 — Every assertion's properties are declared on its class
- Severity: Block

R018 — Every assertion's relationships are declared in the ontology
- Severity: Block

R019 — Cardinality constraints satisfied
- Severity: Block

R020 — Rules satisfied
- Every rule declared in the ontology evaluates to true for the assertion.
- Severity: Block

R021 — Classification tag is one of the five canonical tiers
- Severity: Block

R022 — Inferred assertions carry evidence
- Severity: Block

R023 — Confirmed assertions meet confidence threshold
- Severity: Block

R024 — Assumed assertions carry an explicit assumption statement
- Severity: Block

R025 — Unknown assertions are flagged for escalation
- Severity: Block

### Quality of Authoring

R026 — Classification Tiers section lists all five tiers
- Severity: Warn

R027 — Traceability section present
- Severity: Warn

R028 — Validation section present
- Severity: Warn

R029 — No orphan properties (declared but unused and not marked optional)
- Severity: Warn

R030 — Naming conventions (PascalCase classes, camelCase properties)
- Severity: Warn

6. Execution Model

1. Load ontology file(s).
2. Run metamodel conformance rules (R001-R010).
3. If extension, run parent compatibility rules (R011-R015).
4. If PKG mode, run assertion conformance rules (R016-R025) against each assertion.
5. Run quality-of-authoring rules (R026-R030).
6. Write the report.
7. Return the appropriate exit code.

7. Dependencies

- Core Ontology: GO-001
- Test suite: GTEST-001
- PKG Validator: GVAL-001 (calls GVAL-002 for semantic checks)
- Compiler: GCMP-001 (consumes compiled ontology representation)