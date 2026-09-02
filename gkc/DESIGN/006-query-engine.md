# GKC-006 — Query Engine

> How GKC answers semantic queries over the compiled IR. This is what makes the substrate **useful** at runtime, after the compile is done.

---

## 1. Purpose

Define the Query Engine (C12) as a **typed, ranked, provenance-carrying** query interface over a sealed Repository Snapshot. After this document, every `gkc search`/`explain`/`graph`/`impact`/`stats` answer is implementable without ambiguity.

This document defines:

- the **query kinds** GKC supports,
- each query's **input contract** and **output contract**,
- **ranking** (how results are ordered),
- **provenance** (how results justify themselves),
- **performance targets** and the indexes that support them,
- **extension** (how plugins add new query kinds).

---

## 2. Query Kinds (Catalog)

| # | Query | Purpose | CLI |
|---|---|---|---|
| Q1 | Search | Full-text + metadata search over the registry | `gkc search` |
| Q2 | Explain | Explain one artifact: identity, authority, deps, refs, concepts | `gkc explain <id>` |
| Q3 | Impact | What is affected if artifact X changes? (reverse dependency closure) | `gkc impact <id>` |
| Q4 | Authority traversal | Walk the authority graph from X; what does X derive authority from? | `gkc authority <id>` |
| Q5 | Dependency traversal | Walk the dependency graph from X; what does X require? | `gkc dependencies <id>` |
| Q6 | Concept lookup | Which artifacts declare or reference concept C? | `gkc concept <term>` |
| Q7 | Graph emit | Emit one of the three graphs in text/JSON/DOT | `gkc graph <kind>` |
| Q8 | Stats | Aggregate counts and health metrics | `gkc stats` |
| Q9 | Diagnostics | Query the validation report | `gkc diagnostics [--severity=...]` |
| Q10 | Find | Structured lookup by kind, authority, identifier, path | `gkc find --kind=... --authority=...` |
| Q11 | Similar | Find artifacts similar to X (by concept overlap, by reference overlap) | `gkc similar <id>` |
| Q12 | Path | Find a path from X to Y in a specified graph | `gkc path <src> <dst> --graph=...` |

Plugin extension: new query kinds can be added via the query extension point (per `DESIGN/008`).

---

## 3. Query Contracts

### 3.1 Common envelope

Every query request carries:

```
QueryRequest {
  snapshot_id: SnapshotId,
  kind: QueryKind,
  params: QueryParams,         // kind-specific
  ranking: RankingPolicy,      // default per kind; overridable
  limit: int,                  // default 50; max configurable
  format: OutputFormat,        // text | json | jsonl | dot (where applicable)
}
```

Every query result carries:

```
QueryResult {
  results: [ResultEntry],
  provenance: [ProvenanceEdge],
  truncated: bool,             // true if limit was hit
  query_hash: string,          // for caching
}
```

A `ResultEntry` is:

```
ResultEntry {
  artifact_id: ArtifactId,
  rank: int,                   // 0-based
  score: float,                // kind-specific; deterministic
  summary: string,             // human-readable one-liner
  metadata: map<string, string>,  // kind-specific fields
}
```

### 3.2 Q1 — Search

- **Params**: `query: string`, `kinds: [ArtifactKind]` (optional filter), `authorities: [AuthorityLevel]` (optional filter), `namespace: string` (optional).
- **Ranking**: BM25 score over the search index, multiplied by authority weight (constitutional=1.5, statutory=1.2, guidance=1.0, deprecated=0.5, unknown=0.8).
- **Provenance**: which tokens matched, in which fields.
- **Index used**: search index (`DESIGN/004` § 6.1).
- **Performance target**: under 200 ms on `gold/large-repo` warm cache.

### 3.3 Q2 — Explain

- **Params**: `id: ArtifactId`, `depth: int` (default 1; how deep to traverse each graph).
- **Output**: identity (path, kind, content hash), metadata summary, authority level and chain, declared references, declared dependencies, declared concepts, validation status.
- **Ranking**: not applicable (single result, structured output).
- **Provenance**: every field's source (which artifact, which stage).
- **Index used**: registry, all three traversal indexes.
- **Performance target**: under 100 ms on `gold/large-repo` warm cache.

### 3.4 Q3 — Impact

- **Params**: `id: ArtifactId`, `depth: int` (default unlimited, bounded by closure), `strength: hard | soft | all` (default hard).
- **Output**: set of artifacts that depend on `id` (transitively, per the dependency graph).
- **Ranking**: by topological distance from `id` (closer = higher rank); ties broken by authority (higher authority first), then by id.
- **Provenance**: the dependency chain from `id` to each result.
- **Index used**: traversal index (dependency graph, reverse direction).
- **Performance target**: under 500 ms on `gold/large-repo` warm cache, depth-bounded.

