# GKC-001 — Vision & Philosophy

> **Engineering-grade vision.** This document translates the product-level vision in `VISION.md` into engineering commitments: invariants, definitions of "understanding", measurable success conditions, and the philosophy that constrains every other DESIGN doc.

---

## 1. Purpose

This document answers, at engineering precision:

- Why does GKC exist as a compiler, not a tool or a service?
- What does it mean for GKC to "understand" a repository?
- What invariants must hold across every stage, every plugin, every backend?
- What is GKC's relationship to GENESIS, AIOS, and downstream consumers?
- What is in scope, what is out of scope, and what is explicitly deferred to a later horizon?

Every subsequent DESIGN doc inherits the commitments made here. Conflicts with this document must be resolved by ADR.

---

## 2. Why a Compiler

GKC is a **compiler** because the alternatives fail in characteristic ways:

| Alternative | Failure mode GKC avoids |
|---|---|
| A tool | Tools are ad-hoc; their behavior is whatever the last author wrote. GKC commits to deterministic, staged, cacheable behavior. |
| A service | Services couple compilation to availability and network. GKC is local-first; compilation never depends on a remote host. |
| A library | Libraries expose internals; callers couple to them. GKC exposes a CLI, a query contract, and a plugin contract — nothing else. |
| A database | Databases store; they do not *compile*. GKC's storage is a cache of compiled artifacts, not a source of truth. |
| An LLM agent | Agents are non-deterministic. GKC's outputs are byte-stable for a fixed input set. |

The compiler framing buys us four properties that no other framing gives us together:

1. **Determinism** — same inputs ⇒ same outputs, byte-identical.
2. **Staging** — the pipeline is a sequence of typed stages; each stage's output is the next stage's input.
3. **Incrementality** — a small input change re-runs only the affected subgraph of stages.
4. **Language independence** — frontends and backends are pluggable; the IR is host-language-agnostic.

These are not aspirations. They are invariants (Section 7).

---

## 3. What "Understanding" a Repository Means

A repository is **understood** by GKC when the following four closures are complete, consistent, and queryable:

### 3.1 Classification closure

Every artifact in the repository has a known **kind** (document, schema, manifest, runtime, contract, etc.). Unclassified artifacts are reported as diagnostics, not silently dropped. The set of kinds is open (extensible by plugins) but the closure is total: every artifact has *some* kind, even if that kind is `unknown`.

### 3.2 Authority closure

Every artifact has a known **authority level** drawn from the GENESIS stratification (constitutional, statutory, guidance, deprecated, etc.). The authority graph is acyclic *within a stratum* and stratified *across strata*. Violations are reported, not silently tolerated.

### 3.3 Dependency closure

Every declared dependency of every artifact resolves to another artifact in the registry (or is reported as an unresolved reference). The transitive closure of dependencies is computable in O(registered edges), and cycles are detected.

### 3.4 Ontology closure

Every domain concept declared by an artifact is present in the ontology. Every reference to a domain concept resolves to an ontology node. The ontology is queryable both as a graph and as a term index.

**Definition:** A repository is *fully compiled* iff all four closures hold. A repository is *partially compiled* iff at least one closure is incomplete; in that case, GKC emits a diagnostic set and a partial snapshot, never a silent failure.

---

## 4. Relationship to GENESIS

GENESIS documents `000`–`018` are the **constitutional source of truth**. GKC's job is not to interpret GENESIS freely; GKC's job is to **enforce GENESIS inside a specific repository**.

| If GKC behavior... | Then... |
|---|---|
| Aligns with a GENESIS document | Proceed. |
| Conflicts with a GENESIS document | GKC emits a constitutional violation diagnostic; it does not silently override. |
| Is silent where GENESIS specifies | GKC treats the GENESIS rule as an invariant and codifies it in the validation pass (see `DESIGN/005` § validation). |
| Specifies where GENESIS is silent | GKC files an ADR (`DECISIONS/`) for ratification. |

