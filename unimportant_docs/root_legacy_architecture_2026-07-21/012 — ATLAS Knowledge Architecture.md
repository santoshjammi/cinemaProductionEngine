# 012 — ATLAS Knowledge Architecture

**Status:** Architectural Specification — Phase II
**Version:** 1.0.0
**Date:** 2026-07-21
**Derives Authority From:** `006` (Constitution, Tier 0); `001` §2.1 (ATLAS pillar definition, Tier 2); `004` (COM, the object model ATLAS stores, Tier 2); `007` (CIR, which ATLAS persists, Tier 2); `009` (PKP, which ATLAS persists, Tier 2); `010` (PROMETHEUS, whose media ATLAS persists, Tier 2); `011` (ORACLE, whose reports ATLAS persists, Tier 2); `002` Part 6 (Director Memory, which ATLAS stores, Tier 2); `005` Part 3.3.11 (Learning Faculty, which ATLAS serves, Tier 2).
**Precedence:** Below the Constitution. This specification is the full architectural realization of the ATLAS pillar introduced in `001` §2.1 and constitutionalized by `006` (L-18, L-19, L-20).
**Scope:** ATLAS's knowledge philosophy, knowledge objects, creative memory, learning, experience, semantic search, reasoning support, knowledge evolution, cross-runtime knowledge, institutional memory, knowledge governance, and lifecycle.

---

## Table of Contents

