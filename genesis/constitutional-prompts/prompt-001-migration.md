# Prompt 001 — GENESIS 2.0 Migration Specification

**Status:** Constitutional Prompt — Design History Artifact
**Date:** 2026-07-21
**Corresponding Specification:** `001 — GENESIS 2.0 Migration Specification.md` (located at `docs/genesis/specifications/migration/`)
**Purpose:** Preserve the intent behind the constitutional document, not only the result. This prompt is part of the project's design history and enables consistent regeneration, review, or extension of the corresponding specification.

---

## Role

You are the Chief Enterprise Architect of the Cinema Production Engine (CPE).

## Objective

Produce the master migration blueprint that classifies every existing subsystem of the repository into a four-pillar architecture (GENESIS, PROMETHEUS, ATLAS, ORACLE), defines the canonical compiler pipeline, defines the canonical Production Knowledge Package, and sequences the migration from the current state to the target state.

The document must:

- Analyze the current architecture's strengths, weaknesses, duplications, technical debt, inconsistencies, overlapping responsibilities, and missing abstractions.
- Define the four-pillar model with boundary contracts and cross-pillar communication invariants.
- Redefine GENESIS from a "pre-production system" to an "AI Film Director and Production Compiler."
- Specify the canonical compiler pipeline (19 passes) with fast mode and deep mode.
- Specify the canonical Production Knowledge Package with artifacts, ownership, lifecycle, identifiers, dependency graph, and regeneration rules.
- Inventory existing constitutions and define new derived standards required.
- Define the migration roadmap with phases, risks, and backward compatibility.

## Architectural Rules

- Do NOT generate implementation code.
- Produce an enterprise-grade constitutional architecture specification.
- Ground every recommendation in the existing repository.
- Preserve all existing constitutions (GFS-000..009), ontologies (GO-001..119), PKP specifications (PKP-00..18), workflows, patterns, and templates.
- Extend rather than replace.
- Never duplicate existing concepts.

## Output

> **001 — GENESIS 2.0 Migration Specification**

This document becomes the master migration blueprint. All future implementation work follows the ordering and classification defined here.

---

## Design Intent Notes

This prompt was crafted to force a non-disruptive migration: the existing repository had substantial architectural capital (10 constitutions, 28 ontologies, 19 PKP specs) that had to be preserved, while three parallel pre-production paths, scattered media services, in-memory state, and fragmented evaluation had to be unified. The prompt explicitly forbade invention and mandated grounding in existing files, ensuring the migration would strengthen rather than abandon the existing architecture.