GKC does not amend GENESIS. GKC's evolution is constrained by GENESIS until GENESIS itself is amended through its own governance process.

---

## 5. Relationship to AIOS

AIOS consumes GKC's output as its **knowledge substrate**. The contract is one-way: GKC produces, AIOS consumes. GKC never depends on AIOS.

The contract has three layers:

1. **Registry contract.** AIOS reads the registry to know what artifacts exist and what their metadata is.
2. **Graph contract.** AIOS reads the authority and dependency graphs to navigate relationships.
3. **Context contract.** AIOS requests a context package from GKC (or from a cached package) for a given task; GKC returns a token-bounded, dependency-closed, authority-aware payload.

AIOS is not the only consumer. IDEs, validators, plugins, and the CLI all consume the same substrate through the same contracts. This is deliberate: the substrate is **consumer-agnostic**.

---

## 6. Success Criteria (Engineering-Grade)

These are testable. A milestone exit requires evidence for each.

| # | Criterion | How measured |
|---|---|---|
| S1 | Determinism | Byte-identical snapshots across machines for the same repo + GKC version + plugin set |
| S2 | Incrementality | A single-artifact change re-runs ≤ k stages, where k is bounded by the affected subgraph size, not the repository size |
| S3 | Diagnostic completeness | Every non-zero exit is accompanied by a ranked diagnostic set with provenance |
| S4 | Context sufficiency | A reference agent answers repository questions correctly using only a GKC context package |
| S5 | Query latency | Warm-cache `gkc search`/`explain`/`graph` under 1 s on `gold/large-repo` (≈10k artifacts) |
| S6 | Plugin isolation | A failing plugin in any stage does not corrupt the IR or the snapshot |
| S7 | AIOS boot | AIOS boots against a GKC snapshot with no separate knowledge-acquisition step |
| S8 | Compile throughput | `gold/large-repo` cold compile under 60 s; warm incremental re-compile under 5 s |

These criteria are referenced by `REVIEWS/` for each milestone and by `DESIGN/011-testing.md` for the testing strategy.

---

## 7. Invariants (Compiler Contract)

Every DESIGN doc must respect these invariants. Every ADR that weakens an invariant requires explicit ratification.

### 7.1 Determinism invariant

For a fixed `(repository state, GKC version, plugin set, plugin versions, configuration)`, GKC produces a byte-identical snapshot. Sources of nondeterminism (timestamps, filesystem walk order, parallel scheduling) must be normalized before they enter any persisted artifact.

### 7.2 Staging invariant

The pipeline is a directed acyclic graph of stages. Each stage has a typed input contract and a typed output contract. No stage reads from a later stage's output. Stages may emit diagnostics but cannot mutate earlier stages' outputs.

### 7.3 Incrementality invariant

For any artifact change Δ, the set of stages that must re-run is computable in O(|Δ| + |affected subgraph|), and is a strict subset of all stages. Cache invalidation is content-addressed, not time-based.

### 7.4 Cacheability invariant

Every stage's output is cacheable by `(stage id, input content hash, configuration hash, plugin set hash)`. A cache hit returns byte-identical output. Cache misses are reproducible.

### 7.5 Diagnostic invariant

Every stage may emit diagnostics. Diagnostics carry: artifact id, stage id, severity, invariant reference, evidence, suggested resolution. Diagnostics are immutable once emitted; ranking is a post-processing step.

### 7.6 Plugin isolation invariant

A plugin failure in any stage is caught at the stage boundary. The failure is reported as a diagnostic. The stage's output for the affected artifact is the *prior* stage's output plus a `plugin-failed` marker. Other artifacts and other stages are unaffected.

### 7.7 GENESIS primacy invariant

If any GKC output conflicts with a GENESIS document, GKC must emit a constitutional violation diagnostic. GKC must not silently produce output that violates GENESIS.

### 7.8 Local-first invariant

