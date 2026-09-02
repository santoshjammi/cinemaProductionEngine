# GKC-011 — Testing Strategy

> How GKC is tested: unit, integration, repository tests, golden repositories, regression, performance, compiler correctness, and context correctness. Testing is not an afterthought — it's how the invariants in `DESIGN/001` are enforced.

---

## 1. Purpose

Define the **testing strategy** for GKC such that every invariant in `DESIGN/001` § 7, every success criterion in § 6, and every contract in `DESIGN/003` is verifiable automatically.

This document defines:

- the **test layers** (unit, integration, repository, golden, regression, performance),
- **golden repositories** (the canonical test fixtures),
- **compiler correctness** tests (determinism, incrementality, staging),
- **context correctness** tests (sufficiency, LLM independence),
- **performance budgets** and benchmarks,
- the **test harness** and **CI integration**.

---

## 2. Test Layers

| Layer | What it tests | Count target | Runtime target |
|---|---|---|---|
| Unit | Individual functions and types | 1000+ | < 30 s |
| Integration | Component-to-component contracts | 200+ | < 60 s |
| Repository | End-to-end compile of a real repository | 50+ | < 5 min |
| Golden | End-to-end compile of canonical fixtures | 10+ | < 10 min |
| Regression | Known-fixed bugs stay fixed | 100+ | < 60 s |
| Performance | Throughput and latency targets | 20+ | < 30 min |
| Compiler correctness | Determinism, incrementality, staging invariants | 30+ | < 10 min |
| Context correctness | Sufficiency, LLM independence | 50+ | < 30 min |

---

## 3. Unit Tests

### 3.1 Scope

- Domain types (`DESIGN/002`): construction, equality, lifecycle transitions, identity determinism.
- Identifier functions (`DESIGN/004` § 2): hash determinism, namespace correctness.
- Serializer/deserializer round-trips.
- Ranking and tie-break functions (`DESIGN/006` § 4).
- Budget allocation algorithms (`DESIGN/007` § 8).
- Classifier and parser logic (built-in kinds).

### 3.2 Property tests

- **Determinism property**: for any input, calling the function twice yields equal outputs.
- **Round-trip property**: for any value, `deserialize(serialize(v)) == v`.
- **Identity property**: for any value, reconstructing from identity fields yields an equal value.
- **Inverse property**: for any transformation, its inverse recovers the original.

### 3.3 Negative tests

- Every documented invariant violation is rejected by the relevant constructor.
- Every invalid input produces a typed error, not a panic.

---

## 4. Integration Tests

### 4.1 Scope

- Stage-to-stage contracts (`DESIGN/005`): each stage's output feeds the next stage's input correctly.
- Component-to-component contracts (`DESIGN/003`): C1 → C2 → ... → C11 dispatch.
- Plugin framework dispatch (`DESIGN/008`): plugins are loaded and called correctly.
- Storage read/write (`DESIGN/010`): snapshots and caches are written and read correctly.
- CLI to component routing (`DESIGN/009`): subcommands invoke the right components.

### 4.2 Boundary tests

- Plugin failure isolation (per `DESIGN/003` § C14).
- Storage failure isolation (per `DESIGN/010` § 12).
- Validator failure isolation (per `DESIGN/005` § 5.1).

---

## 5. Repository Tests

### 5.1 Scope

End-to-end compile of real repositories (small to medium). Verifies the whole pipeline produces a valid snapshot.

### 5.2 Test repositories

- `tests/repos/small-repo` — ~30 artifacts; clean.
- `tests/repos/medium-repo` — ~500 artifacts; clean.
- `tests/repos/drifted-repo` — ~30 artifacts; with constitutional violations.
- `tests/repos/plugin-heavy-repo` — ~30 artifacts; with multiple plugin kinds.

### 5.3 Assertions

- Compile succeeds (or fails with expected diagnostics).
- Snapshot is sealed and loadable.
- Registry entry count matches expected.
- Graphs are cycle-free (or report expected cycles).
- Validation report matches expected diagnostic set.

---

## 6. Golden Repositories

### 6.1 Purpose

Golden repositories are **canonical fixtures** with known-good outputs. They are snapshot-tested: the compiled snapshot is compared byte-for-byte to a recorded golden snapshot.

### 6.2 Golden repository set

