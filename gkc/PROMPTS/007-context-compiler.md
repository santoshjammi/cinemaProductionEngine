# GKC-007 — Engineering Prompt

## Objective

Implement the **Context Compiler (C11)** — the flagship component. Build the full 7-stage pipeline from `DESIGN/007-context-compiler.md` § 3, with all built-in providers, the sufficiency test harness, and the caching layer.

## Inputs

- `DESIGN/007-context-compiler.md` (authoritative)
- `DESIGN/004-data-model.md` (for snapshot and indexes)
- `DESIGN/006-query-engine.md` (for search and traversal queries used in slice selection)
- `DESIGN/002-domain-model.md` (for Context Package, Task Descriptor, Token Budget)
- `DECISIONS/007-context-compiler-adr-candidates.md`
- `IMPLEMENTATION/golden-tasks.md` (the golden task set; create if missing)

## Scope

1. **Slice selector** (§ 4) — build the candidate set from a TaskDescriptor; produce typed slices per the six kinds in § 4.1.
2. **Semantic filter** (§ 5) — score slices by relevance × authority weight; threshold and drop.
3. **Dependency expansion** (§ 6) — close under hard dependencies using the dependency closure index; respect depth limits; emit `closure-truncated` info.
4. **Authority expansion** (§ 7) — walk authority chains; pull in higher-authority artifacts covering the same concept; detect conflicts; emit `context-conflict` info.
5. **Budget allocator** (§ 8) — implement the tiered allocation; per-category budgets; overflow policy `drop-lowest-authority` (default) plus configurable `truncate`/`summarize`/`fail`.
6. **Rendering / providers** (§ 9) — implement the four built-in providers (`markdown`, `anthropic-xml`, `openai-json`, `local-llm`); provider selection from model profile; fallback to `markdown` on provider failure.
7. **Package assembly** (§ 10) — order slices per § 10.1; attach metadata per § 10.2; emit single payload.
8. **Caching** (§ 11) — cache by identity tuple; invalidate per § 11.2; incremental re-build per § 11.3.
9. **Sufficiency test harness** (§ 13) — given a golden task and a reference agent, run the test and emit a `sufficiency-test-failed` diagnostic on failure.
10. **Failure modes** (§ 14) — all seven failures are typed errors or diagnostics, not exceptions.
11. **Extension points** (§ 15) — register plugin-provided providers, scorers, allocators.

## Out of Scope

- Real LLM calls (the sufficiency test uses a stub agent for M3; real LLMs added in M5).
- CLI argument parsing (covered in `DESIGN/009`).
- Snapshot loading (covered in C13).
- Real plugin loading (use stubs).

## Done Conditions

- The 7-stage pipeline runs end-to-end on a golden task against `gold/small-repo` and produces a non-empty package.
- **Determinism**: same `(task, snapshot, budget, provider)` ⇒ byte-identical package.
- **Dependency closure**: the package satisfies the closure invariant (§ 6.1) — verified by a property test that checks every artifact in the package has its hard deps included or reachable.
- **Authority preference**: under a tight budget, the package keeps higher-authority artifacts and drops lower-authority ones — verified by a test with a synthetic IR.
- **Budget compliance**: `total_tokens ≤ budget` always; verified by a property test.
- **Provider fallback**: a throwing provider triggers fallback to `markdown` with the `provider-fallback` marker.
- **Caching**: a second call with the same identity tuple returns in under 100 ms from cache.
- **Incremental**: a single-artifact change re-builds only affected slices.
- **Sufficiency**: the stub reference agent passes the sufficiency test on all golden tasks.
- **LLM independence**: the same task against the same snapshot with `markdown`, `local-llm`, and `openai-json` providers produces semantically equivalent packages (same artifacts, same order, different rendering).

## Constraints

- Implementation language: per `DECISIONS/0010-implementation-language.md`.
- No LLM calls in the compiler itself; LLMs only in the sufficiency test harness.
- No mutation of the IR.
- All stages are deterministic.
- Token estimation uses `chars / 4` by default (configurable per model profile).

## Deliverables

- `context/selector` — slice selection
- `context/filter` — semantic filtering
- `context/expand-dependency` — dependency expansion
- `context/expand-authority` — authority expansion and conflict detection
- `context/budget` — budget allocation
- `context/providers/markdown`, `context/providers/anthropic-xml`, `context/providers/openai-json`, `context/providers/local-llm`
- `context/assembly` — package assembly
- `context/cache` — context package cache
- `context/sufficiency` — sufficiency test harness
- `context/failures` — typed errors and diagnostics
- `context/extension` — plugin extension point registration
- `context/tests/*` — per-stage and end-to-end tests
- `IMPLEMENTATION/golden-tasks.md` — golden task set (created if missing)

## Verification

1. `gkc test context` — all context tests pass.
2. `gkc context --task="Explain artifact X" --snapshot=<id> --budget=4000` — produces a package.
3. Determinism: same command twice → byte-identical package.
4. Closure property test: every artifact in the package has its hard deps included or reachable.
5. Budget property test: `total_tokens ≤ budget` for 100 random (task, budget) pairs.
6. Provider fallback test: inject a failing provider; verify `markdown` fallback with marker.
7. Cache test: second call returns in < 100 ms.
8. Incremental test: change one artifact; verify only affected slices re-build.
9. Sufficiency test: stub agent passes all golden tasks.
10. LLM independence test: three providers produce semantically equivalent packages.

Report pass/fail per step. Any failure blocks M3.