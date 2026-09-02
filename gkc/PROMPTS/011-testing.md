# GKC-011 — Engineering Prompt

## Objective

Implement the **test harness and fixtures** for GKC: the `gkc test` subcommand, golden repository fixtures, golden task definitions, compiler correctness test suites, context correctness test suites, performance benchmarks, and CI integration scripts.

## Inputs

- `DESIGN/011-testing.md` (authoritative)
- `DESIGN/001-vision.md` (for invariants and success criteria)
- `DESIGN/007-context-compiler.md` (for sufficiency test methodology)
- `DECISIONS/011-testing-adr-candidates.md`

## Scope

1. **`gkc test` subcommand** (§ 11) — implement the 9 test subcommands; output text/JSON; parallelism rules.
2. **Golden repositories** (§ 6.2) — create the 10 golden repos; record initial golden snapshots.
3. **Golden task set** (§ 13.2) — define the initial 10 golden tasks in `IMPLEMENTATION/golden-tasks.md`.
4. **Compiler correctness suites** (§ 9) — implement all 7 categories (determinism, incrementality, staging, cacheability, plugin isolation, GENESIS primacy, local-first).
5. **Context correctness suites** (§ 10) — implement sufficiency, LLM independence, closure, budget compliance, authority preference.
6. **Performance benchmarks** (§ 8) — implement `gkc bench`; measure the 4 targets.
7. **Reference agents** (§ 13.3) — implement the stub reference agent; define interfaces for local and frontier LLM agents.
8. **CI integration scripts** — per-commit, per-PR, nightly, release configurations.
9. **Coverage measurement** — line coverage per module; invariant coverage mapping.

## Out of Scope

- Real LLM-based tests (run in nightly CI only; not in per-commit).
- Mutation testing (quarterly; not in scope for M0–M5).
- Fuzzing (per ADR-Candidate-0059 if open).

## Done Conditions

- `gkc test all` runs all 8 test categories and reports pass/fail per test.
- All 10 golden repos compile and produce byte-stable snapshots.
- All 7 compiler correctness categories have at least 3 passing tests.
- All 5 context correctness categories have at least 5 passing tests.
- `gkc bench` measures all 4 performance targets and reports them.
- The stub reference agent passes the sufficiency test for all 10 golden tasks.
- CI integration scripts work for per-commit, per-PR, and nightly configurations.
- Coverage is measured and reported.

## Constraints

- Implementation language: per `DECISIONS/0010-implementation-language.md`.
- Use the stdlib test framework; no external test libraries (keeps dependencies small).
- Golden snapshots are committed to the repo; not generated in CI.
- Performance tests serialize on the workspace.

## Deliverables

- `testing/harness` — `gkc test` subcommand
- `testing/golden/` — golden repos and recorded snapshots
- `testing/golden-tasks.md` — golden task definitions (in `IMPLEMENTATION/`)
- `testing/correctness/{determinism,incremental,staging,cacheability,plugin-isolation,genesis-primacy,local-first}`
- `testing/context/{sufficiency,llm-independence,closure,budget,authority-preference}`
- `testing/perf/` — performance benchmarks
- `testing/agents/stub` — stub reference agent
- `testing/agents/contract` — interface for LLM agents
- `testing/ci/` — CI integration scripts
- `testing/coverage/` — coverage measurement

## Verification

1. `gkc test all` runs and passes (with stubs for unimplemented components).
2. `gkc test golden` compares compiled snapshots to recorded; passes on a clean tree.
3. `gkc test correctness` runs all 7 categories; passes.
4. `gkc test context` runs all 5 categories; stub agent passes sufficiency.
5. `gkc bench` runs and reports the 4 targets.
6. CI script `testing/ci/per-commit.sh` runs in under 10 minutes.
7. Coverage report is generated.

Report pass/fail per step. Any failure blocks M1.