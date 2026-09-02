# GKC-010 — Engineering Review

> Adversarial review of `DESIGN/010-storage.md`.

## Review Stance

The reviewer is a storage engineer who has lost data to non-atomic writes, been paged on cache-corruption loops, and seen GC reclaim live snapshots. They assume storage is unsafe until proven otherwise.

## 1. Workspace Layout (§ 2)

- [ ] All paths are explicit.
- [ ] Path conventions (forward slashes, full hex ids) are stated.
- [ ] Workspace lock is documented; advisory nature is acknowledged.
- [ ] Concurrent-session behavior is defined.

## 2. Snapshot Format (§ 3)

- [ ] Manifest schema is complete.
- [ ] All files in the snapshot directory are listed.
- [ ] Atomic commit (temp + rename) is specified.
- [ ] Partial snapshots are supported (per ADR-Candidate-0030).
- [ ] Content hashes cover every file.

## 3. Graph Storage (§ 4)

- [ ] File format is specified (header, nodes, edges).
- [ ] Nodes and edges are sorted for determinism.
- [ ] Compression is applied.
- [ ] Loading is on-demand (per ADR-Candidate-0025).

## 4. Index Storage (§ 5)

- [ ] Per-index-kind format is specified.
- [ ] Incremental updates are partition-level.
- [ ] Plugin indexes are supported.

## 5. Caches (§ 6)

- [ ] All four cache layers are specified (stage, snapshot, context, query).
- [ ] Cache keys are content-addressed.
- [ ] Eviction policy (LRU + reference counting + retention) is defined.
- [ ] Integrity check on load is specified.

## 6. Versioning (§ 7)

- [ ] Schema versioning is per-blob.
- [ ] Snapshot versioning forms a tree.
- [ ] Workspace versioning handles older/newer GKC versions.

## 7. Compression (§ 8)

- [ ] Default algorithm and level are specified.
- [ ] Compression is per file (per ADR-Candidate-0028).
- [ ] Integrity hashes are pre-compression (deterministic).

## 8. Incremental Updates (§ 9)

- [ ] File-level deltas are described.
- [ ] Index partition rewrites are described.
- [ ] Snapshot tree and flattening are supported.

## 9. GC (§ 10)

- [ ] Reference counting is specified.
- [ ] LRU is specified.
- [ ] Retention policy is configurable.
- [ ] GC safety rules (never reclaim live or parent-of-live) are stated.

## 10. Storage Backend Contract (§ 11)

- [ ] The interface is fully specified.
- [ ] Backend requirements (atomicity, integrity, concurrency, local-first) are stated.
- [ ] Plugin backends are supported.
- [ ] Built-in backend cannot be uninstalled.

## 11. Failure Modes (§ 12)

- [ ] All six failures are typed errors.
- [ ] Disk full and permission denied are distinguished.
- [ ] Plugin backend failure has a defined fallback behavior.
- [ ] No silent failures.

## 12. Observability (§ 13)

- [ ] Storage metrics are enumerated.
- [ ] `gkc doctor` performs integrity checks.
- [ ] `gkc cache stats` reports sizes and hit rates.

## 13. Security (§ 14)

- [ ] Permissions are restrictive.
- [ ] No secrets are persisted.
- [ ] Integrity verification is mandatory.

## 14. Cross-Document Consistency

- [ ] Snapshot format matches `DESIGN/004` § 5.2.
- [ ] Cache layers match `DESIGN/005` § 4.
- [ ] Context cache matches `DESIGN/007` § 11.
- [ ] Query cache matches `DESIGN/006` § 6.
- [ ] Plugin backends match `DESIGN/008` § 4.12.

## 15. Open Questions

- [ ] All five open questions are ADR candidates in `DECISIONS/010-storage-adr-candidates.md`.
- [ ] None block M0.

## 16. Document Quality

- [ ] No implementation code.
- [ ] No language-specific idioms.
- [ ] Reasonable length (target: under 1500 lines).

## 17. Exit Criteria

The document passes iff every checkbox is checked or addressed by an ADR candidate.

Reviewer sign-off: ____________________ Date: __________