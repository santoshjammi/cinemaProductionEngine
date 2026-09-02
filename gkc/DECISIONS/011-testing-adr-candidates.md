# ADR Candidates — GKC-011 Testing

> Decisions surfaced by `DESIGN/011-testing.md`.

---

## ADR-Candidate-0059 — Fuzzing

**Context.** § 14 does not mention fuzzing. Should it be part of the strategy?

**Options.**
- **A. No fuzzing.** Tests are hand-written; coverage is sufficient.
- **B. Fuzzing for parsers and deserializers.** Target the parts that accept untrusted input (file content, plugin manifests, snapshot blobs).
- **C. Fuzzing across the whole pipeline.** Broad fuzzing of repository inputs.

**Recommendation.** B. Fuzzing for parsers and deserializers. These are the surfaces most likely to have handling bugs on malformed input. Broad pipeline fuzzing (C) is expensive for marginal benefit at M0–M5.

**Blocking impact.** None for M0–M5; add as a post-M5 enhancement.

---

## ADR-Candidate-0060 — Snapshot testing for CLI output

**Context.** Should the test harness support snapshot testing for CLI text output (compare stdout to a recorded golden output)?

**Options.**
- **A. No.** CLI output stability is tested via determinism tests (same input ⇒ same output); no separate snapshot testing.
- **B. Yes, for text output.** Golden text outputs are recorded and compared.
- **C. Yes, for both text and JSON.** Full snapshot testing of CLI output.

**Recommendation.** B. Yes, for text output. JSON output is already schema-validated and deterministic; text output benefits from snapshot testing because it's the human-facing surface and small changes are easy to miss.

**Blocking impact.** Blocks M2 CLI testing. Must be resolved before M2.

---

## ADR-Candidate-0061 — Coverage enforcement

**Context.** § 14.1 sets coverage targets. Should CI enforce them?

**Options.**
- **A. No enforcement.** Coverage is reported; humans review trends.
- **B. Hard fail below threshold.** CI fails if coverage drops below 90%/80%.
- **C. Soft fail with warning.** CI warns but does not fail.

**Recommendation.** C. Soft fail with warning for M0–M5. Hard fails encourage gaming (writing tests that increase coverage without verifying behavior). Revisit at post-M5 if coverage discipline is established.

**Blocking impact.** Blocks M0 CI integration. Must be resolved before M0.

---

## ADR-Candidate-0062 — Performance test scope per PR

**Context.** § 12.2 says performance tests run on PRs touching pipeline, query, or context. How is "touching" determined?

**Options.**
- **A. File path matching.** PRs that modify files under `pipeline/`, `query/`, `context/` trigger perf tests.
- **B. Label-based.** PRs labeled `perf-impact` trigger perf tests.
- **C. Always run; report-only on non-impact PRs.** Perf tests run on every PR; failures block only on `perf-impact` PRs.

**Recommendation.** A. File path matching. Objective, automatic, and matches the actual impact surface. Label-based (B) relies on humans; always-run (C) is expensive.

**Blocking impact.** Blocks M2 CI integration. Must be resolved before M2.

---

## ADR-Candidate-0063 — Reference LLM model pinning

**Context.** § 13.3 says nightly CI runs local and frontier LLM agents. Should the models be pinned?

**Options.**
- **A. Pinned to specific versions.** e.g., `claude-haiku-3.5-20241022`; reproducible; may go stale.
- **B. Pinned to model families.** e.g., `claude-haiku-latest`; stays current; non-reproducible.
- **C. Pinned with manual override.** Default to a pinned version; override via env var.

**Recommendation.** C. Pinned with manual override. Pinning ensures reproducibility (a core invariant); the override lets us test newer models without changing the test suite.

**Blocking impact.** Blocks M3 context correctness tests. Must be resolved before M3.