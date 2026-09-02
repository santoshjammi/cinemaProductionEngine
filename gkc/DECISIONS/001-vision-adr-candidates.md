# ADR Candidates — GKC-001 Vision

> Architectural decisions surfaced by `DESIGN/001-vision.md`, awaiting ratification. Each candidate has: context, options, recommendation, blocking impact. A candidate becomes an ADR when ratified and moved to `DECISIONS/ADR-XXXX.md`.

---

## ADR-Candidate-0001 — GKC IR is self-describing

**Context.** The Knowledge IR (registry + graphs + ontology) is consumed by AIOS, IDEs, plugins, and the CLI. Consumers need to know the schema version of what they're reading.

**Options.**
- **A. Self-describing IR.** Every snapshot embeds its schema. Consumers validate against the embedded schema before reading.
- **B. Externally versioned IR.** Schema is documented separately; snapshots carry only a version number. Consumers look up the schema externally.

**Recommendation.** A. Self-describing snapshots make GKC forward-compatible: a consumer that does not recognize the embedded schema can refuse gracefully, without an external lookup.

**Blocking impact.** Blocks `DESIGN/004` (data model) and `DESIGN/010` (storage). Must be resolved before M1.

---

## ADR-Candidate-0002 — Context compiler is a pipeline stage

**Context.** `DESIGN/007` describes the context compiler as the flagship consumer of the IR. It could be (a) a late pipeline stage that runs eagerly after indexing, or (b) a separate process that consumes the IR on demand.

**Options.**
- **A. Pipeline stage (eager).** Context slices are precomputed for a default set of task profiles. Faster queries; larger snapshot.
- **B. Separate process (lazy).** Context is built on demand and cached. Smaller snapshot; first-call latency.
- **C. Hybrid.** A small set of "standard" slices are precomputed; everything else is lazy.

**Recommendation.** C. Hybrid. Precompute a minimal standard slice set (e.g., "repository overview", "current task"); everything else lazy. Matches both S5 (warm-cache latency) and the cacheability invariant (7.4) without bloating snapshots.

**Blocking impact.** Blocks `DESIGN/005` (pipeline) and `DESIGN/007` (context). Must be resolved before M3.

---

## ADR-Candidate-0003 — Plugin failures are recoverable per-artifact

**Context.** Invariant 7.6 requires plugin failures not to corrupt the IR. The granularity of recovery matters.

**Options.**
- **A. Fatal at stage.** A plugin failure aborts the stage; the entire stage's output is the prior stage's output. Simple; coarse.
- **B. Recoverable per-artifact.** A plugin failure marks only the affected artifact; other artifacts in the same stage proceed. Complex; preserves throughput.
- **C. Configurable.** Default per-artifact; configurable to fatal.

**Recommendation.** B. Recoverable per-artifact. The compiler invariant (7.6) requires this — "Other artifacts and other stages are unaffected" implies per-artifact recovery.

**Blocking impact.** Blocks `DESIGN/008` (plugin framework) and the M0 skeleton. Must be resolved before M0.

---

## ADR-Candidate-0004 — Partial vs complete snapshots

**Context.** A snapshot is the persisted form of the IR. It could be (a) always complete (one file/blob with the entire IR), or (b) partial (per-stage persistence, with a manifest tying them together).

**Options.**
- **A. Complete snapshots only.** Simpler; atomic; easier to verify determinism. Larger writes; slower incremental updates.
- **B. Partial snapshots with manifest.** Faster incremental writes; harder to verify atomicity; harder determinism.
- **C. Layered: complete at milestone exits, partial during work.** Hybrid; more state to manage.

**Recommendation.** A. Complete snapshots only for M0–M3. Revisit at M5 if incremental write latency becomes a measured problem. Simplicity favors determinism (7.1) over write throughput.

**Blocking impact.** Blocks `DESIGN/010` (storage). Must be resolved before M0.

---

## ADR-Candidate-0005 — Validator runs inside the pipeline

**Context.** Validation (M4) checks the IR against GENESIS invariants. It could be (a) a late pipeline stage, or (b) an external consumer of the IR.

