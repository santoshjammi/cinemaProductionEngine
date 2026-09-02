# PROMETHEUS-001 — Vision & Philosophy

> **Engineering-grade vision.** This document translates the product-level vision in `VISION.md` into engineering commitments: invariants, definitions of "execution", measurable success conditions, and the philosophy that constrains every other DESIGN doc.

---

## 1. Purpose

This document answers, at engineering precision:

- Why does PROMETHEUS exist as an execution engine, not a tool, an agent, or an orchestrator?
- What does it mean for PROMETHEUS to "execute" a PKP?
- What invariants must hold across every stage, every adapter, every plugin?
- What is PROMETHEUS's relationship to GENESIS (`010`), ORACLE (`011`), and ATLAS (`012`)?
- What is in scope, what is out of scope, and what is explicitly deferred to a later horizon?

Every subsequent DESIGN doc inherits the commitments made here. Conflicts with this document must be resolved by ADR. Conflicts with `010 — PROMETHEUS Runtime Architecture.md` must be resolved by constitutional revision, not by this document.

---

## 2. Why an Execution Engine

PROMETHEUS is an **execution engine** because the alternatives fail in characteristic ways:

| Alternative | Failure mode PROMETHEUS avoids |
|---|---|
| A pipeline script | Scripts couple intent to execution order; they cannot be re-planned or re-executed against a different adapter set. PROMETHEUS compiles the PKP into an EIR that any adapter can consume. |
| An orchestrator | Orchestrators decide *how* to run things and drift from intent. PROMETHEUS decides only *how to execute what was declared*; it never invents steps. |
| A job runner | Job runners track jobs but not provenance. PROMETHEUS produces a complete execution report and event stream traceable to every PKP artifact. |
| An agent loop | Agent loops are non-deterministic. PROMETHEUS is deterministic: same PKP + same adapter versions ⇒ same outputs. |
| A monolithic runtime | Monoliths couple the engine to the adapters. PROMETHEUS is adapter-pluggable: the engine is unchanged when providers are swapped. |

The execution-engine framing buys four properties that no other framing gives together:

1. **Determinism** — same inputs ⇒ same outputs, byte-identical (or hash-identical, with the recorded-output fallback per `010` §9.3 for irreducibly non-deterministic providers).
2. **Staging** — PKP → EIR → Schedule → Execute → Emit is a sequence of typed stages; each stage's output is the next stage's input.
3. **Resumability** — a checkpoint at any stage can resume without recomputing prior stages.
4. **Adapter independence** — adapters consume the EIR; they never touch the PKP. The EIR is the execution contract.

These are not aspirations. They are invariants (Section 7).

---

## 3. What "Executing" a PKP Means

A PKP is **executed** by PROMETHEUS when the following five closures are complete, consistent, and observable:

### 3.1 Compilation closure

Every PKP artifact is compiled into one or more EIR nodes. No PKP artifact is dropped silently. Artifacts the PKP marks `skipped` (with rationale) are represented in the EIR as explicit skip nodes; they are not omitted. The EIR is a total mapping of the PKP.

### 3.2 Dependency closure

Every EIR node declares its dependencies on other EIR nodes. The dependency graph is acyclic. Cycles are reported as diagnostics, not silently tolerated. The scheduler can compute a valid topological execution order in O(EIR edges).

### 3.3 Execution closure

Every executable EIR node is dispatched to exactly one adapter invocation. No node is executed twice unless the execution is explicitly a retry (recorded in the event stream). No node is skipped unless the PKP marked it `skipped` or a failure classified as fatal and unrecoverable terminated the execution.

### 3.4 Provenance closure

Every output artifact carries provenance: the PKP artifact it was rendered from, the PKP hash, the EIR node id, the adapter id and version, the seed (if any), the timestamp, and the parent outputs it depended on. The provenance graph is a subgraph of the EIR and is queryable.

### 3.5 Observability closure

Every execution step emits a structured event with: timestamp, duration, inputs, outputs, dependencies, adapter metrics, resource usage, diagnostics, and provenance. No silent execution is permitted (`010` §5, `DESIGN/008`). The event stream is the basis for the execution report.

**Definition:** A PKP is *fully executed* iff all five closures hold. A PKP is *partially executed* iff at least one closure is incomplete; in that case, PROMETHEUS emits a diagnostic set and a partial execution report, never a silent failure (`010` §8.4).

---

## 4. Relationship to GENESIS

GENESIS documents `000`–`018` are the **constitutional source of truth**. `010 — PROMETHEUS Runtime Architecture.md` is the canonical architectural definition of the runtime. PROMETHEUS's job is not to interpret `010` freely; PROMETHEUS's job is to **execute the PKP that GENESIS compiled**, within the constraints `010` fixed.

