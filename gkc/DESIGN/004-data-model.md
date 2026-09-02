# GKC-004 — Repository Data Model

> How repository knowledge is **structured, identified, versioned, snapshotted, and indexed**. This document is the persistence and query-facing view of the domain model from `DESIGN/002`.

---

## 1. Purpose

`DESIGN/002` defines *what* the domain objects are. This document defines *how they are laid out* for storage, indexing, versioning, and snapshotting. The two documents are tightly coupled; conflicts are resolved by ADR.

Specifically, this document defines:

- **Identifiers** — how every object's stable id is computed.
- **Schemas** — the structural form of each persisted object.
- **Versioning** — how schemas evolve; how snapshots version.
- **Snapshots** — the atomic unit of compiled knowledge.
- **Indexes** — what indexes are built, over what, for what queries.
- **History** — how prior versions of the IR are retained and queried.

---

## 2. Identifier Schemes

### 2.1 Identifier principles

1. **Content-addressed where possible.** Identifiers are derived from the content they reference, not from external allocation.
2. **Deterministic.** Same content + same schema ⇒ same id.
3. **Namespaced.** Every id carries a kind prefix to avoid collisions across object kinds.
4. **Opaque.** Consumers treat ids as opaque strings; they do not parse them.

### 2.2 Identifier formats

| Object | Format | Hash inputs |
|---|---|---|
| Repository | `repo:<hex>` | SHA-256 of canonical tree descriptor |
| Artifact | `artifact:<hex>` | SHA-256 of `(path, content_hash)` |
| Registry Entry | `entry:<hex>` | SHA-256 of `(artifact_id, metadata_canonical, schema_version)` |
| Reference | `ref:<hex>` | SHA-256 of `(source_id, target_descriptor, kind)` |
| Dependency | `dep:<hex>` | SHA-256 of `(source_id, target_descriptor, kind, strength)` |
| Ontology Node | `onto:<namespace>:<term-slug>` | Deterministic slug of the term; namespace-prefixed |
| Knowledge Graph | `graph:<snapshot-id>:<kind>` | Composite; kind ∈ {authority, dependency, ontology} |
| Context Package | `ctx:<hex>` | SHA-256 of `(task_hash, snapshot_id, budget, provider_id)` |
| Validation Report | `vr:<snapshot-id>:<validator-version>` | Composite |
| Diagnostic | `diag:<hex>` | SHA-256 of `(artifact_id, stage_id, invariant_id, evidence_hash)` |
| Repository Snapshot | `snap:<hex>` | SHA-256 of `(repo_id, plugin_set_hash, config_hash, gkc_version, parent_snapshot_id?)` |
| Build Session | `session:<uuid>` | UUID (not content-addressed; not persisted) |
| Plugin | `plugin:<id>@<version>` | Authoritative from manifest |
| Workspace | `ws:<absolute-path-hash>` | SHA-256 of the normalized absolute path |

### 2.3 Hex conventions

- Hex is lowercase.
- SHA-256 is the default hash; shorter ids are not truncated (collision risk is acceptable at SHA-256 width).
- For human-friendly display, ids are abbreviated to the first 12 chars with a `…` suffix; the full id is used in persisted form.

### 2.4 Slug conventions (for ontology terms)

- Lowercase.
- Spaces → hyphens.
- Non-alphanumeric characters stripped.
- Slug collisions within a namespace are merged per ADR-Candidate-0018.

---

## 3. Schemas

### 3.1 Schema principles

1. **Self-describing.** Every persisted blob carries its schema version (per ADR-Candidate-0001).
2. **Forward-compatible.** Schema additions (new optional fields) do not break old readers.
3. **Backward-compatible.** Old snapshots remain readable by new GKC versions; deprecated fields are preserved.
4. **Incompatible changes require major version bump.** Removed fields, renamed fields, or type changes are major-version bumps and require migration.

### 3.2 Schema version format

