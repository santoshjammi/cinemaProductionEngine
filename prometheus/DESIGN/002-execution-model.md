# PROMETHEUS-002 — Execution Model

> The universal execution pipeline: how a frozen PKP becomes fully-provenanced outputs. This document defines the *dynamic flow*; the static component inventory is in `DESIGN/003`.

---

## 1. Purpose

Pin down, at engineering precision:

- What are the canonical execution stages, in what order, and why?
- What flows between stages (typed artifacts, not ad-hoc data)?
- What execution modes are supported (sequential, parallel, distributed, incremental, checkpoint, resume, retry, selective, partial, conditional)?
- What is the end-to-end lifecycle of a single EIR node, from scheduler dispatch to emission?
- What is the end-to-end lifecycle of a full execution, from PKP load to execution report?

Every subsequent DESIGN doc that touches flow (`005` pipeline, `006` adapter framework, `011` scheduler, `012` recovery, `013` emission) inherits the commitments made here.

---

## 2. The Universal Execution Pipeline

PROMETHEUS compiles a PKP into executable work through a fixed sequence of stages. The sequence is universal: it applies to any PKP from any domain. Domain-specific behavior lives in the adapters, not in the pipeline.

```
Frozen PKP (009) — read from ATLAS by identity + version
   │
   ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 1 — LOAD                                                     │
│  PKP Loader: verify hash, verify state=frozen, read into memory.     │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ LoadedPKP
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 2 — VALIDATE (CONSTITUTIONAL)                                 │
│  Constitutional Validator: check PKP against GENESIS invariants;    │
│  emit ranked diagnostics.                                           │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ ValidatedPKP (+ diagnostics)
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 3 — RESOLVE DEPENDENCIES                                      │
│  Dependency Resolver: close declared dependencies; surface          │
│  unresolved references as diagnostics.                              │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ DependencyClosedPKP
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 4 — RESOLVE RESOURCES                                         │
│  Resource Resolver: resolve adapter ids, asset refs, seeds,         │
│  configs; resolve to concrete adapter instances via registry.       │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ ResolvedPKP
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 5 — BUILD TIMELINE                                            │
│  Timeline Builder: order work along the PKP's timeline.             │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ Timeline
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 6 — PLAN EXECUTION                                            │
│  Execution Planner: choose components, providers, order,            │
│  fallbacks from the PKP + capability registry.                      │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ ExecutionPlan
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 7 — BUILD EXECUTION GRAPH                                     │
│  Execution Graph Builder: construct the DAG of executable units    │
│  from the plan + timeline.                                           │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ ExecutionGraph
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 8 — EMIT EIR                                                  │
│  Produce the Execution Intermediate Representation — the language-   │
│  neutral execution contract consumed by adapters.                   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ EIR
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 9 — SCHEDULE                                                  │
│  Scheduler: topological dispatch; independent nodes in parallel;   │
│  deterministic merge order.                                          │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ Schedule
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 10 — EXECUTE                                                  │
│  Adapter Framework: dispatch EIR nodes to adapters via the          │
│  capability registry; Runtime State Manager tracks state; Event     │
│  Bus emits structured events.                                       │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ ExecutionEvents + RawOutputs
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 11 — RECOVER (CONTINUOUS)                                     │
│  Failure Recovery Engine: classify failures; apply retry /          │
│  fallback / fatal-termination. Checkpoint Manager persists state.   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ RecoveredOutputs
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 12 — EMIT OUTPUTS                                             │
│  Asset Emission Service: stamp provenance; write outputs to ATLAS. │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ Outputs + Provenance
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 13 — REPORT                                                   │
│  Execution Report Builder: assemble EIR + schedule + events +       │
│  diagnostics + fallbacks + retries + skips + output manifest;       │
│  write to ATLAS.                                                     │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ ExecutionReport
                               ▼
                     ATLAS (012) — preserves outputs + report
                     ORACLE (011) — reads + validates (indirect)
```

### 2.1 Stage contract

Every stage is specified by a five-field contract:

