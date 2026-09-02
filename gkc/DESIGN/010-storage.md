# GKC-010 — Storage Architecture

> How GKC persists knowledge: snapshots, indexes, caches, graphs, versioning, compression, incremental updates, and the storage backend contract.

---

## 1. Purpose

Define the Storage component (C13) as a **durable, atomic, content-addressed, plugin-extensible** persistence layer. After this document, every byte GKC writes has a defined location, schema, integrity guarantee, and lifecycle.

This document defines:

- the **workspace layout** (what's on disk),
- the **snapshot format** (per `DESIGN/004` § 5.2, expanded here),
- **caches** (stage, snapshot, context, query; layers and eviction),
- **graph storage** (how the three graphs are persisted),
- **index storage** (how indexes are persisted),
- **versioning** (schema and snapshot versioning),
- **compression** (per `DESIGN/004` § 9, expanded),
- **incremental updates** (per `DESIGN/005` § 3, storage-side),
- **GC** (reference counting, LRU, retention),
- the **storage backend contract** (plugin extension),
- **failure modes** and **integrity verification**.

---

## 2. Workspace Layout

```
<workspace-root>/
└── .gkc/
    ├── config.json                  (workspace config; per `DESIGN/009` § 8.1)
    ├── manifest.json                (workspace metadata: schema version, GKC version, lock)
    ├── models/                      (model profiles)
    │   └── <profile>.json
    ├── plugins/                     (per-workspace plugins; per ADR-Candidate-0015)
    │   └── <plugin-id>/
    │       ├── manifest.json
    │       └── code/
    ├── snapshots/                   (sealed snapshots; content-addressed)
    │   └── <snapshot-id>/
    │       ├── manifest.json
    │       ├── registry.bin
    │       ├── authority.bin
    │       ├── dependency.bin
    │       ├── ontology.bin
    │       ├── indexes/
    │       │   ├── search.bin
    │       │   ├── traversal-authority.bin
    │       │   ├── traversal-dependency.bin
    │       │   ├── traversal-ontology.bin
    │       │   ├── concepts.bin
    │       │   ├── authority-ranking.bin
    │       │   └── dependency-closure.bin
    │       └── validation.json
    ├── cache/
    │   ├── stage/                   (per-stage outputs; keyed by stage cache identity)
    │   │   └── <stage-id>/<cache-key>.bin
    │   ├── context/                 (context packages; keyed by identity tuple)
    │   │   └── <cache-key>.bin
    │   └── query/                   (query results; keyed by query hash)
    │       └── <cache-key>.bin
    ├── sessions/                    (session logs; per-session; ephemeral)
    │   └── <session-id>.log
    └── tmp/                         (scratch directory for atomic writes)
        └── ...
```

### 2.1 Path conventions

- All paths use forward slashes (normalized on Windows).
- Snapshot ids are full hex (no truncation).
- Cache keys are full hex.
- File extensions: `.bin` for compressed binary; `.json` for uncompressed JSON.

### 2.2 Workspace lock

- `<workspace>/.gkc/manifest.json` contains a `lock` field.
- A session acquires the lock at start; releases at end.
- Lock is advisory (file-based; not enforced by OS).
- Concurrent sessions on the same workspace must use different snapshot branches (per `DESIGN/005` § 9).

---

## 3. Snapshot Format

### 3.1 Snapshot directory (per `DESIGN/004` § 5.2)

```
<snapshot-id>/
├── manifest.json
├── registry.bin
├── authority.bin
├── dependency.bin
├── ontology.bin
├── indexes/
│   └── ...
└── validation.json
```

### 3.2 Snapshot manifest

```json
{
  "schema_version": "gkc.snapshot/1.0.0",
  "snapshot_id": "snap:<hex>",
  "repo_id": "repo:<hex>",
  "parent_id": null,
  "plugin_set_hash": "<hex>",
  "config_hash": "<hex>",
  "gkc_version": "0.1.0",
  "schema_versions": {
    "registry": "gkc.entry/1.0.0",
    "graph": "gkc.graph/1.0.0",
    "ontology": "gkc.ontology-node/1.0.0",
    "validation": "gkc.validation/1.0.0"
  },
  "compiled_at": "2026-07-21T12:00:00.000Z",
  "delta_from_parent": {
    "added": ["entry:<hex>", "..."],
    "modified": ["entry:<hex>", "..."],
    "removed": ["entry:<hex>", "..."]
  },
  "content_hashes": {
    "registry.bin": "sha256:<hex>",
    "authority.bin": "sha256:<hex>",
    "dependency.bin": "sha256:<hex>",
    "ontology.bin": "sha256:<hex>",
    "indexes/search.bin": "sha256:<hex>",
    "...": "..."
  },
  "unbuilt": []
}
```

### 3.3 Atomic commit

1. Write all files to `<workspace>/.gkc/tmp/<snapshot-id>/`.
2. Compute content hashes; write manifest.
3. Verify all hashes.
4. Rename `tmp/<snapshot-id>/` to `snapshots/<snapshot-id>/` (atomic on POSIX).
5. On any failure, discard `tmp/<snapshot-id>/`; no partial state in `snapshots/`.

### 3.4 Partial snapshots (per ADR-Candidate-0030)

A partial snapshot has `unbuilt: [stage-id, ...]` listing the stages not run. Consumers that require a full snapshot reject partials with `partial-snapshot` error. `gkc stats` accepts partials.

---

## 4. Graph Storage

### 4.1 File format

Each graph (`authority.bin`, `dependency.bin`, `ontology.bin`) is a compressed binary containing:

```
GraphHeader
├── schema_version
├── kind (authority | dependency | ontology)
├── node_count
├── edge_count
└── content_hash

Nodes (sorted by node id)
├── node_id
└── node_metadata (varies by graph kind)

Edges (sorted by (source, target, kind))
├── source_id
├── target_id
├── edge_kind
├── edge_metadata (provenance, weight, declared-vs-inferred)
└── ...
```

### 4.2 Serialization

- Nodes and edges are serialized in sorted order for determinism.
- The serialization format is binary (not JSON) for size; the format is documented in the schema registry.
- Compression: zstd level 3 (per `DESIGN/004` § 9).

### 4.3 Loading

- The full graph is loaded into memory on demand (per ADR-Candidate-0025 partial loading).
- Traversal indexes are loaded alongside the graph for O(1) adjacency.

---

## 5. Index Storage

### 5.1 Index file format

Each index (`search.bin`, `traversal-*.bin`, `concepts.bin`, `authority-ranking.bin`, `dependency-closure.bin`) is a compressed binary with a header describing the index kind, schema version, and content hash.

### 5.2 Incremental index updates

- On incremental compile, only affected index partitions are rewritten.
- The index file's manifest records which partitions were rewritten.
- Full index rebuild happens only when the schema version changes.

### 5.3 Plugin indexes

Plugin-provided indexes (per `DESIGN/008` § 4.9) are stored in `indexes/<plugin-index-id>.bin` with the plugin's schema. The framework handles serialization via the plugin's declared schema.

---

## 6. Caches

### 6.1 Stage cache (per `DESIGN/005` § 4.1)

- **Location**: `<workspace>/.gkc/cache/stage/<stage-id>/<cache-key>.bin`.
- **Key**: `(stage id, input content hash, config hash, plugin set hash)` (per `DESIGN/005` § 4.1).
- **Contents**: the stage's typed output, serialized.
- **Eviction**: LRU within `cache.max_size_gb`.
- **Integrity**: content-addressed; corrupt entries detected on load and treated as miss.

### 6.2 Snapshot cache

- Snapshots themselves are the cache for the full pipeline output.
- **Location**: `<workspace>/.gkc/snapshots/<snapshot-id>/`.
- **Eviction**: reference counting + retention policy (`cache.snapshot_retention_per_repo`).

### 6.3 Context cache (per `DESIGN/007` § 11)

- **Location**: `<workspace>/.gkc/cache/context/<cache-key>.bin`.
- **Key**: `(task hash, snapshot id, budget, provider id)`.
- **Contents**: the rendered context package + metadata.
- **Eviction**: LRU.
- **Integrity**: content-addressed.

### 6.4 Query cache (per `DESIGN/006` § 6)

- **Location**: `<workspace>/.gkc/cache/query/<cache-key>.bin`.
- **Key**: `(query hash, snapshot id)`.
- **Contents**: the query result + provenance.
- **Eviction**: LRU.
- **Integrity**: content-addressed.

### 6.5 Cache integrity

- All cache entries are content-addressed.
- On load, the framework verifies the entry's hash; on mismatch, treats as a miss and re-computes.
- Cache corruption never propagates to the IR.

---

## 7. Versioning

### 7.1 Schema versioning (per `DESIGN/004` § 3)

- Every persisted blob carries its schema version.
- Forward compatibility: new optional fields are accepted by old readers.
- Backward compatibility: missing fields are defaulted by new readers.
- Major version bumps require migration.

### 7.2 Snapshot versioning (per `DESIGN/004` § 4.2)

- Snapshots form a tree via `parent_id`.
- Two snapshots with the same `(repo, plugins, config, gkc_version)` have the same id.
- Migration: a snapshot may be upgraded to a newer schema version by a migration pass (produces a new snapshot with a new id).

### 7.3 Workspace versioning

- `<workspace>/.gkc/manifest.json` records the GKC version that last opened the workspace.
- Opening a workspace with an older GKC version produces a `workspace-version-newer` warning.
- Opening a workspace with a newer GKC version triggers auto-migration (if minor/patch) or rejection (if major).

---

## 8. Compression (per `DESIGN/004` § 9)

### 8.1 Default

- **Algorithm**: zstd.
- **Level**: 3 (configurable via `cache.compression_level`).
- **Scope**: per file (per ADR-Candidate-0028).

### 8.2 What is compressed

- `*.bin` files: compressed.
- `*.json` files (manifests, validation): not compressed (small, frequently read).

### 8.3 Integrity

- Content hashes are computed **pre-compression** (over the uncompressed bytes).
- On load: decompress, then verify hash.
- A corrupt compressed file is detected as a hash mismatch.

---

## 9. Incremental Updates (Storage-Side)

### 9.1 Per `DESIGN/005` § 3

- The pipeline computes the affected subgraph; storage writes only the affected files.
- The snapshot's `delta_from_parent` records the entry-level delta.

### 9.2 File-level deltas

- `registry.bin` is rewritten if any entry changed (full file rewrite; the format does not support partial file updates).
- Graph files are rewritten if the graph changed.
- Index files are partitioned; only affected partitions are rewritten.

### 9.3 Snapshot tree

- Incremental snapshots have `parent_id` set.
- A chain of incremental snapshots can be "flattened" into a full snapshot by `gkc cache flatten <snap>` (produces a new full snapshot with the same content).

---

## 10. Garbage Collection

### 10.1 Reference counting

- Snapshots are reference-counted: each live session handle, each pinned snapshot, increments the count.
- A snapshot with count 0 is `gc-eligible`.

### 10.2 LRU eviction

- Caches (stage, context, query) use LRU within `cache.max_size_gb`.
- `gkc cache prune` evicts to the limit.

### 10.3 Retention policy

- `cache.snapshot_retention_per_repo` (default 10): keep the latest N snapshots per repository.
- Older snapshots are `gc-eligible` after the retention window.
- `gkc cache clear --snapshots` evicts all `gc-eligible` snapshots.

### 10.4 GC safety

- GC never reclaims a snapshot with a live handle.
- GC never reclaims a snapshot that is the parent of a live snapshot.
- GC is conservative: if in doubt, keep.

---

## 11. Storage Backend Contract

### 11.1 Default backend: filesystem

The default backend implements the storage interface over the local filesystem (per § 2 layout).

### 11.2 Plugin backends

A plugin can replace the filesystem backend (per `DESIGN/008` § 4.12). The plugin implements the storage interface; the framework routes all I/O through it.

### 11.3 Storage interface (contractual)

```
interface Storage {
  // Workspace
  open(workspace_path) → WorkspaceHandle
  close(workspace_handle)
  lock(workspace_handle) → LockResult
  unlock(workspace_handle)

  // Snapshots
  write_snapshot(workspace_handle, snapshot_dir) → SnapshotId
  read_snapshot(workspace_handle, snapshot_id) → SnapshotDir | SnapshotNotFound
  list_snapshots(workspace_handle) → [SnapshotId]
  delete_snapshot(workspace_handle, snapshot_id)

  // Caches
  write_cache(workspace_handle, cache_kind, cache_key, payload) → CacheAddress
  read_cache(workspace_handle, cache_kind, cache_key) → Payload | CacheMiss
  delete_cache(workspace_handle, cache_kind, cache_key)

  // GC
  gc(workspace_handle, policy) → GCReport
}
```

### 11.4 Backend requirements

- **Atomicity**: `write_snapshot` is atomic (all or nothing).
- **Integrity**: all writes are content-addressed; reads verify hashes.
- **Concurrency**: `lock`/`unlock` serialize concurrent sessions.
- **Local-first**: backends must not require external network (per `DESIGN/001` § 7.8). A backend that requires network is rejected by the capability policy.

### 11.5 Built-in backend

The built-in filesystem backend is registered as `storage:filesystem` and cannot be uninstalled. A plugin backend can override it (per `DESIGN/008` § 4.12).

---

## 12. Failure Modes

| Failure | Behavior |
|---|---|
| Disk full | `storage-full` error; snapshot not written; session ends with exit 4 |
| Permission denied | `storage-permission-denied` error; session ends with exit 4 |
| Snapshot not found | `snapshot-not-found` typed error |
| Snapshot corrupt (hash mismatch) | `snapshot-corrupt` typed error; snapshot marked `corrupt`; GC will reclaim |
| Cache corrupt | Treated as cache miss; re-computed |
| Concurrent write conflict | Lock contention; second session waits or fails per `lock` policy |
| Plugin backend failure | Falls back to filesystem backend with `storage-backend-fallback` warning (only if `--allow-fallback` is set; otherwise fatal) |

---

## 13. Observability

### 13.1 Storage metrics

- `snapshot_count`, `cache_size_by_kind`, `cache_hit_rate`, `gc_runs`, `gc_reclaimed_bytes`.
- Exposed via `gkc stats` and `gkc doctor`.

### 13.2 Integrity checks

- `gkc doctor` verifies all snapshot manifests; reports corrupt snapshots.
- `gkc cache stats` reports cache sizes and hit rates.

---

## 14. Security

### 14.1 Permissions

- Storage writes respect filesystem permissions.
- The workspace directory is created with restrictive permissions (0700 on POSIX).
- Plugin backends must respect the capability policy (per `DESIGN/008` § 5).

### 14.2 No secrets in storage

- Storage never persists secrets (API keys, credentials).
- Model profiles may reference env vars for keys but do not store them.

### 14.3 Integrity verification

- All persisted blobs are content-addressed.
- Tampering is detected on load (hash mismatch).
- The workspace manifest is signed with the workspace's local key (optional; per ADR-Candidate-0054).

---

## 15. Open Questions for ADR

Surfaced in `DECISIONS/010-storage-adr-candidates.md`:

1. Should storage support encryption at rest?
2. Should the workspace manifest be cryptographically signed?
3. Should snapshots support deduplication (cross-snapshot content sharing)?
4. Should the stage cache be shared across GKC versions?
5. Should storage support transactions across multiple cache writes?