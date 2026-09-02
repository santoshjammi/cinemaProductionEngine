Genesis Contracts
GC-004 — API Contract

Document ID: GC-004
Title: External API Semantic Contract
Version: 1.0.0
Status: Binding Contract
Authority: Derived from GFS-000, GFS-005, GFS-010, GFS-011

1. Purpose

This contract governs every REST and GraphQL endpoint exposed by the Genesis
Engine to external consumers, including the Studio Engine, creator tools,
review dashboards, and downstream Movie OS subsystems. It instantiates the
Semantic Contract Template (GC-001) for the specific case of an HTTP-based
programmatic surface.

Genesis exposes knowledge, not operations. Every endpoint is a
materialized view of the Production Knowledge Graph. No endpoint may
perform an action that bypasses constitutional validation, governance, or
provenance.

2. Foundational Principle

The API is a derived surface, not a source of truth.

Every response is a projection of the PKG. Every mutation routes through a
constitutional agent. The API never writes to the PKG directly; it always
delegates to an agent that holds the appropriate authority.

3. Parties

3.1 API Provider

- Party Class: SUBSYSTEM
- Authority: OPERATIONAL
- Accountability: transport correctness, authentication, rate limiting,
  response shape conformance

3.2 API Consumer

- Party Class: SUBSYSTEM | HUMAN | EXTERNAL
- Authority: scoped by granted credentials
- Accountability: honoring rate limits, presenting valid credentials,
  respecting the response contract

3.3 Authoritative Agents

- Party Class: AGENT
- Authority: DOMAIN
- Accountability: producing the knowledge that the API materializes

3.4 Governance Agent

- Party Class: AGENT
- Authority: CONSTITUTIONAL
- Accountability: revoking credentials, arbitrating disputes, auditing
  access

4. Endpoints

Genesis exposes two surface styles.

4.1 REST

REST endpoints follow the form:

    POST /v1/{resource}
    GET  /v1/{resource}/{id}
    GET  /v1/{resource}?filter=...
    PATCH /v1/{resource}/{id}
    DELETE /v1/{resource}/{id}

Resources are drawn from the ontology registry. A resource name maps to an
ontology class IRI. The response body is JSON-LD conforming to the PKG
serialization (GFS-010 section 4).

4.2 GraphQL

GraphQL is exposed at `/v1/graphql` and is the preferred surface for
subgraph extraction, temporal queries, and confidence-filtered reads.
GraphQL mutations are limited to operations backed by a registered agent;
arbitrary mutations are not permitted.

4.3 Mandatory Endpoints

Every Genesis deployment shall expose at minimum:

- `GET /v1/health` — liveness probe
- `GET /v1/version` — build and ontology registry version
- `GET /v1/productions/{id}` — fetch a production summary
- `GET /v1/productions/{id}/pkg` — fetch the PKG as JSON-LD
- `GET /v1/productions/{id}/readiness` — fetch the readiness certificate
- `POST /v1/productions` — create a production from a brief (delegates to
  Production Orchestrator)
- `POST /v1/productions/{id}/sessions` — start a reasoning session
- `GET /v1/ontologies` — list active ontologies
- `POST /v1/graphql` — GraphQL entry point

5. Authentication

- Scheme: OAuth 2.0 bearer tokens, scoped per production and per operation
  class
- Token lifetime: 1 hour, refreshable
- Scope names: `pkg:read`, `pkg:write` (never direct), `ontology:read`,
  `govern:approve`, `session:start`, `readiness:certify`
- Anonymous access is permitted only on `/v1/health` and `/v1/version`

A request without a valid token, or with an insufficient scope, shall
receive HTTP 401 or 403 respectively. The denial is written to the audit log.

6. Rate Limits

- Anonymous: not permitted except health/version probes
- Authenticated READ: 600 requests per minute per token
- Authenticated WRITE: 60 requests per minute per token
- GraphQL: 120 requests per minute per token; query depth limit 10; query
  complexity limit 1000
