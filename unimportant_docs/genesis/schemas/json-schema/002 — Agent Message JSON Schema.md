Genesis Schema Specification (GSS)
GSS-002 — Agent Message JSON Schema

Document ID: GSS-002
Title: Agent Message JSON Schema
Version: 1.0.0
Status: Schema Specification
Authority: Derived from GFS-011

1. Purpose

This Schema defines the canonical JSON Schema for agent-to-agent messages in the Genesis Engine.

Every communication between Genesis agents — requests, responses, notifications, queries, and errors — shall conform to this schema.

The schema governs message structure, routing, correlation, prioritization, lifecycle, and payload typing. It does not govern the semantics of individual operations; those are defined by operation-specific payload schemas referenced herein.

2. Architectural Position

```text
Agent A
   │
   ↓
Agent Message (GSS-002)
   │
   ↓
Message Bus
   │
   ↓
Agent B
```

All agent communication passes through messages that conform to this schema.

3. Top-Level Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://genesis.movieos.dev/schemas/message/v1.json",
  "title": "Agent Message",
  "type": "object",
  "required": [
    "message_id",
    "message_type",
    "sender",
    "recipient",
    "session_id",
    "timestamp",
    "version",
    "payload"
  ],
  "properties": {
    "message_id": {
      "type": "string",
      "format": "uuid",
      "description": "Globally unique identifier for this message."
    },
    "message_type": {
      "type": "string",
      "enum": ["REQUEST", "RESPONSE", "NOTIFICATION", "QUERY", "ERROR"],
      "description": "Canonical message type governing processing semantics."
    },
    "sender": {
      "type": "string",
      "description": "Registered agent name of the sender."
    },
    "recipient": {
      "type": "string",
      "description": "Registered agent name of the recipient, or 'broadcast' for fan-out."
    },
    "session_id": {
      "type": "string",
      "format": "uuid",
      "description": "Production session this message belongs to."
    },
    "correlation_id": {
      "type": "string",
      "format": "uuid",
      "description": "ID of the message this message correlates to (for REQUEST/RESPONSE pairing)."
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp of message creation."
    },
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$",
      "description": "Schema version this message conforms to."
    },
    "payload": {
      "type": "object",
      "description": "Operation-specific payload. Must conform to the operation-specific schema referenced in payload_schema."
    },
    "payload_schema": {
      "type": "string",
      "format": "uri",
      "description": "URI of the operation-specific payload schema."
    },
    "priority": {
      "type": "string",
      "enum": ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
      "default": "MEDIUM"
    },
    "ttl_seconds": {
      "type": "integer",
      "minimum": 1,
      "maximum": 3600,
      "default": 300,
      "description": "Time-to-live in seconds. Messages past TTL shall be discarded."
    },
    "trace": {
      "type": "object",
      "properties": {
        "origin_agent": { "type": "string" },
        "origin_session": { "type": "string", "format": "uuid" },
        "chain": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["agent", "timestamp"],
            "properties": {
              "agent": { "type": "string" },
              "timestamp": { "type": "string", "format": "date-time" },
              "action": { "type": "string" }
            }
          }
        }
      },
      "description": "Optional trace chain for explainability per GFS-000 Eighth Principle."
    },
    "confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "Confidence carried by inferred payloads. Required when payload contains inferred knowledge."
    },
    "evidence": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Citations supporting inferred payloads. Required when confidence is present."
    }
  },
  "additionalProperties": false
}
```

4. Message Type Semantics

### 4.1 REQUEST

- Initiates an operation requiring a response
- `correlation_id` shall be absent on the request and present on the matching response
- `recipient` shall be a single registered agent

### 4.2 RESPONSE

- Replies to a REQUEST
- `correlation_id` shall equal the request's `message_id`
- `sender` shall equal the request's `recipient`
- `recipient` shall equal the request's `sender`

### 4.3 NOTIFICATION

- One-way informational message; no response expected
- `correlation_id` may be present to relate to a prior context
- `recipient` may be a single agent or `broadcast`

### 4.4 QUERY

- Read-only request that does not modify state
- Shall be answered with a RESPONSE
- Shall not trigger side effects

### 4.5 ERROR

- Reports a failure in processing a prior message
- `correlation_id` shall equal the failed message's `message_id`
- `payload` shall conform to the Error Payload schema (§6.5)

5. Validation Rules

- `message_id` shall be a valid UUID
- `message_type` shall be one of the five defined types
- `sender` and `recipient` shall be registered agent names (or `broadcast` for recipient)
- `timestamp` shall be in ISO 8601 format
- `version` shall match a published schema version
- `payload` shall conform to the schema referenced by `payload_schema`
- `ttl_seconds` shall be between 1 and 3600
- RESPONSE messages shall have `correlation_id` equal to the original REQUEST's `message_id`
- ERROR messages shall have `correlation_id` equal to the failed message's `message_id`
- Messages carrying inferred knowledge shall include `confidence` and `evidence`
- `additionalProperties` is false; unknown fields shall be rejected
- Broadcast messages shall not use REQUEST or QUERY types

6. Canonical Payload Schemas

### 6.1 ProductionBriefPayload

```json
{
  "type": "object",
  "required": ["synopsis", "constraints"],
  "properties": {
    "synopsis": { "type": "string" },
    "constraints": { "type": "object" },
    "audience": { "type": "string" },
    "target_duration_seconds": { "type": "integer", "minimum": 1 }
  }
}
```

### 6.2 SubgraphPayload

```json
{
  "type": "object",
  "required": ["subgraph_type", "nodes", "edges"],
  "properties": {
    "subgraph_type": { "type": "string", "enum": ["narrative", "character", "world", "knowledge", "event", "communication", "visual", "audio"] },
    "nodes": { "type": "array" },
    "edges": { "type": "array" }
  }
}
```

### 6.3 ValidationReportPayload

```json
{
  "type": "object",
  "required": ["report_type", "status", "score", "findings"],
  "properties": {
    "report_type": { "type": "string" },
    "status": { "type": "string", "enum": ["PASS", "WARN", "FAIL"] },
    "score": { "type": "number", "minimum": 0, "maximum": 1 },
    "findings": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["severity", "message"],
        "properties": {
          "severity": { "type": "string", "enum": ["INFO", "WARN", "ERROR", "BLOCKER"] },
          "message": { "type": "string" },
          "citation": { "type": "string" }
        }
      }
    }
  }
}
```

### 6.4 QueryPayload

```json
{
  "type": "object",
  "required": ["query"],
  "properties": {
    "query": { "type": "string" },
    "parameters": { "type": "object" }
  }
}
```

### 6.5 ErrorPayload

```json
{
  "type": "object",
  "required": ["error_code", "error_message"],
  "properties": {
    "error_code": { "type": "string", "enum": [
      "SCHEMA_VIOLATION",
      "UNKNOWN_AGENT",
      "TTL_EXPIRED",
      "PERMISSION_DENIED",
      "DEPENDENCY_MISSING",
      "VALIDATION_FAILED",
      "INTERNAL_ERROR"
    ]},
    "error_message": { "type": "string" },
    "details": { "type": "object" }
  }
}
```

7. Examples

### 7.1 REQUEST example

```json
{
  "message_id": "11111111-1111-1111-1111-111111111111",
  "message_type": "REQUEST",
  "sender": "ProductionOrchestratorAgent",
  "recipient": "StoryArchitectAgent",
  "session_id": "22222222-2222-2222-2222-222222222222",
  "timestamp": "2026-07-19T10:00:00Z",
  "version": "1.0.0",
  "payload_schema": "https://genesis.movieos.dev/schemas/payload/production-brief/v1.json",
  "payload": {
    "synopsis": "A monk confronts doubt on the night before his ordination.",
    "constraints": { "duration_seconds": 600, "language": "en" }
  },
  "priority": "HIGH",
  "ttl_seconds": 600
}
```

### 7.2 RESPONSE example

```json
{
  "message_id": "33333333-3333-3333-3333-333333333333",
  "message_type": "RESPONSE",
  "sender": "StoryArchitectAgent",
  "recipient": "ProductionOrchestratorAgent",
  "session_id": "22222222-2222-2222-2222-222222222222",
  "correlation_id": "11111111-1111-1111-1111-111111111111",
  "timestamp": "2026-07-19T10:02:00Z",
  "version": "1.0.0",
  "payload_schema": "https://genesis.movieos.dev/schemas/payload/subgraph/v1.json",
  "payload": {
    "subgraph_type": "narrative",
    "nodes": [],
    "edges": []
  },
  "confidence": 0.87,
  "evidence": ["synopsis-derivation-1", "synopsis-derivation-2"]
}
```

### 7.3 ERROR example

```json
{
  "message_id": "44444444-4444-4444-4444-444444444444",
  "message_type": "ERROR",
  "sender": "DialogueQualityAgent",
  "recipient": "ProductionOrchestratorAgent",
  "session_id": "22222222-2222-2222-2222-222222222222",
  "correlation_id": "11111111-1111-1111-1111-111111111111",
  "timestamp": "2026-07-19T10:03:00Z",
  "version": "1.0.0",
  "payload_schema": "https://genesis.movieos.dev/schemas/payload/error/v1.json",
  "payload": {
    "error_code": "DEPENDENCY_MISSING",
    "error_message": "Character Subgraph not available; cannot evaluate dialogue voice consistency.",
    "details": { "missing_dependency": "CharacterSubgraph" }
  },
  "priority": "HIGH"
}
```

8. Relationship with Other Schemas

- Operation-specific payload schemas are referenced by `payload_schema` and versioned independently
- The Agent Registry (GFS-011 derived) defines valid `sender` and `recipient` values
- The Trace schema supports the explainability requirement of GFS-000 Eighth Principle
- The Confidence and Evidence fields operationalize the GFS-000 Sixth Principle (inference vs. fact)

9. Constitutional Invariants

- All agent communication shall conform to this schema
- Inferred knowledge shall carry confidence and evidence
- Message IDs and correlation IDs shall be UUIDs
- Trace shall be preserved for explainability
- Unknown fields shall be rejected
- Message evolution shall remain backward-compatible within a major version

10. Evolution Policy

This schema may evolve through additive, backward-compatible changes governed by the Schema Governance Framework.

Breaking changes shall require a major version increment and a migration path.