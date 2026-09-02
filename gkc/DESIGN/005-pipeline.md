# GKC-005 — Compiler Pipeline

> The dynamic architecture: stage order, contracts, incremental compilation, caching, parallelism, diagnostics. This is what makes GKC a *compiler*, not a *script*.

---

## 1. Purpose

Define the GKC compilation pipeline as a **directed acyclic graph of stages**, each with a typed contract, a cache identity, a failure policy, and a defined incremental behavior. After this document, the pipeline is implementable without ambiguity.

This document defines:

- the **canonical pipeline** (stages 1–11, their order, their contracts),
- **incremental compilation** (what is re-run when an artifact changes),
- **caching** (cache keys, hit/miss semantics, eviction),
- **diagnostics** (emission, ranking, propagation),
- **parallelism** (what can run in parallel, what must serialize),
- **partial compilation** (running a subset of stages).

---

## 2. Canonical Pipeline

### 2.1 Stage list

| # | Stage | Component | Input | Output | Cacheable | Parallel |
|---|---|---|---|---|---|---|
| 1 | Scan | C1 Scanner | Repository | `[Artifact]` | Yes | Across files |
| 2 | Parse | C2 Parser | `[Artifact]` | `[RawMetadata]` | Yes (per-artifact) | Across artifacts |
| 3 | Normalize | C3 Normalizer | `[RawMetadata]` | `[CanonicalMetadata]` | Yes (per-artifact) | Across artifacts |
| 4 | Resolve | C4 Resolver | `[CanonicalMetadata]`, Registry snapshot | `[ResolvedArtifact]` | Yes (per-artifact) | Across artifacts |
| 5 | Register | C5 Registry | `[ResolvedArtifact]` | Registry delta | Yes (per-entry) | Serialize on registry |
| 6 | Authority | C6 Authority Builder | Registry snapshot | Authority Graph | Yes (full graph) | Internal parallelism |
| 7 | Dependency | C7 Dependency Builder | Registry snapshot | Dependency Graph | Yes (full graph) | Internal parallelism |
| 8 | Ontology | C8 Ontology Compiler | Registry snapshot | Ontology + Ontology Graph | Yes (full) | Internal parallelism |
| 9 | Validate | C9 Validator | IR (registry + graphs + ontology) | Validation Report | Yes (per invariant) | Across invariants |
| 10 | Index | C10 Indexer | IR | Indexes | Yes (per index) | Across indexes |
| 11 | Context (lazy) | C11 Context Compiler | IR + Task + Budget | Context Package | Yes (per package) | Across tasks |

### 2.2 Stage ordering

