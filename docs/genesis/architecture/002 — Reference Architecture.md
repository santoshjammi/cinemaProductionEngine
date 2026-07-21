Genesis Architecture Specification (GAS)
GARCH-002 — Reference Architecture

Document ID: GARCH-002
Title: Genesis Reference Architecture
Version: 1.0.0
Status: Architecture Specification
Authority: Derived from GARCH-001 and GFS-000

1. Purpose

This document specifies the technical Reference Architecture of the Genesis Engine. Where GARCH-001 defines the layers and boundaries conceptually, this document defines the concrete subsystems, their interfaces, their storage, their communication fabric, and their integration with external providers.

The Reference Architecture is binding for all implementations of Genesis. Any implementer must satisfy every interface defined here, even if the underlying technology differs.

2. Subsystem Overview

Genesis is composed of nine primary subsystems arranged across the layers defined in GARCH-001.

| # | Subsystem | Layer | Role |
|---|-----------|------|------|
| S1 | Graph Database | 2 | Canonical store for the PKG |
| S2 | Provenance Ledger | 2 | Append-only record of every PKG mutation |
| S3 | Validation Engine | 2 | Continuous evaluator of PKG integrity |
| S4 | Governance Engine | 4 | Approval gates and certification |
| S5 | Agent Runtime | 3 | Hosts and dispatches constitutional agents |
| S6 | Workflow Engine | 4 | Orchestrates multi-agent sequences |
| S7 | Message Bus | 5 | Inter-agent and inter-subsystem communication |
| S8 | CLI Interface | 5 | Operator-facing command surface |
| S9 | REST/GraphQL API | 5 | Programmatic access surface |
| S10 | LLM Integration Layer | 5 | Provider-agnostic model access |

3. Graph Database (S1)

The Graph Database is the canonical persistence layer for the Production Knowledge Graph. It is the only subsystem permitted to store knowledge as truth.

3.1 Required Capabilities
- Labeled property graph with typed nodes and typed edges
- Native support for semantic relationship predicates (depends_on, supports, evokes, contradicts, references, validates, etc. per GO-002)
- Transactional writes with multi-version concurrency control
- Immutable revision history (no in-place updates; every mutation creates a new revision)
- Graph traversal and pattern matching (Cypher-compatible or Gremlin-compatible query surface)
- Schema enforcement via SHACL or equivalent constraints derived from the Core Ontology

3.2 Node Model
Every node in the PKG shall expose:
- `id` — immutable canonical identifier
- `ontology_type` — reference to a Core or Domain Ontology concept
- `canonical_name` — stable human-readable name
- `confidence` — one of EXPLICIT, INFERRED, CONFIRMED, ASSUMED, UNKNOWN
- `state` — lifecycle state (Proposed, Reviewed, Validated, Approved, Published, Deprecated, Archived)
- `version` — monotonically increasing integer
- `created_at`, `created_by` — provenance anchor
- `properties` — domain-specific attribute bag validated against the ontology

3.3 Edge Model
Every edge shall expose:
- `from_id`, `to_id` — endpoint node identifiers
- `predicate` — semantic relationship from GO-002
- `confidence` — confidence classification of the relationship
- `evidence` — reference to one or more Provenance Ledger entries
- `version`, `created_at`, `created_by`

3.4 Query Interface
The Graph Database exposes a query surface to all upper layers. Queries must support:
- Node lookup by identifier or canonical name
- Predicate traversal (one-hop, multi-hop, variable-depth)
- Confidence filtering (e.g., "return only CONFIRMED")
- Provenance traversal (jump from any node to its supporting evidence)
- Subgraph extraction (return all nodes and edges within a bounded neighborhood)
- Materialized view extraction (return a projection shaped for a specific deliverable)

3.5 Implementation Independence
The Reference Architecture does not mandate a specific vendor. Acceptable implementations include Neo4j, Memgraph, Amazon Neptune, or an embedded store such as an in-process graph library. Whatever the choice, the query surface and revision semantics defined here must be preserved.

