# GKC Architecture

This is the **system-level architecture map**. It does not re-derive any subsystem — it orients the reader and links to the DESIGN doc that does. Read this file once; navigate from it forever after.

---

## One-Paragraph Architecture

GKC is a **multi-stage knowledge compiler**. A scanner frontend reads a repository and classifies its artifacts. A parser extracts metadata. A resolver turns references into stable identifiers. A registry stores the result. Two graph builders (authority, dependency) and an ontology compiler operate over the registry. A validation pass checks the registry and graphs against GENESIS invariants. A context compiler slices the registry and graphs into token-bounded, authority-aware, dependency-closed packages for AI agents. A query engine answers semantic questions over the registry and graphs. A CLI exposes all of it. A storage layer persists registries, snapshots, graphs, and caches. A plugin framework extends every stage without forking.

---

## System Diagram

```
┌────────────────────────────────────────────────────────────────────────┐
│                              Repository                                 │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │ scan
                                     ▼
┌────────────────────────────────────────────────────────────────────────┐
│  Frontend                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐   │
│  │ Scanner  │→ │ Parser   │→ │Metadata  │→ │ Resolver             │   │
│  │classify  │  │extract   │  │normalize │  │ resolve references   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────────┘   │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │ resolved artifacts
                                     ▼
┌────────────────────────────────────────────────────────────────────────┐
│  Knowledge IR                                                          │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ Registry │  │ Authority    │  │ Dependency   │  │ Ontology     │   │
│  │ entries  │  │ Graph        │  │ Graph        │  │              │   │
│  └──────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │ graphs + registry
            ┌────────────────────────┼────────────────────────┐
            │                        │                        │
            ▼                        ▼                        ▼
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│  Validation Pass    │  │  Query Engine       │  │  Context Compiler   │
│  vs GENESIS         │  │  search/explain/    │  │  slice + budget +   │
│  invariants         │  │  impact/authority   │  │  emit for agent     │
└─────────────────────┘  └─────────────────────┘  └─────────────────────┘
            │                        │                        │
            ▼                        ▼                        ▼
┌────────────────────────────────────────────────────────────────────────┐
│  Backends / Consumers                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐   │
│  │ CLI      │  │ Plugin   │  │ Storage  │  │ AIOS / IDEs / Agents │   │
│  │  gkc *   │  │ providers│  │ snapshots│  │  consume substrate   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────────┘   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Component → DESIGN doc map

| Component | Responsibility | DESIGN doc |
|---|---|---|
| Scanner | Discover and classify artifacts | `003`, `005` |
| Parser | Extract structured metadata per artifact kind | `003`, `005` |
| Metadata normalizer | Canonicalize metadata fields and identifiers | `002`, `004` |
| Resolver | Turn references into stable, content-addressed identifiers | `002`, `005` |
| Registry | Persistent, queryable index of resolved artifacts | `002`, `004`, `010` |
| Authority graph builder | Build graph of constitutional authority relationships | `002`, `005`, `006` |
| Dependency graph builder | Build graph of structural dependencies; detect cycles | `002`, `005`, `006` |
| Ontology compiler | Compile domain concepts and their links into an ontology | `002`, `005` |
| Validation pass | Check registry + graphs against GENESIS invariants; emit diagnostics | `005`, `011` |
| Query engine | Answer semantic queries (search, explain, impact, traversal) | `006` |
| Context compiler | Slice registry + graphs into token-bounded context packages | `007` |
| Plugin framework | Extend scanner, parser, graph edges, context providers | `008` |
| CLI | Stable subcommand surface; automation contract | `009` |
| Storage | Persistence, snapshots, graphs, caches, versioning | `010` |
| Testing | Golden repos, regression, correctness, performance | `011` |
| Reference implementation | Engineering roadmap, packages, deliverables | `012` |

---

## Pipeline Stages (canonical order)

See `DESIGN/005-pipeline.md` for the full stage contract. The canonical order is:

```
1. Scan        — discover artifacts, classify
2. Parse       — extract metadata per kind
3. Normalize   — canonicalize fields and identifiers
4. Resolve     — resolve references; surface unresolved as diagnostics
5. Register    — write entries into the persistent registry
6. Authority   — build authority graph
7. Dependency  — build dependency graph; detect cycles
8. Ontology    — compile ontology from declared concepts
9. Validate    — check registry + graphs against GENESIS invariants
10. Index      — build query indexes (search, traversal)
11. Context    — (lazy) build/refresh context slices on demand
```

Stages 1–10 are **eager**. Stage 11 is **lazy** — context is built on demand and cached. Every stage is **deterministic, cacheable, and incrementally re-runnable** from any prior stage's output.

---

## Data Flow Contracts

| Between | Contract |
|---|---|
| Scanner → Parser | `Artifact` (path, kind, content hash, classifier provenance) |
| Parser → Normalizer | `RawMetadata` (kind-specific structured fields) |
| Normalizer → Resolver | `CanonicalMetadata` (stable identifiers, normalized fields) |
| Resolver → Registry | `RegistryEntry` (stable id, version, authority, deps, refs) |
| Registry → Graph builders | `Registry snapshot` (immutable, content-addressed) |
| Graph builders → Ontology | `Graphs` (authority + dependency) |
| Graphs + Registry → Validation | `Knowledge IR` (registry + graphs + ontology) |
| Knowledge IR → Query engine | `Query indexes` |
| Knowledge IR → Context compiler | `Knowledge IR` + `TaskDescriptor` + `TokenBudget` |
| All → Storage | `Snapshot` (registry + graphs + ontology + indexes, content-addressed) |

Every contract is **typed and stable across versions**. Schema evolution is governed by `DESIGN/004` and `DESIGN/010`.

---

## Invariants (must hold at every milestone exit)

1. **Determinism.** Same repository + same GKC version + same plugins ⇒ byte-identical snapshot.
2. **Incrementality.** A single-artifact change re-runs only the affected subgraph of stages.
3. **Cache stability.** Cache hits are content-addressed; cache misses are reproducible.
4. **Diagnostic completeness.** A non-zero exit is always accompanied by a ranked diagnostic set.
5. **Plugin isolation.** A plugin failure in any stage does not corrupt the IR or the snapshot.
6. **GENESIS primacy.** Any conflict between GKC output and a GENESIS document surfaces as a constitutional violation diagnostic, never as silent override.

---

## Cross-Cutting Concerns

| Concern | Owned by | Notes |
|---|---|---|
| Versioning | Storage (`010`) | Snapshot versioning + metadata schema versioning |
| Caching | Storage (`010`) + Pipeline (`005`) | Two layers: stage input/output cache + compiled snapshot cache |
| Parallelism | Pipeline (`005`) | Stages 1–4 embarrassingly parallel; 5–10 graph-shaped |
| Diagnostics | Validation (`005`/`011`) + every stage | Every stage can emit diagnostics; only Validation ranks them |
| Observability | CLI (`009`) `gkc doctor` + stats | Health, cache hit rate, stage timings, plugin inventory |
| Security | Plugin framework (`008`) | Capability declarations, load-time rejection, no implicit network |

---

## See Also

- `DESIGN/003-component-architecture.md` — per-component responsibilities and boundaries.
- `DESIGN/005-pipeline.md` — full pipeline contract including incremental compilation.
- `DESIGN/010-storage.md` — persistence, snapshots, and versioning.
- `DECISIONS/` — every ADR that adjusts this architecture.