| Field | Definition |
|---|---|
| **Input** | The typed artifact the stage consumes (e.g., `LoadedPKP`). |
| **Output** | The typed artifact the stage produces (e.g., `ValidatedPKP`). |
| **Determinism** | The stage is deterministic: same input + same config + same plugin set ⇒ same output, byte-identical. |
| **Cacheability** | The stage's output is cacheable by `(stage id, input content hash, configuration hash, plugin set hash)`. |
| **Diagnostics** | The stage emits a diagnostic set; diagnostics flow forward with the output. |

A stage never reads from a later stage. A stage never mutates its input (inputs are immutable). A stage never makes a creative decision (`010` §1.2, `006` L-15).

### 2.2 Stage ordering rules

- Stages 1–8 are **eager and deterministic** — they produce the same output for the same input + config + plugin set. They run in strict order; each consumes the prior stage's output.
- Stage 9 (Schedule) is **eager** for the schedule artifact but **lazy** for actual dispatch — the scheduler produces a schedule, then dispatches per the schedule.
- Stage 10 (Execute) is **executing** — timing varies, but outputs are deterministic (same PKP + same adapter versions ⇒ same outputs).
- Stage 11 (Recover) is **continuous** — it interleaves with Stage 10, not runs after it. Checkpointing runs throughout.
- Stages 12–13 are **closing** — they run after execution completes (or after a fatal failure terminates it).

### 2.3 Stage failure rules

- A stage failure emits a diagnostic and, depending on severity, either continues (recoverable), retries (retryable), or terminates (fatal).
- A constitutional-violation diagnostic in Stage 2 is **fatal** — the PKP cannot be executed.
- An unresolved dependency in Stage 3 is **recoverable** if the PKP marks the artifact optional; otherwise it is **fatal** for that artifact (others continue).
- An adapter failure in Stage 10 is classified by the failure recovery engine (Stage 11) — see `DESIGN/012`.

---

## 3. Execution Modes

PROMETHEUS supports the following execution modes. The pipeline is the same in every mode; only the scheduler's dispatch policy and the checkpoint frequency differ.

### 3.1 Sequential execution

Nodes execute one at a time, in topological order. Used for: debugging, deterministic replay, low-resource environments.

### 3.2 Parallel execution

Independent nodes execute concurrently, up to a configurable concurrency limit. Merge order is deterministic (by EIR node id). Used for: default execution mode.

### 3.3 Distributed execution

Nodes execute across multiple worker processes or machines, coordinated by a shared scheduler and a shared event bus. The EIR is the unit of distribution; workers consume EIR slices. Used for: large productions. Deferred to a later horizon per `VISION.md`.

### 3.4 Incremental execution

Only the EIR nodes affected by a PKP change are re-executed; unaffected nodes use cached outputs. "Affected subgraph" is the transitive closure of changed nodes in the EIR dependency graph. Used for: re-rendering after a small PKP edit.

### 3.5 Checkpoint execution

The runtime checkpoints state at every stage (or at a configurable frequency). Checkpoints are content-addressed and resumable. Used for: long productions; unreliable environments.

### 3.6 Resume execution

The runtime resumes from a checkpoint without recomputing prior stages. Resume is byte-identical to a no-checkpoint run (Invariant 7.3). Used for: recovering from a crash; pausing and resuming.

### 3.7 Retry execution

A failed node is retried per the retry strategy (bounded retries, per-failure-class policy). Retries are recorded in the event stream. Used for: transient adapter failures.

### 3.8 Selective execution

