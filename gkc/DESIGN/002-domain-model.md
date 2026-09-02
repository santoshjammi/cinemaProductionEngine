# GKC-002 — Domain Model

> Every domain object GKC manipulates, with its ownership, lifecycle, and relationships. This is the **ubiquitous language** of the compiler; every other DESIGN doc uses these terms exactly.

---

## 1. Purpose

Define every domain object GKC knows about. Pin down ownership (who creates it, who mutates it, who destroys it) and lifecycle (what states it transitions through). Resolve naming ambiguity here once, so the rest of the design has a stable vocabulary.

A domain object is **in scope** for this document iff GKC manipulates it as a first-class value. Objects GKC only reads (e.g., a raw file on disk before classification) are mentioned as inputs but not modeled here.

---

## 2. Reading Guide

Each domain object is documented with:

- **Identity** — what makes two instances the same.
- **Fields** — the structured data it carries.
- **Ownership** — which stage/component creates, mutates, and destroys it.
- **Lifecycle** — the states it transitions through.
- **Relationships** — what it links to and how.
- **Invariants** — what must always hold.

Fields are described structurally, not typed. Type contracts are the job of `DESIGN/004`.

---

## 3. Domain Object Index

| # | Object | One-liner |
|---|---|---|
| 3.1 | Repository | The compilation unit's source: a directory tree of artifacts. |
| 3.2 | Artifact | A single classifiable unit in a repository (file, document, schema, etc.). |
| 3.3 | Document | A prose artifact with declared authority and references. |
| 3.4 | Reference | A directed link from one artifact to another, declared or inferred. |
| 3.5 | Metadata | The structured data extracted from an artifact by a parser. |
| 3.6 | Authority | The constitutional weight an artifact carries. |
| 3.7 | Dependency | A structural reliance of one artifact on another. |
| 3.8 | Registry Entry | The persistent, resolved record of one artifact. |
| 3.9 | Knowledge Graph | The union of authority and dependency graphs over a registry. |
| 3.10 | Ontology Node | A domain concept declared in or referenced by an artifact. |
| 3.11 | Context Package | A token-bounded slice of the IR produced for a specific task. |
| 3.12 | Validation Report | The ranked diagnostic set produced by the validation pass. |
| 3.13 | Compilation Unit | A request to compile a repository (or a subgraph) into a snapshot. |
| 3.14 | Plugin | An extension loaded at runtime that adds a capability to a stage. |
| 3.15 | Workspace | The local directory holding snapshots, caches, and plugin state. |
| 3.16 | Repository Snapshot | The persisted, content-addressed IR for one repository at one point in time. |
| 3.17 | Build Session | One invocation of the compiler from CLI or API. |
| 3.18 | Task Descriptor | The description of work an agent wants to do; input to the context compiler. |
| 3.19 | Token Budget | The constraint on context package size, expressed in tokens. |
| 3.20 | Diagnostic | A single immutable finding emitted by any stage or plugin. |

---

## 3.1 Repository

**Identity.** A canonical root path plus a content hash of the full tree at scan time. Two repositories are the same iff their root paths and tree hashes match.

**Fields.**
- `root_path` — absolute, normalized.
- `tree_hash` — content-addressed hash of the scanned tree.
- `scan_time` — normalized to UTC; **not** used for identity.
- `ignore_rules` — the set of path rules under which scan was performed.

**Ownership.**
- Created by: Scanner (stage 1).
- Mutated by: none (immutable once scanned).
- Destroyed by: Workspace GC when no snapshot references it.

**Lifecycle.** `discovered → scanned → hashed → referenced`. A Repository exists as long as at least one Repository Snapshot references its tree hash.

**Relationships.**
- Contains many Artifacts (3.2).
- Backs one or more Repository Snapshots (3.16).

**Invariants.**
- The tree hash is reproducible: scanning the same tree with the same ignore rules yields the same hash.
- The scan time is **never** part of identity or cache keys (per `DESIGN/001` § 7.1).

---

## 3.2 Artifact

**Identity.** A path relative to the repository root, plus a content hash. Two artifacts are the same iff both match.