1. [Knowledge Philosophy](#1-knowledge-philosophy)
2. [Knowledge Objects](#2-knowledge-objects)
3. [Creative Memory](#3-creative-memory)
4. [Learning](#4-learning)
5. [Experience](#5-experience)
6. [Semantic Search](#6-semantic-search)
7. [Reasoning Support](#7-reasoning-support)
8. [Knowledge Evolution](#8-knowledge-evolution)
9. [Cross-Runtime Knowledge](#9-cross-runtime-knowledge)
10. [Institutional Memory](#10-institutional-memory)
11. [Knowledge Governance](#11-knowledge-governance)
12. [Lifecycle](#12-lifecycle)

---

# 1. Knowledge Philosophy

## 1.1 Knowledge Outlives Media

The ACI Platform's first philosophical commitment is **knowledge over media** (`00` §3.1): media is ephemeral; knowledge is durable. A generated image can be lost, a model can be deprecated, a rendering pipeline can be replaced — but the creative knowledge that defined why that image existed, what it depicted, and how it served the story must survive.

ATLAS is the architectural realization of this principle. ATLAS is the **Knowledge Operating System** of the platform: the layer that persists all creative knowledge (CIS, CIR, PKP), all derived artifacts (media, validation reports), and all institutional memory (constitution, ADRs, prompts, reviews) with full provenance, immutable revisions, and indefinite retention.

| What ATLAS stores | What ATLAS does not store |
|-------------------|--------------------------|
| CIS (`003`) — human intent. | (Nothing is excluded; ATLAS is the platform's sole persistence authority.) |
| CIR (`007`) — creative decisions and reasoning. | |
| PKP (`009`) — compiled executable specifications. | |
| Media (`010`) — rendered images, video, audio. | |
| Validation reports (`011`) — drift, certification, audit. | |
| Director Memory (`002` Part 6) — accepted/rejected ideas, rationale, motifs. | |
| Faculty enrichments (`005` Part 4.3) — cognitive interpretations. | |
| Compilation reports (`008` Part 10.3). | |
| Execution reports (`010` Part 2.4). | |
| Institutional memory — constitution, ADRs, prompts, reviews. | |

## 1.2 The Single Persistence Authority

ATLAS is the **only** system that writes to durable storage on behalf of the engine (`001` §2.1, invariant 4). This centralization is architectural, not convenience:

- **Provenance integrity**: if any component could write to storage, provenance chains would be broken by components that do not record provenance correctly. ATLAS enforces provenance on every write (L-5, L-9).
- **History immutability**: if any component could overwrite a frozen artifact, history would be mutable, breaking L-19. ATLAS enforces immutability on frozen artifacts.
- **Auditability**: if artifacts were scattered across component-private stores, ORACLE (`011`) could not audit the platform holistically. ATLAS centralizes artifacts for audit.

Components do not write to storage; they issue store/retrieve requests to ATLAS. ATLAS is the mediator between all components and durable storage.

## 1.3 ATLAS Makes No Creative Decisions

ATLAS is a **non-creative body** (`006` Part 4.3): it stores, retrieves, versions, and archives; it does not decide, does not cognize, does not compile, does not render, does not validate. ATLAS has **knowledge authority** (L-18) and **no creative authority**.

| ATLAS may | ATLAS may not |
|-----------|---------------|
| Store artifacts with provenance. | Make creative decisions. |
| Retrieve artifacts by identity or query. | Amend the CIS, CIR, or PKP. |
| Version artifacts per GFS-003. | Alter a frozen artifact (L-19). |
| Archive artifacts indefinitely. | Retroactively re-reason archived productions (L-20). |
| Provide precedent to the Learning Faculty. | Impose cognitive patterns without governance (L-21). |
| Index artifacts for semantic search. | Call GENESIS, PROMETHEUS, or ORACLE (`001` §2.3). |

## 1.4 Constitutional Derivation

| Law | How it governs ATLAS |
|-----|---------------------|
| L-18 (Knowledge Outlives Media) | ATLAS persists knowledge; media is a derived projection. |
| L-19 (History Is Immutable) | ATLAS enforces immutability on frozen artifacts. |
| L-20 (Learning Never Rewrites History) | ATLAS provides archived artifacts read-only to the Learning Faculty. |
| L-5 (Objects Have Identity, Provenance, Lifecycle) | ATLAS enforces identity, provenance, and lifecycle on every stored object. |
| L-9 (Every Decision Has Provenance) | ATLAS enforces provenance on every stored CIR node. |

---

# 2. Knowledge Objects

## 2.1 What ATLAS Stores

ATLAS stores **Knowledge Objects** — a unified term for all artifacts the platform produces. Every Knowledge Object is a COM object (`004` Part 2) in some state (intent, reasoning, executable, rendered, validated, archived), persisted with full provenance.

| Knowledge Object type | COM type | State | Producer | Consumer |
|-----------------------|----------|-------|----------|----------|
| CIS | Creative Intent (`004` §2.3.51) | intent | Human | Directorial Board |
| CIR node | Creative Decision (`004` §2.3.52) | reasoning | Directorial Board | Compiler; ORACLE |
| PKP artifact | Creative Artifact (`004` §2.3.53) | executable | Compiler | PROMETHEUS; ORACLE |
| Media | Creative Artifact (media subtype) | rendered | PROMETHEUS | ORACLE; human |
| Validation report | Creative Artifact (report subtype) | validated | ORACLE | Board; human; Learning Faculty |
| Director Memory entry | (typed memory record) | archived | Directors | Learning Faculty; future reasoning |
| Faculty enrichment | (typed enrichment record) | archived | Creative Mind | Learning Faculty; future reasoning |
| Compilation report | Creative Artifact (report subtype) | archived | Compiler | ORACLE |
| Execution report | Creative Artifact (report subtype) | archived | PROMETHEUS | ORACLE |
| Institutional memory | (typed document) | archived | Governance | All; future contributors |

## 2.2 The Knowledge Object Contract

Every Knowledge Object in ATLAS carries:

| Field | Definition |
|-------|-----------|
| **Identity** | The COM identity (`004` Part 2.1): `com:<production-id>:<type>:<ordinal>[@<revision>]`. |
| **Type** | The COM type (`004` Part 2.2). |
| **State** | The object's lifecycle state (`004` Part 6). |
| **Provenance** | Full provenance: producer, inputs, timestamp, confidence (L-5, L-9). |
| **Version** | The object's version (GFS-003 immutable revisions). |
| **Content** | The object's content (the COM object's fields). |
| **References** | Edges to other Knowledge Objects (the COM's relationship model, `004` Part 3). |

## 2.3 Knowledge Object Storage

ATLAS stores Knowledge Objects in a **typed graph store** — the Production Knowledge Graph (PKG, GFS-003). The PKG is the platform's canonical store; ATLAS is the OS that governs it. The PKG holds:

- All COM objects in all states.
- All relationship edges (`004` Part 3).
- All provenance chains.
- All version lineages (`amends`, `branched_from`).

The PKG is not a relational database; it is a graph store (per ADR-002, `docs/genesis/decisions/`). ATLAS governs the PKG's storage, indexing, and retrieval, but the PKG's structure is defined by the COM (`004`) and the CIR (`007`), not by ATLAS.

---

# 3. Creative Memory

## 3.1 Director Memory

Director Memory (`002` Part 6) is persisted by ATLAS. Each director's memory is a typed corpus within the PKG:

| Memory class | Contents | Owner |
|--------------|----------|-------|
| Accepted ideas | CIR nodes that reached Freeze. | Each director. |
| Rejected ideas | Alternatives that were not selected. | Each director. |
| Revision history | Immutable revisions of frozen CIR nodes. | ATLAS (storage); director (semantics). |
| Creative rationale | Trade-off analyses that justified selections. | Each director. |
| Inspirations | External references cited during Research. | Any director. |
| References | Cross-production reusable assets (character hero images, voice profiles, style presets). | ATLAS Content Library. |
| Cinematic motifs | Recurring visual/sonic/narrative motifs. | Each director. |
| Recurring themes | Thematic patterns a director favors. | Story Director, Chief Director. |
| Human overrides | Every `human_override` record. | Chief Director. |
| Style evolution | Time-series of a director's preference changes. | Each director. |
| Production history | The set of CIRs from prior productions. | ATLAS. |

## 3.2 Faculty Enrichments

Faculty enrichments (`005` Part 4.3) are persisted by ATLAS as a typed corpus. Each enrichment is a Knowledge Object with:

- The enriching faculty's identity.
- The COM object enriched.
- The enrichment type (interpretation, implication, coherence assessment, alternative, conflict flag, confidence).
- The enrichment's content and confidence.
- The production the enrichment was produced for.
- The CIS version the enrichment was based on.

Enrichments are persisted for learning (`005` Part 3.3.11) and for audit (ORACLE may traverse from a CIR node's provenance to the enrichments that informed it, `007` Part 5.1).

## 3.3 Cross-Production Character Registry

ATLAS maintains a **cross-production character registry** — a persistent registry of character identities, hero images, voice profiles, and visual identities reusable across productions (`001` MA-7, `002` Part 6.2). The registry:

- Stores character definitions with full provenance (which production created the character, when, from what CIS).
- Enables the Character Director (`002` Part 2.3.4) to query for prior character definitions during reasoning.
- Enables PROMETHEUS to reuse hero images across productions for character consistency.
- Is governed: a character may be reused only with the human's approval (L-25).

## 3.4 The Deterministic Replay Registry

ATLAS maintains a **deterministic replay registry** — a registry of `(CIR version, PKP version, provider versions, media hash)` tuples (`001` MA-8). The registry:

- Records what was produced, with which providers, and with what result.
- Enables verification of deterministic replay: re-rendering with the same tuple should produce the same media hash.
- Is the basis for the platform's reproducibility guarantee (`00` §3.6).

---

# 4. Learning

## 4.1 ATLAS's Role in Learning

ATLAS serves the Learning Faculty (`005` Part 3.3.11) by:

1. **Providing precedent during reasoning.** When the Creative Mind is reasoning about a new production, the Learning Faculty queries ATLAS for relevant prior productions, prior decisions, prior enrichments, and prior character definitions. ATLAS returns the precedent; the Learning Faculty provides it to the reasoning faculties.
2. **Persisting cognitive-pattern updates.** When the Learning Faculty proposes a cognitive-pattern update (governed, `005` Part 10.2), the update is persisted in ATLAS with full provenance. The update applies to future productions only (L-20).

## 4.2 Learning Queries

The Learning Faculty queries ATLAS via the Semantic Query Model (`004` Part 7):

| Query | Purpose |
|-------|---------|
| `semantic_search(production, theme, <value>)` | Find prior productions with a similar theme. |
| `semantic_search(character, psychology, <value>)` | Find prior characters with similar psychology. |
| `semantic_search(decision, type, <value>, status: rejected)` | Find prior rejected decisions of a type (for learning from failures). |
| `lineage(cir-node)` | Trace a decision's revision history (for learning how decisions evolved). |
| `provenance(cir-node)` | Understand a decision's basis (for learning what evidence informed it). |

## 4.3 Learning and the Constitution

ATLAS's learning support is governed by:

| Law | How it applies |
|-----|----------------|
| L-20 (Learning Never Rewrites History) | ATLAS provides archived artifacts read-only; the Learning Faculty may not modify them. |
| L-21 (Learning Is Governed) | Cognitive-pattern updates are persisted with governance approval; ungoverned updates are non-compliant. |

---

# 5. Experience

## 5.1 Cross-Production Experience

ATLAS accumulates **experience** — the corpus of all productions the platform has processed. Experience is not a single artifact; it is the totality of archived CISs, CIRs, PKPs, media, validation reports, enrichments, and memory entries across all productions.

Experience is the substrate for:

- **Learning** (`005` Part 9): the Learning Faculty learns from experience.
- **Precedent**: the Creative Mind reasons with precedent from experience.
- **Quality trends**: ORACLE tracks quality metrics across experience (`011` Part 10).
- **Taste evolution**: the platform's aesthetic defaults evolve with experience (`005` Part 9.1).

## 5.2 Experience and Privacy

Experience may contain sensitive creative content (a human's unpublished work). ATLAS governs access to experience:

- **Within a production**: all components have read access to that production's artifacts.
- **Across productions**: the Learning Faculty has read access to archived productions for precedent, governed by the human's consent (L-25).
- **External**: no external system has access to ATLAS's contents without the human's explicit authorization.

---

# 6. Semantic Search

## 6.1 The Semantic Query Model over ATLAS

ATLAS supports the Semantic Query Model (`004` Part 7) over all stored Knowledge Objects:

| Primitive | ATLAS's realization |
|-----------|---------------------|
| `lookup(id)` | Fetch a Knowledge Object by identity. |
| `traceability(id)` | Traverse upstream to the authoring source and downstream to compilations and media. |
| `dependency_traversal(id)` | Traverse `depends_on` edges. |
| `lineage(id)` | Traverse `amends` edges across versions. |
| `provenance(id)` | Fetch the full provenance chain. |
| `impact_analysis(id)` | Traverse downstream to find all dependent objects. |
| `semantic_search(type, attribute, value)` | Find objects by type, attribute, or relationship. |
| `reverse_lookup(id)` | Find objects that reference a given object. |

## 6.2 Indexing

ATLAS indexes the PKG for query performance:

- **Identity index**: by Knowledge Object identity (for `lookup`).
- **Type index**: by COM type (for `semantic_search` by type).
- **Relationship index**: by edge type and target (for `dependency_traversal`, `reverse_lookup`).
- **Provenance index**: by producer and timestamp (for `provenance` queries).
- **Version index**: by version lineage (for `lineage`).
- **Attribute index**: by COM object attributes (for `semantic_search` by attribute).

Indices are derived from the PKG's content; they are not authoritative (the PKG is authoritative). Indices may be rebuilt from the PKG at any time.

## 6.3 Query Access Control

Queries are subject to access control (Part 5.2, Part 11): a component may query only the artifacts it is authorized to read. The compiler may query the CIR; PROMETHEUS may query the PKP; ORACLE may query the CIR, PKP, and media; the Learning Faculty may query archived artifacts for precedent. Access control is enforced by ATLAS, not by the querying component.

---

# 7. Reasoning Support

## 7.1 How ATLAS Supports the Creative Mind

During reasoning (`005` Part 3, the Creative Mind's lifecycle), the Creative Mind's faculties query ATLAS for:

- **Prior productions** with similar themes, characters, or emotional journeys (for analogical reasoning).
- **Prior character definitions** (for the Character Faculty's cross-production reuse).
- **Prior director decisions** (for the Learning Faculty's precedent).
- **Prior enrichments** (for the Reflective Faculty's quality assessment).
- **Prior validation reports** (for the Reflective Faculty's learning from past drift).

ATLAS provides this support through the Semantic Query Model (Part 6). The Creative Mind issues queries; ATLAS returns results. The Creative Mind does not access ATLAS's storage directly; it goes through the query interface.

## 7.2 Reasoning Support and the Constitution

ATLAS's reasoning support is read-only (L-20): the Creative Mind reads archived knowledge; it does not modify it. The Learning Faculty's pattern updates are governed (L-21) and apply to future productions, not to the archived knowledge that informed them.

---

# 8. Knowledge Evolution

## 8.1 How Knowledge Grows

ATLAS's knowledge corpus grows monotonically: every production adds artifacts; no artifacts are deleted (L-19). Growth is governed by:

- **Versioning**: every artifact revision creates a new version; prior versions are retained.
- **Archiving**: completed productions are archived in their entirety; the archive is indefinite (L-18).
- **Indexing**: new artifacts are indexed as they are stored, maintaining query performance.

## 8.2 Retention and Deprecation

While knowledge grows monotonically, some artifacts may be **deprecated** (per `006` Part 8.2):

- A deprecated COM type (`004` Part 10.2) is marked deprecated; new productions may not author it; archived productions using it remain accessible.
- A deprecated PKP specification (`009` Part 13) is marked deprecated; new productions may not produce it; archived PKPs containing it remain renderable.

Deprecated artifacts are not deleted; they are marked. Deletion is not a supported operation (L-19).

## 8.3 Knowledge Compaction

For very large knowledge corpora, ATLAS may **compact** knowledge by:

- **Summarizing** old validation reports (retaining the summary and the drift findings, discarding the detailed per-frame data).
- **Archiving** media to cold storage (retaining the metadata and the PKP, moving the media files to slower storage).

Compaction is governed: the human may opt out of compaction for specific productions. Compaction never discards knowledge (L-18); it only moves or summarizes.

---

# 9. Cross-Runtime Knowledge

## 9.1 Runtime-Independent Knowledge

ATLAS's knowledge is **runtime-independent** because it is written in the COM (`004`), which is runtime-independent (`004` Part 1.6, `006` L-4). A Character object means the same thing in cinema, games, books, and any future runtime. This enables:

- **Cross-runtime character reuse**: a character defined in a cinema production can be reused in a game production (with the human's approval).
- **Cross-runtime learning**: the Learning Faculty can learn from a cinema production's decisions and apply the learning to a game production's reasoning.
- **Cross-runtime coherence**: the same semantic model across runtimes ensures that knowledge is portable.

## 9.2 Runtime-Specific Knowledge

Some knowledge is runtime-specific:

- **PKP artifacts** are compiled for a specific runtime (cinema's PKP-00..18; a future game runtime's own PKP specs).
- **Media** is runtime-specific (a cinema video; a game's interactive assets).
- **Validation reports** are runtime-specific (cinema's continuity checks; a game's interactivity checks).

ATLAS stores runtime-specific knowledge with a `runtime` tag, enabling queries to filter by runtime. Cross-runtime queries (e.g., "find all Characters across all runtimes with avoidant attachment") return results from all runtimes, because the COM's Character type is shared.

## 9.3 Cross-Runtime Knowledge Sharing

Cross-runtime knowledge sharing is governed:

- A runtime may query another runtime's archived knowledge for precedent (e.g., a game runtime's Character Faculty queries a cinema runtime's character definitions).
- A runtime may not render another runtime's media (a game runtime cannot render a cinema video; the PKPs are different).
- A runtime may not make decisions for another runtime (L-8: each runtime's decision body is authoritative within its runtime).

---

# 10. Institutional Memory

## 10.1 What Institutional Memory Contains

ATLAS persists the platform's **institutional memory** — the documents and records that constitute the platform's design history and governance:

| Institutional memory | Location | ATLAS's role |
|---------------------|----------|--------------|
| The Constitution (`006`) and all constitutional versions. | Repository root + ATLAS. | ATLAS persists all constitutional versions with provenance, enabling constitutional audit and amendment tracking. |
| Constitutional specifications (`00`–`005`). | Repository root + ATLAS. | ATLAS persists all specification versions. |
| Architectural specifications (`007`–`012`). | Repository root + ATLAS. | ATLAS persists all architectural specification versions. |
| Constitutional prompts (`genesis/constitutional-prompts/`). | Repository + ATLAS. | ATLAS persists the prompts as design history. |
| Architectural prompts (`genesis/architectural-prompts/`). | Repository + ATLAS. | ATLAS persists the prompts as design history. |
| Architecture reviews (`genesis/architecture-reviews/`). | Repository + ATLAS. | ATLAS persists the reviews as coherence records. |
| Architecture Decision Records (`genesis/decisions/`). | Repository + ATLAS. | ATLAS persists ADRs as records of irreversible decisions. |
| GFS-000..009 (cinema-runtime constitution). | `docs/genesis/constitutions/` + ATLAS. | ATLAS persists all GFS versions. |
| GO-001..119 (ontology). | `docs/genesis/ontology/` + ATLAS. | ATLAS persists all ontology versions. |
| PKP-00..18 (cinema-runtime PKP specs). | `docs/genesis/specifications/pkp/` + ATLAS. | ATLAS persists all PKP spec versions. |

## 10.2 Institutional Memory and the Constitution

Institutional memory is governed by the Constitution (`006` Part 8.7): the Constitution and all its versions are preserved indefinitely. The Freeze Principle (`006` Part 8.8) applies: institutional memory is frozen at the point of ratification and amended through process, not edited casually.

## 10.3 Institutional Memory and Future Contributors

Institutional memory enables future contributors to understand the platform's design without reconstructing it from months of conversations:

- **The Constitution** explains the supreme law.
- **The constitutional and architectural specifications** explain the architecture.
- **The prompts** explain why each document was created.
- **The reviews** explain the coherence checks and gap analyses.
- **The ADRs** explain the irreversible decisions and their rationale.

Together, these form the platform's complete institutional memory, from constitutional intent through architectural realization.

---

# 11. Knowledge Governance

## 11.1 Access Control

ATLAS enforces access control over knowledge:

| Component | Read access | Write access |
|-----------|-------------|--------------|
| Human | All artifacts in their productions. | CIS (intent); overrides; locks. |
| Creative Mind | Archived artifacts for precedent (read-only). | Enrichments (to ATLAS, via the Mind's interface). |
| Directorial Board | CIR (their productions); archived CIRs for precedent. | CIR nodes (to ATLAS). |
| Compiler | CIR (their productions). | PKP artifacts (to ATLAS). |
| PROMETHEUS | PKP (their productions). | Media (to ATLAS). |
| ORACLE | CIR, PKP, media (their productions); archived artifacts for audit. | Validation reports (to ATLAS). |
| Learning Faculty | Archived artifacts (read-only). | Cognitive-pattern updates (governed, to ATLAS). |
| Constitutional Review Board | All artifacts (for audit). | Audit results (to ATLAS). |

## 11.2 Retention Policy

ATLAS's retention policy is governed by the Constitution:

| Artifact class | Retention |
|----------------|-----------|
| Constitutional documents | Indefinite (L-18, `006` Part 8.7). |
| CIS, CIR, PKP | Indefinite (knowledge outlives media, L-18). |
| Media | Indefinite (but may be compacted to cold storage, Part 8.3). |
| Validation reports | Indefinite (audit history). |
| Director Memory, enrichments | Indefinite (learning substrate). |
| Institutional memory (prompts, reviews, ADRs) | Indefinite (design history). |

No artifact is deleted. Deprecated artifacts are marked, not removed (Part 8.2). Compaction summarizes or relocates but does not delete (Part 8.3).

## 11.3 Knowledge Governance and the Constitution

ATLAS's knowledge governance is governed by:

| Law | How it applies |
|-----|----------------|
| L-18 (Knowledge Outlives Media) | ATLAS retains knowledge indefinitely. |
| L-19 (History Is Immutable) | ATLAS enforces immutability on frozen artifacts. |
| L-20 (Learning Never Rewrites History) | ATLAS provides archived artifacts read-only for learning. |
| L-25 (Human Supremacy) | The human may opt out of compaction; the human controls cross-production access. |

---

# 12. Lifecycle

## 12.1 The Knowledge Object Lifecycle

A Knowledge Object in ATLAS transitions through:

```
stored → indexed → (frozen) → (archived) → (compacted) → (deprecated)
```

| State | What it means |
|-------|---------------|
| **stored** | The object has been written to ATLAS with provenance. |
| **indexed** | The object has been indexed for semantic search. |
| **frozen** | The object is immutable (per GFS-003, L-19). |
| **archived** | The object's production is complete; the object is in long-term storage. |
| **compacted** | The object has been summarized or relocated (Part 8.3); the summary/metadata is retained. |
| **deprecated** | The object's type has been deprecated (`004` Part 10.2); the object remains accessible but new objects of this type may not be authored. |

## 12.2 The Production Lifecycle in ATLAS

A production's artifacts in ATLAS follow the production's lifecycle (`009` Part 14):

```
production conceived
   │
   ▼ (human authors CIS)
CIS stored → indexed → pinned
   │
   ▼ (Board reasons; compiler compiles)
CIR stored → indexed → frozen
   │
   ▼ (compiler compiles)
PKP stored → indexed → frozen
   │
   ▼ (PROMETHEUS renders)
Media stored → indexed
   │
   ▼ (ORACLE validates)
Validation reports stored → indexed
   │
   ▼ (production complete)
All artifacts archived
   │
   ▼ (revision, if needed)
CIR revised → PKP incrementally updated → media re-rendered → re-validated → re-archived
```

## 12.3 The Platform Lifecycle

ATLAS itself has a lifecycle that spans the platform's existence:

- **Initialization**: ATLAS is initialized with the Constitution, the constitutional specifications, and the institutional memory.
- **Growth**: each production adds artifacts; the knowledge corpus grows monotonically.
- **Evolution**: ATLAS's architecture (this specification) evolves under the Constitution; ATLAS's indices may be rebuilt; ATLAS's storage may be compacted.
- **Persistence**: ATLAS persists indefinitely; the knowledge outlives every model, every runtime, and every technology (`00` §3.1, L-18).

---

## Architectural Rules (Restated)

This specification produced no implementation code, no database structures, no schemas, no APIs. It architecturalizes ATLAS as the Knowledge Operating System of the ACI Platform — the single persistence authority that governs how all artifacts are stored, versioned, retrieved, and learned from, governed by constitutional laws L-18 (knowledge outlives media), L-19 (history is immutable), and L-20 (learning never rewrites history).

ATLAS is the platform's long-term memory. It outlives every model, every runtime, and every technology. It holds the creative work of every production, the institutional memory of the platform, and the substrate for the platform's learning. It is the layer that makes the platform's knowledge durable.

---

## Cross-References

| Reference | Relevance |
|-----------|-----------|
| `006` (Constitution) | L-18, L-19, L-20, L-5, L-9 govern ATLAS. |
| `001` §2.1 | The ATLAS pillar definition; architecturalized here. |
| `004` (COM) | The object model ATLAS stores. |
| `007` (CIR) | Persisted by ATLAS; queried by ORACLE and the Learning Faculty. |
| `009` (PKP) | Persisted by ATLAS; queried by PROMETHEUS and ORACLE. |
| `010` (PROMETHEUS) | Writes media to ATLAS. |
| `011` (ORACLE) | Writes validation reports to ATLAS; reads artifacts from ATLAS. |
| `002` Part 6 | Director Memory; persisted by ATLAS. |
| `005` Part 3.3.11 | Learning Faculty; served by ATLAS. |
| `005` Part 4.3 | Faculty enrichments; persisted by ATLAS. |
| `00` §3.1 | Knowledge over media; ATLAS is the realization. |
| `00` §3.5 | Provenance mandatory; ATLAS enforces it. |
| GFS-003 | PKG as the canonical store; ATLAS governs it. |
| `genesis/constitutional-prompts/` | Institutional memory; persisted by ATLAS. |
| `genesis/architectural-prompts/` | Institutional memory; persisted by ATLAS. |
| `genesis/architecture-reviews/` | Institutional memory; persisted by ATLAS. |
| `genesis/decisions/` | Institutional memory (ADRs); persisted by ATLAS. |

---

**End of Specification.**