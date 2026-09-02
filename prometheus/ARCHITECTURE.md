# PROMETHEUS Architecture

This is the **system-level architecture map**. It does not re-derive any subsystem — it orients the reader and links to the DESIGN doc that does. Read this file once; navigate from it forever after.

---

## One-Paragraph Architecture

PROMETHEUS is a **multi-stage execution compiler**. A PKP loader reads a frozen PKP from ATLAS and verifies its hash and state. A constitutional validator checks the PKP against GENESIS invariants. A dependency resolver and resource resolver close the PKP's declared dependencies. A timeline builder orders the work; an execution planner and execution graph builder produce an Execution Intermediate Representation (EIR) — the language-neutral execution contract. A scheduler dispatches executable EIR nodes to runtime adapters through a capability registry. A runtime state manager tracks progress; an event bus emits structured events for every step. A failure recovery engine classifies failures and applies retry, fallback, or fatal-termination strategies. A checkpoint manager persists state for resume. A metrics engine, diagnostics, and logging feed an execution report. An asset emission service stamps every output with provenance and writes outputs + the execution report to ATLAS. A plugin framework, CLI, API, SDK, testing framework, and benchmark framework surround the core. Everything outside the runtime core is replaceable.

---

## System Diagram

```
┌────────────────────────────────────────────────────────────────────────┐
│                              ATLAS (012)                                 │
│                  holds the frozen PKP, prior media, reports             │
└──────────────────────────────┬─────────────────────────────────────────┘
                               │ read PKP by identity + version
                               ▼
┌────────────────────────────────────────────────────────────────────────┐
│  LOADING & VALIDATION                                                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐    │
│  │ PKP      │→ │Constitu- │→ │Dependency│→ │ Resource Resolver    │    │
│  │ Loader   │  │tional    │  │Resolver  │  │ (adapters, assets,    │    │
│  │          │  │Validator │  │          │  │  seeds, configs)     │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────────┘    │
└──────────────────────────────┬─────────────────────────────────────────┘
                               │ resolved, validated PKP
                               ▼
┌────────────────────────────────────────────────────────────────────────┐
│  PLANNING & COMPILATION                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────────┐  │
│  │ Timeline      │→ │ Execution     │→ │ Execution Graph Builder      │  │
│  │ Builder       │  │ Planner       │  │  → EIR (the execution        │  │
│  │               │  │               │  │     contract; see DESIGN/004)│  │
│  └──────────────┘  └──────────────┘  └──────────────────────────────┘  │
└──────────────────────────────┬─────────────────────────────────────────┘
                               │ EIR
                               ▼
┌────────────────────────────────────────────────────────────────────────┐
│  SCHEDULING & EXECUTION                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────────┐  │
│  │ Scheduler     │→ │ Runtime       │→ │ Adapter Framework            │  │
│  │ (seq/par/     │  │ State Mgr     │  │  (capability registry,        │  │
│  │  dist/retry)  │  │ + Event Bus   │  │   provider abstraction)      │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────────┘  │
│         │                  │                       │                     │
│         │          ┌───────┴────────┐      ┌───────┴──────────┐          │
│         ▼          │ Failure        │      │ Resource Mgr +   │          │
│   Checkpoint Mgr    │ Recovery +     │      │ Cache Mgr        │          │
│                     │ Retry Strategy │      └──────────────────┘          │
└─────────────────────┴───────────────┴──────────────────────────────────┘
                               │ execution events + outputs
                               ▼
┌────────────────────────────────────────────────────────────────────────┐
│  EMISSION & OBSERVABILITY                                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────────┐  │
│  │ Provenance    │→ │ Execution     │→ │ Metrics + Diagnostics +      │  │
│  │ Stamping      │  │ Report        │  │ Logging + Progress Monitor   │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────────┘  │
└──────────────────────────────┬─────────────────────────────────────────┘
                               │ write outputs + report
                               ▼
┌────────────────────────────────────────────────────────────────────────┐
│                              ATLAS (012)                                 │
│            preserves outputs, provenance, execution report               │
└─────────────────────────────────────────────────────────────────────────┘
                               │ read for validation
                               ▼
                            ORACLE (011)
```

---

## Subsystem → DESIGN doc map