GKC compiles without network access. Plugins may declare network capability, but the core compiler never requires it. Compilation works on an air-gapped machine.

---

## 8. Philosophy

### 8.1 Compilation over interpretation

GKC does not interpret repositories on demand. It compiles them ahead of demand, persists the result, and serves queries from the compiled form. This is what makes sub-second queries possible.

### 8.2 Closed-world over open-world

Within a single repository snapshot, GKC operates closed-world: if something is not in the registry, it does not exist. Cross-repository federation is a later horizon (see `VISION.md` § Future Evolution) and will be additive, not a recompilation.

### 8.3 Authority is not popularity

When the context compiler must choose between artifacts under a token budget, **authority wins**. A constitutional document outranks a tutorial, even if the tutorial is more recent or more frequently referenced.

### 8.4 Diagnostics over silence

GKC never silently drops, silently overrides, or silently ignores. If a behavior is undefined, GKC emits a diagnostic. If a behavior is defined but violated, GKC emits a diagnostic. The only silent behavior is success.

### 8.5 Evolving over frozen

Unlike GENESIS, GKC's design documents evolve with engineering. Every change is recorded as an ADR. There is no constitutional amendment process for GKC — only an engineering decision process.

### 8.6 Local LLM parity

GKC's context compiler must produce context that is usable by a local LLM (limited context window, no tool use) and by a frontier LLM (large context window, tool use) from the same substrate. The substrate is LLM-agnostic; the emitter is LLM-specific.

---

## 9. Non-Goals (Engineering-Grade)

These are *engineering* non-goals, complementing the product non-goals in `VISION.md`.

- GKC does not **execute** any artifact it compiles. Execution is PROMETHEUS's job.
- GKC does not **generate** code, prose, or prompts. Generation is the runtime's job.
- GKC does not **schedule** agents or work. Scheduling is AIOS's job.
- GKC does not **authenticate** users or manage permissions. That is the platform's job.
- GKC does not **synchronize** across machines. GKC is local-first; sync is the user's mechanism (git, rsync, etc.).
- GKC does not **learn** across compilations. The cache is content-addressed, not learned.

---

## 10. Future Evolution (Engineering Horizons)

The vision document names five horizons. The engineering implications:

| Horizon | Engineering impact | DESIGN doc affected |
|---|---|---|
| Ontologies and schemas | Ontology compiler becomes a first-class frontend, not a stage over the registry | `005`, `008` |
| Contracts and policies | New validation pass over contracts; policy enforcement at compile time | `005`, `011` |
| Prompts as artifacts | New artifact kind; context compiler treats prompts as first-class inputs | `002`, `007` |
| Runtime traces | New graph edge type; registry absorbs runtime observations | `002`, `010` |
| Cross-repository | Federated registries; resolver crosses repository boundaries | `004`, `010` |

Each horizon is **additive**: it extends an existing stage or adds a new stage, but does not restructure the pipeline. This is the engineering payoff of the compiler framing.

---

## 11. Open Questions for ADR

These are surfaced as ADR candidates in `DECISIONS/0001-vision-adr-candidates.md`:

1. Should GKC's IR be self-describing (schema embedded) or externally versioned?
2. Should the context compiler be a separate process or a pipeline stage?
3. Should plugin failures be fatal at the stage level or recoverable per-artifact?
4. Should GKC support partial snapshots (per-stage persistence) or only complete snapshots?
5. Should the validator run inside the pipeline or as an external consumer of the IR?

---

## 12. References

- `VISION.md` — product-level vision (this document is the engineering-grade companion).
- `ARCHITECTURE.md` — system architecture map.
- `DESIGN/005-pipeline.md` — the pipeline that operationalizes the invariants in §7.
- `DESIGN/007-context-compiler.md` — the flagship consumer of the philosophy in §8.3–8.6.
- `DECISIONS/0001-vision-adr-candidates.md` — open questions from this document.