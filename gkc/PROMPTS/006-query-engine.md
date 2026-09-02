# GKC-006 — Engineering Prompt

## Objective

Implement the **Query Engine (C12)**: typed query dispatch, ranking, provenance, caching, and all 12 built-in query kinds. Reads from a sealed snapshot; never mutates.

## Inputs

- `DESIGN/006-query-engine.md` (authoritative)
- `DESIGN/004-data-model.md` (for snapshot and indexes)
- `DESIGN/003-component-architecture.md` (for C12 boundaries)
- `DECISIONS/006-query-engine-adr-candidates.md`

## Scope

1. **Query dispatch** — register Q1–Q12 with their params/result schemas; dispatch by kind; reject unknown kinds.
2. **Common envelope** — implement `QueryRequest`, `QueryResult`, `ResultEntry`, `ProvenanceEdge` per § 3.1.
3. **Each of Q1–Q12** — implement per its contract in §§ 3.2–3.13. Use the indexes from `DESIGN/004` § 6; if an index is unavailable, fail with `index-unavailable` (or fall back to scan if `--allow-scan` is set).
4. **Ranking** — implement the default ranking per query kind; support `RankingPolicy` override per § 4.2; enforce total tie-break.
5. **Provenance** — emit `ProvenanceEdge` sets that are sufficient to re-derive each result per § 5.3.
6. **Caching** — in-memory per session; optional on-disk in workspace cache; invalidate per § 6.2.
7. **Output formats** — text, JSON, JSONL, DOT (for graph queries).
8. **Failure modes** — all eight in § 8 are typed errors, not exceptions.
9. **Extension registry** — plugin-provided query kinds can be registered; conflicts are rejected per § 9.3.

## Out of Scope

- Building indexes (that's C10).
- CLI argument parsing (that's C15 / `DESIGN/009`).
- Snapshot loading (that's C13).
- Real plugin loading (use stubs).

## Done Conditions

- All 12 query kinds are implemented and pass contract tests (input → expected output structure).
- Ranking is deterministic: same `(query, snapshot, policy)` ⇒ byte-identical ranked result.
- Provenance re-derivation test: for each result, following the provenance edges yields the same result.
- All performance targets in § 7 are met on `gold/large-repo` warm cache (within 2× tolerance for M2; tight targets by M5).
- All eight failure modes are exercised by tests.
- Plugin-provided query kind registration works (with a stub plugin).
- Output in all four formats is valid (text stable; JSON schema-conformant; JSONL one-object-per-line; DOT graphviz-valid).

## Constraints

- Implementation language: per `DECISIONS/0010-implementation-language.md`.
- No mutation of the snapshot or indexes.
- No external services; in-process only.
- All queries are deterministic.
- No LLM calls; the query engine is a pure function over the IR.

## Deliverables

- `query/dispatch` — query kind registry and dispatch
- `query/envelope` — common request/result types
- `query/q01-search`, `query/q02-explain`, ..., `query/q12-path` — per-query implementations
- `query/ranking` — ranking policies and tie-breaks
- `query/provenance` — provenance emission and re-derivation
- `query/cache` — query result cache
- `query/formats` — text/JSON/JSONL/DOT emitters
- `query/failures` — typed error implementations
- `query/extension` — plugin query kind registration
- `query/tests/*` — per-query and cross-cutting tests

## Verification

1. `gkc test query` — all query tests pass.
2. Contract test: each Q1–Q12 produces the documented output structure for a sample input.
3. Determinism test: same query twice → byte-identical results.
4. Provenance test: for a sample explain/impact/similar query, following the provenance edges re-derives the result.
5. Performance test: each query meets its target on `gold/large-repo` warm cache (within 2× for M2).
6. Failure-mode test: each of the eight failures is provoked and produces the correct typed error.
7. Format test: each query's output is valid in all applicable formats.

Report pass/fail per step. Any failure blocks M2.