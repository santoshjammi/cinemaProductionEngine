Genesis Foundational Standards (GFS)
GFS-011 — Agent Communication Protocol

Document ID: GFS-011
Title: Agent Communication Protocol
Version: 1.0.0
Status: Foundational Standard
Authority: Derived from GFS-005 Agent Constitution

1. Purpose

This Protocol defines how constitutional roles communicate within the Genesis Engine. It establishes the message format, routing rules, session lifecycle, and error handling for all inter-agent communication.

2. Foundational Principle

Communication is structured, not conversational.

Agents do not chat. They exchange structured messages that conform to the Production Knowledge Graph schema. Every message must reduce uncertainty or advance production readiness.

3. Message Format

Every agent-to-agent message must conform to the following structure:

{
  "message_id": "uuid",
  "message_type": "REQUEST | RESPONSE | NOTIFICATION | QUERY | ERROR",
  "sender": "agent-role-name",
  "recipient": "agent-role-name | BROADCAST",
  "session_id": "uuid",
  "correlation_id": "uuid (for request-response pairing)",
  "timestamp": "ISO 8601",
  "payload": { ... },
  "priority": "LOW | MEDIUM | HIGH | CRITICAL",
  "ttl_seconds": 300
}

4. Message Types

4.1 REQUEST

An agent requests a specific operation from another agent. The request must specify:
- The operation to perform (from the Genesis Operation Registry)
- The input data (as a subgraph or node references)
- The expected output format
- The deadline for response

4.2 RESPONSE

An agent responds to a previous REQUEST. The response must include:
- The correlation_id of the original request
- The result (as a subgraph, nodes, edges, or validation report)
- The confidence level of the result
- Any errors or warnings encountered

4.3 NOTIFICATION

An agent broadcasts information to all subscribed agents. Notifications are used for:
- State changes in the PKG
- New knowledge discovered
- Validation failures detected
- Milestones reached

4.4 QUERY

An agent queries the PKG through another agent. Queries use a subset of the Graph Query Language defined in GFS-010.

4.5 ERROR

An agent reports an unrecoverable error. The error message must include:
- The error type (from the Genesis Error Catalog)
- The affected nodes or edges
- The reason for failure
- Suggested recovery action

5. Session Lifecycle

5.1 Session Creation

A session begins when the Production Orchestrator Agent initiates a new production. The session_id is the production UUID.

5.2 Message Routing

Messages are routed through the Genesis Message Bus. The bus guarantees:
- At-least-once delivery
- Message ordering per sender
- Dead letter queue for undeliverable messages
- Message expiry based on TTL

5.3 Session Termination

A session ends when the Governance Agent certifies production readiness or when the Production Orchestrator Agent terminates the session due to unrecoverable error.

6. Error Handling

6.1 Retry Policy

- LOW priority: Retry up to 3 times with exponential backoff (1s, 4s, 16s)
- MEDIUM priority: Retry up to 5 times with exponential backoff (500ms, 2s, 8s, 32s, 128s)
- HIGH priority: Retry up to 10 times with linear backoff (1s intervals)
- CRITICAL priority: Immediate escalation to Governance Agent

6.2 Dead Letter Queue

Messages that exceed their retry limit are moved to the dead letter queue. The Governance Agent reviews the dead letter queue at the end of each session and determines whether to:
- Re-route the message to a different agent
- Adjust the production plan to work around the failure
- Terminate the session

7. Security

All inter-agent communication must be:
- Authenticated (each message carries the sender's identity certificate)
- Authorized (the sender must have permission to perform the requested operation)
- Audited (all messages are logged to the provenance log)
- Non-repudiable (the sender cannot deny having sent the message)

8. Compliance

Every agent implementation must conform to this Protocol. Custom communication patterns are permitted only when they do not violate the message format, routing rules, or security requirements defined herein.
