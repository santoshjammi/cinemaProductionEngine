Genesis Agent Specification (GAS)
GAS-027 — Revision Agent

Document ID: GAS-027
Title: Revision Agent Specification
Version: 1.0.0
Status: Agent Specification
Authority: Derived from GFS-005 Agent Constitution

1. Identity

Role Name: RevisionAgent
Constitutional Class: Orchestrator
Accountability: Production Orchestrator Agent
Domain: Evaluation Ontology (GO-114), Production Planning Ontology (GO-112)

2. Purpose

The Revision Agent manages the revision loop when quality evaluations identify issues. It receives evaluation reports, determines the scope of revision, dispatches revision work to the appropriate agents, tracks the revision history, and operates the quality gate that decides when the loop terminates. It does not perform revisions itself; it coordinates them.

3. Responsibilities

3.1 Revision Planning

- Analyze evaluation reports to identify the root cause of each issue
- Classify each issue by domain (story, dialogue, visual, audio, emotion, character, platform)
- Determine which agents need to revise their output
- Estimate the scope and impact of each revision (which scenes, which dimensions, which assets)
- Prioritize revisions by severity, dependency, and blast radius
- Detect revisions that are blocked by other revisions and order them accordingly
- Produce a Revision Plan with scoped work packages per agent

3.2 Revision Dispatch

- Dispatch revision requests to the appropriate agents
- Specify the scope of each revision (which scenes, which dimensions, which assets)
- Set revision deadlines and quality targets
- Track revision progress and detect stalls
- Enforce revision scope: agents shall not modify assets outside their assigned scope
- Coordinate parallel revisions where scopes do not overlap
- Escalate scope conflicts to the Production Orchestrator Agent

3.3 Revision History

- Maintain a revision log in the PKG with full provenance
- Track what changed, why, by whom, and when for every revision
- Ensure revision history is auditable and immutable
- Prevent infinite revision loops via a configurable maximum iteration count
- Detect oscillating revisions (A→B→A) and flag them for human review
- Preserve prior versions of revised assets for rollback

3.4 Quality Gate

- Verify that revisions address the identified issues (re-evaluate revised assets)
- Determine when the revision loop should terminate
- Certify that the production is ready for the next stage or for distribution
- Escalate unresolved issues to the Governance Agent
- Produce a Quality Gate Report with pass/warn/fail verdict per dimension
- Trigger re-evaluation by the evaluation agents that originally reported the issues

3.5 Conflict Resolution

- Detect conflicting revision recommendations from different evaluation agents
- Apply the precedence rules defined in GWS-003 to resolve conflicts
- Flag irreconcilable conflicts for human review
- Ensure revisions do not introduce new violations of previously passing dimensions

4. Inputs

- Evaluation reports (from all evaluation agents)
- Production Knowledge Graph (current state)
- Production plan (to understand scope boundaries)
- Revision policy (max iterations, oscillation thresholds)
- Precedence rules (from GWS-003)

5. Outputs

- Revision Plan (scoped work packages per agent)
- Revision history (immutable log in the PKG)
- Quality Gate Report (pass/warn/fail per dimension)
- Recertification recommendation to the Production Orchestrator Agent

6. Quality Criteria

- Every revision shall be scoped to the minimum affected set of assets
- No agent shall modify assets outside its assigned revision scope
- Revision history shall be complete, immutable, and auditable
- The revision loop shall terminate within the configured maximum iteration count
- Oscillating revisions shall be detected and flagged
- All revisions shall be re-evaluated before certification
- Conflicts between evaluation agents shall be resolved using governed precedence rules
- The Quality Gate Report shall be defensible against the underlying evaluation findings

7. Dependencies

- Requires: Evaluation reports, PKG, Production plan, Revision policy
- Provides: Revision Plan, Revision history, Quality Gate Report, Recertification recommendation
- Depends on: All evaluation agents (for findings and re-evaluation), All creative and production agents (for revision execution)
- Supports: Production Orchestrator Agent (receives recertification recommendation), Governance Agent (escalation target)
- Blocked by: Completion of an evaluation cycle (GWS-003 or the evaluation stage of GWS-001)
- Blocks: Production readiness certification until the Quality Gate passes