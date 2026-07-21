Genesis Validator (GVAL)
GVAL-003 — Quality Gates

Document ID: GVAL-003
Title: Quality Gates
Version: 1.0.0
Status: Active
Authority: Derived from GFS-000

1. Purpose

Defines the quality gates that must pass before each stage of a Genesis
production can advance. A gate is a binary decision: pass or fail. Gates are
evaluated by the orchestrator before transitioning between workflow stages and
before certification.

2. Scope

- Applies to all workflows (GWS-NNN).
- Applies to PKG certification (`genesis certify`).
- Gates are declarative; they do not implement logic. Logic lives in the
  validators (GVAL-001, GVAL-002) and the agents.

3. Gate Model

Every gate has:
- `id`: GVAL-003-G<NN>
- `name`: human-readable
- `stage`: the workflow stage it guards
- `evaluator`: the validator or check that produces the pass/fail
- `severity`: Block | Warn
- `on_fail`: retry | escalate | abort
- `remediation`: link to a guide or agent

4. Gate Catalog

### Discovery → Reasoning

G01 — Brief validity gate
- Evaluator: GVAL-001 (S001-S005 against the brief)
- Severity: Block
- On fail: abort
- Remediation: re-author the brief

G02 — Discovery completeness gate
- Evaluator: discovery agent declares all material questions identified
- Severity: Block
- On fail: retry

### Reasoning → Architecture

G03 — Reasoning confidence gate
- Evaluator: every inferred assertion has confidence ≥ 0.6 OR is escalated
- Severity: Block
- On fail: escalate

G04 — Consistency gate
- Evaluator: GVAL-001 (M001-M005)
- Severity: Block
- On fail: abort

### Architecture → Compilation

G05 — Character DNA gate
- Evaluator: every named character has a schema-valid Character DNA
- Severity: Block
- On fail: retry

G06 — Scene specification gate
- Evaluator: every scene has a schema-valid scene specification
- Severity: Block
- On fail: retry

G07 — World knowledge gate
- Evaluator: world knowledge schema-valid and consistent with the narrative
- Severity: Block
- On fail: retry

### Compilation → Validation

G08 — PKG assembly gate
- Evaluator: GVAL-001 (S001-S005)
- Severity: Block
- On fail: abort

### Validation → Certification

G09 — PKG validation gate
- Evaluator: GVAL-001 all Block checks pass
- Severity: Block
- On fail: abort

G10 — Ontology conformance gate
- Evaluator: GVAL-002 all Block checks pass
- Severity: Block
- On fail: abort

G11 — Completeness gate
- Evaluator: GVAL-001 (C001-C005)
- Severity: Block
- On fail: retry

G12 — Traceability gate
- Evaluator: GVAL-001 (T001-T005) Block checks pass
- Severity: Block
- On fail: retry

G13 — Confidence threshold gate
- Evaluator: every required decision meets its declared confidence threshold
- Severity: Block
- On fail: escalate

### Certification → Handoff

G14 — No unresolved contradictions gate
- Evaluator: GVAL-001 (M004) zero unresolved
- Severity: Block
- On fail: abort

G15 — No media artifacts gate
- Evaluator: PKG output directory contains zero image/audio/video/voice assets
- Severity: Block
- On fail: abort

G16 — Handoff manifest gate
- Evaluator: handoff manifest for Movie OS Studio Engine is present and schema-valid
- Severity: Block
- On fail: retry

5. Evaluation Order

For a given stage transition, the orchestrator evaluates gates in declaration
order. The first Block-severity failure halts the transition and triggers the
declared `on_fail` action. Warn-severity failures are recorded but do not halt.

6. Gate Extension

New gates are added by editing this document and bumping its version. A gate
cannot be removed without a superseding ADR (ADR-NNN) explaining why.

7. Dependencies

- Validators: GVAL-001, GVAL-002
- Workflows: GWS-001 and all composed workflows
- Certification: `genesis certify` (GTOOL-001)
- Handoff: GINT-003