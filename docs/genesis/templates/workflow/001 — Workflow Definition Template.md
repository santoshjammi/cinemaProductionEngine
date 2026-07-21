Genesis Template (GTMP)
GTMP-006 — Workflow Definition Template

Document ID: GTMP-006
Title: Workflow Definition Template
Version: 1.0.0
Status: Template
Authority: Derived from GFS-000

1. Purpose

Blank template for a Genesis workflow definition. Workflows orchestrate agents,
validators, and compilers into ordered, repeatable processes. Place finished
workflows in `workflows/<type>/` with the GWS-NNN scheme.

2. Template

```
Genesis Workflow (GWS)
GWS-NNN — <WorkflowName>

Document ID: GWS-NNN
Title: <WorkflowName>
Version: 1.0.0
Status: Draft | Validated | Active
Authority: Derived from GFS-000

1. Purpose
<One paragraph describing what this workflow achieves.>

2. Trigger
- Event: <event name>
- Source: <agent, CLI, upstream workflow>
- Pre-conditions:
  - <condition>

3. Inputs
- <input> — <type> — <required | optional>

4. Stages
For each stage:
- Stage N: <stageName>
- Agent: GAS-NNN
- Inputs: <list>
- Outputs: <list>
- Quality gate: GVAL-NNN
- On failure: <retry | escalate | abort>

5. Order
1. <stage 1>
2. <stage 2> (depends on stage 1)
3. <stage 3> (depends on stage 2)

6. Parallelism
- Stages that may run concurrently: <list>
- Stages that must be serial: <list>

7. Outputs
- <output> — <type> — <destination>

8. Quality Gates
- Pre-stage gates: <GVAL-NNN list>
- Post-stage gates: <GVAL-NNN list>
- Final gate: <GVAL-NNN>

9. Rollback
- On abort: <action>
- On unrecoverable failure: <action>

10. Observability
- Metrics emitted: <list>
- Log fields: <list>
- Trace spans: <list>

11. Dependencies
- Workflows: <GWS-NNN list>
- Agents: <GAS-NNN list>
- Validators: <GVAL-NNN list>
```

3. Usage Notes

- Every stage must declare a quality gate.
- The Full Production Workflow (GWS-001) is the baseline; all others compose from it.
- Workflows must be deterministic given the same inputs and PKG state.