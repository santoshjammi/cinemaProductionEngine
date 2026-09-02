# GKC-004 — Engineering Review

> Adversarial review of `DESIGN/004-data-model.md`.

## Review Stance

The reviewer is a storage and versioning specialist who assumes every persistence design hides a future migration nightmare. They look for: non-deterministic inputs, schema evolution gaps, integrity holes, and incremental-correctness flaws.

## 1. Identifier Soundness

For each identifier format in § 2.2:

- [ ] The hash inputs are fully specified (no "etc.").
- [ ] The hash function is named (SHA-256 or equivalent).
- [ ] The canonical serialization that feeds the hash is defined or referenced.
- [ ] The id is namespaced to avoid cross-kind collisions.
- [ ] Human-readable abbreviation does not collide (12-char prefix collision probability is acceptable).

## 2. Schema Evolution

- [ ] Self-describing schemas are required (per ADR-Candidate-0001).
- [ ] Forward compatibility is defined: how does an old reader handle a new optional field?
- [ ] Backward compatibility is defined: how does a new reader handle a missing field?
- [ ] Major version bumps require migration — is the migration mechanism defined?
- [ ] Mixed-schema snapshots (entries on different minor versions) are explicitly allowed; is the rule for major versions explicit?

## 3. Snapshot Atomicity

- [ ] A snapshot is either fully written or not at all (per § 5.2).
- [ ] The atomic commit mechanism (temp + rename) is specified for the filesystem backend.
- [ ] Concurrent writes to the same snapshot id are idempotent (same inputs ⇒ same id ⇒ same content).
- [ ] A failed write does not leave a partial snapshot that could be loaded.

## 4. Determinism of Snapshot

- [ ] § 5.4 lists the non-deterministic inputs that must be normalized.
- [ ] Timestamps are excluded from content hashes.
- [ ] Walk order is sorted.
- [ ] Parallel merge order is deterministic.
- [ ] Locale and encoding are pinned (UTF-8, Unicode-default case-folding).

## 5. Index Coverage

For each index in § 6:

- [ ] Purpose is stated.
- [ ] Indexed fields are enumerated.
- [ ] Builder component (C10) is named.
- [ ] Query consumer is named.
- [ ] Update strategy (incremental vs. rebuild) is defined.
- [ ] Failure mode is defined.

## 6. Incremental Correctness

- [ ] § 10.1 lists the 9 steps; each is unambiguous.
- [ ] The invariant "incremental result == full rebuild result" is stated and testable.
- [ ] The cache identity (per `DESIGN/001` § 7.4) is reused.
- [ ] Cache misses fall back cleanly to full execution.
- [ ] The affected subgraph for graph rebuild is defined (not "the relevant subgraph").

## 7. History and Retention

- [ ] Snapshot chains form a tree, not a DAG (single parent).
- [ ] History queries are listed.
- [ ] Retention policy is configurable; defaults are conservative.
- [ ] GC does not reclaim referenced snapshots.

## 8. Compression

- [ ] Compression is per-file, not per-blob (per § 9.2).
- [ ] Compression is deterministic (same input ⇒ same compressed output).
- [ ] Compression level is configurable.
- [ ] Compression does not break integrity verification (hashes computed pre-compression or post-compression — which?).

## 9. Reference Integrity

- [ ] All cross-object references are by id.
- [ ] Referential integrity is verified at commit.
- [ ] Forward references are not allowed within a snapshot.
- [ ] Dangling references after GC are detected.

## 10. Cross-Document Consistency

- [ ] All object kinds in § 3.4 match `DESIGN/002` § 3.
- [ ] All components referenced (C10, C12, C13) match `DESIGN/003`.
- [ ] Snapshot lifecycle matches `DESIGN/002` § 3.16.
- [ ] Determinism rules match `DESIGN/001` § 7.1.

## 11. Open Questions

- [ ] All five open questions in § 11 are ADR candidates in `DECISIONS/004-data-model-adr-candidates.md`.
- [ ] None block M0; if any do, escalate.

## 12. Document Quality

- [ ] No implementation code.
- [ ] No language-specific idioms.
- [ ] No public API.
- [ ] Reasonable length (target: under 1500 lines).

## 13. Exit Criteria

The document passes iff every checkbox is checked or addressed by an ADR candidate.

Reviewer sign-off: ____________________ Date: __________