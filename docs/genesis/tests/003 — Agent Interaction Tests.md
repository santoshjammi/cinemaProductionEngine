Genesis Test (GTEST)
GTEST-003 — Agent Interaction Tests

Document ID: GTEST-003
Title: Agent Interaction Tests
Version: 1.0.0
Status: Active
Authority: Derived from GFS-000

1. Purpose

Test cases for agent-to-agent and agent-to-orchestrator communication inside
Genesis. These tests verify that agents honor their invocation contracts, emit
correctly tagged outputs, and escalate correctly when confidence thresholds are
not met.

2. Scope

- Applies to all agents defined by GAS-NNN specifications.
- Applies to orchestrators that invoke agents per GWS-NNN workflows.
- Does not test full workflow execution (covered by GTEST-004).
- Does not test end-to-end production (covered by GTEST-005).

3. Test Cases

T001 — Agent spec exists
- Given: an agent is invoked
- When: the orchestrator resolves the agent
- Then: a GAS-NNN spec exists and is Active
- Severity: Block

T002 — Canonical prompt exists
- Given: an agent is invoked
- When: the orchestrator resolves the prompt
- Then: a GPROMPT-NNN exists whose Authority derives from the agent's GAS-NNN
- Severity: Block

T003 — Inputs satisfy the agent's required list
- Given: an agent invocation request
- When: validated against the agent's Inputs.Required list
- Then: all required inputs are present and type-correct
- Severity: Block

T004 — Output validates against declared schema
- Given: an agent produces output
- When: validated against the schema declared in the agent's Outputs
- Then: validation succeeds with zero errors
- Severity: Block

T005 — Output carries classification tags
- Given: an agent output containing assertions
- When: parsed
- Then: every assertion is tagged as Explicit, Inferred, Confirmed, Assumed, or Unknown
- Severity: Block

T006 — Output carries traceability
- Given: an agent output
- When: parsed
- Then: every output record contains origin, evidence, confidence, and revision
- Severity: Block

T007 — Confidence threshold respected
- Given: an agent with a confidence threshold defined in its spec
- When: the agent's output confidence is below threshold
- Then: the agent escalates rather than promoting the output to Confirmed
- Severity: Block

T008 — No media generation
- Given: any agent invocation
- When: the agent runs
- Then: no image, audio, video, or voice asset is produced
- Severity: Block

T009 — Stateless across invocations
- Given: the same agent invoked twice with identical inputs and identical PKG state
- When: outputs are compared
- Then: outputs are identical
- Severity: Block

T010 — Escalation path honored
- Given: an agent that fails to meet exit criteria
- When: failure is reported
- Then: the orchestrator routes the failure to the agent declared in the spec's Reports-to
- Severity: Block

T011 — Side effects declared
- Given: an agent invocation
- When: the agent runs
- Then: any write to the PKG or filesystem matches the spec's Invocation Contract
- Severity: Block

T012 — Orchestrator fan-out correctness
- Given: an orchestrator that fans out to multiple agents
- When: the agents complete
- Then: the orchestrator merges outputs without losing classification tags or traceability
- Severity: Block

T013 — Agent timeout
- Given: an agent with a declared timeout
- When: execution exceeds the timeout
- Then: the orchestrator aborts the agent and records the failure
- Severity: Warn

T014 — Retry policy honored
- Given: an agent with a retry policy
- When: a transient failure occurs
- Then: the orchestrator retries per the policy and does not exceed the declared limit
- Severity: Warn

T015 — No undeclared dependencies
- Given: an agent invocation
- When: the agent runs
- Then: the agent does not read from or write to any resource not declared in its Dependencies
- Severity: Block

4. Fixtures

- `tests/fixtures/agent/mock-orchestrator.yaml`
- `tests/fixtures/agent/sample-character-architect-input.json`
- `tests/fixtures/agent/sample-character-architect-output.json`
- `tests/fixtures/agent/low-confidence-output.json` — triggers T007

5. Execution

```
genesis test --suite agent
genesis test --agent GAS-NNN --input <fixture>
```

6. Exit Criteria

- All Block-severity tests pass.
- Output is a JSON report at `tests/reports/GTEST-003-<timestamp>.json`.
- Each failure records the agent ID, the input fixture, and the failed test ID.