# 015 — Architecture Registry

**Status:** Platform Engineering Specification — Phase III
**Version:** 1.0.0
**Date:** 2026-07-21
**Derives Authority From:** `006` (Constitution); `013` (Repository Architecture); `014` (Governance Engine); `016` (Metadata).
**Precedence:** Below the Constitution. This specification defines the **Architecture Registry** — the machine-readable index of every architectural artifact in the repository.
**Scope:** Registry philosophy, artifact catalogue, identifier model, dependencies, authority graph, ownership graph, specification catalogue, version registry, review registry, status registry, discovery model, lifecycle, evolution.

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

## 1.1 The Registry Is the Platform's Machine-Readable Map of Itself

The ACI Platform's repository (`013`) contains documents — specifications, constitutions, ontologies, schemas, prompts, reviews, ADRs. These documents are written for humans and AI agents to read. But reading every document to understand the architecture is impractical for a machine. The Architecture Registry is the **machine-readable map** of the repository: a typed graph of every architectural artifact, with its identity, authority, dependencies, status, and version, queryable by the Governance Engine (014) and the Developer Platform (018).

The Registry is to the repository what the PKG (`007` Part 4.3) is to a production: a typed graph of artifacts with identity and relationships. The Registry uses the COM's (`004`) identity and relationship model, extended to architectural artifacts.

## 1.2 Constitutional Derivation

| Law | How it governs the Registry |
|-----|----------------------------|
| L-4 (Shared Semantic Model) | The Registry uses the COM's identity and relationship model; it is the architectural analog of the COM. |
| L-5 (Objects Have Identity, Provenance, Lifecycle) | Every Registry entry has identity, provenance, and lifecycle. |

---

# 2. Objectives

| # | Objective | How this specification achieves it |
|---|-----------|-----------------------------------|
| O-1 | **Machine-readable** | The Registry is a typed graph, queryable by machines. |
| O-2 | **Complete** | The Registry indexes every architectural artifact in the repository. |
| O-3 | **Current** | The Registry is updated when artifacts are added, amended, or deprecated. |
| O-4 | **Queryable** | The Registry supports the Semantic Query Model (`004` Part 7) over architectural artifacts. |
| O-5 | **Authority graph** | The Registry builds the authority graph: which artifact derives authority from which. |
| O-6 | **Dependency graph** | The Registry builds the dependency graph: which artifact depends on which. |

---

# 3. Principles

| # | Principle | Statement |
|---|-----------|-----------|
| RG-1 | **The Registry is derived, not authored.** The Registry is built by scanning the repository's documents and their metadata (016); it is not hand-edited. |
| RG-2 | **The Registry is read-only for consumers.** The Governance Engine (014) and the Developer Platform (018) read the Registry; they do not modify it. |
| RG-3 | **The Registry is rebuildable.** The Registry can be rebuilt from the repository at any time; it is not authoritative (the repository is authoritative). |
| RG-4 | **The Registry is runtime-independent.** The Registry indexes architectural artifacts, which are runtime-independent; runtime-specific artifacts are tagged with their runtime. |

---

# 4. Architecture

## 4.1 The Artifact Catalogue

The Registry indexes the following artifact types:

| Artifact type | Source | Identity scheme |
|---------------|--------|-----------------|
| **Constitution** | `006` | `reg:constitution:006` |
| **Constitutional specification** | `000`–`005` | `reg:spec:NNN` (e.g., `reg:spec:002`) |
| **Runtime architectural specification** | `007`–`012` | `reg:spec:NNN` |
| **Platform engineering specification** | `013`–`018` | `reg:spec:NNN` |
| **Runtime constitution (GFS)** | `docs/genesis/constitutions/` | `reg:gfs:NNN` |
| **Ontology (GO)** | `docs/genesis/ontology/` | `reg:go:NNN` |
| **PKP specification** | `docs/genesis/specifications/pkp/` | `reg:pkp:NN` |
| **Schema** | `docs/genesis/schemas/` | `reg:schema:NNN` |
| **Pattern** | `docs/genesis/patterns/` | `reg:pattern:NNN` |
| **Template** | `docs/genesis/templates/` | `reg:template:NNN` |
| **Workflow** | `docs/genesis/workflows/` | `reg:workflow:NNN` |
| **Agent specification** | `docs/genesis/agents/` | `reg:agent:NNN` |
| **ADR** | `genesis/decisions/` | `reg:adr:NNN` |
| **Constitutional prompt** | `genesis/constitutional-prompts/` | `reg:prompt:NNN` |
| **Architectural prompt** | `genesis/architectural-prompts/` | `reg:prompt:NNN` |
| **Architecture review** | `genesis/architecture-reviews/` | `reg:review:NNN` |

## 4.2 The Registry Entry

Every Registry entry has:

