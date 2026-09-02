# GKC-003 — Component Architecture

> Every GKC subsystem: its responsibilities, its interfaces, its boundaries with other subsystems. This is the **static architecture**; the dynamic flow is in `DESIGN/005`.

---

## 1. Purpose

Pin down each component of GKC as a named, bounded, interface-having unit. After this document, no two DESIGN docs should disagree about what a component does or owns.

This document defines:

- the **component inventory** (what exists),
- each component's **responsibilities** (what it does),
- each component's **interfaces** (what it accepts and produces),
- each component's **boundaries** (what it explicitly does not do),
- the **interaction map** (who calls whom).

Implementation-level details (concrete APIs, data structures, algorithms) live in the per-component DESIGN docs cross-referenced here.

---

## 2. Component Inventory

GKC has 12 core components plus 3 cross-cutting concerns.

### 2.1 Core components (pipeline stages)

| # | Component | Role | Stage # |
|---|---|---|---|
| C1 | Scanner | Discover and classify artifacts in a repository | 1 |
| C2 | Parser | Extract structured metadata per artifact kind | 2 |
| C3 | Normalizer | Canonicalize metadata fields and identifiers | 3 |
| C4 | Resolver | Resolve references and dependencies to stable ids | 4 |
| C5 | Registry | Persist resolved artifacts as Registry Entries | 5 |
| C6 | Authority Builder | Build the authority graph | 6 |
| C7 | Dependency Builder | Build the dependency graph; detect cycles | 7 |
| C8 | Ontology Compiler | Compile the ontology from declared concepts | 8 |
| C9 | Validator | Check IR against GENESIS invariants; rank diagnostics | 9 |
| C10 | Indexer | Build query indexes over the registry and graphs | 10 |
| C11 | Context Compiler | Slice IR into token-bounded packages (lazy, on-demand) | 11 |

### 2.2 Service components

| # | Component | Role |
|---|---|---|
| C12 | Query Engine | Answer semantic queries over the IR |
| C13 | Storage | Persist snapshots, caches, graphs; manage GC |
| C14 | Plugin Framework | Load, validate, sandbox, and dispatch plugins |
| C15 | CLI | Stable subcommand surface; automation contract |

### 2.3 Cross-cutting concerns

| # | Concern | Owner | Notes |
|---|---|---|---|
| X1 | Diagnostics | Every stage emits; Validator ranks | See `DESIGN/005` § diagnostics |
| X2 | Caching | Storage owns the cache; stages use it | See `DESIGN/010` § caching |
| X3 | Observability | CLI `gkc doctor` aggregates; stages emit metrics | See `DESIGN/009` |

---

## 3. Component Specifications

### C1 — Scanner

**Responsibilities.**
- Walk a repository directory tree, respecting ignore rules.
- Read each file's content hash and basic attributes.
- Classify each file into an Artifact Kind using a pluggable classifier chain.
- Emit one Artifact per file (with kind `unknown` if no classifier matched).
- Emit `scanner-skip` info diagnostics for ignored files (suppressed by default).

**Interfaces.**
- **In:** `ScanRequest { repository_root, ignore_rules, classifiers }`
- **Out:** `ScanResult { artifacts: [Artifact], diagnostics: [Diagnostic] }`

**Boundaries.**
- Does **not** parse file contents into structured metadata (that's C2's job).
- Does **not** resolve references (that's C4's job).
- Does **not** decide authority (that's C2 / C3's job).
- Does **not** persist anything (that's C5 / C13's job).

**Extensibility.** Classifiers are pluggable (see `DESIGN/008` § classifier extension point).

**Failure modes.**
- Permission error on a directory ⇒ diagnostic, skip subtree.
- Classifier exception ⇒ per-artifact recovery (per ADR-Candidate-0003); the artifact gets kind `unknown` with a `classifier-failed` provenance marker.

---

### C2 — Parser

**Responsibilities.**
- For each Artifact, select a parser based on its kind.
- Extract kind-specific structured Metadata.
- Detect declared references, dependencies, and concepts.
- Detect declared authority level (if any).
- Emit diagnostics for malformed metadata.

