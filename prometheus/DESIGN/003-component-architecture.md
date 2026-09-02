# PROMETHEUS-003 — Component Architecture

> Every PROMETHEUS subsystem: its responsibilities, its interfaces, its boundaries with other subsystems. This is the **static architecture**; the dynamic flow is in `DESIGN/002`.

---

## 1. Purpose

Pin down each subsystem of PROMETHEUS as a named, bounded, interface-having unit. After this document, no two DESIGN docs should disagree about what a subsystem does or owns.

This document defines:

- the **subsystem inventory** (what exists),
- each subsystem's **responsibilities** (what it does),
- each subsystem's **interfaces** (what it accepts and produces),
- each subsystem's **boundaries** (what it explicitly does not do),
- the **interaction map** (who calls whom).

Implementation-level details (concrete APIs, data structures, algorithms) live in the per-subsystem DESIGN docs cross-referenced here.

---

## 2. Subsystem Inventory

PROMETHEUS has 30 subsystems, grouped into seven layers. The grouping is organizational, not a runtime hierarchy — all subsystems cooperate inside a single runtime process (or a distributed set of processes in distributed execution mode).

### 2.1 Core layer

| # | Subsystem | Role | DESIGN doc |
|---|---|---|---|
| S1 | Runtime Core | Process boundary; owns the lifecycle; wires subsystems together; hosts the plugin framework | `003` (this doc) |

### 2.2 Loading & validation layer

| # | Subsystem | Role | DESIGN doc |
|---|---|---|---|
| S2 | PKP Loader | Load + hash-verify + state-verify the frozen PKP from ATLAS | `007` |
| S3 | Constitutional Validator | Check PKP against GENESIS invariants; emit ranked diagnostics | `010` |
| S4 | Dependency Resolver | Close declared dependencies; surface unresolved as diagnostics | `005` |
| S5 | Resource Resolver | Resolve adapter identities, asset references, seeds, configs | `005`, `014` |

### 2.3 Planning & compilation layer

| # | Subsystem | Role | DESIGN doc |
|---|---|---|---|
| S6 | Timeline Builder | Order work along the PKP's timeline | `005` |
| S7 | Execution Planner | Choose components, providers, and order from the PKP | `005` |
| S8 | Execution Graph Builder | Build the DAG of executable units | `005` |
| S9 | Execution Intermediate Representation (EIR) | The language-neutral execution contract | `004` |

### 2.4 Scheduling & execution layer

| # | Subsystem | Role | DESIGN doc |
|---|---|---|---|
| S10 | Scheduler | Dispatch EIR nodes (seq/par/dist/retry/selective/conditional) | `011` |
| S11 | Runtime State Manager | Track per-node, per-execution state | `012` |
| S12 | Event Bus | Structured event emission; no silent execution | `008` |
| S13 | Adapter Framework | Capability registry, provider abstraction, adapter lifecycle | `006` |
| S14 | Resource Manager | Compute/memory/concurrency budgets; serialization when needed | `014` |
| S15 | Cache Manager | Cache outputs by (PKP artifact hash, adapter version, seed) | `014` |

### 2.5 Recovery layer

| # | Subsystem | Role | DESIGN doc |
|---|---|---|---|
| S16 | Failure Recovery Engine | Classify failures; apply recovery strategy | `012` |
| S17 | Retry Strategy | Per-failure-class retry policy; bounded retries | `012` |
| S18 | Checkpoint Manager | Persist state for resume; resume from any checkpoint | `012` |

### 2.6 Observability & emission layer

| # | Subsystem | Role | DESIGN doc |
|---|---|---|---|
| S19 | Progress Monitor | Surface execution progress to CLI/API/SDK | `008` |
| S20 | Metrics Engine | Collect per-step, per-adapter, per-resource metrics | `008` |
| S21 | Diagnostics | Rank and group diagnostics; cite violated invariants | `010` |
| S22 | Logging | Structured, leveled, observable logs | `008` |
| S23 | Asset Emission Service | Stamp provenance; write outputs + report to ATLAS | `013` |

### 2.7 Platform layer