**Fields.**
- `path` — repository-relative, normalized.
- `content_hash` — content-addressed.
- `kind` — an Artifact Kind (see 3.2.1).
- `size_bytes`.
- `encoding` — text/utf-8, binary, etc.
- `classifier_provenance` — which classifier (built-in or plugin) assigned the kind.

**Ownership.**
- Created by: Scanner (stage 1).
- Mutated by: Parser (fills in `kind` if previously `unknown`), Resolver (fills in stable identifiers).
- Destroyed by: Workspace GC when no Registry Entry references it.

**Lifecycle.** `discovered → classified → parsed → resolved → registered`. An Artifact's lifecycle ends when it becomes a Registry Entry (3.8); the Artifact itself is immutable from then on.

**Relationships.**
- Belongs to one Repository.
- Becomes one Registry Entry.
- Declares zero or more References (3.4).
- Declares zero or more Dependencies (3.7).

**Invariants.**
- `kind` is always set; `unknown` is a valid kind.
- `content_hash` is reproducible from the file contents.
- `path` is reproducible from the repository root.

### 3.2.1 Artifact Kind

An open enum, extensible by plugins. Built-in kinds (M1):

| Kind | Description | Typical parser |
|---|---|---|
| `document` | Prose artifact (Markdown, plain text, etc.) | Document parser |
| `schema` | Structured schema (YAML, JSON, TOML with a schema role) | Schema parser |
| `manifest` | Declares a runtime, contract, or component | Manifest parser |
| `runtime` | Declares or implements a runtime | Runtime parser |
| `contract` | Declares an interface contract | Contract parser |
| `prompt` | A prompt template or prompt artifact | Prompt parser (Horizon 3) |
| `unknown` | Scanner could not classify | Default no-op parser |

Kinds are not mutually exclusive hierarchically; an artifact has exactly one kind. Subtyping is handled by metadata (3.5), not by kind.

---

## 3.3 Document

**Identity.** Inherits identity from its Artifact. A Document **is** an Artifact of kind `document` plus its parsed structure.

**Fields.**
- All fields from Artifact (3.2).
- `authority_level` — see Authority (3.6).
- `heading_tree` — structural outline.
- `declared_references` — references found in the document body.
- `declared_concepts` — ontology terms declared in the document.
- `genesis_reference` — optional GENESIS document id this document operationalizes.

**Ownership.**
- Created by: Parser (stage 2) for kind=document.
- Mutated by: Normalizer (stage 3) for canonical references; Resolver (stage 4) for resolved references.
- Destroyed by: follows Artifact lifecycle.

**Lifecycle.** Follows Artifact lifecycle with an additional `parsed` state holding structural data.

**Relationships.**
- May operationalize one GENESIS document (`genesis_reference`).
- Declares zero or more References.
- Declares zero or more Ontology Nodes.

**Invariants.**
- If `genesis_reference` is set, the referenced GENESIS document exists and is part of the frozen `000`–`018` stack.
- `authority_level` is drawn from the GENESIS stratification (see 3.6).

---

## 3.4 Reference

**Identity.** `(source artifact id, target descriptor, reference kind)`. The target descriptor is pre-resolution text; the target artifact id is post-resolution. Two references are the same iff all three match.

**Fields.**
- `source` — artifact id.
- `target_descriptor` — the unresolved text or path the source declared.
- `target` — resolved artifact id, or `unresolved`.
- `kind` — `citation`, `link`, `implements`, `extends`, `operationalizes`, etc.
- `provenance` — location in the source artifact (line, column, heading path).

**Ownership.**
- Created by: Parser (stage 2).
- Mutated by: Resolver (stage 4) — fills in `target`.
- Destroyed by: follows source Artifact lifecycle.

**Lifecycle.** `declared → resolving → resolved | unresolved`.

**Relationships.**
- One source Artifact.
- One target Artifact (or unresolved).

**Invariants.**
- A Reference is never silently dropped. Unresolved references are emitted as diagnostics.
- `kind` is drawn from an open enum; new kinds require a plugin.

---

## 3.5 Metadata

**Identity.** `(artifact id, schema version)`. Metadata is versioned because parsers evolve.

