Genesis Specification (GSPEC)
GSPEC-062 — Scalability Specification

Document ID: GSPEC-062
Title: Scalability Specification
Version: 1.0.0
Status: Specification
Authority: Derived from GFS-000, GSPEC-052, GSPEC-061

1. Purpose

This Specification defines the scalability requirements, targets, and
operating envelopes for the Genesis Engine across Local, Cloud, and Enterprise
deployments. It establishes the thresholds at which the architecture must
scale, the bottlenecks that must be addressed, and the quotas that govern
tenant consumption.

2. Scaling Dimensions

Genesis scales along five independent dimensions:

1. **Productions** — number of concurrent productions per tenant.
2. **PKG size** — nodes and edges per single Production Knowledge Graph.
3. **Throughput** — agent invocations and validations per second.
4. **Tenancy** — number of tenants and users per deployment.
5. **Ontology surface** — classes, properties, and constraints in the active
   ontology set.

Each dimension has independent targets and may be scaled without forcing the
others to scale.

3. Targets

### Local Deployment (GSPEC-051)
- Productions: unlimited on disk; 1 concurrent active workflow.
- PKG size: up to 250k nodes / 1M edges.
- Throughput: 5 agent invocations/min, 1 validation/min.
- Tenancy: 1 user.
- Ontology surface: full canonical ontology set.

### Cloud Deployment (GSPEC-052)
- Productions: 10,000 concurrent per tenant (default quota).
- PKG size: up to 5M nodes / 25M edges per production.
- Throughput: 500 agent invocations/sec per tenant; 100 validations/sec.
- Tenancy: 1,000 tenants per region.
- Ontology surface: full canonical set plus tenant-approved extensions.

### Enterprise Architecture (GSPEC-061)
- Productions: 100,000 concurrent per federation member.
- PKG size: up to 20M nodes / 100M edges per production.
- Throughput: 5,000 agent invocations/sec per region.
- Tenancy: federated, no hard upper bound.
- Ontology surface: federated set pinned via Ontology Compiler manifest.

4. Latency Targets (p95)

| Operation                        | Local   | Cloud   | Enterprise |
|----------------------------------|---------|---------|------------|
| GET /productions/{id}            | 50 ms   | 120 ms  | 150 ms     |
| GET /pkg/nodes/{id}              | 20 ms   | 60 ms   | 80 ms      |
| POST /pkg/nodes                  | 80 ms   | 200 ms  | 250 ms     |
| POST /agents/{id}/invoke (sync)  | 2 s     | 5 s     | 8 s        |
| POST /productions/{id}/validate  | 30 s    | 60 s    | 90 s       |
| Full discovery workflow          | 5 min   | 15 min  | 30 min     |

5. Bottleneck Analysis

### Graph Store
The Graph Store is the primary scaling bottleneck. Mitigations:
- Read replicas for GET-heavy workloads (Cloud, Enterprise).
- Per-tenant shard partitioning for large PKGs.
- Caching layer for hot nodes (characters, scenes, plot beats).
- Background index refresh to avoid write stalls.

### Agent Worker Pool
Agent throughput is bounded by model provider latency. Mitigations:
- Per-agent-type queues so a slow agent does not block others.
- Batching of independent agent invocations.
- Provider circuit breakers and fallback providers (per GFS-000 §16).
- Caching of agent outputs for deterministic inputs.

### Validation Service
Validation cost grows with PKG size. Mitigations:
- Incremental validation: re-validate only the affected subgraph.
- Parallel SHACL evaluation by shape partition.
- Memoized constraint evaluation keyed on node hash.

### Ontology Compiler
Compilation is offline for Local and rare for Cloud. Mitigations:
- Content-hash caching (GSPEC-031 §9).
- Parallel domain compilation.
- Staging dist with atomic swap (GSPEC-052 §15).

6. Quotas

Cloud and Enterprise enforce per-tenant quotas:

| Quota                       | Default | Configurable |
|-----------------------------|---------|--------------|
| Concurrent productions      | 10,000  | yes          |
| PKG nodes per production    | 5M      | yes          |
| Agent invocations / minute  | 5,000   | yes          |
| Validations / hour          | 2,000   | yes          |
| Workflow runtime / hour     | 200 hrs | yes          |
| Storage per tenant          | 500 GB  | yes          |

Quota breaches return HTTP 429 with `Retry-After` and a `Quota-Reset-At`
header. Quota configuration is restricted to platform administrators.

7. Load Testing

The repository includes a load harness in `tests/load/` that simulates:
- Steady-state PKG reads and writes.
- Burst agent invocation patterns.
- Large validation submissions.
- Multi-tenant concurrent discovery.

Load tests MUST be run before any scalability claim is certified. Results are
recorded in `tests/load/reports/` and referenced from the readiness assessment.

8. Capacity Planning

Operators MUST monitor the leading indicators:
- Graph store cache hit ratio (target > 85%).
- Agent queue depth (target p95 < 20).
- Validation queue wait time (target p95 < 5s).
- API gateway p95 latency (target per §4).

When any indicator breaches its target for 15 consecutive minutes, the
autoscaler MUST add capacity or the operator MUST open a capacity incident.

9. Degradation Modes

- **Degraded Read**: writes disabled, reads served from cache. Triggered when
  the Graph Store loses quorum.
- **Degraded Validation**: full validation disabled, only JSON Schema enforced.
  Triggered when SHACL workers are unavailable.
- **Degraded Discovery**: orchestrator runs with reduced agent set. Triggered
  when a model provider is unavailable.

Each degradation mode is documented in `runtime/runbooks/` and surfaces a
banner in the API health endpoint.

10. Cross-References

- Cloud Deployment: GSPEC-052
- Enterprise Architecture: GSPEC-061
- Ontology Compiler: GSPEC-031
- REST API quotas: GSS-701 §7
- Validation pipeline: GWS-040 (Validation Workflow)