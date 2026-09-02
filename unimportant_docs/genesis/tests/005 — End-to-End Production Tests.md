Genesis Test (GTEST)
GTEST-005 — End-to-End Production Tests

Document ID: GTEST-005
Title: End-to-End Production Tests
Version: 1.0.0
Status: Active
Authority: Derived from GFS-000

1. Purpose

End-to-end test cases that verify Genesis can take a synopsis and constraints,
run the Full Production Workflow (GWS-001), and produce a certified,
production-ready Production Knowledge Package (PKG) without manual intervention.

2. Scope

- Exercises the entire Genesis pipeline from Production Brief ingestion to PKG
  certification.
- Uses real agents (GAS-NNN), workflows (GWS-NNN), validators (GVAL-NNN), and
  the compiler (GCMP-NNN).
- Does not exercise downstream Movie OS Studio Engine (covered separately).

3. Test Cases

T001 — Synopsis-to-Brief ingestion
- Given: a raw synopsis and constraints
- When: ingested by Genesis
- Then: a Production Brief conforming to GSPEC-001 is produced and schema-valid
- Severity: Block

T002 — Discovery completes
- Given: a valid Production Brief
- When: the Discovery workflow runs
- Then: missing knowledge is identified as questions with declared impact
- Severity: Block

T003 — Reasoning completes
- Given: discovery output
- When: the Reasoning workflow runs
- Then: inferred knowledge is produced with classification tags and confidence
- Severity: Block

T004 — Character DNA produced
- Given: a production in reasoning
- When: the Character Architect agent runs
- Then: a Character DNA is produced for every named character, conforming to GSS-NNN
- Severity: Block

T005 — Scene specifications produced
- Given: a reasoned production
- When: the Scene Architect agent runs
- Then: scene specifications are produced conforming to GSS-NNN
- Severity: Block

T006 — World knowledge produced
- Given: a reasoned production
- When: the World Architect agent runs
- Then: world knowledge is produced conforming to the relevant ontology
- Severity: Block

T007 — PKG assembled
- Given: all stage outputs
- When: the compiler runs
- Then: a PKG manifest is produced and all referenced artifacts exist
- Severity: Block

T008 — PKG validation passes
- Given: an assembled PKG
- When: the PKG Validator (GVAL-001) runs
- Then: structural, semantic, and completeness checks all pass
- Severity: Block

T009 — Ontology validation passes
- Given: a complete PKG
- When: the Ontology Validator (GVAL-002) runs
- Then: all assertions conform to their governing ontologies
- Severity: Block

T010 — Quality gates pass
- Given: a complete PKG
- When: the Quality Gates (GVAL-003) are evaluated
- Then: every gate required for production readiness passes
- Severity: Block

T011 — Consistency override
- Given: a complete PKG
- When: consistency analysis runs
- Then: no unresolved contradictions exist; any contradiction was resolved before certification
- Severity: Block

T012 — Confidence thresholds met
- Given: a complete PKG
- When: confidence is aggregated
- Then: every required decision meets its declared confidence threshold
- Severity: Block

T013 — Traceability complete
- Given: a complete PKG
- When: traceability is audited
- Then: every decision records origin, evidence, alternatives, confidence, and revision
- Severity: Block

T014 — Certification issued
- Given: a PKG that passes T008-T013
- When: the governance agent runs
- Then: a Production Readiness Certificate is issued
- Severity: Block

T015 — No media artifacts produced
- Given: a complete end-to-end run
- When: the output directory is inspected
- Then: zero image, audio, video, or voice assets are present
- Severity: Block

T016 — Handoff manifest present
- Given: a certified PKG
- When: inspected
- Then: a handoff manifest for Movie OS Studio Engine is present and schema-valid
- Severity: Block

T017 — Determinism across runs
- Given: the same synopsis and constraints run twice on a fresh PKG
- When: the two PKGs are compared
- Then: structurally equivalent (same nodes, same edges, same classifications)
- Severity: Warn

4. Fixtures

- `tests/fixtures/e2e/synopsis-night-he-stopped-reaching.md`
- `tests/fixtures/e2e/constraints-default.yaml`
- `tests/fixtures/e2e/expected-pkg-structure.json`

5. Execution

```
genesis test --suite e2e
genesis run --synopsis <fixture> --constraints <fixture> --output pkg/
```

6. Exit Criteria

- All Block-severity tests pass.
- A PKG is produced at the declared output path.
- A Production Readiness Certificate is produced.
- Output is a JSON report at `tests/reports/GTEST-005-<timestamp>.json`.
- The PKG is ready for handoff to Movie OS Studio Engine per GINT-003.