Genesis Validator (GVAL)
GVAL-001 — PKG Validator

Document ID: GVAL-001
Title: PKG Validator
Version: 1.0.0
Status: Active
Authority: Derived from GFS-000

1. Purpose

The PKG Validator is the engine that verifies a Production Knowledge Package
(PKG) is structurally sound, semantically consistent, and complete enough to
be certified for production handoff. It is the primary gate before the
Ontology Validator (GVAL-002) and the Quality Gates (GVAL-003).

2. Scope

- Operates on an assembled PKG directory (the output of `genesis compile --pkg`).
- Does not validate individual ontology files (covered by GVAL-002).
- Does not evaluate production readiness thresholds (covered by GVAL-003).

3. Inputs

- `--pkg <dir>`: the PKG directory.
- `--config <file>`: optional override of validation config.

4. Outputs

- JSON report at `<pkg>/validation/pkg-report.json`.
- Exit code 0 only if all Block-severity checks pass.
- Report fields:
  - `pkg_id`, `validated_at`, `validator_version`
  - `checks`: array of `{id, severity, passed, message, path}`
  - `summary`: `{block_passed, block_failed, warn_passed, warn_failed}`

5. Check Categories

### Structural Checks

S001 — Manifest present
- The PKG contains `manifest.yaml` conforming to GSS-NNN.
- Severity: Block

S002 — All manifest artifacts exist
- Every artifact referenced in the manifest is present on disk.
- Severity: Block

S003 — All artifacts are schema-valid
- Every artifact validates against its declared GSS-NNN schema.
- Severity: Block

S004 — No orphan artifacts
- Every file in the PKG directory is referenced by the manifest.
- Severity: Warn

S005 — Directory structure matches convention
- The PKG directory layout matches the declared convention (brief/, characters/, scenes/, world/, narrative/).
- Severity: Warn

### Semantic Checks

M001 — No unresolved references
- Every cross-artifact reference resolves to an existing artifact.
- Severity: Block

M002 — No classification conflicts
- An assertion is not tagged as both Explicit and Inferred in the same artifact.
- Severity: Block

M003 — Inverse relationships consistent
- If A relates to B, the inverse relationship from B to A is present and consistent.
- Severity: Block

M004 — No contradictions between artifacts
- No two artifacts assert mutually exclusive facts about the same entity.
- Severity: Block

M005 — Inference chains acyclic
- Inferred assertions do not form a cycle of dependencies.
- Severity: Block

### Completeness Checks

C001 — All required production brief fields populated
- The Production Brief has all required fields non-empty per GSPEC-001.
- Severity: Block

C002 — Every named character has a Character DNA
- Every character named in the brief or scenes has a Character DNA artifact.
- Severity: Block

C003 — Every scene has a scene specification
- Every scene referenced in the narrative has a scene specification artifact.
- Severity: Block

C004 — All required decisions present
- Every decision declared as required by the workflow is present in the PKG.
- Severity: Block

C005 — All required decisions meet confidence threshold
- Every required decision's confidence is at or above its declared threshold.
- Severity: Block

### Traceability Checks

T001 — Every decision has origin
- Every decision in the PKG records its origin (agent, workflow, or human).
- Severity: Block

T002 — Every decision has evidence
- Every decision records the evidence supporting it.
- Severity: Block

T003 — Every decision has alternatives
- Every significant decision records alternatives considered.
- Severity: Warn

T004 — Every decision has confidence
- Every decision records a confidence value.
- Severity: Block

T005 — Every decision has revision history
- Every decision records at least one revision entry.
- Severity: Warn

6. Execution Model

1. Load manifest.
2. Run structural checks (S001-S005).
3. If any Block structural check fails, halt and report.
4. Run semantic checks (M001-M005).
5. Run completeness checks (C001-C005).
6. Run traceability checks (T001-T005).
7. Write the report.
8. Return the appropriate exit code.

7. Dependencies

- Schemas: GSS-NNN set
- Ontology Validator: GVAL-002 (delegated for semantic class checks)
- Compiler: GCMP-001 (to assemble the PKG before validation)
- CLI: GTOOL-001 (entry point)