```
schema_version: "<major>.<minor>.<patch>"
```

- **Major**: incompatible changes (requires migration).
- **Minor**: backward-compatible additions.
- **Patch**: bug fixes to schema validation rules.

### 3.3 Schema registry

GKC ships a schema registry, indexed by `(object kind, schema version)`. The registry is itself versioned and content-addressed. Plugins may register new schemas for new artifact kinds.

### 3.4 Per-object schemas (summary)

Each object's schema is documented in `DESIGN/002` § 3; this section records the schema metadata only.

| Object | Schema id | Current version | Self-describing? |
|---|---|---|---|
| Repository | `gkc.repository/1.0.0` | 1.0.0 | Yes |
| Artifact | `gkc.artifact/1.0.0` | 1.0.0 | Yes |
| Registry Entry | `gkc.entry/1.0.0` | 1.0.0 | Yes |
| Reference | `gkc.reference/1.0.0` | 1.0.0 | Yes |
| Dependency | `gkc.dependency/1.0.0` | 1.0.0 | Yes |
| Ontology Node | `gkc.ontology-node/1.0.0` | 1.0.0 | Yes |
| Knowledge Graph | `gkc.graph/1.0.0` | 1.0.0 | Yes |
| Context Package | `gkc.context/1.0.0` | 1.0.0 | Yes |
| Validation Report | `gkc.validation/1.0.0` | 1.0.0 | Yes |
| Repository Snapshot | `gkc.snapshot/1.0.0` | 1.0.0 | Yes |
| Diagnostic | `gkc.diagnostic/1.0.0` | 1.0.0 | Yes |

---

## 4. Versioning

### 4.1 Object versioning

- **Immutable objects** (Artifact, Registry Entry, Reference, Dependency, Knowledge Graph, Ontology Node, Snapshot, Diagnostic): versioning is by identity. Two different versions of an artifact are two different artifacts (different content hash ⇒ different id). The Registry Entry's `parent` field links versions.
- **Mutable objects** (Workspace, Build Session): versioning is by event log. Each mutation is an event; the current state is the fold over the event log.

### 4.2 Snapshot versioning

Snapshots form a tree rooted at a full (non-incremental) snapshot.

```
snap:aaa (full)
  ├── snap:bbb (incremental from aaa)
  │     └── snap:ccc (incremental from bbb)
  └── snap:ddd (incremental from aaa)
```

- Each snapshot records its `parent` and the `delta` from parent (set of added, modified, removed entry ids).
- Full snapshots have `parent = null`.
- Two snapshots with the same `(repo, plugins, config, gkc_version)` have the same id, regardless of whether one is incremental from the other (content-addressed).

### 4.3 Schema versioning

- Each snapshot records the schema versions of every object kind it contains.
- A snapshot with mixed schema versions (some entries on 1.0.0, some on 1.1.0) is valid as long as the schema major versions match.
- Migration: a snapshot may be "upgraded" by running a migration pass that rewrites entries to a newer schema version. The migrated snapshot has a new id.

### 4.4 Configuration versioning

- Workspace configuration has its own schema version.
- A snapshot records the configuration hash used to compile it; loading a snapshot with a different configuration hash is a `config-mismatch` warning, not an error.

---

## 5. Snapshots

### 5.1 Snapshot contents

A Repository Snapshot is the atomic unit of compiled knowledge. It contains:

```
Snapshot
├── metadata
│   ├── id
│   ├── repo_id
│   ├── parent_id (nullable)
│   ├── plugin_set_hash
│   ├── config_hash
│   ├── gkc_version
│   ├── schema_versions (per object kind)
│   ├── compiled_at (normalized UTC; not part of identity)
│   └── delta_from_parent (added/modified/removed entry ids)
├── registry
│   ├── entries (set of Registry Entry ids; entries themselves persisted separately)
│   └── identifier_index (identifier → entry id)
├── graphs
│   ├── authority_graph (nodes, edges, edge metadata)
│   ├── dependency_graph (nodes, edges, edge metadata)
│   └── ontology_graph (nodes, edges, edge metadata)
├── ontology_nodes
├── indexes
│   ├── search_index
│   ├── traversal_index (per graph)
│   └── concept_index
└── validation_report
```

