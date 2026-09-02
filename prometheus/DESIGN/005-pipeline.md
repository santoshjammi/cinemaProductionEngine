# PROMETHEUS-005 — Pipeline & Compilation

> The canonical pipeline: stages, stage contracts, determinism, incrementality, caching, and the compilation path from PKP to EIR. This document defines the *how* of the pipeline; the *what flows* is in `DESIGN/002`.

---

## 1. Purpose

Define, at engineering precision:

- The canonical stage list and order.
- The stage contract (inputs, outputs, determinism, cacheability, diagnostics).
- How stages compose (strict order, typed artifacts, immutable inputs).
- How determinism is preserved across stages.
- How incrementality works (affected subgraph re-execution).
- How caching works (stage-level and node-level).
- How diagnostics flow forward.

Every subsystem that participates in a stage (S2–S23) inherits the commitments made here.

---

## 2. The Canonical Pipeline

The pipeline is a fixed sequence of 14 stages. The sequence is universal; it applies to any PKP from any domain.

```
 1. Load         — PKP Loader (S2)
 2. Validate     — Constitutional Validator (S3)
 3. Resolve Deps — Dependency Resolver (S4)
 4. Resolve Res  — Resource Resolver (S5)
 5. Timeline     — Timeline Builder (S6)
 6. Plan         — Execution Planner (S7)
 7. Build Graph  — Execution Graph Builder (S8)
 8. Emit EIR     — EIR (S9)
 9. Schedule     — Scheduler (S10)
10. Execute      — Adapter Framework (S13) + State Manager (S11) + Event Bus (S12)
11. Recover      — Failure Recovery (S16) + Retry (S17) + Checkpoint (S18)  [continuous]
12. Emit Outputs — Asset Emission (S23)
13. Report       — Report Builder (S23)
```

Stage 11 is **continuous**: it interleaves with Stage 10, not runs after it. Stages 1–8 are **eager and deterministic**. Stage 9 is **eager** for the schedule. Stage 10 is **executing**. Stages 12–13 are **closing**.

---

## 3. Stage Contract

Every stage is specified by a five-field contract (restated from `DESIGN/002` §2.1 with full detail here):

### 3.1 Fields

| Field | Definition |
|---|---|
| **Stage id** | A stable string (e.g., `"load"`, `"validate"`, `"emit-eir"`). |
| **Input** | The typed artifact the stage consumes. Immutable. |
| **Output** | The typed artifact the stage produces. Immutable. |
| **Determinism** | The stage is a pure function: same input + same config + same plugin set + same compiler version ⇒ same output, byte-identical. |
| **Cacheability** | The stage's output is cacheable by `(stage id, input content hash, configuration hash, plugin set hash, compiler version)`. |
| **Diagnostics** | The stage emits a diagnostic set; diagnostics flow forward with the output. |
| **Failure policy** | The stage's behavior on failure (fatal / recoverable / retryable). |

### 3.2 Stage rules

- A stage **never** reads from a later stage.
- A stage **never** mutates its input (inputs are immutable).
- A stage **never** makes a creative decision (L-15).
- A stage **never** calls GENESIS, ORACLE, or the human.
- A stage **never** writes to ATLAS (except the Asset Emission Service, S23, in Stages 12–13).
- A stage **always** emits at least one event (no silent execution, Invariant 7.5).
- A stage **always** emits diagnostics for any anomaly (no silent drops, Invariant 7.5).

### 3.3 Stage artifacts

The typed artifacts that flow between stages:

