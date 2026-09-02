# 009 — Production Knowledge Package (PKP) Architecture

**Status:** Architectural Specification — Phase II
**Version:** 1.0.0
**Date:** 2026-07-21
**Derives Authority From:** `006` (Constitution, Tier 0); `001` §5 (the canonical PKP definition, Tier 2); `008` (Compiler, which produces the PKP, Tier 2); `007` (CIR, from which the PKP is compiled, Tier 2); `004` (COM, the object model the PKP is written in, Tier 2).
**Precedence:** Below the Constitution. Below the constitutional specifications that define the PKP's context. This specification is the full architectural realization of the PKP concept introduced in `001` §5 and constitutionalized by `006` (L-13, L-14, L-18, L-19).
**Scope:** The PKP's architecture, artifact model, dependency graph, identifiers, ownership, regeneration, incremental updates, packaging, distribution, validation, compilation outputs, runtime contracts, governance, and lifecycle.

---

## Table of Contents

1. [Architecture](#1-architecture)
2. [Artifact Model](#2-artifact-model)
3. [Dependency Graph](#3-dependency-graph)
4. [Identifiers](#4-identifiers)
5. [Ownership](#5-ownership)
6. [Regeneration](#6-regeneration)
7. [Incremental Updates](#7-incremental-updates)
8. [Packaging](#8-packaging)
9. [Distribution](#9-distribution)
10. [Validation](#10-validation)
11. [Compilation Outputs](#11-compilation-outputs)
12. [Runtime Contracts](#12-runtime-contracts)
13. [Governance](#13-governance)
14. [Lifecycle](#14-lifecycle)

---

# 1. Architecture

## 1.1 The PKP as the Compiled Binary

In the compiler metaphor (`00` §3.2, `007` Part 1.1), the PKP is the **compiled binary**: the deterministic, executable specification that PROMETHEUS (`010`) renders into media. The PKP carries **what to render**; it does not carry *why* (that is the CIR's, `007`) or *what the human wants* (that is the CIS's, `003`).

| Artifact | Carries | Does not carry |
|----------|---------|----------------|
| **CIS** | What the human wants. | Decisions, rationale, executable specifications. |
| **CIR** | Decisions and rationale. | Executable specifications, media. |
| **PKP** | **Executable specifications (what to render).** | **Rationale, media.** |
| **Media** | Rendered output. | Specifications, rationale. |

## 1.2 The PKP as a Graph

The PKP is a **typed graph** of Creative Artifacts (`004` §2.3.53) in executable state. It is a subgraph of the PKG (GFS-003), using the COM's identity scheme and the PKG's immutable-revision semantics. The PKP's graph structure:

```
PKP Root
   │
   ├── references the frozen CIR version and hash (007 Part 9.2)
   ├── references the compiler version and provider versions (008 Part 10.3)
   ├── carries the PKP version and hash (Part 8)
   │
   ├── Artifact Subgraph
   │      ├── Story artifacts (PKP-04)
   │      ├── Narrative artifacts (PKP-09)
   │      ├── Directorial language artifacts (PKP-10)
   │      ├── Scene artifacts (PKP-09/15)
   │      ├── Shot artifacts (PKP-15)
   │      ├── Dialogue artifacts (PKP-12)
   │      ├── Character artifacts (PKP-06/07/08)
   │      ├── Camera artifacts (PKP-10)
   │      ├── Lighting artifacts (PKP-10/11)
   │      ├── Music artifacts (PKP-12)
   │      ├── Audio artifacts (PKP-12)
   │      ├── Voice artifacts (PKP-12)
   │      ├── Timeline artifacts (PKP-15/18)
   │      ├── Prompt artifacts (PKP-15)
   │      └── ... (per the 19-pass pipeline, 008 Part 3.2)
   │
   └── Compilation Provenance Subgraph
          ├── per-artifact cir_origin (007 Part 10.4)
          ├── per-artifact pass identifier
          ├── per-artifact provider versions
          └── the compilation report (008 Part 10.3)
```

## 1.3 PKP Partitions

The PKP is partitioned for rendering and validation:

| Partition | Contents | Consumer |
|-----------|----------|----------|
| **Root** | CIR reference, compiler reference, PKP version and hash. | PROMETHEUS (entry point); ORACLE (validation entry point). |
| **Artifacts** | The executable specifications, grouped by pass. | PROMETHEUS (rendering); ORACLE (validation). |
| **Compilation Provenance** | `cir_origin` per artifact; provider versions; compilation report. | ORACLE (audit); ATLAS (persistence). |

## 1.4 Constitutional Derivation

| Law | How it governs the PKP |
|-----|------------------------|
| L-13 (Production Knowledge Is Compiled) | The PKP is the deterministic output of compiling the CIR. |
| L-14 (Execution Never Changes Intent) | PROMETHEUS may not alter the PKP; the PKP is the frozen executable. |
| L-18 (Knowledge Outlives Media) | The PKP is canonical knowledge; media is a derived projection. |
| L-19 (History Is Immutable) | A frozen PKP is immutable; recompilation creates a new PKP version. |

---

# 2. Artifact Model

## 2.1 The PKP Artifact Contract

Every PKP artifact is specified by a ten-field contract:

| Field | Definition |
|-------|-----------|
| **Identity** | `pkp:<production-id>:<artifact-type>:<ordinal>[@<revision>]`, extending the COM's identity scheme (`004` Part 2.1). |
| **Type** | A COM object type (`004` Part 2.2) in executable state (e.g., Scene, Shot, Dialogue, Camera, Lighting, Music, Timeline). |
| **`cir_origin`** | The CIR node (`007` Part 4) that authorized this artifact. Mandatory (L-11, `004` I-SI-21). |
| **`cir_hash`** | The hash of the CIR version this artifact was compiled from. |
| **Pass** | The compiler pass (`008` Part 3.2) that produced this artifact. |
| **Provider versions** | The model and configuration versions used to produce this artifact (for replay). |
| **State** | `compiled / frozen / rendered / validated / archived`. |
| **Dependencies** | Other PKP artifacts this artifact depends on (mirroring the CIR's `depends_on`). |
| **Consumers** | Which PROMETHEUS component (`010`) renders this artifact; which ORACLE validator (`011`) validates it. |
| **Provenance** | Full compilation provenance: pass, CIR node, provider versions, timestamp. |

## 2.2 Artifact Types

PKP artifacts are COM objects (`004` Part 2) in executable state. The artifact types map to the 19 PKP specifications (PKP-00..18, `docs/genesis/specifications/pkp/`):

| PKP spec | Artifact type | Producing pass |
|----------|--------------|----------------|
| PKP-00 (Vision) | Vision (compiled from the Story Director's theme decision) | Pass 01 (Story) |
| PKP-04 (Story) | Story (compiled) | Pass 01 |
| PKP-09 (Narrative) | Narrative, Act, Sequence, Screenplay (compiled) | Pass 02, 03 |
| PKP-10 (Directorial Language) | Visual Language, Camera, Lighting (compiled) | Pass 04, 10, 11 |
| PKP-11 (Production Design) | Environment, Location (compiled) | Pass 11 (lighting subset) + Pass 16 (prompt subset) |
| PKP-12 (Audio Intent) | Dialogue, Music, Soundscape, Voice (compiled) | Pass 07, 12, 13, 14 |
| PKP-15 (Production Blueprint) | Scene, Shot, Timeline, Prompt (compiled) | Pass 05, 06, 15, 16 |
| PKP-06 (Character) | Character (compiled) | Pass 09 |
| PKP-07 (Relationship) | Relationship (compiled) | Pass 09 |
| PKP-08 (Psychology) | Psychology, Emotion (compiled) | Pass 08, 09 |
| PKP-16 (Distribution) | Platform constraints (compiled) | Pass 15 (timeline subset) |
| PKP-17 (Quality) | Quality specifications (compiled) | Pass 18 (validation gate) |
| PKP-18 (Knowledge Graph) | PKG nodes for the compiled artifacts | Pass 17 (package assembly) |

## 2.3 Artifact State

PKP artifacts transition through states:

```
compiled → frozen → rendered → validated → archived
```

- **compiled**: the artifact has been produced by a compiler pass.
- **frozen**: the PKP has been frozen (Part 8); the artifact is immutable.
- **rendered**: PROMETHEUS has rendered media from the artifact.
- **validated**: ORACLE has validated the rendered media against the artifact.
- **archived**: the artifact (and its media) is persisted in ATLAS.

---

# 3. Dependency Graph

## 3.1 PKP Artifact Dependencies

PKP artifacts depend on each other, mirroring the CIR's `depends_on` graph (`007` Part 4). If CIR node A `depends_on` CIR node B, and pass X compiles A into PKP artifact P_A, and pass Y compiles B into PKP artifact P_B, then P_A `depends_on` P_B.

The PKP's dependency graph is the compiled projection of the CIR's dependency graph. It is acyclic (`004` I-SI-15) and is the basis for:

- **Incremental updates** (Part 7): a changed artifact's dependents are recompiled.
- **Rendering order** (`010`): PROMETHEUS renders artifacts in dependency order.
- **Validation order** (`011`): ORACLE validates artifacts in dependency order.

## 3.2 Cross-Partition Dependencies

Artifacts may depend on artifacts in other partitions (e.g., a Shot artifact depends on a Scene artifact; a Timeline artifact depends on Scene, Shot, Dialogue, Music, Audio, and Voice artifacts). The dependency graph spans the PKP's partitions; it is not partition-local.

## 3.3 Dependency and `cir_origin`

Every dependency edge in the PKP mirrors a `depends_on` edge in the CIR. This means:

- From a PKP artifact, the platform can enumerate the PKP artifacts it depends on (downstream in the CIR) and the PKP artifacts that depend on it (upstream in the CIR).
- From a PKP artifact's `cir_origin`, the platform can traverse to the CIR node and its dependencies.

This bidirectional traceability is what enables surgical revision (`007` Part 10.5): a drift report on a PKP artifact names the artifact; the artifact's `cir_origin` names the CIR node; the CIR node's `depends_on` graph identifies the affected nodes; the affected nodes' PKP artifacts are the ones to recompile.

---

# 4. Identifiers

## 4.1 The PKP Identity Scheme

PKP artifacts use the COM's identity scheme (`004` Part 2.1), extended with a `pkp:` prefix to distinguish executable-state objects from reasoning-state objects:

`pkp:<production-id>:<artifact-type>:<ordinal>[@<revision>]`

Examples:
- `pkp:ew001:scene:07` — Scene 7's executable specification.
- `pkp:ew001:shot:07.03` — Shot 3 of Scene 7's executable specification.
- `pkp:ew001:dialogue:07.02` — Dialogue line 2 of Scene 7.

## 4.2 Relationship to CIR and COM Identities

The PKP identity is related to but distinct from the CIR and COM identities:

| Identity | Form | State |
|----------|------|-------|
| COM (generic) | `com:<prod>:<type>:<ordinal>` | Type-level (any state). |
| CIR (reasoning) | `cir:<prod>:<director>:<node-type>:<ordinal>` | Reasoning state (a decision). |
| PKP (executable) | `pkp:<prod>:<type>:<ordinal>` | Executable state (a compiled artifact). |

A PKP artifact's `cir_origin` references the CIR identity; the PKP identity is the executable-state projection of the same underlying COM object. The three identities are linked via `cir_origin` and the COM's identity scheme, enabling traversal across all three layers.

## 4.3 PKP Root Identifier

The PKP Root has the identifier `pkp:<production-id>:root`, carrying the CIR version, the compiler version, the PKP version, and the PKP hash.

---

# 5. Ownership

## 5.1 Production Ownership

Each PKP artifact is produced by exactly one compiler pass (`008` Part 3.2) and is owned by that pass. The pass's identifier is recorded on the artifact.

## 5.2 Consumption Ownership

Each PKP artifact is consumed by:

- **PROMETHEUS** (`010`): renders the artifact into media.
- **ORACLE** (`011`): validates the rendered media against the artifact.

The consumption contract is specified in Part 12.

## 5.3 No Shared Authorship

A PKP artifact has exactly one producing pass. No artifact is co-authored by multiple passes. If two passes contribute to a single artifact, the artifact is split into two artifacts with a dependency between them. This preserves the single-authorship invariant that enables `cir_origin` traceability and incremental compilation.

---

# 6. Regeneration

## 6.1 Full Regeneration

Full regeneration recompiles the entire CIR into a new PKP. This is the default when:

- A new production is compiled for the first time.
- The CIR is revised in a way that affects the root or a large subset of the dependency graph.
- The provider versions change (requiring recompilation for the new provider's output).

Full regeneration produces a new PKP version with a new hash. The prior PKP version is retained (L-19).

## 6.2 Regeneration and Determinism

Full regeneration is deterministic: the same CIR + the same provider versions → the same PKP (same hash). This is the constitutional guarantee of L-13, architecturally enforced by the compiler's seed-based reproducibility and provider-version recording (`008` Part 1.2).

## 6.3 Regeneration from an Archived PKP

An archived PKP can be regenerated from its archived CIR (referenced by the PKP Root's `cir_hash`) and the archived provider versions (recorded in the PKP's compilation provenance). This enables:

- **Media regeneration**: if media is lost, the PKP can be re-rendered by PROMETHEUS.
- **PKP regeneration**: if the PKP is lost, it can be recompiled from the CIR.
- **Cross-provider regeneration**: the same CIR can be compiled with different providers (e.g., a newer model) to produce a new PKP version, enabling quality comparison.

Cross-provider regeneration is the architectural basis for the platform's model independence (`00` §3.4): the creative work (CIS, CIR) is provider-independent; the PKP is provider-specific but regenerable from the CIR with any provider.

---

# 7. Incremental Updates

## 7.1 The Incremental Update Model

When a CIR is revised (a new CIR version for a subset of changed decisions, `007` Part 9), the PKP is updated incrementally (`008` Part 7):

1. The compiler identifies the changed CIR nodes (by comparing CIR versions).
2. The compiler identifies the PKP artifacts produced from those nodes (via `cir_origin`).
3. The compiler identifies the downstream PKP artifacts (via the PKP's dependency graph, Part 3).
4. Only the affected artifacts are recompiled; unaffected artifacts are retained from the prior PKP.
5. The new PKP version contains: recompiled affected artifacts + retained unaffected artifacts.

## 7.2 Incremental Update Provenance

Every artifact in an incrementally updated PKP carries:

- `cir_origin`: the CIR node (unchanged for retained artifacts; new for recompiled artifacts).
- `cir_hash`: the hash of the CIR version (new for all artifacts, since the CIR version changed).
- `prior_artifact`: the prior PKP artifact this one replaces (for recompiled artifacts; null for retained artifacts).
- `recompiled`: a boolean indicating whether this artifact was recompiled in this version.

This provenance allows ORACLE to verify that the incremental update correctly identified and recompiled the affected artifacts, and that the unaffected artifacts are genuinely unchanged (their `prior_artifact` chain is intact).

## 7.3 Incremental Update and the PKP Hash

The PKP hash (Part 8) changes on every incremental update, because the CIR hash changes (the CIR version changed) and the recompiled artifacts' content changes. The hash is computed over the complete PKP graph state, including retained artifacts, ensuring the hash uniquely identifies the PKP version.

---

# 8. Packaging

## 8.1 The PKP Assembly

PKP assembly is Pass 17 of the compiler pipeline (`008` Part 3.2). It:

1. Collects all artifacts produced by passes 01–16.
2. Verifies that every artifact carries `cir_origin` (L-11, `004` I-SI-21).
3. Verifies that the dependency graph is acyclic and complete (`004` I-SI-15).
4. Assembles the artifacts into the PKP graph.
5. Produces the PKP Root with the CIR reference, compiler reference, and compilation provenance.

## 8.2 The PKP Freeze

PKP freeze is Pass 19 of the compiler pipeline. It:

1. Runs the Validation Gate (Pass 18, Part 10) on the assembled PKP.
2. If validation passes, transitions all artifacts to the `frozen` state.
3. Computes the PKP hash (Part 8.3).
4. Records the PKP version and hash on the Root.
5. Persists the frozen PKP to ATLAS (`012`).
6. Notifies PROMETHEUS (`010`) that the PKP is frozen and ready for rendering.

## 8.3 The PKP Hash

The PKP hash is a cryptographic hash over the PKP's complete graph state: all artifacts, all dependency edges, all `cir_origin` references, the CIR hash, and the compiler/provenance metadata. The hash is recorded on the PKP Root.

The hash is the basis for:

- **Replay verification** (`011`): ORACLE verifies that the PKP hash matches the hash recorded in the compilation report.
- **Media verification** (`010`): PROMETHEUS records the PKP hash it rendered from; ORACLE verifies the match.
- **Audit** (`011`): the PKP hash uniquely identifies a production's executable specification at a point in time.

## 8.4 PKP Versioning

PKP versions follow GFS-003 (immutable revisions): `pkp:<production-id>:v<major>.<minor>.<patch>`. A frozen PKP is immutable; recompilation creates a new version. Versions form a lineage via `amends` edges, mirroring the CIR's version lineage.

---

# 9. Distribution

## 9.1 The PKP-PROMETHEUS Handoff

The PKP is distributed to PROMETHEUS (`010`) via ATLAS (`012`):

1. The frozen PKP is persisted to ATLAS.
2. PROMETHEUS reads the PKP from ATLAS (by PKP identity and version).
3. PROMETHEUS renders the PKP into media.
4. PROMETHEUS writes the media to ATLAS with provenance referencing the PKP.

The handoff is **artifact-based, not call-based** (`001` §2.3): PROMETHEUS does not call the compiler; it reads the PKP from ATLAS. This preserves the four-pillar boundary.

## 9.2 The PKP-ORACLE Handoff

The PKP is distributed to ORACLE (`011`) via ATLAS:

1. ORACLE reads the PKP from ATLAS (the same PKP PROMETHEUS rendered).
2. ORACLE reads the rendered media from ATLAS.
3. ORACLE validates the media against the PKP.
4. ORACLE writes validation reports to ATLAS, referencing the PKP and the media.

## 9.3 The PKP-Human Handoff

The human may inspect the PKP via the Semantic Query Model (`004` Part 7.1):

- `lookup(pkp-artifact-id)`: inspect any artifact.
- `traceability(pkp-artifact-id)`: traverse to the CIR node (`cir_origin`) and to the CIS.
- `impact_analysis(pkp-artifact-id)`: enumerate the media rendered from this artifact.

The human may not amend the PKP directly; amendments go through the CIR (re-compilation). The human may override ORACLE's validation report (accepting media that ORACLE flagged), but the override is recorded and does not alter the PKP.

---

# 10. Validation

## 10.1 Pre-Freeze PKP Validation (Pass 18)

Before the PKP is frozen, the Validation Gate (Pass 18, `008` Part 3.2) validates:

| Check | Law | Effect on failure |
|-------|-----|-------------------|
| Every artifact carries `cir_origin`. | L-11, I-SI-21 | Blocking. |
| Every artifact's `cir_origin` references a frozen CIR node. | L-11 | Blocking. |
| The dependency graph is acyclic. | I-SI-15 | Blocking. |
| The COM invariants (`004` Part 5) hold for executable-state objects. | L-5 | Blocking. |
| The runtime envelope (total duration, scene count) is within the production profile. | — | Blocking. |
| Every scene has a duration; durations sum to total runtime. | I-SI-23, I-SI-40 | Blocking. |
| Every speaking character has voice direction. | I-SI-22 | Blocking. |

## 10.2 Post-Render Validation (ORACLE)

After PROMETHEUS renders the PKP into media, ORACLE (`011`) validates:

- **Structural validation**: does the media match the PKP structurally (right scene count, right durations, all characters present)?
- **Visual consistency**: do characters look the same across scenes?
- **Emotional arc adherence**: does the rendered video's emotional trajectory match the PKP's emotional arc?
- **Continuity**: are props, wardrobe, blocking, and lighting continuous across scenes?
- **Drift detection**: did PROMETHEUS produce any media content not traceable to a PKP artifact (and thus not traceable to a CIR node)?
- **Quality scoring**: aggregate quality across visual, audio, narrative, emotional, and technical dimensions.

ORACLE's drift reports reference PKP artifacts (by identity) and, via `cir_origin`, the CIR nodes that authorized them. A drift report is the trigger for surgical revision (Part 7, `007` Part 10.5).

## 10.3 Validation and the Constitution

PKP validation enforces:

| Law | How |
|-----|-----|
| L-12 (Compilation Never Invents Creativity) | Pre-freeze: every artifact has `cir_origin`. Post-render: drift detection. |
| L-14 (Execution Never Changes Intent) | Post-render: media is compared to the PKP; divergence is drift. |
| L-17 (Validation Is Against Intent and Decisions) | ORACLE validates media against the PKP (which traces to the CIR and the CIS). |

---

# 11. Compilation Outputs

## 11.1 The 19 PKP Specifications

The PKP's compilation outputs are the 19 PKP specifications (PKP-00..18) defined in `docs/genesis/specifications/pkp/`. Each PKP specification is the compiled projection of one or more CIR decision domains:

| PKP spec | Title | CIR source (directors) |
|----------|-------|------------------------|
| PKP-00 | Vision Specification | Chief Director (theme, message, reflection) |
| PKP-01 | Creative Strategy Specification | Chief Director (creative profile, strategy) |
| PKP-02 | Project Specification | (production profile; not director-authored) |
| PKP-03 | Research Specification | (discovery; not director-authored) |
| PKP-04 | Story Specification | Story Director |
| PKP-05 | World Specification | Production Designer (world subset) |
| PKP-06 | Character Specification | Character Director |
| PKP-07 | Relationship Specification | Character Director (relationship subset) |
| PKP-08 | Psychology Specification | Psychology Director |
| PKP-09 | Narrative Specification | Narrative Director |
| PKP-10 | Directorial Language Specification | Visual, Cinematography, Lighting Directors |
| PKP-11 | Production Design Specification | Production Designer |
| PKP-12 | Audio Intent Specification | Dialogue, Music, Sound, Performance Directors |
| PKP-13 | Editing Language Specification | Editorial Director |
| PKP-14 | Animation Intent Specification | (cinema-specific; future) |
| PKP-15 | Production Blueprint Specification | Cinematography, Editorial Directors (shot, timeline) |
| PKP-16 | Distribution Specification | Platform Director |
| PKP-17 | Quality Specification | Quality Director |
| PKP-18 | Knowledge Graph Specification | (integration; the PKG nodes for the compiled artifacts) |

## 11.2 PKP Outputs and COM Object Types

Each PKP specification is a projection of COM object types (`004` Part 2) in executable state. The mapping is specified in Part 2.2. The PKP does not introduce new object types; it compiles existing types from reasoning state to executable state.

## 11.3 PKP Outputs and Runtime Independence

The 19 PKP specifications are cinema-specific (they map to cinema's directors and cinema's rendering needs). A future runtime defines its own PKP specifications, using the PKP's architecture (artifact model, dependency graph, packaging, distribution) but its own artifact types. The PKP's architecture is runtime-independent; the 19 specifications are cinema-specific.

---

# 12. Runtime Contracts

## 12.1 The PKP-PROMETHEUS Contract

| Aspect | PKP's obligation | PROMETHEUS's obligation |
|--------|-------------------|------------------------|
| **Read access** | The PKP is readable by PROMETHEUS after freeze. | PROMETHEUS reads the PKP from ATLAS by identity and version. |
| **Write access** | The PKP is **read-only** for PROMETHEUS. | PROMETHEUS writes media (not the PKP) to ATLAS. |
| **Completeness** | The PKP is complete (all artifacts frozen, all invariants satisfied) before PROMETHEUS reads it. | PROMETHEUS may assume the PKP is complete. |
| **Determinism** | The PKP is deterministic (same CIR + same providers → same PKP). | PROMETHEUS is deterministic (same PKP + same providers → same media). |
| **`cir_origin`** | Every artifact carries `cir_origin`. | PROMETHEUS records the PKP artifact each media item was rendered from. |
| **No creativity** | (The PKP carries what to render.) | PROMETHEUS makes zero creative decisions (L-15). |

## 12.2 The PKP-ORACLE Contract

| Aspect | PKP's obligation | ORACLE's obligation |
|--------|-------------------|---------------------|
| **Read access** | The PKP is readable by ORACLE. | ORACLE reads the PKP from ATLAS. |
| **Write access** | The PKP is read-only for ORACLE (L-16). | ORACLE writes validation reports (not the PKP) to ATLAS. |
| **Traceability** | Every artifact carries `cir_origin` for upstream traversal. | ORACLE traverses from media → PKP artifact → CIR node → CIS domain for drift detection. |
| **Validation** | The PKP is the specification against which media is validated. | ORACLE validates media against the PKP and reports drift. |

## 12.3 The PKP-Human Contract

The human may inspect the PKP but may not amend it directly. Amendments go through the CIR (re-compilation). The human may override ORACLE's validation report (accepting flagged media), but the override does not alter the PKP; it is recorded in the validation report's provenance.

---

# 13. Governance

## 13.1 PKP Evolution

The PKP's architecture evolves under the Constitution:

| Change type | Authority |
|--------------|-----------|
| **New PKP specification (new artifact type)** | Architectural amendment to this specification and to the COM (`004` Part 10.2). |
| **Artifact model change** | Architectural amendment to this specification. |
| **Runtime contract change** | Coordinated amendment to this specification, `010` (PROMETHEUS), and `011` (ORACLE). |

## 13.2 Compatibility

| Concern | Rule |
|---------|------|
| **Backward compatibility** | A new PKP version must be renderable by the current PROMETHEUS (or a documented newer version). Archived PKPs remain renderable by the PROMETHEUS version recorded in their provenance. |
| **Forward compatibility** | The PKP leaves extension points (new artifact types, new partitions) for future runtimes. |
| **Cross-runtime compatibility** | The PKP's architecture (artifact model, dependency graph, packaging) is runtime-independent; the 19 PKP specifications are cinema-specific. A future runtime defines its own PKP specifications using the architecture. |

## 13.3 Constitutional Compliance

| Law | Compliance |
|-----|------------|
| L-13 (Production Knowledge Is Compiled) | Part 1.1, Part 6. |
| L-14 (Execution Never Changes Intent) | Part 12.1 (PKP is read-only for PROMETHEUS). |
| L-18 (Knowledge Outlives Media) | Part 6.3 (PKP regeneration from archived CIR). |
| L-19 (History Is Immutable) | Part 8.4 (frozen PKPs are immutable). |

---

# 14. Lifecycle

## 14.1 The PKP Lifecycle

```
compiled → assembled → frozen → distributed → rendered → validated → archived
                                                              │
                                                              ▼
                                                         (revision loop)
```

| State | What it means |
|-------|---------------|
| **compiled** | Artifacts are being produced by the compiler passes. |
| **assembled** | Pass 17 has assembled the artifacts into the PKP graph. |
| **frozen** | Pass 19 has frozen the PKP; the PKP is immutable with a hash. |
| **distributed** | The PKP is in ATLAS, available to PROMETHEUS and ORACLE. |
| **rendered** | PROMETHEUS has rendered media from the PKP. |
| **validated** | ORACLE has validated the media against the PKP. |
| **archived** | The PKP (and its media and validation reports) is archived in ATLAS. |
| **(revision loop)** | ORACLE drift or human amendment triggers CIR revision → PKP incremental update → re-rendering → re-validation. |

## 14.2 Lifecycle and the CIR

The PKP's lifecycle is coupled to the CIR's lifecycle (`007` Part 9):

- CIR freeze → PKP compilation.
- CIR revision → PKP incremental update.
- CIR branch → PKP branch (a new PKP lineage from the branched CIR).

The PKP does not lead the CIR; it follows. A PKP is always the compiled projection of a frozen CIR version.

## 14.3 Lifecycle and ATLAS

The PKP is persisted by ATLAS (`012`) at every state transition:

- **compiled**: intermediate artifacts are cached in ATLAS (the compilation cache, `008` Part 9).
- **frozen**: the frozen PKP is persisted to ATLAS.
- **rendered**: the media is persisted to ATLAS with PKP references.
- **validated**: the validation reports are persisted to ATLAS with PKP and media references.
- **archived**: the complete PKP (with media and reports) is archived in ATLAS indefinitely (L-18).

---

## Architectural Rules (Restated)

This specification produced no implementation code. It architecturalizes the PKP as the compiled binary of the ACI Platform: the deterministic, executable specification that PROMETHEUS renders and ORACLE validates, governed by constitutional laws L-13, L-14, L-18, and L-19.

---

## Cross-References

| Reference | Relevance |
|-----------|-----------|
| `006` (Constitution) | L-13, L-14, L-18, L-19 govern the PKP. |
| `001` §5 | The canonical PKP definition; architecturalized here. |
| `008` (Compiler) | The compiler that produces the PKP. |
| `007` (CIR) | The CIR the PKP is compiled from; `cir_origin` on every artifact. |
| `004` (COM) | The object model the PKP is written in (executable state). |
| `010` (PROMETHEUS) | The runtime that renders the PKP. |
| `011` (ORACLE) | The validator that validates media against the PKP. |
| `012` (ATLAS) | The persistence layer for the PKP. |
| PKP-00..18 | The 19 cinema-runtime PKP specifications (`docs/genesis/specifications/pkp/`). |

---

**End of Specification.**