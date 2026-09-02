# GKC-012 — Engineering Prompt

## Objective

Stand up the **reference implementation repository**: package structure, build system, CI scaffolding, milestone tracking, and the M0 skeleton deliverables. This prompt bootstraps the engineering effort; subsequent prompts (per `PROMPTS/001`–`011`) fill in the implementation.

## Inputs

- `DESIGN/012-reference-implementation.md` (authoritative)
- `DESIGN/003-component-architecture.md` (for package structure)
- `ROADMAP.md` (for milestone done-conditions)
- `DECISIONS/012-reference-implementation-adr-candidates.md`
- `DECISIONS/0010-implementation-language.md` (must be ratified first)

## Scope

1. **Repository structure** (§ 4) — create the directory layout; initialize the git repo; add `.gitignore`, `README.md`, `LICENSE`, `CONTRIBUTING.md`, build script.
2. **Package skeleton** (§ 3) — create empty packages matching the structure; add package-level documentation files; configure inter-package dependencies per § 3.1.
3. **Build system** — set up the build for the chosen language; configure determinism (pinned dependencies, reproducible builds).
4. **CI scaffolding** — set up per-commit, per-PR, nightly, and release CI configurations per `DESIGN/011` § 12.
5. **M0 skeleton deliverables** (§ 5.1) — implement the M0 items per `PROMPTS/001` and `PROMPTS/003`:
   - Stage interface and runner skeleton.
   - Diagnostic type (complete).
   - Determinism harness (working).
   - Cache key function (stub).
   - Plugin failure boundary (skeleton).
   - GENESIS primacy hook (stub).
   - Local-first test (working).
   - `gold/empty` fixture (complete).
   - CLI shell for `scan`, `doctor`, `stats` (skeleton).
6. **Milestone tracking** (§ 6) — create `IMPLEMENTATION/m0-status.md` from the template; populate initial done-conditions.
7. **Self-compilation setup** (§ 4.1) — configure `.gkc/` as a gitignored workspace; verify `gkc scan .` works on the implementation repo itself.

## Out of Scope

- M1+ deliverables (those have their own prompts).
- Real component implementations (skeletons only at M0).
- Real plugin implementations (stubs only).
- Distribution packaging (post-M5 per ADR-Candidate-0011).

## Done Conditions

- The repository structure matches § 4.
- All packages from § 3 exist with documentation files.
- The build system produces a `gkc` binary (or equivalent) with `--version` working.
- CI runs on every commit and exercises the test suite.
- All M0 deliverables in § 5.1 are implemented and pass their tests.
- `gkc scan gold/empty` produces a (skeleton) snapshot.
- `gkc doctor` reports a healthy workspace.
- `IMPLEMENTATION/m0-status.md` is up to date.
- Self-compilation: `gkc scan .` on the implementation repo produces a snapshot.

## Constraints

- Implementation language: per `DECISIONS/0010-implementation-language.md`.
- No external dependencies beyond stdlib and the chosen build tool.
- Reproducible builds (pinned dependencies, no network at build time).
- All M0 tests pass in CI.

## Deliverables

- Repository structure (per § 4)
- Package skeleton (per § 3)
- Build system configuration
- CI configurations (per-commit, per-PR, nightly, release)
- M0 skeleton deliverables (per § 5.1)
- `IMPLEMENTATION/m0-status.md`
- `gold/empty/` fixture
- Self-compilation workspace

## Verification

1. `gkc --version` prints a version string.
2. `gkc init /tmp/test-ws` creates a valid workspace.
3. `gkc scan gold/empty --workspace=/tmp/test-ws` produces a snapshot id.
4. `gkc doctor --workspace=/tmp/test-ws` reports healthy.
5. `gkc test all` runs and passes (skeleton tests).
6. CI runs on a sample PR; all checks pass.
7. `gkc scan .` (self-compilation) produces a snapshot.
8. `IMPLEMENTATION/m0-status.md` shows all done-conditions checked.

Report pass/fail per step. Any failure blocks M0 exit and milestone release.