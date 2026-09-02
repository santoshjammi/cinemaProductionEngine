# Prompt 003 — Creative Intent Specification (CIS) Architecture

**Status:** Constitutional Prompt — Design History Artifact
**Date:** 2026-07-21
**Corresponding Specification:** `003 — Creative Intent Specification (CIS) Architecture.md` (located at repository root)
**Purpose:** Preserve the intent behind the constitutional document, not only the result. This prompt is part of the project's design history and enables consistent regeneration, review, or extension of the corresponding specification.

---

## Role

You are the Chief Enterprise Architect of the Cinema Production Engine (CPE).

## Objective

Design the canonical **Creative Intent Specification (CIS)** — the primary input contract for GENESIS. The CIS replaces the traditional concept of a "Synopsis." Every production begins with a CIS. GENESIS never reasons directly from unstructured text.

The CIS captures **WHAT** the creator wants. GENESIS determines **HOW** to realize that intent. PROMETHEUS determines **HOW** to render it.

The document must define:

1. **Philosophy** — Why synopsis is insufficient, why creative intent is richer, why intent must be explicit, why deterministic production requires structured intent. Human → CIS → GENESIS relationship.
2. **CIS Architecture** — 24 domains: Story Intent, Theme, Message, Emotional Journey, Emotion Transition Graph, Audience, Educational/Entertainment Objectives, Platform/Runtime Goals, Narrative/Ethical Constraints, Cultural Context, Language Strategy, Accessibility/Localization Intent, Visual/Audio/Music Expectations, Ending Intent, Reflection Goals, Creative Constraints, Presentation Profile, Provenance. Domain relationships and consistency rules.
3. **Emotional Architecture** — Emotion as a first-class architectural concept. Baseline, peaks, valleys, transitions, contrast, resolution, memory, audience journey. Emotion Transition Graph structure. How these become inputs to Director Intelligence.
4. **Audience Model** — Target audience, maturity, prior knowledge, cultural familiarity, language proficiency, attention expectations, platform consumption patterns. How GENESIS adapts without changing intent.
5. **Creative Constraints** — Budget, production limitations, ethical boundaries, historical accuracy, educational fidelity, religious sensitivity, brand, platform restrictions. Why constraints are intent, not implementation. Precedence.
6. **Presentation Profiles** — Intent vs. presentation separation. Visual/editing/music/voice/narration/pacing/color/camera presentation domains. Why profiles influence execution but do not redefine intent. Relationship to Creative Profiles (002).
7. **Human Authoring Workflow** — Progressive refinement, guided authoring, templates, defaults, validation, review, approval, revision.
8. **CIS Validation** — Completeness, consistency, ambiguity detection, conflict detection, missing intent, contradictions, human approval, readiness for GENESIS.
9. **CIS ↔ CIR ↔ PKP** — The three-artifact chain. Why all three are required. Human intent / Director reasoning / Production execution.
10. **Lifecycle** — Creation, revision, versioning, branching, approval, production, reuse, archival, learning.
11. **Migration Strategy** — From synopsis-based workflows to CIS. Backward compatibility. Migration principles.

## User Amendment

The user provided an ordering rationale: the CIS should come **before** the PKP (004 in the planned sequence, not PROMETHEUS), because the PKP is the compiled result of the CIS passing through Director Intelligence. The clean compiler-inspired progression:

```
Human Creator → CIS → GENESIS Director Intelligence → CIR → PKP → PROMETHEUS → Film → ORACLE → ATLAS
```

This ordering establishes an unambiguous contract for every downstream component before any of them are designed.

## Architectural Rules

- Do NOT generate implementation, schemas, YAML, or JSON.
- Design the architecture only.
- Ground every recommendation in the existing repository.

## Output

> **003 — Creative Intent Specification (CIS) Architecture**

---

## Design Intent Notes

This prompt was crafted to replace the unstructured synopsis with a validated, versioned, structured input contract. The critical insight: deterministic production begins with deterministic intent, and the CIS is the deterministic intent artifact. The ordering rationale (CIS before PKP) encoded the compiler metaphor: CIS is the source program, CIR is the AST, PKP is the compiled binary. The separation of intent (D-1..D-22) from presentation (D-23) was a structural defense against the failure mode where presentation preferences silently rewrite creative intent.