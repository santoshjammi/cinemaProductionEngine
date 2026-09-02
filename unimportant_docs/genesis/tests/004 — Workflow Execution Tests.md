Genesis Test (GTEST)
GTEST-004 — Workflow Execution Tests

Document ID: GTEST-004
Title: Workflow Execution Tests
Version: 1.0.0
Status: Active
Authority: Derived from GFS-000

1. Purpose

Test cases for Genesis workflow execution. These verify that workflows (GWS-NNN)
run their stages in the correct order, honor quality gates, and produce the
declared outputs. They do not verify full production correctness (covered by
GTEST-005).

2. Scope

- Applies to all workflows defined by GWS-NNN.
- Applies to orchestrators executing those workflows.
- Does not test end-to-end production runs (covered by GTEST-005).

3. Test Cases

T001 — Workflow spec exists and is Active
- Given: a workflow invocation
- When: the orchestrator resolves the workflow
- Then: a GWS-NNN spec exists with Status = Active
- Severity: Block

T002 — Trigger pre-conditions satisfied
- Given: a workflow invocation
- When: pre-conditions are evaluated
- Then: all pre-conditions are true; otherwise the workflow does not start
- Severity: Block

T003 — Stage order respected
- Given: a workflow with declared stage order
- When: executed
- Then: no stage runs before its declared dependencies complete
- Severity: Block

T004 — Parallelism honored
- Given: a workflow with declared parallel stages
- When: executed
- Then: only declared-parallel stages run concurrently; all others run serially
- Severity: Block

T005 — Pre-stage quality gates enforced
- Given: a stage with a pre-stage gate
- When: the gate is evaluated
- Then: the stage does not start unless the gate passes
- Severity: Block

T006 — Post-stage quality gates enforced
- Given: a stage with a post-stage gate
- When: the stage produces output
- Then: the gate runs and the stage is not marked complete unless it passes
- Severity: Block

T007 — Final gate enforced
- Given: a workflow with a final gate
- When: all stages complete
- Then: the final gate runs and the workflow is not marked complete unless it passes
- Severity: Block

T008 — On-failure action honored
- Given: a stage that fails
- When: the failure is reported
- Then: the workflow performs the declared On-failure action (retry | escalate | abort)
- Severity: Block

T009 — Rollback executed on abort
- Given: a workflow that aborts
- When: abort is triggered
- Then: the declared Rollback action runs and PKG state is restored or marked invalid
- Severity: Block

T010 — Outputs match declaration
- Given: a completed workflow
- When: outputs are collected
- Then: every output declared in the workflow spec is present and schema-valid
- Severity: Block

T011 — Determinism
- Given: the same workflow run twice with identical inputs and identical PKG state
- When: outputs are compared
- Then: outputs are identical
- Severity: Block

T012 — Metrics emitted
- Given: a workflow execution
- When: each stage completes
- Then: the metrics declared in the Observability section are emitted
- Severity: Warn

T013 — Trace spans emitted
- Given: a workflow execution
- When: each stage runs
- Then: a trace span is emitted with workflow ID, stage ID, and duration
- Severity: Warn

T014 — No undeclared stages
- Given: a workflow execution
- When: monitored
- Then: no agent or stage outside the workflow spec is invoked
- Severity: Block

T015 — Workflow composes with GWS-001
- Given: any workflow other than GWS-001
- When: analyzed
- Then: it either composes from GWS-001 stages or declares an explicit exception
- Severity: Block

4. Fixtures

- `tests/fixtures/workflow/minimal-valid-workflow.yaml`
- `tests/fixtures/workflow/failing-gate-workflow.yaml` — triggers T006
- `tests/fixtures/workflow/abort-rollback-workflow.yaml` — triggers T009

5. Execution

```
genesis test --suite workflow
genesis workflow run --id GWS-NNN --input <fixture>
```

6. Exit Criteria

- All Block-severity tests pass.
- Output is a JSON report at `tests/reports/GTEST-004-<timestamp>.json`.
- Each failure records the workflow ID, the stage, the gate, and the failed test ID.