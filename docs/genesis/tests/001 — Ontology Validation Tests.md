Genesis Test (GTEST)
GTEST-001 — Ontology Validation Tests

Document ID: GTEST-001
Title: Ontology Validation Tests
Version: 1.0.0
Status: Active
Authority: Derived from GFS-000

1. Purpose

Test cases that every ontology file (GO-NNN) and ontology extension (GOX-NNN)
must pass before being promoted to Validated or Canonical. These tests
operationalize the rules defined in the Core Ontology (GO-001) and the
Ontology Validator (GVAL-002).

2. Scope

- Applies to all files in `ontology/` and `ontology/*/extensions/`.
- Does not test schema conformance (covered by GTEST-002).
- Does not test agent behavior (covered by GTEST-003).

3. Test Cases

T001 — Header block present
- Given: an ontology file
- When: parsed
- Then: Document ID, Title, Version, Status, Authority fields are present and non-empty
- Severity: Block

T002 — Document ID matches filename
- Given: file `ontology/<domain>/GO-NNN — <Title>.md`
- When: parsed
- Then: Document ID equals `GO-NNN`
- Severity: Block

T003 — Derives from GO-001
- Given: any ontology file
- When: parsed
- Then: Authority field contains "Derived from GO-001" OR a chain that traces to GO-001
- Severity: Block

T004 — At least one class defined
- Given: an ontology file
- When: parsed
- Then: the Classes section contains at least one class definition
- Severity: Block

T005 — Every class has a name and description
- Given: a class definition
- When: parsed
- Then: Name and Description are non-empty
- Severity: Block

T006 — Parent class resolves
- Given: a class with a Parent field
- When: Parent is not None
- Then: Parent resolves to a class defined in this ontology or a parent ontology
- Severity: Block

T007 — No duplicate class names within an ontology
- Given: an ontology file
- When: parsed
- Then: all class names are unique within the file
- Severity: Block

T008 — No duplicate relationship names within an ontology
- Given: an ontology file
- When: parsed
- Then: all relationship names are unique within the file
- Severity: Block

T009 — Relationship domain and range resolve
- Given: a relationship definition
- When: parsed
- Then: Domain and Range resolve to classes in this or a parent ontology
- Severity: Block

T010 — Cardinality is one of the allowed forms
- Given: a relationship
- When: parsed
- Then: Cardinality is one of {1:1, 1:N, M:N}
- Severity: Block

T011 — No contradiction with parent ontology
- Given: an ontology that extends a parent
- When: compared with the parent
- Then: no class is removed, no relationship is reversed, no rule is negated
- Severity: Block

T012 — Classification tiers present
- Given: an ontology file
- When: parsed
- Then: Classification Tiers section lists all five tiers: Explicit, Inferred, Confirmed, Assumed, Unknown
- Severity: Warn

T013 — Traceability section present
- Given: an ontology file
- When: parsed
- Then: Traceability section records origin, evidence, and confidence threshold
- Severity: Warn

T014 — Validation section present
- Given: an ontology file
- When: parsed
- Then: Validation section lists structural, semantic, completeness, and confidence checks
- Severity: Warn

T015 — Extension backward compatibility
- Given: a GOX-NNN extension file
- When: compared with its parent GO-NNN
- Then: Backward Compatibility section is present and all parent rules remain satisfiable
- Severity: Block

T016 — No naming collisions with parent
- Given: a GOX-NNN extension
- When: parsed
- Then: no new class or relationship name collides with a name in the parent ontology
- Severity: Block

4. Fixtures

- `tests/fixtures/ontology/minimal-valid.yml` — passes all tests
- `tests/fixtures/ontology/missing-header.yml` — fails T001
- `tests/fixtures/ontology/duplicate-class.yml` — fails T007
- `tests/fixtures/ontology/bad-cardinality.yml` — fails T010

5. Execution

```
genesis test --suite ontology
```

6. Exit Criteria

- All Block-severity tests pass.
- Warn-severity tests pass or are explicitly waived in the ontology's Status note.
- Output is a JSON report written to `tests/reports/GTEST-001-<timestamp>.json`.