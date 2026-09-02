# 007 — Creative Intent Record (CIR) Architecture

**Status:** Architectural Specification — Phase II
**Version:** 1.0.0
**Date:** 2026-07-21
**Derives Authority From:** `006 — Artificial Creative Intelligence Constitution & Architectural Governance.md` (Constitution, Tier 0); `002 — Director Intelligence & Creative Reasoning Architecture Specification.md` (Tier 2, where the CIR is defined at Part 12); `005 — Cognitive Intelligence Architecture & Creative Faculties Specification.md` (Tier 2, where the cognition feeding the CIR is defined); `004 — Creative Object Model (COM) & Semantic Architecture Specification.md` (Tier 2, the object model the CIR is written in); `003 — Creative Intent Specification (CIS) Architecture.md` (Tier 2, the intent the CIR reasons from).
**Precedence:** Below the Constitution (`006`). Below the constitutional specifications that define the CIR's context (`002`, `003`, `004`, `005`). This specification is the **full architectural realization** of the CIR concept introduced in `002` Part 12 and constitutionalized by `006` (L-8, L-9, L-10, L-11). It does not redefine the CIR; it specifies how the CIR is architected.
**Scope:** The CIR's philosophy, architecture, intermediate representation, decision graph, provenance, alternatives, confidence, review, versioning, traceability, freeze rules, compiler interface, human interaction, governance, and migration.

---

## Table of Contents

