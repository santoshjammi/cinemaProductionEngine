# GKC Roadmap

This roadmap tracks the **engineering product**, not the architecture. GENESIS (`000`–`018`) is frozen and has no roadmap. GKC has six milestones, each producing a usable compiler state. Milestones are strictly cumulative — each milestone's compiler is a strict superset of the previous one.

The roadmap is deliberately conservative about *dates* and aggressive about *done conditions*. A milestone is done when its done-conditions hold, not when a calendar says so.

---

## Milestone Index

| Milestone | Name | One-line goal | Design docs exercised |
|---|---|---|---|
| M0 | Skeleton | Compiler shape, CLI shell, empty pipeline | 003, 009, 012 |
| M1 | Scanner & Registry | A real repository parses into a real registry | 002, 004, 005 (stages 1–4) |
| M2 | Graphs & Ontology | Authority and dependency graphs close; ontology compiles | 005 (stages 5–7), 006 (basic) |
| M3 | Context Compiler | GKC emits token-bounded context packages for agents | 007 |
| M4 | Validation & Diagnostics | Drift against GENESIS surfaces as ranked diagnostics | 005 (validation), 011 |
| M5 | Plugin & AIOS Integration | Pluggable frontends; AIOS boots against GKC output | 008, 010 |

---

## M0 — Skeleton

**Goal:** A runnable compiler that does nothing correctly but is structurally a compiler.

**Done conditions:**
- `gkc scan`, `gkc doctor`, `gkc stats` execute on an empty repository and exit 0.
- The pipeline exists as named stages with no-op implementations; each stage produces a typed (empty) artifact and passes it forward.
- The storage layer exists with a writable, readable workspace directory and a snapshot metadata file.
- The plugin framework's extension points are declared but unimplemented.
- A golden repository `gold/empty` compiles end-to-end and produces a deterministic, byte-stable snapshot.

**Risk:** None. M0 is structural only.

---

## M1 — Scanner & Registry

**Goal:** A real repository parses into a real, queryable registry.

**Done conditions:**
- The scanner classifies artifacts by kind (document, schema, manifest, runtime, contract, etc.) using pluggable classifiers; at least four built-in classifiers ship.
- The parser extracts metadata for each artifact kind, including: identifier, version, authority level, references, and declared dependencies.
- The resolver resolves references into stable identifiers and reports unresolved references as diagnostics.
- The registry is persistent, content-addressed, and supports `gkc registry list`, `gkc registry show <id>`, `gkc registry find --kind=<K> --authority=<A>`.
- An incremental re-scan of a single changed artifact completes in O(affected subgraph), not O(repository).
- The golden repository `gold/small-repo` (≈30 artifacts) compiles in under 5 seconds on a warm cache.

**Design docs exercised:** `002` (domain model), `004` (data model), `005` stages 1–4.

**Risk:** Classifier boundary disputes — where does "document" end and "schema" begin? Mitigated by `DECISIONS/0002-artifact-kind-taxonomy.md`.

---

## M2 — Graphs & Ontology

**Goal:** The two graphs close; the ontology compiles; basic queries answer.

**Done conditions:**
- The **authority graph** is built from the registry and reflects every artifact's authority relationships (e.g., runtime → platform architecture → constitution).
- The **dependency graph** is built from declared and resolved dependencies; cycles are detected and reported.
- The **ontology** is compiled: domain concepts declared in artifacts become ontology nodes; references between them become ontology edges.
- `gkc graph authority|dependency|ontology` emits each graph in at least two formats (text + JSON), with stable schemas.
- `gkc search`, `gkc explain <id>` answer using the graphs, returning ranked results with provenance.
- The golden repository `gold/small-repo` produces a cycle-free authority graph, a cycle-free dependency graph (or reported cycles), and a fully linked ontology.

**Design docs exercised:** `005` stages 5–7, `006` (basic query surface).

**Risk:** Authority-cycle detection across constitutional levels. Mitigated by `DECISIONS/0003-authority-graph-stratification.md`.

---

## M3 — Context Compiler

**Goal:** GKC emits context packages that let an AI agent perform a task without reading the repository.

This is the flagship milestone. Everything before it produces the substrate; M3 produces the **payload** that makes GKC valuable to AI agents and IDEs.