| Name | Size | Purpose |
|---|---|---|
| `gold/empty` | 0 artifacts | Skeleton compile; determinism baseline |
| `gold/small-repo` | ~30 artifacts | Full pipeline; baseline for M1 |
| `gold/drifted-repo` | ~30 artifacts | Validation; constitutional violations |
| `gold/large-repo` | ~10k artifacts | Performance; throughput targets |
| `gold/plugin-heavy-repo` | ~30 artifacts | Plugin dispatch and isolation |
| `gold/cyclic-deps` | ~10 artifacts | Cycle detection |
| `gold/authority-conflict` | ~10 artifacts | Authority conflict resolution |
| `gold/multi-version` | ~20 artifacts | Schema version migration |
| `gold/incremental-chain` | ~30 artifacts × 5 versions | Incremental compile correctness |
| `gold/context-tasks` | ~30 artifacts + 10 tasks | Context sufficiency |

### 6.3 Golden snapshot recording

- `gkc test golden --record` compiles each golden repo and records the snapshot.
- Recorded snapshots are committed to the repo (in `gold/<name>/expected/`).
- `gkc test golden` (default) compares compiled snapshots to recorded.
- A mismatch fails the test and prints a diff.

### 6.4 Golden snapshot updates

- When a DESIGN doc change intentionally changes output, the golden snapshots are re-recorded.
- The re-recording is a separate commit, reviewed independently.
- The commit message references the DESIGN doc change and the ADR that justifies it.

---

## 7. Regression Tests

### 7.1 Purpose

Every bug fix gets a regression test that fails before the fix and passes after.

### 7.2 Organization

- `tests/regression/BUG-<id>.md` — describes the bug and the fix.
- `tests/regression/BUG-<id>.test` — the test itself.
- Linked from the ADR that recorded the bug.

### 7.3 CI

Regression tests run on every commit; they are never skipped.

---

## 8. Performance Tests

### 8.1 Targets (per `DESIGN/001` § 6)

| Target | Value | Test fixture |
|---|---|---|
| Cold compile throughput | `gold/large-repo` under 60 s | `gold/large-repo` |
| Warm incremental re-compile | `gold/large-repo` under 5 s | `gold/large-repo` |
| Warm query latency | Under 1 s (per query kind) | `gold/large-repo` |
| Warm context cache hit | Under 100 ms | `gold/large-repo` + golden task |

### 8.2 Benchmark methodology

- Run on a reference machine (per ADR-Candidate-0008: normalized to `gkc bench`).
- Warm cache = snapshot loaded in memory (per ADR-Candidate-0007).
- 10 runs; report median and p95.
- Performance tests run in CI on PRs affecting pipeline, query, or context.

### 8.3 Performance regression detection

- Each PR's benchmark results are compared to the main branch.
- A regression > 10% on any target fails the PR.
- Trends are tracked over time (not just per-PR).

---

## 9. Compiler Correctness Tests

### 9.1 Determinism (per `DESIGN/001` § 7.1)

- **Test**: compile `gold/small-repo` twice on two fresh checkouts; assert byte-identical snapshots.
- **Variant**: compile with parallelism=1 and parallelism=4; assert byte-identical.
- **Variant**: compile on two different machines (CI matrix); assert byte-identical.

### 9.2 Incrementality (per `DESIGN/001` § 7.3)

- **Test**: compile `gold/incremental-chain` version 1; apply delta to version 2; compile incrementally; assert byte-identical to a full compile of version 2.
- **Variant**: apply a single-artifact change; assert only affected stages re-ran (verify via metrics).
- **Variant**: apply a no-op change (same content); assert no stages re-ran.

### 9.3 Staging (per `DESIGN/001` § 7.2)

- **Test**: attempt to run stage 6 without stage 5; assert rejection.
- **Test**: verify the pipeline DAG is acyclic (topological sort).
- **Test**: verify no stage reads from a later stage's output (static analysis).

### 9.4 Cacheability (per `DESIGN/001` § 7.4)

- **Test**: compile with cache; clear cache; compile again; assert byte-identical.
- **Test**: cache hit returns byte-identical output to a fresh run.

### 9.5 Plugin isolation (per `DESIGN/001` § 7.6)

- **Test**: inject a failing plugin in stage 2; assert affected artifact marked `plugin-failed`; other artifacts proceed.
- **Test**: inject a plugin that exceeds declared capability; assert plugin terminated; other artifacts proceed.

### 9.6 GENESIS primacy (per `DESIGN/001` § 7.7)

- **Test**: compile `gold/drifted-repo`; assert constitutional violation diagnostics are emitted.
- **Test**: verify the validator does not silently override GENESIS.

### 9.7 Local-first (per `DESIGN/001` § 7.8)

- **Test**: compile `gold/small-repo` with network disabled (sandboxed); assert successful exit.
- **Test**: attempt to load a plugin requiring `network-external` with network disabled; assert rejection.