1. [Philosophy](#1-philosophy)
2. [Architecture](#2-architecture)
3. [Intermediate Representation](#3-intermediate-representation)
4. [Decision Graph](#4-decision-graph)
5. [Creative Provenance](#5-creative-provenance)
6. [Alternatives](#6-alternatives)
7. [Confidence](#7-confidence)
8. [Review](#8-review)
9. [Versioning](#9-versioning)
10. [Traceability](#10-traceability)
11. [Freeze Rules](#11-freeze-rules)
12. [Compiler Interface](#12-compiler-interface)
13. [Human Interaction](#13-human-interaction)
14. [Governance](#14-governance)
15. [Migration](#15-migration)

---

# 1. Philosophy

## 1.1 The CIR Is the Intermediate Representation of Artificial Creativity

In a traditional compiler, the source program is parsed into an Abstract Syntax Tree (AST), the AST is semantically analyzed and transformed, and the resulting IR is emitted to the code-generation passes. The AST/IR is the **intermediate representation**: the structured form that sits between the human's source and the machine's executable.

The ACI Platform has the same structure, with creative analogs (`00` §3.2, `002` Part 12.1):

| Traditional compiler | ACI Platform |
|---------------------|--------------|
| Source program | Creative Intent Specification (CIS, `003`) |
| Parser | Directorial Board (`002` Part 2) consuming the CIS and the Creative Mind's (`005`) enrichments |
| AST / IR | **Creative Intent Record (CIR)** |
| Semantic analysis | Pre-freeze validation (Part 11) |
| Code generation | GENESIS Compiler (`008`) producing the PKP (`009`) |
| Executable | Production Knowledge Package (PKP) |
| Runtime | PROMETHEUS (`010`) |

The CIR is the IR of Artificial Creativity. It is the structured form of creative decisions that sits between the human's intent (CIS) and the compiler's executable (PKP). It is what the compiler consumes; it is what ORACLE (`011`) validates against; it is what ATLAS (`012`) persists as the canonical record of creative reasoning.

## 1.2 Why the CIR Is Not the CIS and Not the PKP

The three artifacts (CIS, CIR, PKP) are constitutionally separate (`003` Part 9.2, `006` L-1/L-11/L-13). The CIR's distinct role:

| Artifact | Question it answers | Author | Consumer |
|----------|---------------------|--------|----------|
| **CIS** | What does the human want? | Human | Directorial Board (via the Creative Mind) |
| **CIR** | **Why was each creative decision made, and what is the executable creative representation?** | **Directorial Board** | **Compiler** |
| **PKP** | What do I render? | Compiler | PROMETHEUS |

The CIR is the **only artifact that carries both the decision and its rationale**. The CIS carries intent without decisions. The PKP carries compiled decisions without rationale. The CIR carries decisions *and* rationale — the "what" and the "why" — in a form the compiler can traverse and ORACLE can audit.

This separation is what enables surgical revision (Part 10) and explainability (`006` L-10): a drift report names a CIR node, the node's provenance is traversed to the CIS domain and the faculty enrichment that informed it, and only that node and its downstream dependents re-enter the pipeline.

## 1.3 Constitutional Derivation

The CIR is governed by the following constitutional laws (`006` Part 3):

| Law | How it governs the CIR |
|-----|------------------------|
| L-6 (Cognition Precedes Decision) | A CIR node may not be authored before the relevant faculty enrichments exist. |
| L-8 (Decision Authority Is Defined) | Every CIR node names its home director; no node may name a faculty or the compiler as its authority. |
| L-9 (Every Decision Has Provenance) | Every CIR node carries full provenance (Part 5). |
| L-10 (Every Decision Is Explainable) | For any CIR node, the platform can traverse its provenance and answer "why?" |
| L-11 (Decision Precedes Compilation) | The compiler may not run before the CIR is frozen. |
| L-19 (History Is Immutable) | A frozen CIR node may not be mutated; revisions create new versions. |

This specification derives its authority from these laws and from `002` Part 12 (the CIR's constitutional definition). It does not amend either; it specifies the CIR's architecture within those bounds.

---

# 2. Architecture

## 2.1 The CIR as a Graph

The CIR is a **typed graph** of Creative Decision objects (`004` §2.3.52). It is not a document; it is not a file; it is a graph stored in the Production Knowledge Graph (PKG, GFS-003) as a typed subgraph (`002` Part 4.3). The CIR's graph structure:

```
CIR Root
   │
   ├── references the pinned CIS version
   ├── references the production profile
   ├── references the Creative Profile (002 Part 9)
   │
   ├── Decision Subgraph (the Creative Decision Graph, CDG)
   │      ├── Decision nodes (one per creative decision)
   │      ├── Dependency edges (depends_on)
   │      ├── Causal edges (causes)
   │      ├── Conflict edges (conflicts_with)
   │      ├── Alternative edges (rejected_in_favor_of)
   │      └── Override edges (human_override)
   │
   ├── Enrichment Reference Subgraph
   │      └── references to the Creative Mind's enrichments (005 Part 4.3)
   │         that informed each decision (by faculty, by COM object, by confidence)
   │
   ├── COM Object Subgraph
   │      └── the COM objects (004 Part 2) in reasoning state, each authorized
   │         by a Decision node
   │
   └── Review Subgraph
          ├── human review records
          ├── override records
          └── lock records
```

The CIR is a **subgraph of the PKG**, using the PKG's identity scheme, provenance rules, and immutable-revision semantics (GFS-003). It is not a separate store; it is a typed partition of the PKG.

## 2.2 CIR Partitions

The CIR is partitioned for queryability and incremental compilation:

| Partition | Contents | Query pattern |
|-----------|----------|---------------|
| **Root** | CIS version, production profile, Creative Profile, freeze metadata, CIR hash. | `lookup(cir:<production-id>:root)` |
| **Decisions** | Creative Decision nodes, each with provenance, alternatives, confidence. | `lookup(cir:<production-id>:<director-slug>:<node-type>:<ordinal>)` |
| **Enrichment References** | References to the Creative Mind's enrichments that informed each decision. | `provenance(decision) → enrichments` |
| **COM Objects (reasoning state)** | The COM objects in reasoning state, each authorized by a Decision. | `lookup(com:<production-id>:<object-type>:<ordinal>)` with state = `reasoning` |
| **Review Records** | Human review, override, and lock records. | `lookup(cir:<production-id>:review:<ordinal>)` |

## 2.3 The CIR Root

The CIR Root is the single entry point to a production's CIR. It carries:

- The production identity (`com:<production-id>:production:01`, per `004` §2.3.1).
- The pinned CIS version (`003` Part 10.2.1) the CIR reasons from.
- The production profile (`config/production_profiles.yaml`).
- The Creative Profile (`002` Part 9) selected by the Chief Director.
- The CIR version (`<major>.<minor>.<patch>`).
- The CIR hash (Part 9.3).
- The freeze metadata: frozen-at timestamp, frozen-by (Chief Director or human), freeze state.
- The enrichment-reference index: a summary of the Creative Mind's enrichments the CIR consumed.

The Root is the compiler's entry point (`008` reads the Root, then traverses the Decisions and COM Objects). It is also ORACLE's entry point for provenance traversal (`011` traverses from a PKP artifact's `cir_origin` to the Root, then to the CIS).

---

# 3. Intermediate Representation

## 3.1 The CIR as IR

As an IR, the CIR has the properties of a compiler IR:

| IR Property | CIR realization |
|-------------|-----------------|
| **Typed** | Every CIR node is a COM object (`004` Part 2) of type Creative Decision (`004` §2.3.52) or a COM object in reasoning state. Types are drawn from the COM's closed catalog (`004` Part 2.2). |
| **Traversable** | The CIR is a graph; any node can be reached from the Root; any node's dependents can be enumerated. |
| **Validatable** | The CIR is validated against the COM's invariants (`004` Part 5) and the constitutional laws (`006` Part 3) before freeze. |
| **Transformable** | The compiler transforms the CIR's reasoning-state COM objects into executable-state COM objects (the PKP). |
| **Deterministic** | Given the same pinned CIS, the same faculty enrichments, and the same Directorial Board reasoning seeds, the CIR is identical. |
| **Versioned** | The CIR is versioned per GFS-003; revisions create new versions, never mutate. |
| **Hashable** | The CIR has a content hash that uniquely identifies its frozen state (Part 9.3). |

## 3.2 What the CIR Represents

The CIR represents **the completed result of Creative Cognition and Directorial Decision-Making** (`002` Part 3, `005` Part 1.4). Concretely, for each creative decision:

- **The decision itself**: the selected alternative, expressed as an enrichment of a COM object (e.g., "Scene 7's emotional goal is grief, with intensity 0.8, achieved through a static wide composition and a silence at the midpoint").
- **The provenance**: which director decided, which CIS domain was the source, which faculty enrichments informed the decision, which alternatives were considered and rejected, what confidence the decision carries.
- **The dependencies**: which other CIR nodes this decision depends on (e.g., Scene 7's emotional decision depends on the Story's theme decision and the Character's psychology decision).
- **The authorizations**: which COM objects this decision authorizes (e.g., the Scene 7 emotional decision authorizes the Scene 7 Emotion object's `grief` value).

## 3.3 What the CIR Does Not Represent

- **The CIS**: the CIR references the CIS by version; it does not contain the CIS.
- **Faculty enrichments**: the CIR references enrichments by provenance; it does not contain the enrichments (those live in the Mind's cognitive layer, `005` Part 4.3).
- **The PKP**: the CIR is compiled into the PKP; it does not contain the PKP.
- **Media**: the CIR has no relationship to media; media is rendered from the PKP by PROMETHEUS.

---

# 4. Decision Graph

## 4.1 The Creative Decision Graph (CDG)

The CIR's core subgraph is the **Creative Decision Graph (CDG)**, defined constitutionally in `002` Part 4. This specification architecturalizes it: the CDG is the CIR's partition of Creative Decision nodes and their edges.

### 4.1.1 Nodes

Every CDG node is a Creative Decision (`004` §2.3.52) with the full lifecycle record from `002` Part 3.2:

| Field | Source |
|-------|--------|
| Identity | `cir:<production-id>:<director-slug>:<node-type>:<ordinal>` (`002` Part 12.4) |
| Home director | One of the 18 directors (`002` Part 2.3) |
| Selected alternative | The chosen creative content |
| Alternatives | The rejected alternatives (Part 6) |
| Rationale | The trade-off analysis that justified the selection |
| Evidence | CIS domains, faculty enrichments, ontology terms, ATLAS memory referenced |
| Confidence | One of `explicit / inferred / confirmed / assumed / unknown` (ADR-004) |
| Assumptions | Explicit assumptions the decision depends on |
| Freeze state | `draft / frozen / revised` |
| Provenance | Full provenance chain (Part 5) |

### 4.1.2 Edges

The CDG uses the COM's relationship catalog (`004` Part 3.2). The primary edge types within the CDG:

| Edge | Semantics | Example |
|------|-----------|---------|
| `depends_on` | The target decision must be frozen before the source. | Scene 7's camera decision `depends_on` Scene 7's emotional decision. |
| `causes` | The target decision causally motivated the source. | The Story's theme decision `causes` the Visual Language's color-language decision. |
| `conflicts_with` | The two decisions are in tension; the conflict was resolved (resolution recorded). | The Music Director's tension-music decision `conflicts_with` the Dialogue Director's silence decision; resolved by the Audio Director. |
| `rejected_in_favor_of` | An alternative decision that was not selected; links the rejected alternative to the selected one. | Alternative A (warm lighting) `rejected_in_favor_of` selected decision (cool lighting). |
| `human_override` | A human overrode the Board's decision; the override edge links the Board's decision to the human's. | The Board proposed a bleak ending; the human `human_override` to a hopeful ending. |
| `authorizes` | The decision authorizes a COM object's value. | Scene 7's emotional decision `authorizes` the Scene 7 Emotion object's `grief` value. |
| `learns_from` | The decision references a prior archived decision as precedent. | The Story Director's theme decision `learns_from` a prior production's theme decision. |

### 4.1.3 Graph Properties

The CDG inherits the graph properties from `002` Part 4.2:

- **Dependency** (`depends_on`): blocks freeze (a node cannot freeze before its dependencies).
- **Causal link** (`causes`): for explainability queries.
- **Inheritance**: child decisions inherit constraints from parents.
- **Constraints**: decisions impose constraints on their dependents.
- **Priority**: per the home director's authority level (`002` Part 8.2.1).
- **Confidence**: per ADR-004; the graph's minimum-confidence path determines freeze readiness.
- **Traceability**: any node can be traversed to the Root and to its CIS source.
- **Explainability**: the "why?" query traverses the dependency subtree.
- **Conflict detection**: the graph is scanned for unresolved `conflicts_with` edges before freeze.

## 4.2 The CIR as a Subgraph of the PKG

The CDG (and the CIR as a whole) is a typed subgraph of the PKG (`002` Part 4.3). Concretely:

- **Node identity**: CIR nodes use the PKG identity scheme; a CIR node is a PKG node of type `creative_intent` or `creative_decision`.
- **Provenance**: GFS-003 provenance rules apply; every CIR node carries full provenance.
- **Revisions**: amending a frozen CIR node creates a new immutable revision (GFS-003); the old revision is retained.
- **PKP cross-reference**: every PKP artifact carries `cir_origin` referencing the CIR node that authorized it (`002` Part 7.2).
- **ORACLE cross-reference**: ORACLE drift reports reference CIR nodes by identifier (`002` Part 11.2).

This integration requires no new graph infrastructure (`002` Part 4.3). The CIR is the creative-decision partition of the PKG.

---

# 5. Creative Provenance

## 5.1 The Provenance Chain

Every CIR node carries a **provenance chain** that traces from the decision back to its ultimate source. The chain is the architectural realization of `006` L-9 (every decision has provenance) and L-10 (every decision is explainable).

```
CIR Node (Creative Decision)
   │
   ├── home_director: <director-slug>
   ├── decided_at: <timestamp>
   ├── cis_source: <cis-domain-reference>          # The CIS domain the decision reasons from
   ├── cis_version: <cis-version>                  # The pinned CIS version
   ├── faculty_enrichments:                        # The Creative Mind's enrichments that informed the decision
   │      ├── <enrichment-id>: {faculty, com_object, confidence, evidence}
   │      └── ...
   ├── alternatives_considered: [<alternative-ids>] # Part 6
   ├── rationale: <trade-off-analysis>
   ├── assumptions: [<assumption-records>]
   ├── confidence: <adr-004-level>
   ├── atlas_precedent: [<prior-decision-ids>]     # Prior decisions the Learning Faculty provided as precedent
   └── human_review: <review-record> | null        # Part 8
```

## 5.2 Provenance Completeness

A CIR node is **provenance-complete** when all of the following are present:

1. The home director is named (L-8).
2. The CIS source domain and version are named (L-1).
3. The faculty enrichments that informed the decision are referenced (L-6).
4. At least two alternatives were considered, or a `single_option` justification is recorded (Part 6).
5. The rationale is recorded (L-10).
6. The confidence level is assigned (ADR-004).
7. Any assumptions are explicit.
8. Any human review is recorded (Part 8).

A node that is not provenance-complete cannot be frozen (Part 11). This is the architectural enforcement of L-9.

## 5.3 Provenance Traversal

The provenance chain is traversable via the Semantic Query Model (`004` Part 7.1):

- **`provenance(cir-node)`**: returns the full provenance chain.
- **`traceability(cir-node)`**: traverses upstream to the CIS domain and the human author.
- **`explain(cir-node)`**: the "why?" query — returns the rationale, the alternatives, and the enrichments that informed the decision.

These queries are the interface ORACLE uses for drift detection (`011`) and the interface the human uses for review (Part 8).

---

# 6. Alternatives

## 6.1 Alternatives as First-Class Records

Rejected alternatives are **first-class CIR records**, not discarded options. Every Creative Decision records at least two alternatives (the selected one and at least one rejected one), or declares `single_option` with a justification (`002` Part 3.1).

An alternative is a COM object of type Creative Decision (`004` §2.3.52) in the `rejected` state, linked to the selected decision via a `rejected_in_favor_of` edge. The alternative carries:

- Its content (what was proposed).
- Its rationale (why it was considered).
- Its rejection rationale (why it was not selected).
- Its trade-off analysis (how it compared to the selected alternative).
- Its confidence (if it had been selected).

## 6.2 Why Alternatives Are Preserved

Alternatives are preserved for three reasons:

1. **Revision without re-rolling.** When a decision is revised, the reviser (the director or the human) can choose from the preserved alternatives rather than re-running the entire deliberation. This is the surgical-revision enabler.
2. **Explainability.** The "why this and not that?" question is answered by the preserved alternatives and their rejection rationales.
3. **Learning.** The Learning Faculty (`005` Part 3.3.11) learns from patterns of selected-vs-rejected alternatives across productions, refining the Mind's cognitive defaults.

## 6.3 The Alternatives Subgraph

The CIR's alternatives form a subgraph within the CDG: for each selected decision, the alternatives are nodes linked by `rejected_in_favor_of` edges. The subgraph is queryable: "show me all alternatives considered for Scene 7's lighting" returns the alternative set with their rationales.

---

# 7. Confidence

## 7.1 The Five-Level Taxonomy

Every CIR node carries a confidence level from the ADR-004 taxonomy:

| Level | Definition | When used |
|-------|-----------|-----------|
| `explicit` | The decision directly follows from an explicit CIS statement. | The CIS states the ending is "ambiguous"; the ending decision is `explicit`. |
| `inferred` | The decision follows from a CIS statement by inference. | The CIS states the character's goal; the character's need is `inferred` from the goal. |
| `confirmed` | The decision was inferred and then confirmed by cross-domain coherence. | The character's need was `inferred` and then `confirmed` by alignment with the theme. |
| `assumed` | The decision relies on an assumption not stated in the CIS. | The character's attachment style is `assumed` from behavioral hints. |
| `unknown` | The decision's basis is unclear; flagged for human review. | A scene's emotional goal is `unknown` because the CIS is silent and the faculty enrichments conflict. |

## 7.2 Confidence Propagation

Confidence propagates across the CDG (`005` Part 4.6):

- **Downstream**: a decision that depends on a low-confidence decision is at most that confident. If the Character's need is `assumed`, a Scene's emotional decision grounded on that need is at most `assumed`.
- **Across domains**: a low-confidence decision in one domain flags related decisions in other domains.

The CIR records the propagated confidence for each node, computed from the node's own confidence and the minimum confidence of its dependency subtree. The propagated confidence is what the freeze validator (Part 11) checks against the freeze threshold.

## 7.3 Confidence and Human Review

Decisions below `confirmed` in high-stakes domains (story, character psychology, continuity, music philosophy, per `002` Part 8.2.5) trigger Human Review before freeze (Part 8). The CIR records the review outcome with the decision.

---

# 8. Review

## 8.1 Human Review of CIR Nodes

The human may review any CIR node before freeze. Review is the human-facing surface of the CIR, governed by `006` L-25 (human supremacy) and `002` Part 10.

The review record on a CIR node:

| Field | Definition |
|-------|-----------|
| `reviewed_by` | The human's identity. |
| `reviewed_at` | Timestamp. |
| `review_outcome` | `approved / revised / overridden / locked`. |
| `review_notes` | The human's notes (optional for `approved`; required for `revised` and `overridden`). |
| `revised_from` | If `revised`, the prior decision's identifier. |
| `override_of` | If `overridden`, the Board's decision's identifier. |
| `locked_until` | If `locked`, the lock's scope and duration. |

## 8.2 The Review Gate

Before freeze, the Quality Director (`002` Part 2.3.18) flags decisions requiring human review:

- Decisions below `confirmed` confidence in high-stakes domains.
- Decisions in productions whose review policy mandates review.
- Decisions with unresolved `conflicts_with` edges that the Board declared undecidable.

The flagged decisions enter the review gate. The human reviews each, and the review outcome is recorded on the CIR node. The CIR may not freeze with outstanding review-flagged nodes (`002` Part 11).

## 8.3 Override and Lock

The human may:

- **Override** any Board decision. The override is recorded as a `human_override` edge; the Board's original decision is retained as a rejected alternative. The override is final for that decision (`006` L-25).
- **Lock** any CIR node. A locked node may not be revised by the Board without an explicit human unlock. Locks survive revision cycles (`003` Part 10.2.1).

Overrides and locks are recorded in the CIR's Review Subgraph (Part 2.1).

---

# 9. Versioning

## 9.1 Immutable Revisions

The CIR versions per GFS-003 (`006` L-19): a frozen CIR is immutable; any change produces a new version with a new identifier and an `amends` edge to the prior version.

CIR version identifiers: `cir:<production-id>:v<major>.<minor>.<patch>`. The version is recorded on the CIR Root.

## 9.2 The CIR Hash

Every frozen CIR version has a **content hash** — a cryptographic hash over the CIR's complete graph state (all nodes, all edges, all provenance, all alternatives). The hash is recorded on the CIR Root.

The hash is the basis for:

- **Deterministic replay** (`006` L-13): the same pinned CIS + the same faculty enrichments + the same Board reasoning seeds → the same CIR → the same hash.
- **Compilation replay** (`008`): the compiler records the CIR hash it compiled from; re-compilation with the same CIR hash produces the same PKP.
- **Audit** (`011`): ORACLE verifies that the CIR hash matches the hash the compiler recorded.

## 9.3 Version Relationships

CIR versions form a lineage via `amends` edges:

```
CIR v1.0.0 (frozen)
   │
   ├── amends → (none, initial version)
   │
   ▼
CIR v1.0.1 (frozen, minor revision: Scene 7 lighting revised)
   │
   ├── amends → CIR v1.0.0
   │
   ▼
CIR v1.1.0 (frozen, minor revision: multiple scenes revised after ORACLE drift)
   │
   ├── amends → CIR v1.0.1
   │
   ▼
...
```

Branching (a divergent CIR line from a source version) is supported via `branched_from` edges, per `003` Part 10.2.2. A branch is an independent CIR lineage; it does not re-converge with its source.

---

# 10. Traceability

## 10.1 The Traceability Chain

The CIR is the **middle link** of the platform's traceability chain (`004` Part 7.1, `002` Part 7.2):

```
Human
   ↓ authors
CIS (003) — intent
   ↓ interpreted by
Creative Mind (005) — enrichments
   ↓ consumed by
Directorial Board (002) — decisions
   ↓ recorded in
CIR (this specification) — reasoning
   ↓ compiled by
Compiler (008) — compilation
   ↓ produces
PKP (009) — executable
   ↓ rendered by
PROMETHEUS (010) — media
   ↓ validated by
ORACLE (011) — validation
   ↓ persisted by
ATLAS (012) — archive
```

## 10.2 Upstream Traceability

From any CIR node, the platform can trace upstream:

- **To the faculty enrichments** that informed the decision (via `provenance.faculty_enrichments`).
- **To the CIS domain** the decision reasons from (via `provenance.cis_source` and `cis_version`).
- **To the human author** of the CIS (via the CIS's provenance, `003` Part 2.2 D-24).

## 10.3 Downstream Traceability

From any CIR node, the platform can trace downstream:

- **To the PKP artifacts** the decision authorized (via `cir_origin` on PKP artifacts, `002` Part 7.2).
- **To the media** rendered from those PKP artifacts (via ATLAS's asset provenance, `012`).
- **To the validation reports** on that media (via ORACLE's report references, `011`).

## 10.4 The `cir_origin` Contract

Every PKP artifact carries a `cir_origin` field naming the CIR node that authorized it (`002` Part 7.2, `004` I-SI-21, `006` L-11). This is the architectural link between the CIR and the PKP. The link is:

- **Bidirectional**: from CIR node, the authorized PKP artifacts are enumerable; from PKP artifact, the authorizing CIR node is directly addressable.
- **Mandatory**: a PKP artifact without `cir_origin` is non-compliant (`006` L-11) and cannot be rendered by PROMETHEUS.
- **Validated**: ORACLE verifies that every PKP artifact's `cir_origin` references a frozen CIR node.

## 10.5 Surgical Revision

The traceability chain enables **surgical revision** (`002` Part 11.2): when ORACLE reports drift on a PKP artifact, the artifact's `cir_origin` names the CIR node to re-enter. Only that node and its downstream dependents (enumerated via `depends_on` traversal) re-enter the pipeline. The rest of the CIR — and the rest of the PKP — remains frozen.

This is the architectural payoff of the CIR/PKP separation: revision is surgical, not total. A single scene's lighting can be revised without re-running the entire production.

---

# 11. Freeze Rules

## 11.1 The Freeze Authority

The CIR is frozen by the **Chief Director** (`002` Part 2.3.1), who has the sole authority to declare the CIR frozen. The human may also freeze the CIR by override (`006` L-25). No other body may freeze the CIR.

## 11.2 Pre-Freeze Validation

Before the CIR may be frozen, the pre-freeze validator (architecturalized in `011` ORACLE, but the CIR-side validation is specified here) verifies:

| Check | Law | Effect on failure |
|-------|-----|-------------------|
| Every node is provenance-complete (Part 5.2). | L-9 | Blocking. |
| Every node has a home director (no orphan nodes). | L-8 | Blocking. |
| Every node has at least two alternatives or a `single_option` justification. | — | Blocking. |
| Every node has a confidence level. | ADR-004 | Blocking. |
| All `depends_on` edges point to frozen nodes. | `004` I-SI-15 | Blocking. |
| No unresolved `conflicts_with` edges. | `002` Part 4.2 | Blocking. |
| All review-flagged nodes have been reviewed. | Part 8 | Blocking. |
| All high-stakes low-confidence nodes have been reviewed. | `002` Part 8.2.5 | Blocking. |
| The CIR Root references a pinned CIS. | L-1 | Blocking. |
| The COM invariants (`004` Part 5) hold for all reasoning-state COM objects. | L-5 | Blocking. |

A CIR with any blocking validation failure may not be frozen. The Chief Director may not override validation failures; the human may, by explicit override with rationale (recorded as a `human_override` on the CIR Root).

## 11.3 The Freeze Operation

The freeze operation:

1. The pre-freeze validator runs (Part 11.2). All checks must pass (or be overridden by the human).
2. The Chief Director declares the CIR frozen.
3. The CIR's state transitions to `frozen` on every node.
4. The CIR hash is computed and recorded on the Root.
5. The frozen CIR is persisted to ATLAS (`012`).
6. The compiler (`008`) is notified that the CIR is frozen and may begin compilation.

## 11.4 Post-Freeze Immutability

Once frozen, the CIR is immutable (`006` L-19). Any change — a revised decision, a new alternative, a human override — creates a new CIR version (Part 9.1). The prior version is retained in ATLAS with full provenance.

This immutability is the foundation of deterministic replay (`006` L-13) and audit (`011`): the platform can always return to a frozen CIR version and replay compilation from it, knowing the CIR has not changed.

---

# 12. Compiler Interface

## 12.1 The CIR-Compiler Contract

The CIR and the compiler (`008`) have a formal contract:

| Aspect | CIR's obligation | Compiler's obligation |
|--------|-------------------|----------------------|
| **Read access** | The CIR is readable by the compiler after freeze. | The compiler reads the CIR by traversing the Root, then the Decisions, then the COM Objects in reasoning state. |
| **Write access** | The CIR is **read-only** for the compiler. The compiler may not write to the CIR. | The compiler writes to the PKP, not the CIR. |
| **Completeness** | The CIR is complete (all nodes frozen, all invariants satisfied) before the compiler reads it. | The compiler may assume the CIR is complete; it does not re-validate. |
| **Determinism** | The CIR is deterministic (same inputs → same CIR → same hash). | The compiler is deterministic (same CIR → same PKP). |
| **`cir_origin`** | Every CIR node has a stable identity. | Every PKP artifact the compiler produces carries `cir_origin` referencing the authorizing CIR node. |
| **Incremental compilation** | The CIR's `depends_on` graph enables incremental compilation: only changed nodes and their dependents need recompilation. | The compiler traverses `depends_on` from changed nodes to determine what to recompile. |
| **Versioning** | The CIR records its version and hash on the Root. | The compiler records the CIR version and hash it compiled from, in the PKP. |

## 12.2 What the Compiler Reads

The compiler reads, for each compiler pass (`001` §4.2, `008`):

1. The CIR Root (for the CIS version, the production profile, the Creative Profile).
2. The Decision nodes owned by that pass's directors (e.g., the Story Compiler pass reads the Story Director's decisions).
3. The COM Objects in reasoning state that those decisions authorize.
4. The `depends_on` edges to determine compilation order.

## 12.3 What the Compiler Does Not Read

- The faculty enrichments (those are cognitive-layer; the compiler reads the decisions, not the cognition that informed them).
- The alternatives (the compiler compiles the selected decision, not the rejected ones).
- The review records (the compiler compiles the frozen decision, regardless of its review history).

This separation keeps the compiler's input clean: the compiler sees decisions, not deliberation. Deliberation is the Mind's and the Board's; the compiler executes.

---

# 13. Human Interaction

## 13.1 The Human's CIR Interface

The human interacts with the CIR through three operations (from `002` Part 10.2, architecturalized here):

| Operation | Effect | CIR record |
|-----------|--------|------------|
| **Review** | The human inspects a CIR node's provenance, alternatives, and rationale. | A review record is appended (Part 8). |
| **Amend** | The human edits a CIR node's content. | A new CIR version is created with the amended node; the prior node is retained as a rejected alternative. |
| **Override** | The human overrides a Board decision. | A `human_override` edge is added; the Board's decision is retained as a rejected alternative; the override is final. |
| **Lock** | The human locks a CIR node. | A lock record is appended; the node may not be revised without an unlock. |

## 13.2 The CIR Explorer

The human explores the CIR via the Semantic Query Model (`004` Part 7.1):

- **`lookup(node-id)`**: inspect any node.
- **`provenance(node-id)`**: trace a node's provenance.
- **`traceability(node-id)`**: trace upstream to the CIS or downstream to the PKP.
- **`impact_analysis(node-id)`**: enumerate the downstream PKP artifacts affected by a node (for revision planning).
- **`semantic_search(type, attribute)`**: find nodes by type or attribute.

These queries are the human's window into the CIR. They are also the interface ORACLE and the compiler use, ensuring all three (human, ORACLE, compiler) see the same CIR.

## 13.3 Collaborative Editing

The human and a director may co-edit a CIR node in a shared session (`002` Part 10.2). Each edit is attributed (per-edit `edited_by`, `edited_at`). Collaborative edits produce a new CIR version on save, not on each keystroke; the session is a draft, and the saved version is frozen.

---

# 14. Governance

## 14.1 CIR Evolution

The CIR's architecture (this specification) evolves under the ACI Constitution (`006`):

| Change type | Authority | Process |
|--------------|-----------|---------|
| **CIR schema extension** (new node fields, new edge types) | Constitutional amendment (`006` Part 8.1) if it affects constitutional laws; otherwise architectural amendment to this specification. | Per `006` Part 8.1 or the architectural specification amendment process. |
| **CIR partition extension** (new subgraphs) | Architectural amendment to this specification. | Per the specification amendment process. |
| **Freeze rule change** | Constitutional amendment (affects L-9, L-11, L-19). | Per `006` Part 8.1. |
| **Compiler interface change** | Architectural amendment to this specification and to `008`. | Coordinated amendment. |

## 14.2 Compatibility

| Concern | Rule |
|---------|------|
| **Backward compatibility** | A new CIR version must not invalidate archived CIRs. Archived CIRs remain valid under the CIR version they were frozen under. |
| **Forward compatibility** | The CIR leaves extension points (new node fields, new edge types) governed by the COM (`004` Part 10) and the Constitution. |
| **Cross-runtime compatibility** | The CIR is runtime-independent (it is written in the COM, which is runtime-independent, `004` Part 1.6). A future runtime's CIR uses the same architecture; only the decision bodies differ. |

## 14.3 Constitutional Compliance

This specification is constitutionally compliant (`006` Part 9):

| Law | Compliance |
|-----|------------|
| L-1 (Intent Precedes Cognition) | The CIR Root references a pinned CIS; a CIR without a pinned CIS is non-compliant. |
| L-6 (Cognition Precedes Decision) | Every CIR node's provenance references faculty enrichments; a node without enrichment references is non-compliant. |
| L-8 (Decision Authority Is Defined) | Every CIR node names its home director. |
| L-9 (Every Decision Has Provenance) | Part 5. |
| L-10 (Every Decision Is Explainable) | Part 5.3, Part 10. |
| L-11 (Decision Precedes Compilation) | Part 11, Part 12. |
| L-19 (History Is Immutable) | Part 9, Part 11.4. |

---

# 15. Migration

## 15.1 Integration Principles

| # | Principle | Statement |
|---|-----------|-----------|
| MI-1 | **The CIR is additive.** This specification architecturalizes the CIR concept defined in `002` Part 12; it does not redefine it. |
| MI-2 | **The CIR is a PKG subgraph.** No new graph infrastructure; the CIR is a typed partition of the PKG (GFS-003). |
| MI-3 | **The CIR is written in the COM.** CIR nodes are COM objects; the CIR uses the COM's identity, relationship, and invariant model. |
| MI-4 | **The CIR preserves the four-pillar boundaries.** The CIR is inside GENESIS; it is not a pillar. |
| MI-5 | **The CIR does not duplicate the CIS or the PKP.** The three artifacts are separate (Part 1.2). |

## 15.2 Migration Phases

### Phase CIR-1 — CIR Schema Documentation
- Document the CIR's partitions (Part 2), node structure (Part 3), edge vocabulary (Part 4), and provenance chain (Part 5) in `docs/genesis/specifications/` (extending the existing specification structure).
- Cross-reference each CIR element to its constitutional source (`002` Part 12, `004` Part 2, `006` Part 3).
- No runtime change.

**Exit criteria:** CIR schema documented; cross-references complete; ADR issued recording the CIR-as-IR decision.

### Phase CIR-2 — CIR Validation
- Implement the pre-freeze validator (Part 11.2).
- Implement the provenance-completeness check (Part 5.2).
- Implement the `cir_origin` contract on PKP artifacts (Part 10.4).

**Exit criteria:** Pre-freeze validation runs; blocking failures prevent freeze; `cir_origin` is present on all PKP artifacts.

### Phase CIR-3 — CIR Versioning and Hashing
- Implement CIR versioning (Part 9.1) and the CIR hash (Part 9.2).
- Implement the `amends` lineage.
- Implement branching via `branched_from`.

**Exit criteria:** CIR versions are immutable; hashes are computed; lineages are traversable; branches are independent.

### Phase CIR-4 — Compiler Interface
- Wire the compiler (`008`) to read the CIR per the contract (Part 12).
- Implement incremental compilation via `depends_on` traversal.
- Implement `cir_origin` stamping on PKP artifacts.

**Exit criteria:** The compiler reads the CIR; incremental compilation works; `cir_origin` is stamped.

### Phase CIR-5 — Human Interface
- Implement the CIR explorer (Part 13.2).
- Implement the review, amend, override, and lock operations (Part 13.1).
- Implement collaborative editing (Part 13.3).

**Exit criteria:** The human can explore, review, amend, override, and lock CIR nodes; collaborative editing produces versioned CIRs.

### Phase CIR-6 — ATLAS Persistence
- Wire the CIR to ATLAS (`012`) for persistence.
- Implement CIR archival and retrieval.

**Exit criteria:** Frozen CIRs are persisted in ATLAS; archived CIRs are retrievable; the CIR survives session restarts.

## 15.3 Backward Compatibility

| Existing artifact | Compatibility | Action |
|-------------------|---------------|--------|
| `002` Part 12 (CIR definition) | **Preserved and architecturalized.** This spec is the full realization of `002` Part 12; it does not contradict it. | None. |
| `004` Part 2 (COM) | **Preserved.** The CIR is written in the COM; the COM's types and relationships are unchanged. | None. |
| `005` Part 4 (Faculty enrichments) | **Preserved.** The CIR references enrichments by provenance; it does not contain them. | None. |
| GFS-003 (PKG) | **Preserved.** The CIR is a PKG subgraph. | None. |
| `001` §4.2 (compiler passes) | **Preserved.** The compiler reads the CIR per the contract (Part 12); the pass structure is unchanged. | Wire passes to read the CIR (Phase CIR-4). |
| `001` §5 (PKP) | **Preserved.** The PKP gains `cir_origin` on its artifacts; no other change. | Add `cir_origin` (Phase CIR-2). |

## 15.4 Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| **CIR bloat.** Large productions may produce very large CIRs. | Medium | The CIR is partitioned (Part 2.2); queries target partitions, not the whole graph. ATLAS (`012`) indexes the CIR for query performance. |
| **Provenance overhead.** Full provenance on every node may be expensive. | Medium | Provenance is structural (it is the audit trail); it is not logging. The cost is justified by the auditability and revision-surgery it enables. |
| **Freeze validation latency.** Validating a large CIR before freeze may be slow. | Low | Validation is incremental (nodes are validated as they are authored); the pre-freeze validator checks the accumulated state, not the full graph. |
| **CIR/PKP conflation.** Implementers may treat the CIR as a PKP superset. | High | Part 1.2 is explicit; the `cir_origin` is the only structural link; code review enforces the separation. |

---

## Architectural Rules (Restated)

This specification produced **no implementation code, no Python, no TypeScript, no YAML, no JSON schemas, no prompts, no APIs**. It produced an architectural specification of the Creative Intent Record, deriving authority from the ACI Constitution (`006`) and the constitutional specifications (`002`, `003`, `004`, `005`).

The CIR is the IR of Artificial Creativity: the structured, typed, provenanced, versioned, hashable graph of creative decisions that sits between cognition and compilation. It is the artifact that makes creative decisions executable, explainable, auditable, and surgically revisable.

---

## Cross-References

| Reference | Relevance |
|-----------|-----------|
| `006` (Constitution) | Supreme authority. L-6, L-8, L-9, L-10, L-11, L-19 govern the CIR. |
| `002` Part 12 | The CIR's constitutional definition. This spec architecturalizes it. |
| `002` Part 3 | The Creative Decision Lifecycle; every CIR node follows this lifecycle. |
| `002` Part 4 | The Creative Decision Graph; the CIR's core subgraph. |
| `002` Part 7 | The Director↔Compiler boundary; the CIR is the boundary artifact. |
| `002` Part 8 | Conflict resolution; `conflicts_with` edges in the CIR. |
| `002` Part 10 | Human collaboration; review, amend, override, lock on CIR nodes. |
| `003` (CIS) | The CIR's upstream traceability target. |
| `004` Part 2 | The COM object types the CIR is written in. |
| `004` Part 3 | The COM relationship types the CIR's edges use. |
| `004` Part 5 | The COM invariants the CIR's reasoning-state objects must satisfy. |
| `004` Part 7 | The Semantic Query Model the CIR exposes. |
| `005` Part 4 | The faculty enrichments the CIR's provenance references. |
| `001` §4.2 | The compiler passes that read the CIR. |
| `001` §5 | The PKP that the CIR is compiled into. |
| `008` (Compiler) | The compiler that reads the CIR (Part 12). |
| `009` (PKP) | The compiled output; carries `cir_origin`. |
| `011` (ORACLE) | The validator that checks the CIR and traverses its provenance. |
| `012` (ATLAS) | The persistence layer for the CIR. |
| GFS-003 | The PKG as the CIR's store. |
| ADR-004 | The five-level confidence taxonomy used by every CIR node. |

---

**End of Specification.**