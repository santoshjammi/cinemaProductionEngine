Genesis Schema Specification (GSS)
GSS-601 — Agent Message Protobuf

Document ID: GSS-601
Title: Agent Message Protobuf
Version: 1.0.0
Status: Schema Specification
Authority: Derived from GFS-010, GSS-002, GSS-502

1. Purpose

This Schema defines the Protocol Buffers message format used for inter-agent
communication inside the Genesis Runtime. Agent Messages are the canonical wire
format for orchestration events, task assignments, partial results, and
termination signals exchanged between Orchestrator Agents and Specialist Agents.

Protobuf is chosen for agent-to-agent messaging because it is compact, schema
evolution is forward-compatible, and it generates typed bindings for Python,
Rust, and TypeScript runtimes.

2. Package

All messages belong to the `genesis.agent.v1` package. The `.proto` source is
maintained in `schemas/protobuf/genesis_agent_v1.proto` and compiled artifacts
are published to the runtime language registries.

3. Core Envelope

message AgentMessage {
  string message_id = 1;          // UUID
  string trace_id = 2;            // distributed trace identifier
  string session_id = 3;          // Genesis session id
  google.protobuf.Timestamp issued_at = 4;
  string source_agent = 5;        // agent identifier (e.g. "orchestrator")
  string target_agent = 6;        // agent identifier or "broadcast"
  AgentMessageType type = 7;
  AgentMessageStatus status = 8;
  uint32 schema_version = 9;
  bytes payload = 10;             // type-specific serialized payload
  Provenance provenance = 11;
  repeated string correlation_ids = 12;
}

enum AgentMessageType {
  AGENT_MESSAGE_TYPE_UNSPECIFIED = 0;
  TASK_ASSIGN = 1;
  TASK_ACCEPT = 2;
  TASK_PROGRESS = 3;
  TASK_RESULT = 4;
  TASK_FAILURE = 5;
  QUESTION_RAISE = 6;
  QUESTION_ANSWER = 7;
  CONTEXT_UPDATE = 8;
  HANDOFF = 9;
  TERMINATE = 10;
  HEARTBEAT = 11;
}

enum AgentMessageStatus {
  AGENT_MESSAGE_STATUS_UNSPECIFIED = 0;
  OK = 1;
  INVALID = 2;
  RETRY = 3;
  FATAL = 4;
}

4. Provenance

message Provenance {
  string agent = 1;
  string session = 2;
  string rationale = 3;
  repeated string evidence_ids = 4;
  Confidence confidence = 5;
  google.protobuf.Timestamp recorded_at = 6;
}

enum Confidence {
  CONFIDENCE_UNSPECIFIED = 0;
  EXPLICIT = 1;
  INFERRED = 2;
  CONFIRMED = 3;
  ASSUMED = 4;
  UNKNOWN = 5;
}

5. Task Payloads

message TaskAssign {
  string task_id = 1;
  string task_type = 2;
  string intent = 3;
  map<string, string> inputs = 4;
  repeated string required_outputs = 5;
  uint32 deadline_seconds = 6;
  uint32 priority = 7;
}

message TaskResult {
  string task_id = 1;
  map<string, string> outputs = 2;
  repeated string pkg_node_ids = 3;   // nodes produced/modified
  repeated string pkg_edge_ids = 4;   // edges produced/modified
  Confidence confidence = 5;
  string summary = 6;
}

message TaskFailure {
  string task_id = 1;
  string error_code = 2;
  string error_message = 3;
  bool retriable = 4;
  string recovery_hint = 5;
}

6. Question Payload

message QuestionRaise {
  string question_id = 1;
  string question_text = 2;
  string rationale = 3;
  repeated string affected_decisions = 4;
  uint32 uncertainty_reduction = 5;  // 0..100
}

7. Handoff and Termination

message Handoff {
  string from_agent = 1;
  string to_agent = 2;
  string reason = 3;
  repeated string carried_context_ids = 4;
}

message Terminate {
  string reason = 1;
  bool force = 2;
  string initiator = 3;
}

8. Validation Rules

- `message_id` MUST be a UUIDv4 string.
- `schema_version` MUST match the runtime's supported major version.
- `payload` MUST be decodable as the message type referenced by `type`.
- Every TASK_RESULT MUST reference at least one `pkg_node_id` OR `pkg_edge_id`,
  unless `outputs` explicitly records a "no-op" reason.
- Provenance is REQUIRED for TASK_RESULT, TASK_FAILURE, and QUESTION_RAISE.
- Confidence values MUST be one of the five constitutional levels.

9. Backward Compatibility

Fields 1-12 of `AgentMessage` are reserved. New fields MUST be appended with
new tag numbers and MUST be declared `optional` until runtime adoption reaches
the rollout threshold defined in GSPEC-023.

10. Usage

Compiled stubs are imported by the Genesis Runtime and by every agent
implementation. The Orchestrator Agent serializes TASK_ASSIGN messages and
deserializes TASK_RESULT/TASK_FAILURE messages. Specialist Agents do the
inverse.