Genesis Schema Specification (GSS)
GSS-701 — Genesis REST API OpenAPI

Document ID: GSS-701
Title: Genesis REST API OpenAPI
Version: 1.0.0
Status: Schema Specification
Authority: Derived from GFS-010, GSS-001, GSS-501

1. Purpose

This Schema defines the OpenAPI 3.1 contract for the Genesis REST API — the
HTTP surface used by external clients (studios, IDE plugins, CI runners) to
create productions, query the Production Knowledge Graph, invoke agents, and
stream validation events.

GraphQL (GSS-501) remains the canonical read API; this REST surface is provided
for clients that require synchronous request/response semantics or that cannot
integrate GraphQL.

2. OpenAPI Document

openapi: 3.1.0
info:
  title: Genesis REST API
  version: 1.0.0
  description: Pre-Production Intelligence System HTTP surface.
  contact:
    name: Genesis Working Group
    url: https://genesis.movieos.dev
servers:
  - url: https://api.genesis.movieos.dev/v1
    description: Production
  - url: http://localhost:8080/v1
    description: Local runtime
tags:
  - Production
  - KnowledgeGraph
  - Agent
  - Validation
  - Provenance

3. Authentication

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
security:
  - BearerAuth: []

4. Resources

### Productions

POST /productions
  Create a new production from a Production Brief.
  Request: ProductionBrief (GSS-101) YAML or JSON.
  Response: 201 Created → ProductionRecord.

GET /productions/{productionId}
  Returns production metadata and current readiness state.

POST /productions/{productionId}/discover
  Triggers the Discovery Workflow (GWS-001).
  Response: 202 Accepted → WorkflowHandle.

GET /productions/{productionId}/readiness
  Returns the Production Readiness Assessment (GSPEC-014).

### Knowledge Graph

GET /productions/{productionId}/pkg
  Returns the full Production Knowledge Graph (GSS-001).

GET /productions/{productionId}/pkg/nodes/{nodeId}
  Returns a single node with provenance.

GET /productions/{productionId}/pkg/edges
  Query: ?type=&source_id=&target_id=&confidence=

POST /productions/{productionId}/pkg/nodes
  Create a node. Requires `X-Genesis-Agent` and `X-Genesis-Session` headers.
  Response: 201 Created → Node.

PATCH /productions/{productionId}/pkg/nodes/{nodeId}
  Update node properties. Triggers validation.

### Agents

GET /agents
  Lists registered agents and their current state.

POST /agents/{agentId}/invoke
  Body: AgentInvocation { intent, inputs, deadline_seconds }
  Response: 202 Accepted → WorkflowHandle.

GET /agents/{agentId}/sessions/{sessionId}
  Returns session state and recent messages (GSS-601).

### Validation

POST /productions/{productionId}/validate
  Triggers full PKG validation (SHACL + JSON Schema + business rules).
  Response: 202 Accepted → WorkflowHandle.

GET /validations/{validationId}
  Returns ValidationReport { status, errors, warnings, shacl_results }.

GET /productions/{productionId}/validations
  Returns validation history for the production.

### Provenance

GET /productions/{productionId}/provenance/{entityId}
  Returns provenance chain for any node or edge.

GET /provenance/agents/{agentId}
  Returns the agent's decision history across productions.

5. Standard Error Model

components:
  schemas:
    Error:
      type: object
      required: [code, message]
      properties:
        code:
          type: string
          enum:
            - PRODUCTION_NOT_FOUND
            - PKG_INVALID
            - VALIDATION_FAILED
            - AGENT_UNAVAILABLE
            - UNAUTHORIZED
            - RATE_LIMITED
            - INTERNAL
        message: { type: string }
        trace_id: { type: string }
        details: { type: object, additionalProperties: true }

6. Headers

| Header                  | Purpose                                  |
|-------------------------|------------------------------------------|
| Authorization           | Bearer JWT                               |
| X-Genesis-Agent         | Calling agent identifier (write paths)   |
| X-Genesis-Session       | Session identifier (write paths)         |
| X-Genesis-Trace-Id      | Distributed trace id                     |
| X-Genesis-Idempotency   | Client-supplied idempotency key          |

7. Rate Limiting

- Read endpoints: 600 req/min per token.
- Write endpoints: 120 req/min per token.
- Agent invocation: 30 req/min per token.
Rate-limited responses use HTTP 429 with `Retry-After`.

8. Streaming

Long-running operations return a `WorkflowHandle` with a `stream_url` pointing
to `/v1/workflows/{workflowId}/events` (Server-Sent Events). Events are JSON
serialization of AgentMessage envelopes (GSS-601).

9. Versioning

The REST API uses URL versioning (`/v1`). Breaking changes require a new major
version and a parallel deprecation period of no less than 12 months. Additive
changes within a major version are permitted and MUST be documented in the
CHANGELOG.

10. Cross-References

- GraphQL canonical API: GSS-501
- Agent wire format: GSS-601
- PKG schema: GSS-001
- Production Brief schema: GSS-101
- Production readiness: GSPEC-014