- Governance operations: 10 requests per minute per token

On exceeding a limit the API returns HTTP 429 with a `Retry-After` header.
Repeated violations trigger a temporary credential suspension logged to the
Governance Agent.

7. Error Codes

Errors use the Genesis Error Catalog (GFS-002 runtime) and map to HTTP
status codes:

- 400 CONTRACT_INVALID_REQUEST — malformed payload
- 401 CONTRACT_UNAUTHENTICATED — missing or invalid token
- 403 CONTRACT_UNAUTHORIZED — scope insufficient
- 404 CONTRACT_NOT_FOUND — resource does not exist
- 409 CONTRACT_CONFLICT — optimistic concurrency failure
- 422 CONTRACT_VALIDATION_FAILED — semantic validation rejected the
  request
- 429 CONTRACT_RATE_LIMITED — rate limit exceeded
- 500 CONTRACT_INTERNAL — unhandled error; auto-escalated to Governance
- 503 CONTRACT_TIMEOUT — upstream agent did not respond within TTL

Every error response body shall contain:

    {
      "error_type": "...",
      "severity": "MINOR | MAJOR | CRITICAL",
      "reason": "...",
      "correlation_id": "...",
      "recoverable": true | false,
      "suggested_action": "..."
    }

8. Pagination

List endpoints shall support cursor-based pagination:

- `?cursor={opaque}` — pagination cursor
- `?limit={1..200}` — page size, default 50, max 200
- Response envelope:

    {
      "data": [ ... ],
      "next_cursor": "..." | null,
      "prev_cursor": "..." | null,
      "total_estimate": 1234 | null
    }

Offset pagination is not supported. Cursors are opaque to the consumer and
stable for at most 24 hours.

9. Provenance

Every response shall include:

- `X-Genesis-Correlation-Id`: UUID for the request
- `X-Genesis-Pkg-Version`: version of the PKG consulted
- `X-Genesis-Agent`: name of the agent that produced the materialized view
- `X-Genesis-Confidence-Min`: minimum confidence present in the response

Responses are cacheable only when they carry a `Cache-Control: private,
max-age=0, must-revalidate` directive. PKG versions are immutable; cached
responses shall include the version they reflect.

10. Guarantees

- The API shall return schema-valid JSON-LD for any resource endpoint
- The API shall never expose a node whose confidence is below the
  consumer's requested floor (default floor: INFERRED)
- The API shall never expose a node from a non-ACTIVE ontology
- The API shall include the PKG version in every response
- The API shall never accept a write that bypasses a registered agent

11. Penalties

- MINOR (wrong content-type, missing provenance header): logged; provider
  notified; auto-retry not offered
- MAJOR (schema-violating response, dropped rate limit, token leak): the
  provider is quarantined; affected consumers receive 503 until corrected
- CRITICAL (unauthenticated write accepted, governance bypass, provenance
  forgery): immediate revocation of the deployment's credentials; the
  Governance Agent opens a constitutional review

12. Duration

- Start: deployment of the API version
- End: deployment of a superseding version, or revocation by Governance
- Each API version is independently supported for at least 12 months after
  its successor ships

13. Termination

- Versioned sunset: a MAJOR version is deprecated with at least 6 months
  notice and a migration guide
- Emergency termination: Governance may revoke an endpoint immediately for
  CRITICAL breaches; affected consumers are notified out-of-band
- On termination, in-flight requests are drained within the TTL; new
  requests receive 410 Gone

14. Compliance

This contract is enforced by the API Provider subsystem and audited by the
Governance Agent. Every endpoint shall be documented in the OpenAPI 3.1
specification shipped with the deployment. Undocumented endpoints are a
breach.

15. Invariants

- The API is derived, never authoritative.
- Writes flow through agents.
- Reads carry provenance and PKG version.
- Errors are cataloged and recoverable where possible.
- Authentication is mandatory for every non-health endpoint.
- Rate limits are enforced and reported.
- Sunset is versioned and announced.