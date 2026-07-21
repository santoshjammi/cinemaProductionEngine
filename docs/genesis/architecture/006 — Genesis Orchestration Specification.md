Genesis Architecture Specification (GAS)
GARCH-006 — Genesis Orchestration Specification

Document ID: GARCH-006
Title: Genesis Orchestration Specification
Version: 1.0.0
Status: Architecture Specification
Authority: Derived from GARCH-001, GARCH-002, GFS-005, GFS-006, GFS-007

1. Purpose

This document specifies how agents are coordinated inside Genesis. It defines the execution flow, the review loops, the conflict resolution procedures, and the completion gates that govern every workflow from initial creative intent to certified Production Knowledge Package.

Orchestration is the responsibility of the Workflow Engine (S6) operating above the Agent Runtime (S5). Agents never invoke one another. The Workflow Engine is the sole dispatcher.

2. Orchestration Model

Genesis uses a *task-graph orchestration* model:

- A workflow is a directed graph of tasks.
- Each task is bound to exactly one agent (GAS-NNN).
- Each task declares its input subgraph, its expected outputs, and its completion criteria.
- Tasks execute when their input predicates are satisfied by the PKG.
- Task results are written to the PKG before downstream tasks become eligible.

This model is deterministic in ordering, asynchronous in execution, and replayable from any checkpoint.

3. Execution Flow

3.1 Intake
The Production Orchestrator (GAS-026) receives creative intent and registers a new production in the PKG. An initial confidence classification of UNKNOWN is assigned to every asserted concept pending reasoning.

3.2 Discovery
The Research Agent (GAS-007) and Story Architect (GAS-001) decompose intent into a narrative spine, themes, and known unknowns. Gaps are recorded as explicit Unknown nodes in the PKG.

3.3 Expansion
Architects (GAS-002, GAS-003, GAS-010, GAS-024) expand the narrative into scenes, beats, shots, and score plans. Each expansion is an assertion with provenance and confidence.

3.4 Validation
Validators (GAS-017 through GAS-023) score the expanded subgraphs. Findings are written as Validation Finding nodes referencing the offending assertions.

3.5 Review
Reviewers (GAS-009) provide adversarial critique. Review findings are first-class PKG nodes and may block progression.

3.6 Governance
The Governance Engine inspects the PKG for constitutional compliance, ontology conformance, and approval state. It issues or withholds approval.

3.7 Certification
When all gates pass, the Production Publisher (GAS-P01) materializes the PKP and signs it. The PKP is frozen and emitted to the Studio Engine.

4. Review Loops

Every validation or review finding opens a review loop:

- The Workflow Engine routes the finding to the responsible agent (the agent whose assertion was flagged).
- The agent revises the assertion, producing a new revision with new provenance.
- The validator re-runs against the revised subgraph.
- The loop terminates when the finding is closed or escalated.

Loops are bounded. After N iterations (default N=3) without convergence, the finding is escalated to the Governance Engine for adjudication.

5. Conflict Resolution

Conflicts arise when two agents assert contradictory facts about the same concept (e.g., two character profiles for the same character ID). Resolution proceeds as follows:

5.1 Detection
The Validation Engine detects conflicts via ontology constraints and semantic relationship checks (GO-002).

5.2 Ranking
Assertions are ranked by confidence classification, provenance weight, and recency. EXPLICIT > CONFIRMED > INFERRED > ASSUMED > UNKNOWN.

5.3 Reconciliation
The higher-ranked assertion prevails. The lower-ranked assertion is marked superseded but retained in history.

5.4 Escalation
If ranks are equal, the conflict is escalated to the Governance Engine, which may request a Reviewer or Research Agent to break the tie with new evidence.

5.5 Recording
Every conflict and its resolution is recorded in the Audit Log and reflected in the PKP.

6. Completion Gates

A production is eligible for certification only when all of the following gates pass:

- G1 Completeness — every required ontology concept has at least one instance.
- G2 Confidence — every assertion required for production has confidence >= INFERRED.
- G3 Validation — no open validation findings with severity >= blocking.
- G4 Review — no open review findings.
- G5 Governance — explicit governance approval recorded.
- G6 Provenance — every assertion carries complete provenance.
- G7 Consistency — no unresolved conflicts.
- G8 Handoff readiness — all Studio Engine inputs derivable from the PKG.

Any failed gate blocks certification. The Workflow Engine routes the failure back to the appropriate agent.

7. Checkpointing

The Workflow Engine checkpoints at every task boundary:

- The current task graph state is persisted.
- The PKG revision ID is recorded.
- Pending tasks are listed.
- The checkpoint is immutable.

Checkpointing enables resumption after crashes, replay for audit, and rollback for governance investigations.

8. Error Handling

Errors are categorized as:

- Agent errors — the agent produced a malformed assertion. Routed back to the agent with a structured failure report.
- Validation errors — the PKG violates a constraint. Routed to the responsible agent.
- Governance errors — a constitutional violation. Routed to the Governance Engine.
- System errors — runtime failure. The Workflow Engine retries with backoff, then escalates.

No error is silently swallowed. Every error is recorded in the Audit Log with its category, context, and resolution.

9. Concurrency

Multiple tasks may execute concurrently when their input subgraphs are disjoint. The Workflow Engine enforces serialization only when tasks write to overlapping subgraphs. Concurrency is bounded by the Agent Runtime configuration.

10. Replay and Audit

Every workflow execution is replayable from its checkpoints. Replay reproduces the exact sequence of assertions, findings, and governance decisions. The Audit Log is the authoritative record; the PKG is the authoritative state.

11. Approval

This specification is binding for all workflow definitions and all agent dispatchers operating inside Genesis.