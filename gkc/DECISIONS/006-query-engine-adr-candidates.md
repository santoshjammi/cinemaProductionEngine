# ADR Candidates — GKC-006 Query Engine

> Decisions surfaced by `DESIGN/006-query-engine.md`.

---

## ADR-Candidate-0034 — Query result pagination

**Context.** § 3.1 has `limit` but no pagination. Should queries support pagination?

**Options.**
- **A. No pagination.** `limit` is the only bound; users refine their query for more.
- **B. Cursor-based pagination.** Results include a `next_cursor`; clients pass it back for the next page.
- **C. Offset-based pagination.** Clients pass `offset` and `limit`.

**Recommendation.** A for M2–M3; revisit B at M5 if real-world usage needs it. Pagination adds complexity (cursor stability under incremental updates) for limited current benefit. `limit` plus query refinement covers the use cases.

**Blocking impact.** Blocks M2 query implementation. Must be resolved before M2.

---

## ADR-Candidate-0035 — Streaming results

**Context.** Should the query engine stream large result sets?

**Options.**
- **A. No streaming.** Results are materialized; bounded by `limit`.
- **B. Streaming for graph queries only.** Graph emit can stream; others materialize.
- **C. Streaming for all.** Every query can stream.

**Recommendation.** B. Graph emit (Q7) is the only query that can produce very large output; streaming it is valuable. Other queries are bounded by `limit` and don't need streaming.

**Blocking impact.** Blocks M2 graph emit. Must be resolved before M2.

---

## ADR-Candidate-0036 — Cross-session query cache

**Context.** § 6 says the in-memory cache is per-session. Should it be shared across sessions?

**Options.**
- **A. Per-session only.** Each session starts with an empty in-memory cache; falls back to on-disk cache.
- **B. Shared via a daemon.** A `gkc serve` daemon holds a shared in-memory cache. Operational complexity.
- **C. On-disk only.** No in-memory cache; all queries hit disk.

**Recommendation.** A. Per-session in-memory + on-disk. The on-disk cache already provides cross-session sharing; a daemon (B) adds operational burden not justified for M2–M3.

**Blocking impact.** Blocks M2 query cache. Must be resolved before M2.

---

## ADR-Candidate-0037 — Plugin queries mutating snapshots

**Context.** § 9 says plugins add query kinds; can they mutate the snapshot?

**Options.**
- **A. No.** Queries are read-only. Period.
- **B. Yes, with declared capability.** Plugin queries can declare `snapshot-mutate` capability; the framework enforces.
- **C. Separate "action" extension point.** Mutations go through a separate extension point, not the query engine.

**Recommendation.** A. No. Queries are read-only; this preserves the snapshot immutability invariant (`DESIGN/002` § 3.16) and the staging invariant (`DESIGN/001` § 7.2). Mutations belong in a separate "action" or "transform" extension point, deferred to a later horizon.

**Blocking impact.** Blocks M2 query extension. Must be resolved before M2.

---

## ADR-Candidate-0038 — Programmatic query API

**Context.** § 9.2 of `DESIGN/003` says the CLI is the only public surface. Should the query engine expose a programmatic API?

**Options.**
- **A. CLI only.** All queries go through `gkc <subcommand>`.
- **B. Library API.** GKC ships as a library; programs import and call the query engine directly.
- **C. Both.** CLI is primary; library API is supported but not stable across versions.

**Recommendation.** A for M2–M3. CLI only. A library API (B) couples GKC to a language-specific ABI and breaks the "no public API in design" constraint. AIOS and IDEs consume GKC via the CLI's JSON output, which is stable. A library API can be revisited at M5.

**Blocking impact.** Blocks M2 query consumption model. Must be resolved before M2.