4. Provenance Ledger (S2)

The Provenance Ledger is an append-only log of every write to the PKG.

4.1 Ledger Entry
Every entry contains:
- `entry_id` — monotonic sequence
- `timestamp`
- `agent_id` — the constitutional agent that performed the write
- `operation` — CREATE, UPDATE, RETIRE, RELATE, VALIDATE, APPROVE
- `target_id` — the node or edge affected
- `before_version`, `after_version`
- `evidence_refs` — references to source artifacts (synopsis, prior decisions, observations)
- `rationale` — short human-readable explanation
- `signature` — cryptographic signature of the agent

4.2 Invariants
- The ledger is append-only. No entry may be deleted or modified.
- Every PKG mutation must produce exactly one ledger entry.
- Ledger entries are queryable by target_id, agent_id, and timestamp.
- The ledger is part of the Production Knowledge Package at certification time.

5. Validation Engine (S3)

The Validation Engine continuously evaluates the PKG against constitutional rules, ontology constraints, and production-specific invariants.

5.1 Validation Sources
- Constitutional rules from GFS-000..009
- Ontology constraints from GO-001 and derived ontologies
- Relationship cardinality and directionality from GO-002
- Production-specific invariants declared at session creation
- Confidence threshold rules from the Governance Constitution

5.2 Validation Findings
Every evaluation produces one of:
- `PASS` — invariant satisfied
- `WARN` — invariant partially satisfied; advisory only
- `FAIL` — invariant violated; blocks certification
- `BLOCK` — invariant violated; blocks further writes in the affected subgraph until resolved

5.3 Triggering
Validation may be triggered by:
- Any PKG mutation (immediate validation of the affected subgraph)
- Workflow checkpoint (full validation of the touched domains)
- Explicit governance request (full PKG validation)
- Certification request (mandatory full validation)

6. Governance Engine (S4)

The Governance Engine enforces approval gates and certifies production readiness.

6.1 Approval Gates
- Discovery gate — discovery agents may not produce specifications until discovery is approved
- Validation gate — specifications may not be materialized until validation passes
- Review gate — materialized views may not be exported until reviewed
- Certification gate — the PKP may not be issued until the Governance Agent certifies readiness

6.2 Certification
Certification requires:
- All validation findings at PASS or accepted WARN
- All required deliverables present in the PKG
- All confidence thresholds met per the production's confidence profile
- All governance approvals recorded in the Provenance Ledger
- The Governance Agent's signature on the PKP manifest

7. Agent Runtime (S5)

The Agent Runtime hosts constitutional agents and dispatches work to them.

7.1 Responsibilities
- Resolve agent specifications from the Agent Registry (GAS-001..027)
- Provide agents with read and write access to the PKG via the Graph Database interface
- Enforce per-agent permissions (read scope, write scope, validation scope)
- Capture agent outputs as PKG mutations with provenance
- Report agent progress to the Workflow Engine
- Handle agent timeouts, retries, and escalations

7.2 Agent Interface
Every agent implementation must expose:
- `invoke(inputs) -> outputs` — synchronous entry point
- `stream(inputs) -> events` — streaming entry point for long-running agents
- `describe() -> manifest` — self-description for registry discovery

8. Workflow Engine (S6)

The Workflow Engine orchestrates multi-agent sequences declared in workflow definitions (GWS-001+).

8.1 Responsibilities
- Parse workflow definitions
- Dispatch steps to the Agent Runtime
- Manage checkpoints and resume support
- Handle branching, parallelism, and conditional steps
- Produce an audit trail of every step executed

8.2 Checkpointing
The Workflow Engine must checkpoint after every step that mutates the PKG. Checkpoints contain:
- Workflow ID and step ID
- PKG revision at checkpoint time
- Agent outputs and validation results
- Pending next actions

9. Message Bus (S7)

The Message Bus is the communication fabric between subsystems and between agents.