**Fields.** Varies by Artifact Kind. Common fields:
- `identifier` — the artifact's declared name, normalized.
- `version` — the artifact's declared version.
- `authority_level` — see 3.6.
- `declared_dependencies` — list of dependency descriptors.
- `declared_references` — list of reference descriptors.
- `declared_concepts` — list of ontology term descriptors.
- `parser_provenance` — which parser (built-in or plugin) produced this metadata.

**Ownership.**
- Created by: Parser (stage 2).
- Mutated by: Normalizer (stage 3) — canonicalizes identifiers and fields.
- Destroyed by: follows Artifact lifecycle.

**Lifecycle.** `raw → normalized → frozen`. Frozen when the Registry Entry is written.

**Relationships.** Belongs to one Artifact.

**Invariants.**
- Metadata schema is self-describing (per ADR-Candidate-0001).
- Metadata is immutable once the Registry Entry is written.

---

## 3.6 Authority

**Identity.** A value from a stratified, finite enum. Two artifacts have the same authority iff their levels match.

**Levels (from GENESIS stratification).**

| Level | Source | Examples |
|---|---|---|
| `constitutional` | GENESIS `000`–`018` | Constitution, runtime architecture, registry architecture |
| `statutory` | GKC design docs, ratified ADRs | DESIGN docs, ADRs |
| `guidance` | Non-binding guidance | Tutorials, guides, examples |
| `deprecated` | Marked deprecated | Anything with `status: deprecated` |
| `unknown` | Default when not declared | Any artifact without an authority declaration |

**Ownership.**
- Created by: Parser (extracts declared authority).
- Mutated by: Normalizer (canonicalizes to the enum).
- Destroyed by: follows Artifact lifecycle.

**Lifecycle.** `declared | inferred | unknown`. `inferred` means GKC assigned the level from artifact context (e.g., a document under `docs/genesis/` defaults to `constitutional`); `inferred` is always marked with provenance.

**Relationships.** Belongs to one Artifact. Aggregated into the Authority Graph (3.9).

**Invariants.**
- Authority stratification is acyclic across levels: `constitutional` > `statutory` > `guidance` > `deprecated`. `unknown` is treated as `guidance` for graph purposes but flagged.
- Inference is always marked; never silently assigned.

---

## 3.7 Dependency

**Identity.** `(source artifact id, target descriptor, dependency kind)`. Post-resolution, the target descriptor becomes a target artifact id.

**Fields.**
- `source` — artifact id.
- `target_descriptor` — pre-resolution.
- `target` — post-resolution artifact id, or `unresolved`.
- `kind` — `requires`, `uses`, `implements`, `extends`, `composed-of`, etc.
- `strength` — `hard` (compile fails if missing) or `soft` (warning).
- `provenance` — location in source.

**Ownership.**
- Created by: Parser (declared dependencies).
- Mutated by: Resolver (resolves target).
- Destroyed by: follows source Artifact lifecycle.

**Lifecycle.** `declared → resolving → resolved | unresolved`. Hard unresolved dependencies are fatal diagnostics; soft ones are warnings.

**Relationships.** Source and target Artifacts. Aggregated into the Dependency Graph (3.9).

**Invariants.**
- Hard cycles are detected and reported. Soft cycles are reported but not fatal.
- A Dependency is distinct from a Reference: a Reference is informational; a Dependency is structural. Both may exist between the same pair.

---

## 3.8 Registry Entry

**Identity.** A stable, content-addressed identifier: `hash(metadata + content_hash + version)`. Two entries are the same iff their identifiers match.

**Fields.**
- `id` — the stable identifier.
- `artifact` — the underlying Artifact.
- `metadata` — the frozen Metadata.
- `authority` — the Authority level.
- `references` — resolved References.
- `dependencies` — resolved Dependencies.
- `concepts` — declared Ontology Nodes.
- `registered_at` — normalized UTC; **not** part of identity.
- `schema_version` — registry schema version.

**Ownership.**
- Created by: Registry (stage 5).
- Mutated by: Graph builders (stages 6–8) add derived edges; the entry itself is immutable.
- Destroyed by: Workspace GC when no snapshot references it.

