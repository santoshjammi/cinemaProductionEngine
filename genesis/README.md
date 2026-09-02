# Institutional Memory — Index

**Status:** Design History Artifact
**Date:** 2026-07-21
**Purpose:** This directory tree preserves the complete institutional memory of the Artificial Creative Intelligence platform — from constitutional intent through architectural realization and the decisions that shaped it.

## Structure

```
genesis/
├── constitutional-prompts/     # Why each constitutional document was created (Phase I)
├── architectural-prompts/      # How each architectural capability should be designed (Phase II)
├── architecture-reviews/       # Coherence checks, gap analyses, cross-document verification
└── decisions/                  # Architecture Decision Records (ADRs) — irreversible decisions
```

## Tiers of Memory

| Tier | Directory | What it preserves | Mutability |
|------|-----------|-------------------|------------|
| **Constitutional Prompts** | `constitutional-prompts/` | The intent behind constitutional documents (000–006). | Immutable once the corresponding specification is frozen. |
| **Architectural Prompts** | `architectural-prompts/` | The intent behind architectural specifications (007+). | Immutable once the corresponding specification is frozen. |
| **Architecture Reviews** | `architecture-reviews/` | Coherence reports produced after each Phase II specification, capturing gap analyses and cross-document verification. | Immutable (they are historical records of a review at a point in time). |
| **ADRs** | `decisions/` | The handful of irreversible decisions that define the platform's identity, with rationale. | Immutable once ratified; superseded by new ADRs, never edited. |

## Naming Conventions

- Constitutional prompts: `prompt-NNN-<short-name>.md`
- Architectural prompts: `prompt-NNN-<short-name>.md` (same pattern; the number matches the spec)
- Architecture reviews: `review-NNN-<short-name>.md` (one per Phase II spec)
- ADRs: `adr-NNN-<short-name>.md` (numbered independently; an ADR may precede or follow a spec)

## Relationship to the Constitution

This institutional memory is governed by the ACI Constitution (`006`). The Freeze Principle (`006` Part 8.8) applies: these documents are frozen at the point their corresponding specification is frozen, and are amended through process, not edited casually.

## Catalog

### Constitutional Prompts (Phase I — frozen)
| Prompt | Specification | Status |
|--------|--------------|--------|
| `prompt-001-migration.md` | `001 — GENESIS 2.0 Migration Specification.md` | Frozen |
| `prompt-002-director-intelligence.md` | `002 — Director Intelligence & Creative Reasoning Architecture Specification.md` | Frozen |
| `prompt-003-cis.md` | `003 — Creative Intent Specification (CIS) Architecture.md` | Frozen |
| `prompt-004-com.md` | `004 — Creative Object Model (COM) & Semantic Architecture Specification.md` | Frozen |
| `prompt-005-cognitive-intelligence.md` | `005 — Cognitive Intelligence Architecture & Creative Faculties Specification.md` | Frozen |
| `prompt-006-constitution.md` | `006 — Artificial Creative Intelligence Constitution & Architectural Governance.md` | Frozen |

### Architectural Prompts (Phase II — frozen)
| Prompt | Specification | Status |
|--------|--------------|--------|
| `prompt-007-cir.md` | `007 — Creative Intent Record (CIR) Architecture.md` | Frozen |
| `prompt-008-compiler.md` | `008 — GENESIS Compiler Architecture.md` | Frozen |
| `prompt-009-pkp.md` | `009 — Production Knowledge Package (PKP) Architecture.md` | Frozen |
| `prompt-010-prometheus.md` | `010 — PROMETHEUS Runtime Architecture.md` | Frozen |
| `prompt-011-oracle.md` | `011 — ORACLE Validation Architecture.md` | Frozen |
| `prompt-012-atlas.md` | `012 — ATLAS Knowledge Architecture.md` | Frozen |

### Architecture Reviews (Phase II — frozen)
| Review | Subject | Status |
|--------|---------|--------|
| `review-007-cir.md` | CIR coherence report | Frozen |
| `review-008-compiler.md` | Compiler coherence report | Frozen |
| `review-009-pkp.md` | PKP coherence report | Frozen |
| `review-010-prometheus.md` | PROMETHEUS coherence report | Frozen |
| `review-011-oracle.md` | ORACLE coherence report | Frozen |
| `review-012-atlas.md` | ATLAS coherence report | Frozen |

### Architecture Decision Records (frozen)
| ADR | Decision | Status |
|-----|----------|--------|
| `adr-001-through-006.md` | Phase II: ADR-001 (CIR as IR), ADR-002 (isolated passes), ADR-003 (PKP read-only), ADR-004 (runtime zero creative authority), ADR-005 (ORACLE advisory), ADR-006 (ATLAS single persistence) | Recommended for ratification |
| `adr-007-through-012.md` | Phase III: ADR-007 (repository mirrors tiers), ADR-008 (governance advisory), ADR-009 (registry derived), ADR-010 (metadata mandatory), ADR-011 (rules are projections), ADR-012 (platform no authority) | Recommended for ratification |

## Phase Status

| Phase | Status | Specifications |
|-------|--------|----------------|
| **Phase I — Constitutional Foundation** | Complete & Frozen | 000–006 |
| **Phase II — Runtime Architecture** | Complete & Frozen | 007–012 |
| **Phase III — Platform Engineering** | Complete & Frozen | 013–018 |

The ACI Platform's architecture is fully specified across three phases:
- **Phase I** defines the constitutional law and the creative front-end (CIS, COM, Creative Mind, Directorial Board, CIR concept).
- **Phase II** defines the runtime back-end (CIR architecture, Compiler, PKP, PROMETHEUS, ORACLE, ATLAS).
- **Phase III** defines the platform engineering layer (Repository, Governance Engine, Registry, Metadata, Validation Rules, Developer Platform).

**The architecture is frozen.** Per the Freeze Principle (`006` Part 8.8), these documents are amended through process, not edited casually. The next milestone is engineering: creating the derived artifacts (ontologies, schemas, contracts, reference implementations, tooling) from this stable foundation.