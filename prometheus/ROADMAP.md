# PROMETHEUS Roadmap

This roadmap tracks the **engineering product**, not the architecture. GENESIS (`000`–`018`) is frozen and has no roadmap. PROMETHEUS has six milestones, each producing a usable runtime state. Milestones are strictly cumulative — each milestone's runtime is a strict superset of the previous one.

The roadmap is deliberately conservative about *dates* and aggressive about *done conditions*. A milestone is done when its done-conditions hold, not when a calendar says so.

---

## Milestone Index

| Milestone | Name | One-line goal | Design docs exercised |
|---|---|---|---|
| M0 | Skeleton | Runtime shape, CLI shell, empty pipeline, EIR schema | 003, 004, 009, 012 |
| M1 | Load & Validate | A real PKP loads, validates, and resolves into a real EIR | 005, 007, 010, 014 |
| M2 | Schedule & Execute | The EIR executes end-to-end through stub adapters; events emit | 006, 008, 011, 012 |
| M3 | Real Adapters & Recovery | Cinema adapters (image, voice, music, ffmpeg) run; recovery and resume work | 006, 012, 013, 014 |
| M4 | Observability & Provenance | Metrics, diagnostics, execution report, full provenance to ATLAS | 008, 010, 013 |
| M5 | Plugin & Platform Independence | Pluggable adapters/validators/schedulers; non-cinema PKP executes | 015, 016 |

---

## M0 — Skeleton

**Goal:** A runnable runtime that does nothing correctly but is structurally a runtime.

**Done conditions:**
- `prometheus run`, `prometheus doctor`, `prometheus status` execute on an empty PKP and exit 0.
- The pipeline exists as named stages with no-op implementations; each stage produces a typed (empty) artifact and passes it forward.
- The EIR schema is defined as a language-neutral data contract (JSON Schema + a stable textual form); an empty PKP produces an empty EIR.
- The adapter interface is declared but unimplemented; a stub adapter is registered and callable.
- The event bus exists; every stage emits at least one structured event with the required fields (`DESIGN/008`).
- The checkpoint manager exists with a writable, readable workspace directory and a snapshot metadata file.
- The plugin framework's extension points are declared but unimplemented.
- A golden PKP `gold/empty` executes end-to-end and produces a deterministic, byte-stable execution report.

**Risk:** None. M0 is structural only.

**Design docs exercised:** `003` (component architecture), `004` (EIR schema), `009` (CLI), `012` (checkpoint).

---

## M1 — Load & Validate

**Goal:** A real PKP loads, validates, and compiles into a real, queryable EIR.

**Done conditions:**
- The PKP loader reads a frozen PKP from ATLAS (or a local path for testing), verifies the PKP hash, and verifies the PKP is in the `frozen` state; mismatches emit `constitutional-violation` diagnostics.
- The constitutional validator checks the PKP against a codified subset of GENESIS invariants (at least: L-14 read-only, L-15 no-invent, L-18 knowledge-outlives-media, plus the PKP completeness rules from `009`).
- The dependency resolver closes the PKP's declared dependencies; unresolved references emit diagnostics, not silent drops.
- The resource resolver resolves adapter identities, asset references, seeds, and configs; unresolved resources emit diagnostics.
- The timeline builder, execution planner, and execution graph builder produce a complete EIR from the resolved PKP; every PKP artifact maps to ≥1 EIR node.
- The EIR dependency graph is acyclic; cycles emit `dependency-cycle` diagnostics.
- `prometheus eir show <node>`, `prometheus eir graph`, `prometheus eir validate` work and emit stable JSON.
- Incremental re-planning of a single changed PKP artifact completes in O(affected subgraph), not O(EIR).
- The golden PKP `gold/small-pkp` (≈30 artifacts) compiles in under 5 seconds on a warm cache and produces a byte-stable EIR.

**Design docs exercised:** `005` (pipeline), `007` (loader), `010` (validator), `014` (resource resolution).

**Risk:** GENESIS invariant codification is non-trivial; mitigated by `IMPLEMENTATION/invariants.md` and a dedicated sub-project tracked there.

---

## M2 — Schedule & Execute

**Goal:** The EIR executes end-to-end through stub adapters; the event stream and state manager work; failures classify.

**Done conditions:**
- The scheduler dispatches EIR nodes in topological order; independent nodes run in parallel; deterministic merge order is by EIR node id.
- The runtime state manager tracks per-node state (`pending`, `running`, `succeeded`, `failed`, `skipped`, `retried`).
- The event bus emits one structured event per node transition with all required fields (`DESIGN/008`).
- The adapter framework dispatches to stub adapters (image-stub, voice-stub, music-stub, ffmpeg-stub) that produce deterministic placeholder outputs.
- The failure recovery engine classifies failures into: recoverable, retryable, fatal, constitutional, infrastructure, dependency, configuration, adapter, resource, validation.
- The retry strategy applies a per-class retry policy with bounded retries; retries are recorded in the event stream.
- A fault-injecting adapter demonstrates that a failing adapter produces a diagnostic, not a crash, and the execution continues for other nodes.
- The golden PKP `gold/small-pkp` executes end-to-end with stub adapters and produces a complete execution report.

**Design docs exercised:** `006` (adapter framework), `008` (events/metrics), `011` (scheduler), `012` (recovery/checkpoint).

**Risk:** Concurrency model choice (threads/actors/async) interacts with determinism; mitigated by `DECISIONS/00XX-concurrency-model.md`.

---

