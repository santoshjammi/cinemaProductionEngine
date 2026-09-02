# ADR Candidates — GKC-003 Component Architecture

> Decisions surfaced by `DESIGN/003-component-architecture.md`.

---

## ADR-Candidate-0019 — Context budget allocation policy

**Context.** C11 Context Compiler must allocate a token budget across slices. The policy determines quality.

**Options.**
- **A. Fixed reservations.** `overview: 10%, artifacts: 60%, diagnostics: 5%, graph-excerpts: 25%`. Predictable; rigid.
- **B. Greedy by authority × relevance.** Rank all candidate slices; greedily fill until budget exhausted. Adaptive; may starve overview.
- **C. Tiered.** Reserve a minimum for each category; allocate remainder by B. Hybrid.

**Recommendation.** C. Tiered. Guarantees a minimum overview and diagnostic presence; allocates the bulk adaptively. Matches "authority wins" (§ 8.3 of `DESIGN/001`) while preventing starvation.

**Blocking impact.** Blocks `DESIGN/007`. Must be resolved before M3.

---

## ADR-Candidate-0020 — Plugin sandboxing level

**Context.** C14 Plugin Framework must isolate plugins. How strong is the sandbox?

**Options.**
- **A. Load-time capability check only.** Plugins declare capabilities; runtime trusts the declaration. No runtime enforcement.
- **B. Runtime capability enforcement.** Filesystem, network, and subprocess calls go through framework-provided shims that enforce capabilities.
- **C. Process isolation.** Plugins run in separate processes; IPC via the framework.
- **D. Container/WASM isolation.** Plugins run in WASM or a container.

**Recommendation.** A for M0–M3, B for M4–M5, C/D as a later horizon. Load-time check is sufficient for the core compiler invariants (7.6); runtime enforcement adds defense in depth but is complex. Process isolation is a post-M5 evolution.

**Blocking impact.** Blocks `DESIGN/008`. M0 requires A; M5 requires B.

---

## ADR-Candidate-0021 — Indexer is a stage vs. a Storage property

**Context.** C10 Indexer could be a pipeline stage or a Storage property (indexes computed on snapshot write).

**Options.**
- **A. Stage (current design).** Explicit stage; visible in diagnostics; can fail independently.
- **B. Storage property.** Storage builds indexes on commit; less visible; harder to extend per-kind.
- **C. Both.** Storage builds essential indexes; C10 builds extended indexes via plugins.

**Recommendation.** A. Stage. Indexes are first-class artifacts of the IR; making them a Storage property hides failures and complicates the extension point contract.

**Blocking impact.** Blocks `DESIGN/005` and `DESIGN/010`. Must be resolved before M2.

---

## ADR-Candidate-0022 — Plugin dependencies

**Context.** Can plugin A declare a dependency on plugin B?

**Options.**
- **A. No.** Plugins are independent; if A needs B's behavior, the user installs both and A handles B's absence.
- **B. Yes, declared in manifest.** Framework loads B before A; fails if B is missing.
- **C. Yes, with version constraints.** Like B but with semver constraints.

**Recommendation.** A for M0–M3. No plugin dependencies. Plugin composition is the user's responsibility. Revisit at M5 if real-world plugins need it.

**Blocking impact.** Blocks `DESIGN/008`. Must be resolved before M0.

---

## ADR-Candidate-0023 — Storage transactions across snapshots

**Context.** C13 Storage — should multi-snapshot writes be transactional?

**Options.**
- **A. No.** Each snapshot is atomic; multi-snapshot writes are not supported.
- **B. Yes.** Storage supports a transaction spanning multiple snapshot commits.
- **C. Batch only.** A "batch commit" writes multiple snapshots atomically; no general transactions.

**Recommendation.** A. No multi-snapshot transactions. Each snapshot is atomic (already invariant); multi-snapshot transactions add complexity for no current use case. Cross-repo federation (later horizon) may revisit.

**Blocking impact.** Blocks `DESIGN/010`. Must be resolved before M0.