Genesis Specification (GSPEC)
GSPEC-072 — Graph Database Implementation Guide

Document ID: GSPEC-072
Title: Graph Database Implementation Guide
Version: 1.0.0
Status: Specification
Authority: Derived from GFS-000 §5, GSS-001, GSS-301, GSS-401

1. Purpose

This Specification defines how the Production Knowledge Graph is implemented
atop a graph database. It establishes the storage model, indexing strategy,
constraint enforcement, query patterns, and migration procedures so that any
conforming graph store (Neo4j, Neptune, Cosmos Graph, TigerGraph, embedded)
can serve as the canonical PKG backend.

2. Store Selection

The reference store is Neo4j 5+. Other stores are supported via the adapter
contract in §10. All stores MUST be RDF-serializable (GSS-301) to preserve
portability and to satisfy the Fifth Principle (knowledge is canonical).

3. Label and Type Model

Neo4j labels:
- `:Node` — base label for every PKG node
- `:Node:{Type}` — one additional label per PKG `type` (e.g. `:Node:Character`)
- `:Edge` — edge metadata is stored on relationships (see below)

Relationships:
- One Neo4j relationship type per PKG edge `type`. Relationship type names are
  uppercased and prefixed with `E_` (e.g. `E_APPEARS_IN`).
- Every relationship carries properties: `edge_id`, `confidence`, `created_at`,
  `provenance_agent`, `provenance_session`.

4. Required Properties on Every Node

| Property              | Type     | Notes                                  |
|-----------------------|----------|----------------------------------------|
| node_id               | string   | UUIDv4, indexed unique                 |
| type                  | string   | PKG type, indexed                      |
| label                 | string   | human-readable                         |
| confidence            | string   | EXPLICIT/INFERRED/CONFIRMED/ASSUMED/UNKNOWN |
| created_at            | datetime | indexed                                |
| provenance_agent      | string   | indexed                                |
| provenance_session    | string   | indexed                                |
| tenant_id             | string   | required in multi-tenant deployments   |
| production_id         | string   | indexed                                |
| properties            | string   | JSON blob for type-specific properties |

5. Indexes

- Unique constraint on `(node_id)` and `(edge_id)`.
- Composite index on `(production_id, type)`.
- Composite index on `(production_id, confidence)`.
- Index on `created_at` for time-range queries.
- Full-text index on `label` for search.

Indexes are created by the Ontology Compiler's DDL emitter (GSPEC-031 §3) and
applied via `genesis db migrate`.

6. Constraints

- Uniqueness: `node_id`, `edge_id`.
- Existence: `type`, `label`, `confidence`, `production_id`, `tenant_id`.
- Enum: `confidence` in the five constitutional values.
- Referential integrity: every edge `source_id` and `target_id` MUST reference
  an existing node. Enforced in application code (Neo4j lacks native FK
  constraints) and re-checked by the Validation Service.

7. Query Patterns

### Read a node with provenance
MATCH (n:Node {node_id: $node_id})
RETURN n

### Read a subgraph (BFS up to depth 3)
MATCH p = (n:Node {node_id: $root})-[*1..3]-(m:Node)
WHERE n.production_id = $production_id
RETURN p

### Find nodes by type and confidence
MATCH (n:Node {production_id: $pid, type: $type})
WHERE n.confidence IN $levels
RETURN n ORDER BY n.created_at DESC

### Provenance lookup
MATCH (n:Node {node_id: $id})
RETURN n.provenance_agent, n.provenance_session, n.created_at

### Tenant isolation guard
Every query MUST include `WHERE n.tenant_id = $tenant_id`. A query planner
hook rejects queries missing the tenant filter in multi-tenant deployments.

8. Transactions

- Writes are transactional. A single agent invocation creates one transaction
  containing all node/edge mutations plus the provenance records.
- Long-running discovery workflows commit per-agent-invocation, not per
  workflow, to keep transaction size bounded.
- Optimistic concurrency: each write carries the PKG version it was based on;
  a mismatch triggers a retry with re-fetched state.

9. Migration

Schema migrations are versioned in `db/migrations/` and applied in order. Each
migration is idempotent and includes a rollback. The runtime refuses to start
when the database schema version is ahead of the runtime's supported range.

10. Adapter Contract

A conforming store adapter implements:

class GraphStore(Protocol):
    async def get_node(self, node_id: str) -> Node: ...
    async def upsert_nodes(self, nodes: list[Node], provenance: Provenance) -> None: ...
    async def upsert_edges(self, edges: list[Edge], provenance: Provenance) -> None: ...
    async def query(self, pattern: QueryPattern) -> list[Node | Edge]: ...
    async def validate_integrity(self, production_id: str) -> ValidationReport: ...
    async def export_rdf(self, production_id: str, format: str) -> bytes: ...
    async def import_rdf(self, production_id: str, data: bytes) -> None: ...

Adapters ship as separate packages (`genesis-store-neo4j`,
`genesis-store-neptune`, etc.) and register via the `genesis.stores` entry
point.

11. Backup and Restore

- Daily snapshot of the store (store-native mechanism).
- RDF export (GSS-301) per production on demand.
- Restore validates RDF, re-imports, and re-runs SHACL before marking the
  production readable.

12. Performance

- Query timeout: 5s for reads, 30s for subgraph reads.
- Write batch size: max 500 nodes or edges per transaction.
- Cache: application-level LRU for hot nodes, 100k entries, 5 min TTL.

13. Cross-References

- PKG JSON Schema: GSS-001
- PKG RDF Serialization: GSS-301
- Core OWL Ontology: GSS-401
- Python Implementation: GSPEC-071
- Validation Workflow: GWS-040