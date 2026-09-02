# GKC-004 — Engineering Prompt

## Objective

Implement the **data model persistence layer**: serialization, deserialization, schema registry, snapshot writer, snapshot reader, integrity verification. No query support; no index building; just durable read/write of the IR.

## Inputs

- `DESIGN/004-data-model.md` (authoritative)
- `DESIGN/002-domain-model.md` (for types)
- `DECISIONS/004-data-model-adr-candidates.md`

## Scope

1. **Identifier module** — implements the identifier formats in § 2.2. Pure functions; no I/O.
2. **Schema registry** — registers per-object schemas; supports lookup by `(kind, version)`. Schemas are self-describing (each serialized blob carries its schema id).
3. **Serializer/deserializer** — for each object kind in § 3.4. Round-trip lossless. Deterministic byte output for a given input.
4. **Snapshot writer** — assembles a snapshot directory per § 5.2; writes manifest with content hashes; atomic commit (write to temp, rename on success).
5. **Snapshot reader** — reads a snapshot; verifies manifest hashes; rejects on mismatch with a `snapshot-corrupt` diagnostic.
6. **Incremental delta computation** — given two snapshots, compute the entry-level delta (added, modified, removed) per § 10.1.
7. **Compression integration** — apply zstd (or configurable equivalent) per § 9.
8. **History queries** — `gkc snapshot list`, `gkc snapshot diff` (output only; no CLI parsing yet, just the underlying queries).

## Out of Scope

- Index building (covered by C10 in `DESIGN/003`).
- Query answering (covered by C12 in `DESIGN/006`).
- Context cache (covered by C11 + C13 in `DESIGN/007`).
- Plugin loading.
- CLI argument parsing.

## Done Conditions

- All 11 object kinds in § 3.4 have serializers and deserializers with round-trip property tests.
- Snapshot writer produces byte-identical output for the same input across runs (determinism property test).
- Snapshot reader detects corruption (intentionally corrupt one file; reader rejects with a typed error).
- Incremental delta computation is correct: applying the delta to the parent yields the child's registry.
- Compression is applied per § 9 and does not break determinism.
- History queries return correct results on a synthetic 5-snapshot chain.

## Constraints

- Implementation language: per `DECISIONS/0010-implementation-language.md`.
- Use stdlib compression if available; otherwise pick a single library and document it.
- No external services; filesystem only.
- All file writes are atomic (temp file + rename).

## Deliverables

- `data/identifiers` — id format implementations
- `data/schema-registry` — schema registry
- `data/serde` — per-kind serializer/deserializer
- `data/snapshot-writer`, `data/snapshot-reader`
- `data/delta` — incremental delta computation
- `data/compression` — compression integration
- `data/history` — history queries
- `data/tests/*` — round-trip, determinism, corruption, delta, history tests

## Verification

1. `gkc test data` — all data layer tests pass.
2. Property test: for any IR, `serialize(serialize(obj)) == serialize(obj)` (idempotent serialization).
3. Property test: for any IR, `deserialize(serialize(obj)) == obj` (lossless round-trip).
4. Property test: writing the same IR twice yields byte-identical snapshot directories.
5. Negative test: corrupting one byte in `registry.bin` causes the reader to reject the snapshot.
6. Integration test: build snapshot S0; build incremental S1 from S0; verify S1's registry equals a full rebuild's registry.

Report pass/fail per step. Any failure blocks M1.