### 3.5 Q4 — Authority traversal

- **Params**: `id: ArtifactId`, `direction: up | down` (default up).
- **Output**: artifacts in the authority chain above (or below) `id`.
- **Ranking**: by distance from `id`; ties broken by authority level.
- **Provenance**: the authority edge sequence.
- **Index used**: traversal index (authority graph).
- **Performance target**: under 200 ms on `gold/large-repo` warm cache.

### 3.6 Q5 — Dependency traversal

- **Params**: `id: ArtifactId`, `direction: up | down` (default down), `strength: hard | soft | all`.
- **Output**: artifacts that `id` depends on (down) or that depend on `id` (up).
- **Ranking**: by topological distance; ties broken by id.
- **Provenance**: the dependency edge sequence.
- **Index used**: traversal index (dependency graph).
- **Performance target**: under 200 ms on `gold/large-repo` warm cache, depth-bounded.

### 3.7 Q6 — Concept lookup

- **Params**: `term: string`, `namespace: string` (optional).
- **Output**: artifacts that declare or reference the concept.
- **Ranking**: declared-by first (higher rank), then referenced-by; ties broken by authority.
- **Provenance**: whether each result declares or references the concept.
- **Index used**: concept index.
- **Performance target**: under 50 ms on `gold/large-repo` warm cache.

### 3.8 Q7 — Graph emit

- **Params**: `kind: authority | dependency | ontology`, `format: text | json | dot`, `filter: GraphFilter` (optional; by node kind, edge kind, authority).
- **Output**: the graph in the requested format.
- **Ranking**: not applicable.
- **Provenance**: not applicable.
- **Index used**: traversal indexes.
- **Performance target**: under 1 s on `gold/large-repo` warm cache.

### 3.9 Q8 — Stats

- **Params**: none.
- **Output**: aggregate counts (artifacts by kind, entries by authority, diagnostics by severity, graph edge counts, index availability, snapshot metadata).
- **Ranking**: not applicable.
- **Provenance**: not applicable.
- **Performance target**: under 50 ms on any snapshot.

### 3.10 Q9 — Diagnostics

- **Params**: `severity: [Severity]` (optional filter), `artifact: ArtifactId` (optional filter), `invariant: InvariantId` (optional filter).
- **Output**: ranked diagnostics matching the filter.
- **Ranking**: by the validation report's total order (per `DESIGN/002` § 3.12).
- **Provenance**: not applicable (diagnostics are self-describing).
- **Performance target**: under 100 ms on any snapshot.

### 3.11 Q10 — Find

- **Params**: `kind: ArtifactKind` (optional), `authority: AuthorityLevel` (optional), `identifier: string` (optional), `path: string` (optional).
- **Output**: matching artifacts.
- **Ranking**: by id (deterministic; no relevance ranking for structured lookup).
- **Provenance**: not applicable.
- **Index used**: registry indexes.
- **Performance target**: under 50 ms on `gold/large-repo` warm cache.

### 3.12 Q11 — Similar

- **Params**: `id: ArtifactId`, `by: concept | reference | both` (default both), `limit: int`.
- **Output**: artifacts similar to `id`.
- **Ranking**: by overlap score (Jaccard over concept sets and reference sets); ties broken by authority, then id.
- **Provenance**: the shared concepts and references.
- **Index used**: concept index, traversal indexes.
- **Performance target**: under 1 s on `gold/large-repo` warm cache.

### 3.13 Q12 — Path

- **Params**: `src: ArtifactId`, `dst: ArtifactId`, `graph: authority | dependency | ontology`, `max_depth: int` (default 10).
- **Output**: a path (sequence of edges) from src to dst, or `no-path`.
- **Ranking**: shortest path (BFS); ties broken by lexicographically smallest edge sequence.
- **Provenance**: the edge sequence itself.
- **Index used**: traversal indexes.
- **Performance target**: under 500 ms on `gold/large-repo` warm cache, depth-bounded.

---

## 4. Ranking Policies

### 4.1 Default ranking

Each query kind has a default ranking policy (per § 3). Defaults are tuned for "most useful first" for human consumption.

### 4.2 Ranking policy override

A query request may override the ranking policy:

```
RankingPolicy {
  primary: RankingKey,         // relevance | authority | recency | topological-distance | id
  secondary: RankingKey,       // tie-break
  direction: asc | desc,
}
```

Not all keys are valid for all query kinds (e.g., `topological-distance` only applies to traversal queries). Invalid combinations are rejected with a typed error.

### 4.3 Determinism

Ranking is **deterministic** for a fixed `(query, snapshot, policy)`. The tie-break is always total: `(primary, secondary, id)`.

### 4.4 Authority weighting

When `primary = relevance` (search), the relevance score is multiplied by the authority weight (per § 3.2). This implements "authority wins" (per `DESIGN/001` § 8.3) at query time.