9.1 Channels
- `pkg.events` — PKG mutation events
- `agent.commands` — dispatch commands from Workflow Engine to Agent Runtime
- `agent.events` — agent progress and completion events
- `validation.events` — validation findings
- `governance.events` — approval and certification events
- `audit.events` — audit log entries

9.2 Delivery Semantics
- At-least-once delivery for command channels
- At-most-once delivery for event channels
- Idempotency required for all command handlers
- Ordering preserved within a channel partition

10. CLI Interface (S8)

The CLI is the operator-facing surface of Genesis.

10.1 Required Commands
- `genesis init` — create a new production session and PKG
- `genesis ingest <brief>` — ingest a synopsis or brief
- `genesis run <workflow>` — execute a workflow
- `genesis query <cypher|graphql>` — query the PKG
- `genesis validate` — trigger validation
- `genesis approve <gate>` — record a governance approval
- `genesis certify` — issue the Production Knowledge Package
- `genesis export <view>` — materialize a view from the PKG
- `genesis status` — show session, agent, and workflow status

10.2 Output Formats
- Human-readable by default
- JSON via `--json` flag
- YAML via `--yaml` flag
- Graph projection via `--graph` flag for visualization

11. REST/GraphQL API (S9)

The API surface exposes Genesis to programmatic consumers, including the Movie OS shell and external integrations.

11.1 REST Endpoints
- `POST /sessions` — create a production session
- `POST /sessions/{id}/ingest` — ingest a brief
- `POST /sessions/{id}/workflows/{name}` — run a workflow
- `GET /sessions/{id}/pkg` — query the PKG (graph query in body)
- `POST /sessions/{id}/validate` — trigger validation
- `POST /sessions/{id}/approve/{gate}` — record approval
- `POST /sessions/{id}/certify` — issue PKP
- `GET /sessions/{id}/pkgp` — retrieve the certified PKP

11.2 GraphQL Schema
The GraphQL surface exposes the PKG as a typed graph. Every ontology concept is a GraphQL type. Every semantic relationship is a GraphQL field returning related nodes. Confidence and provenance are first-class fields on every type.

12. LLM Integration Layer (S10)

The LLM Integration Layer abstracts model access so that no agent couples to a specific provider.

12.1 Responsibilities
- Provider registry (OpenAI, Anthropic, local, custom)
- Provider selection per request (cost, capability, latency)
- Prompt assembly from PKG fragments and templates
- Response parsing into structured PKG mutations
- Token and cost accounting written to the Audit Log
- Fallback and retry across providers

12.2 Provider Independence
Agents never call providers directly. They emit structured reasoning requests to the LLM Integration Layer, which translates them into provider calls and returns structured results. This guarantees the Constitutional Charter's mandate that Genesis remain model-independent.

13. Deployment Mapping

| Subsystem | Local | Cloud | Hybrid |
|-----------|-------|-------|--------|
| Graph Database | Embedded | Managed distributed | Synced embedded + managed |
| Provenance Ledger | Local file | Managed log | Replicated log |
| Validation Engine | In-process | Service | Both |
| Governance Engine | In-process | Service | Both |
| Agent Runtime | In-process | Containerized services | Local + cloud workers |
| Workflow Engine | In-process | Service | Both |
| Message Bus | In-memory | Managed broker | Bridged |
| CLI | Local binary | Cloud shell | Same binary |
| REST/GraphQL API | Local server | Cloud gateway | Both |
| LLM Integration Layer | Direct API calls | Gateway service | Both |

14. Security Posture

- All PKG writes require agent identity and signature
- All approvals require governance role credentials
- All external API access requires authentication
- Provenance entries are tamper-evident
- The PKP is signed and verifiable by downstream engines

15. Observability

Every subsystem emits structured events to the Audit Log. The Audit Log is the single source of operational truth. Metrics, traces, and dashboards are derived from it, not stored separately.

16. Approval

This specification is approved as the canonical Reference Architecture of the Genesis Engine. Any implementation must satisfy every interface defined herein, even where the underlying technology choice differs.