## M3 — Real Adapters & Recovery

**Goal:** Cinema adapters (image, voice, music, ffmpeg) run against a real PKP; recovery, fallback, and resume work.

**Done conditions:**
- At least four real adapters ship: image generation (Stable Diffusion / FLUX local, with a cloud fallback behind the same interface), voice synthesis (edge-tts local, with a cloud fallback), music generation (procedural local, with a cloud fallback), and audio/video assembly (FFmpeg).
- Each adapter records its version, the seed (if any), and its invocation parameters in the event stream and provenance.
- The recorded-output fallback (`010` §9.3) is implemented for irreducibly non-deterministic providers; replay reads the recorded output from ATLAS instead of re-invoking the provider.
- The failure recovery engine applies fallback providers per the capability registry; fallbacks are recorded in the execution report.
- The rendering-gap path (`010` §8.3) is implemented: a PKP artifact missing a required detail produces a `rendering-gap` diagnostic and continues rendering other artifacts.
- The checkpoint manager persists state at every stage; resuming from a checkpoint produces byte-identical outputs to a no-checkpoint run.
- The golden PKP `gold/cinema-pkp` (a real short production) renders end-to-end and produces a real video.

**Design docs exercised:** `006` (real adapters), `012` (recovery/resume), `013` (provenance/emission), `014` (resource/cache).

**Risk:** Real adapter non-determinism is the single hardest engineering problem; mitigated by the recorded-output fallback and `DECISIONS/00XX-recorded-output-policy.md`.

---

## M4 — Observability & Provenance

**Goal:** Every execution is fully observable; every output is fully provenanced; ORACLE can audit from the report alone.

**Done conditions:**
- The metrics engine collects per-step, per-adapter, per-resource metrics (duration, inputs, outputs, dependencies, resource usage, diagnostics).
- The diagnostics subsystem ranks diagnostics by severity (constitutional > structural > drift > warning > info) and groups by artifact and invariant.
- The execution report includes: the EIR, the schedule, every event, every diagnostic, every fallback, every retry, every skip, and the final output manifest.
- The asset emission service stamps every output with provenance: PKP artifact, PKP hash, EIR node id, adapter id + version, seed, timestamp, parent outputs.
- The execution report and provenance are written to ATLAS; ORACLE can validate outputs against the PKP using only the report + provenance.
- `prometheus report`, `prometheus provenance <output>` work and emit stable JSON.
- The golden PKP `gold/cinema-pkp` produces a deterministic, ranked diagnostic set and a byte-stable execution report that is snapshot-tested.

**Design docs exercised:** `008` (observability), `010` (diagnostics), `013` (provenance/report).

**Risk:** Provenance graph scale for long productions; mitigated by `DECISIONS/00XX-provenance-compaction.md`.

---

## M5 — Plugin & Platform Independence

**Goal:** PROMETHEUS is extensible without forking, and a non-cinema PKP executes through the same engine.

**Done conditions:**
- A plugin can add a new adapter (with its own capability interface) without touching the runtime core.
- A plugin can add a new validator (e.g., a domain-specific invariant set) without touching the runtime core.
- A plugin can add a new scheduler strategy (e.g., a distributed scheduler) without touching the runtime core.
- Plugins are sandboxed by capability: a plugin declares required capabilities (filesystem read, network, subprocess) and is rejected at load time if it exceeds them.
- A non-cinema golden PKP (e.g., `gold/book-pkp` or `gold/gamelevel-pkp`) executes through the same engine with domain-specific adapters and produces a complete execution report. This validates S8 (domain independence).
- An end-to-end test: a fresh PKP → `prometheus run` → outputs + report in ATLAS → ORACLE validates, with no human-curated context.

**Design docs exercised:** `015` (plugin/security), `016` (testing/benchmark).

**Risk:** Plugin sandboxing is a hard problem; the M5 scope is intentionally minimal (declared capabilities, load-time rejection) and defers runtime sandboxing to a later horizon.

---

## Cross-Cutting Work

These run continuously across milestones, not inside a single one:

| Track | Owner | Artifacts |
|---|---|---|
| Golden PKPs | Testing | `gold/empty`, `gold/small-pkp`, `gold/cinema-pkp`, `gold/book-pkp`, `gold/drifted-pkp` |
| Invariant codification | Validation | `IMPLEMENTATION/invariants.md`, fed into M1 |
| Determinism harness | Pipeline | Two-execution byte-identity test runs on every golden PKP |
| Performance budget | Pipeline | Compiling + executing `gold/large-pkp` (≈10k artifacts) in under 120 s warm |
| Documentation | All | Each milestone ships updated DESIGN docs + ADRs |

---

## Out of Scope for the Roadmap

- **Implementation language choice.** Tracked in `DECISIONS/` and resolved before M0 exits. The reference implementation targets one language; all contracts remain language-neutral.
- **Distribution mechanism.** Tracked in `DECISIONS/` and resolved before M5.
- **Federated / cross-runtime execution.** Horizon 5+ per `VISION.md`; not on this roadmap.
- **Real-time / streaming execution.** Horizon 5+; not on this roadmap.
- **Adaptive re-planning mid-run.** Horizon 5+; the initial scheduler is static-plan.

---

## See Also

- `DESIGN/012-reference-implementation.md` — the engineering-grade companion to this roadmap (to be written in Phase 2).
- `DECISIONS/` — every ADR that adjusts the roadmap.
- `IMPLEMENTATION/` — per-milestone tracking artifacts (filled during build, not during design).