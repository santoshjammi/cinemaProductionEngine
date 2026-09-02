# PROMETHEUS Vision

## Why PROMETHEUS Exists

Intent without execution is prose. The GENESIS constitutional stack (`000`–`018`) defines, with engineering precision, what a creative work *should be*. The PKP (`009`) compiles that intent into a frozen, executable specification. But a specification that is never executed is still prose — it just wears a schema. The gap between *what the PKP declares* and *what the runtime actually produces* is where every failure mode of long-lived creative pipelines lives: silent drift, untraceable outputs, unreproducible renders, lost provenance, and the slow erosion of intent under the pressure of "just ship it."

PROMETHEUS exists to **close that gap by execution**.

It treats a PKP not as a checklist, but as a **program** — a deterministic specification that can be loaded, compiled into an Execution Intermediate Representation (EIR), scheduled, executed through replaceable adapters, observed event-by-event, recovered from failure, and emitted as fully-provenanced outputs. Those outputs become the substrate that ORACLE validates and ATLAS preserves.

---

## Why Execution Must Be a Compilation

PROMETHEUS is a **compiler of intent into work** because the alternatives fail in characteristic ways:

| Alternative | Failure mode PROMETHEUS avoids |
|---|---|
| A pipeline script | Scripts couple intent to execution order; they cannot be re-planned, re-scheduled, or re-executed against a different adapter set. PROMETHEUS compiles the PKP into an EIR that any adapter can consume. |
| An orchestrator | Orchestrators decide *how* to run things; they drift from intent. PROMETHEUS decides only *how to execute what was declared*; it never invents steps. |
| A job runner | Job runners track jobs but not provenance. PROMETHEUS produces a complete execution report and event stream traceable to every PKP artifact. |
| An agent loop | Agent loops are non-deterministic. PROMETHEUS is deterministic: same PKP + same adapter versions ⇒ same outputs. |
| A monolithic runtime | Monoliths couple the engine to the adapters. PROMETHEUS is adapter-pluggable: the engine is unchanged when providers are swapped. |

The compiler framing buys four properties that no other framing gives together:

1. **Determinism** — same inputs ⇒ same outputs, byte-identical (or hash-identical, with the recorded-output fallback for irreducibly non-deterministic providers, per `010` §9.3).
2. **Staging** — PKP → EIR → Schedule → Execute → Emit is a sequence of typed stages; each stage's output is the next stage's input.
3. **Resumability** — a checkpoint at any stage can resume without recomputing prior stages.
4. **Adapter independence** — adapters consume the EIR; they never touch the PKP. The EIR is the execution contract.

These are not aspirations. They are invariants (see `DESIGN/001`).

---

## What "Executing" a PKP Means

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

Every execution step emits a structured event with: timestamp, duration, inputs, outputs, dependencies, adapter metrics, resource usage, diagnostics, and provenance. No silent execution is permitted (`010` §5, and the observability rules in this package). The event stream is the basis for the execution report.

**Definition:** A PKP is *fully executed* iff all five closures hold. A PKP is *partially executed* iff at least one closure is incomplete; in that case, PROMETHEUS emits a diagnostic set and a partial execution report, never a silent failure (`010` §8.4).

---

## Relationship to GENESIS

GENESIS documents `000`–`018` are the **constitutional source of truth**. PROMETHEUS's job is not to interpret GENESIS freely; PROMETHEUS's job is to **execute the PKP that GENESIS compiled**, within the constraints GENESIS fixed.

| If PROMETHEUS behavior... | Then... |
|---|---|
| Aligns with a GENESIS document | Proceed. |
| Conflicts with a GENESIS document | PROMETHEUS emits a constitutional violation diagnostic; it does not silently override. |
| Is silent where GENESIS specifies | PROMETHEUS treats the GENESIS rule as an invariant and codifies it in the constitutional validator (see `DESIGN/010`). |
| Specifies where GENESIS is silent | PROMETHEUS files an ADR (`DECISIONS/`) for ratification. |

PROMETHEUS does not amend GENESIS. PROMETHEUS's evolution is constrained by GENESIS until GENESIS itself is amended through its own governance process. Where the constitutional architecture in `010` is found to be incomplete, the gap is closed by **constitutional revision or ADR** — never by silently overriding the architecture.

---

## Relationship to the Other Pillars

| Pillar | Relationship |
|---|---|
| **GENESIS** | Defines intent. PROMETHEUS executes intent. GENESIS is the authority; PROMETHEUS is the executor. |
| **ORACLE** | Verifies that PROMETHEUS's output matched the PKP's intent. PROMETHEUS does not call ORACLE directly (`010` §6.3); the contract is mediated by ATLAS. |
| **ATLAS** | Preserves the PKP, PROMETHEUS's outputs, and the execution report. PROMETHEUS reads the PKP from ATLAS and writes outputs + reports to ATLAS. |