**Lifecycle.** `registered → indexed → graphed → validated`. Entries are immutable; new versions create new entries.

**Relationships.**
- Belongs to one Repository Snapshot.
- Participates in Authority Graph, Dependency Graph, Ontology.
- Source/target of References and Dependencies.

**Invariants.**
- Registry Entries are content-addressed: same inputs ⇒ same id.
- Entries are immutable. Updates create new entries with new ids and a parent link.
- An entry's `schema_version` matches the snapshot's schema version.

---

## 3.9 Knowledge Graph

**Identity.** `(snapshot id, graph kind)` where graph kind ∈ {`authority`, `dependency`, `ontology`}.

**Fields.**
- `kind` — which graph.
- `nodes` — set of Registry Entry ids.
- `edges` — typed, directed edges.
- `edge_metadata` — per-edge: provenance, weight, declared-vs-inferred.

**Ownership.**
- Created by: Graph builders (stages 6, 7, 8).
- Mutated by: none (immutable once built).
- Destroyed by: follows Repository Snapshot lifecycle.

**Lifecycle.** `building → built → validated`. Validation may mark edges as `invalid` without removing them.

**Relationships.** Belongs to one Repository Snapshot.

**Invariants.**
- Authority graph: acyclic within a stratum, stratified across strata (per ADR-Candidate-0011).
- Dependency graph: cycles are detected and reported; soft cycles allowed.
- Ontology graph: edges are typed (e.g., `is-a`, `part-of`, `references`); untyped edges are invalid.

---

## 3.10 Ontology Node

**Identity.** `(snapshot id, term, namespace)`. Two nodes are the same iff all three match.

**Fields.**
- `term` — the canonical term.
- `namespace` — the namespace the term belongs to (e.g., `genesis`, `gkc`, `runtime`).
- `declared_by` — set of Registry Entry ids that declare this term.
- `referenced_by` — set of Registry Entry ids that reference this term.
- `aliases` — set of non-canonical terms mapped to this node.
- `definition` — optional, drawn from the declaring artifact.

**Ownership.**
- Created by: Ontology compiler (stage 8).
- Mutated by: none (immutable per snapshot).
- Destroyed by: follows Repository Snapshot lifecycle.

**Lifecycle.** `declared → linked → validated`.

**Relationships.** Participates in the Ontology Graph (3.9).

**Invariants.**
- Every `alias` resolves to exactly one canonical node.
- A term with no `declared_by` is reported as a diagnostic (orphan reference).
- Namespaces are open; collisions across namespaces are allowed.

---

## 3.11 Context Package

**Identity.** `(task descriptor hash, snapshot id, token budget, provider id)`. Two packages are the same iff all four match.

**Fields.**
- `task` — the Task Descriptor (3.18).
- `snapshot` — the Repository Snapshot the package was built from.
- `token_budget` — the budget in effect.
- `provider` — the context provider (built-in or plugin) that emitted the package.
- `slices` — ordered list of Context Slices (3.11.1).
- `total_tokens` — actual token count.
- `cache_key` — derived from the identity tuple.

**Ownership.**
- Created by: Context Compiler (stage 11 / on-demand).
- Mutated by: none (immutable once emitted).
- Destroyed by: Cache GC under LRU policy.

**Lifecycle.** `composing → slicing → expanding → budgeting → emitting → cached`.

**Relationships.** Built from one Repository Snapshot. Consumed by one or more AI agents.

**Invariants.**
- The package is **dependency-closed**: every artifact the slices reference is either included or transitively reachable from included slices.
- The package is **authority-aware**: higher-authority artifacts are preferred under budget pressure.
- The package is **provider-stable**: same identity tuple ⇒ byte-identical package.

### 3.11.1 Context Slice

A unit of context: one or more registry entries rendered through a provider template. Slices have:
- `kind` — `overview`, `artifact`, `graph-excerpt`, `definition`, `diagnostic`.
- `entries` — the registry entries in this slice.
- `tokens` — token count of the rendered slice.
- `rank` — priority within the package.

---

## 3.12 Validation Report

**Identity.** `(snapshot id, validator version, run config hash)`.

