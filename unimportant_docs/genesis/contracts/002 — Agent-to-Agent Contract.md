Genesis Contracts
GC-002 — Agent-to-Agent Contract

Document ID: GC-002
Title: Agent-to-Agent Semantic Contract
Version: 1.0.0
Status: Binding Contract
Authority: Derived from GFS-005, GFS-010, GFS-011

1. Purpose

This contract governs every exchange of structured knowledge between two
Genesis agents. It instantiates the Semantic Contract Template (GC-001) for
the specific case of agent-to-agent collaboration over the Genesis Message
Bus defined in GFS-011.

Any agent that dispatches a REQUEST to another agent accepts this contract.
Any agent that returns a RESPONSE to such a REQUEST accepts this contract.
The contract is in force from the moment a REQUEST is issued until the
corresponding RESPONSE is committed to the Production Knowledge Graph or the
exchange is declared failed by the Governance Agent.

2. Foundational Principle

Agent communication is structured, not conversational.

Two agents collaborate by exchanging messages that conform to the Production
Knowledge Graph schema. Every message must reduce uncertainty or advance
production readiness. A message that does neither is a contract violation.

3. Parties

3.1 Requesting Agent

- Party Class: AGENT
- Authority: DOMAIN (limited to its constitutional role)
- Accountability: correctness of the REQUEST payload, deadline, and
  correlation_id
- Channel: Genesis Message Bus (GFS-011)

3.2 Responding Agent

- Party Class: AGENT
- Authority: DOMAIN (limited to its constitutional role)
- Accountability: correctness, confidence, and provenance of the RESPONSE
- Channel: Genesis Message Bus (GFS-011)

3.3 Implicit Parties

- Production Orchestrator Agent (GAS-026): supervises dispatch and timeout
- Governance Agent: arbitrates breaches and dead-letter handling
- Production Knowledge Graph: canonical store of all exchanged knowledge

4. Request Format

The Requesting Agent shall issue a message of type REQUEST conforming to
GFS-011. The payload shall contain:

- operation: a registered operation from the Genesis Operation Registry
- input: a subgraph, node references, or document references
- output_format: the expected response shape
- deadline: ISO 8601 timestamp, no later than ttl_seconds from issue
- priority: LOW | MEDIUM | HIGH | CRITICAL
- confidence_floor: minimum confidence the response must meet
- provenance_hint: originating agent and session

A REQUEST missing any of the above fields is invalid. The Responding Agent
shall reject it with an ERROR of type CONTRACT_INVALID_REQUEST and shall not
allocate reasoning resources to it.

5. Response Guarantee

The Responding Agent shall return a RESPONSE within the deadline. The
RESPONSE shall contain:

- correlation_id: equal to the REQUEST correlation_id
- result: a subgraph, node set, edge set, or validation report
- confidence: one of EXPLICIT | INFERRED | CONFIRMED | ASSUMED | UNKNOWN
- warnings: non-blocking issues encountered
- errors: blocking issues encountered (empty on success)
- provenance: agent identity, session, reasoning references

The Responding Agent guarantees that every node and edge in the result
conforms to the Production Knowledge Graph specification (GFS-010). A result
that violates the schema is a breach of class MAJOR.

6. Timeout

- Default TTL: 300 seconds (per GFS-011)
- CRITICAL requests: TTL may be lowered to 30 seconds; on expiry the
  Production Orchestrator escalates immediately
- LONG operations: TTL may be raised up to 3600 seconds with explicit
  justification recorded in the REQUEST

On expiry the Responding Agent is released from the obligation to produce a
result, but must still emit a terminal ERROR of type CONTRACT_TIMEOUT. The
Requesting Agent is then free to retry per section 7 or escalate.

7. Retry

Retries follow GFS-011 section 6.1 and are bounded by priority:

- LOW: 3 attempts, exponential backoff 1s, 4s, 16s
- MEDIUM: 5 attempts, exponential backoff 500ms, 2s, 8s, 32s, 128s
- HIGH: 10 attempts, linear backoff 1s
- CRITICAL: no retry; immediate escalation to Governance Agent

A retry is a new REQUEST with a fresh message_id but the same correlation_id.
The Responding Agent shall treat retries as idempotent: the same input must
yield the same output unless the PKG has changed underneath.

8. Error Handling

Errors shall use the Genesis Error Catalog (GFS-002 runtime). Each ERROR
message shall contain:

- error_type: a catalog identifier
- severity: MINOR | MAJOR | CRITICAL
- affected_nodes: list of node UUIDs (may be empty)
- affected_edges: list of edge UUIDs (may be empty)
- reason: human-readable explanation
- recoverable: boolean
- suggested_action: next step the Requesting Agent should take

Errors that are not in the catalog are treated as CONTRACT_UNKNOWN_ERROR and
escalated automatically. Concealing an error is a CRITICAL breach.

9. Provenance

Every REQUEST and RESPONSE shall be written to the provenance log with:

- message_id, correlation_id, sender, recipient
- timestamp, priority, ttl_seconds
- PKG diff produced by the exchange (nodes added, edges added)
- confidence distribution of the result
- validation status of the result

Provenance entries are immutable. They are retained per the Data Retention
Policy (GPOL-004). No agent may amend or delete a provenance entry.

10. Penalties

- MINOR breach (malformed payload, missing warnings): automatic retry with
  the same correlation_id; logged for trend analysis
- MAJOR breach (schema violation, missed deadline, dropped provenance):
  escalation to Production Orchestrator; the offending agent is quarantined
  for the remainder of the session
- CRITICAL breach (concealed error, fabricated confidence, unauthorized
  canonical mutation): immediate escalation to Governance Agent; the
  offending agent is suspended pending review; production readiness
  certification is blocked until resolved

11. Duration

- Start: issuance of the REQUEST
- End: commit of the RESPONSE to the PKG, OR emission of a terminal ERROR,
  OR contract termination by the Governance Agent
- Checkpoint: every exchange is independently auditable; no implicit state
  carries across REQUESTs

12. Termination

- Normal: RESPONSE committed and acknowledged
- Timeout: terminal ERROR of type CONTRACT_TIMEOUT
- Breach: Governance Agent revokes the contract and reassigns work
- Session end: Production Orchestrator terminates all in-flight contracts

13. Compliance

This contract is mandatory for all inter-agent communication inside Genesis.
Agents that cannot conform are non-compliant and shall not be registered in
the Agent Registry. External integrations are governed by GC-004 (API
Contract) and may layer additional transport requirements on top of this
contract, but may not weaken any provision herein.