**Options.**
- **A. Inside pipeline (stage 9).** Validation runs on every compile; diagnostics are part of the snapshot. Always-fresh; couples validation to compile.
- **B. External consumer.** Validation is a separate command (`gkc validate`); runs against a compiled snapshot. Decoupled; can lag.
- **C. Both.** A minimal invariant set runs in the pipeline; the full set runs externally.

**Recommendation.** C. Both. A minimal set (constitutional violations, cycle detection) runs in the pipeline so they're always visible. The full set runs externally on demand. Matches "diagnostics over silence" (§ 8.4) without coupling the compiler to the full invariant set.

**Blocking impact.** Blocks `DESIGN/005` (pipeline) and `DESIGN/011` (testing). Must be resolved before M4.

---

## ADR-Candidate-0006 — Network access definition

**Context.** Invariant 7.8 requires GKC to compile without network. "Network" is ambiguous.

**Options.**
- **A. Strict.** No socket operations of any kind, including loopback and Unix domain sockets.
- **B. No external network.** Loopback and Unix sockets allowed (for local plugin IPC); no external network.
- **C. Configurable.** Default strict; plugin capability `network:loopback` opt-in.

**Recommendation.** B. No external network. Local IPC is reasonable for plugins; external network is not. Cross-check with `DESIGN/008` plugin capabilities.

**Blocking impact.** Blocks the local-first test in M0. Must be resolved before M0.

---

## ADR-Candidate-0007 — "Warm cache" definition

**Context.** Success criterion S5 specifies warm-cache query latency. "Warm cache" is undefined.

**Options.**
- **A. Cache hit.** The query has been run before in this session; result is in the in-memory cache.
- **B. Snapshot loaded.** The compiled snapshot is in memory; the query is the first of its kind.
- **C. Specified per benchmark.** Each benchmark declares its cache state.

**Recommendation.** B. Snapshot loaded. "Warm" means the snapshot is in memory; the query itself may be a cache miss but does not require recompilation. This matches user expectations after `gkc scan`.

**Blocking impact.** Blocks S5 measurement. Must be resolved before M2.

---

## ADR-Candidate-0008 — Hardware reference for throughput

**Context.** S8 specifies compile throughput targets. Without a hardware reference, the target is untestable.

**Options.**
- **A. Fixed reference machine.** Specify a concrete machine (e.g., "M2 Pro, 16GB"). Reproducible; not widely available.
- **B. Normalized to a benchmark.** Run a reference benchmark; throughput targets are multiples of it. Portable; harder to reason about.
- **C. Per-repository-class.** Different targets for different repo sizes; no absolute hardware reference.

**Recommendation.** B. Normalized to a benchmark. Define `gkc bench` as a reference workload; throughput targets are expressed as "X times the reference benchmark on the same machine".

**Blocking impact.** Blocks S8 measurement and `DESIGN/011` performance tests. Must be resolved before M5.

---

## ADR-Candidate-0009 — Authority tie-breaking

**Context.** § 8.3 says "authority wins" under token budget. What happens when two artifacts have equal authority?

**Options.**
- **A. Recency.** Newer artifact wins.
- **B. Reference count.** More-referenced artifact wins.
- **C.Declared priority.** Artifacts declare an explicit priority; ties broken by A then B.
- **D. Deterministic hash.** Tie broken by content hash; fully deterministic; arbitrary.

**Recommendation.** D, with B as a secondary signal. Determinism (7.1) requires the tie-break be deterministic; reference count is a useful secondary signal but is not strictly deterministic across incremental updates. C is appealing but adds authoring burden.

**Blocking impact.** Blocks `DESIGN/007` context budget allocation. Must be resolved before M3.

---

## ADR-Candidate-0010 — "Reference agent" definition for S4

**Context.** S4 requires a "reference agent" to answer repository questions using only a GKC context package. The reference agent is undefined.

**Options.**
- **A. Stub agent.** A deterministic stub that pattern-matches against the context package; not an LLM.
- **B. Local LLM.** A specified local model (e.g., 7B) with no tool use.
- **C. Frontier LLM.** A specified frontier model with tool use.
- **D. All three.** Test the same context package against all three; require all to answer correctly.

**Recommendation.** D. All three. The philosophy (§ 8.6) requires local LLM parity; testing against all three verifies the substrate is LLM-agnostic.

**Blocking impact.** Blocks S4 measurement and `DESIGN/011` context correctness tests. Must be resolved before M3.