Genesis Master Specification
06 — Runtime

Document ID: GMS-006
Title: Genesis Master Specification — Runtime
Version: 1.0.0
Status: Master Specification
Authority: Derived from GARCH-002, GFS-005, GFS-007

1. Purpose

This document describes how Genesis runs: the session lifecycle, agent dispatch, the message bus, checkpointing, and error handling. It is the operational companion to the architecture documents.

2. Runtime Subsystems

The Genesis runtime consists of:

- Agent Runtime — hosts and dispatches constitutional agents.
- Workflow Engine — orchestrates multi-agent sequences.
- Message Bus — carries inter-agent and inter-subsystem communication.
- Knowledge Layer — mediates all PKG reads and writes.
- Validation Engine — continuously evaluates PKG integrity.
- Governance Engine — enforces approval gates.
- Materialization Service — produces derived views on demand.
- Persistence Adapters — graph database, provenance ledger, audit log.
- LLM Integration Layer — abstracts provider calls.
- CLI and API — operator and programmatic surfaces.

3. Session Lifecycle

A Genesis session is a single execution of a workflow against a production.

3.1 Open
A session is opened with a creative intent or a revision request. The Production Orchestrator (GAS-026) or Revision Agent (GAS-027) registers the session and binds it to a PKG root.

3.2 Run
The Workflow Engine dispatches tasks to agents. Agents read from the PKG, reason, and write assertions back. The Validation Engine runs continuously. Checkpoints are taken at every task boundary.

3.3 Review
Validation and review findings open review loops. Loops are bounded; unresolved loops escalate to the Governance Engine.

3.4 Approve
The Governance Engine inspects the PKG against the completion gates (GARCH-006). If all gates pass, it issues approval.

3.5 Certify
The Production Publisher (GAS-P01) assembles the PKP, signs it, and emits it to the Studio Engine.

3.6 Close
The session is closed. The PKG remains live for future revisions; the PKP is frozen.

4. Agent Dispatch

Agents are dispatched by the Workflow Engine, never by each other. Dispatch follows the task-graph model:

- A task is bound to exactly one agent (GAS-NNN).
- A task declares its input subgraph, expected outputs, and completion criteria.
- Tasks execute when their input predicates are satisfied by the PKG.
- Task results are written to the PKG before downstream tasks become eligible.

Dispatch is asynchronous and concurrent when input subgraphs are disjoint. The Workflow Engine serializes only when tasks write to overlapping subgraphs.

5. Message Bus

The Message Bus carries:

- Task dispatch events (Workflow Engine → Agent Runtime).
- Task completion events (Agent Runtime → Workflow Engine).
- Validation finding events (Validation Engine → Workflow Engine).
- Governance events (Governance Engine → Workflow Engine).
- Materialization requests (Publishers → Materialization Service).
- Audit events (all subsystems → Audit Log).

The bus is the sole inter-subsystem channel. No subsystem calls another directly except through the bus or the Knowledge Layer.

6. Checkpointing

The Workflow Engine checkpoints at every task boundary:

- Current task graph state.
- Current PKG revision ID.
- Pending tasks.
- Open findings.
- Last governance decision.

Checkpoints are immutable. They enable resumption after crashes, replay for audit, and rollback for governance investigations.

7. Error Handling

Errors are categorized:

- Agent errors — malformed assertion. Routed back to the agent with a structured failure report.
- Validation errors — PKG constraint violation. Routed to the responsible agent.
- Governance errors — constitutional violation. Routed to the Governance Engine.
- System errors — runtime failure. Retried with backoff, then escalated.

No error is silently swallowed. Every error is recorded in the Audit Log with category, context, and resolution.

8. Concurrency Model

- Agents are stateless; multiple instances may run concurrently.
- Tasks with disjoint input subgraphs run in parallel.
- Tasks with overlapping input subgraphs are serialized by the Workflow Engine.
- Concurrency is bounded by the Agent Runtime configuration.

9. LLM Integration

The LLM Integration Layer abstracts provider calls. Agents express reasoning requests declaratively; the layer selects a provider, manages retries, and returns structured results. No agent is coupled to a specific provider.

10. Persistence

- PKG → graph database.
- Provenance Ledger → append-only log.
- Audit Log → append-only log.
- Checkpoints → immutable snapshots.
- PKP → frozen bundle on shared storage or API.

11. Observability

Every subsystem emits audit events. The Audit Log is append-only and is part of the PKP. Operators may replay any session from its checkpoints and the audit log.

12. Failure and Recovery

- Crash → resume from the last checkpoint.
- Corrupt assertion → validation finding, agent re-runs.
- Governance rejection → revision workflow opens.
- PKG corruption → restore from immutable revision history.

13. Approval

This document is the consolidated runtime reference. For any conflict, GARCH-002 prevails.