**Fields.**
- `snapshot` — the Repository Snapshot being validated.
- `diagnostics` — ordered list of Diagnostics (3.20), ranked.
- `summary` — counts by severity.
- `invariants_checked` — list of invariant ids.
- `validator_version`.

**Ownership.**
- Created by: Validation pass (stage 9, in-pipeline) or external `gkc validate`.
- Mutated by: none (immutable once emitted).
- Destroyed by: follows Repository Snapshot lifecycle.

**Lifecycle.** `running → ranked → frozen`.

**Relationships.** Belongs to one Repository Snapshot.

**Invariants.**
- Diagnostics are ordered by a total order: `(severity, artifact_id, invariant_id, evidence_hash)`.
- The report is deterministic for a fixed `(snapshot, validator version, run config)`.

---

## 3.13 Compilation Unit

**Identity.** A build-session-local id; not persisted. Two compilation units are the same iff their session ids and local ids match.

**Fields.**
- `repository` — the Repository to compile.
- `target_snapshot` — the snapshot to produce or update.
- `incremental_from` — optional prior snapshot id.
- `configuration` — compile configuration (plugins, profile, etc.).
- `requested_stages` — subset of stages to run (for partial compilation).

**Ownership.**
- Created by: Build Session (3.17).
- Mutated by: Pipeline runner (advances stage state).
- Destroyed by: Build Session end.

**Lifecycle.** `queued → running → completed | failed`. Per-stage state is tracked on the unit.

**Relationships.** Owned by one Build Session. Produces one Repository Snapshot.

**Invariants.**
- `requested_stages` is a downward-closed subset of the pipeline DAG (you cannot run stage 6 without stages 1–5).

---

## 3.14 Plugin

**Identity.** `(plugin id, version)`. Plugin ids are reverse-DNS or namespaced identifiers.

**Fields.**
- `id`, `version`.
- `declared_capabilities` — set of `filesystem-read`, `filesystem-write`, `network-loopback`, `network-external`, `subprocess`, etc.
- `extension_points` — which stages this plugin extends (scanner, parser, graph, context-provider, validator, etc.).
- `declared_invariants` — invariants the plugin claims to respect (used by load-time check).
- `integrity_hash` — content-addressed hash of the plugin package.

**Ownership.**
- Created by: plugin author.
- Loaded by: Plugin Loader (at Build Session start).
- Destroyed by: Build Session end (unloaded).

**Lifecycle.** `discovered → integrity-checked → capability-checked → loaded → active → unloaded`.

**Relationships.** Registered with one Workspace (3.15).

**Invariants.**
- A plugin may not exceed its declared capabilities; violations are fatal at load time.
- Plugin integrity is verified before load.
- A plugin failure during a stage is recoverable per-artifact (per ADR-Candidate-0003).

---

## 3.15 Workspace

**Identity.** A canonical root directory path. Two workspaces are the same iff their paths match.

**Fields.**
- `root_path`.
- `snapshots` — set of snapshot ids present.
- `caches` — set of stage-cache entries.
- `plugins` — set of registered Plugin ids.
- `config` — workspace configuration.
- `lock` — advisory lock for concurrent build sessions.

**Ownership.**
- Created by: `gkc init` (user).
- Mutated by: Build Sessions, plugin installs, GC.
- Destroyed by: user deletion.

**Lifecycle.** `initialized → active → idle → gc-running → active`. Workspaces are long-lived.

**Relationships.** Contains many Repository Snapshots. Hosts many Plugins.

**Invariants.**
- Concurrent build sessions serialize on the workspace lock or work on isolated snapshot branches.
- A Workspace never holds state for two different GKC major versions simultaneously without explicit migration.

---

## 3.16 Repository Snapshot

**Identity.** A content-addressed hash of `(repository tree hash, plugin set hash, configuration hash, GKC version)`. Two snapshots are the same iff their hashes match.

**Fields.**
- `id` — the hash.
- `repository` — the Repository it was built from.
- `registry` — the set of Registry Entry ids.
- `graphs` — the three Knowledge Graphs.
- `ontology` — the set of Ontology Nodes.
- `indexes` — query indexes (search, traversal).
- `validation_report` — the Validation Report.
- `parent` — optional prior snapshot this one incrementally derives from.
- `schema_version`.