Stages 1–10 form a strict sequence (each depends on the prior stage's output). Stages 6, 7, 8 are independent of each other (all depend on stage 5 only) and can run in parallel. Stage 9 depends on stages 5, 6, 7, 8. Stage 10 depends on stages 5, 6, 7, 8. Stage 11 depends on stage 10 and runs on demand.

```
       ┌─ Stage 6: Authority  ─┐
       │                       │
Stage 5 ┼─ Stage 7: Dependency ┼─ Stage 9: Validate ─┐
       │                       │                      ├─ Stage 10: Index ─► (Stage 11: Context, lazy)
       └─ Stage 8: Ontology   ─┘                      │
                                                      │
                            (Validator also reads 5) ─┘
```

### 2.3 Stage contracts

Every stage has:

- **Input contract**: a typed value (or set of values).
- **Output contract**: a typed value (or set of values).
- **Diagnostic contract**: zero or more Diagnostics, each with the stage's id as `stage` field.
- **Cache identity**: a function `(input content hash, config hash, plugin set hash, schema version) → cache key`.
- **Failure policy**: per § 5 below.

The input/output types reference domain objects from `DESIGN/002`. They are stable across schema minor versions; major version changes require migration.

### 2.4 Stage 1: Scan — detailed contract

- **Input**: `ScanRequest { repository_root, ignore_rules, classifier_chain }`
- **Output**: `ScanResult { artifacts: [Artifact], diagnostics: [Diagnostic] }`
- **Side effects**: reads filesystem; no writes.
- **Determinism**: walk order is sorted by normalized path; content hashes are SHA-256 of file contents; scan timestamps are excluded from output.
- **Failure policy**: per-file — a file that cannot be read (permission, encoding) is skipped with a `scanner-skip` info diagnostic; the rest of the scan proceeds.

### 2.5 Stage 2: Parse — detailed contract

- **Input**: `ParseRequest { artifact, parser_registry }`
- **Output**: `ParseResult { raw_metadata, diagnostics }`
- **Side effects**: none.
- **Determinism**: parser output is deterministic for a given input and parser version.
- **Failure policy**: per-artifact — a parser exception produces an empty `raw_metadata` and an `error` diagnostic; the artifact proceeds with kind `unknown` and a `parse-failed` marker.

### 2.6 Stage 3: Normalize — detailed contract

- **Input**: `NormalizeRequest { raw_metadata, artifact, inference_rules }`
- **Output**: `NormalizeResult { canonical_metadata, diagnostics }`
- **Determinism**: normalization rules are deterministic; inference is always marked with provenance.
- **Failure policy**: per-artifact — conflicting metadata is resolved by deterministic tie-break (per ADR-Candidate-0009) and flagged with a `warning` diagnostic.

### 2.7 Stage 4: Resolve — detailed contract

- **Input**: `ResolveRequest { canonical_metadata, registry_snapshot, resolver_strategies }`
- **Output**: `ResolveResult { resolved_references, resolved_dependencies, diagnostics }`
- **Determinism**: resolver strategy is deterministic; unresolved references are reported, not silently dropped.
- **Failure policy**: per-artifact — unresolved hard dependencies produce `error` diagnostics; soft ones produce `warning`; the artifact is still registered with unresolved references marked `unresolved`.

### 2.8 Stage 5: Register — detailed contract

- **Input**: `RegisterRequest { resolved_artifact }`
- **Output**: `RegisterResult { registry_entry, delta }`
- **Determinism**: registry entries are content-addressed (per `DESIGN/002` § 3.8); same input ⇒ same entry id.
- **Failure policy**: insertion of an existing entry (same id) is a no-op; duplicate identifiers (different id, same identifier) produce an `error` diagnostic but both entries coexist.
- **Concurrency**: serializes on the registry; multiple resolutions can be computed in parallel, but registration commits one at a time.

### 2.9 Stages 6, 7, 8 — detailed contract

Each graph builder takes a registry snapshot and produces a typed graph plus diagnostics. They are independent of each other and can run in parallel after stage 5.

- **Determinism**: graph edges are sorted by `(source, target, kind)` before emission; output is byte-stable.
- **Failure policy**: per-graph — a cycle detection failure produces a diagnostic; the graph is still emitted with the cycle marked.

### 2.10 Stage 9: Validate — detailed contract

- **Input**: `ValidateRequest { ir, invariants, run_config }`
- **Output**: `ValidateResult { validation_report }`
- **Determinism**: invariants are run in a sorted order; diagnostics are ranked by the total order in `DESIGN/002` § 3.12.
- **Failure policy**: per-invariant — an invariant that throws is marked `not-checked`; other invariants proceed.

### 2.11 Stage 10: Index — detailed contract

- **Input**: `IndexRequest { ir }`
- **Output**: `IndexResult { indexes }`
- **Determinism**: indexes are built in a sorted order; serialized deterministically.
- **Failure policy**: per-index — an index that fails to build is marked `unavailable`; queries against it return `index-unavailable`.

### 2.12 Stage 11: Context (lazy) — detailed contract

- **Input**: `ContextCompileRequest { task_descriptor, token_budget, snapshot, provider }`
- **Output**: `ContextCompileResult { context_package, diagnostics }`
- **Determinism**: same `(task, snapshot, budget, provider)` ⇒ byte-identical package.
- **Failure policy**: per-package — provider failure falls back to the built-in Markdown provider with a `provider-fallback` marker.

---

## 3. Incremental Compilation

### 3.1 The incremental invariant

For any repository delta Δ applied to a parent snapshot S0, the incremental compile produces S1 such that:

> **S1 is byte-identical to a full compile of the same repository state.**

This invariant is testable and is verified by a property test (see `DESIGN/011`).

### 3.2 Delta computation

A delta Δ between two repository states is a set of:

- **Added** artifacts (new paths).
- **Modified** artifacts (same path, different content hash).
- **Removed** artifacts (path no longer exists).

### 3.3 Per-stage incremental behavior

| Stage | Re-runs on Δ if... |
|---|---|
| 1 Scan | Any file in Δ is added/modified/removed. Re-scans only Δ paths. |
| 2 Parse | Any artifact in Δ is added/modified. Re-parses only those. |
| 3 Normalize | Any raw_metadata in Δ. Re-normalizes only those. |
| 4 Resolve | Any canonical_metadata in Δ, OR any artifact that references a Δ artifact. Re-resolves affected. |
| 5 Register | Any resolved_artifact in Δ. Re-registers affected. |
| 6 Authority | Any entry in Δ, OR any entry that references a Δ entry. Re-builds affected subgraph. |
| 7 Dependency | Same as 6. |
| 8 Ontology | Any concept declared by a Δ entry, OR any concept referenced by a Δ entry. Re-builds affected subgraph. |
| 9 Validate | Any entry/graph in Δ. Re-runs affected invariants. |
| 10 Index | Any entry/concept in Δ. Re-builds affected index partitions. |
| 11 Context | Lazy: invalidated when underlying IR changes. Re-builds only on next request. |

### 3.4 Affected-subgraph computation

For stages 4, 6, 7, 8, 9, 10, the "affected subgraph" is computed by:

1. Start with the set of changed entries (from stage 5).
2. For each changed entry, find all entries that reference it or depend on it (reverse closure).
3. The union is the affected set.

The reverse closure is bounded by the dependency closure index (per `DESIGN/004` § 6.5) for hard dependencies; soft dependencies are computed on the fly.

### 3.5 Incremental correctness for graphs

Graph builders re-build only the affected subgraph:

- For each changed entry, remove its old edges.
- For each changed entry, recompute its new edges.
- Re-attach the new edges to the existing graph.
- Re-run cycle detection over the affected subgraph (not the whole graph).

The result is byte-identical to a full rebuild because edges are sorted by `(source, target, kind)` before emission.

---

## 4. Caching

### 4.1 Cache layers

| Layer | Cached | Keyed by | Stored in |
|---|---|---|---|
| Stage cache | Per-stage input/output | `(stage id, input hash, config hash, plugin set hash)` | Workspace cache dir |
| Snapshot cache | Full snapshots | Snapshot id (content-addressed) | Workspace snapshots dir |
| Context cache | Context packages | `(task hash, snapshot id, budget, provider id)` | Workspace cache dir |

### 4.2 Cache hit semantics

- **Stage cache hit**: the stage's output for the given input is already in the cache. The stage is not re-run; the cached output is returned. Byte-identical to a fresh run.
- **Snapshot cache hit**: a snapshot with the same id already exists. The compile is a no-op; the existing snapshot is returned.
- **Context cache hit**: a package with the same identity tuple already exists. The compile is a no-op; the cached package is returned.

### 4.3 Cache miss semantics

A cache miss falls back to full stage execution. The result is written to the cache after the stage completes successfully. Failed stages do not pollute the cache.

### 4.4 Cache eviction

- **LRU** within a configurable size limit.
- **Explicit** via `gkc cache prune`.
- Snapshots are reference-counted; a snapshot with live handles is never evicted.

### 4.5 Cache integrity

- Cache entries are content-addressed; a corrupt entry is detected on load (hash mismatch) and treated as a miss.
- Cache entries are not compressed (fast load); snapshots are compressed (per `DESIGN/004` § 9).

---

## 5. Failure Policies

### 5.1 Stage failure

A stage failure is **fatal to the affected artifact** and **non-fatal to the rest of the compile**. The stage emits a diagnostic and produces an output with the affected artifact marked (`parse-failed`, `resolve-failed`, etc.). Downstream stages process the marked artifact with conservative defaults (e.g., an unresolved reference is treated as `unresolved`).

### 5.2 Plugin failure

A plugin failure is caught at the component boundary (per `DESIGN/003` § C14). The affected artifact is marked `plugin-failed`; the rest of the stage proceeds. Diagnostic: `plugin-failed` with plugin id and exception details.

### 5.3 Hard invariant failure

A `constitutional-violation` diagnostic from stage 9 does not block the compile by default. The snapshot is still written, with the violation in its validation report. The CLI exit code reflects the violation (exit 3) so CI can detect it.

Configuration option `--fail-on-constitutional-violation` makes the compile abort after stage 9; no snapshot is written.

### 5.4 Storage failure

A storage failure during snapshot commit is fatal to the build session. The snapshot is not written; the session ends with exit 4. The prior snapshot (if any) is unaffected.

### 5.5 Diagnostic emission

Every stage may emit diagnostics. Diagnostics are emitted to a session-local diagnostic buffer; they are not directly persisted. At the end of the pipeline, the diagnostic buffer is ranked (per `DESIGN/002` § 3.12) and included in the snapshot's validation report.

---

## 6. Parallelism

### 6.1 Embarrassingly parallel stages

Stages 1, 2, 3, 4 are embarrassingly parallel across artifacts. The pipeline runner may process artifacts concurrently, bounded by a configurable parallelism degree (default: number of CPU cores).

### 6.2 Graph-shaped stages

Stages 6, 7, 8 are independent of each other and can run in parallel after stage 5. Within each graph builder, internal parallelism is possible (e.g., per-edge computation) but the final emission is serialized in a sorted order for determinism.

### 6.3 Per-invariant parallelism

Stage 9 can run invariants in parallel; each invariant is independent. Diagnostics are merged in a sorted order.

### 6.4 Per-index parallelism

Stage 10 can build indexes in parallel; each index kind is independent.

### 6.5 Serialization points

- Stage 5 (Register) serializes on the registry.
- Snapshot commit serializes on the workspace.
- Diagnostic ranking serializes (it needs the full diagnostic set).

### 6.6 Determinism under parallelism

Parallel stages produce outputs that are merged in a **sorted order** before persistence. The sort key is the artifact id (for per-artifact outputs) or the edge id (for graph edges). This guarantees byte-identical output regardless of scheduling.

---

## 7. Partial Compilation

### 7.1 Stage subsets

A compilation unit may request a subset of stages (per `DESIGN/002` § 3.13). The subset must be **downward-closed** in the pipeline DAG: you cannot run stage 6 without stage 5.

### 7.2 Use cases

- `gkc scan` runs stages 1–5 only (no graphs, no validation).
- `gkc validate` runs stage 9 only (over an existing snapshot).
- `gkc context` runs stage 11 only (over an existing snapshot).
- `gkc graph` runs stages 6–8 only (over an existing snapshot).

### 7.3 Partial compile output

A partial compile produces a **partial snapshot** — a snapshot with some components marked `unbuilt`. Partial snapshots are not sealable; they cannot be loaded by consumers that expect a full snapshot. The CLI exposes the partial state via `gkc stats`.

---

## 8. Diagnostics

### 8.1 Emission

Any stage or plugin may emit a Diagnostic (per `DESIGN/002` § 3.20). Diagnostics are emitted to the session's diagnostic buffer.

### 8.2 Severity levels

| Severity | Meaning | Exit code contribution |
|---|---|---|
| `constitutional-violation` | A GENESIS invariant is violated | exit 3 (or abort if configured) |
| `error` | A structural error (unresolved hard dep, parse failure) | exit 2 |
| `warning` | A potential issue (unresolved soft dep, inferred authority) | exit 0 (warning) |
| `info` | Informational (scanner skip, parse skipped for unknown kind) | exit 0 |

### 8.3 Ranking

Diagnostics are ranked by the total order: `(severity, artifact_id, invariant_id, evidence_hash)`. Severity is ordered: `constitutional-violation > error > warning > info`.

### 8.4 Propagation

- Diagnostics are **immutable** once emitted.
- The validation report (stage 9 output) is the canonical ranked set.
- The CLI renders diagnostics in ranked order; machine-readable output (JSON) preserves the rank.

### 8.5 Stable diagnostic ids

Each diagnostic carries a content-addressed id (per ADR-Candidate-0016) so consumers can track the same issue across runs.

---

## 9. Build Session Lifecycle

```
init
  → load plugins (C14)
  → open workspace (C13)
  → create compilation unit(s)
  → run pipeline stages per unit
  → commit snapshot (C13)
  → emit diagnostics (CLI)
  → close session
```

A build session is single-threaded with respect to snapshot commits. Multiple sessions can compile in parallel into different snapshot branches; the workspace lock prevents concurrent commits to the same snapshot id.

---

## 10. Observability Hooks

Each stage emits structured metrics to the session log:

- `stage_id`, `started_at`, `ended_at`, `duration_ms`.
- `input_count` (e.g., number of artifacts), `output_count`.
- `cache_hit` / `cache_miss`.
- `diagnostics_emitted` (count by severity).
- `plugin_calls` (count per plugin id).

`gkc doctor` aggregates these across sessions; `gkc stats` shows the latest session's metrics.

---

## 11. Open Questions for ADR

Surfaced in `DECISIONS/005-pipeline-adr-candidates.md`:

1. Should stage 11 (Context) be a true pipeline stage or a separate on-demand service?
2. Should partial snapshots be loadable with `unbuilt` markers, or strictly rejected?
3. Should the stage cache be shared across workspaces or per-workspace?
4. Should incremental compile re-use cached diagnostics or always re-emit?
5. Should the pipeline runner support stage-level retry on transient failures?