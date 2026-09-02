# Prompt 002 — Director Intelligence & Creative Reasoning Architecture Specification

**Status:** Constitutional Prompt — Design History Artifact
**Date:** 2026-07-21
**Corresponding Specification:** `002 — Director Intelligence & Creative Reasoning Architecture Specification.md` (located at repository root)
**Purpose:** Preserve the intent behind the constitutional document, not only the result. This prompt is part of the project's design history and enables consistent regeneration, review, or extension of the corresponding specification.

---

## Role

You are the Chief Enterprise Architect of the Cinema Production Engine (CPE).

## Objective

Define the intelligence architecture that sits **above every compiler pass** inside GENESIS. This document defines **what happens BEFORE compilation** — how creative reasoning works, how cinematic decisions are made, how artistic choices become deterministic compiler inputs. This document defines the **mind of GENESIS**.

The document must define:

1. **Director Intelligence Philosophy** — What an AI Film Director is, how it differs from an LLM/agent/compiler, why creative reasoning precedes compilation, why rendering never invents creative ideas, why creative intent is deterministic. Design principles, invariants, boundaries, authority, human collaboration.
2. **Creative Council (renamed Directorial Board)** — Not one director but a hierarchical board of specialized directors (Chief, Story, Narrative, Character, Psychology, Performance, Dialogue, Visual, Cinematography, Lighting, Production Designer, Audio, Music, Sound, Editorial, Platform, Continuity, Quality). Each defined by mission, authority, responsibilities, inputs, outputs, decision scope, dependencies, compiler pass ownership, PKP ownership, KG/constitution/ontology dependencies. Communication, consensus, escalation rules.
3. **Creative Decision Lifecycle** — Idea → Research → Context → Alternatives → Trade-off → Selection → Review → CIR entry → Compiler input → PKP mapping → Validation → Freeze. Provenance, confidence, rationale, evidence, alternatives, rejected options, assumptions.
4. **Creative Decision Graph** — Every decision as a graph node; dependencies, causal links, inheritance, constraints, priority, confidence, traceability, explainability, conflict detection. Integration with the PKG.
5. **Creative Reasoning Engine** — Idea generation, alternative exploration, evaluation. Reasoning modes: emotional, symbolic, psychological, cinematic, audience, platform. Reasoning models for suspense, pacing, silence, transitions, rhythm, metaphors, callbacks, foreshadowing, payoff, motivations. How reasoning becomes deterministic.
6. **Director Memory** — Accepted/rejected ideas, revisions, rationale, inspirations, references, motifs, themes, human overrides, style evolution, production history. Integration with ATLAS.
7. **Director ↔ Compiler Boundary** — Director decides; compiler executes. Passes may never invent dialogue/symbolism/emotion/pacing/camera/music/editing philosophy. Every pass traces to a creative decision. Every PKP artifact references its originating decision.
8. **Creative Decision Conflict Resolution** — Priority hierarchy, constitutional precedence, weighted reasoning, voting, confidence, human override, arbitration, audit trail.
9. **Creative Profiles** — Hollywood, Psychological Cinema, Pixar, Anime, Documentary, Devotional, Educational, Historical, Kids, Commercial, YouTube Premium. Profiles influence decisions, not prompts.
10. **Human Collaboration** — Roles (Director, Producer, Reviewer, Creative Partner, Client, Studio). Approvals, revisions, amendments, overrides, locking, collaborative editing, review workflow.
11. **Creative Metrics** — Emotional effectiveness, narrative coherence, character depth, psychological realism, dialogue quality, pacing, symbolism, audience engagement, replay value, retention, continuity, cinematic realism, platform readiness. ORACLE validation of each.
12. **Creative Intent Record (CIR)** — The canonical representation of creative reasoning; the AST of filmmaking. Purpose, lifecycle, schema philosophy, identifiers, versioning, relationship to PKP/PKG/compiler/ATLAS/ORACLE. Canonical pipeline. Why CIR and PKP are separate.
13. **Migration Strategy** — From compiler-first to Director-first architecture.

## User Amendment

The Creative Council was renamed to **Directorial Board**. The hierarchy was specified as:

```
Chief Director
├── Story Director
├── Narrative Director
├── Character Director
├── Psychology Director
│   ├── Performance Director
│   └── Dialogue Director
├── Visual Director
│   ├── Cinematography Director
│   ├── Lighting Director
│   └── Production Designer
├── Audio Director
│   ├── Music Director
│   └── Sound Director
├── Editorial Director
├── Platform Director
├── Continuity Director
└── Quality Director
```

## Architectural Rules

- Do NOT generate implementation code, Python, TypeScript, YAML, or JSON schemas.
- Produce an enterprise-grade constitutional architecture specification.
- Ground every recommendation in the existing repository.
- Preserve all existing constitutions, ontologies, PKP specifications.
- Extend rather than replace. Never duplicate existing concepts.
- Cross-reference existing documents wherever applicable.

## Output

> **002 — Director Intelligence & Creative Reasoning Architecture Specification**

---

## Design Intent Notes

This prompt was crafted to define the layer **above** the compiler — the creative reasoning that authorizes every compiler pass. The critical insight encoded in the prompt: GENESIS is not merely a compiler, it is an AI Film Director, and compilation is simply the execution of creative decisions. The CIR was introduced as the AST-analog of filmmaking, distinct from the PKP (the compiled binary), enabling surgical revision and explainability. The user's rename from "Creative Council" to "Directorial Board" and the explicit hierarchy reflected a cinema-production-team metaphor rather than a committee metaphor.