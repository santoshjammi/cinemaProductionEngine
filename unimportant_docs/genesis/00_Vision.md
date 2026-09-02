Genesis Master Specification
00 — Vision

Document ID: GMS-000
Title: Genesis Master Specification — Vision
Version: 1.0.0
Status: Master Specification
Authority: Derived from GFS-000 Constitutional Charter

1. Purpose

This document is the top-level master specification of the Genesis Engine. It is the "brain" for every coding agent, every contributor, and every downstream consumer. It consolidates the vision, philosophy, architecture overview, constitutional principles, and the rules that govern every file, every name, and every line of code in this repository.

When in doubt, start here. Every other document in this repository derives from this one.

2. Vision

Genesis is the Pre-Production Intelligence System of Movie OS. It transforms incomplete human creative intent into complete, validated, internally consistent, and production-ready structured knowledge.

Genesis is not a content generator. It is not a rendering engine. It is not an animation system. It is the authoritative source of truth for every production decision *before* any media generation begins.

3. Mission

Genesis exists to reduce ambiguity. Every operation must increase clarity, consistency, completeness, or confidence within a production. If an operation does not reduce uncertainty, it does not belong in Genesis.

4. Philosophy

- Knowledge precedes production.
- The graph is canonical; documents are projections.
- Constitutional supremacy outranks engineering convenience.
- Genesis produces knowledge only, never media.
- Implementation independence: knowledge outlives every framework, provider, and runtime.
- Provenance is mandatory; confidence is explicit; validation is continuous.

5. Architecture Overview

Genesis is a strict layer cake:

- Layer 0 — Constitutional (GFS-000..009)
- Layer 1 — Ontology (GO-001..006 core, GO-101..119 domain, GO-201+ specialized)
- Layer 2 — Knowledge (PKG, Provenance, Confidence, Validation)
- Layer 3 — Agents (GAS-001..027 + learning/publishers)
- Layer 4 — Workflows (GWS-001+)
- Layer 5 — Execution (CLI, API, LLM integration, message bus, persistence)

Each layer depends only on the layer beneath it. Cross-layer calls are forbidden. See `architecture/001 — Enterprise Architecture.md` for the full layer definitions.

6. Genesis Foundational Standards (GFS) Overview

The GFS family is the constitutional layer. It cannot be overridden.

- GFS-000 Constitutional Charter — supreme authority, value system, invariants.
- GFS-001 Identity Constitution — what Genesis is and is not.
- GFS-002 Reasoning Constitution — how agents reason.
- GFS-003 Knowledge Constitution — how knowledge is stored, versioned, traced.
- GFS-004 Discovery Constitution — how intent is decomposed.
- GFS-005 Agent Constitution — agent contracts and supervision.
- GFS-006 Validation Constitution — validation rules and findings.
- GFS-007 Governance Constitution — approval, certification, handoff.
- GFS-008 Constitutional Meta-Model — how constitutions are written.
- GFS-009 Constitutional Ontology Framework — how ontologies conform.

See `02_Constitution.md` for the consolidated summary and `03_GFS.md` for the per-standard overview.

7. Genesis Ontology (GO) Overview

The GO family is the vocabulary layer.

- GO-001 Core Ontology — universal concepts.
- GO-002 Semantic Relationship Catalog — typed relationships.
- GO-003 State and Lifecycle — concept lifecycle.
- GO-004 Confidence and Provenance — assertion metadata.
- GO-005 Creative Intent — input concepts.
- GO-006 Production Readiness — certification concepts.
- GO-101..119 Domain Ontologies — narrative, character, world, psychology, visual, audio, etc.
- GO-201+ Specialized Ontologies — grammar-specific extensions (e.g., psychological cinema).
- GO-301+ Production Ontologies — production-specific extensions.
- GO-200+ Generated Ontologies — compiler-derived ontologies.

See `04_GO.md` for the per-ontology overview.

8. Layer Architecture (4-Layer View)

From the perspective of a downstream consumer, Genesis exposes four conceptual layers:

1. Knowledge — the PKG and its ontologies.
2. Specifications — materialized views and prompts.
3. Production — the certified PKP.
4. Delivery — the handoff to the Studio Engine.

See `01_Architecture.md` for the consolidated architecture document.

9. Knowledge Graph Architecture

The Production Knowledge Graph (PKG) is the canonical data structure. It stores instances of every ontology concept, their relationships, confidence, provenance, and lifecycle state. Materialized views (documents, manifests, prompts) are derived projections and may be invalidated at any time.

See `05_KnowledgeGraph.md` for the full knowledge graph document.

10. Naming Conventions

- Files: `NNN — Title.md` (em-dash preferred, regular dash acceptable).
- Documents: `GFS-NNN`, `GO-NNN`, `GAS-NNN`, `GARCH-NNN`, `GWS-NNN`, `GSPEC-NNN`, `GSS-NNN`, `GREF-NNN`, `GTMP-NNN`.
- Concepts: PascalCase, singular, English.
- Properties: camelCase.
- Relationships: snake_case.
- Enumerations: UPPER_SNAKE_CASE.

11. Generation Rules

- Every ontology concept must derive from a Core or Domain concept.
- Every assertion must carry confidence and provenance.
- Every workflow must reference GWS-001 as the baseline.
- Every agent must conform to the common agent contract (GARCH-005).
- Every PKP must satisfy the validation rules in GARCH-008.

12. File Layout

- `constitutions/` — GFS-000..009.
- `ontology/` — GO-001..301+ organized by domain.
- `architecture/` — GARCH-001..009.
- `agents/` — GAS-001..027 organized by role.
- `workflows/` — GWS-001+ organized by type.
- `specifications/` — GSPEC-NNN+ organized by category.
- `schemas/` — GSS-NNN+.
- `references/` — GREF-NNN+.
- `templates/` — GTMP-NNN+.
- `examples/` — filled-in productions.
- `decisions/` — ADRs.
- `compiler/`, `generators/`, `runtime/`, `validation/`, `governance/` — subsystem docs.

13. Validation Rules

- Every document must declare Document ID, Version, and Status.
- Every ontology must derive from GO-001.
- Every agent spec must define inputs, outputs, dependencies.
- Every specification must define validation requirements.
- Every workflow must reference GWS-001.

14. Coding Standards

- Implementations live outside this repository (in `movie_os/`). This repository is the specification.
- Implementations must satisfy every interface declared in GARCH-002.
- No implementation may treat a projection as canonical.
- No implementation may write to the PKG outside an agent's constitutional authority.

15. Documentation Standards

- Every document opens with a header block: title, Document ID, Version, Status, Authority.
- Documents are numbered uniquely within their directory.
- Cross-references use the document ID (e.g., `GARCH-005`), not file paths.
- No document may contradict a higher-authority document.

16. Approval

This master specification is the canonical entry point for the Genesis Engine. Every other document in this repository is subordinate to it.