| If PROMETHEUS behavior... | Then... |
|---|---|
| Aligns with a GENESIS document | Proceed. |
| Conflicts with a GENESIS document | PROMETHEUS emits a `constitutional-violation` diagnostic; it does not silently override. |
| Is silent where GENESIS specifies | PROMETHEUS treats the GENESIS rule as an invariant and codifies it in the constitutional validator (see `DESIGN/010`). |
| Specifies where GENESIS is silent | PROMETHEUS files an ADR (`DECISIONS/`) for ratification. |

PROMETHEUS does not amend GENESIS. Where `010` is found to be incomplete, the gap is closed by **constitutional revision or ADR** — never by silently overriding the architecture. This package's engineering decisions are a different track from GENESIS's constitutional decisions and the two must never be confused.

---

## 5. Relationship to the Other Pillars

| Pillar | Relationship | Direct calls? |
|---|---|---|
| **GENESIS** | Defines intent. PROMETHEUS executes intent. | No — PROMETHEUS never calls GENESIS during execution (`010` §6.2). |
| **ORACLE** | Verifies that PROMETHEUS's output matched the PKP. | No — the contract is mediated by ATLAS (`010` §6.3). |
| **ATLAS** | Preserves the PKP, PROMETHEUS's outputs, and the execution report. | Yes — PROMETHEUS reads the PKP from ATLAS and writes outputs + reports to ATLAS. |

The four pillars are deliberately decoupled. All cross-pillar interaction is mediated by ATLAS. This keeps the runtime a pure executor and makes the entire pipeline auditable from ATLAS alone.

The single-Responsibility principle stated in `README.md`:

| Pillar | Responsibility |
|---|---|
| GENESIS | Defines intent — *what should exist* |
| PROMETHEUS | Compiles intent into executable work — *how it should execute* |
| ORACLE | Verifies execution matched intent — *was it executed correctly?* |
| ATLAS | Preserves execution knowledge and provenance — *what happened and how can it be reused?* |

---

## 6. Success Criteria

PROMETHEUS is successful when, for **any** PKP from **any** domain that conforms to the PKP contract (`009`):

| # | Criterion | Measurable as |
|---|---|---|
| S1 | The PKP compiles to a complete EIR. | Every PKP artifact maps to ≥1 EIR node; the EIR dependency graph is acyclic. |
| S2 | The EIR executes under any compliant adapter set. | A second adapter set (e.g., a stub adapter) produces a complete execution report. |
| S3 | Execution is reproducible. | Two executions of the same PKP + same adapter versions produce hash-identical outputs (or recorded-output-identical for non-deterministic providers). |
| S4 | Execution is explainable. | The execution report plus event stream reconstructs every decision the scheduler made. |
| S5 | Execution is resumable. | A checkpoint at any stage resumes without recomputing prior stages; outputs are byte-identical to a no-checkpoint run. |
| S6 | Execution is auditable. | ORACLE can validate outputs against the PKP using only the execution report + provenance. |
| S7 | The engine is adapter-independent. | Swapping an adapter requires no engine code changes; only the registry changes. |
| S8 | The platform is domain-independent. | A non-cinema PKP (e.g., a book, a game level) executes through the same engine with domain-specific adapters. |

S8 is the longest-horizon condition; the initial milestones target cinema but the architecture does not assume cinema.

---

## 7. Invariants

Every invariant below is **testable** and has a defined test harness or cross-reference. A DESIGN doc or implementation that violates an invariant must either change or file an ADR justifying the violation.

### 7.1 Determinism

> Same PKP + same adapter versions ⇒ same outputs, byte-identical (or hash-identical via the recorded-output fallback).

- **Normalization of non-deterministic inputs:** timestamps, wall-clock durations, and walk orders are normalized before they affect output identity. Timestamps are recorded in events but do not enter output hashes. Walk order is determined by EIR node id (lexicographic), not by OS scheduling.
- **Test harness:** `gold/determinism-harness` runs every golden PKP twice on two fresh checkouts and asserts byte-identical outputs (or recorded-output-identical for non-deterministic providers). Cross-reference `DESIGN/016` § determinism tests.

### 7.2 Staging

> The pipeline is a DAG of typed stages; each stage's output is the next stage's input.

- **DAG structure:** defined in `DESIGN/005` § stage contract. The canonical order is: Load → Validate → ResolveDeps → ResolveRes → Timeline → Plan → BuildGraph → EmitEIR → Schedule → Execute → Recover → Checkpoint → EmitOutputs → Report.
- **Test:** `prometheus pipeline graph` emits the stage DAG; a test asserts it is acyclic and matches the canonical order.

### 7.3 Resumability