The runtime executes a subset of the EIR (e.g., only Scene 3's image realization), specified by a filter. Used for: targeted re-rendering.

### 3.9 Partial execution

The runtime executes as much as possible, marking failed/gapped nodes and continuing. The final assembly is not produced until all required nodes succeed (or the human accepts gaps). Used for: development; debugging.

### 3.10 Conditional execution

A node's execution is gated by a condition expressed in the EIR (e.g., "only render the high-quality version if the cached low-quality version's score is below threshold"). Conditions are PKP-declared, not runtime-invented (`010` §1.2). Used for: quality-gated re-rendering.

---

## 4. EIR Node Lifecycle

A single EIR node moves through the following states during execution:

```
   pending
      │
      │ scheduler dispatches
      ▼
   running ──────┬──────► succeeded ──────► emitted
      │          │
      │          │ retryable failure
      │          ▼
      │       retried ──────► running (retry)
      │
      │ fatal / unrecoverable
      ▼
   failed
      │
      │ PKP marked skipped, or human accepted gap
      ▼
   skipped
```

| State | Meaning |
|---|---|
| `pending` | The node is in the EIR; the scheduler has not dispatched it. |
| `running` | An adapter is executing the node. |
| `retried` | A retryable failure occurred; the node will be re-dispatched per the retry strategy. |
| `succeeded` | The adapter produced a valid output; the output is ready for emission. |
| `failed` | A fatal or unrecoverable failure occurred; the node will not be retried. |
| `skipped` | The PKP marked the artifact `skipped`, or a rendering gap was accepted. |
| `emitted` | The output has been stamped with provenance and written to ATLAS. |

Every state transition emits an event on the event bus (`DESIGN/008`). The runtime state manager tracks the current state of every node (`DESIGN/012`).

---

## 5. Full Execution Lifecycle

A full execution moves through the following phases:

### 5.1 Setup

- Load the PKP (Stage 1).
- Validate constitutionally (Stage 2).
- Resolve dependencies and resources (Stages 3–4).
- Build the timeline, plan, graph, and EIR (Stages 5–8).

Setup is **eager and deterministic**: the same PKP + same adapter versions + same config ⇒ the same EIR, byte-identical.

### 5.2 Schedule

- Compute the schedule (Stage 9).

The schedule is **eager and deterministic**: the same EIR + same scheduler config ⇒ the same schedule.

### 5.3 Execute

- Dispatch nodes per the schedule (Stage 10).
- Recover from failures (Stage 11, continuous).
- Checkpoint state (continuous).

Execution is **deterministic in output, variable in timing**: the same EIR + same adapter versions ⇒ the same outputs, but wall-clock duration varies.

### 5.4 Emit

- Stamp provenance (Stage 12).
- Write outputs to ATLAS.
- Assemble the execution report (Stage 13).
- Write the report to ATLAS.

Emission is **deterministic**: the same outputs + same provenance schema ⇒ the same emission, byte-identical.

### 5.5 Close

- Finalize the execution report.
- Exit 0 on success; exit non-zero on any unrecoverable failure or constitutional violation.

---

## 6. Determinism Across the Pipeline

Determinism is the runtime's constitutional obligation (`010` §1.3, `006` L-14). The pipeline preserves determinism as follows:

| Stage | Determinism mechanism |
|---|---|
| Load | Hash verification; state verification. |
| Validate | Pure function of PKP + invariants. |
| Resolve Deps | Pure function of PKP + registry. |
| Resolve Res | Pure function of PKP + capability registry. |
| Timeline | Deterministic order by PKP timeline + node id. |
| Plan | Pure function of PKP + capability registry. |
| Build Graph | Deterministic topological construction. |
| Emit EIR | Pure function of the graph; byte-stable serialization. |
| Schedule | Topological order by EIR node id; deterministic merge. |
| Execute | Seed-based reproducibility for deterministic providers; recorded-output fallback for non-deterministic providers (`010` §9.3). |
| Recover | Deterministic retry policy; deterministic fallback selection. |
| Emit Outputs | Pure function of outputs + provenance schema. |
| Report | Pure function of EIR + schedule + events + diagnostics. |

Non-deterministic inputs (timestamps, wall-clock durations, OS scheduling) are **normalized** before they affect output identity:

- Timestamps are recorded in events but do not enter output hashes.
- Durations are recorded in metrics but do not enter output hashes.
- Walk order is determined by EIR node id (lexicographic), not by OS scheduling.
- Parallel merge order is by EIR node id, not by completion order.

---

## 7. Observability Across the Pipeline

Every stage emits structured events (`DESIGN/008`). No silent execution is permitted (Invariant 7.5). Each event carries:

| Field | Definition |
|---|---|
| `event_id` | Unique, deterministic (stage id + node id + sequence). |
| `timestamp` | Wall-clock time (recorded, not used in hashes). |
| `stage_id` | The stage that emitted the event. |
| `node_id` | The EIR node the event concerns (if any). |
| `type` | The event type (stage-start, node-dispatch, node-succeed, node-fail, etc.). |
| `duration_ms` | Wall-clock duration (recorded, not used in hashes). |
| `inputs` | References to input artifacts (by hash). |
| `outputs` | References to output artifacts (by hash). |
| `dependencies` | References to dependency node ids. |
| `adapter_metrics` | Per-adapter metrics (if any). |
| `resource_usage` | CPU, memory, GPU (if any). |
| `diagnostics` | Diagnostics emitted by this event (if any). |
| `provenance` | Provenance stub (full provenance assembled at emission). |

The event stream is the basis for the execution report (`DESIGN/013`).

---

## 8. Failure Modes Across the Pipeline

| Stage | Failure class | Recovery |
|---|---|---|
| Load | Constitutional (hash mismatch, wrong state) | Fatal; emit `constitutional-violation`. |
| Validate | Constitutional (invariant violation) | Fatal; emit `constitutional-violation`. |
| Resolve Deps | Dependency (unresolved reference) | Recoverable if optional; fatal for the artifact if required. |
| Resolve Res | Resource (unresolved adapter/asset/seed) | Recoverable with fallback; fatal if no fallback. |
| Build Graph | Structural (dependency cycle) | Fatal; emit `dependency-cycle`. |
| Emit EIR | Structural (serialization failure) | Fatal; emit `eir-serialization-error`. |
| Schedule | Configuration (invalid policy) | Fatal; emit `scheduler-config-error`. |
| Execute | Adapter (exception, timeout, bad output) | Retryable or recoverable with fallback; fatal if unrecoverable. |
| Execute | Resource (OOM, GPU unavailable) | Recoverable with serialization; fatal if persistent. |
| Recover | Infrastructure (checkpoint write failure) | Retryable; fatal if persistent. |
| Emit Outputs | Constitutional (provenance missing) | Fatal; emit `provenance-violation`. |
| Report | Infrastructure (ATLAS write failure) | Retryable; fatal if persistent. |

Failure classification and recovery strategies are specified in `DESIGN/012`.

---

## 9. What This Document Does Not Define

- The EIR schema itself — that is `DESIGN/004`.
- The adapter interface — that is `DESIGN/006`.
- The scheduler's internal algorithm — that is `DESIGN/011`.
- The failure recovery engine's classification logic — that is `DESIGN/012`.
- The event schema's full field set — that is `DESIGN/008`.
- The provenance schema — that is `DESIGN/013`.

This document defines how the stages fit together and what flows between them. The internals of each stage are in the per-subsystem DESIGN docs.

---

## 10. ADR Candidates Surfaced

| Candidate | Decision | Blocking milestone |
|---|---|---|
| 0011 | Stage cache granularity (per-stage vs per-node) | M1 |
| 0012 | Default concurrency limit | M2 |
| 0013 | Distributed execution protocol (deferred; record the decision now) | M5+ |
| 0014 | Conditional execution expression in the EIR | M5 |
| 0015 | Selective execution filter syntax | M2 |

---

## 11. Cross-References

| Reference | Relevance |
|---|---|
| `010` §2 (Execution Model) | Constitutional execution model; this document is its engineering realization. |
| `009` (PKP) | The runtime's input. |
| `DESIGN/003` | Component architecture (static). |
| `DESIGN/004` | EIR (the execution contract). |
| `DESIGN/005` | Pipeline (stage contract details). |
| `DESIGN/006` | Adapter framework. |
| `DESIGN/008` | Event bus (event schema). |
| `DESIGN/011` | Scheduler. |
| `DESIGN/012` | Failure recovery + checkpoint. |
| `DESIGN/013` | Asset emission + provenance. |

---

**End of PROMETHEUS-002.**