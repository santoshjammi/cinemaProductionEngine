Genesis Specification (GSPEC)
GSPEC-002 — Genesis Error Catalog

Document ID: GSPEC-002
Title: Genesis Error Catalog
Version: 1.0.0
Status: Specification
Authority: Derived from GFS-011

1. Purpose

This Catalog defines all error types that can be raised by Genesis agents. Every error message must include the error code from this catalog.

2. Error Categories

2.1 Input Errors (ERR-INP-*)

ERR-INP-001: MissingRequiredField — A required field is missing from the input
ERR-INP-002: InvalidFieldType — A field has an incorrect type
ERR-INP-003: FieldOutOfRange — A field value is outside the allowed range
ERR-INP-004: InvalidFormat — The input format is not recognized
ERR-INP-005: EmptyInput — The input is empty

2.2 Knowledge Errors (ERR-KNW-*)

ERR-KNW-001: NodeNotFound — A referenced node does not exist in the PKG
ERR-KNW-002: EdgeNotFound — A referenced edge does not exist in the PKG
ERR-KNW-003: ConfidenceTooLow — Confidence level is below the minimum threshold
ERR-KNW-004: ContradictoryKnowledge — Two pieces of knowledge contradict each other
ERR-KNW-005: MissingSubgraph — A required subgraph is not populated
ERR-KNW-006: CircularDependency — A circular dependency was detected in the PKG

2.3 Agent Errors (ERR-AGT-*)

ERR-AGT-001: AgentNotResponding — An agent did not respond within the timeout
ERR-AGT-002: AgentReturnedError — An agent returned an error response
ERR-AGT-003: AgentNotFound — The requested agent is not registered
ERR-AGT-004: AgentBusy — The agent is currently processing another request
ERR-AGT-005: AgentCapacityExceeded — The agent has exceeded its processing capacity

2.4 Communication Errors (ERR-COM-*)

ERR-COM-001: MessageFormatInvalid — The message does not conform to GFS-011
ERR-COM-002: MessageExpired — The message TTL has expired
ERR-COM-003: RoutingFailed — The message could not be routed to the recipient
ERR-COM-004: AuthenticationFailed — The sender could not be authenticated
ERR-COM-005: AuthorizationDenied — The sender does not have permission

2.5 Validation Errors (ERR-VAL-*)

ERR-VAL-001: SchemaValidationFailed — The document does not conform to its schema
ERR-VAL-002: SemanticValidationFailed — The document contains semantic contradictions
ERR-VAL-003: CompletenessValidationFailed — Required elements are missing
ERR-VAL-004: ConsistencyValidationFailed — The document is internally inconsistent
ERR-VAL-005: ConfidenceThresholdNotMet — Confidence levels are below minimum

2.6 Production Errors (ERR-PRD-*)

ERR-PRD-001: ProductionNotFound — The production session does not exist
ERR-PRD-002: ProductionAlreadyComplete — The production has already been certified
ERR-PRD-003: ProductionTerminated — The production was terminated
ERR-PRD-004: ResourceExceeded — Resource requirements exceed available capacity
ERR-PRD-005: DeadlineExceeded — The production deadline has passed

2.7 System Errors (ERR-SYS-*)

ERR-SYS-001: InternalError — An unexpected internal error occurred
ERR-SYS-002: ConfigurationError — The system is misconfigured
ERR-SYS-003: DependencyUnavailable — A required dependency is not available
ERR-SYS-004: ResourceExhausted — System resources are exhausted
ERR-SYS-005: NotImplemented — The requested operation is not yet implemented

3. Error Message Format

{
  "error_code": "ERR-CAT-NNN",
  "message": "Human-readable description",
  "details": { ... },
  "severity": "CRITICAL | HIGH | MEDIUM | LOW",
  "source": "agent-name",
  "timestamp": "ISO 8601",
  "recovery": "Suggested recovery action"
}
