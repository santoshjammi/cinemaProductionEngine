# GKC-012 — Reference Implementation

> The engineering roadmap from this design package to a working compiler. Package structure, repository structure, milestones, deliverables, risks, migration, and future evolution.

---

## 1. Purpose

This document is the **engineering-grade companion** to `ROADMAP.md`. Where the roadmap names milestones and done-conditions, this document specifies:

- the **package structure** of the implementation,
- the **repository structure** for the source code,
- the **per-milestone deliverables** with file-level granularity,
- the **risks** and mitigations,
- the **migration** path for users and workspaces as GKC evolves,
- the **future evolution** of the implementation beyond M5.

This document is the bridge from design to engineering. After it, an engineering team or AI coding agent can start building.

---

## 2. Implementation Language

The design is language-independent. The reference implementation language is chosen for M0 and recorded in `DECISIONS/0010-implementation-language.md`.

Selection criteria (in order):

1. **Deterministic serialization** — stdlib or mature library for stable binary serialization.
2. **Concurrency** — stdlib support for parallel execution with deterministic merging.
3. **Plugin ABI** — a stable way to load plugins (FFI, dynamic loading, or language-native).
4. **Distribution** — single-binary distribution preferred.
5. **Test ergonomics** — stdlib testing framework with property-test support.
6. **Team familiarity** — the implementing team's fluency.

Candidates (no preference expressed here; the ADR decides):

- **Rust** — strong on 1, 2, 4; plugin ABI via WASM or dynamic crates.
- **Go** — strong on 2, 4, 6; plugin ABI via Go plugins (Linux only) or RPC.
- **TypeScript/Node** — strong on 6; weaker on 1, 4; plugin ABI via npm packages.
- **Python** — strong on 6; weaker on 1, 4; plugin ABI via importlib.

The ADR must be ratified before M0 starts.

---

## 3. Package Structure

The implementation is organized into packages matching the components in `DESIGN/003`:

```
gkc/                              (implementation root)
├── core/                         (compiler core; no external deps)
│   ├── domain/                   (DESIGN/002 domain types)
│   ├── identifiers/              (DESIGN/004 § 2 id formats)
│   ├── serde/                    (DESIGN/004 § 3 serialization)
│   ├── schema-registry/          (DESIGN/004 § 3.3)
│   ├── diagnostics/              (DESIGN/002 § 3.20)
│   └── lifecycle/                (DESIGN/002 § 5 state machines)
│
├── components/                   (DESIGN/003 components)
│   ├── scanner/                  (C1)
│   ├── parser/                   (C2)
│   ├── normalizer/               (C3)
│   ├── resolver/                 (C4)
│   ├── registry/                 (C5)
│   ├── authority-builder/        (C6)
│   ├── dependency-builder/       (C7)
│   ├── ontology-compiler/        (C8)
│   ├── validator/                (C9)
│   ├── indexer/                  (C10)
│   ├── context-compiler/         (C11)
│   ├── query-engine/             (C12)
│   ├── storage/                  (C13)
│   ├── plugin-framework/         (C14)
│   └── cli/                      (C15)
│
├── pipeline/                     (DESIGN/005 pipeline runner)
│   ├── dag/
│   ├── runner/
│   ├── cache/
│   ├── incremental/
│   └── session/
│
├── plugins/                      (built-in plugins; per DESIGN/008 § 9)
│   ├── classifiers/              (built-in artifact classifiers)
│   ├── parsers/                  (built-in parsers per kind)
│   ├── providers/                (built-in context providers)
│   ├── queries/                  (built-in query kinds)
│   └── invariants/               (built-in GENESIS invariants)
│
├── testing/                      (DESIGN/011 testing harness)
│   ├── harness/
│   ├── golden/
│   ├── correctness/
│   ├── context/
│   ├── perf/
│   ├── agents/
│   └── ci/
│
├── gold/                         (golden repositories; per DESIGN/011 § 6.2)
│   ├── empty/
│   ├── small-repo/
│   ├── drifted-repo/
│   ├── large-repo/
│   ├── plugin-heavy-repo/
│   ├── cyclic-deps/
│   ├── authority-conflict/
│   ├── multi-version/
│   ├── incremental-chain/
│   └── context-tasks/
│
└── docs/                         (engineering documentation)
    ├── architecture/             (auto-generated architecture docs)
    ├── adr/                      (ratified ADRs; mirrored from DECISIONS/)
    └── changelog/                (per-milestone changelogs)
```