### 5.2 Snapshot storage form

A snapshot is persisted as a single atomic blob (per ADR-Candidate-0004) with the following layout:

```
<workspace>/snapshots/<snapshot-id>/
├── manifest.json          (metadata, schema versions, content hashes)
├── registry.bin           (entries; format is storage-backend-specific)
├── authority.bin          (authority graph)
├── dependency.bin         (dependency graph)
├── ontology.bin           (ontology graph + nodes)
├── indexes/
│   ├── search.bin
│   ├── traversal-authority.bin
│   ├── traversal-dependency.bin
│   └── concepts.bin
└── validation.json        (validation report)
```

The manifest carries content hashes for every other file; load-time integrity check verifies all hashes.

### 5.3 Snapshot lifecycle

```
building ─► sealed ─► referenced ─► gc-eligible
```

- **building**: in-progress; not yet readable.
- **sealed**: fully written; immutable; readable.
- **referenced**: at least one consumer (CLI, AIOS, IDE) has a handle.
- **gc-eligible**: no live handles; reclaimable by `gkc cache prune`.

### 5.4 Snapshot determinism

For a fixed `(repo state, plugins, config, gkc version)`, the snapshot id and all blob hashes are byte-identical. This is the determinism invariant (`DESIGN/001` § 7.1) made operational.

Non-deterministic inputs that must be normalized before they enter a snapshot:

- Timestamps → normalized to UTC ISO-8601 with millisecond precision, but **excluded** from content hashes.
- Filesystem walk order → sorted by normalized path before hashing.
- Parallel scheduling → output is merged in a deterministic order (by id).
- Locale → UTF-8 normalized; case-folding uses Unicode-default.

---

## 6. Indexes

### 6.1 Search index

- **Purpose**: Full-text search over artifact content and metadata.
- **Built by**: C10 Indexer.
- **Indexed fields**: artifact path, content (tokenized), metadata fields (identifier, version, authority), declared concepts.
- **Query use**: C12 `gkc search`.
- **Update**: Rebuilt incrementally when entries are added/modified.
- **Format**: Implementation-defined; plugin-extensible.

### 6.2 Traversal indexes (per graph)

- **Purpose**: O(1) adjacency lookup for graph traversal.
- **Built by**: C10.
- **Indexed fields**: per-node outgoing and incoming edge lists, by edge kind.
- **Query use**: C12 `gkc explain`, `gkc graph`, impact analysis.
- **Format**: Adjacency lists; serialization is storage-backend-specific.

### 6.3 Concept index

- **Purpose**: Term → ontology nodes lookup.
- **Built by**: C10.
- **Indexed fields**: canonical term, aliases, namespace.
- **Query use**: C12 concept queries; C11 context expansion.
- **Format**: Hash table or trie; backend-specific.

### 6.4 Authority ranking index

- **Purpose**: Pre-computed authority ranking for budget allocation in C11.
- **Built by**: C10.
- **Indexed fields**: entry id → authority level + reference count.
- **Query use**: C11 context budget allocation.

### 6.5 Dependency closure index

- **Purpose**: Pre-computed transitive closure for hard dependencies (up to a bounded depth).
- **Built by**: C10.
- **Indexed fields**: entry id → set of transitive hard-dependency entry ids (bounded depth; deeper closure computed on query).
- **Query use**: C11 context dependency expansion; C12 impact analysis.
- **Note**: Full transitive closure is not pre-computed (could be O(n²) in pathological graphs); bounded depth is configurable.

---

## 7. History

### 7.1 Snapshot chains

History is the chain of snapshots through `parent` links. A workspace's history is a forest of snapshot trees.