| Field | Definition |
|-------|-----------|
| **identity** | The Registry identity (Part 4.1). |
| **document_identity** | The document's COM identity or file path. |
| **type** | The artifact type (Part 4.1). |
| **constitutional_tier** | Tier 0/1/2/3/4 (`006` Part 1.5). |
| **deriving_authority** | The artifact from which this artifact derives authority. |
| **dependencies** | The artifacts this artifact depends on. |
| **dependents** | The artifacts that depend on this artifact (reverse lookup). |
| **owner** | The body responsible for the artifact (`013` Part 4.3). |
| **version** | The artifact's current version. |
| **status** | `draft / reviewed / ratified / published / deprecated / obsolete / archived`. |
| **metadata** | The document's metadata (016), as parsed from the document. |
| **review_references** | References to architecture reviews that covered this artifact. |
| **adr_references** | References to ADRs that affect this artifact. |

## 4.3 The Authority Graph

The Registry builds the **authority graph**: a directed graph where an edge `A derives_authority_from B` means artifact A derives its constitutional authority from artifact B. The authority graph mirrors the constitutional tier hierarchy:

```
006 (Constitution, Tier 0)
   │
   ├── 000 derives_authority_from 006
   ├── 001 derives_authority_from 006
   ├── 002 derives_authority_from 006
   ├── ... (all Tier 2 specs derive from 006)
   │
   ├── GFS-000 derives_authority_from 006 (Tier 1)
   ├── GFS-001 derives_authority_from GFS-000
   ├── ... (GFS chain)
   │
   ├── GO-001 derives_authority_from GFS-009
   ├── GO-002 derives_authority_from GFS-009
   ├── ... (GO derives from GFS-009)
   │
   └── PKP-00 derives_authority_from 001 §5
       ... (PKP derives from 001)
```

The authority graph is what the Governance Engine (014) traverses to verify that every artifact's authority is valid and that no artifact derives from a non-existent or non-ratified source.

## 4.4 The Dependency Graph

The Registry builds the **dependency graph**: a directed graph where an edge `A depends_on B` means artifact A references artifact B (cross-reference, conceptual dependency, or structural dependency). The dependency graph enables:

- **Impact analysis**: if artifact B changes, which artifacts (A) depend on it?
- **Completeness check**: does artifact A reference a non-existent artifact B?
- **Circular dependency detection**: does the dependency graph have cycles?

## 4.5 The Version Registry

The Registry tracks every artifact's version history:

| Field | Definition |
|-------|-----------|
| **current_version** | The artifact's current version. |
| **version_history** | The lineage of versions (via `amends` edges). |
| **ratification_dates** | When each version was ratified. |

## 4.6 The Review Registry

The Registry tracks every architecture review:

| Field | Definition |
|-------|-----------|
| **review_identity** | `reg:review:NNN`. |
| **subject** | The artifact reviewed. |
| **findings** | The review's findings (from `genesis/architecture-reviews/`). |
| **adr_candidates** | ADRs identified by the review. |
| **date** | When the review was performed. |

## 4.7 The Status Registry

The Registry tracks every artifact's status:

| Status | Meaning |
|--------|---------|
| `draft` | The artifact is drafted but not reviewed. |
| `reviewed` | The artifact has passed constitutional review. |
| `ratified` | The artifact is ratified by the human. |
| `published` | The artifact is the canonical version. |
| `deprecated` | The artifact is deprecated. |
| `obsolete` | The artifact is obsolete. |
| `archived` | The artifact is archived. |

## 4.8 The Discovery Model

The Registry supports discovery queries:

| Query | Purpose |
|-------|---------|
| `lookup(reg-identity)` | Fetch a Registry entry by identity. |
| `semantic_search(type, attribute, value)` | Find artifacts by type or attribute. |
| `authority_graph(artifact)` | Traverse the authority graph from an artifact. |
| `dependency_graph(artifact)` | Traverse the dependency graph from an artifact. |
| `impact_analysis(artifact)` | Find all artifacts that depend on a given artifact. |
| `reverse_lookup(artifact)` | Find all artifacts that reference a given artifact. |
| `status_search(status)` | Find all artifacts with a given status. |

---

# 5. Components

| Component | What it is |
|-----------|-----------|
| **Registry Builder** | Scans the repository and builds the Registry from documents and metadata. |
| **Authority Graph** | The directed graph of authority relationships. |
| **Dependency Graph** | The directed graph of dependency relationships. |
| **Version Registry** | The version history of every artifact. |
| **Review Registry** | The registry of architecture reviews. |
| **Status Registry** | The status of every artifact. |
| **Query Interface** | The discovery model (Part 4.8). |

---

# 6. Responsibilities