### 3.1 Dependency rules

- `core/` depends on nothing external (only stdlib).
- `components/` depend on `core/` and possibly each other (per `DESIGN/003` § 4.1).
- `pipeline/` depends on `core/` and `components/`.
- `plugins/` depends on `core/` (for contracts) but not on `components/` (plugins are dispatched via the framework).
- `testing/` depends on everything.
- `gold/` depends on nothing (test fixtures).

### 3.2 Public surface

The only public API is the CLI (per `DESIGN/009`). No package other than `cli/` exposes a public interface. All other packages are internal.

---

## 4. Repository Structure

The implementation lives in a single git repository:

```
gkc/                              (git root)
├── .gkc/                         (workspace for self-compilation; gitignored)
├── core/
├── components/
├── pipeline/
├── plugins/
├── testing/
├── gold/
├── docs/
├── DESIGN/                       (this design package; tracked)
├── DECISIONS/                    (ADRs; tracked)
├── REVIEWS/                      (design reviews; tracked)
├── PROMPTS/                      (engineering prompts; tracked)
├── IMPLEMENTATION/               (implementation tracking; tracked)
├── README.md
├── LICENSE
├── CONTRIBUTING.md
└── Makefile or build script
```

### 4.1 Self-compilation

GKC compiles its own repository. The `.gkc/` workspace is gitignored; `gkc scan .` produces a snapshot of GKC's own source. This is both a dogfooding test and a useful tool for GKC development.

### 4.2 Branching

- `main` — always shippable; protected.
- `feature/<name>` — feature branches; merged via PR.
- `milestone/m<N>` — milestone branches; tagged at milestone exit.

### 4.3 Tags

Each milestone exit is tagged: `v0.1.0-m0`, `v0.2.0-m1`, etc. Final 1.0 is tagged at M5 exit.

---

## 5. Per-Milestone Deliverables

### 5.1 M0 — Skeleton

| Deliverable | Package | Status |
|---|---|---|
| Stage interface and runner | `pipeline/dag`, `pipeline/runner` | Skeleton |
| Diagnostic type | `core/diagnostics` | Complete |
| Determinism harness | `testing/correctness/determinism` | Working |
| Cache key function | `pipeline/cache` | Stub |
| Plugin failure boundary | `components/plugin-framework` | Skeleton |
| GENESIS primacy hook | `components/validator` | Stub |
| Local-first test | `testing/correctness/local-first` | Working |
| `gold/empty` fixture | `gold/empty/` | Complete |
| CLI shell (`scan`, `doctor`, `stats`) | `components/cli` | Skeleton |

### 5.2 M1 — Scanner & Registry

| Deliverable | Package |
|---|---|
| Scanner with 4 built-in classifiers | `components/scanner`, `plugins/classifiers` |
| Parser for `document`, `schema`, `manifest`, `runtime` | `components/parser`, `plugins/parsers` |
| Normalizer with authority inference | `components/normalizer` |
| Resolver with path and identifier strategies | `components/resolver` |
| Registry with content-addressed entries | `components/registry` |
| `gkc registry list/show/find/history` | `components/cli` |
| `gold/small-repo` fixture | `gold/small-repo/` |
| Incremental re-scan | `pipeline/incremental` |

### 5.3 M2 — Graphs & Ontology

| Deliverable | Package |
|---|---|
| Authority builder | `components/authority-builder` |
| Dependency builder with cycle detection | `components/dependency-builder` |
| Ontology compiler | `components/ontology-compiler` |
| Indexer with search, traversal, concept, authority-ranking, dependency-closure indexes | `components/indexer` |
| Query engine: search, explain, find, stats, diagnostics, graph emit | `components/query-engine` |
| `gkc graph`, `gkc search`, `gkc explain` | `components/cli` |

