# 008 — GENESIS Compiler Architecture

**Status:** Architectural Specification — Phase II
**Version:** 1.0.0
**Date:** 2026-07-21
**Derives Authority From:** `006` (Constitution, Tier 0); `001` §4.2 (the canonical compiler pipeline, Tier 2); `007` (CIR, the compiler's input, Tier 2); `004` (COM, the object model the compiler operates on, Tier 2); `002` Part 7 (Director↔Compiler boundary, Tier 2).
**Precedence:** Below the Constitution. Below the constitutional specifications that define the compiler's context. This specification is the full architectural realization of the compiler concept introduced in `001` §4.2 and constitutionalized by `006` (L-11, L-12, L-13).
**Scope:** The compiler's philosophy, pipeline, pass architecture, scheduling, dependency resolution, optimization, incremental compilation, partial compilation, caching, diagnostics, recovery, plugins, extension points, governance, and migration.

---

## Table of Contents

1. [Compiler Philosophy](#1-compiler-philosophy)
2. [Compiler Pipeline](#2-compiler-pipeline)
3. [Pass Architecture](#3-pass-architecture)
4. [Scheduling](#4-scheduling)
5. [Dependency Resolution](#5-dependency-resolution)
6. [Optimization](#6-optimization)
7. [Incremental Compilation](#7-incremental-compilation)
8. [Partial Compilation](#8-partial-compilation)
9. [Caching](#9-caching)
10. [Compiler Diagnostics](#10-compiler-diagnostics)
11. [Recovery](#11-recovery)
12. [Compiler Plugins](#12-compiler-plugins)
13. [Compiler Extension Points](#13-compiler-extension-points)
14. [Governance](#14-governance)
15. [Migration](#15-migration)

---

# 1. Compiler Philosophy

## 1.1 Compilation Over Generation

The ACI Platform compiles rather than generates (`00` §3.2, `006` L-13). The distinction is architectural:

- **Generation** implies the model is the author; the output is emergent, unpredictable, and unrepeatable.
- **Compilation** implies the specification is the author; the output is deterministic given the same specification and the same providers. The model is a compiler pass, not a creative agent.

The GENESIS Compiler is the architectural realization of this principle. It transforms the CIR (`007`) — the structured representation of creative decisions — into the PKP (`009`) — the executable production specification — through a deterministic pipeline of passes. The compiler does not generate; it compiles.

## 1.2 Determinism

The compiler is deterministic (`006` L-13): given the same frozen CIR and the same provider versions, it produces the same PKP. Determinism is achieved through:

- **Seed-based reproducibility.** Every model invocation in a compiler pass carries an explicit seed, recorded in the pass's provenance. The same seed + same inputs → same output.
- **No hidden state.** The compiler carries no state between runs except the CIR (input) and the PKP (output). There is no "compiler memory" that could vary across runs.
- **Provider versioning.** The compiler records the provider versions used (model versions, configuration versions) in the PKP's provenance. Replay pins these versions.

## 1.3 The Compiler Never Invents Creativity

The compiler is constitutionally prohibited from inventing creative content (`006` L-12, `002` Part 7.1). Every output of every pass must trace to a frozen CIR node via `cir_origin` (`007` Part 10.4). If a pass finds it cannot produce its output without a creative decision that is not in the CIR, the pass **fails loudly** (`00` §3.7) and re-enters the Directorial Board at the appropriate director. It does not invent.

This is the architectural enforcement of the separation of creative and technical authority (`00` §3.3): the Board decides; the compiler executes; neither crosses the boundary.

## 1.4 Constitutional Derivation

| Law | How it governs the compiler |
|-----|----------------------------|
| L-11 (Decision Precedes Compilation) | The compiler may not run before the CIR is frozen. |
| L-12 (Compilation Never Invents Creativity) | Every pass output traces to a CIR node; no invention. |
| L-13 (Production Knowledge Is Compiled) | The PKP is the deterministic output of compiling the CIR. |
| L-19 (History Is Immutable) | A frozen PKP is immutable; recompilation creates a new PKP version. |

---

# 2. Compiler Pipeline

## 2.1 The Canonical Pipeline

The canonical compiler pipeline is defined in `001` §4.2. This specification architecturalizes it: the pipeline is a sequence of passes, each consuming CIR nodes and producing PKP artifacts, governed by dependency order.

```
Frozen CIR (007)
   │
   ▼
┌─────────────────────────────────────────────────────────────┐
│  PRE-COMPILATION                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ CIR Loader    │  │ Profile       │  │ Dependency       │   │
│  │               │  │ Resolver      │  │ Analyzer         │   │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────┘   │
│         └──────────────────┴──────────────────────┘         │
│                            │                                │
└────────────────────────────┼────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  COMPILER PASSES (in dependency order, per 001 §4.2)         │
│                                                              │
│  01. Story Compiler                                          │
│  02. Narrative Compiler                                      │
│  03. Screenplay Compiler                                     │
│  04. Director Compiler                                       │
│  05. Scene Compiler                                          │
│  06. Shot Compiler                                           │
│  07. Dialogue Compiler                                       │
│  08. Emotion Compiler                                        │
│  09. Character Compiler                                      │
│  10. Camera Compiler                                         │
│  11. Lighting Compiler                                       │
│  12. Music Compiler                                          │
│  13. Audio Compiler                                          │
│  14. Voice Compiler                                          │
│  15. Timeline Compiler                                       │
│  16. Prompt Compiler                                         │
│  17. Production Package Assembly                             │
│  18. Validation Gate                                         │
│  19. Freeze + Hash                                           │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
                     Production Knowledge Package (PKP, 009)
                     (frozen, versioned, hashed)
```

## 2.2 The Pre-Compilation Stage

Before the passes run, the pre-compilation stage prepares the compilation context:

| Step | What it does |
|------|-------------|
| **CIR Loader** | Loads the frozen CIR from ATLAS; verifies the CIR hash; verifies the CIR is in the `frozen` state. |
| **Profile Resolver** | Resolves the production profile and the Creative Profile from the CIR Root. |
| **Dependency Analyzer** | Traverses the CIR's `depends_on` edges to build the compilation dependency graph (Part 5). |

The pre-compilation stage is read-only with respect to the CIR. It may not modify the CIR.

## 2.3 Pass Execution

The passes execute in dependency order (Part 5). Each pass:

1. Reads its input CIR nodes (the decisions owned by the pass's directors, per `001` §4.2).
2. Reads the COM objects in reasoning state that those decisions authorize.
3. Transforms the reasoning-state objects into executable-state objects.
4. Stamps each output PKP artifact with `cir_origin` (referencing the authorizing CIR node) and `cir_hash` (the CIR's hash).
5. Validates its output against the pass's validation rules (`001` §4.2).
6. Emits its output to the PKP-in-progress.

## 2.4 The Validation Gate and Freeze

Pass 18 (Validation Gate) validates the assembled PKP against:

- The COM invariants (`004` Part 5) for executable-state objects.
- The constitutional laws (`006` L-12: no invention; every artifact has `cir_origin`).
- The production profile's constraints (runtime envelope, scene count, etc.).

Pass 19 (Freeze + Hash) freezes the PKP, computes the PKP hash, and records the CIR hash and provider versions in the PKP's provenance. The frozen PKP is persisted to ATLAS.

---

# 3. Pass Architecture

## 3.1 The Pass Contract

Every compiler pass is specified by a ten-field contract:

| Field | Definition |
|-------|-----------|
| **Pass identifier** | `pass:<ordinal>:<name>` (e.g., `pass:01:story_compiler`). |
| **Input CIR nodes** | The CIR node types the pass consumes (the decisions owned by the pass's directors). |
| **Output PKP artifacts** | The PKP artifacts the pass produces. |
| **Dependencies** | Which passes must complete before this pass. |
| **Validation rules** | What the pass validates on its output. |
| **Fast mode** | The fast-mode implementation (`001` §4.2 fast-mode column). |
| **Deep mode** | The deep-mode implementation (`001` §4.2 deep-mode column). |
| **CIR directors** | The directors whose decisions this pass compiles. |
| **PKP mapping** | Which PKP specifications the pass produces. |
| **Determinism requirements** | The seed and provider-version requirements for deterministic replay. |

## 3.2 The Pass Catalog

The pass catalog is the 19-pass pipeline from `001` §4.2, architecturalized. Each pass's full contract is specified in `001` §4.2 (Pass 01 through Pass 19); this specification does not repeat those contracts but binds them to the CIR-compiler interface (Part 12 of `007`):

| Pass | Input CIR nodes (directors) | Output PKP artifacts | PKP mapping |
|------|----------------------------|----------------------|-------------|
| 01 Story | Story Director's decisions | Story specification | PKP-04 |
| 02 Narrative | Narrative Director's decisions | Narrative specification | PKP-09 |
| 03 Screenplay | Narrative Director's decisions (screenplay subset) | Screenplay specification | PKP-09 (screenplay subset) |
| 04 Director | Chief + Visual Directors' decisions | Directorial language specification | PKP-10 |
| 05 Scene | Narrative + Story Directors' decisions | Scene specifications | PKP-09 (scene subset) + PKP-15 |
| 06 Shot | Cinematography Director's decisions | Shot specifications | PKP-15 (shot subset) |
| 07 Dialogue | Dialogue Director's decisions | Dialogue plans | PKP-12 (dialogue subset) |
| 08 Emotion | Psychology Director's decisions | Emotional specifications | PKP-08 (emotion subset) |
| 09 Character | Character + Psychology Directors' decisions | Character, relationship, psychology specifications | PKP-06, PKP-07, PKP-08 |
| 10 Camera | Cinematography Director's decisions (camera subset) | Camera specifications | PKP-10 (camera subset) |
| 11 Lighting | Lighting Director's decisions | Lighting specifications | PKP-10 (lighting) + PKP-11 |
| 12 Music | Music Director's decisions | Music direction | PKP-12 (music subset) |
| 13 Audio | Sound Director's decisions | Audio direction | PKP-12 (SFX subset) |
| 14 Voice | Performance + Dialogue Directors' decisions (voice subset) | Voice direction | PKP-12 (voice subset) |
| 15 Timeline | Editorial Director's decisions | Timeline | PKP-15 (timeline) + PKP-18 |
| 16 Prompt | Visual + Cinematography + Lighting + Production Design Directors' decisions | Cinematic prompts | PKP-15 (prompt subset) |
| 17 Package Assembly | (integration; no new decisions) | Assembled PKP | PKP-00..18 |
| 18 Validation Gate | (validation; no new decisions) | Validation report | (internal) |
| 19 Freeze + Hash | (freeze; no new decisions) | Frozen PKP with hash | (internal) |

## 3.3 Pass Isolation

Each pass is **isolated**: a pass reads only its input CIR nodes and the outputs of prior passes (via the PKP-in-progress). A pass does not read other passes' internal state, does not communicate with other passes directly, and does not modify the CIR. Passes communicate only through the PKP-in-progress.

This isolation is what enables:

- **Incremental compilation** (Part 7): only changed passes re-run.
- **Parallelism** (Part 4): independent passes run concurrently.
- **Determinism** (Part 1.2): no hidden cross-pass state.

---

# 4. Scheduling

## 4.1 Dependency-Driven Scheduling

Passes are scheduled by the Dependency Analyzer (Part 2.2) based on the CIR's `depends_on` graph and the pass dependency graph. The scheduling rules:

1. **Dependency order.** A pass may not execute until all passes it depends on have completed.
2. **Parallelism.** Passes with no inter-dependency may execute concurrently. (e.g., Pass 09 Character and Pass 07 Dialogue may run concurrently if their CIR dependencies are satisfied.)
3. **Deterministic order.** When passes are independent and concurrent, their outputs are merged in a deterministic order (by pass identifier) to ensure replay determinism.

## 4.2 The Compilation Dependency Graph

The compilation dependency graph is derived from two sources:

- **The pass dependency graph**: which passes depend on which (per `001` §4.2, "Dependencies" column).
- **The CIR dependency graph**: which CIR nodes depend on which (per `007` Part 4, the CDG's `depends_on` edges).

The combined graph determines the execution order. A pass may not execute until:

- All passes it depends on have completed, AND
- All CIR nodes its input depends on are available (i.e., the passes producing those nodes' outputs have completed).

## 4.3 Scheduling and the Profile

The production profile and the Creative Profile (`002` Part 9) influence scheduling:

- **Fast mode** (`001` §4.2): some passes are skipped or merged (e.g., Pass 06 Shot is not executed in fast mode; shots are implicit in the scene's camera field). The scheduler respects the mode.
- **Deep mode**: all passes execute; the scheduler runs the full pipeline.

The mode is recorded in the PKP's provenance for replay.

---

# 5. Dependency Resolution

## 5.1 The Dependency Resolver

The Dependency Analyzer (Part 2.2) builds the compilation dependency graph by traversing:

1. The CIR's `depends_on` edges (from CIR node to CIR node).
2. The pass dependency graph (from pass to pass).
3. The COM object `belongs_to` and `contains` edges (from object to parent object).

The resolver produces a **topological order** of passes and CIR nodes, respecting:

- **Acyclicity.** The dependency graph must be acyclic (`004` I-SI-15). A cycle is a compile-time error (Part 10).
- **Completeness.** Every CIR node the compiler needs must be present and frozen. A missing node is a compile-time error.
- **`cir_origin` availability.** A pass may not produce a PKP artifact until the CIR node that authorizes it is available.

## 5.2 Dependency-Driven Incremental Compilation

The dependency graph is the basis for incremental compilation (Part 7). When a CIR node changes (a new CIR version is created for a revised decision):

1. The Dependency Analyzer identifies the passes that consume that CIR node.
2. Those passes are marked for recompilation.
3. The Dependency Analyzer traverses the `depends_on` graph downstream to identify passes that depend on the recompiled passes' outputs.
4. Those passes are also marked for recompilation.
5. Passes not reachable from the changed node are not recompiled; their prior PKP artifacts are reused.

This is the architectural basis for surgical revision: a single scene's lighting change recompiles only the Lighting pass and the passes that depend on lighting (Prompt, Timeline), not the entire pipeline.

---

# 6. Optimization

## 6.1 Within-Profile Optimization

The compiler may optimize within the bounds of the CIS's constraints (`003` D-22), the production profile, and the Creative Profile (`002` Part 9). Optimization is **not creative**: it does not invent content; it selects among the alternatives the CIR provides or adjusts execution parameters within the CIR's authorized envelope.

Examples of legitimate optimization:

- **Pacing optimization**: within the runtime envelope (CIS D-10), the Timeline pass may adjust scene durations to better match the emotional curve, provided the adjustment stays within the CIR's authorized durations.
- **Prompt optimization**: the Prompt pass may refine a cinematic prompt for a specific provider within the CIR's authorized visual language, provided the refinement does not change the creative intent.

## 6.2 What Optimization May Not Do

Optimization may not:

- Invent creative content not authorized by a CIR node (L-12).
- Violate a CIS constraint (L-2, L-14).
- Exceed the runtime envelope.
- Change the emotional journey's resolution.
- Override a human-locked CIR node.

Any optimization that would do any of these is a compile-time error (Part 10).

## 6.3 Optimization and the Creative Metrics

The compiler's optimization targets the Creative Metrics (`002` Part 11) where they are compile-time measurable (e.g., pacing curve fit, runtime envelope compliance). ORACLE (`011`) measures the post-render metrics; the compiler optimizes the compile-time proxies.

---

# 7. Incremental Compilation

## 7.1 The Incremental Compilation Model

Incremental compilation is the architectural realization of surgical revision (`007` Part 10.5). When a CIR is revised (a new CIR version is created for a subset of changed decisions):

1. The compiler loads the new CIR version and the prior PKP version.
2. The Dependency Analyzer identifies the changed CIR nodes (by comparing the new and old CIR versions).
3. The Dependency Analyzer traverses the `depends_on` graph from the changed nodes to identify the affected passes.
4. Only the affected passes re-execute; their outputs replace the corresponding prior PKP artifacts.
5. Unaffected PKP artifacts are retained from the prior PKP version.

## 7.2 Incremental Compilation and Determinism

Incremental compilation preserves determinism: the recompiled passes use the same seeds and provider versions as the original compilation (recorded in the prior PKP's provenance). The new PKP's hash differs from the prior PKP's hash only in the artifacts produced by the recompiled passes.

## 7.3 Incremental Compilation and Provenance

Every PKP artifact in an incrementally compiled PKP carries:

- `cir_origin`: the CIR node that authorized it.
- `cir_hash`: the hash of the CIR version it was compiled from.
- `prior_artifact`: the prior PKP artifact it replaces (if any), for audit.

This provenance allows ORACLE to verify that the incremental compilation correctly identified and recompiled the affected artifacts.

---

# 8. Partial Compilation

## 8.1 Subset Compilation

Partial compilation is the compilation of a subset of the CIR — for example, a single scene, or a single character — without compiling the entire production. Partial compilation is used for:

- **Preview**: compiling a single scene for review before the full CIR is frozen (requires a partial freeze; see below).
- **Revision**: recompiling a single scene after a CIR revision (a special case of incremental compilation, Part 7).
- **Localization**: recompiling the dialogue and prompt passes for a localized version without recompiling the visual passes.

## 8.2 Partial Freeze

Partial compilation requires a **partial freeze**: the CIR nodes for the subset being compiled must be frozen, even if the rest of the CIR is not. The Chief Director may declare a partial freeze for a subset of the CIR; the partial freeze is recorded on the CIR Root with the subset's scope.

A partially frozen CIR may be partially compiled; the compiler compiles only the frozen subset. The unfrozen rest of the CIR is not compiled.

## 8.3 Partial Compilation and the PKP

A partial compilation produces a **partial PKP** — a PKP containing only the artifacts for the compiled subset. A partial PKP is marked `partial` with the subset's scope; it is not a complete production and may not be rendered as a complete work by PROMETHEUS. Partial PKPs are merged into a complete PKP when the full CIR is frozen and the remaining passes execute.

---

# 9. Caching

## 9.1 The Compilation Cache

The compiler maintains a **compilation cache** — a store of prior pass outputs keyed by (CIR node hash, pass identifier, provider versions). The cache enables:

- **Replay determinism.** A cached pass output is reused on recompilation with the same inputs, ensuring identical output.
- **Incremental compilation.** Unchanged passes reuse their cached outputs.
- **Performance.** Passes do not re-execute when their inputs have not changed.

## 9.2 Cache Keys

The cache key for a pass output is: `(cir_node_hash, pass_identifier, provider_versions, profile_version, creative_profile_version)`. If any component of the key changes, the cache entry is invalid and the pass re-executes.

## 9.3 Cache Storage

The compilation cache is persisted by ATLAS (`012`), keyed by the production identity. The cache survives session restarts, enabling long-running productions to resume compilation without re-executing completed passes.

## 9.4 Cache and Determinism

The cache is a performance optimization, not a determinism mechanism. Determinism is guaranteed by seed-based reproducibility (Part 1.2), not by the cache. A cache miss triggers a re-execution that produces the same output as the cached entry, because the inputs and seeds are identical.

---

# 10. Compiler Diagnostics

## 10.1 Diagnostic Classes

The compiler produces diagnostics during compilation:

| Class | Severity | Example |
|-------|----------|---------|
| **Error** | Compilation halts. | A pass cannot produce its output because a required CIR node is missing. |
| **Warning** | Compilation continues; the warning is recorded. | A pass optimized within the envelope but near its boundary. |
| **Info** | Informational; recorded for audit. | A pass reused a cached output. |
| **Drift** | The pass detected that a CIR node's content implies creative content the CIR does not explicitly authorize. | The Story pass found that the story implies a character not in the CIR. Drift is a warning unless it violates L-12, in which case it is an error. |

## 10.2 Diagnostic Reporting

Diagnostics are reported to:

- **The compiler's caller** (the human or the runtime operator): via the compilation report.
- **The PKP**: warnings and infos are recorded in the PKP's compilation provenance.
- **ORACLE** (`011`): errors and drift are reported for post-compilation validation.
- **The Directorial Board** (`002`): drift and errors that require a CIR amendment are reported to the Board for re-entry.

## 10.3 The Compilation Report

Every compilation produces a **compilation report** — a structured record of the compilation, including:

- The CIR version and hash compiled from.
- The PKP version and hash produced.
- The passes executed (and their cache status: hit/miss).
- The provider versions used.
- All diagnostics (errors, warnings, infos, drift).
- The compilation duration.

The report is persisted in ATLAS with the PKP, enabling audit and replay verification.

---

# 11. Recovery

## 11.1 Pass Failure

When a pass fails (produces an error diagnostic, Part 10), the compiler:

1. Halts the failed pass.
2. Records the failure in the compilation report.
3. Determines whether the failure is recoverable.

A failure is **recoverable** if the pass's output is not required by any subsequent pass (i.e., the failure is in a leaf pass). A failure is **unrecoverable** if the pass's output is required by a subsequent pass.

## 11.2 Recoverable Failure

For a recoverable failure, the compiler:

1. Marks the failed pass's output as `failed` in the PKP-in-progress.
2. Continues compilation of the remaining passes.
3. Produces a partial PKP with the failed pass's output marked `failed`.
4. Reports the failure to the Board for CIR amendment.

The partial PKP may not be rendered by PROMETHEUS until the failure is resolved (the failed artifact is either recompiled after a CIR amendment or explicitly overridden by the human).

## 11.3 Unrecoverable Failure

For an unrecoverable failure, the compiler:

1. Halts compilation entirely.
2. Records the failure in the compilation report.
3. Produces no PKP.
4. Reports the failure to the Board for CIR amendment.

The Board re-enters the CIR at the failed decision, amends it, and the compiler re-runs (incrementally, per Part 7, recompiling only the affected passes).

## 11.4 The Recovery Loop

The recovery loop is:

```
Compilation fails
   │
   ▼
Compiler reports failure to Board
   │
   ▼
Board re-enters CIR at the failed decision
   │
   ▼
CIR is amended (new version)
   │
   ▼
Compiler re-runs incrementally (only affected passes)
   │
   ▼
Compilation succeeds OR fails again (loop)
```

The recovery loop is bounded by human oversight: if the loop fails repeatedly, the human intervenes (`006` L-25) to amend the CIR or the CIS directly.

---

# 12. Compiler Plugins

## 12.1 Runtime-Specific Passes

The compiler supports **plugins** — runtime-specific passes that extend the canonical pipeline. A plugin pass:

- Is governed under the Constitution (Part 13).
- Reads CIR nodes (like any pass).
- Produces PKP artifacts (like any pass).
- Is stamped with `cir_origin` (like any pass).
- Does not invent creativity (L-12).

Example plugin passes:

- A cinema-runtime plugin: a Subtitle pass that produces subtitle artifacts from the dialogue plans.
- A future game-runtime plugin: an Interactivity pass that produces interaction specifications from the narrative decisions.
- A future book-runtime plugin: a Typography pass that produces typographic specifications from the screenplay.

## 12.2 Plugin Registration

Plugins are registered with the compiler via a governed registry (Part 13). A plugin declares:

- Its pass identifier.
- Its input CIR node types.
- Its output PKP artifact types.
- Its dependencies (which passes must precede it).
- Its runtime binding (which runtimes it applies to).

The compiler's scheduler (Part 4) includes registered plugin passes in the compilation dependency graph.

## 12.3 Plugins and Determinism

Plugins are subject to the same determinism requirements as canonical passes (Part 1.2): seed-based reproducibility, no hidden state, provider versioning. A plugin that is non-deterministic is non-compliant.

---

# 13. Compiler Extension Points

## 13.1 Governed Extension

The compiler's extension points are governed under the Constitution (`006` Part 8.1):

| Extension | Authority | Process |
|-----------|-----------|---------|
| **New canonical pass** | Constitutional amendment (affects the pipeline defined in `001` §4.2). | Per `006` Part 8.1. |
| **New plugin pass** | Architectural amendment to this specification. | Per the specification amendment process; the plugin must satisfy the plugin contract (Part 12.2). |
| **New optimization** | Architectural amendment to this specification. | Per the specification amendment process; the optimization must honor Part 6.2. |
| **New diagnostic class** | Architectural amendment to this specification. | Per the specification amendment process. |

## 13.2 Extension and the COM

A new pass (canonical or plugin) may not introduce new COM object types (`004` Part 10.2). New types are added to the COM under `004`'s governance, not under the compiler's. The compiler consumes and produces COM types; it does not define them.

## 13.3 Extension and the CIR

A new pass may not read CIR nodes that do not exist. If a pass requires a new CIR node type, the CIR's architecture (`007` Part 14) is amended first, then the pass is added. The compiler follows the CIR; it does not lead it.

---

# 14. Governance

## 14.1 Compiler Evolution

The compiler's architecture (this specification) evolves under the ACI Constitution:

| Change type | Authority |
|--------------|-----------|
| **Pipeline change** (add/remove/reorder canonical passes) | Constitutional amendment (affects `001` §4.2 and L-13). |
| **Pass contract change** | Architectural amendment to this specification and to `001` §4.2. |
| **Plugin registry change** | Architectural amendment to this specification. |
| **Optimization policy change** | Architectural amendment to this specification. |

## 14.2 Compatibility

| Concern | Rule |
|---------|------|
| **Backward compatibility** | A new compiler version must be able to compile an archived CIR (producing the same PKP, given the same provider versions). |
| **Forward compatibility** | The compiler leaves extension points (plugins, Part 12) for future runtimes. |
| **Cross-runtime compatibility** | The canonical pipeline is cinema-specific (the 19 passes map to cinema's directors). A future runtime defines its own pipeline, using the compiler's architecture (pass contract, scheduling, dependency resolution, caching) but its own passes. The compiler's architecture is runtime-independent; the canonical pipeline is cinema-specific. |

## 14.3 Constitutional Compliance

| Law | Compliance |
|-----|------------|
| L-11 (Decision Precedes Compilation) | The compiler reads only frozen CIRs (Part 2.2). |
| L-12 (Compilation Never Invents Creativity) | Every pass output traces to a CIR node (Part 2.3); drift is detected (Part 10.1). |
| L-13 (Production Knowledge Is Compiled) | The PKP is the deterministic output of the compiler (Part 1.2). |
| L-19 (History Is Immutable) | A frozen PKP is immutable; recompilation creates a new PKP version. |

---

# 15. Migration

## 15.1 Integration Principles

| # | Principle | Statement |
|---|-----------|-----------|
| MI-1 | **The compiler is additive.** This spec architecturalizes the compiler concept from `001` §4.2; it does not redefine it. |
| MI-2 | **The compiler reads the CIR (`007`).** It does not read the CIS, does not consume enrichments, does not render media. |
| MI-3 | **The compiler produces the PKP (`009`).** Every artifact carries `cir_origin`. |
| MI-4 | **The compiler preserves the four-pillar boundaries.** It is inside GENESIS; it is not a pillar. |
| MI-5 | **The compiler is deterministic.** Same CIR + same providers → same PKP. |

## 15.2 Migration Phases

### Phase COMP-1 — Pass Contract Documentation
- Document the 19-pass contracts (Part 3.2) bound to the CIR-compiler interface.
- Cross-reference each pass to its CIR directors and PKP outputs.

### Phase COMP-2 — Dependency Resolver
- Implement the Dependency Analyzer (Part 5).
- Implement dependency-driven scheduling (Part 4).

### Phase COMP-3 — Incremental Compilation
- Implement incremental compilation (Part 7) via `depends_on` traversal.
- Implement partial compilation (Part 8) for previews and revisions.

### Phase COMP-4 — Caching
- Implement the compilation cache (Part 9) in ATLAS.
- Implement cache-key computation and invalidation.

### Phase COMP-5 — Diagnostics and Recovery
- Implement the diagnostic classes (Part 10).
- Implement the recovery loop (Part 11).

### Phase COMP-6 — Plugin Architecture
- Implement the plugin registry (Part 12.2).
- Implement plugin scheduling within the dependency graph.

## 15.3 Backward Compatibility

| Existing artifact | Compatibility | Action |
|-------------------|---------------|--------|
| `001` §4.2 (19 passes) | **Preserved and architecturalized.** | None. |
| `007` (CIR) | **Preserved.** The compiler reads the CIR per the contract. | Wire the compiler to the CIR (Phase COMP-1). |
| `004` (COM) | **Preserved.** The compiler operates on COM objects. | None. |
| `002` Part 7 (Director↔Compiler boundary) | **Preserved and enforced.** | None. |

## 15.4 Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Provider non-determinism.** A provider (LLM, diffusion model) is non-deterministic despite seeding. | High | The compiler records provider versions; replay pins versions. Where a provider is irreducibly non-deterministic, the compiler records the specific output used, enabling replay from the recorded output rather than from the provider. |
| **Pass coupling.** Passes may become coupled through implicit dependencies, breaking isolation. | Medium | Pass isolation (Part 3.3) is enforced; passes communicate only through the PKP-in-progress. Code review enforces. |
| **Cache coherence.** The cache may return stale outputs if the key is incomplete. | Medium | The cache key (Part 9.2) includes all inputs (CIR hash, pass ID, provider versions, profile versions); a stale entry is impossible if the key is complete. |
| **Plugin proliferation.** Too many plugins may make the pipeline unmanageable. | Low | Plugins are governed (Part 13); the registry is reviewed. |

---

## Architectural Rules (Restated)

This specification produced no implementation code. It architecturalizes the GENESIS Compiler as a deterministic, pass-based, dependency-driven compiler that transforms the CIR into the PKP, governed by constitutional laws L-11, L-12, L-13, and L-19.

---

## Cross-References

| Reference | Relevance |
|-----------|-----------|
| `006` (Constitution) | L-11, L-12, L-13, L-19 govern the compiler. |
| `001` §4.2 | The canonical 19-pass pipeline; architecturalized in Part 3. |
| `007` (CIR) | The compiler's input; the CIR-compiler contract (Part 12 of `007`). |
| `009` (PKP) | The compiler's output. |
| `004` (COM) | The object model the compiler operates on. |
| `002` Part 7 | The Director↔Compiler boundary; L-12 enforcement. |
| `002` Part 9 | Creative Profiles influence fast/deep mode. |
| `002` Part 11 | Creative metrics are the optimization target (Part 6). |
| `010` (PROMETHEUS) | The runtime that renders the compiler's PKP output. |
| `011` (ORACLE) | The validator that checks the compiler's output. |
| `012` (ATLAS) | The persistence layer for the CIR, PKP, and compilation cache. |

---

**End of Specification.**