| Artifact | Producer | Consumer | Contents |
|---|---|---|---|
| `LoadedPKP` | Load | Validate | pkp_id, pkp_hash, pkp_version, state, artifacts |
| `ValidatedPKP` | Validate | Resolve Deps | pkp, diagnostics (ranked) |
| `DependencyClosedPKP` | Resolve Deps | Resolve Res | pkp, resolved dependencies, diagnostics |
| `ResolvedPKP` | Resolve Res | Timeline | pkp, resolved adapters/assets/seeds/configs, diagnostics |
| `Timeline` | Timeline | Plan | ordered work units |
| `ExecutionPlan` | Plan | Build Graph | components, providers, order, fallbacks |
| `ExecutionGraph` | Build Graph | Emit EIR | DAG of executable units |
| `EIR` | Emit EIR | Schedule, Adapters, Report | the execution contract (`DESIGN/004`) |
| `Schedule` | Schedule | Execute | topological dispatch plan |
| `ExecutionEvents` | Execute | Recover, Report | structured event stream |
| `RawOutputs` | Execute | Emit Outputs | outputs + provenance stubs |
| `RecoveredOutputs` | Recover | Emit Outputs | outputs (post-retry/fallback) |
| `Outputs` | Emit Outputs | Report | outputs + provenance + ATLAS refs |
| `ExecutionReport` | Report | ATLAS, ORACLE | EIR + schedule + events + diagnostics + output manifest |

---

## 4. Stage Specifications

### 4.1 Stage 1 — Load