### 5.4 M3 — Context Compiler

| Deliverable | Package |
|---|---|
| Context compiler 7-stage pipeline | `components/context-compiler` |
| 4 built-in providers | `plugins/providers` |
| Context cache | `components/storage/caches/context` |
| `gkc context` | `components/cli` |
| Sufficiency test harness (stub agent) | `testing/context/sufficiency`, `testing/agents/stub` |
| `gold/context-tasks` fixture | `gold/context-tasks/` |

### 5.5 M4 — Validation & Diagnostics

| Deliverable | Package |
|---|---|
| Validator with ranked diagnostics | `components/validator` |
| Codified GENESIS invariants | `plugins/invariants` |
| `gkc validate` | `components/cli` |
| `gold/drifted-repo` fixture | `gold/drifted-repo/` |
| Invariant codification tracker | `IMPLEMENTATION/invariants.md` |

### 5.6 M5 — Plugin & AIOS Integration

| Deliverable | Package |
|---|---|
| Plugin framework with runtime capability enforcement (level B) | `components/plugin-framework` |
| Plugin CLI (`install`, `uninstall`, `list`, `info`, `hash`) | `components/cli` |
| AIOS integration contract test | `testing/integration/aios-boot` |
| `gold/plugin-heavy-repo` fixture | `gold/plugin-heavy-repo/` |
| End-to-end test: fresh checkout → scan → context → AIOS agent | `testing/integration/e2e` |

---

## 6. Implementation Tracking

### 6.1 `IMPLEMENTATION/` directory

Contains per-milestone tracking artifacts, updated as engineering proceeds:

- `IMPLEMENTATION/m0-status.md` — M0 progress, blockers, decisions.
- `IMPLEMENTATION/m1-status.md` — M1 progress.
- ... etc.
- `IMPLEMENTATION/invariants.md` — GENESIS invariant codification tracker (per `DESIGN/005`).
- `IMPLEMENTATION/golden-tasks.md` — golden task set (per `DESIGN/011` § 13.2).
- `IMPLEMENTATION/changelog.md` — engineering changelog.

### 6.2 Per-milestone status template

```markdown
# M<N> Status

## Done conditions
- [ ] condition 1
- [ ] condition 2

## In progress
- ...

## Blockers
- ...

## Open ADRs
- ADR-XXXX: ...

## Next actions
- ...
```

---

## 7. Risks

### 7.1 Engineering risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Token-budget allocation is too aggressive; packages are insufficient | High | High | Sufficiency test catches early; golden tasks cover diverse cases |
| Incremental compile produces different output than full compile | Medium | Critical | Compiler correctness test (§ 9.2) on every commit |
| Plugin ABI is unstable across versions | Medium | High | Pin ABI to major version; deprecation policy |
| GENESIS invariant codification is harder than expected | High | Medium | Defer some invariants to post-M4; track in `IMPLEMENTATION/invariants.md` |
| Performance targets are missed | Medium | Medium | Performance tests from M1; optimize early |
| Local LLM context packages are too small to be useful | Medium | High | Sufficiency test includes local LLM profile; adjust budget policy |

### 7.2 Organizational risks

| Risk | Mitigation |
|---|---|
| Scope creep (adding features beyond the design) | Strict milestone done-conditions; ADRs for additions |
| Design drift (implementation diverges from design) | Reviews at each milestone exit; ADRs for deviations |
| Plugin ecosystem fails to materialize | GKC is useful without plugins (built-ins cover core); plugins are additive |

### 7.3 External risks

| Risk | Mitigation |
|---|---|
| GENESIS architecture changes | GENESIS is frozen; GKC files an ADR if a conflict emerges |
| AIOS contract changes | GKC's contract is one-way (produces); AIOS adapts to consume |
| LLM landscape shifts | LLM independence (per `DESIGN/007` § 12) isolates GKC; providers are pluggable |

---

## 8. Migration

### 8.1 Workspace migration

When GKC upgrades to a new minor version:

- Old workspaces open with a `workspace-version-newer` warning.
- Snapshots from the old version are loadable (forward compatibility per `DESIGN/004` § 3).
- Caches may be invalidated (per ADR-Candidate-0057, GKC version is in the cache key).

