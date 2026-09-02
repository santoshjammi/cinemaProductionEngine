Genesis Specification (GSPEC)
GSPEC-051 — Local Deployment Specification

Document ID: GSPEC-051
Title: Local Deployment Specification
Version: 1.0.0
Status: Specification
Authority: Derived from GFS-000, GFS-010

1. Purpose

This Specification defines the Local Deployment profile for the Genesis Engine
— a single-machine installation suitable for individual creators, small teams,
and offline development. Local Deployment provides the full Genesis capability
set with reduced infrastructure assumptions.

2. Scope

Local Deployment includes:
- Genesis Runtime (orchestrator + agents)
- Production Knowledge Graph store (embedded)
- Ontology Compiler toolchain
- Local REST API and GraphQL API
- Local validation pipeline

Local Deployment excludes:
- Multi-tenant isolation
- Horizontal autoscaling
- Managed secrets services
- Federated agent registries

3. System Requirements

- OS: macOS 13+, Ubuntu 22.04+, or Windows 11 with WSL2
- CPU: 8 cores minimum, 16 recommended
- RAM: 16 GB minimum, 32 GB recommended
- Disk: 50 GB free (SSD) for runtime, ontologies, and PKG cache
- Python: 3.11+
- Node.js: 20+ (for TypeScript tooling and GraphQL server)
- Docker: 24+ (optional, for containerized graph store)

4. Directory Layout

~/.genesis/
├── config.yaml          # local configuration
├── ontologies/          # compiled ontology artifacts
├── productions/         # one directory per production
│   └── {production_id}/
│       ├── brief.yaml
│       ├── pkg.json
│       ├── provenance/
│       └── validations/
├── cache/               # model and ontology cache
├── logs/
└── db/                  # embedded graph store files

5. Configuration

`config.yaml` defines:
- `runtime.mode`: "local"
- `runtime.graph_store`: "embedded" | "docker-neo4j"
- `runtime.api.bind`: host and port (default 127.0.0.1:8080)
- `runtime.api.auth`: "disabled" | "static-token"
- `agents.registry`: path to local agent registry
- `models.providers`: per-provider endpoints and API keys (env-injected)
- `validation.strict`: boolean, default false

Secrets MUST NOT be stored in `config.yaml`. They are read from environment
variables or a local `.env` file with `chmod 600`.

6. Embedded Graph Store

The default Local graph store is an embedded embedded key-value backed
adjacency-list engine (`genesis-graph-local`) sufficient for productions up to
~250k nodes. For larger productions, operators MAY switch to `docker-neo4j`,
which launches a Neo4j community container on `localhost:7687`.

Switching stores is performed via `genesis runtime switch-store docker-neo4j`.
PKG data is migrated automatically.

7. API Surface

Local Deployment exposes:
- REST: http://127.0.0.1:8080/v1 (GSS-701)
- GraphQL: http://127.0.0.1:8080/graphql (GSS-501)
- Agent SSE: http://127.0.0.1:8080/v1/workflows/{id}/events

By default the API binds to loopback only. Binding to other interfaces is
explicitly opt-in and requires `runtime.api.auth: static-token`.

8. CLI

`genesis` is the local entrypoint. Key commands:

- `genesis init` — initialize `~/.genesis/`
- `genesis ontology compile` — run the Ontology Compiler (GSPEC-031)
- `genesis production create --brief path/to/brief.yaml`
- `genesis production discover {productionId}`
- `genesis production validate {productionId}`
- `genesis production readiness {productionId}`
- `genesis runtime status`
- `genesis runtime logs --follow`

9. Bootstrap Sequence

1. `genesis init` creates the directory layout and default config.
2. `genesis ontology compile` populates `~/.genesis/ontologies/`.
3. `genesis runtime start` launches the API server and agent workers.
4. Health check at `/v1/health` returns 200 when ready.

Bootstrap is idempotent; re-running `genesis init` preserves existing
productions and config.

10. Production Lifecycle (Local)

- Create: `genesis production create` ingests a Brief, creates a PKG stub.
- Discover: `genesis production discover` runs the Discovery Workflow (GWS-001)
  synchronously by default, or `--async` with SSE.
- Validate: `genesis production validate` runs SHACL + JSON Schema + business
  rules and writes a ValidationReport to `productions/{id}/validations/`.
- Readiness: `genesis production readiness` returns the readiness assessment.
- Export: `genesis production export` materializes the Production Knowledge
  Package to a directory or archive.

11. Backups

Local Deployment recommends daily snapshots of `~/.genesis/productions/` and
`~/.genesis/db/`. The `genesis runtime snapshot` command produces a tarball
including the embedded store, configuration (minus secrets), and ontologies.

12. Limitations and Upgrade Path

Local Deployment is single-user. When a team exceeds one concurrent user,
requires shared PKG access, or needs multi-tenant isolation, operators MUST
migrate to Cloud Deployment (GSPEC-052) or Enterprise Architecture (GSPEC-061).
The `genesis runtime export-to-cloud` command produces a migration bundle.

13. Security Posture

- Loopback-only API by default.
- No remote model invocation unless explicitly configured.
- Secrets loaded from environment, never logged.
- Production data remains on local disk; no telemetry is sent.

14. Cross-References

- Cloud Deployment: GSPEC-052
- Enterprise Architecture: GSPEC-061
- Ontology Compiler: GSPEC-031
- REST API: GSS-701
- GraphQL API: GSS-501