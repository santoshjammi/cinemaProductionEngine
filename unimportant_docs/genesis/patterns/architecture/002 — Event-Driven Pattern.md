Genesis Pattern (GP)
GP-ARCH-002 — Event-Driven Pattern

Document ID: GP-ARCH-002
Title: Event-Driven Pattern
Version: 1.0.0
Status: Pattern
Authority: Derived from GFS-000, GFS-005, GFS-008

1. Purpose

The Event-Driven Pattern defines how Genesis components communicate through typed events rather than direct function calls. Events decouple producers from consumers, allow the Production Orchestrator to observe and audit every transition, and let long-running workflows coordinate without blocking.

In Genesis, events are first-class knowledge artifacts. Every event is recorded in the PKG with provenance, classification, and confidence. An event is not a side-channel — it is a constitutional record. The Charter's Eighth Principle (every decision must be traceable) is operationalized through event logs.

2. When to Apply

Apply this pattern when:

- A workflow stage must notify the orchestrator without blocking downstream agents.
- A validation result must trigger a revision loop in a different agent.
- A governance approval must unblock multiple waiting workflows.
- A learning agent must react to production-completion events asynchronously.
- A revision request must be dispatched without coupling the requesting agent to the revising agent.

Do not apply this pattern for synchronous request/response within a single agent — events add latency and audit overhead that synchronous calls do not need.

3. Event Structure

Every Genesis event is a typed record with:

- Event ID — stable identifier.
- Event Type — from the registered Event Type Catalog (see §5).
- Emitter — the agent or component that produced the event (GAS-NNN or component ID).
- Subject — the PKG node the event concerns.
- Payload — the typed data the event carries.
- Provenance — links to the Decision Record that caused the event.
- Confidence — in [0,1], inherited from the causing decision.
- Timestamp — monotonic session clock.
- Trace ID — workflow execution identifier, propagated across consumers.

Events without an Event Type from the catalog are invalid. Events without provenance are treated as assertions, not events.

4. Event Bus

Genesis components publish events to and subscribe from a single Event Bus owned by the Production Orchestrator. The Bus is not a generic message queue — it is a governed, typed, audited channel.

Bus rules:

- Events are immutable once published.
- Subscribers receive a copy; they cannot mutate the original.
- Subscribers declare the Event Types they consume.
- The Bus records every publish and every delivery to the PKG.
- The Bus does not deliver events to unregistered subscribers.
- The Bus supports ordered delivery within a trace; cross-trace ordering is not guaranteed.

5. Event Type Catalog

Registered event types include:

- Stage Started / Stage Completed
- Agent Invoked / Agent Returned
- Validation Passed / Validation Failed
- Revision Requested / Revision Completed
- Approval Requested / Approval Granted / Approval Denied
- Conflict Detected / Conflict Resolved
- Knowledge Object Created / Knowledge Object Updated
- Gap Detected / Gap Resolved
- Production Readiness Certified

New event types are added through the same governance process as ontologies — registration, validation, publication.

6. Workflow

6.1 Declare Subscriptions

An agent's spec declares the event types it consumes. At registration, the Bus validates that the agent's input contract matches the payload type of each subscribed event.

6.2 Emit Events

When an agent completes a decision, it emits the corresponding event with provenance. The Bus records the emission and routes to subscribers.

6.3 Consume Events

Subscribers receive events and may invoke their own logic. Each consumption is recorded with the subscriber's agent ID and the trace ID. A subscriber may emit further events, propagating the trace.

6.4 Audit

The PKG's event log is the authoritative audit trail. The Governance Agent and the Traceability Auditor reconstruct any decision chain by walking events backward through provenance links.

7. Use Inside Genesis

- Stage transitions — Stage Completed events drive the Production Orchestrator's next-stage decision.
- Revision loops — Validation Failed emits Revision Requested; the Revision Agent subscribes and dispatches to the responsible upstream agent.
- Governance approvals — Approval Granted unblocks all subscribers waiting on that approval.
- Learning — Production Readiness Certified triggers the Learning Agent to ingest the production into the learning corpus.
- Conflict resolution — Conflict Detected triggers the Merge Agent to rewind the offending branch.

8. Worked Example

The Structural Validation Agent runs on a Screenplay Document:

1. Validation completes with a cardinality failure.
2. Agent emits Validation Failed with subject = Screenplay Document, payload = failing SHACL shapes, provenance = Decision Record D-7732.
3. The Revision Agent (subscribed to Validation Failed) receives the event.
4. Revision Agent emits Revision Requested with subject = Character Manager Agent (the responsible upstream agent), trace ID preserved.
5. Character Manager Agent receives Revision Requested, re-executes, emits Knowledge Object Updated on completion.
6. Production Orchestrator (subscribed to Knowledge Object Updated) re-triggers validation.

Every emission is recorded in the PKG. The trace ID is preserved end to end, so the Governance Agent can reconstruct the full revision loop.

9. Anti-Patterns

- Emitting events without provenance — they are assertions, not events.
- Mutating event payloads after publication — events are immutable.
- Subscribing to events not declared in the agent spec — undeclared subscriptions are invalid.
- Using the Event Bus for synchronous request/response — use a direct call.
- Skipping the Bus and having agents call each other directly — this defeats traceability.
- Allowing an unregistered Event Type — the catalog is closed.

10. Exit Criteria

An event-driven interaction is complete when:

- The Event Type is registered.
- The emitter has emitted the event with provenance and trace ID.
- The Bus has recorded the emission and delivered to all declared subscribers.
- Each subscriber has recorded its consumption.
- The event is resolvable in the PKG audit log by Event ID and by trace ID.