| # | Subsystem | Responsibility | DESIGN doc |
|---|---|---|---|
| S1 | Runtime Core | Process boundary; owns the lifecycle; wires subsystems together | `003` |
| S2 | PKP Loader | Load + hash-verify + state-verify the frozen PKP from ATLAS | `007` |
| S3 | Constitutional Validator | Check PKP against GENESIS invariants; emit ranked diagnostics | `010` |
| S4 | Dependency Resolver | Close declared dependencies; surface unresolved as diagnostics | `005` |
| S5 | Resource Resolver | Resolve adapter identities, asset references, seeds, configs | `005`, `014` |
| S6 | Timeline Builder | Order work along the PKP's timeline | `005` |
| S7 | Execution Planner | Choose components, providers, and order from the PKP | `005` |
| S8 | Execution Graph Builder | Build the DAG of executable units | `005` |
| S9 | Execution Intermediate Representation (EIR) | The language-neutral execution contract | `004` |
| S10 | Scheduler | Dispatch EIR nodes (seq/par/dist/retry/selective/conditional) | `011` |
| S11 | Runtime State Manager | Track per-node, per-execution state | `012` |
| S12 | Event Bus | Structured event emission; no silent execution | `008` |
| S13 | Adapter Framework | Capability registry, provider abstraction, adapter lifecycle | `006` |
| S14 | Resource Manager | Compute/memory/concurrency budgets; serialization when needed | `014` |
| S15 | Cache Manager | Cache outputs by (PKP artifact hash, adapter version, seed) | `014` |
| S16 | Failure Recovery Engine | Classify failures; apply recovery strategy | `012` |
| S17 | Retry Strategy | Per-failure-class retry policy; bounded retries | `012` |
| S18 | Checkpoint Manager | Persist state for resume; resume from any checkpoint | `012` |
| S19 | Progress Monitor | Surface execution progress to CLI/API/SDK | `008` |
| S20 | Metrics Engine | Collect per-step, per-adapter, per-resource metrics | `008` |
| S21 | Diagnostics | Rank and group diagnostics; cite violated invariants | `010` |
| S22 | Logging | Structured, leveled, observable logs | `008` |
| S23 | Configuration | Profiles, adapter configs, scheduler configs | `009` |
| S24 | Security | Capability policy, secret handling, sandbox boundaries | `015` |
| S25 | Plugin Framework | Load, validate, sandbox, dispatch plugins | `015` |
| S26 | CLI | Stable subcommand surface; automation contract | `009` |
| S27 | API | Programmatic contract (language-neutral) | `010` |
| S28 | SDK | Language bindings; multiple languages later | `010` |
| S29 | Testing Framework | Golden PKPs, regression, correctness, performance | `016` |
| S30 | Benchmark Framework | Performance budgets; reproducible benchmarks | `016` |

### Cross-cutting concerns

| # | Concern | Owner | Notes |
|---|---|---|---|
| X1 | Diagnostics | Every stage emits; Constitutional Validator ranks | `DESIGN/010` |
| X2 | Provenance | Asset Emission stamps; ATLAS preserves | `DESIGN/013` |
| X3 | Determinism | Every stage preserves; seed + recorded-output fallback | `DESIGN/004`, `DESIGN/012` |
| X4 | Observability | Event Bus + Metrics + Logging | `DESIGN/008` |
| X5 | Versioning | Inputs, EIR, adapters, outputs all carry versions | `DESIGN/004`, `DESIGN/013` |

---

## Pipeline Stages (canonical order)

See `DESIGN/005` for the full stage contract. The canonical order is:

```
 1. Load        — read the PKP from ATLAS; verify hash and state
 2. Validate    — constitutional integrity; emit ranked diagnostics
 3. Resolve Deps— close declared dependencies; surface unresolved
 4. Resolve Res — resolve adapter ids, asset refs, seeds, configs
 5. Timeline    — order work along the PKP timeline
 6. Plan        — choose components, providers, order
 7. Build Graph — construct the execution DAG
 8. Emit EIR    — produce the Execution Intermediate Representation
 9. Schedule    — dispatch EIR nodes to adapters
10. Execute     — adapters run; events emit; state tracks
11. Recover     — classify failures; retry/fallback/terminate
12. Checkpoint  — persist state (continuous, not a terminal stage)
13. Emit Outputs— stamp provenance; write to ATLAS
14. Report      — assemble execution report; write to ATLAS
```

Stages 1–8 are **eager and deterministic** — they produce the same EIR for the same PKP + same adapter versions. Stages 9–11 are **executing** — timing varies, but outputs are deterministic. Stages 12–14 are **continuous** — checkpoint runs throughout; emission and reporting close the execution.

Every stage is **deterministic, cacheable, and resumable** from any prior stage's output.

---

## Contract Flow

The contracts that flow between subsystems are language-neutral and are the stable surfaces of the platform:

| Contract | Producer | Consumer | Defined in |
|---|---|---|---|
| Frozen PKP | GENESIS (compiler, `008`) | PROMETHEUS (Loader) | `009` (GENESIS) |
| Validated PKP | Constitutional Validator | Dependency/Resource Resolvers | `DESIGN/010` |
| Resolved PKP | Resource Resolver | Timeline Builder, Planner | `DESIGN/005` |
| EIR | Execution Graph Builder | Scheduler, Adapters | `DESIGN/004` |
| Schedule | Scheduler | Runtime State Manager | `DESIGN/011` |
| Execution Events | Adapters / Runtime | Event Bus, Metrics, Report | `DESIGN/008` |
| Outputs + Provenance | Asset Emission | ATLAS, ORACLE | `DESIGN/013` |
| Execution Report | Report Builder | ATLAS, ORACLE, Board | `DESIGN/013` |

The **EIR is the central contract**. Everything upstream produces it; everything downstream consumes it. Adapters never touch the PKP directly — they consume the EIR. This is the architectural enforcement of adapter independence.

---

## Separation from GENESIS

This package is the **engineering product**. It derives from `010` and never overrides it:

| `010` (constitutional) | `prometheus/` (engineering) |
|---|---|
| Defines what the runtime *is* | Defines how the runtime is *built* |
| Frozen; amended by constitutional revision | Evolves; amended by ADR |
| Architecture | Engineering |
| Read by humans, referenced by machines | Read by machines, supervised by humans |

If a DESIGN doc in this package conflicts with `010`, `010` wins. The DESIGN doc must either change or surface an ADR requesting a constitutional amendment. See `DECISIONS/README.md` for the ADR process.

---

## See Also

- `README.md` — product overview.
- `VISION.md` — engineering vision and philosophy.
- `ROADMAP.md` — milestone plan.
- `010 — PROMETHEUS Runtime Architecture.md` (repo root) — canonical architecture.
- `gkc/ARCHITECTURE.md` — sibling product; the pattern this package follows.