### 7.2 History queries

- `gkc registry history <id>` — list all Registry Entry versions for the given identifier.
- `gkc snapshot list` — list all snapshots in the workspace.
- `gkc snapshot diff <a> <b>` — show the delta between two snapshots.

### 7.3 History retention

- Default: keep the latest 10 snapshots per repository.
- Configurable: `workspace.history.retention = { per_repo: N, max_age_days: M }`.
- GC reclaims snapshots that fall outside retention policy.

### 7.4 Entry history

- Registry Entries are immutable; "updating" an artifact creates a new entry with a `parent` link to the old one.
- The registry holds only the latest entry per identifier (per ADR-Candidate-0012); older entries are reachable via snapshot history.

---

## 8. Relationships (Storage View)

### 8.1 Storage-level relationships

```
Workspace
  └── Snapshots (tree)
        ├── Registry Entries
        │     ├── References (to other entries)
        │     ├── Dependencies (to other entries)
        │     └── Concepts (to ontology nodes)
        ├── Graphs
        │     ├── Authority Graph (over entries)
        │     ├── Dependency Graph (over entries)
        │     └── Ontology Graph (over nodes)
        ├── Ontology Nodes
        ├── Indexes
        └── Validation Report
              └── Diagnostics (per entry / workspace)

Build Session
  └── Compilation Units
        └── (produces) Snapshot

Context Cache
  └── Context Packages (keyed by (task, snapshot, budget, provider))
```

### 8.2 Reference integrity

- Every cross-object reference in storage is by id.
- The storage layer verifies referential integrity on snapshot commit; dangling references fail the commit.
- Forward references are not allowed in a sealed snapshot (all referenced ids must be present in the same snapshot or a parent snapshot).

---

## 9. Compression

### 9.1 Compression policy

- Snapshots are compressed at the file level (per file in the snapshot directory).
- Default compression: zstd level 3 (good ratio, fast decode).
- Configurable per workspace.

### 9.2 What is compressed

- `registry.bin`, `*.bin` graph files, `*.bin` index files: compressed.
- `manifest.json`, `validation.json`: not compressed (small, frequently read).

### 9.3 What is not compressed

- Context Packages in the cache: not compressed (they are read by external consumers that may not handle compression).
- Plugin packages: compressed at install time, not by Storage.

---

## 10. Incremental Updates

### 10.1 Incremental compilation

Given a prior snapshot `S0` and a repository delta `Δ`, GKC produces `S1 = S0 + Δ` by:

1. Re-scanning only paths in `Δ` (added, modified, removed).
2. Re-parsing only changed artifacts.
3. Re-resolving references for changed artifacts and any artifacts that referenced them.
4. Re-registering changed entries; computing the registry delta.
5. Re-building graphs over the delta (subgraph re-build, not full rebuild).
6. Re-compiling ontology over the delta.
7. Re-running validation over the delta and the affected subgraph.
8. Re-building indexes incrementally.
9. Committing `S1` with `parent = S0.id` and `delta_from_parent` populated.

### 10.2 Cache reuse

- Stages 1–4 outputs are cached by `(stage id, input content hash, config hash, plugin set hash)`.
- An incremental compile reuses cached outputs for unchanged artifacts.
- Cache misses fall back to full stage execution; the result is cached.

### 10.3 Incremental correctness

The incremental result `S1` must be **byte-identical** to a full compile of the same repository state. This is verified by a property test (see `DESIGN/011`).

---

## 11. Open Questions for ADR

Surfaced in `DECISIONS/004-data-model-adr-candidates.md`:

1. Should the registry index by identifier be a hash table or a trie?
2. Should snapshots support partial loading (load only the registry, not the graphs)?
3. Should the search index be a BM25-style inverted index or a vector index by default?
4. Should the dependency closure depth be configurable per workspace or per query?
5. Should compression be per-file or per-snapshot-blob?