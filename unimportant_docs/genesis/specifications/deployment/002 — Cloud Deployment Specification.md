Genesis Specification (GSPEC)
GSPEC-052 — Cloud Deployment Specification

Document ID: GSPEC-052
Title: Cloud Deployment Specification
Version: 1.0.0
Status: Specification
Authority: Derived from GFS-000, GFS-010, GSPEC-051

1. Purpose

This Specification defines the Cloud Deployment profile for the Genesis Engine
— a managed, multi-tenant deployment suitable for studios, production houses,
and platform integrators. Cloud Deployment provides horizontal scaling, shared
Production Knowledge Graphs, federated agent registries, and operational
observability.

2. Scope

Cloud Deployment includes:
- Genesis Runtime cluster (orchestrator + agent workers)
- Managed Production Knowledge Graph store (Neo4j or equivalent)
- Ontology Compiler service
- REST and GraphQL API gateways
- Asynchronous workflow engine
- Validation pipeline
- Observability stack (logs, metrics, traces)
- Secrets management integration

Cloud Deployment excludes:
- On-premises air-gapped installations (see Enterprise Architecture GSPEC-061)
- Direct end-user media generation (handled by Studio Engine)

3. Reference Topology

- API Gateway (REST + GraphQL) — stateless, horizontally scaled
- Orchestrator Pool — stateful per-session, partitioned by production id
- Agent Worker Pool — autoscaled per agent type and queue depth
- Graph Store — managed Neo4j cluster (or AWS Neptune / Azure Cosmos Graph)
- Validation Service — dedicated workers for SHACL and JSON Schema validation
- Ontology Compiler Service — on-demand and scheduled compilation jobs
- Object Store — Brief YAML, PKG exports, validation reports
- Message Bus — Agent Message envelopes (GSS-601) over NATS or Kafka
- Secrets Manager — platform-native (AWS Secrets Manager, Azure Key Vault)
- Observability — OpenTelemetry collector, Prometheus, Loki, Tempo

4. Tenancy

Cloud Deployment is multi-tenant. Each tenant is identified by a Tenant ID in
the JWT claim set. Production IDs are namespaced per tenant. The Graph Store
enforces tenant isolation via row-level security labels on every node and edge.

A single PKG node MUST NOT be visible to more than one tenant unless explicitly
shared via a cross-tenant collaboration contract recorded in the registry.

5. Data residency

Tenants MAY select a primary region for their data. PKG data, Briefs, and
validation reports are pinned to the primary region. Ontologies and compiled
artifacts are globally replicated read-only. Backups remain in the primary
region unless a cross-region replication policy is configured.

6. Compute

- API Gateway: minimum 3 replicas across 3 availability zones.
- Orchestrator: minimum 2 replicas per active production region.
- Agent Workers: autoscaled 1..N per agent type. Scale-to-zero is permitted
  for cold agent types with a documented cold-start SLA.
- Validation Workers: minimum 2 replicas, autoscaled on queue depth.

7. Storage

- Graph Store: Neo4j 5+ cluster with 3 core members and read replicas. Page
  cache sized to hold the working set of the largest active PKG.
- Object Store: S3-class service with bucket-per-tenant and lifecycle policies
  moving exports to cold storage after 90 days.
- Relational fallback: PostgreSQL 15+ for metadata, sessions, and audit logs.

8. Networking

- Public API endpoints terminate TLS 1.3 at the gateway.
- Internal traffic uses mTLS between services via a service mesh.
- Agent Worker egress to model providers is restricted to a dedicated egress
  proxy with allow-listed domains (per GFS-000 §16 provider-independence).

9. Authentication and Authorization

- OAuth 2.1 + OIDC for user identity.
- Service-to-service: SPIFFE/SPIRE workload identities.
- Tenant RBAC enforced at API Gateway and Graph Store.
- Agent invocation requires `genesis.agent.invoke` scope.

10. API Surface

Same canonical surfaces as Local Deployment:
- REST (GSS-701) at `https://api.genesis.{tenant}.movieos.dev/v1`
- GraphQL (GSS-501) at `https://api.genesis.{tenant}.movieos.dev/graphql`
- Agent SSE for streaming workflow events.

A management plane API (`/v1/admin`) provides tenant, quota, and registry
operations restricted to platform administrators.

11. Workflows

Cloud Deployment uses an asynchronous workflow engine (Temporal or equivalent).
Every Discovery, Validation, and Agent Invocation creates a durable workflow
with checkpointing. Workflow state survives worker restarts and may be queried
via `/v1/workflows/{id}`.

12. Observability

- Logs: structured JSON, shipped to Loki/CloudWatch. Trace and Tenant IDs are
  mandatory fields.
- Metrics: Prometheus scrape at `/metrics`. Core metrics: pkgs_active,
  workflow_duration_seconds, validation_failures_total, agent_invocations_total.
- Traces: OpenTelemetry, sampled at 10% default, 100% for production-critical
  workflows.
- Alerts: defined in `runtime/alerts/*.yaml` with runbooks linked.

13. Scaling

- Horizontal scaling is the default. Vertical scaling is reserved for the Graph
  Store core members.
- Autoscaling targets: CPU 70%, queue depth > 10, p95 latency > 500ms.
- Maximum cluster size is governed by tenant quota (see GSPEC-062).

14. Disaster Recovery

- Graph Store: automated daily snapshots, 35-day retention, cross-region replica.
- Object Store: versioning enabled, 14-day undelete, 90-day lifecycle.
- RPO: 15 minutes. RTO: 2 hours for full API availability.
- DR runbooks executed quarterly.

15. Upgrade Path

Cloud Deployment supports in-place upgrades of the Genesis Runtime with rolling
restarts. Ontology Compiler upgrades require a compile-then-swap sequence:
compile to a staging dist, validate against the test corpus, then atomically
swap the active dist pointer.

16. Cross-References

- Local Deployment: GSPEC-051
- Enterprise Architecture: GSPEC-061
- Scalability: GSPEC-062
- REST API: GSS-701
- GraphQL API: GSS-501
- Agent Message: GSS-601