| # | Subsystem | Role | DESIGN doc |
|---|---|---|---|
| S24 | Configuration | Profiles, adapter configs, scheduler configs | `009` |
| S25 | Security | Capability policy, secret handling, sandbox boundaries | `015` |
| S26 | Plugin Framework | Load, validate, sandbox, dispatch plugins | `015` |
| S27 | CLI | Stable subcommand surface; automation contract | `009` |
| S28 | API | Programmatic contract (language-neutral) | `010` |
| S29 | SDK | Language bindings; multiple languages later | `010` |
| S30 | Testing Framework | Golden PKPs, regression, correctness, performance | `016` |
| S31 | Benchmark Framework | Performance budgets; reproducible benchmarks | `016` |

### 2.8 Cross-cutting concerns

| # | Concern | Owner | Notes |
|---|---|---|---|
| X1 | Diagnostics | Every subsystem emits; Constitutional Validator ranks | `DESIGN/010` |
| X2 | Provenance | Asset Emission stamps; ATLAS preserves | `DESIGN/013` |
| X3 | Determinism | Every subsystem preserves; seed + recorded-output fallback | `DESIGN/004`, `DESIGN/012` |
| X4 | Observability | Event Bus + Metrics + Logging | `DESIGN/008` |
| X5 | Versioning | Inputs, EIR, adapters, outputs all carry versions | `DESIGN/004`, `DESIGN/013` |

---

## 3. Subsystem Specifications

Each subsystem is specified by a four-field contract: responsibilities, interfaces, boundaries, dependencies.

### S1 — Runtime Core

| Field | Value |
|---|---|
| **Responsibilities** | Own the process lifecycle; wire subsystems together; host the plugin framework; own the event loop; own the configuration root. |
| **Interfaces** | `Runtime(config) → RuntimeHandle`; `RuntimeHandle.run(pkp_id) → ExecutionReport`; `RuntimeHandle.checkpoint() → CheckpointId`; `RuntimeHandle.resume(checkpoint_id) → ExecutionReport`. |
| **Boundaries** | Does not implement any stage logic; does not call adapters directly; does not call GENESIS, ORACLE, or the human. |
| **Dependencies** | All other subsystems (it wires them). |

### S2 — PKP Loader

| Field | Value |
|---|---|
| **Responsibilities** | Read the PKP from ATLAS (or a local path); verify the PKP hash; verify the PKP state is `frozen`; deserialize the PKP into the in-memory PKP model; emit `loaded-pkp` event. |
| **Interfaces** | `Loader.load(pkp_id) → LoadedPKP`; `LoadedPKP` carries: pkp_id, pkp_hash, pkp_version, state, artifacts. |
| **Boundaries** | Does not validate constitutionally (that's S3); does not resolve dependencies (that's S4); does not modify the PKP (L-14). |
| **Dependencies** | ATLAS (read); Configuration (for ATLAS endpoint). |

### S3 — Constitutional Validator

| Field | Value |
|---|---|
| **Responsibilities** | Check the PKP against codified GENESIS invariants; emit ranked diagnostics; classify constitutional violations as fatal. |
| **Interfaces** | `Validator.validate(loaded_pkp) → ValidatedPKP`; `ValidatedPKP` carries: pkp, diagnostics (ranked). |
| **Boundaries** | Does not amend the PKP; does not execute; does not call ORACLE. |
| **Dependencies** | Invariant set (`IMPLEMENTATION/invariants.md`); Diagnostics (S21). |

### S4 — Dependency Resolver