**Ownership.**
- Created by: Build Session (end of pipeline).
- Mutated by: none (immutable once written).
- Destroyed by: Workspace GC.

**Lifecycle.** `building → sealed → referenced → gc-eligible`. Sealed snapshots are immutable.

**Relationships.** Belongs to one Workspace. Derives from zero or one parent snapshot.

**Invariants.**
- Snapshots are immutable and content-addressed (per ADR-Candidate-0004).
- `parent` chains form a tree rooted at a full (non-incremental) snapshot.
- A snapshot's `schema_version` is self-describing (per ADR-Candidate-0001).

---

## 3.17 Build Session

**Identity.** A UUID-like id, generated per invocation. Not persisted across runs.

**Fields.**
- `id`.
- `workspace`.
- `started_at` — normalized UTC; not part of identity.
- `compilation_units` — set of Compilation Units in this session.
- `plugins` — set of loaded Plugins.
- `log` — structured event log; not part of any snapshot.

**Ownership.**
- Created by: CLI invocation or API call.
- Mutated by: Pipeline runner.
- Destroyed by: session end.

**Lifecycle.** `initializing → plugins-loaded → running → committing → ended | aborted`.

**Relationships.** Owned by one Workspace. Produces zero or more Repository Snapshots.

**Invariants.**
- A session is single-threaded with respect to snapshot commits (two sessions can compile in parallel into different snapshot branches).
- Session logs are not part of the IR; they do not affect determinism.

---

## 3.18 Task Descriptor

**Identity.** A content-addressed hash of the descriptor's canonical form.

**Fields.**
- `description` — natural-language task description.
- `target_artifacts` — optional set of artifact ids the task is about.
- `target_concepts` — optional set of ontology terms.
- `requested_authority` — optional minimum authority level.
- `requested_format` — context provider id (e.g., `markdown`, `anthropic-xml`).
- `model_profile` — target LLM profile (context window size, tool-use support).

**Ownership.**
- Created by: caller (CLI, AIOS, plugin).
- Mutated by: Context Compiler (fills in derived fields like expanded concepts).
- Destroyed by: caller.

**Lifecycle.** `declared → expanded → compiled-against`.

**Relationships.** Input to the Context Compiler.

**Invariants.**
- The descriptor's canonical form is deterministic: same description + same options ⇒ same hash.
- `model_profile` is required at compile time; defaults are filled in by the Context Compiler.

---

## 3.19 Token Budget

**Identity.** A value with units (tokens, not bytes). Two budgets are the same iff their token counts and reservation policies match.

**Fields.**
- `total` — total token budget.
- `reservations` — per-category reservations (e.g., `overview: 500`, `artifacts: 60%`, `diagnostics: 200`).
- `overflow_policy` — `truncate`, `summarize`, `drop-lowest-authority`, `fail`.

**Ownership.**
- Created by: caller or default profile.
- Mutated by: Context Compiler (applies reservations).
- Destroyed by: follows Task Descriptor.

**Lifecycle.** `declared → applied → exhausted | satisfied`.

**Relationships.** Inputs to Context Compiler.

**Invariants.**
- The budget is **deterministic**: same budget + same IR ⇒ same allocation.
- Reservations sum to ≤ `total`; overflow policy handles the remainder.

---

## 3.20 Diagnostic

**Identity.** `(artifact id, stage id, invariant id, evidence hash)`. Two diagnostics are the same iff all four match.

**Fields.**
- `artifact` — the offending artifact id (or `workspace` for workspace-level).
- `stage` — which stage emitted it.
- `severity` — `constitutional-violation | error | warning | info`.
- `invariant` — the invariant id violated (e.g., `genesis-001 § 7.1`).
- `evidence` — the evidence (snippet, path, value).
- `resolution` — suggested resolution.
- `provenance` — location in the artifact.

**Ownership.**
- Created by: any stage or plugin.
- Mutated by: Validation pass (ranks them); otherwise immutable.
- Destroyed by: follows Repository Snapshot lifecycle (or session, if session-only).

**Lifecycle.** `emitted → ranked → frozen`.

