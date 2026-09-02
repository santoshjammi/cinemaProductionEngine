# GKC-010 — Engineering Prompt

## Objective

Implement the **Storage component (C13)**: workspace management, snapshot atomic commit/read, cache layers (stage, snapshot, context, query), graph and index persistence, versioning, compression, incremental updates, GC, and the storage backend contract.

## Inputs

- `DESIGN/010-storage.md` (authoritative)
- `DESIGN/004-data-model.md` (for snapshot and schema formats)
- `DESIGN/005-pipeline.md` (for cache integration)
- `DESIGN/008-plugin-framework.md` (§ 4.12 storage backend extension)
- `DECISIONS/010-storage-adr-candidates.md`

## Scope

1. **Workspace management** (§ 2) — `gkc init` creates the workspace layout; `open`/`close`/`lock`/`unlock` manage session access.
2. **Snapshot writer** (§ 3) — atomic commit via temp + rename; manifest with content hashes; integrity verification.
3. **Snapshot reader** (§ 3) — load manifest; verify hashes; support partial loading (per ADR-Candidate-0025).
4. **Graph storage** (§ 4) — binary serialization in sorted order; zstd compression.
5. **Index storage** (§ 5) — per-index-kind binary format; partitioned for incremental updates.
6. **Caches** (§ 6) — stage, context, query caches; content-addressed; LRU eviction.
7. **Versioning** (§ 7) — schema versioning per blob; snapshot tree; workspace version checks.
8. **Compression** (§ 8) — zstd level 3 default; configurable.
9. **Incremental updates** (§ 9) — file-level deltas; partition rewrites for indexes.
10. **GC** (§ 10) — reference counting; LRU; retention policy; safety rules.
11. **Storage backend contract** (§ 11) — define the interface; implement the filesystem backend; plugin backend registration.
12. **Failure modes** (§ 12) — all six failures are typed errors.
13. **Observability** (§ 13) — storage metrics; integrity checks via `gkc doctor`.

## Out of Scope

- Plugin backend implementations (use the filesystem backend; plugins are stubbed).
- Encryption at rest (per ADR-Candidate-0054 if open).
- Cross-workspace cache sharing (per ADR-Candidate-0031: per-workspace).

## Done Conditions

- `gkc init` creates a valid workspace; `gkc doctor` reports it healthy.
- Snapshot write is atomic: killing the process mid-write leaves no partial snapshot.
- Snapshot read verifies all content hashes; corruption is detected.
- All four caches work: write, read, evict; LRU is correct.
- Compression is applied per § 8 and does not break determinism.
- Incremental updates write only affected files (verified by file mtime checks).
- GC respects reference counting and retention policy; never reclaims live snapshots.
- The filesystem backend implements the full storage interface.
- All six failure modes are exercised by tests.

## Constraints

- Implementation language: per `DECISIONS/0010-implementation-language.md`.
- Use stdlib compression (or a single documented library).
- All writes are atomic (temp + rename).
- No external services; filesystem only for the built-in backend.
- Workspace permissions are restrictive (0700 on POSIX).

## Deliverables

- `storage/workspace` — workspace management
- `storage/snapshot-writer`, `storage/snapshot-reader`
- `storage/graphs` — graph persistence
- `storage/indexes` — index persistence
- `storage/caches/{stage,context,query}` — cache implementations
- `storage/versioning` — schema and snapshot versioning
- `storage/compression` — compression integration
- `storage/incremental` — incremental update support
- `storage/gc` — garbage collection
- `storage/backends/filesystem` — built-in backend
- `storage/backends/contract` — storage interface definition
- `storage/observability` — metrics
- `storage/tests/*` — per-feature tests

## Verification

1. `gkc test storage` — all storage tests pass.
2. `gkc init /tmp/test-ws` — creates a valid workspace.
3. `gkc scan gold/empty --workspace=/tmp/test-ws` — writes a snapshot.
4. Kill the process mid-snapshot-write; verify no partial snapshot in `snapshots/`.
5. Corrupt one byte in `registry.bin`; verify `gkc doctor` reports the snapshot as corrupt.
6. Write 100 entries to the stage cache; verify LRU evicts the oldest when the limit is hit.
7. `gkc cache prune` reduces cache size to the configured limit.
8. GC test: a referenced snapshot is not reclaimed; an unreferenced one is.
9. Incremental test: a single-artifact change rewrites only affected files.
10. `gkc doctor` reports storage health.

Report pass/fail per step. Any failure blocks M0.