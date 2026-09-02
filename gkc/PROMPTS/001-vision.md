# GKC-001 — Engineering Prompt

> Use this prompt to drive an engineering agent to implement the **vision layer** of GKC. This is not implementation code; it is the engineering scaffolding that makes the vision testable.

## Objective

Establish the engineering substrate that enforces the vision invariants from `DESIGN/001-vision.md` § 7. Before any subsystem is implemented, the compiler must be structurally incapable of violating invariants 7.1–7.8.

## Inputs

- `DESIGN/001-vision.md` (authoritative)
- `ARCHITECTURE.md` (system map)
- `ROADMAP.md` M0 scope

## Scope

Implement, at the skeleton level (M0):

1. **Stage interface.** A typed stage abstraction with: stage id, input contract, output contract, run function, diagnostic sink. No stage reads from later stages.
2. **Diagnostic type.** Carries: artifact id, stage id, severity, invariant reference, evidence, suggested resolution. Immutable once emitted.
3. **Determinism harness.** A test harness that compiles a golden repository twice on two fresh checkouts and asserts byte-identical snapshots.
4. **Cache identity.** A function `(stage id, input content hash, configuration hash, plugin set hash) → cache key`. Not yet backed by storage; the function must be deterministic and pure.
5. **Plugin failure boundary.** A stage-runner that catches plugin exceptions, marks the affected artifact with a `plugin-failed` marker, and continues. Verify with a fault-injecting test plugin.
6. **GENESIS primacy check (stub).** A validation hook that, given a registry entry and a GENESIS document reference, emits a `constitutional-violation` diagnostic if the entry conflicts. The conflict-detection function is a stub for M0; the hook is real.
7. **Local-first verification.** A test that compiles a golden repository with the network disabled (sandboxed environment) and asserts successful exit.

## Out of Scope

- Real scanner, parser, registry, graphs, ontology, context. Those have their own prompts.
- Storage backend. Use an in-memory stub.
- CLI beyond `gkc doctor` and `gkc stats` stubs.
- Plugin loading mechanism. Use a hard-coded test plugin for the failure-boundary test.

## Done Conditions

- All seven items above are implemented and have at least one passing test.
- The determinism harness passes on `gold/empty`.
- The fault-injection test demonstrates plugin isolation: a failing plugin produces a diagnostic, not a crash, and the snapshot still writes.
- The local-first test passes with no network access.
- No design doc invariants from `DESIGN/001` § 7 are violated by the skeleton.

## Constraints

- Implementation language: per `DECISIONS/0010-implementation-language.md` (resolve before starting).
- No public API in the skeleton; only internal interfaces.
- All emitted diagnostics conform to the type in § 2 of this prompt.

## Deliverables

- `skeleton/stage` — stage interface and runner
- `skeleton/diagnostic` — diagnostic type and severity enum
- `skeleton/cache` — cache key function
- `skeleton/determinism` — determinism harness
- `skeleton/plugin-failure` — failure-boundary test
- `skeleton/genesis-primacy` — validation hook stub
- `skeleton/local-first` — network-disabled test
- `gold/empty/` — empty golden repository
- Test report: "M0 vision scaffolding passes invariant tests"

## Verification

Run, in order:

1. `gkc test skeleton` — all skeleton tests pass
2. `gkc compile gold/empty` — produces a snapshot
3. `gkc compile gold/empty` (second run, fresh checkout) — byte-identical snapshot
4. `gkc compile gold/empty --network=disabled` — successful exit
5. `gkc compile gold/empty --inject-plugin-failure` — diagnostic emitted, snapshot still written

Report pass/fail per step. Any failure blocks M0 exit.