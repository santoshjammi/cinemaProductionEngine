# ADR Candidates — GKC-004 Data Model

> Decisions surfaced by `DESIGN/004-data-model.md`.

---

## ADR-Candidate-0024 — Registry identifier index: hash table vs. trie

**Context.** § 6 does not specify the data structure for the identifier index.

**Options.**
- **A. Hash table.** O(1) exact lookup; no prefix queries.
- **B. Trie.** O(k) lookup (k = key length); supports prefix queries.
- **C. Both.** Hash table for exact; trie for prefix.

**Recommendation.** A. Hash table. Prefix queries are not in the M1–M3 scope. If prefix queries become needed, a plugin can add a trie index (per `DESIGN/008` index extension point).

**Blocking impact.** Blocks M1 registry implementation. Must be resolved before M1.

---

## ADR-Candidate-0025 — Snapshot partial loading

**Context.** § 5.2 implies a snapshot is loaded as a whole. Should partial loading (e.g., load only the registry) be supported?

**Options.**
- **A. No.** Always load the full snapshot. Simplest; matches atomicity.
- **B. Yes, per file.** Load the manifest first; load other files on demand.
- **C. Yes, per index.** Load only the indexes a query needs.

**Recommendation.** B. Per file. The manifest is always loaded; other files load lazily. Matches S5 (warm-cache latency) by avoiding unnecessary loading of large graph files when only the registry is needed.

**Blocking impact.** Blocks `DESIGN/010` storage reader. Must be resolved before M2.

---

## ADR-Candidate-0026 — Default search index: BM25 vs. vector

**Context.** § 6.1 says the search index is "implementation-defined; plugin-extensible". What is the default?

**Options.**
- **A. BM25 inverted index.** Token-based; deterministic; no model dependency; fast.
- **B. Vector index.** Semantic similarity; non-deterministic across model versions; requires embedding model.
- **C. Both, with BM25 default.** BM25 ships in core; vector index is a plugin.

**Recommendation.** C. BM25 default, vector optional. Determinism (per `DESIGN/001` § 7.1) requires a deterministic default; vector search is non-deterministic across model versions and violates the invariant unless the embedding model is pinned. A plugin can add vector search with a pinned model.

**Blocking impact.** Blocks M2 search index. Must be resolved before M2.

---

## ADR-Candidate-0027 — Dependency closure depth configuration

**Context.** § 6.5 says bounded depth is configurable. Per workspace or per query?

**Options.**
- **A. Per workspace.** One depth for all queries. Predictable.
- **B. Per query.** Each query specifies its depth. Flexible.
- **C. Per workspace default, per query override.** Hybrid.

**Recommendation.** C. Hybrid. Default per workspace (e.g., depth 3); override per query for deep impact analysis. Matches both common-case performance and deep-query flexibility.

**Blocking impact.** Blocks M3 context expansion. Must be resolved before M3.

---

## ADR-Candidate-0028 — Compression granularity

**Context.** § 9.1 says compression is per-file. Should it be per-snapshot-blob (one big compressed file) instead?

**Options.**
- **A. Per file (current).** Allows partial loading (per ADR-Candidate-0025). Slightly lower ratio.
- **B. Per snapshot blob.** Better ratio; defeats partial loading.
- **C. Per file with shared dictionary.** Compression dictionary shared across files in a snapshot; better ratio; keeps partial loading.

**Recommendation.** A. Per file. Partial loading (ADR-Candidate-0025) is more valuable than the marginal compression gain. Shared-dictionary (C) is a possible later optimization.

**Blocking impact.** Blocks M0 storage writer. Must be resolved before M0.