**Done conditions:**
- `gkc context --task="<description>"` produces a context package bounded by a configurable token budget (default: model-dependent, configurable via profile).
- The context package is **dependency-closed** (all artifacts the task touches, plus their required dependencies) and **authority-aware** (higher-authority artifacts are preferred when budget forces a choice).
- The context package is **LLM-independent**: emitted as structured Markdown by default, with plugin providers for other formats (Anthropic XML, OpenAI JSON, local-LLM prompt files).
- Caching: a second `gkc context` call for the same task on an unchanged repository returns in under 100 ms from cache.
- Incremental: a single-artifact change invalidates only the context slices that depended on it.
- A reference agent (stub) consumes a GKC context package and answers a question about the repository correctly without any other input.

**Design docs exercised:** `007` (flagship), with `005` (pipeline integration) and `010` (cache storage).

**Risk:** Token-budget allocation policy is the single hardest design problem in GKC. Mitigated by `DECISIONS/0004-context-budget-allocation.md` and the adversarial review in `REVIEWS/007-context-compiler.md`.

---

## M4 — Validation & Diagnostics

**Goal:** A drifting repository produces **ranked, actionable diagnostics**, not a wall of errors.

**Done conditions:**
- A configurable validation pass runs after graph compilation, checking the registry and graphs against the GENESIS invariants surfaced from `000`–`018`.
- Diagnostics are ranked by severity (constitutional violation > structural error > drift > warning > info) and grouped by artifact and by invariant.
- Every diagnostic names: the offending artifact, the violated invariant (with GENESIS doc reference), the evidence, and a suggested resolution.
- `gkc validate` exits non-zero on any constitutional violation; CI integrable.
- The golden repository `gold/drifted-repo` produces a deterministic, ranked diagnostic set that is snapshot-tested.

**Design docs exercised:** `005` (validation stage), `011` (golden repositories and regression tests).

**Risk:** GENESIS invariants are prose; extracting them as machine-checkable rules is non-trivial. Mitigated by a dedicated invariant-codification sub-project tracked in `IMPLEMENTATION/invariants.md`.

---

## M5 — Plugin & AIOS Integration

**Goal:** GKC is extensible without forking, and AIOS boots against GKC's output.

**Done conditions:**
- A plugin can add a new artifact kind (with its own scanner, parser, metadata schema) without touching GKC core.
- A plugin can add a new graph edge type (e.g., "runtime-trace" edges) without touching GKC core.
- A plugin can add a new context provider (e.g., Anthropic XML, custom prompt template) without touching GKC core.
- Plugins are sandboxed by capability: a plugin declares required capabilities (filesystem read, network, subprocess) and is rejected at load time if it exceeds them.
- AIOS can boot against a compiled GKC workspace: it reads the registry, the graphs, and the ontology, and starts scheduling agents without a separate knowledge-acquisition step.
- An end-to-end test: a fresh checkout of a repository → `gkc scan` → `gkc context` → AIOS agent answers an architectural question, with no human-curated context.

**Design docs exercised:** `008` (plugin framework), `010` (storage contract for AIOS consumption).

**Risk:** Plugin sandboxing is a hard problem; the M5 scope is intentionally minimal (declared capabilities, load-time rejection) and defers runtime sandboxing to a later horizon.

---

## Cross-Cutting Work

These run continuously across milestones, not inside a single one:

| Track | Owner | Artifacts |
|---|---|---|
| Golden repositories | Testing | `gold/empty`, `gold/small-repo`, `gold/drifted-repo`, `gold/large-repo` |
| Invariant codification | Validation | `IMPLEMENTATION/invariants.md`, fed into M4 |
| Performance budget | Pipeline | Compiling `gold/large-repo` (≈10k artifacts) in under 60 s warm |
| Documentation | All | Each milestone ships updated DESIGN docs + ADRs |

---

## Out of Scope for the Roadmap

- **Implementation language choice.** Tracked in `DECISIONS/0010-implementation-language.md` and resolved before M0 exits.
- **Distribution mechanism** (brew, npm, cargo, pip, standalone binary). Tracked in `DECISIONS/0011-distribution.md` and resolved before M5.
- **Federated / cross-repository compilation.** Horizon 5+ per `VISION.md`; not on this roadmap.

---

## See Also

- `DESIGN/012-reference-implementation.md` — the engineering-grade companion to this roadmap.
- `DECISIONS/` — every ADR that adjusts the roadmap.
- `IMPLEMENTATION/` — per-milestone tracking artifacts (filled during build, not during design).