---

## 10. Context Correctness Tests

### 10.1 Sufficiency (per `DESIGN/007` § 13)

- **Test**: for each golden task, build the context package; hand to the stub reference agent; assert it answers correctly.
- **Test**: for each golden task, run with the local LLM profile; assert the agent answers correctly.
- **Test**: for each golden task, run with the frontier LLM profile; assert the agent answers correctly.
- **Failure**: if any agent fails, emit `sufficiency-test-failed` with the missing slice.

### 10.2 LLM independence (per `DESIGN/007` § 12)

- **Test**: for a golden task, build packages with `markdown`, `local-llm`, `openai-json`, `anthropic-xml` providers; assert semantically equivalent (same artifacts, same order).

### 10.3 Closure (per `DESIGN/007` § 6.1)

- **Property test**: for 100 random (task, snapshot) pairs, every artifact in the package has its hard dependencies included or transitively reachable.

### 10.4 Budget compliance (per `DESIGN/007` § 8.1)

- **Property test**: for 100 random (task, snapshot, budget) pairs, `total_tokens ≤ budget`.

### 10.5 Authority preference (per `DESIGN/007` § 7.1)

- **Test**: construct a synthetic IR with two artifacts covering the same concept (one constitutional, one guidance); build a package with a tight budget; assert the constitutional artifact is included and the guidance one is dropped.

---

## 11. Test Harness

### 11.1 `gkc test` subcommand

- `gkc test unit` — run unit tests.
- `gkc test integration` — run integration tests.
- `gkc test repo` — run repository tests.
- `gkc test golden [--record]` — run (or record) golden tests.
- `gkc test regression` — run regression tests.
- `gkc test perf` — run performance tests.
- `gkc test correctness` — run compiler correctness tests.
- `gkc test context` — run context correctness tests.
- `gkc test all` — run everything.

### 11.2 Output

- Text by default; JSON via `--format=json`.
- Exit 0 if all pass; exit 1 if any fail.
- Failed tests are listed with details.

### 11.3 Parallelism

- Unit and integration tests run in parallel (bounded by CPU).
- Golden and repository tests serialize on the workspace (per `DESIGN/010` § 2.2).
- Performance tests serialize (they measure timing).

---

## 12. CI Integration

### 12.1 Per-commit CI

- Unit + integration + regression + compiler correctness.
- Target: under 10 minutes total.

### 12.2 Per-PR CI

- All of the above + repository tests + golden tests.
- Performance tests run on PRs touching pipeline, query, or context.
- Target: under 30 minutes total.

### 12.3 Nightly CI

- All of the above + performance tests + context correctness (with real LLM calls).
- Target: under 2 hours.

### 12.4 Release CI

- All of the above + golden re-record (verify no unexpected changes).
- Cross-platform matrix (Linux, macOS, Windows).
- Target: under 4 hours.

---

## 13. Test Fixtures Management

### 13.1 Golden repos

- Stored in `gold/` at the repo root.
- Each golden repo is self-contained (no external dependencies).
- Changes to golden repos require ADR justification.

### 13.2 Golden tasks

- Stored in `IMPLEMENTATION/golden-tasks.md`.
- Each task has: description, expected target artifacts, expected concepts, expected sufficiency answers.
- Tasks are versioned with the design.

### 13.3 Reference agents

- **Stub agent**: deterministic; pattern-matches against the context package. Used in per-commit CI.
- **Local LLM**: specified model (per ADR-Candidate-0010); runs in nightly CI.
- **Frontier LLM**: specified model; runs in nightly CI (requires API key via env var).

---

## 14. Coverage

### 14.1 Line coverage

- Target: 90% for core; 80% for plugins.
- Measured per-module; reported in CI.

### 14.2 Invariant coverage

- Every invariant in `DESIGN/001` § 7 has at least one test in § 9.
- Every success criterion in `DESIGN/001` § 6 has at least one test in § 8 or § 10.
- Every contract in `DESIGN/003` has at least one integration test.

### 14.3 Mutation testing

- Run quarterly on core modules.
- Target: 80% of mutants killed.

---

## 15. Open Questions for ADR

Surfaced in `DECISIONS/011-testing-adr-candidates.md`:

1. Should fuzzing be added to the test strategy?
2. Should the test harness support snapshot testing for CLI output?
3. Should coverage thresholds be enforced (CI fails below threshold)?
4. Should performance tests run on every PR or only on labeled PRs?
5. Should the reference LLM agents be pinned to specific model versions?