| Field | Value |
|---|---|
| Stage id | `load` |
| Input | `PKPId` (the PKP's identity in ATLAS) |
| Output | `LoadedPKP` |
| Determinism | Pure function of pkp_id + ATLAS state. Hash-verified. |
| Cacheability | Cache by `(pkp_id, pkp_version)`. |
| Diagnostics | `constitutional-violation` (hash mismatch, wrong state). |
| Failure policy | Constitutional violations are fatal. |

The loader verifies the PKP hash matches the declared hash and the PKP state is `frozen`. Mismatches emit `constitutional-violation` and terminate.

### 4.2 Stage 2 — Validate

| Field | Value |
|---|---|
| Stage id | `validate` |
| Input | `LoadedPKP` |
| Output | `ValidatedPKP` |
| Determinism | Pure function of pkp + invariant set + compiler version. |
| Cacheability | Cache by `(pkp hash, invariant set hash, compiler version)`. |
| Diagnostics | `constitutional-violation` (L-14, L-15, L-18 violations); `pkp-completeness` (missing required fields). |
| Failure policy | Constitutional violations are fatal. Completeness violations are fatal for the affected artifact. |

The validator checks the PKP against the codified invariant set (`IMPLEMENTATION/invariants.md`). Diagnostics are ranked (S21) and flow forward.

### 4.3 Stage 3 — Resolve Dependencies

| Field | Value |
|---|---|
| Stage id | `resolve-deps` |
| Input | `ValidatedPKP` |
| Output | `DependencyClosedPKP` |
| Determinism | Pure function of pkp + registry. |
| Cacheability | Cache by `(pkp hash, registry hash)`. |
| Diagnostics | `unresolved-reference` (recoverable if optional, fatal if required); `dependency-cycle` (fatal). |
| Failure policy | Unresolved required references are fatal for the artifact; optional references are recoverable (the artifact is skipped). |

The resolver closes the PKP's declared dependencies. Cycles emit `dependency-cycle` and terminate the affected subgraph.

### 4.4 Stage 4 — Resolve Resources

| Field | Value |
|---|---|
| Stage id | `resolve-res` |
| Input | `DependencyClosedPKP` |
| Output | `ResolvedPKP` |
| Determinism | Pure function of pkp + capability registry + config. |
| Cacheability | Cache by `(pkp hash, capability registry hash, config hash)`. |
| Diagnostics | `unresolved-adapter`, `unresolved-asset`, `unresolved-seed`, `unresolved-config`. |
| Failure policy | Unresolved resources with fallbacks are recoverable; unresolved resources without fallbacks are fatal for the artifact. |

The resolver resolves adapter identities to concrete adapter instances via the capability registry (S13), asset references to concrete assets, seeds, and configs.

### 4.5 Stage 5 — Timeline

| Field | Value |
|---|---|
| Stage id | `timeline` |
| Input | `ResolvedPKP` |
| Output | `Timeline` |
| Determinism | Pure function of resolved pkp; order by PKP timeline + node id. |
| Cacheability | Cache by `(resolved pkp hash)`. |
| Diagnostics | `timeline-conflict` (if the PKP timeline has contradictions). |
| Failure policy | Timeline conflicts are fatal. |

The timeline builder orders work along the PKP's declared timeline. The order is deterministic (by PKP-declared order, then by node id for ties).

### 4.6 Stage 6 — Plan

| Field | Value |
|---|---|
| Stage id | `plan` |
| Input | `Timeline` + `CapabilityRegistry` |
| Output | `ExecutionPlan` |
| Determinism | Pure function of timeline + capability registry + config. |
| Cacheability | Cache by `(timeline hash, capability registry hash, config hash)`. |
| Diagnostics | `planning-conflict`, `no-provider-available`. |
| Failure policy | No-provider-available with fallback is recoverable; without fallback is fatal. |

The planner chooses rendering components, providers, execution order, and fallbacks from the PKP + capability registry. It does not make creative decisions (L-15); it projects the PKP's declared choices.

### 4.7 Stage 7 — Build Graph

| Field | Value |
|---|---|
| Stage id | `build-graph` |
| Input | `ExecutionPlan` |
| Output | `ExecutionGraph` |
| Determinism | Pure function of plan. Deterministic topological construction. |
| Cacheability | Cache by `(plan hash)`. |
| Diagnostics | `dependency-cycle` (fatal). |
| Failure policy | Cycles are fatal. |

The graph builder constructs the DAG of executable units from the plan + timeline.

### 4.8 Stage 8 — Emit EIR

| Field | Value |
|---|---|
| Stage id | `emit-eir` |
| Input | `ExecutionGraph` |
| Output | `EIR` (per `DESIGN/004`) |
| Determinism | Pure function of graph. Byte-stable serialization. |
| Cacheability | Cache by `(graph hash, eir schema version, compiler version)`. |
| Diagnostics | `eir-serialization-error` (fatal). |
| Failure policy | Serialization errors are fatal. |

The EIR is emitted in the language-neutral serialization (per ADR 0003). The EIR is immutable from this point.

### 4.9 Stage 9 — Schedule

| Field | Value |
|---|---|
| Stage id | `schedule` |
| Input | `EIR` + `SchedulerConfig` |
| Output | `Schedule` |
| Determinism | Pure function of EIR + config. Topological order by node id; deterministic merge. |
| Cacheability | Cache by `(eir hash, scheduler config hash)`. |
| Diagnostics | `scheduler-config-error` (fatal). |
| Failure policy | Config errors are fatal. |

The scheduler computes the topological dispatch order. Independent nodes are grouped for parallel execution; merge order is by node id.

### 4.10 Stage 10 — Execute

| Field | Value |
|---|---|
| Stage id | `execute` |
| Input | `Schedule` + `EIR` |
| Output | `ExecutionEvents` + `RawOutputs` |
| Determinism | Deterministic in output (same EIR + same adapter versions ⇒ same outputs); variable in timing. |
| Cacheability | Per-node cache by `(node hash, adapter id, adapter version, seed, config hash)`. |
| Diagnostics | `adapter-failure`, `validation-failure`, `rendering-gap`, `resource-exhausted`. |
| Failure policy | Per-failure-class (see `DESIGN/012`). |

The adapter framework dispatches EIR nodes to adapters. The runtime state manager tracks state. The event bus emits events. Failures are classified by the failure recovery engine (Stage 11).

### 4.11 Stage 11 — Recover (continuous)

| Field | Value |
|---|---|
| Stage id | `recover` |
| Input | `ExecutionEvents` (continuous) |
| Output | `RecoveredOutputs` |
| Determinism | Deterministic retry/fallback policy. |
| Cacheability | Per-node (retry results are cached as new outputs). |
| Diagnostics | `retry-exhausted`, `fallback-used`, `fatal-failure`. |
| Failure policy | Per-failure-class (see `DESIGN/012`). |

The failure recovery engine classifies failures and applies retry, fallback, or fatal-termination. The checkpoint manager persists state continuously.

### 4.12 Stage 12 — Emit Outputs

| Field | Value |
|---|---|
| Stage id | `emit-outputs` |
| Input | `RecoveredOutputs` |
| Output | `Outputs` (+ provenance + ATLAS refs) |
| Determinism | Pure function of outputs + provenance schema. |
| Cacheability | Cache by `(output hash, provenance schema hash)`. |
| Diagnostics | `provenance-violation` (fatal — missing provenance). |
| Failure policy | Provenance violations are fatal (Invariant 7.9). |

The asset emission service stamps every output with provenance and writes to ATLAS.

### 4.13 Stage 13 — Report

| Field | Value |
|---|---|
| Stage id | `report` |
| Input | `EIR` + `Schedule` + `ExecutionEvents` + `Diagnostics` + `Outputs` |
| Output | `ExecutionReport` |
| Determinism | Pure function of inputs. Byte-stable serialization. |
| Cacheability | Cache by `(eir hash, schedule hash, event set hash, output set hash)`. |
| Diagnostics | `report-assembly-error` (fatal). |
| Failure policy | Assembly errors are fatal. |

The report builder assembles the execution report and writes it to ATLAS. The report is the basis for ORACLE's validation.

---

## 5. Determinism Across Stages

Determinism is preserved stage-by-stage (per `DESIGN/002` §6):

| Stage | Determinism mechanism |
|---|---|
| Load | Hash verification; state verification. |
| Validate | Pure function of PKP + invariants. |
| Resolve Deps | Pure function of PKP + registry. |
| Resolve Res | Pure function of PKP + capability registry + config. |
| Timeline | Deterministic order by PKP timeline + node id. |
| Plan | Pure function of timeline + capability registry + config. |
| Build Graph | Deterministic topological construction. |
| Emit EIR | Pure function of graph; byte-stable serialization. |
| Schedule | Topological order by node id; deterministic merge. |
| Execute | Seed-based reproducibility; recorded-output fallback. |
| Recover | Deterministic retry/fallback policy. |
| Emit Outputs | Pure function of outputs + provenance schema. |
| Report | Pure function of inputs; byte-stable serialization. |

Non-deterministic inputs (timestamps, durations, walk order) are normalized: timestamps are recorded but do not enter hashes; walk order is by node id; merge order is by node id.

---

## 6. Incrementality

Incrementality is the property that a small PKP change re-runs only the affected subgraph of stages and nodes.

### 6.1 Affected subgraph

Given a PKP change, the **affected subgraph** is:

- The changed PKP artifacts.
- All EIR nodes that depend (transitively) on the changed artifacts.
- All stages that produced artifacts in the affected subgraph.

Stages and nodes outside the affected subgraph use cached outputs.

### 6.2 Incremental re-execution

The runtime recomputes:

- Stages 2–8 for the affected subgraph (validate, resolve, timeline, plan, build graph, emit EIR for the affected nodes only).
- Stage 9 (schedule) for the affected nodes.
- Stage 10 (execute) for the affected nodes only; unaffected nodes use cached outputs.
- Stages 12–13 (emit, report) for the affected outputs and the updated report.

Incremental re-execution produces byte-identical outputs to a full re-execution (for the unaffected nodes, the cached outputs are reused; for the affected nodes, the outputs are recomputed and match a full re-execution's outputs).

### 6.3 Incrementality test

`gold/incremental-harness`:

- Execute a golden PKP; record outputs.
- Modify one PKP artifact; re-execute incrementally.
- Assert the affected nodes' outputs match a full re-execution.
- Assert the unaffected nodes' outputs are byte-identical to the prior run (cache hit).
- Assert the wall-clock time is proportional to the affected subgraph size, not the full EIR.

---

## 7. Caching

### 7.1 Stage-level cache

Each stage's output is cacheable by `(stage id, input content hash, configuration hash, plugin set hash, compiler version)`. A cache hit reuses the output; a cache miss recomputes.

The stage-level cache is **deterministic**: a cache hit is byte-identical to a recompute.

### 7.2 Node-level cache (execution)

Each executable node's output is cacheable by `(node hash, adapter id, adapter version, seed, config hash)`. A cache hit reuses the output; a cache miss invokes the adapter.

The node-level cache is **deterministic**: a cache hit is byte-identical (or recorded-output-identical) to a re-invoke.

### 7.3 Cache invalidation

A change in any key component invalidates the cache entry for that node only; other entries are unaffected. Cache invalidation is automatic; no manual invalidation is required.

### 7.4 Cache storage

The stage-level cache is stored locally (per `DECISIONS/0008`). The node-level cache is stored locally and/or in ATLAS (per ADR). The cache is a cache, not a source of truth; the PKP is the source of truth.

---

## 8. Diagnostics Flow

Diagnostics flow forward with the stage output:

- Stage 2 (Validate) emits `constitutional-violation`, `pkp-completeness`.
- Stage 3 (Resolve Deps) emits `unresolved-reference`, `dependency-cycle`.
- Stage 4 (Resolve Res) emits `unresolved-adapter`, `unresolved-asset`.
- Stage 10 (Execute) emits `adapter-failure`, `validation-failure`, `rendering-gap`, `resource-exhausted`.
- Stage 11 (Recover) emits `retry-exhausted`, `fallback-used`, `fatal-failure`.
- Stage 12 (Emit) emits `provenance-violation`.

All diagnostics are ranked (S21) and included in the execution report. No silent execution is permitted (Invariant 7.5).

---

## 9. Checkpointing Across Stages

The checkpoint manager (S18) persists state at every stage (or at a configurable frequency). A checkpoint is content-addressed and resumable.

- A checkpoint after Stage 8 (Emit EIR) allows resume from scheduling without recomputing stages 1–8.
- A checkpoint during Stage 10 (Execute) allows resume from the last completed node without recomputing succeeded nodes.
- A checkpoint after Stage 12 (Emit) allows resume of the report without recomputing emission.

Resume is byte-identical to a no-checkpoint run (Invariant 7.3). See `DESIGN/012` for the checkpoint protocol.

---

## 10. What This Document Does Not Define

- The EIR schema — that is `DESIGN/004`.
- The adapter interface — that is `DESIGN/006`.
- The scheduler's algorithm — that is `DESIGN/011`.
- The failure classification logic — that is `DESIGN/012`.
- The event schema — that is `DESIGN/008`.
- The provenance schema — that is `DESIGN/013`.

This document defines the pipeline's structure and contracts. The internals of each stage are in the per-subsystem DESIGN docs.

---

## 11. ADR Candidates Surfaced

| Candidate | Decision | Blocking milestone |
|---|---|---|
| 0025 | Stage cache backend (local disk / ATLAS / distributed) | M1 |
| 0026 | Node cache backend (local / ATLAS) | M1 |
| 0027 | Checkpoint frequency (every stage / configurable / time-based) | M2 |
| 0028 | Incremental re-planning trigger (always / on significant change) | M1 |
| 0029 | Diagnostic deduplication across stages | M1 |

---

## 12. Cross-References

| Reference | Relevance |
|---|---|
| `010` §2 (Execution Model) | Constitutional execution model. |
| `DESIGN/002` | Execution model (dynamic flow). |
| `DESIGN/003` | Component architecture (subsystems per stage). |
| `DESIGN/004` | EIR (Stage 8 output). |
| `DESIGN/006` | Adapter framework (Stage 10 executor). |
| `DESIGN/011` | Scheduler (Stage 9). |
| `DESIGN/012` | Recovery + checkpoint (Stage 11). |
| `DESIGN/013` | Asset emission + report (Stages 12–13). |
| `DESIGN/014` | Resource + cache managers. |

---

**End of PROMETHEUS-005.**