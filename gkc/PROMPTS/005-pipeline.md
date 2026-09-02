# GKC-005 — Engineering Prompt

## Objective

Implement the **pipeline runner**: stage orchestration, cache integration, incremental compilation, parallel scheduling, diagnostic ranking, partial compilation. Stages themselves are stubs (from `DESIGN/003`); this prompt wires them together.

## Inputs

- `DESIGN/005-pipeline.md` (authoritative)
- `DESIGN/003-component-architecture.md` (for stage interfaces)
- `DESIGN/004-data-model.md` (for snapshot storage)
- `DECISIONS/005-pipeline-adr-candidates.md`

## Scope

1. **Stage DAG** — declare the 11 stages and their dependencies as a typed DAG. Verify downward-closed subsets for partial compilation.
2. **Stage runner** — execute stages in topological order; respect the parallelism rules in § 6; merge outputs in sorted order for determinism.
3. **Cache integration** — wire the stage cache from `DESIGN/004` § 4; hit/miss semantics per § 4.2; cache writes only on success.
4. **Incremental compile** — given a parent snapshot and a repository delta, compute the affected subgraph per § 3.4 and re-run only affected stages.
5. **Diagnostic buffer** — session-local; collects diagnostics from all stages; ranks them at the end per § 8.3.
6. **Failure policies** — implement per § 5: stage failure, plugin failure, hard invariant failure, storage failure.
7. **Partial compilation** — accept a `requested_stages` parameter; verify downward-closed; produce a partial snapshot with `unbuilt` markers.
8. **Observability hooks** — emit structured metrics per stage per § 10.
9. **Build session lifecycle** — implement the lifecycle in § 9.

## Out of Scope

- Real stage implementations (they remain stubs from `DESIGN/003`).
- Storage backend (use the in-memory stub from `DESIGN/004`).
- Plugin loading (use the stub from `DESIGN/003`).
- CLI integration (covered in `DESIGN/009`).

## Done Conditions

- The pipeline runs end-to-end on `gold/empty` and produces a (partial, mostly empty) snapshot.
- Determinism: two runs of the same repository state produce byte-identical snapshots.
- Incremental: a single-artifact change re-runs only the affected stages; the result is byte-identical to a full rebuild.
- Parallelism: with parallelism degree > 1, the output is still byte-identical to a serial run.
- Failure policies: each policy in § 5 is exercised by a test that injects the corresponding failure and verifies the documented behavior.
- Partial compilation: `requested_stages = [1, 2, 3, 4, 5]` produces a partial snapshot with stages 6–11 marked `unbuilt`.
- Diagnostic ranking: a synthetic diagnostic set is ranked correctly per the total order in § 8.3.
- Observability: metrics are emitted for each stage and queryable via a session API.

## Constraints

- Implementation language: per `DECISIONS/0010-implementation-language.md`.
- Parallelism uses stdlib concurrency; no external schedulers.
- All outputs are merged in a deterministic sorted order.
- No silent failures; every failure path emits a diagnostic.

## Deliverables

- `pipeline/dag` — stage DAG definition
- `pipeline/runner` — stage runner with parallelism
- `pipeline/cache` — cache integration
- `pipeline/incremental` — incremental compile
- `pipeline/diagnostics` — diagnostic buffer and ranking
- `pipeline/failures` — failure policy implementations
- `pipeline/partial` — partial compilation
- `pipeline/observability` — metrics emission
- `pipeline/session` — build session lifecycle
- `pipeline/tests/*` — per-feature tests

## Verification

1. `gkc test pipeline` — all pipeline tests pass.
2. `gkc compile gold/empty` — produces a snapshot.
3. `gkc compile gold/empty` (second run) — byte-identical snapshot.
4. `gkc compile gold/small-repo --inject-failure=stage-2` — diagnostic emitted, snapshot still written with `parse-failed` markers.
5. `gkc compile gold/small-repo --incremental-from=<snap>` — only affected stages run; result byte-identical to full rebuild.
6. `gkc compile gold/small-repo --parallelism=4` — byte-identical to `--parallelism=1`.
7. `gkc compile gold/small-repo --stages=1-5` — partial snapshot with `unbuilt` markers.
8. `gkc doctor` — shows metrics from the latest session.

Report pass/fail per step. Any failure blocks M1.