**Relationships.** Aggregated into Validation Reports.

**Invariants.**
- Diagnostics are immutable once emitted (per `DESIGN/001` § 7.5).
- Every diagnostic references a specific invariant or `unspecified-invariant` (the latter is itself a warning).

---

## 4. Ownership Matrix

| Object | Created by | Mutated by | Destroyed by |
|---|---|---|---|
| Repository | Scanner | — | Workspace GC |
| Artifact | Scanner | Parser, Resolver | Workspace GC |
| Document | Parser | Normalizer, Resolver | follows Artifact |
| Reference | Parser | Resolver | follows Artifact |
| Metadata | Parser | Normalizer | follows Artifact |
| Authority | Parser | Normalizer | follows Artifact |
| Dependency | Parser | Resolver | follows Artifact |
| Registry Entry | Registry | (immutable; graph edges derived) | Workspace GC |
| Knowledge Graph | Graph builders | — | follows Snapshot |
| Ontology Node | Ontology compiler | — | follows Snapshot |
| Context Package | Context Compiler | — | Cache GC |
| Validation Report | Validation | — | follows Snapshot |
| Compilation Unit | Build Session | Pipeline | Session end |
| Plugin | Author | — (immutable) | Session end |
| Workspace | User (`gkc init`) | Sessions, GC | User |
| Repository Snapshot | Build Session | — (immutable) | Workspace GC |
| Build Session | CLI/API | Pipeline | Session end |
| Task Descriptor | Caller | Context Compiler | Caller |
| Token Budget | Caller/Profile | Context Compiler | follows Task |
| Diagnostic | Stages/Plugins | Validation (rank only) | follows Snapshot/Session |

---

## 5. Lifecycle State Machines (Summary)

```
Artifact:      discovered → classified → parsed → resolved → registered
Reference:     declared → resolving → resolved | unresolved
RegistryEntry: registered → indexed → graphed → validated
Snapshot:      building → sealed → referenced → gc-eligible
Plugin:        discovered → integrity-checked → capability-checked → loaded → active → unloaded
BuildSession:  initializing → plugins-loaded → running → committing → ended | aborted
CompilationUnit: queued → running → completed | failed
ContextPackage: composing → slicing → expanding → budgeting → emitting → cached
Diagnostic:    emitted → ranked → frozen
```

---

## 6. Relationship Map (High-Level)

```
Workspace ──contains──► Repository Snapshots
                          │
                          ├──► Registry ──► Registry Entries
                          │                  │
                          │                  ├──► References ──► target Entry
                          │                  ├──► Dependencies ──► target Entry
                          │                  └──► Concepts ──► Ontology Nodes
                          │
                          ├──► Knowledge Graphs (authority, dependency, ontology)
                          ├──► Indexes
                          └──► Validation Report ──► Diagnostics

Build Session ──produces──► Repository Snapshot
                          (via Compilation Units)

Task Descriptor + Token Budget ──► Context Compiler ──► Context Package
                                  (reads from Snapshot)

Plugin ──extends──► (any stage or provider)
```

---

## 7. Invariants Cross-Reference

| Invariant | Source |
|---|---|
| All domain objects have stable, content-addressed identity | `DESIGN/001` § 7.1 (determinism) |
| All lifecycles are finite and named | `DESIGN/001` § 7.2 (staging) |
| All cross-object links are typed and explicit | `DESIGN/001` § 7.2 |
| Plugin failures do not destroy domain objects | `DESIGN/001` § 7.6 |
| Diagnostics are immutable | `DESIGN/001` § 7.5 |
| Snapshots are immutable and content-addressed | ADR-Candidate-0004 |
| IR is self-describing | ADR-Candidate-0001 |

---

## 8. Open Questions for ADR

Surfaced in `DECISIONS/002-domain-model-adr-candidates.md`:

1. Should `Repository` be modeled per-directory or per-git-commit?
2. Should `Registry Entry` support multiple versions simultaneously (multi-version registry)?
3. Should `Context Package` be a single payload or a stream of slices?
4. Should `Plugin` instances be shared across Workspaces or per-Workspace?
5. Should `Diagnostic` carry a stable identifier across incremental compilations?