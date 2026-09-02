# ADR Candidates — GKC-002 Domain Model

> Decisions surfaced by `DESIGN/002-domain-model.md`, awaiting ratification.

---

## ADR-Candidate-0011 — Authority graph stratification formal definition

**Context.** § 3.6 and § 3.9 state the authority graph is "acyclic within a stratum, stratified across strata". This needs a formal definition for the graph builder to enforce.

**Options.**
- **A. Strict level order.** Constitutional=4, statutory=3, guidance=2, deprecated=1, unknown=0. Edges only go from lower to higher (a statutory artifact may reference a constitutional one; the reverse is a violation). Within a level, edges are forbidden (acyclic trivially).
- **B. Partial order with edges within levels.** Edges within a level are allowed but must be acyclic. Edges across levels follow A.
- **C. Typed edges with constraints.** Different edge kinds (`cites`, `implements`, `extends`, `operationalizes`) have different stratification rules.

**Recommendation.** A. Strict level order. Simplest to enforce, easiest to validate, and matches the GENESIS model where authority flows downward. Within-level edges are forbidden; if a within-level relationship is needed, it's a Dependency, not an Authority edge.

**Blocking impact.** Blocks `DESIGN/005` authority graph builder. Must be resolved before M2.

---

## ADR-Candidate-0012 — Multi-version registry entries

**Context.** § 3.8 says Registry Entries are immutable; updates create new entries with new ids and a parent link. Should the registry hold multiple versions simultaneously, or only the latest?

**Options.**
- **A. Multi-version.** The registry holds all versions; queries can request a specific version or the latest. Memory cost; supports history queries.
- **B. Latest-only.** Only the latest version is in the registry; older versions live in snapshot history. Lower memory; history queries require snapshot traversal.
- **C. Multi-version with retention policy.** Multi-version, but old versions are GC'd by a configurable policy.

**Recommendation.** B. Latest-only in the registry; history in snapshots. The registry is the working set; snapshots are the history. This keeps the registry small and matches the snapshot-immutable invariant.

**Blocking impact.** Blocks `DESIGN/004` (data model) and `DESIGN/010` (storage). Must be resolved before M1.

---

## ADR-Candidate-0013 — Repository identity: directory vs git commit

**Context.** § 3.1 says Repository identity is `(root_path, tree_hash)`. Should we also support git-commit-based identity for repositories under git?

**Options.**
- **A. Path + tree hash only.** GKC is git-agnostic; works on any directory.
- **B. Git commit when available.** If the repository is a git repo, identity is `(git remote, commit hash)`; otherwise falls back to A.
- **C. Both, with explicit mode.** Caller chooses; default is A.

**Recommendation.** A. Path + tree hash only. Git coupling adds complexity and breaks the local-first invariant if a remote is referenced. Tree hash already provides content identity; git commit is redundant for GKC's purposes.

**Blocking impact.** Blocks `DESIGN/004`. Must be resolved before M1.

---

## ADR-Candidate-0014 — Context package: single payload vs slice stream

**Context.** § 3.11 models Context Package as having an ordered list of slices. Should the runtime emit it as a single payload or a stream?

**Options.**
- **A. Single payload.** The package is one blob; consumers read it whole. Simple; matches current LLM input conventions.
- **B. Slice stream.** The package is a stream of slices; consumers can stop reading when their budget is exhausted. Efficient for very large packages; complex.
- **C. Both via provider.** The provider decides; built-in providers default to A.

**Recommendation.** C. Both via provider. The Context Package data model is a list of slices (already in the doc); emission is a provider concern. Built-in providers emit a single payload; streaming providers can be added as plugins.

**Blocking impact.** Blocks `DESIGN/007`. Must be resolved before M3.

---

## ADR-Candidate-0015 — Plugins: per-workspace or shared

**Context.** § 3.14 says plugins are registered with a Workspace. Should plugins be installed per-workspace or shared across workspaces?

**Options.**
- **A. Per-workspace.** Each workspace has its own plugin directory. Reproducible per workspace; disk duplication.
- **B. Shared global plugin directory.** One directory; all workspaces see the same plugins. Less duplication; cross-workspace breakage.
- **C. Per-workspace with shared fallback.** Workspace plugins take precedence; global plugins fill in.

**Recommendation.** A. Per-workspace. Reproducibility (a core invariant) requires that a workspace's plugin set be self-contained. Shared plugins break the determinism invariant if a global plugin is updated.

**Blocking impact.** Blocks `DESIGN/008` and the M0 plugin loader. Must be resolved before M0.

---

## ADR-Candidate-0016 — Stable diagnostic identifiers

**Context.** § 3.20 says diagnostics are immutable. Should a diagnostic carry a stable id so the same issue across incremental compilations can be tracked?

**Options.**
- **A. Yes, content-addressed id.** The diagnostic's id is `hash(invariant, artifact, evidence)`. Same issue across runs ⇒ same id. Enables "this issue persists" tracking.
- **B. No.** Diagnostics are ephemeral; tracking is the consumer's job.
- **C. Optional.** Diagnostics may carry an id; not required.

**Recommendation.** A. Content-addressed id. This is required for IDE integration (showing "this issue is the same as last time") and for AIOS to track which diagnostics an agent has already seen. The id is already derivable from the identity tuple in § 3.20; making it explicit costs nothing.

**Blocking impact.** Blocks `DESIGN/005` (diagnostic emission) and IDE integrations. Must be resolved before M2.

---

## ADR-Candidate-0017 — Artifact kind extensibility boundary

**Context.** § 3.2.1 says kinds are an open enum extensible by plugins. Where is the boundary?

**Options.**
- **A. Plugins declare kinds; core knows only built-ins.** Any non-built-in kind must come from a plugin.
- **B. Plugins declare kinds; core recognizes a generic `custom` kind.** Plugin kinds are subtypes of `custom`.
- **C. Free-form.** Any string is a valid kind; validation is the plugin's problem.

**Recommendation.** A. Plugins declare kinds; core knows only built-ins. This keeps the core small and forces kind authors to be explicit. Cross-check with `DESIGN/008` plugin contract.

**Blocking impact.** Blocks `DESIGN/008` and `DESIGN/003` scanner. Must be resolved before M1.

---

## ADR-Candidate-0018 — Ontology namespace policy

**Context.** § 3.10 says namespaces are open and collisions across namespaces are allowed. What about collisions within a namespace?

**Options.**
- **A. Within-namespace collisions are diagnostics.** Two artifacts declaring the same term in the same namespace produce a collision diagnostic.
- **B. Within-namespace collisions merge.** The terms merge into one node with multiple `declared_by`.
- **C. Within-namespace collisions are an error.** Compile fails.

**Recommendation.** B. Merge. Collisions are expected (multiple documents define the same concept); merging models this correctly. The merged node's `declared_by` records all contributors. If the definitions conflict, that's a separate diagnostic at the validation pass.

**Blocking impact.** Blocks `DESIGN/005` ontology compiler. Must be resolved before M2.