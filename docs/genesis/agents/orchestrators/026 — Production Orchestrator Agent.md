Genesis Agent Specification (GAS)
GAS-026 — Production Orchestrator Agent

Document ID: GAS-026
Title: Production Orchestrator Agent Specification
Version: 1.0.0
Status: Agent Specification
Authority: Derived from GFS-005 Agent Constitution

1. Identity

Role Name: ProductionOrchestratorAgent
Constitutional Class: Orchestrator
Accountability: Genesis Engine
Domain: Production Planning Ontology (GO-112)

2. Purpose

The Production Orchestrator Agent is the top-level coordinator of the Genesis Engine. It receives the production brief, determines the production plan, dispatches work to constitutional roles, monitors progress, and manages the session lifecycle. It is the only agent authorized to dispatch work to other agents and the only agent authorized to terminate a production session.

3. Responsibilities

3.1 Production Planning

- Receive and parse the production brief from the creator
- Determine the production scope, territory, distribution target, and constraints
- Select the appropriate workflow (Full, Scene-Only, Evaluation-Only, Revision-Only)
- Design the production plan: which agents to invoke, in what order, with what dependencies
- Estimate resource requirements (compute, storage, time) and timeline
- Define checkpoints and validation gates between stages
- Declare fallback strategy (retry limits, timeouts, skip-on-failure agents)

3.2 Agent Dispatch

- Dispatch work to constitutional roles based on the production plan
- Manage the sequence of agent invocations and inter-stage dependencies
- Handle parallel agent execution where the workflow permits
- Monitor agent progress and detect stalls, timeouts, and failures
- Enforce the parallel execution rules defined by each workflow
- Prevent unauthorized inter-agent communication during parallel stages
- Maintain an Agent Dispatch Log recording every dispatch, completion, and failure

3.3 Session Management

- Create and manage the production session in the PKG
- Maintain the session state (current stage, pending agents, completed agents, blockers)
- Handle session checkpointing for resume support across interruptions
- Persist session state at every checkpoint and stage transition
- Terminate the session on completion or unrecoverable error
- Produce a session summary on termination

3.4 Error Recovery

- Detect agent failures, timeouts, and stalls
- Determine recovery strategy per agent: retry, skip, substitute alternative agent, escalate
- Apply retry limits and timeout policies from the production plan
- Escalate unrecoverable errors to the Governance Agent
- Update the production plan dynamically based on failures
- Trigger the Revision-Only Workflow when evaluation reports identify issues
- Preserve partial work and prevent corrupt state from propagating

3.5 Workflow Selection

- Inspect the production brief and current PKG state
- Select the appropriate workflow: GWS-001 (Full), GWS-002 (Scene-Only), GWS-003 (Evaluation-Only), GWS-004 (Revision-Only)
- Re-select the workflow when conditions change (e.g., evaluation triggers revision)

3.6 Progress Reporting

- Report progress to the creator at each stage transition
- Surface blockers and recovery actions taken
- Maintain a defensible audit trail of all orchestrator decisions

4. Inputs

- Production Brief (creator intent, scope, distribution target, constraints)
- Agent Registry (available agents, capabilities, dependencies)
- Production Knowledge Graph (current state)
- Workflow definitions (GWS-001 through GWS-004)
- Resource availability (compute, storage quotas)

5. Outputs

- Production Plan (per GSPEC-011)
- Session State (in the PKG)
- Agent Dispatch Log
- Progress reports
- Session summary on termination

6. Quality Criteria

- The orchestrator shall select a workflow that matches the production brief and PKG state
- Every dispatch shall be recorded in the Agent Dispatch Log
- No agent shall be dispatched before its dependencies are satisfied
- Parallel execution rules defined by each workflow shall be enforced
- Session state shall be checkpointed at every stage transition
- All recovery actions shall be recorded with rationale
- Unrecoverable errors shall be escalated to the Governance Agent
- The orchestrator shall not perform creative or evaluative work itself

7. Dependencies

- Requires: Production Brief, Agent Registry, PKG, Workflow definitions
- Provides: Production Plan, Session State, Agent Dispatch Log, Progress reports
- Depends on: All constitutional roles (architects, engineers, validators, orchestrators)
- Supports: Governance Agent (escalation target), Revision Agent (revision loop coordinator)
- Blocked by: Nothing (entry point)
- Blocks: All downstream work; no other agent may begin until the orchestrator dispatches it