| Field | Value |
|---|---|
| **Responsibilities** | Close the PKP's declared dependencies; resolve references to stable identifiers; surface unresolved references as diagnostics; detect cycles. |
| **Interfaces** | `DepResolver.resolve(validated_pkp) → DependencyClosedPKP`. |
| **Boundaries** | Does not resolve resources (that's S5); does not modify the PKP. |
| **Dependencies** | Registry (for reference targets); Diagnostics (S21). |

### S5 — Resource Resolver

| Field | Value |
|---|---|
| **Responsibilities** | Resolve adapter identities to concrete adapter instances via the capability registry; resolve asset references to concrete assets; resolve seeds; resolve configs. |
| **Interfaces** | `ResResolver.resolve(dep_closed_pkp) → ResolvedPKP`. |
| **Boundaries** | Does not invoke adapters (that's S13); does not modify the PKP. |
| **Dependencies** | Capability Registry (S13); Cache Manager (S15); Diagnostics (S21). |

### S6 — Timeline Builder

| Field | Value |
|---|---|
| **Responsibilities** | Order work along the PKP's declared timeline; produce a Timeline artifact. |
| **Interfaces** | `TimelineBuilder.build(resolved_pkp) → Timeline`. |
| **Boundaries** | Does not choose providers (that's S7); does not schedule (that's S10). |
| **Dependencies** | ResolvedPKP (input). |

### S7 — Execution Planner

| Field | Value |
|---|---|
| **Responsibilities** | Choose rendering components, providers, execution order, and fallbacks from the PKP + capability registry; produce an ExecutionPlan. |
| **Interfaces** | `Planner.plan(timeline, capability_registry) → ExecutionPlan`. |
| **Boundaries** | Does not build the graph (that's S8); does not schedule (that's S10); does not make creative decisions (L-15). |
| **Dependencies** | Timeline (S6); Capability Registry (S13). |

### S8 — Execution Graph Builder

| Field | Value |
|---|---|
| **Responsibilities** | Construct the DAG of executable units from the plan + timeline; detect cycles; produce an ExecutionGraph. |
| **Interfaces** | `GraphBuilder.build(execution_plan) → ExecutionGraph`. |
| **Boundaries** | Does not emit the EIR (that's S9); does not schedule. |
| **Dependencies** | ExecutionPlan (S7). |

### S9 — Execution Intermediate Representation (EIR)

| Field | Value |
|---|---|
| **Responsibilities** | Be the language-neutral execution contract; carry nodes, dependencies, adapter bindings, seeds, configs, and provenance stubs. The EIR is the single artifact adapters consume. |
| **Interfaces** | `EIRBuilder.emit(execution_graph) → EIR`; `EIR` is serializable to a language-neutral format (JSON Schema + a stable binary form per ADR). |
| **Boundaries** | The EIR does not contain creative decisions (L-15); it does not contain adapter secrets; it is read-only for adapters. |
| **Dependencies** | ExecutionGraph (S8). Schema defined in `DESIGN/004`. |

### S10 — Scheduler

| Field | Value |
|---|---|
| **Responsibilities** | Compute a topological schedule; dispatch EIR nodes to adapters; coordinate parallelism; enforce deterministic merge order; support selective and conditional execution. |
| **Interfaces** | `Scheduler.schedule(eir) → Schedule`; `Scheduler.dispatch(schedule) → ExecutionHandle`. |
| **Boundaries** | Does not invoke adapters directly (goes through S13); does not make creative decisions; does not modify the EIR. |
| **Dependencies** | EIR (S9); Runtime State Manager (S11); Adapter Framework (S13); Resource Manager (S14). |

### S11 — Runtime State Manager

| Field | Value |
|---|---|
| **Responsibilities** | Track per-node state (`pending`, `running`, `retried`, `succeeded`, `failed`, `skipped`, `emitted`); track per-execution state; provide queryable state to the CLI/API/SDK. |
| **Interfaces** | `StateManager.get_state(node_id) → NodeState`; `StateManager.get_execution_state() → ExecutionState`. |
| **Boundaries** | Does not dispatch (that's S10); does not classify failures (that's S16). |
| **Dependencies** | Event Bus (S12) — state transitions are event-driven. |

### S12 — Event Bus

| Field | Value |
|---|---|
| **Responsibilities** | Emit structured events for every execution step; deliver events to subscribers (metrics, logging, progress, report); guarantee no silent execution. |
| **Interfaces** | `EventBus.emit(event) → void`; `EventBus.subscribe(filter, handler) → SubscriptionId`. |
| **Boundaries** | Does not classify events (that's S16); does not persist events (that's S13 + ATLAS). |
| **Dependencies** | Event schema (`DESIGN/008`). |

### S13 — Adapter Framework

| Field | Value |
|---|---|
| **Responsibilities** | Own the capability registry; abstract providers behind capability interfaces; manage adapter lifecycle (load, invoke, unload); dispatch EIR nodes to adapters; record adapter version + invocation params. |
| **Interfaces** | `AdapterFramework.invoke(node, adapter_id) → AdapterResult`; `CapabilityRegistry.resolve(capability, constraints) → AdapterId`. |
| **Boundaries** | Does not make creative decisions; does not modify the EIR; does not call ORACLE. |
| **Dependencies** | EIR (S9); Plugin Framework (S26) — adapters are plugins. |

### S14 — Resource Manager

| Field | Value |
|---|---|
| **Responsibilities** | Enforce compute/memory/concurrency budgets; serialize rendering jobs that exceed available resources; preserve determinism under resource constraints. |
| **Interfaces** | `ResourceManager.acquire(budget) → Lease`; `ResourceManager.release(lease) → void`. |
| **Boundaries** | Does not decide execution order (that's S10). |
| **Dependencies** | Configuration (S24) — budgets are configurable. |

### S15 — Cache Manager

| Field | Value |
|---|---|
| **Responsibilities** | Cache outputs by `(EIR node hash, adapter id, adapter version, seed, configuration hash)`; serve cache hits; invalidate on key change. |
| **Interfaces** | `CacheManager.get(key) → Option<Output>`; `CacheManager.put(key, output) → void`. |
| **Boundaries** | Does not execute (that's S13); does not persist long-term (that's ATLAS). |
| **Dependencies** | Configuration (S24) — cache backend is configurable. |

### S16 — Failure Recovery Engine

| Field | Value |
|---|---|
| **Responsibilities** | Classify failures (recoverable, retryable, fatal, constitutional, infrastructure, dependency, configuration, adapter, resource, validation); apply recovery strategy (retry, fallback, terminate). |
| **Interfaces** | `Recovery.classify(failure) → FailureClass`; `Recovery.handle(failure, node) → RecoveryDecision`. |
| **Boundaries** | Does not invoke adapters (goes through S13); does not make creative decisions. |
| **Dependencies** | Retry Strategy (S17); Capability Registry (S13) — for fallbacks. |

### S17 — Retry Strategy

| Field | Value |
|---|---|
| **Responsibilities** | Define per-failure-class retry policies (max attempts, backoff, jitter); bound retries; record retries in the event stream. |
| **Interfaces** | `Retry.should_retry(failure_class, attempt) → bool`; `Retry.next_attempt(failure_class, attempt) → Delay`. |
| **Boundaries** | Does not classify failures (that's S16); does not invoke adapters. |
| **Dependencies** | Configuration (S24) — retry policies are configurable. |

### S18 — Checkpoint Manager

| Field | Value |
|---|---|
| **Responsibilities** | Persist state at every stage (or at a configurable frequency); resume from any checkpoint; guarantee byte-identical resume. |
| **Interfaces** | `CheckpointManager.save(state) → CheckpointId`; `CheckpointManager.load(checkpoint_id) → State`. |
| **Boundaries** | Does not execute stages; does not call ATLAS directly (writes go through S23 or a local store). |
| **Dependencies** | Configuration (S24) — checkpoint backend is configurable. |

### S19 — Progress Monitor

| Field | Value |
|---|---|
| **Responsibilities** | Surface execution progress to the CLI/API/SDK; report per-node and per-execution progress. |
| **Interfaces** | `Progress.report() → ProgressReport`. |
| **Boundaries** | Does not execute; does not classify failures. |
| **Dependencies** | Runtime State Manager (S11); Event Bus (S12). |

### S20 — Metrics Engine

| Field | Value |
|---|---|
| **Responsibilities** | Collect per-step, per-adapter, per-resource metrics (duration, inputs, outputs, dependencies, resource usage, diagnostics); expose to the report and to the CLI/API. |
| **Interfaces** | `Metrics.record(event) → void`; `Metrics.query(filter) → MetricSet`. |
| **Boundaries** | Does not classify metrics; does not persist long-term. |
| **Dependencies** | Event Bus (S12). |

### S21 — Diagnostics

| Field | Value |
|---|---|
| **Responsibilities** | Define the diagnostic schema; rank diagnostics by severity; group by artifact and invariant; cite the violated invariant with a GENESIS doc reference. |
| **Interfaces** | `Diagnostics.rank(set) → RankedSet`; `Diagnostics.group(set) → GroupedSet`. |
| **Boundaries** | Does not execute; does not amend the PKP. |
| **Dependencies** | Invariant set (`IMPLEMENTATION/invariants.md`). |

### S22 — Logging

| Field | Value |
|---|---|
| **Responsibilities** | Provide structured, leveled logging; correlate logs with events; never log secrets. |
| **Interfaces** | `Logger.log(level, message, fields) → void`. |
| **Boundaries** | Does not replace the event bus (events are structured; logs are for humans). |
| **Dependencies** | Configuration (S24) — log level and destination are configurable. |

### S23 — Asset Emission Service

| Field | Value |
|---|---|
| **Responsibilities** | Stamp every output with provenance (PKP artifact, PKP hash, EIR node id, adapter id + version, seed, timestamp, parent outputs); write outputs + the execution report to ATLAS. |
| **Interfaces** | `Emission.emit(output, provenance) → ATLASRef`; `Emission.emit_report(report) → ATLASRef`. |
| **Boundaries** | Does not write to the PKP, CIR, or CIS (L-14); does not call ORACLE. |
| **Dependencies** | ATLAS (write); Provenance schema (`DESIGN/013`). |

### S24 — Configuration

| Field | Value |
|---|---|
| **Responsibilities** | Own profiles, adapter configs, scheduler configs, retry policies, cache backends, checkpoint backends, log levels; resolve configs from files + env + CLI flags. |
| **Interfaces** | `Config.load(profile) → Config`; `Config.get(key) → Value`. |
| **Boundaries** | Does not execute; does not hold secrets in memory longer than necessary. |
| **Dependencies** | Filesystem (read); env (read). |

### S25 — Security

| Field | Value |
|---|---|
| **Responsibilities** | Define capability policy (filesystem read, network, subprocess) for plugins and adapters; handle secrets (API keys) without logging; enforce sandbox boundaries. |
| **Interfaces** | `Security.capability_policy(plugin_id) → Policy`; `Security.check(plugin_id, capability) → bool`. |
| **Boundaries** | Does not execute plugins; does not call network. |
| **Dependencies** | Configuration (S24); Plugin Framework (S26). |

### S26 — Plugin Framework

| Field | Value |
|---|---|
| **Responsibilities** | Load, validate, sandbox, and dispatch plugins; reject plugins that exceed their declared capabilities at load time; support adapters, validators, schedulers, storage, caches, metrics, hooks, and custom executors as plugins. |
| **Interfaces** | `Plugins.load(manifest) → PluginId`; `Plugins.invoke(plugin_id, op, args) → Result`. |
| **Boundaries** | Does not implement plugin logic; does not bypass the capability policy. |
| **Dependencies** | Security (S25); Configuration (S24). |

### S27 — CLI

| Field | Value |
|---|---|
| **Responsibilities** | Provide a stable subcommand surface (`run`, `doctor`, `status`, `eir`, `report`, `provenance`, `cache`, `checkpoint`, `pipeline`); be the automation contract. |
| **Interfaces** | `prometheus <subcommand> [args]`. |
| **Boundaries** | Does not implement business logic; delegates to the API (S28). |
| **Dependencies** | API (S28); Configuration (S24). |

### S28 — API

| Field | Value |
|---|---|
| **Responsibilities** | Provide the programmatic contract (language-neutral); own the public surface the SDK (S29) and CLI (S27) build on. |
| **Interfaces** | A language-neutral API specification (JSON Schema + an IDL); the SDK and CLI are projections of it. |
| **Boundaries** | Does not implement; delegates to the Runtime Core (S1). |
| **Dependencies** | Runtime Core (S1). |

### S29 — SDK

| Field | Value |
|---|---|
| **Responsibilities** | Provide language bindings for the API; ship in multiple languages over time. |
| **Interfaces** | Language-specific bindings (e.g., `prometheus.run(pkp_id)`). |
| **Boundaries** | Does not define the contract (that's S28); does not implement business logic. |
| **Dependencies** | API (S28). |

### S30 — Testing Framework

| Field | Value |
|---|---|
| **Responsibilities** | Own golden PKPs, regression tests, correctness tests, performance tests, the determinism harness, the fault-injection harness. |
| **Interfaces** | `Testing.run_golden(pkp_id) → TestResult`; `Testing.run_determinism(pkp_id) → DeterminismResult`. |
| **Boundaries** | Does not ship in production builds. |
| **Dependencies** | Runtime Core (S1); Benchmark Framework (S31). |

### S31 — Benchmark Framework

| Field | Value |
|---|---|
| **Responsibilities** | Define performance budgets; run reproducible benchmarks; report budget violations. |
| **Interfaces** | `Benchmark.run(suite) → BenchmarkReport`. |
| **Boundaries** | Does not replace the testing framework; benchmarks are a subset of tests. |
| **Dependencies** | Testing Framework (S30). |

---

## 4. Interaction Map

Who calls whom, at the layer boundary:

```
CLI (S27) ──► API (S28) ──► Runtime Core (S1)
                                  │
       ┌──────────────────────────┼──────────────────────────┐
       │                          │                          │
       ▼                          ▼                          ▼
  Loading & Validation     Planning & Compilation    Scheduling & Execution
  S2 Loader                 S6 Timeline Builder       S10 Scheduler
  S3 Validator              S7 Planner                S11 State Manager
  S4 DepResolver            S8 GraphBuilder           S12 Event Bus
  S5 ResResolver            S9 EIR                    S13 Adapter Framework
                                                        S14 Resource Manager
                                                        S15 Cache Manager
                                  │
                                  ▼
                            Recovery
                            S16 Failure Recovery
                            S17 Retry Strategy
                            S18 Checkpoint Manager
                                  │
                                  ▼
                     Observability & Emission
                     S19 Progress Monitor
                     S20 Metrics Engine
                     S21 Diagnostics
                     S22 Logging
                     S23 Asset Emission ──► ATLAS
                                  │
                                  ▼
                     Platform (cross-cutting)
                     S24 Configuration
                     S25 Security
                     S26 Plugin Framework
                     S30 Testing Framework
                     S31 Benchmark Framework
```

---

## 5. Subsystem → DESIGN doc map

| Subsystem | Primary DESIGN doc | Secondary DESIGN docs |
|---|---|---|
| S1 Runtime Core | `003` (this doc) | `009`, `015` |
| S2 PKP Loader | `007` | `005` |
| S3 Constitutional Validator | `010` | `005` |
| S4 Dependency Resolver | `005` | `010` |
| S5 Resource Resolver | `005`, `014` | `006` |
| S6 Timeline Builder | `005` | — |
| S7 Execution Planner | `005` | `006` |
| S8 Execution Graph Builder | `005` | `004` |
| S9 EIR | `004` | `005` |
| S10 Scheduler | `011` | `005`, `014` |
| S11 Runtime State Manager | `012` | `008` |
| S12 Event Bus | `008` | — |
| S13 Adapter Framework | `006` | `015` |
| S14 Resource Manager | `014` | `011` |
| S15 Cache Manager | `014` | — |
| S16 Failure Recovery Engine | `012` | `006` |
| S17 Retry Strategy | `012` | — |
| S18 Checkpoint Manager | `012` | `014` |
| S19 Progress Monitor | `008` | `009` |
| S20 Metrics Engine | `008` | — |
| S21 Diagnostics | `010` | `008` |
| S22 Logging | `008` | — |
| S23 Asset Emission Service | `013` | `012` |
| S24 Configuration | `009` | — |
| S25 Security | `015` | — |
| S26 Plugin Framework | `015` | `006` |
| S27 CLI | `009` | `028` |
| S28 API | `010` (API DESIGN, not validator) | `028` |
| S29 SDK | `010` (API DESIGN) | — |
| S30 Testing Framework | `016` | — |
| S31 Benchmark Framework | `016` | — |

---

## 6. What This Document Does Not Define

- The EIR schema — that is `DESIGN/004`.
- The pipeline's stage contract details — that is `DESIGN/005`.
- The adapter interface — that is `DESIGN/006`.
- The event schema — that is `DESIGN/008`.
- The scheduler's algorithm — that is `DESIGN/011`.
- The failure classification logic — that is `DESIGN/012`.
- The provenance schema — that is `DESIGN/013`.

This document defines *what exists*. The per-subsystem DESIGN docs define *how it works*.

---

## 7. ADR Candidates Surfaced

| Candidate | Decision | Blocking milestone |
|---|---|---|
| 0016 | Plugin sandbox scope (load-time vs runtime) | M5 |
| 0017 | API IDL choice (OpenAPI / gRPC / JSON Schema + custom) | M0 |
| 0018 | Adapter invocation protocol (in-process / subprocess / IPC) | M2 |
| 0019 | State manager storage (in-memory / on-disk / distributed) | M2 |
| 0020 | Event bus delivery guarantees (at-most-once / at-least-once / exactly-once) | M2 |

---

## 8. Cross-References

| Reference | Relevance |
|---|---|
| `010` (PROMETHEUS Runtime Architecture) | Constitutional architecture; this document is its engineering realization. |
| `DESIGN/002` | Execution model (dynamic flow). |
| `DESIGN/004` | EIR. |
| `DESIGN/005` | Pipeline (stage contract). |
| `DESIGN/006` | Adapter framework. |
| `gkc/DESIGN/003` | Sibling product's component architecture; the pattern this document follows. |

---

**End of PROMETHEUS-003.**