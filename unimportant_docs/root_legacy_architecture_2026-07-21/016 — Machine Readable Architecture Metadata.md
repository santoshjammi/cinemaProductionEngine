# 016 — Machine Readable Architecture Metadata

**Status:** Platform Engineering Specification — Phase III
**Version:** 1.0.0
**Date:** 2026-07-21
**Derives Authority From:** `006` (Constitution); `013` (Repository Architecture, RP-3 metadata is mandatory); `015` (Architecture Registry, populated from metadata).
**Precedence:** Below the Constitution. This specification defines the **metadata contract** that every architectural artifact in the repository must carry.
**Scope:** Metadata philosophy, taxonomy, canonical fields, version semantics, authority/dependency/review/ADR/ontology/schema references, validation requirements, lifecycle, evolution.

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

## 1.1 Metadata Makes the Repository Machine-Readable

A document without metadata is prose — readable by humans, opaque to machines. A document with metadata is a **typed artifact** — readable by humans and machines, locatable by the Registry (015), validatable by the Governance Engine (014), and navigable by AI agents. Metadata is the bridge between the human-authored repository and the machine-operated platform.

## 1.2 Constitutional Derivation

| Law | How it governs metadata |
|-----|------------------------|
| L-4 (Shared Semantic Model) | Metadata uses the COM's identity and relationship vocabulary. |
| L-5 (Objects Have Identity, Provenance, Lifecycle) | Metadata declares the artifact's identity, provenance, and lifecycle. |
| L-22 (Amendments Require Process) | Metadata's version field tracks amendments. |

---

# 2. Objectives

| # | Objective |
|---|-----------|
| O-1 | Every architectural artifact in the repository carries machine-readable metadata. |
| O-2 | Metadata declares the artifact's constitutional tier, deriving authority, and dependencies. |
| O-3 | Metadata enables the Registry (015) to build the authority and dependency graphs. |
| O-4 | Metadata enables the Governance Engine (014) to validate the artifact. |
| O-5 | Metadata enables AI agents to discover and navigate the architecture. |

---

# 3. Principles

| # | Principle |
|---|-----------|
| MP-1 | **Metadata is mandatory.** (013 RP-3) A document without metadata is non-compliant. |
| MP-2 | **Metadata is machine-parseable.** The metadata is in a structured format at the document's head. |
| MP-3 | **Metadata is minimal.** The metadata contains only what the Registry and the Governance Engine need; it does not duplicate the document's content. |
| MP-4 | **Metadata is versioned with the document.** When the document is amended, the metadata is updated to reflect the new version. |

---

# 4. Architecture

## 4.1 The Metadata Header

Every architectural artifact begins with a **metadata header** — a structured block declaring the artifact's constitutional identity. The header is at the document's head, before the content.

The metadata header's structure (defined architecturally; the specific format — YAML frontmatter, TOML, custom — is an implementation concern, not architectural):

```
[Metadata Header]
   document_id:         <reg-identity>          (e.g., reg:spec:006)
   title:                <document title>
   type:                 <artifact type>          (Part 4.2)
   constitutional_tier:  <0 | 1 | 2 | 3 | 4>      (006 Part 1.5)
   version:              <major.minor.patch>
   status:               <draft | reviewed | ratified | published | deprecated | obsolete | archived>
   deriving_authority:   <reg-identity>           (the artifact this derives from)
   dependencies:         [<reg-identity>, ...]    (artifacts this depends on)
   ontology_references:  [<go-identity>, ...]     (ontology terms used)
   schema_references:    [<schema-identity>, ...] (schemas referenced)
   review_references:    [<reg:review:NNN>, ...]  (reviews that covered this artifact)
   adr_references:       [<reg:adr:NNN>, ...]     (ADRs affecting this artifact)
   owner:                <body>                   (013 Part 4.3)
   ratified_at:          <date>                   (when ratified)
   ratified_by:          <human identity>         (L-25)
   preceding_version:    <reg-identity or null>   (for amended artifacts)
   supersedes:           [<reg-identity>, ...]    (if this supersedes prior artifacts)
```

## 4.2 The Metadata Taxonomy

| Field | Type | Purpose |
|-------|------|---------|
| `document_id` | Registry identity | Unique identification in the Registry. |
| `title` | String | Human-readable title. |
| `type` | Enum | The artifact type (015 Part 4.1). |
| `constitutional_tier` | Integer (0–4) | The constitutional tier (`006` Part 1.5). |
| `version` | Semantic version | The artifact's version. |
| `status` | Enum | The artifact's lifecycle status. |
| `deriving_authority` | Registry identity | The artifact this derives authority from. |
| `dependencies` | List of Registry identities | Artifacts this depends on. |
| `ontology_references` | List of GO identities | Ontology terms used in the document. |
| `schema_references` | List of schema identities | Schemas referenced. |
| `review_references` | List of review identities | Reviews that covered this artifact. |
| `adr_references` | List of ADR identities | ADRs affecting this artifact. |
| `owner` | String | The responsible body. |
| `ratified_at` | Date | Ratification timestamp. |
| `ratified_by` | String | The ratifying human (L-25). |
| `preceding_version` | Registry identity or null | For amended artifacts. |
| `supersedes` | List of Registry identities | If this supersedes prior artifacts. |

## 4.3 Version Semantics

The `version` field follows semantic versioning:

| Change type | Version increment |
|--------------|-------------------|
| **Major**: a change that affects the constitutional laws or invariants. | Major (e.g., 1.0.0 → 2.0.0). |
| **Minor**: a change that adds new content without breaking existing dependencies. | Minor (e.g., 1.0.0 → 1.1.0). |
| **Patch**: an editorial correction that does not change meaning. | Patch (e.g., 1.0.0 → 1.0.1). |