> A checkpoint at any stage resumes without recomputing prior stages; outputs are byte-identical to a no-checkpoint run.

- **Checkpoint identity:** `(stage id, input content hash, configuration hash, adapter set hash, plugin set hash) → checkpoint key`. The function is pure and deterministic.
- **Resume semantics:** resuming from a checkpoint re-reads the checkpoint's stage output and proceeds; it does not recompute the stage.
- **Test:** run a golden PKP to completion; run the same PKP with a checkpoint after each stage and resume; assert byte-identical outputs. Cross-reference `DESIGN/012`.

### 7.4 Cacheability

> A cache hit reuses prior outputs; a cache miss re-executes. The cache key is pure and total.

- **Cache key:** `(EIR node hash, adapter id, adapter version, seed, configuration hash) → cache key`. The function is pure.
- **Cache invalidation:** a change in any key component invalidates the cache entry for that node only; other entries are unaffected.
- **Test:** execute a golden PKP; execute again with the cache warm; assert the second run uses cache hits for every node and produces byte-identical outputs. Cross-reference `DESIGN/014` § cache.

### 7.5 Diagnostic completeness

> Every failure, gap, fallback, retry, and skip emits a diagnostic. No silent execution.

- **Diagnostic schema:** defined in `DESIGN/010` § diagnostics. Every diagnostic carries: artifact id, stage id, severity, invariant reference (if any), evidence, suggested resolution.
- **Severity ranking:** constitutional > structural > drift > warning > info. Ranking is a total order within a stage; cross-stage ranking is by stage order then severity.
- **Test:** fault-injecting adapters (image-fail, voice-fail, ffmpeg-fail) produce diagnostics, not crashes; the diagnostic set is snapshot-tested. Cross-reference `DESIGN/010`.

### 7.6 Adapter isolation

> An adapter failure is contained to the failing node; it does not crash the runtime.

- **Failure boundary:** adapter exceptions, timeouts, bad outputs, and resource exhaustion are caught by the adapter framework, classified by the failure recovery engine, and recorded as diagnostics.
- **Test:** a fault-injecting adapter produces a diagnostic for its node; other nodes continue; the execution report records the failure. Cross-reference `DESIGN/006`, `DESIGN/012`.

### 7.7 GENESIS primacy

> If this package conflicts with `010` or any GENESIS document, GENESIS wins.

- **Conflict detection:** the constitutional validator checks the PKP and the EIR against codified GENESIS invariants. Conflicts emit `constitutional-violation` diagnostics.
- **Escalation:** a DESIGN doc that conflicts with `010` must either change or file an ADR requesting constitutional revision. Engineering ADRs cannot amend GENESIS.
- **Test:** the validator is seeded with a codified invariant set (`IMPLEMENTATION/invariants.md`); a PKP that violates a known invariant produces a `constitutional-violation` diagnostic. Cross-reference `DESIGN/010`.

### 7.8 Local-first

> The runtime runs with no network access; cloud adapters are opt-in behind the same capability interface.

- **Network access definition:** any socket open to a non-loopback address. Loopback (for local model servers like Ollama) is permitted; non-loopback is gated by configuration and capability policy.
- **Test:** execute a golden PKP with the network disabled (sandboxed environment) using only local adapters; assert successful exit. Cross-reference `DESIGN/015` § security.

### 7.9 Provenance completeness

> Every output carries full provenance; an output without provenance is not a PROMETHEUS output.

- **Provenance fields:** PKP artifact, PKP hash, EIR node id, adapter id + version, seed (if any), timestamp, parent outputs.
- **Test:** every output in a golden run has a provenance entry; the provenance graph is a subgraph of the EIR; `prometheus provenance <output>` reconstructs the full chain. Cross-reference `DESIGN/013`.

---

## 8. Philosophy

The philosophy that constrains every DESIGN doc in this package:

### 8.1 Execution, not creation

PROMETHEUS executes what GENESIS declares. It never invents (`010` §1.2, `006` L-15). If the PKP is silent on a detail the runtime needs, the runtime reports a **rendering gap** (`010` §8.3), not an invention.

### 8.2 Determinism is constitutional

Given the same PKP and the same adapter versions, PROMETHEUS produces the same outputs. Determinism is the final link in the platform's deterministic replay chain (`010` §1.3, `006` L-14). The recorded-output fallback (`010` §9.3) ensures determinism even for irreducibly non-deterministic providers.

### 8.3 Diagnostics over silence

Every failure, gap, fallback, and skip is reported loudly (`010` §8.4, `00` §3.7). PROMETHEUS never silently produces broken outputs. An artifact marked `rendering_failed` or `rendering_gap` is not included in the final assembly.

### 8.4 Provenance is non-negotiable