---

## 5. Provenance

### 5.1 Why provenance

Every result carries provenance so consumers (especially AI agents) can justify their conclusions. An agent that says "artifact X depends on Y" must be able to point to the edge in the dependency graph that justifies this.

### 5.2 Provenance format

```
ProvenanceEdge {
  source: ArtifactId,
  target: ArtifactId,
  edge_kind: string,           // authority | dependency | ontology edge kind
  graph: authority | dependency | ontology,
  declared_in: ArtifactId,     // which artifact declared this edge
  inferred: bool,              // true if inferred by GKC rather than declared
}
```

### 5.3 Provenance completeness

For every result, the provenance set is **sufficient to re-derive the result**. A consumer that follows the provenance edges must arrive at the same conclusion as the query engine.

---

## 6. Caching

### 6.1 Query result cache

Query results are cached by `(query_hash, snapshot_id)`. The cache is in-memory per build session and optionally on-disk in the workspace cache.

### 6.2 Cache invalidation

A query result cache entry is invalidated when:

- The underlying snapshot is GC'd.
- The query engine version changes (recorded in the cache key).
- The user runs `gkc cache clear --queries`.

### 6.3 Cache hit semantics

A cache hit returns the cached result, including provenance. Byte-identical to a fresh query.

---

## 7. Performance Targets

(Per `DESIGN/001` § 6 S5: under 1 s on `gold/large-repo` warm cache.)

| Query | Target | Notes |
|---|---|---|
| Search | 200 ms | BM25 lookup + authority weighting |
| Explain | 100 ms | Single-artifact lookup + shallow traversal |
| Impact | 500 ms | Reverse closure, depth-bounded |
| Authority traversal | 200 ms | Graph traversal |
| Dependency traversal | 200 ms | Graph traversal |
| Concept lookup | 50 ms | Hash lookup |
| Graph emit | 1 s | Full graph serialization |
| Stats | 50 ms | Aggregate counters |
| Diagnostics | 100 ms | Filtered scan of validation report |
| Find | 50 ms | Index lookup |
| Similar | 1 s | Set-overlap computation |
| Path | 500 ms | BFS, depth-bounded |

Targets are verified by `DESIGN/011` performance tests.

---

## 8. Failure Modes

| Failure | Behavior |
|---|---|
| Snapshot not found | Typed error: `snapshot-not-found` |
| Snapshot corrupt | Typed error: `snapshot-corrupt` |
| Required index unavailable | Typed error: `index-unavailable`; may fall back to slower scan if `--allow-scan` is set |
| Invalid query params | Typed error: `invalid-query` with details |
| Unknown query kind | Typed error: `unknown-query-kind` |
| Plugin-provided query kind throws | Typed error: `query-plugin-failed`; the query returns no results with a diagnostic |

Every failure mode is covered by a test in `DESIGN/011`.

---

## 9. Extension

### 9.1 Adding a new query kind

A plugin registers a new query kind by providing:

- `kind_id` — namespaced identifier (e.g., `acme:similar-by-embedding`).
- `params_schema` — schema for the kind-specific params.
- `result_schema` — schema for the kind-specific result metadata.
- `execute` — function: `(QueryRequest, Snapshot, Indexes) → QueryResult`.
- `required_indexes` — list of index kinds the query needs (the framework ensures these are built before invoking).

### 9.2 Built-in queries are not privileged

Built-in query kinds (Q1–Q12) are registered at startup exactly like plugin-provided ones. The query engine has no special-case code for built-ins; they go through the same dispatch path.

### 9.3 Query kind conflicts

If two plugins register the same `kind_id`, the framework rejects the second with a `query-kind-conflict` diagnostic. Plugins must namespace their ids.

---

## 10. Output Formats

### 10.1 Text (default for terminal)

Human-readable, with provenance summarized inline. Stable across versions for the same query (for scripting).

### 10.2 JSON

Structured output with full provenance. Schema is self-describing (per ADR-Candidate-0001).

### 10.3 JSONL

One JSON object per result entry. Suitable for streaming to other tools.

### 10.4 DOT

For graph queries only; emits a Graphviz DOT file.

### 10.5 Format selection

The CLI `--format` flag selects the output format (per `DESIGN/009`). The query engine supports all formats; the CLI is responsible for routing to stdout/file.

---

## 11. Open Questions for ADR

Surfaced in `DECISIONS/006-query-engine-adr-candidates.md`:

1. Should query results support pagination (beyond `limit`)?
2. Should the query engine support streaming results (for very large result sets)?
3. Should the in-memory query cache be shared across build sessions?
4. Should plugin-provided query kinds be allowed to mutate the snapshot (e.g., for "auto-fix" queries)?
5. Should the query engine expose a programmatic API (not just via CLI)?