## 4.4 Authority References

The `deriving_authority` field names the artifact from which this artifact derives constitutional authority. This is the edge in the authority graph (015 Part 4.3). The Governance Engine (014) validates that:

- The deriving authority exists.
- The deriving authority is ratified.
- The deriving authority's tier is higher than this artifact's tier.

## 4.5 Dependency References

The `dependencies` field names the artifacts this artifact depends on (cross-references, conceptual dependencies). This is the edge in the dependency graph (015 Part 4.4). The Governance Engine validates that:

- Every dependency exists.
- No dependency is circular.

## 4.6 Validation Requirements

The metadata itself has validation requirements (enforced by the Governance Engine, 014, per rules in 017):

| Requirement | Effect on failure |
|-------------|-------------------|
| `document_id` is present and unique. | Blocking. |
| `type` is a valid artifact type. | Blocking. |
| `constitutional_tier` is 0–4. | Blocking. |
| `version` is a valid semantic version. | Blocking. |
| `status` is a valid status. | Blocking. |
| `deriving_authority` references an existing artifact. | Blocking. |
| `dependencies` reference existing artifacts. | Blocking. |
| `owner` is a known body. | Warning. |
| `ratified_at` and `ratified_by` are present if status is `ratified` or `published`. | Blocking. |

---

# 5. Components

| Component | What it is |
|-----------|-----------|
| **Metadata Header** | The structured block at every document's head. |
| **Metadata Parser** | Parses the header into a Registry entry (015). |
| **Metadata Validator** | Validates the header against the requirements (Part 4.6). |

---

# 6. Responsibilities

| Body | Metadata responsibility |
|------|------------------------|
| **Document author** | Ensures the document carries a complete, valid metadata header. |
| **Registry Builder (015)** | Parses the metadata header and builds the Registry entry. |
| **Governance Engine (014)** | Validates the metadata header against the requirements (017). |
| **Constitutional Review Board** | Reviews metadata during constitutional review. |

---

# 7. Governance

| Change type | Authority |
|--------------|-----------|
| **New metadata field** | Architectural amendment to this specification. |
| **New validation requirement** | Architectural amendment to this specification and to 017. |

## 7.1 Constitutional Compliance

| Law | Compliance |
|-----|------------|
| L-4 | Metadata uses the COM's identity vocabulary. |
| L-5 | Metadata declares identity, provenance (via `ratified_by`), and lifecycle (via `status`). |
| L-22 | Metadata's `version` and `preceding_version` track amendments. |

---

# 8. Lifecycle

The metadata's lifecycle is the document's lifecycle (013 Part 8.1):

```
draft → reviewed → ratified → published → (amended → new version) → (deprecated) → (obsolete) → (archived)
```

The `status` field transitions with the document. The `version` increments on amendment. The `preceding_version` references the prior version.

---

# 9. Integration

| Spec | Integration |
|------|-------------|
| `013` (Repository) | Metadata is mandatory (RP-3). |
| `014` (Governance Engine) | Validates metadata (Part 4.6). |
| `015` (Registry) | Registry is populated from metadata. |
| `017` (Validation Rules) | Defines the executable metadata validation rules. |
| `018` (Developer Platform) | Provides tooling for metadata authoring and validation. |

---

# 10. Migration

## 10.1 Migration Phases

### Phase META-1 — Metadata Schema Definition
- Define the metadata schema (Part 4.2) as an architectural standard.

### Phase META-2 — Metadata Backfill
- Add metadata headers to all existing root specifications (000–012).
- Add metadata headers to all GFS, GO, and PKP documents.
- Add metadata headers to all institutional memory documents (prompts, reviews, ADRs).

### Phase META-3 — Metadata Validation
- Deploy the Metadata Validator (Part 5) in the Governance Engine (014).

## 10.2 Backward Compatibility

| Existing artifact | Compatibility | Action |
|-------------------|---------------|--------|
| Root specifications (000–012) | **Preserved.** Metadata is added; content is unchanged. | Phase META-2. |
| All other documents | **Preserved.** | Phase META-2. |

## 10.3 Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Backfill burden.** Adding metadata to many documents is labor-intensive. | Medium | AI agents can assist with backfill under human review. |
| **Metadata staleness.** Authors may forget to update metadata when amending. | Medium | The Governance Engine (014) detects staleness; the Developer Platform (018) provides tooling. |

---

# 11. Future Evolution

## 11.1 Rich Metadata
Future versions may add richer metadata (e.g., change logs, contribution records, review transcripts) as governed extensions.

## 11.2 AI-Generated Metadata
AI agents may generate metadata drafts from document content, with human review and ratification.

## 11.3 Cross-Repository Metadata
For multiple runtimes, metadata may include a `runtime` field, enabling cross-runtime artifact discovery.

---

## Architectural Rules (Restated)

This specification produced no implementation code, no JSON, no YAML. It defines the metadata contract — the mandatory, machine-parseable, minimal header that every architectural artifact carries, declaring its identity, authority, dependencies, and status.

---

## Cross-References

| Reference | Relevance |
|-----------|-----------|
| `006` (Constitution) | L-4, L-5, L-22 govern metadata. |
| `013` (Repository) | RP-3 (metadata is mandatory). |
| `014` (Governance Engine) | Validates metadata. |
| `015` (Registry) | Populated from metadata. |
| `017` (Validation Rules) | Defines executable metadata validation rules. |
| `018` (Developer Platform) | Provides metadata authoring and validation tooling. |

---

**End of Specification.**