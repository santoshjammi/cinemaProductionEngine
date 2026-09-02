# 013 — Repository & Metadata Architecture

**Status:** Platform Engineering Specification — Phase III
**Version:** 1.0.0
**Date:** 2026-07-21
**Derives Authority From:** `006` (Constitution, Tier 0); the constitutional specifications `00`–`005` (Tier 2); the runtime architectural specifications `007`–`012` (Tier 2); GFS-007 (Governance Constitution, Tier 1 for cinema); GFS-009 (Constitutional Ontology Framework, Tier 1 for cinema).
**Precedence:** Below the Constitution. Below the constitutional and runtime architectural specifications. This specification governs the **repository as an engineering artifact**: its structure, metadata, versioning, and evolution. It does not govern creative content; it governs the container of creative content.
**Scope:** Repository philosophy, directory taxonomy, document hierarchy, naming conventions, metadata model, versioning model, folder ownership, artifact lifecycle, repository evolution, repository governance, integration, migration, and future evolution.

---

## Table of Contents

1. [Philosophy](#1-philosophy)
2. [Objectives](#2-objectives)
3. [Principles](#3-principles)
4. [Architecture](#4-architecture)
5. [Components](#5-components)
6. [Responsibilities](#6-responsibilities)
7. [Governance](#7-governance)
8. [Lifecycle](#8-lifecycle)
9. [Integration](#9-integration)
10. [Migration](#10-migration)
11. [Future Evolution](#11-future-evolution)

---

# 1. Philosophy

## 1.1 The Repository Is the Constitution's Physical Form

The ACI Platform's Constitution (`006`) and its derived specifications (000–012) are abstract authority. The repository is where that authority becomes physical: documents in directories, with names, metadata, versions, and relationships. A contributor who cannot find a document cannot obey it; a machine that cannot parse a document cannot enforce it. The repository is therefore not a convenience — it is the **constitutional architecture's physical manifestation**, and its structure is an architectural concern.

This specification governs the repository the way `006` governs the platform: not by naming specific files, but by establishing the invariants that every file's location, name, metadata, and version must satisfy.

## 1.2 Why the Repository Must Be Architectural

A repository that grows without architectural governance accumulates **repository drift**: documents in wrong directories, inconsistent naming, missing metadata, broken cross-references, and duplicated concepts. Repository drift is the physical form of architecture drift (`006` Part 8.8), and it is prevented the same way: by a governed structure that changes only through process, not by casual editing.

The repository's structure must mirror the constitutional tier hierarchy (`006` Part 1.5) so that any artifact's location reveals its constitutional authority. A constitution document (Tier 0) lives in one place; a runtime constitution (Tier 1) in another; a specification (Tier 2) in another. The location is the artifact's constitutional signature.

## 1.3 Constitutional Derivation

| Law | How it governs the repository |
|-----|------------------------------|
| L-22 (Constitutional Amendments Require Process) | The repository structure is governed; structural changes require governance approval. |
| L-19 (History Is Immutable) | Repository history (git) is immutable; amendments create new versions, never overwrite. |
| L-4 (Shared Semantic Model) | The repository's document taxonomy mirrors the COM's object taxonomy; the shared language extends to the file system. |

---

# 2. Objectives

The repository architecture objectives:

| # | Objective | How this specification achieves it |
|---|-----------|-----------------------------------|
| O-1 | **Self-documenting** | Every document carries metadata (016) that declares its authority, dependencies, and status. |
| O-2 | **Self-validating** | The repository's structure is verifiable by the Governance Engine (014) against the constitutional rules (017). |
| O-3 | **Machine-readable** | Every document's metadata is machine-parseable, enabling the Architecture Registry (015) to build the authority graph automatically. |
| O-4 | **AI-native** | The repository's structure and metadata enable AI agents to discover, navigate, and operate on the architecture without human guidance. |
| O-5 | **Repository-governed** | The repository's structure is governed by the Constitution; structural changes require governance. |
| O-6 | **Version-controlled** | Every document is versioned per GFS-003; the repository's git history is the platform's engineering history. |
| O-7 | **Constitution-aware** | Every document's location and metadata declare its constitutional tier and deriving authority. |
| O-8 | **Multi-runtime** | The repository accommodates multiple runtimes (cinema today; games, books, etc. tomorrow) without structural changes. |
| O-9 | **Enterprise-ready** | The repository's structure is legible to engineering teams, auditors, and AI agents without onboarding. |

---

# 3. Principles

| # | Principle | Statement |
|---|-----------|-----------|
| RP-1 | **Tier-reflected structure** | The repository's directory taxonomy mirrors the constitutional tier hierarchy (`006` Part 1.5). |
| RP-2 | **One artifact, one home** | Every artifact has exactly one canonical location; no artifact is duplicated across directories. |
| RP-3 | **Metadata is mandatory** | Every document carries the metadata defined in 016; a document without metadata is non-compliant. |
| RP-4 | **Naming is governed** | Document names follow a governed convention (Part 4.4); names are stable and immutable once published. |
| RP-5 | **History is immutable** | The repository's git history is immutable (L-19); amendments create new commits, never rewrite. |
| RP-6 | **Structure is governed** | Structural changes (new directories, renamed directories, taxonomy changes) require governance approval per `006` Part 8.1. |
| RP-7 | **The repository is runtime-independent** | The repository's top-level structure is not cinema-specific; runtime-specific content is scoped to runtime subdirectories. |

---

# 4. Architecture

## 4.1 The Canonical Directory Taxonomy

The repository's top-level directory taxonomy mirrors the constitutional tiers and the platform's institutional memory:

```
/  (repository root)
│
├── 00 — Cinema Production Engine Vision, Philosophy & Reference Architecture.md   (Tier 2: cinema vision)
├── 001 — ...                                                                       (Tier 2: cinema migration)
├── 002 — ...                                                                       (Tier 2: Director Intelligence)
├── 003 — ...                                                                       (Tier 2: CIS)
├── 004 — ...                                                                       (Tier 2: COM)
├── 005 — ...                                                                       (Tier 2: Creative Mind)
├── 006 — Artificial Creative Intelligence Constitution & Architectural Governance.md  (Tier 0: Constitution)
├── 007 — ...                                                                       (Tier 2: CIR Architecture)
├── 008 — ...                                                                       (Tier 2: Compiler Architecture)
├── 009 — ...                                                                       (Tier 2: PKP Architecture)
├── 010 — ...                                                                       (Tier 2: PROMETHEUS Architecture)
├── 011 — ...                                                                       (Tier 2: ORACLE Architecture)
├── 012 — ...                                                                       (Tier 2: ATLAS Architecture)
├── 013 — ... through 018 — ...                                                     (Tier 2: Platform Engineering)
│
├── genesis/                        (Institutional Memory — the platform's design history)
│   ├── README.md                   (Index)
│   ├── constitutional-prompts/     (Why each constitutional document was created — Phase I)
│   ├── architectural-prompts/      (How each architectural capability should be designed — Phases II & III)
│   ├── architecture-reviews/       (Coherence checks and gap analyses)
│   └── decisions/                  (Architecture Decision Records — irreversible decisions)
│
├── docs/                           (Existing Genesis documentation — Tier 1 & Tier 3)
│   └── genesis/
│       ├── constitutions/          (Tier 1: GFS-000..009, the cinema-runtime constitution)
│       ├── ontology/               (Tier 3: GO-001..119, the ontology standards)
│       ├── specifications/         (Tier 3: PKP-00..18 and other derived specifications)
│       ├── schemas/                (Tier 3: schema projections)
│       ├── patterns/               (Tier 3: architecture and design patterns)
│       ├── templates/              (Tier 4: authoring templates)
│       ├── workflows/              (Tier 3: workflow definitions)
│       ├── agents/                 (Tier 3: agent specifications)
│       ├── decisions/              (Tier 3: ADRs — the existing cinema-runtime ADRs)
│       ├── validation/             (Tier 3: validation patterns and quality gates)
│       └── ...                     (other existing documentation)
│
├── config/                         (Tier 4: implementation configuration — existing)
├── frontend/                       (Tier 4: implementation — existing)
├── backend/                        (Tier 4: implementation — existing)
├── movie_os/                       (Tier 4: implementation — existing)
├── pipeline/                       (Tier 4: implementation — existing)
├── tests/                          (Tier 4: implementation — existing)
└── ...                             (other existing implementation directories)
```

## 4.2 Document Hierarchy

Documents in the repository are hierarchically ordered by constitutional authority:

| Hierarchy level | Location | Documents | Authority |
|----------------|----------|-----------|-----------|
| **Root specifications** | `/` | 000–018 (the constitutional and architectural specifications) | Tier 0 (006) and Tier 2 (000–005, 007–018). These are the platform's supreme architectural documents. |
| **Institutional memory** | `/genesis/` | Prompts, reviews, ADRs | Design history; governed by `006` Part 8.7. |
| **Runtime constitution** | `/docs/genesis/constitutions/` | GFS-000..009 | Tier 1 (cinema-runtime constitution). |
| **Standards** | `/docs/genesis/ontology/`, `/docs/genesis/specifications/`, `/docs/genesis/schemas/`, `/docs/genesis/patterns/` | GO, PKP specs, schema projections, patterns | Tier 3 (derived standards). |
| **Guides** | `/docs/genesis/templates/`, `/docs/genesis/workflows/` | Templates, workflows | Tier 4 (advisory guides). |
| **Implementation** | `/config/`, `/frontend/`, `/backend/`, `/movie_os/`, `/pipeline/`, `/tests/` | Code, configuration, tests | Tier 4 (implementation; not law). |

## 4.3 Folder Ownership

Every directory has a defined owner — the body responsible for the directory's content and structure.

| Directory | Owner | Governance |
|-----------|-------|------------|
| `/` (root specifications) | The Constitutional Review Board (`006` Part 7.5). | Root specifications are frozen; changes require constitutional amendment (`006` Part 8.1). |
| `/genesis/` (institutional memory) | The Constitutional Review Board. | Frozen at the point of corresponding specification ratification. |
| `/docs/genesis/constitutions/` | The cinema-runtime governance (GFS-007). | Changes require cinema-runtime constitutional amendment. |
| `/docs/genesis/ontology/` | The ontology governance (GFS-009). | Changes require ontology governance. |
| `/docs/genesis/specifications/` | The specification's deriving authority. | Changes require the specification's amendment process. |
| `/docs/genesis/schemas/` | The schema's deriving specification. | Changes require the deriving specification's amendment. |
| `/docs/genesis/patterns/`, `/templates/`, `/workflows/`, `/agents/`, `/decisions/`, `/validation/` | The respective deriving authorities. | Changes require the deriving authority's process. |
| `/config/`, `/frontend/`, `/backend/`, `/movie_os/`, `/pipeline/`, `/tests/` | The engineering teams. | Implementation directories are freely editable within the constitution's invariants. |

## 4.4 Naming Conventions

The repository's naming convention is governed and stable:

| Artifact type | Convention | Example |
|---------------|-----------|---------|
| Root specification | `NNN — Title.md` (zero-padded number, em-dash, title) | `006 — Artificial Creative Intelligence Constitution & Architectural Governance.md` |
| Constitutional prompt | `prompt-NNN-<short-name>.md` | `prompt-006-constitution.md` |
| Architectural prompt | `prompt-NNN-<short-name>.md` | `prompt-013-repository.md` |
| Architecture review | `review-NNN-<short-name>.md` | `review-013-repository.md` |
| ADR | `adr-NNN-<short-name>.md` or `adr-NNN-through-NNN-<short-name>.md` | `adr-001-through-006.md` |
| GFS (cinema constitution) | `NNN — Title.md` or `NN-Title.md` (existing; normalized per `001` TD-006) | `00-ConstitutionCharter.md` |
| GO (ontology) | `NNN — Title.md` | `001 — Genesis Core Ontology.md` |
| PKP spec | `NN — Title.md` | `00 — Vision Specification.md` |
| Schema | `NNN — Title.md` | (per existing convention) |
| Pattern | `NNN — Title.md` | (per existing convention) |
| Template | `NNN — Title.md` | (per existing convention) |

Names are immutable once published; renaming requires governance approval and a redirect (the prior name is retained as a pointer or a git rename is recorded).

## 4.5 The Metadata Model

Every document in the repository carries a **metadata header** — a machine-readable block at the top of the document declaring the document's constitutional identity. The metadata model is defined fully in 016; this specification establishes that metadata is **mandatory** (RP-3) and that the repository's structure is verifiable against it.

A document without metadata is non-compliant: it cannot be registered in the Architecture Registry (015), cannot be validated by the Governance Engine (014), and cannot be located by AI agents.

## 4.6 The Versioning Model

The repository's versioning model has two layers:

1. **Document versioning** (per GFS-003): each document has a version (`<major>.<minor>.<patch>`) recorded in its metadata. A frozen document is immutable; amendments create new versions.
2. **Repository versioning** (via git): the repository's git history is the platform's engineering history. Each commit is immutable (L-19); amendments create new commits, never rewrite (no force-push, no history rewriting).

The two layers are complementary: document versions are semantic (what changed in the document's meaning); git commits are operational (what changed in the repository's state). Both are immutable.

---

# 5. Components

The repository architecture has the following components:

| Component | What it is | Specification |
|-----------|-----------|---------------|
| **Root specifications** | The constitutional and architectural documents at the repository root. | 000–018. |
| **Institutional memory** | The prompts, reviews, and ADRs in `/genesis/`. | This specification; `genesis/README.md`. |
| **Runtime constitution** | The cinema-runtime GFS-000..009. | `/docs/genesis/constitutions/`. |
| **Standards** | The ontology, PKP specs, schemas, patterns. | `/docs/genesis/`. |
| **Guides** | Templates, workflows. | `/docs/genesis/templates/`, `/docs/genesis/workflows/`. |
| **Implementation** | Code, configuration, tests. | `/config/`, `/frontend/`, `/backend/`, etc. |
| **Metadata** | The metadata header on every document. | 016. |
| **Registry** | The machine-readable registry of all artifacts. | 015. |
| **Governance Engine** | The engine that validates the repository against the Constitution. | 014. |

---

# 6. Responsibilities

| Body | Repository responsibility |
|------|--------------------------|
| **Constitutional Review Board** | Owns the root specifications and the institutional memory; approves structural changes. |
| **Cinema-runtime governance (GFS-007)** | Owns the cinema-runtime constitution and derived standards. |
| **Engineering teams** | Own the implementation directories; free to edit within constitutional invariants. |
| **AI agents** | Read the repository via the Architecture Registry (015); write only through governed processes. |
| **Governance Engine (014)** | Validates the repository's structure and metadata against the constitutional rules (017). |
| **Architecture Registry (015)** | Indexes the repository's artifacts and builds the authority graph. |

---

# 7. Governance

## 7.1 Structural Governance

The repository's structure is governed by the Constitution:

| Change type | Authority | Process |
|--------------|-----------|---------|
| **New root specification** | Constitutional amendment (if it affects the Constitution) or architectural amendment (if it is a derived specification). | Per `006` Part 8.1. |
| **New directory in `/genesis/`** | Constitutional Review Board approval. | Per the institutional memory governance (`genesis/README.md`). |
| **New directory in `/docs/genesis/`** | The deriving authority's approval. | Per the relevant specification's amendment process. |
| **New implementation directory** | Engineering team discretion, within constitutional invariants. | No governance approval required; the directory must not duplicate an existing constitutional concept. |
| **Renaming a directory or document** | Governance approval; the rename is recorded in git. | Per the relevant authority. |
| **Taxonomy change** (new top-level directory, reorganization) | Constitutional amendment (affects the repository's constitutional structure). | Per `006` Part 8.1. |

## 7.2 Repository Drift Detection

The Governance Engine (014) detects repository drift:

- **Misplaced artifacts**: a document in a directory that does not match its constitutional tier.
- **Missing metadata**: a document without the metadata defined in 016.
- **Broken cross-references**: a document that references a non-existent or moved document.
- **Duplicated concepts**: two documents that define the same concept in different locations.
- **Naming violations**: a document whose name does not follow the convention (Part 4.4).

Drift is reported as a governance finding (014); remediation follows `006` Part 9.5.

## 7.3 Constitutional Compliance

The repository is constitutionally compliant when:

| Criterion | How verified |
|-----------|-------------|
| Every root specification is in the root directory. | Registry (015) check. |
| Every institutional memory artifact is in `/genesis/`. | Registry check. |
| Every runtime constitution document is in `/docs/genesis/constitutions/`. | Registry check. |
| Every standard is in its standards directory. | Registry check. |
| Every document carries the metadata defined in 016. | Governance Engine (014) check. |
| Every document's metadata declares its constitutional tier and deriving authority. | Governance Engine check. |
| No document duplicates a concept defined elsewhere. | Governance Engine semantic check (017). |

---

# 8. Lifecycle

## 8.1 The Document Lifecycle in the Repository

```
proposed → drafted → reviewed → ratified → published → (amended) → (deprecated) → (obsolete) → archived
```

| State | What it means | Repository effect |
|-------|---------------|-------------------|
| **proposed** | A document is proposed but not yet drafted. | No file; a proposal record in `/genesis/decisions/` or a governance ticket. |
| **drafted** | The document is written but not reviewed. | A file in the appropriate directory, marked `draft` in metadata. |
| **reviewed** | The document has passed constitutional review. | The file's metadata is updated with the review reference. |
| **ratified** | The document is ratified by the human (`006` L-25). | The file's metadata is updated with the ratification record. |
| **published** | The document is the canonical version. | The file is in its canonical location; its version is recorded. |
| **amended** | A new version is created. | A new file version (per GFS-003); the prior version is retained. |
| **deprecated** | The document is marked deprecated. | The file's metadata is updated with `deprecated` status. |
| **obsolete** | The document is marked obsolete. | The file's metadata is updated with `obsolete` status. |
| **archived** | The document is no longer active but retained. | The file remains in its location; the metadata marks it `archived`. |

## 8.2 The Repository Lifecycle

The repository itself has a lifecycle:

- **Initialization**: the repository is created with the constitutional and architectural specifications at the root, the institutional memory in `/genesis/`, and the existing documentation in `/docs/genesis/`.
- **Growth**: new specifications, standards, and implementation artifacts are added per governance.
- **Evolution**: the repository's structure evolves under governance (Part 7.1); structural changes are recorded in git.
- **Persistence**: the repository's git history is the platform's engineering history; it is immutable (L-19) and persisted indefinitely.

---

# 9. Integration

## 9.1 Integration with the Constitutional Foundation

The repository is the physical container of the constitutional foundation:

| Constitutional artifact | Repository location |
|-------------------------|---------------------|
| The Constitution (006) | `/006 — ...md` (root). |
| Constitutional specifications (000–005) | `/000 — ...md` through `/005 — ...md` (root). |
| Runtime architectural specifications (007–012) | `/007 — ...md` through `/012 — ...md` (root). |
| Platform engineering specifications (013–018) | `/013 — ...md` through `/018 — ...md` (root). |
| Cinema-runtime constitution (GFS-000..009) | `/docs/genesis/constitutions/`. |
| Ontology (GO-001..119) | `/docs/genesis/ontology/`. |
| PKP specifications (PKP-00..18) | `/docs/genesis/specifications/pkp/`. |
| Institutional memory (prompts, reviews, ADRs) | `/genesis/`. |

## 9.2 Integration with the Runtime Architecture

The runtime architecture (007–012) specifies the platform's runtime; the repository holds the runtime's specifications and (eventually) its implementation. The implementation directories (`/config/`, `/frontend/`, `/backend/`, `/movie_os/`, `/pipeline/`, `/tests/`) are the existing implementation, which will evolve toward the runtime architecture under the migration plans in 007–012.

## 9.3 Integration with the Platform Engineering Layer

This specification integrates with the rest of the Platform Engineering layer:

| Spec | Integration |
|------|-------------|
| 014 (Governance Engine) | Validates the repository's structure and metadata against the constitutional rules. |
| 015 (Architecture Registry) | Indexes the repository's artifacts and builds the authority graph. |
| 016 (Metadata) | Defines the metadata that every document in the repository must carry. |
| 017 (Validation Rules) | Defines the executable rules the Governance Engine enforces on the repository. |
| 018 (Developer Platform) | Provides the tooling that engineers and AI agents use to interact with the repository. |

---

# 10. Migration

## 10.1 Integration Principles

| # | Principle | Statement |
|---|-----------|-----------|
| MI-1 | **The repository is additive.** This specification governs the existing repository structure; it does not require a reorganization. |
| MI-2 | **Existing documents are preserved.** The existing `docs/genesis/` structure is retained; this specification formalizes it. |
| MI-3 | **Metadata is added, not replacing.** Existing documents gain metadata headers (016); their content is unchanged. |
| MI-4 | **The root specifications are already in place.** 000–012 are at the root; 013–018 join them. |
| MI-5 | **The institutional memory is already in place.** `/genesis/` exists with its prompts, reviews, and ADRs. |

## 10.2 Migration Phases

### Phase REP-1 — Metadata Backfill
- Add the metadata header (016) to every existing root specification (000–012).
- Add the metadata header to every GFS, GO, and PKP document.
- No content changes; metadata is additive.

### Phase REP-2 — Registry Population
- Build the Architecture Registry (015) by scanning the repository's documents and their metadata.
- Verify that every document is in its canonical location per Part 4.2.

### Phase REP-3 — Governance Engine Deployment
- Deploy the Governance Engine (014) to validate the repository against the constitutional rules (017).
- Run the first repository drift detection (Part 7.2); remediate findings.

### Phase REP-4 — Naming Normalization
- Normalize the GFS filenames per `001` TD-006 (mixed naming: `00-`, `01-`, `002 —`, `004 `, `003 –` → `NNN-Name.md`).
- Record renames in git.

## 10.3 Backward Compatibility

| Existing artifact | Compatibility | Action |
|-------------------|---------------|--------|
| Root specifications (000–012) | **Preserved.** Already at the root. | Add metadata (Phase REP-1). |
| `/genesis/` institutional memory | **Preserved.** Already in place. | Add metadata to prompts, reviews, ADRs. |
| `/docs/genesis/` documentation | **Preserved.** Already in place. | Add metadata; normalize GFS names (Phase REP-4). |
| Implementation directories | **Preserved.** | None. |
| `00` §20 cross-references | **Preserved.** The cross-references in `00` §20 remain valid; this specification adds the platform engineering layer. | None. |

## 10.4 Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Metadata backfill burden.** Adding metadata to every existing document is labor-intensive. | Medium | Metadata is minimal (016 defines the canonical fields); AI agents can assist with backfill under human review. |
| **Naming normalization breakage.** Renaming GFS files may break existing cross-references. | Medium | Renames are recorded in git; cross-references are updated; the Architecture Registry (015) detects broken references. |
| **Repository drift accumulation.** Without the Governance Engine (014), drift may accumulate before Phase REP-3. | Low | The Governance Engine is deployed in Phase REP-3; drift is detected and remediated then. |

---

# 11. Future Evolution

## 11.1 New Runtimes

A new creative runtime (games, books, etc.) adds:

- A new runtime constitution (Tier 1) in `/docs/<runtime>/constitutions/` (or a subdirectory of `/docs/genesis/` if the runtime extends cinema).
- New runtime-specific specifications (Tier 2) at the root (numbered 019+) or in a runtime-specific subdirectory.
- New runtime-specific standards (Tier 3) in `/docs/<runtime>/`.

The repository's top-level structure does not change; runtime-specific content is scoped to runtime subdirectories.

## 11.2 New Specification Tiers

If the platform introduces a new specification tier (e.g., a "reference implementation" tier), the repository accommodates it by adding a new top-level directory or a new subdirectory under `/docs/`, per governance (Part 7.1).

## 11.3 AI-Native Repository Operations

As the platform matures, AI agents may perform repository operations (creating documents, updating metadata, running validations) under human oversight. The repository's machine-readable metadata (016) and the Architecture Registry (015) enable AI agents to operate on the repository without human guidance for routine operations, with human approval for governance actions.

## 11.4 Cross-Repository Knowledge

In the long term, the repository may share knowledge with other ACI Platform repositories (e.g., a game runtime repository, a book runtime repository) through ATLAS (`012` Part 9). The repository's structure is compatible with cross-repository knowledge sharing because its metadata (016) and registry (015) are runtime-independent.

---

## Architectural Rules (Restated)

This specification produced no implementation code, no APIs, no JSON/YAML, no schemas, no vendor tooling. It governs the repository as an architectural artifact: its directory taxonomy mirrors the constitutional tiers; its metadata model makes every document machine-readable; its versioning model preserves history immutably; its governance prevents repository drift.

---

## Cross-References

| Reference | Relevance |
|-----------|-----------|
| `006` (Constitution) | L-22 (amendments require process), L-19 (history is immutable), L-4 (shared semantic model). The repository is the Constitution's physical form. |
| `00`–`012` | The constitutional and runtime architectural specifications; all at the repository root. |
| `001` TD-006 | The naming normalization for GFS files. |
| `genesis/README.md` | The institutional memory index. |
| `genesis/constitutional-prompts/` | The constitutional prompts (Phase I design history). |
| `genesis/architectural-prompts/` | The architectural prompts (Phases II & III design history). |
| `genesis/architecture-reviews/` | The architecture reviews (coherence reports). |
| `genesis/decisions/` | The ADRs (irreversible decisions). |
| `docs/genesis/constitutions/` | GFS-000..009 (cinema-runtime constitution). |
| `docs/genesis/ontology/` | GO-001..119 (ontology standards). |
| `docs/genesis/specifications/pkp/` | PKP-00..18 (cinema-runtime PKP specs). |
| 014 (Governance Engine) | Validates the repository against the Constitution. |
| 015 (Architecture Registry) | Indexes the repository's artifacts. |
| 016 (Metadata) | Defines the metadata every document must carry. |
| 017 (Validation Rules) | Defines the executable rules for repository validation. |
| 018 (Developer Platform) | Provides the tooling for repository interaction. |

---

**End of Specification.**