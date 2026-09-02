Genesis Template (GTMP)
GTMP-005 — Agent Specification Template

Document ID: GTMP-005
Title: Agent Specification Template
Version: 1.0.0
Status: Template
Authority: Derived from GFS-000

1. Purpose

Blank template for creating a new agent specification. Copy this into
`agents/<role>/` with the GAS-NNN scheme. Every agent in Genesis must have a
specification before it can be deployed or invoked.

2. Template

```
Genesis Agent Specification (GAS)
GAS-NNN — <AgentName>

Document ID: GAS-NNN
Title: <AgentName>
Version: 1.0.0
Status: Draft | Validated | Active
Authority: Derived from GFS-000

1. Identity
- Name: <AgentName>
- Role: <Orchestrator | Architect | Engineer | Validator | Researcher | Reviewer>
- Tier: <1 | 2 | 3>
- Reports to: <GAS-NNN or Orchestrator>

2. Purpose
<One paragraph describing the agent's reason to exist.>

3. Responsibilities
- <responsibility>
- <responsibility>
- <responsibility>

4. Inputs
- Required:
  - <input> — <type> — <source>
- Optional:
  - <input> — <type> — <source>

5. Outputs
- <output> — <type> — <destination>
- <output> — <type> — <destination>

6. Procedures
For each procedure:
- Name: <procedureName>
- Trigger: <when this runs>
- Steps:
  1. <step>
  2. <step>
- Exit criteria:
  - <criterion>

7. Quality Criteria
- <criterion> — measured by <metric>
- <criterion> — measured by <metric>

8. Dependencies
- Agents: <GAS-NNN list>
- Ontologies: <GO-NNN list>
- Schemas: <GSS-NNN list>
- Workflows: <GWS-NNN list>

9. Failure Modes
- <failure> — mitigation: <action>
- <failure> — mitigation: <action>

10. Invocation Contract
- Canonical prompt: GPROMPT-NNN
- Tool access: <list>
- Side effects: <none | writes to PKG | writes to filesystem>

11. Classification Handling
- Explicit / Inferred / Confirmed / Assumed / Unknown tagging on all outputs.

12. Traceability
- Every output must record origin, evidence, confidence, and revision.
```

3. Usage Notes

- All agents are stateless across invocations unless explicitly noted.
- No agent may perform media generation (GFS-000 §15).
- Every agent must declare which tier of the orchestration hierarchy it belongs to.