The four pillars are deliberately decoupled. PROMETHEUS never calls GENESIS, ORACLE, or the human during execution (`010` §6.2). All cross-pillar interaction is mediated by ATLAS. This keeps the runtime a pure executor and makes the entire pipeline auditable from ATLAS alone.

---

## Why PROMETHEUS Is a Platform, Not a Framework

A framework is something you build *on*. A platform is something you build *for*. PROMETHEUS is a platform: its contracts (EIR, events, adapter interface, provenance schema) are stable surfaces that other systems target. The contracts are language-neutral so that an adapter can be written in any language, an EIR can be consumed by any runtime, and an SDK can be emitted for any host environment.

| Layer | Language-neutral? | Defined where? |
|---|---|---|
| PKP input | Yes (`009`) | GENESIS |
| EIR | Yes | `DESIGN/004` (this package) |
| Adapter interface | Yes | `DESIGN/006` (this package) |
| Event schema | Yes | `DESIGN/008` (this package) |
| Provenance schema | Yes | `DESIGN/013` (this package) |
| CLI / API / SDK | Yes (the contract); the reference CLI/SDK targets one language (ADR) | `DESIGN/009`, `DESIGN/010` |

The reference implementation targets one language (ratified by ADR), but every external contract remains language-neutral. PROMETHEUS is therefore a platform, not a language-specific framework.

---

## Scope

### In scope

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

### Out of scope

- Creative reasoning, story generation, scene invention, prompt generation, dialogue authoring. Those are GENESIS's job (`005`, `006` L-15).
- Validation that execution matched intent. That is ORACLE's job (`011`).
- Long-term preservation. That is ATLAS's job (`012`).
- Locking the platform to a specific implementation language. The reference implementation is one of many possible implementations.

### Deferred to later horizons

- Federated / distributed execution across multiple PROMETHEUS instances (cross-runtime coordination).
- Real-time / streaming execution (the initial target is batch execution with full provenance).
- Adaptive execution that re-plans mid-run based on adapter feedback (the initial scheduler is static-plan; adaptive scheduling is a later milestone).

---

## Philosophy

The philosophy that constrains every DESIGN doc in this package:

1. **Execution, not creation.** PROMETHEUS executes what GENESIS declares. It never invents (`010` §1.2, `006` L-15).
2. **Determinism is constitutional.** Given the same PKP and the same adapter versions, PROMETHEUS produces the same outputs. Determinism is the final link in the platform's deterministic replay chain (`010` §1.3, `006` L-14).
3. **Diagnostics over silence.** Every failure, gap, fallback, and skip is reported loudly (`010` §8.4, `00` §3.7). PROMETHEUS never silently produces broken outputs.
4. **Provenance is non-negotiable.** Every output carries full provenance (`010` §2.4). An output without provenance is not a PROMETHEUS output.
5. **Adapters are replaceable; the engine is not.** The runtime core is stable; adapters, validators, schedulers, storage, and caches are plugins (`010` §10).
6. **Local-first, cloud-capable.** The default configuration uses local adapters; cloud adapters are opt-in behind the same capability interface (`010` §11.2, `00` §3.4).
7. **Contracts are language-neutral.** The EIR, adapter interface, event schema, and provenance schema do not depend on any implementation language.
8. **GENESIS wins.** If this package conflicts with `010` or any GENESIS document, GENESIS wins. The package files an ADR or changes its behavior; it never silently overrides.

---

## Success Conditions

PROMETHEUS is successful when, for **any** PKP from **any** domain that conforms to the PKP contract (`009`):

| # | Condition | Measurable as |
|---|---|---|
| S1 | The PKP compiles to a complete EIR. | Every PKP artifact maps to ≥1 EIR node; the EIR dependency graph is acyclic. |
| S2 | The EIR executes under any compliant adapter set. | A second adapter set (e.g., a stub adapter) produces a complete execution report. |
| S3 | Execution is reproducible. | Two executions of the same PKP + same adapter versions produce hash-identical outputs (or recorded-output-identical for non-deterministic providers). |
| S4 | Execution is explainable. | The execution report plus event stream reconstructs every decision the scheduler made. |
| S5 | Execution is resumable. | A checkpoint at any stage resumes without recomputing prior stages; outputs are byte-identical to a no-checkpoint run. |
| S6 | Execution is auditable. | ORACLE can validate outputs against the PKP using only the execution report + provenance. |
| S7 | The engine is adapter-independent. | Swapping an adapter (e.g., image provider A → image provider B) requires no engine code changes; only the registry changes. |
| S8 | The platform is domain-independent. | A non-cinema PKP (e.g., a book, a game level) executes through the same engine with domain-specific adapters. |

S8 is the longest-horizon condition; the initial milestones target cinema but the architecture does not assume cinema.

---

## See Also

- `DESIGN/001-vision.md` — engineering-grade vision (invariants, testable definitions of "understanding").
- `ARCHITECTURE.md` — system map and DESIGN doc index.
- `ROADMAP.md` — milestone plan.
- `010 — PROMETHEUS Runtime Architecture.md` (repo root) — constitutional source of authority.