When GKC upgrades to a new major version:

- Old workspaces require explicit migration via `gkc init --migrate`.
- Snapshots may need migration (per `DESIGN/004` § 7.3).
- A migration tool ships with the release.

### 8.2 Plugin migration

When GKC upgrades to a new minor version:

- Old plugins work if their `gkc_version_compat` range includes the new version.

When GKC upgrades to a new major version:

- Old plugins may need to be updated; the framework rejects incompatible plugins with a clear diagnostic.

### 8.3 User migration

For users currently on GENESIS-only workflows (no GKC):

- Install GKC.
- Run `gkc init` in their repository.
- Run `gkc scan .` to compile a snapshot.
- Use `gkc context` to consume the substrate.

No data migration is needed; GKC reads the repository directly.

---

## 9. Future Evolution

### 9.1 Post-M5 horizons

| Horizon | Engineering impact | Trigger |
|---|---|---|
| Ontology as first-class frontend | New frontend stage; ontology compiler becomes a frontend | When users want to compile ontologies independent of repositories |
| Contracts and policies | New validation pass; contract compilation | When GENESIS contracts become machine-checkable |
| Prompts as artifacts | New artifact kind; context compiler treats prompts as inputs | When prompt engineering becomes a first-class workflow |
| Runtime traces | New graph edge type; registry absorbs runtime observations | When PROMETHEUS runtime produces traces GKC should ingest |
| Cross-repository federation | Federated registries; resolver crosses repo boundaries | When users want to compile multi-repo architectures |
| Process-isolated plugins | Plugin sandboxing level C | When plugin trust becomes a problem |
| `gkc serve` long-running mode | New subcommand; in-memory IR | When one-shot CLI latency is insufficient |
| Central plugin registry | Plugin distribution infrastructure | When plugin ecosystem scales beyond git distribution |

### 9.2 Architecture stability

The design's separation of concerns (frontend / IR / backends) means each horizon is **additive**:

- New frontends add stages 1–4 variants; they do not change the IR or backends.
- New backends add consumers; they do not change the IR or frontends.
- New IR components (e.g., runtime traces) add new graph kinds; they do not change existing graphs.

No horizon requires restructuring the pipeline or rewriting components. This is the engineering payoff of the compiler framing (per `DESIGN/001` § 10).

### 9.3 Versioning policy

- **0.x**: M0–M5; no API stability; breaking changes between milestones.
- **1.0**: M5 exit; stable CLI subcommand set; stable JSON output schemas; stable exit codes.
- **1.x**: Additive changes; minor version bumps.
- **2.0**: When a horizon requires a breaking change (e.g., a new IR schema major version).

---

## 10. Release Process

### 10.1 Milestone release

1. All done-conditions verified.
2. All ADR candidates for the milestone are ratified or explicitly deferred.
3. Golden snapshots re-recorded.
4. Release notes written.
5. Tag: `v0.<milestone>.0-m<milestone>`.
6. Announcement.

### 10.2 Patch release

1. Bug fix identified; regression test added.
2. Fix implemented; regression test passes.
3. Golden snapshots unchanged (or re-recorded if the fix changes output, with ADR).
4. Tag: `v<major>.<minor>.<patch>`.

### 10.3 Minor release

1. New features added (additive only).
2. Documentation updated.
3. Tag: `v<major>.<minor>.0`.

### 10.4 Major release

1. Migration tool written and tested.
2. Documentation updated.
3. Deprecation notices from the prior major version are enforced.
4. Tag: `v<major>.0.0`.

---

## 11. Open Questions for ADR

Surfaced in `DECISIONS/012-reference-implementation-adr-candidates.md`:

1. Which implementation language is chosen for the reference implementation? (ADR-0010)
2. Which distribution mechanism (brew, npm, cargo, pip, standalone binary)? (ADR-0011)
3. Should the reference implementation be developed in a separate repo or within the design repo?
4. Should there be a formal verification effort for the core invariants (post-M5)?
5. Should GKC support a "watch" mode for re-compiling on file change?