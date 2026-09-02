# Prompt 004 — Creative Object Model (COM) & Semantic Architecture Specification

**Status:** Constitutional Prompt — Design History Artifact
**Date:** 2026-07-21
**Corresponding Specification:** `004 — Creative Object Model (COM) & Semantic Architecture Specification.md` (located at repository root)
**Purpose:** Preserve the intent behind the constitutional document, not only the result. This prompt is part of the project's design history and enables consistent regeneration, review, or extension of the corresponding specification.

---

## Role

You are the Chief Enterprise Architect of the Cinema Production Engine (CPE).

## Objective

Design the canonical **Creative Object Model (COM)** and the **Semantic Architecture** that underpins the entire Cinema Production Engine. The COM is the canonical semantic model of filmmaking. Every subsystem must use these semantic objects. No subsystem may invent its own competing definitions.

The COM is the shared language spoken by: Human Authoring, GENESIS, Director Intelligence, Compiler Passes, PROMETHEUS, ORACLE, ATLAS.

The document must define:

1. **Philosophy** — Why filmmaking requires a semantic programming model, why ontology alone is insufficient, why prompts are insufficient, why semantic objects are required, why every component must share a common language. How COM differs from CIS/CIR/PKP/Ontology/Knowledge Graph/Runtime.
2. **Creative Object Model** — Every first-class Creative Object (Story, Narrative, Theme, Scene, Beat, Character, Dialogue, Emotion, Reveal, Setup, Payoff, Shot, Camera, Lighting, Music Theme, Timeline, Creative Decision, Creative Intent, Creative Artifact, Creative Version, Creative Branch, etc.). Each object defines purpose, architectural responsibility, identity, ownership, lifecycle, parent/child, cardinality, composition, traceability, versioning, immutability, consumers, producers, validation.
3. **Creative Relationship Model** — Every legal relationship (contains, references, depends_on, causes, creates, resolves, transitions_to, mirrors, contrasts, echoes, extends, specializes, inherits, precedes, follows, belongs_to, produces, consumes, validates, learns_from, archives). Semantics, directionality, cardinality, ownership, validation, lifecycle, examples.
4. **Creative Operations** — All legal operations (Create, Delete, Split, Merge, Replace, Branch, Freeze, Archive, Restore, Escalate Emotion, Insert Beat, Shift POV, Add Reveal, Compress Runtime, Localize, Translate, Adapt, Version, Rollback, etc.). Which preserve intent, which require human/Director approval, which invalidate CIR/PKP, which require regeneration.
5. **Semantic Invariants** — Constitutional rules that always remain true (every Scene has Purpose, every Payoff references a Setup, every Dialogue has a speaker, every Creative Decision has provenance, etc.). These become ORACLE validation rules.
6. **Creative State Model** — Lifecycle state machines for Story, Scene, Character, Dialogue, Creative Decision, Creative Artifact, Creative Branch, Creative Version.
7. **Semantic Query Model** — How every component references creative objects (lookup, traceability, dependency traversal, lineage, provenance, impact analysis, semantic search, reverse lookup). How ORACLE and ATLAS use these.
8. **Mapping Architecture** — The full pipeline: Human → CIS → COM → CIR → PKP → PROMETHEUS → Media → ORACLE → ATLAS. Which layer owns what, how objects evolve, what remains immutable, what becomes executable, what becomes knowledge.
9. **Compiler Semantics** — How GENESIS becomes a compiler operating on creative objects. Semantic analysis, object validation, dependency resolution, creative transformations, optimization, deterministic compilation, incremental compilation, partial regeneration. Why passes manipulate objects, not raw text.
10. **Governance** — Who introduces new object types, how semantic evolution occurs, version compatibility, backward compatibility, deprecation, migration, validation, constitutional precedence.
11. **Migration Strategy** — How COM integrates into the existing architecture, preserving 00/001/002/003/GO/GFS/PKP. No duplicate concepts, no competing models, no parallel architectures.

## User Amendment

The user recommended **freezing the architecture after 004** — reading 000–004 together as a single constitutional document and checking for duplicate concepts, overlapping responsibilities, inconsistent terminology, or missing abstractions before continuing to 005+. The five documents (Vision, Migration, Director Intelligence, CIS, COM) define the intellectual foundation; if that foundation is coherent, every subsequent specification (PKP, PROMETHEUS, ORACLE, ATLAS) will be significantly easier to design and far more consistent.

## Architectural Rules

- Architecture only. No implementation, YAML, JSON, schemas, or source code.
- Ground every recommendation in the existing repository.
- Cross-reference every relevant constitutional document, ontology, specification, workflow, pattern, template, and migration document.
- Every recommendation should strengthen the existing architecture rather than replacing it.
- Should read like the language specification of an operating system rather than documentation for a software project.

## Output

> **004 — Creative Object Model (COM) & Semantic Architecture Specification**

---

## Design Intent Notes

This prompt was crafted to define the **semantic programming model** — the typed object model that every subsystem speaks, distinct from the ontology (which defines vocabulary) and the PKG (which stores instances). The critical insight: ontology is the dictionary; the COM is the type system. The COM binds ontology terms to object identity, lifecycle, operations, and invariants, enabling structural enforcement of invariants that prose and prompts cannot enforce. The user's freeze recommendation triggered a cross-document coherence review that found and fixed two defects: residual "Creative Council" terminology in 002, and a missing `Performance` object detail in 004's catalog.