Every output carries full provenance (`010` §2.4). An output without provenance is not a PROMETHEUS output. Provenance is the basis for ORACLE's validation and ATLAS's preservation.

### 8.5 Adapters are replaceable; the engine is not

The runtime core is stable; adapters, validators, schedulers, storage, and caches are plugins (`010` §10). Swapping an adapter requires no engine code changes; only the registry changes. New adapters are added by implementing the capability interface and registering; no runtime code changes.

### 8.6 Local-first, cloud-capable

The default configuration uses local adapters; cloud adapters are opt-in behind the same capability interface (`010` §11.2, `00` §3.4). The sovereignty principle: the creator must not be dependent on a third party's API quota, model availability, or pricing to produce their own work.

### 8.7 Contracts are language-neutral

The EIR, adapter interface, event schema, and provenance schema do not depend on any implementation language. The reference implementation targets one language (ratified by ADR), but every external contract remains language-neutral. PROMETHEUS is a platform, not a language-specific framework.

### 8.8 GENESIS wins

If this package conflicts with `010` or any GENESIS document, GENESIS wins. The package files an ADR or changes its behavior; it never silently overrides. Engineering ADRs and constitutional amendments are two different tracks.

---

## 9. Scope

### 9.1 In scope

- Loading a frozen PKP and validating its constitutional integrity.
- Compiling the PKP into a deterministic EIR.
- Resolving dependencies and resources.
- Building execution timelines and execution graphs.
- Scheduling execution (sequential, parallel, distributed, incremental, checkpoint, resume, retry, selective, partial, conditional).
- Coordinating runtime adapters through a capability registry.
- Tracking runtime state, emitting structured events, handling failures, checkpointing, retrying.
- Producing complete provenance and execution reports for ORACLE and ATLAS.
- A plugin model that makes validators, schedulers, adapters, storage, caches, metrics, and hooks replaceable.
- A CLI, an API, an SDK, a testing framework, and a benchmark framework.

### 9.2 Out of scope

- Creative reasoning, story generation, scene invention, prompt generation, dialogue authoring. Those are GENESIS's job (`005`, `006` L-15).
- Validation that execution matched intent. That is ORACLE's job (`011`).
- Long-term preservation. That is ATLAS's job (`012`).
- Locking the platform to a specific implementation language.

### 9.3 Deferred to later horizons

- Federated / distributed execution across multiple PROMETHEUS instances.
- Real-time / streaming execution (the initial target is batch execution with full provenance).
- Adaptive execution that re-plans mid-run based on adapter feedback.

---

## 10. Non-Goals (Restated from `010`)

PROMETHEUS does **not**:

- Write stories, invent scenes, generate prompts, or create dialogue.
- Perform creative reasoning or replace the Creative Mind (`005`).
- Replace GENESIS, ORACLE, or ATLAS.
- Make creative decisions when the PKP is silent — it reports a rendering gap (`010` §8.3).
- Depend on a specific implementation language, OS, cloud, or hardware.
- Become a prototype that turns into production by accident.

---

## 11. ADR Candidates Surfaced

This DESIGN doc surfaces the following ADR candidates (to be filed in `DECISIONS/001-vision-adr-candidates.md` during Phase 2):

| Candidate | Decision | Blocking milestone |
|---|---|---|
| 0001 | Implementation language for the reference implementation | M0 |
| 0002 | Concurrency model (threads / actors / async / mixed) | M0 |
| 0003 | EIR serialization format (JSON / MessagePack / Protobuf / custom) | M0 |
| 0004 | Workspace location for the reference implementation | M0 |
| 0005 | Network access definition (loopback policy, sandbox boundary) | M0 |
| 0006 | Determinism tolerance (byte-identical vs hash-identical) | M0 |
| 0007 | Recorded-output policy (when to record; storage budget) | M2 |
| 0008 | Cache sharing across executions | M1 |
| 0009 | Provenance compaction for long productions | M4 |
| 0010 | Adapter failure boundary definition (exception / timeout / bad output) | M2 |

Each candidate has a clear recommendation in this document; ratification is expected to be quick.

---

## 12. Cross-References

| Reference | Relevance |
|---|---|
| `010 — PROMETHEUS Runtime Architecture.md` | Canonical constitutional architecture; this document derives from it. |
| `006` (Constitution) | L-14, L-15, L-18 govern the runtime. |
| `009` (PKP) | The runtime's input contract. |
| `011` (ORACLE) | Validates the runtime's output. |
| `012` (ATLAS) | Preserves the runtime's output and execution report. |
| `gkc/DESIGN/001-vision.md` | Sibling product's vision doc; the pattern this document follows. |

---

**End of PROMETHEUS-001.**