**Interfaces.**
- **In:** `ParseRequest { artifact, parser_registry }`
- **Out:** `ParseResult { raw_metadata: RawMetadata, diagnostics: [Diagnostic] }`

**Boundaries.**
- Does **not** canonicalize (that's C3).
- Does **not** resolve references (that's C4).
- Does **not** decide authority if not declared (that's C3, with inference).
- Does **not** validate against GENESIS (that's C9).

**Extensibility.** Parsers are pluggable per kind (see `DESIGN/008` § parser extension point).

**Failure modes.**
- Parser exception ⇒ per-artifact recovery; raw_metadata is empty, diagnostic emitted.
- Unknown kind ⇒ default no-op parser; metadata is empty; `parse-skipped` info diagnostic.

---

### C3 — Normalizer

**Responsibilities.**
- Take RawMetadata and produce CanonicalMetadata.
- Normalize identifiers (case, separators, namespace prefixes).
- Apply authority inference rules when authority is not declared (e.g., files under `docs/genesis/` default to `constitutional`).
- Detect and report conflicting metadata (e.g., an artifact declares authority `guidance` but lives under `docs/genesis/`).

**Interfaces.**
- **In:** `NormalizeRequest { raw_metadata, artifact, inference_rules }`
- **Out:** `NormalizeResult { canonical_metadata, diagnostics }`

**Boundaries.**
- Does **not** resolve cross-artifact references (that's C4).
- Does **not** infer kinds (that's C1).
- Does **not** validate against GENESIS (that's C9).

**Extensibility.** Inference rules are configurable per workspace; plugins may register additional rules.

**Failure modes.**
- Conflicting metadata ⇒ diagnostic, deterministic tie-break (per ADR-Candidate-0009).

---

### C4 — Resolver

**Responsibilities.**
- Take CanonicalMetadata and resolve all References and Dependencies to stable artifact ids.
- Use a resolver strategy (path-based, identifier-based, manifest-based) per kind.
- Detect and emit unresolved-reference and unresolved-dependency diagnostics.
- Detect duplicate identifiers (two artifacts declaring the same id).

**Interfaces.**
- **In:** `ResolveRequest { canonical_metadata, registry_snapshot, resolver_strategies }`
- **Out:** `ResolveResult { resolved_references, resolved_dependencies, diagnostics }`

**Boundaries.**
- Does **not** mutate the registry (that's C5).
- Does **not** build graphs (that's C6/C7).
- Does **not** infer dependencies that were not declared.

**Extensibility.** Resolver strategies are pluggable per kind.

**Failure modes.**
- Unresolved hard dependency ⇒ `error` diagnostic.
- Unresolved soft dependency ⇒ `warning` diagnostic.
- Duplicate identifier ⇒ `error` diagnostic; deterministic choice (lowest hash) with provenance.

---

### C5 — Registry

**Responsibilities.**
- Accept resolved artifacts and produce Registry Entries.
- Maintain a content-addressed index of entries.
- Expose lookup by id, by kind, by authority, by identifier, by content hash.
- Track entry parent links (for version chains).
- Provide an immutable snapshot view of the registry at any point.

**Interfaces.**
- **In:** `RegisterRequest { resolved_artifact }`
- **Out:** `RegisterResult { registry_entry }`
- **Query:** `Lookup { by_id | by_kind | by_authority | by_identifier | by_content_hash }`
- **Out:** `[RegistryEntry]`

**Boundaries.**
- Does **not** build graphs (C6/C7 do that over the registry).
- Does **not** validate (C9 does that).
- Does **not** keep history beyond parent links (snapshots hold history, per ADR-Candidate-0012).

**Extensibility.** Registry indexes are extensible (plugins can declare new indexed fields).

**Failure modes.**
- Insertion of an entry that already exists (same id) ⇒ no-op (idempotent).
- Insertion of an entry with a conflicting identifier (different id, same identifier) ⇒ duplicate-identifier diagnostic; both entries coexist (the resolver already flagged this).

---

### C6 — Authority Builder

**Responsibilities.**
- Build the authority graph from the registry.
- For each entry, create edges to the artifacts it operationalizes / cites / implements (per ADR-Candidate-0011 strict level order).
- Detect and report violations of the stratification (e.g., a constitutional document citing a guidance document as authority).
- Detect cycles within a stratum (forbidden per ADR-Candidate-0011).

**Interfaces.**
- **In:** `AuthorityBuildRequest { registry_snapshot }`
- **Out:** `AuthorityBuildResult { authority_graph, diagnostics }`

**Boundaries.**
- Does **not** build the dependency graph (C7).
- Does **not** infer authority (C3 does).
- Does **not** validate against GENESIS invariants beyond stratification (C9 does).

**Extensibility.** New authority edge kinds are pluggable, subject to the stratification invariant.

**Failure modes.**
- Stratification violation ⇒ `constitutional-violation` diagnostic.
- Within-stratum cycle ⇒ `error` diagnostic.

---

### C7 — Dependency Builder

**Responsibilities.**
- Build the dependency graph from the registry.
- For each resolved Dependency, create a typed edge.
- Detect cycles; classify as hard (fatal) or soft (warning) per the dependency's `strength`.
- Compute transitive closures for impact analysis (lazily, on query).

**Interfaces.**
- **In:** `DependencyBuildRequest { registry_snapshot }`
- **Out:** `DependencyBuildResult { dependency_graph, cycle_diagnostics }`

**Boundaries.**
- Does **not** build the authority graph (C6).
- Does **not** compute closures eagerly (closures are query-time, C12).
- Does **not** infer dependencies (C4 resolves declared ones only).

**Extensibility.** New dependency edge kinds are pluggable.

**Failure modes.**
- Hard cycle ⇒ `error` diagnostic per cycle.
- Soft cycle ⇒ `warning` diagnostic per cycle.

---

### C8 — Ontology Compiler

**Responsibilities.**
- Extract declared concepts from registry entries.
- Build ontology nodes per namespace; merge within-namespace collisions (per ADR-Candidate-0018).
- Resolve references to concepts across artifacts.
- Build typed ontology edges (`is-a`, `part-of`, `references`, `extends`, etc.).
- Emit diagnostics for orphan concept references (referenced but never declared).

**Interfaces.**
- **In:** `OntologyBuildRequest { registry_snapshot }`
- **Out:** `OntologyBuildResult { ontology_graph, ontology_nodes, diagnostics }`

**Boundaries.**
- Does **not** validate domain meaning (C9 validates structural invariants only).
- Does **not** infer concepts not declared.
- Does **not** merge ontologies across snapshots (federation is a later horizon).

**Extensibility.** Edge kinds are pluggable; namespace policies are configurable.

**Failure modes.**
- Orphan reference ⇒ `warning` diagnostic.
- Conflicting definitions (same term, same namespace, different definitions) ⇒ `info` diagnostic; merge proceeds with both definitions recorded.

---

### C9 — Validator

**Responsibilities.**
- Take the IR (registry + graphs + ontology) and a set of invariant specs.
- Check each invariant; emit Diagnostics for violations.
- Rank diagnostics by `(severity, artifact_id, invariant_id, evidence_hash)`.
- Produce a Validation Report.

**Interfaces.**
- **In:** `ValidateRequest { ir, invariants, run_config }`
- **Out:** `ValidateResult { validation_report }`

**Boundaries.**
- Does **not** mutate the IR (it's immutable post-snapshot).
- Does **not** enforce; it reports. Enforcement (e.g., blocking a compile) is the pipeline runner's job.
- Does **not** invent invariants; they come from GENESIS codification or plugins.

**Extensibility.** Invariants are pluggable. Built-in invariants are codified from GENESIS `000`–`018` (tracked in `IMPLEMENTATION/invariants.md`).

**Failure modes.**
- An invariant plugin throws ⇒ `error` diagnostic from the validator; that invariant is marked `not-checked` in the report.

---

### C10 — Indexer

**Responsibilities.**
- Build query indexes over the registry and graphs.
- Maintain a search index (full-text over artifact content and metadata).
- Maintain a traversal index (adjacency lists for each graph).
- Maintain a concept index (term → nodes).
- Indexes are content-addressed; index rebuilds are incremental.

**Interfaces.**
- **In:** `IndexRequest { ir }`
- **Out:** `IndexResult { indexes }`

**Boundaries.**
- Does **not** answer queries (C12 does).
- Does **not** define ranking (C12 does).
- Does **not** persist indexes beyond the snapshot (snapshots hold them; C13 manages persistence).

**Extensibility.** Index kinds are pluggable (e.g., a plugin could add a vector index for semantic search).

**Failure modes.**
- Index build failure ⇒ `error` diagnostic; the affected index is marked `unavailable`; queries against it return `index-unavailable` errors.

---

### C11 — Context Compiler

**Responsibilities.**
- Accept a Task Descriptor and a Token Budget.
- Slice the IR into candidate Context Slices (overview, artifact, graph-excerpt, definition, diagnostic).
- Expand slices by dependency closure and authority closure.
- Allocate token budget across slices (per ADR-Candidate-0019, see `DESIGN/007`).
- Render slices through a provider (built-in Markdown, or plugin providers).
- Emit a Context Package; cache it by `(task hash, snapshot id, budget, provider)`.

**Interfaces.**
- **In:** `ContextCompileRequest { task_descriptor, token_budget, snapshot, provider }`
- **Out:** `ContextCompileResult { context_package, diagnostics }`

**Boundaries.**
- Does **not** generate prose beyond what's in the IR (no LLM calls).
- Does **not** execute the task (that's AIOS / agents).
- Does **not** mutate the IR.
- Does **not** decide which agent consumes the package.

**Extensibility.** Providers are pluggable (see `DESIGN/008` § context provider extension point).

**Failure modes.**
- Budget too small for any meaningful package ⇒ `error` diagnostic; package is empty.
- Provider exception ⇒ per-package recovery; falls back to the built-in Markdown provider with a `provider-fallback` marker.

---

### C12 — Query Engine

**Responsibilities.**
- Answer semantic queries: search, explain, impact, authority traversal, dependency traversal.
- Use the indexes built by C10.
- Apply ranking (relevance, authority, recency-weighted by authority).
- Return results with provenance (which artifacts, which edges justified each result).

**Interfaces.**
- **In:** `QueryRequest { kind, params, snapshot }`
- **Out:** `QueryResult { ranked_results, provenance }`

**Boundaries.**
- Does **not** mutate the IR.
- Does **not** generate context packages (C11 does).
- Does **not** call LLMs.

**Extensibility.** Query kinds are pluggable (e.g., a plugin could add a "similar artifacts" query using a vector index).

**Failure modes.**
- Unknown query kind ⇒ `error`.
- Index unavailable ⇒ `error` with `index-unavailable` marker; query may fall back to a slower scan if configured.

---

### C13 — Storage

**Responsibilities.**
- Persist Repository Snapshots (registry + graphs + ontology + indexes + validation report).
- Persist stage caches (input/output per stage, content-addressed).
- Persist context cache (Context Packages keyed by identity tuple).
- Manage snapshot GC (reference counting + LRU for caches).
- Manage workspace metadata (config, plugin registry, lock).
- Provide atomic commit (a snapshot is either fully written or not at all).

**Interfaces.**
- **In:** `StoreRequest { snapshot | cache_entry | context_package }`
- **Out:** `StoreResult { address }`
- **In:** `LoadRequest { address }`
- **Out:** `LoadResult { payload, metadata }`

**Boundaries.**
- Does **not** interpret snapshot contents (it's a byte store with schema metadata).
- Does **not** run pipeline stages.
- Does **not** make policy decisions (GC policy is configured; enforcement is Storage's job).

**Extensibility.** Storage backends are pluggable (filesystem default; plugin could add SQLite, S3, etc., subject to local-first invariant).

**Failure modes.**
- Write failure ⇒ `error` diagnostic; snapshot is not committed; pipeline may retry.
- Corrupt snapshot detected on load ⇒ `error` diagnostic; snapshot is marked `corrupt`; GC will reclaim it.

---

### C14 — Plugin Framework

**Responsibilities.**
- Discover plugins in the workspace's plugin directory.
- Verify plugin integrity (content hash matches manifest).
- Verify declared capabilities against workspace policy.
- Load plugins into isolated contexts (per ADR-Candidate-0020 sandboxing level).
- Dispatch plugin calls to extension points (scanner, parser, graph, validator, context-provider, indexer, storage-backend).
- Catch plugin failures at the stage boundary (per ADR-Candidate-0003).

**Interfaces.**
- **In:** `PluginLoadRequest { workspace, plugin_manifest }`
- **Out:** `PluginLoadResult { loaded_plugin | rejection_reason }`
- **Dispatch:** `PluginCall { extension_point, input } → { output | failure }`

**Boundaries.**
- Does **not** implement extension points (plugins do).
- Does **not** define the extension point contracts (each component does, in its own DESIGN doc section).
- Does **not** privilege built-in plugins over external ones (built-ins are simply pre-registered).

**Extensibility.** The plugin framework itself is not extensible by plugins (meta-extension would compromise isolation).

**Failure modes.**
- Plugin integrity failure ⇒ load rejected; `error` diagnostic.
- Capability exceeded at load time ⇒ load rejected; `error` diagnostic.
- Capability exceeded at runtime ⇒ plugin terminated; `error` diagnostic; affected artifact gets `plugin-failed` marker.

---

### C15 — CLI

**Responsibilities.**
- Parse command-line arguments into Build Session / Query / Context requests.
- Route to the appropriate component.
- Format output for human or machine consumption (text, JSON, JSONL).
- Exit codes: 0 success, 1 user error, 2 compile error, 3 constitutional violation, 4 internal error.
- Provide stable subcommands (see `DESIGN/009`).

**Interfaces.**
- **In:** `argv`
- **Out:** stdout (formatted), stderr (diagnostics), exit code

**Boundaries.**
- Does **not** implement business logic (it routes to components).
- Does **not** persist state (it uses Storage).
- Does **not** load plugins directly (it asks the Plugin Framework).

**Extensibility.** CLI subcommands are **not** pluggable (stability is the contract); plugins can add `--provider` options to existing subcommands.

**Failure modes.**
- Invalid args ⇒ exit 1, usage message to stderr.
- Compile error ⇒ exit 2, diagnostics to stderr.
- Constitutional violation ⇒ exit 3, diagnostics to stderr.
- Internal error ⇒ exit 4, stack trace to stderr (if `--debug`).

---

## 4. Interaction Map

### 4.1 Static dependencies (compile-time / import-time)

```
CLI ──depends on──► {C11, C12, C13, C14, C15}
C11 ──depends on──► {C5, C6, C7, C8, C10, C13, C14}
C12 ──depends on──► {C10, C13}
C9  ──depends on──► {C5, C6, C7, C8}
C10 ──depends on──► {C5, C6, C7, C8}
C8  ──depends on──► {C5}
C7  ──depends on──► {C5}
C6  ──depends on──► {C5}
C5  ──depends on──► {C4}
C4  ──depends on──► {C3, C5}
C3  ──depends on──► {C2}
C2  ──depends on──► {C1}
C1  ──depends on──► {C13}
C13 ──depends on──► {C14}
```

Note: this is the static call graph, not the runtime pipeline order. The pipeline DAG is in `DESIGN/005`.

### 4.2 Runtime flow (one compilation)

```
Build Session starts
  → Plugin Framework loads plugins
  → Storage opens workspace
  → Scanner walks repository (uses classifiers from plugins)
  → Parser extracts metadata (uses parsers from plugins)
  → Normalizer canonicalizes
  → Resolver resolves references
  → Registry commits entries
  → Authority Builder builds graph
  → Dependency Builder builds graph
  → Ontology Compiler compiles ontology
  → Validator checks invariants (uses invariants from plugins)
  → Indexer builds indexes
  → Storage commits snapshot
Build Session ends

(Later, on demand)
  → Query Engine reads snapshot, answers query
  → Context Compiler reads snapshot, builds package, caches it
```

### 4.3 Failure isolation boundaries

```
Plugin failure     ─► caught at C14 dispatch boundary ─► artifact marked ─► other artifacts continue
Stage failure      ─► caught at pipeline runner ─► diagnostic emitted ─► downstream stages skipped for affected subgraph
Storage failure    ─► caught at commit boundary ─► snapshot not written ─► build session fails cleanly
Validator failure  ─► caught at C9 ─► invariant marked not-checked ─► other invariants continue
```

---

## 5. Component Boundaries (Summary Table)

| Component | Reads from | Writes to | Mutates | Does NOT |
|---|---|---|---|---|
| C1 Scanner | Filesystem | (in-memory) Artifacts | — | Parse, resolve, persist |
| C2 Parser | Artifacts | (in-memory) RawMetadata | — | Canonicalize, resolve |
| C3 Normalizer | RawMetadata | (in-memory) CanonicalMetadata | — | Resolve cross-artifact |
| C4 Resolver | CanonicalMetadata, Registry | (in-memory) resolved refs | — | Build graphs |
| C5 Registry | Resolved artifacts | Registry | Registry entries | Build graphs, validate |
| C6 Authority | Registry | (in-memory) Authority Graph | — | Build dependency graph |
| C7 Dependency | Registry | (in-memory) Dependency Graph | — | Build authority graph |
| C8 Ontology | Registry | (in-memory) Ontology | — | Validate meaning |
| C9 Validator | IR | (in-memory) Validation Report | — | Enforce, mutate IR |
| C10 Indexer | IR | (in-memory) Indexes | — | Answer queries |
| C11 Context | IR, Task, Budget | (cached) Context Package | — | Generate, execute |
| C12 Query | Indexes, IR | (in-memory) results | — | Generate, mutate |
| C13 Storage | Workspace | Workspace, snapshots, caches | Storage state | Interpret contents |
| C14 Plugin | Plugin dir | (in-memory) loaded plugins | Plugin state | Implement extensions |
| C15 CLI | argv | stdout, stderr | — | Implement logic |

---

## 6. Extension Point Catalog

Every extension point has a contract documented in the relevant DESIGN doc. This catalog is the index.

| Extension point | Component | DESIGN doc | What plugins add |
|---|---|---|---|
| Classifier | C1 Scanner | `008` § classifiers, `005` § stage 1 | New artifact kinds |
| Parser | C2 Parser | `008` § parsers, `005` § stage 2 | Parsers for new kinds |
| Inference rule | C3 Normalizer | `008` § inference | Authority / metadata inference rules |
| Resolver strategy | C4 Resolver | `008` § resolvers | New reference resolution strategies |
| Authority edge kind | C6 | `008` § authority-edges | New authority edge types |
| Dependency edge kind | C7 | `008` § dependency-edges | New dependency edge types |
| Ontology edge kind | C8 | `008` § ontology-edges | New ontology edge types |
| Invariant | C9 Validator | `008` § invariants | New invariants / checks |
| Index kind | C10 Indexer | `008` § indexers | New indexes (e.g., vector) |
| Context provider | C11 Context | `008` § providers | New output formats |
| Query kind | C12 Query | `008` § queries | New query types |
| Storage backend | C13 Storage | `008` § storage | New storage backends |

---

## 7. Non-Goals (Component-Level)

- No component depends on a specific LLM, IDE, or runtime.
- No component makes network calls (except plugin-declared `network-loopback` for IPC, per ADR-Candidate-0006).
- No component spawns subprocesses (except plugins with declared `subprocess` capability).
- No component persists state outside the Workspace (C13 owns all persistence).
- No component re-implements another component's responsibility (boundary violations are ADRs).

---

## 8. Open Questions for ADR

Surfaced in `DECISIONS/003-component-architecture-adr-candidates.md`:

1. Should C11 Context Compiler be a separate process or in-process? (Cross-ref ADR-Candidate-0002.)
2. Should C9 Validator run in-pipeline, externally, or both? (Cross-ref ADR-Candidate-0005.)
3. Should C10 Indexer be a stage or a property of Storage?
4. Should C14 Plugin Framework support plugin dependencies (plugin A requires plugin B)?
5. Should C13 Storage support transactions across multiple snapshots?

---

## 9. References

- `ARCHITECTURE.md` — system-level map (this doc is the engineering-grade expansion).
- `DESIGN/005-pipeline.md` — dynamic flow across these components.
- `DESIGN/008-plugin-framework.md` — extension point contracts.
- `DESIGN/009-cli.md` — CLI subcommand surface.