| Body | Registry responsibility |
|------|------------------------|
| **Registry Builder** | Builds and updates the Registry from the repository. |
| **Governance Engine (014)** | Reads the Registry to validate the architecture. |
| **Developer Platform (018)** | Reads the Registry for discovery, navigation, and reporting. |
| **Constitutional Review Board** | Reads the Registry for audit and review. |
| **AI agents** | Read the Registry to discover and navigate the architecture. |

---

# 7. Governance

## 7.1 Registry Evolution

The Registry's architecture evolves under the Constitution:

| Change type | Authority |
|--------------|-----------|
| **New artifact type** | Architectural amendment to this specification. |
| **New query type** | Architectural amendment to this specification. |
| **New graph type** | Architectural amendment to this specification. |

## 7.2 Registry and the Constitution

The Registry is governed by L-4 (shared semantic model) and L-5 (identity, provenance, lifecycle). The Registry's identity scheme is an extension of the COM's; the Registry's relationships are extensions of the COM's. The Registry is the architectural layer's analog of the PKG.

## 7.3 Registry Integrity

The Registry's integrity is verified by the Governance Engine (014):

- Every artifact in the repository has a Registry entry.
- Every Registry entry's metadata matches the document's actual metadata.
- The authority graph is acyclic (no artifact derives from itself).
- The dependency graph has no broken references.

---

# 8. Lifecycle

```
repository scanned → Registry built → (artifact added/changed) → Registry updated → (artifact deprecated) → Registry status updated → (artifact archived) → Registry status updated
```

The Registry is rebuilt or incrementally updated whenever the repository changes. The Registry is not authoritative (RG-3); the repository is authoritative. The Registry can be rebuilt from the repository at any time.

---

# 9. Integration

| Spec | Integration |
|------|-------------|
| `013` (Repository) | The Registry is built from the repository. |
| `014` (Governance Engine) | The Governance Engine reads the Registry. |
| `016` (Metadata) | The Registry is populated from documents' metadata. |
| `017` (Validation Rules) | The validation rules operate on the Registry. |
| `018` (Developer Platform) | The Developer Platform queries the Registry. |
| `004` (COM) | The Registry's identity and relationship model extends the COM's. |
| `012` (ATLAS) | ATLAS persists the Registry (the Registry is an architectural artifact). |

---

# 10. Migration

## 10.1 Migration Phases

### Phase REG-1 — Registry Builder
- Implement the Registry Builder that scans the repository and builds the Registry from documents and metadata (016).

### Phase REG-2 — Authority and Dependency Graphs
- Build the authority graph (Part 4.3) and the dependency graph (Part 4.4) from the Registry entries.

### Phase REG-3 — Query Interface
- Implement the discovery model (Part 4.8).

### Phase REG-4 — Governance Integration
- Integrate the Registry with the Governance Engine (014) for validation.

### Phase REG-5 — Developer Platform Integration
- Integrate the Registry with the Developer Platform (018) for discovery and navigation.

## 10.2 Backward Compatibility

| Existing artifact | Compatibility | Action |
|-------------------|---------------|--------|
| All repository documents | **Preserved.** The Registry indexes them; it does not modify them. | None. |
| `/genesis/` institutional memory | **Preserved.** The Registry indexes prompts, reviews, ADRs. | None. |

## 10.3 Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Registry staleness.** The Registry may become stale if the repository changes without a rebuild. | Medium | The Registry is rebuilt on every commit (CI integration, 018); staleness is bounded. |
| **Metadata gaps.** Documents without metadata (016) cannot be registered. | Medium | Phase REP-1 (013) backfills metadata; the Registry Builder skips unregistered documents and reports them as drift. |

---

# 11. Future Evolution

## 11.1 Real-Time Registry
The Registry may evolve to update in real time as documents are edited, enabling live architecture visualization.

## 11.2 Cross-Repository Registry
For multiple runtimes, the Registry may index multiple repositories, enabling cross-runtime architecture discovery.

## 11.3 AI-Native Discovery
AI agents may query the Registry in natural language ("which specifications define the CIR?"), with the Query Interface translating to Registry queries.

---

## Architectural Rules (Restated)

This specification produced no implementation code. It defines the Architecture Registry as the platform's machine-readable map of itself — a typed graph of every architectural artifact, queryable by the Governance Engine and the Developer Platform, derived from the repository's documents and metadata.

---

## Cross-References

| Reference | Relevance |
|-----------|-----------|
| `006` (Constitution) | L-4, L-5 govern the Registry. |
| `013` (Repository) | The Registry is built from the repository. |
| `014` (Governance Engine) | Reads the Registry for validation. |
| `016` (Metadata) | The Registry is populated from metadata. |
| `017` (Validation Rules) | Operate on the Registry. |
| `018` (Developer Platform) | Queries the Registry. |
| `004` (COM) | The Registry's identity and relationship model extends the COM's. |
| `012` (ATLAS) | Persists the Registry. |

---

**End of Specification.**