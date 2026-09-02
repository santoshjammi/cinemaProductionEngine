# 002 — Director Intelligence & Creative Reasoning Architecture Specification

**Status:** Constitutional Architecture Specification — Supreme Authority for Director Intelligence
**Version:** 1.0.0
**Date:** 2026-07-21
**Authority:** Derives from `00 — Cinema Production Engine Vision, Philosophy & Reference Architecture.md` (the Constitutional Architecture) and extends the migration blueprint established by `001 — GENESIS 2.0 Migration Specification.md`. This document is the canonical reference for how creative decisions are made inside the Cinema Production Engine. It governs the layer that sits **above every compiler pass** inside GENESIS.
**Precedence:** Below the Constitutional Architecture (§00). Equal in tier to `001 — GENESIS 2.0 Migration Specification.md`. Above all domain specifications, ontology extensions, workflow definitions, and implementation guides. When this document conflicts with an informal convention, a legacy agent design, or a rendering-time heuristic, this document wins unless the conflict is with the Constitutional Architecture itself.
**Scope:** Director Intelligence, the Directorial Board, the Creative Decision Lifecycle, the Creative Decision Graph, the Creative Reasoning Engine, Director Memory, the Director↔Compiler Boundary, Creative Decision Conflict Resolution, Creative Profiles, Human Collaboration, Creative Metrics, and the **Creative Intent Record (CIR)**.

---

## Table of Contents

**PART 1: DIRECTOR INTELLIGENCE PHILOSOPHY**
- [1.1 What Is an AI Film Director](#11-what-is-an-ai-film-director)
- [1.2 Distinctions from Adjacent Concepts](#12-distinctions-from-adjacent-concepts)
- [1.3 Why Creative Reasoning Must Precede Compilation](#13-why-creative-reasoning-must-precede-compilation)
- [1.4 Why Rendering Must Never Invent Creative Ideas](#14-why-rendering-must-never-invent-creative-ideas)
- [1.5 Why Creative Intent Must Be Deterministic](#15-why-creative-intent-must-be-deterministic)
- [1.6 Design Principles](#16-design-principles)
- [1.7 Architectural Invariants](#17-architectural-invariants)
- [1.8 Boundaries and Decision Authority](#18-boundaries-and-decision-authority)
- [1.9 Human Collaboration Philosophy](#19-human-collaboration-philosophy)

**PART 2: THE DIRECTORIAL BOARD**
- [2.1 Why a Board, Not a Single Director](#21-why-a-board-not-a-single-director)
- [2.2 Board Hierarchy](#22-board-hierarchy)
- [2.3 Director Specifications](#23-director-specifications)
- [2.4 Communication, Consensus, and Escalation](#24-communication-consensus-and-escalation)

**PART 3: CREATIVE DECISION LIFECYCLE**
- [3.1 Lifecycle Stages](#31-lifecycle-stages)
- [3.2 Provenance, Confidence, and Rationale](#32-provenance-confidence-and-rationale)

**PART 4: CREATIVE DECISION GRAPH**
- [4.1 From Decision to Graph](#41-from-decision-to-graph)
- [4.2 Graph Properties](#42-graph-properties)
- [4.3 Integration with the Production Knowledge Graph](#43-integration-with-the-production-knowledge-graph)

**PART 5: CREATIVE REASONING ENGINE**
- [5.1 Reasoning Architecture](#51-reasoning-architecture)
- [5.2 Reasoning Models for Cinematic Phenomena](#52-reasoning-models-for-cinematic-phenomena)
- [5.3 From Reasoning to Deterministic Output](#53-from-reasoning-to-deterministic-output)

**PART 6: DIRECTOR MEMORY**
- [6.1 Persistent Creative Memory](#61-persistent-creative-memory)
- [6.2 Integration with ATLAS](#62-integration-with-atlas)

**PART 7: DIRECTOR ↔ COMPILER BOUNDARY**
- [7.1 Responsibility Split](#71-responsibility-split)
- [7.2 Traceability Contract](#72-traceability-contract)

**PART 8: CREATIVE DECISION CONFLICT RESOLUTION**
- [8.1 Conflict Classes](#81-conflict-classes)
- [8.2 Resolution Mechanisms](#82-resolution-mechanisms)

**PART 9: CREATIVE PROFILES**
- [9.1 Profile Semantics](#91-profile-semantics)
- [9.2 Profile Catalog](#92-profile-catalog)

**PART 10: HUMAN COLLABORATION**
- [10.1 Human Roles](#101-human-roles)
- [10.2 Collaboration Workflow](#102-collaboration-workflow)

**PART 11: CREATIVE METRICS**
- [11.1 Measurable Creative Quality](#111-measurable-creative-quality)
- [11.2 ORACLE Validation of Creative Metrics](#112-oracle-validation-of-creative-metrics)

**PART 12: THE CREATIVE INTENT RECORD (CIR)**
- [12.1 Purpose](#121-purpose)
- [12.2 Lifecycle](#122-lifecycle)
- [12.3 Schema Philosophy](#123-schema-philosophy)
- [12.4 Identifiers and Versioning](#124-identifiers-and-versioning)
- [12.5 Relationship Map](#125-relationship-map)
- [12.6 Canonical Pipeline](#126-canonical-pipeline)
- [12.7 Why CIR and PKP Are Separate](#127-why-cir-and-pkp-are-separate)

**PART 13: MIGRATION STRATEGY**
- [13.1 Migration Path](#131-migration-path)
- [13.2 Migration Phases](#132-migration-phases)
- [13.3 Backward Compatibility](#133-backward-compatibility)
- [13.4 Risks and Architectural Impacts](#134-risks-and-architectural-impacts)

---

# PART 1: DIRECTOR INTELLIGENCE PHILOSOPHY

---

## 1.1 What Is an AI Film Director

An AI Film Director is the creative authority that decides **what a cinematic work means and how it should feel**, before any frame is rendered. It is not a model, not an agent, and not a compiler pass. It is a **role** — the role GENESIS assumes for every production, as established in `001 — GENESIS 2.0 Migration Specification.md` §3.1 ("GENESIS is the AI Film Director and Production Compiler").

The Director's job is to resolve every creative ambiguity in a synopsis into a complete, internally consistent, validated set of cinematic decisions. Each decision — why this scene exists, why this character feels this, why the camera moves here, why the music is silent here — must be made explicitly, recorded with provenance, and frozen before compilation begins.

The Director does not write pixels, frames, or waveforms. It writes **creative intent**. PROMETHEUS executes that intent. ORACLE verifies the execution against it. ATLAS persists it.

## 1.2 Distinctions from Adjacent Concepts

| Concept | What it is | How the AI Film Director differs |
|---------|-----------|-----------------------------------|
| **LLM** | A language model that predicts the next token given a prompt. Probabilistic, stateless, no native concept of cinematic structure, no provenance, no authority to "decide." | The Director *uses* LLMs as reasoning engines, but the Director is not an LLM. Decisions are constrained by the Directorial Board, the constitution, the ontology, the profile, and human approval. An LLM proposes; the Director adjudicates. |
| **AI Agent** | A goal-directed actor that plans, calls tools, and produces artifacts. Typically single-perspective, optimizing a local objective. | The Director is a **Board of specialized directors** (Part 2), not a single agent. No director optimizes a local objective; each director's output must satisfy the Board's consensus rules and constitutional constraints. The Director's authority is structural, not emergent. |
| **Compiler** | A deterministic transformer from source program to target representation. It executes; it does not invent. | The Director is what runs **before** the compiler. The compiler (Part 4 of `001`) turns creative intent into a PKP. The Director turns a synopsis into creative intent. Compilation is the execution of decisions the Director already made. |
| **Generative pipeline** | An end-to-end model that maps synopsis → media in one pass. Output is emergent, unpredictable, and unrepeatable. | The Director enforces the "compilation over generation" principle (`00` §3.2). Creative decisions are explicit, traceable, and revisable. The output is deterministic given the same intent, profile, and provider versions (`00` §3.6). |

## 1.3 Why Creative Reasoning Must Precede Compilation

The compiler in `001` §4.1 transforms a synopsis into a PKP. But a synopsis is **underspecified** — it carries a premise, not a philosophy. If the compiler were to infer the missing philosophy on its own, every compiler pass would silently make creative choices that no other pass could see, predict, or validate. The result would be:

- **Untraceable drift.** A camera choice in Pass 10 would not know why the lighting in Pass 11 contradicts it.
- **Unrevisable output.** To change one creative decision, the human would have to re-roll the entire pipeline and hope the new roll is consistent.
- **Unvalidatable media.** ORACLE could not compare rendered media against intent, because the intent was never written down.

Creative reasoning precedes compilation so that **every compiler pass receives a fully-resolved creative specification as input**. The compiler never guesses; it only executes.

This generalizes the principle already in force: `00` §3.3 ("Separation of Creative and Technical Authority") and GFS-004 ("Discovery before Decision"). The Director is the layer that performs the discovery and the decision **above** the compiler.

## 1.4 Why Rendering Must Never Invent Creative Ideas

PROMETHEUS is a compiler backend (`001` §2.1). Its contract is: same PKP + same providers → same output. If PROMETHEUS were allowed to invent dialogue, choose a camera angle, or decide that a scene "felt sadder," three things break immediately:

1. **Deterministic replay fails** (`00` §3.6). Two runs with the same PKP would diverge because the renderer exercised creative judgment.
2. **Provenance breaks** (`00` §3.5, GFS-003). A rendered frame could not trace back to a creative decision, because the decision was made inside the renderer and never recorded.
3. **ORACLE validation becomes impossible.** ORACLE compares media to PKP. If the media carries decisions not in the PKP, ORACLE would have to either reject valid output or accept untracked drift.

Rendering is execution. Creative invention belongs to the Director. This is the architectural invariant that makes the entire four-pillar model coherent. It is restated as a hard boundary in Part 7.

## 1.5 Why Creative Intent Must Be Deterministic

"Creative" and "deterministic" are not opposites. A creative decision is creative when it is **chosen**. It is deterministic when the **choice is recorded** so that the same choice can be reproduced, audited, and revised without re-rolling.

Deterministic creative intent means:

- Given the same synopsis, profile, provider versions, and human approvals, the Director produces the same set of creative decisions.
- Each decision carries a confidence level drawn from the existing five-level taxonomy (ADR-004: `explicit / inferred / confirmed / assumed / unknown`).
- Each decision carries provenance: which director proposed it, what evidence supported it, what alternatives were rejected.
- Revision does not re-roll the entire pipeline. It amends the specific decision and recompiles only the affected compiler passes.

This preserves `00` §3.6 ("Deterministic Creative Replay") at the *creative* layer, not only the *rendering* layer. The full deterministic chain is: **synopsis → CIR (deterministic creative decisions) → PKP (deterministic compilation) → media (deterministic rendering)**.

## 1.6 Design Principles

The Director obeys the eight philosophical commitments of `00` §3 and adds six Director-specific principles.

| # | Principle | Statement |
|---|-----------|-----------|
| DI-1 | **Decision before execution** | No compiler pass may invent a creative decision. Every pass consumes a frozen decision from the CIR. |
| DI-2 | **Plurality before unity** | Creative decisions are produced by a Board, not a single mind. Consensus is required before freeze. |
| DI-3 | **Reasoning is auditable** | Every decision records its reasoning chain, alternatives, evidence, and rejected options. The Director's "why" is as canonical as its "what." |
| DI-4 | **Provenance is structural** | Provenance is not logging; it is a structural part of every decision node. A decision without provenance cannot be frozen. (Inherits GFS-003.) |
| DI-5 | **Profile influences, not dictates** | A Creative Profile (Part 9) shapes reasoning priorities and cinematic language. It never directly rewrites a prompt. |
| DI-6 | **Human is the final authority** | The human may approve, amend, override, or lock any decision. The Director proposes; the human disposes. (Inherits `00` §3.8.) |

## 1.7 Architectural Invariants

These invariants cannot be violated without amending this specification.

1. **I-DI-1 — Creative decisions are made before compilation.** The CIR is frozen before any compiler pass runs.
2. **I-DI-2 — The Directorial Board is the only creative authority inside GENESIS.** No other agent, model, or service may produce a creative decision.
3. **I-DI-3 — Every creative decision has a home director.** No decision is orphaned. Every node in the CIR names the director that owns it.
4. **I-DI-4 — Conflict is resolved before freeze.** The Board may not freeze a CIR with unresolved inter-director conflicts.
5. **I-DI-5 — The CIR is the source of truth for creative intent.** The PKP is the source of truth for compiled production knowledge. They are separate (Part 12).
6. **I-DI-6 — PROMETHEUS, ATLAS, and ORACLE never author creative decisions.** They read the CIR/PKP; they do not write creative intent.

## 1.8 Boundaries and Decision Authority

| Boundary | Director Authority | Counterparty Authority |
|----------|-------------------|-------------------------|
| Director ↔ Compiler | Owns all creative decisions; freezes the CIR before compilation. | Compiler passes only execute. They may not invent dialogue, symbolism, emotion, pacing, camera philosophy, music philosophy, or editing philosophy. |
| Director ↔ PROMETHEUS | Owns creative intent; hands off via the PKP. | PROMETHEUS renders. Zero creative authority. |
| Director ↔ ORACLE | Owns the intent that ORACLE validates against. | ORACLE reports drift; does not override. Director reads reports for revision. |
| Director ↔ ATLAS | Owns creative memory contents; reads prior productions. | ATLAS stores and retrieves; never authors. |
| Director ↔ Human | Proposes decisions; accepts human amendments and locks. | Human may approve, amend, override, or lock any decision. |
| Director ↔ Ontology | Consumes GO-001..GO-119 as the vocabulary of decisions. | Ontology defines the terms; the Director uses them. |
| Director ↔ Constitution | Obeys GFS-000..009 and all derived standards. | Constitution governs the Director; the Director does not amend the constitution. |

## 1.9 Human Collaboration Philosophy

The Director is not a replacement for the human. It is a **studio** for the human. The human is the author; the Director is the production team that turns the author's intent into executable craft. Concretely:

- Every Directorial decision is **proposed**, not imposed. The human sees proposals.
- The human may **amend** any proposal at any stage before freeze.
- The human may **lock** a decision so the Board may not revise it.
- The human may **override** any Board consensus. Overrides are recorded with provenance (`human_override`).
- The human may **delegate** entire domains (e.g., "let the Music Director decide all music") or **re-engage** at any time.
- The human may **collaborate** in real time or asynchronously; the Director never blocks on human input unless a configured review gate requires it.

This restates `00` §3.8 ("The Human Is the Final Reviewer") at the Director layer and is operationalized in Part 10.

---

# PART 2: THE DIRECTORIAL BOARD

---

## 2.1 Why a Board, Not a Single Director

A single director would force one perspective to own story, image, sound, performance, psychology, continuity, and quality. That is not how cinema is made and not how the existing repository is structured — `001` §3.1 already states: *"The AI Film Director is distributed. No single agent is 'the director.' The directorial function is distributed across compiler passes."*

This specification formalizes that distribution as a **Directorial Board**: a hierarchical council of specialized directors, each owning a creative domain, each able to propose decisions within that domain, each subject to consensus and conflict-resolution before any decision is frozen. The Board is the institutional form of the Director.

The Board is **not** a set of independent agents. It is one architectural body with internal specialization. Directors communicate through the Creative Decision Graph (Part 4) and the Creative Reasoning Engine (Part 5), not through ad-hoc message passing.

## 2.2 Board Hierarchy

The Board is organized as a hierarchy. Subordinate directors report to a parent director and may not bypass the parent to publish a decision.

```
                        Chief Director
                              │
        ┌────────┬───────────┼────────────┬──────────┬──────────────┐
        ▼        ▼           ▼            ▼          ▼              ▼
   Story       Narrative  Character   Visual      Audio          Editorial
   Director    Director    Director    Director   Director       Director
                                     │   │   │    │   │
                                     ▼   ▼   ▼    ▼   ▼
                              Cinemato- Light-  Produc- Music  Sound
              graphy      ing      tion    Director Director
              Director    Director Designer
                                                        │
                                                        ▼
                                              (continued)
        ┌──────────────────────┬────────────────┬────────────────┐
        ▼                      ▼                ▼                ▼
   Platform              Continuity        Psychology       Quality
   Director              Director         Director          Director
                                            │
                                            ▼
                              (Performance, Dialogue under
                               Character / Psychology as below)
```

Full hierarchy with all member directors:

```
Chief Director
│
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

**Membership invariant (I-DB-1):** The Board always has exactly one Chief Director. Every other director has exactly one parent in the hierarchy. The hierarchy is acyclic.

**Constitutional mapping:** The Board is the institutional realization of the Director role defined in GFS-001 (as expanded by `001` §3.5). The Board does not amend GFS-001; it operationalizes it.

## 2.3 Director Specifications

Each director is specified by the same twelve-field contract: **Mission, Authority, Responsibilities, Inputs, Outputs, Decision Scope, Dependencies, Compiler Pass Ownership, PKP Ownership, Knowledge Graph Dependencies, Constitution Dependencies, Ontology Dependencies.**

The **Compiler Pass Ownership** and **PKP Ownership** fields cross-reference the passes defined in `001` §4.2 and the PKP specifications in `docs/genesis/specifications/pkp/`. The Director does not replace those passes; it owns the creative reasoning that feeds them.

### 2.3.1 Chief Director

| Field | Value |
|-------|-------|
| **Mission** | Hold the unified creative vision. Resolve cross-domain conflicts. Approve the CIR for freeze. |
| **Authority** | Final Board authority on creative disputes; sole authority to freeze the CIR; may veto any director's proposal. |
| **Responsibilities** | Synthesize the production's thesis, tone, and aesthetic stance. Arbitrate conflicts (Part 8). Sign off on profile selection. Approve human override ratification. Trigger re-entry of GENESIS when ORACLE reports drift. |
| **Inputs** | Synopsis, production profile, discovery output, all director proposals, human amendments, ORACLE drift reports (revision-time). |
| **Outputs** | The unified creative vision statement; the ratified CIR; the freeze decision. |
| **Decision Scope** | Cross-domain. Does not own any single creative domain; owns the integration. |
| **Dependencies** | All other directors. |
| **Compiler Pass Ownership** | Pre-compilation (`001` §4.1) and Pass 17 (Production Package Assembly) in the integration sense; does not author pass content. |
| **PKP Ownership** | PKP-00 (Vision Specification), PKP-01 (Creative Strategy). |
| **Knowledge Graph Dependencies** | PKG root node; vision and theme subgraphs. |
| **Constitution Dependencies** | GFS-000, GFS-001 (expanded), GFS-007. |
| **Ontology Dependencies** | GO-001 (Core), GO-116 (Creativity, Innovation & Design Reasoning). |

### 2.3.2 Story Director

| Field | Value |
|-------|-------|
| **Mission** | Decide what the story is: premise, theme, dramatic question, central conflict, beats, symbolic structure. |
| **Authority** | Sole authority over story-level structure. Narrative Director may reshape *how* the story is told; not *what* the story is. |
| **Responsibilities** | Define premise, theme, logline, dramatic question, central conflict, story beats, symbolic/spine structure, resolution posture, motifs. |
| **Inputs** | Synopsis, profile, discovery output (theme, emotion, conflict, audience, gaps). |
| **Outputs** | Story outline node of the CIR. |
| **Decision Scope** | Story structure, thematic spine, beat sequence. Not narrative ordering; not scene detail. |
| **Dependencies** | Chief Director (report to); Discovery (per GFS-004). |
| **Compiler Pass Ownership** | Pass 01 (Story Compiler). |
| **PKP Ownership** | PKP-04 (Story Specification). |
| **Knowledge Graph Dependencies** | Theme, beat, conflict nodes. |
| **Constitution Dependencies** | GFS-002 (Reasoning), GFS-004 (Discovery). |
| **Ontology Dependencies** | GO-101 (Narrative), GO-116 (Creativity). |

### 2.3.3 Narrative Director

| Field | Value |
|-------|-------|
| **Mission** | Decide how the story is told: acts, sequences, emotional curve, conflict curve, reveal timeline, foreshadowing, callbacks. |
| **Authority** | Owns narrative ordering and pacing logic. May not change story beats; may resequence them. |
| **Responsibilities** | Act/sequence structure, emotional arc, conflict arc, reveal schedule, foreshadowing plan, callback plan, scene transitions rationale. |
| **Inputs** | Story outline, profile runtime targets, scene-class distribution. |
| **Outputs** | Narrative structure node of the CIR. |
| **Decision Scope** | Ordering, arcs, reveals, pacing logic. |
| **Dependencies** | Story Director; Chief Director. |
| **Compiler Pass Ownership** | Pass 02 (Narrative Compiler), Pass 03 (Screenplay Compiler — narrative subset). |
| **PKP Ownership** | PKP-09 (Narrative Specification). |
| **Knowledge Graph Dependencies** | Act, sequence, arc, reveal, foreshadow, callback nodes. |
| **Constitution Dependencies** | GFS-002. |
| **Ontology Dependencies** | GO-101 (Narrative), GO-111 (Temporal Experience, Editing & Narrative Rhythm). |

### 2.3.4 Character Director

| Field | Value |
|-------|-------|
| **Mission** | Decide who the characters are: identity, biography, motivations, relationships, growth arcs, visual identity, voice identity. |
| **Authority** | Owns the character bible. Psychology Director owns the *interior*; Character Director owns the *definition*. |
| **Responsibilities** | Per-character biography, motivations, fear, desires, secrets, strengths, weaknesses, growth arc, wardrobe, visual identity, color identity, voice identity, consistency rules, relationship graph. |
| **Inputs** | Story outline, narrative structure, discovery output. |
| **Outputs** | Character bible node of the CIR. |
| **Decision Scope** | Character definition and inter-character relationships. |
| **Dependencies** | Story Director, Narrative Director; coordinates with Psychology, Performance, Dialogue, Visual, Audio directors. |
| **Compiler Pass Ownership** | Pass 09 (Character Compiler). |
| **PKP Ownership** | PKP-06 (Character), PKP-07 (Relationship). |
| **Knowledge Graph Dependencies** | Character, relationship, arc nodes. |
| **Constitution Dependencies** | GFS-002, GFS-003 (provenance for cross-production character reuse via ATLAS). |
| **Ontology Dependencies** | GO-104 (Character), GO-105 (World & Environment — for character-in-world). |

### 2.3.5 Psychology Director

| Field | Value |
|-------|-------|
| **Mission** | Decide the interior life of characters and the psychological realism of the work: emotional triggers, behavioral patterns, cognitive biases, trauma, attachment styles. |
| **Authority** | Owns psychological truth. May veto a Character Director choice that is psychologically incoherent. |
| **Responsibilities** | Per-character psychology, emotional triggers, behavioral patterns, defense mechanisms, cognitive state per scene, psychological realism checks. |
| **Inputs** | Character bible, scene specifications, narrative structure. |
| **Outputs** | Psychology node of the CIR. |
| **Decision Scope** | Interior life, emotional logic, psychological realism. |
| **Dependencies** | Character Director; supervises Performance Director and Dialogue Director. |
| **Compiler Pass Ownership** | Pass 08 (Emotion Compiler). |
| **PKP Ownership** | PKP-08 (Psychology Specification). |
| **Knowledge Graph Dependencies** | Psychology, emotional-state, behavioral-pattern nodes. |
| **Constitution Dependencies** | GFS-002. |
| **Ontology Dependencies** | GO-103 (Human Psychology & Behavior), GO-102 (Audience Experience). |

### 2.3.6 Performance Director

| Field | Value |
|-------|-------|
| **Mission** | Decide how characters *perform*: body language, facial expressions, vocal energy, micro-behaviors, physical subtext per scene. |
| **Authority** | Owns performance direction. Subordinate to Psychology Director for psychological coherence and to Dialogue Director for verbal delivery. |
| **Responsibilities** | Per-scene, per-character performance direction: body language, facial expressions, energy, posture, blocking motivation, micro-expressions at beat boundaries. |
| **Inputs** | Psychology node, dialogue plans, scene specifications. |
| **Outputs** | Performance direction node of the CIR. |
| **Decision Scope** | Physical and vocal performance. |
| **Dependencies** | Psychology Director, Dialogue Director, Character Director. |
| **Compiler Pass Ownership** | Feeds Pass 07 (Dialogue Compiler — delivery subset) and Pass 14 (Voice Compiler — performance subset). |
| **PKP Ownership** | PKP-12 (Audio Intent — performance subset). |
| **Knowledge Graph Dependencies** | Performance, blocking, expression nodes. |
| **Constitution Dependencies** | GFS-002. |
| **Ontology Dependencies** | GO-103, GO-104. |

### 2.3.7 Dialogue Director

| Field | Value |
|-------|-------|
| **Mission** | Decide what characters say and how they say it: dialogue intent, subtext, rhythm, silence, speech patterns, register. |
| **Authority** | Owns verbal content and rhythm. Subordinate to Psychology Director for psychological coherence; coordinates with Performance Director for delivery. |
| **Responsibilities** | Per-scene conversation intent, subtext, silence opportunities, dialogue rhythm, speech patterns, voice direction, actual dialogue lines. |
| **Inputs** | Scene specifications, character bible, psychology node. |
| **Outputs** | Dialogue plan node of the CIR. |
| **Decision Scope** | Verbal content, rhythm, silence, subtext. |
| **Dependencies** | Psychology Director, Character Director, Narrative Director (for scene purpose). |
| **Compiler Pass Ownership** | Pass 07 (Dialogue Compiler). |
| **PKP Ownership** | PKP-12 (Audio Intent — dialogue subset). |
| **Knowledge Graph Dependencies** | Dialogue, line, silence, subtext nodes. |
| **Constitution Dependencies** | GFS-002. |
| **Ontology Dependencies** | GO-108 (Communication, Dialogue & Interaction). |

### 2.3.8 Visual Director

| Field | Value |
|-------|-------|
| **Mission** | Decide the visual language of the work: overall visual philosophy, color language, composition principles, visual metaphors, blocking philosophy. |
| **Authority** | Owns visual integration. Supervises Cinematography, Lighting, and Production Design directors. Resolves conflicts among them. |
| **Responsibilities** | Camera philosophy, composition principles, color language, blocking philosophy, visual metaphors, visual style guide. |
| **Inputs** | Story outline, narrative structure, character bible, profile. |
| **Outputs** | Visual language node of the CIR. |
| **Decision Scope** | Visual philosophy and integration across camera, light, and design. |
| **Dependencies** | Story Director, Narrative Director, Character Director; supervises Cinematography, Lighting, Production Design. |
| **Compiler Pass Ownership** | Pass 04 (Director Compiler — visual subset). |
| **PKP Ownership** | PKP-10 (Directorial Language Specification). |
| **Knowledge Graph Dependencies** | Visual-language, color, metaphor nodes. |
| **Constitution Dependencies** | GFS-002. |
| **Ontology Dependencies** | GO-109 (Visual Expression, Cinematography & Composition). |

### 2.3.9 Cinematography Director

| Field | Value |
|-------|-------|
| **Mission** | Decide the camera: lens, framing, movement, blocking, depth, per shot. |
| **Authority** | Owns camera decisions. Subordinate to Visual Director for visual philosophy; coordinates with Editorial Director for cut rhythm. |
| **Responsibilities** | Per-scene camera language, lens, composition, movement, blocking, depth, shot framing. |
| **Inputs** | Visual language node, scene specifications, shot specifications. |
| **Outputs** | Camera node of the CIR. |
| **Decision Scope** | Camera placement, movement, lens, framing. |
| **Dependencies** | Visual Director, Narrative Director. |
| **Compiler Pass Ownership** | Pass 10 (Camera Compiler). |
| **PKP Ownership** | PKP-10 (Directorial Language — camera subset). |
| **Knowledge Graph Dependencies** | Camera, shot, lens, movement nodes. |
| **Constitution Dependencies** | GFS-002. |
| **Ontology Dependencies** | GO-109. |

### 2.3.10 Lighting Director

| Field | Value |
|-------|-------|
| **Mission** | Decide the light: lighting style, color palette, mood, atmosphere, time of day, textures per scene. |
| **Authority** | Owns lighting. Subordinate to Visual Director. May not contradict Cinematography Director on exposure-critical choices. |
| **Responsibilities** | Per-scene lighting style, palette, mood, atmosphere, time of day, texture. |
| **Inputs** | Visual language node, scene specifications, location/environment specs. |
| **Outputs** | Lighting node of the CIR. |
| **Decision Scope** | Light, palette, mood, atmosphere. |
| **Dependencies** | Visual Director, Production Designer. |
| **Compiler Pass Ownership** | Pass 11 (Lighting Compiler). |
| **PKP Ownership** | PKP-10 (lighting subset) + PKP-11 (Production Design — lighting subset). |
| **Knowledge Graph Dependencies** | Lighting, palette, mood nodes. |
| **Constitution Dependencies** | GFS-002. |
| **Ontology Dependencies** | GO-109. |

### 2.3.11 Production Designer

| Field | Value |
|-------|-------|
| **Mission** | Decide the world's material reality: sets, props, wardrobe, environments, textures, design era, design coherence. |
| **Authority** | Owns production design. Subordinate to Visual Director. Coordinates with Continuity Director for cross-scene consistency. |
| **Responsibilities** | Set design, prop selection, wardrobe design, environment design, texture palette, design era, design coherence rules. |
| **Inputs** | Story outline, character bible, visual language node, world specification (PKP-05). |
| **Outputs** | Production design node of the CIR. |
| **Decision Scope** | Material world: sets, props, wardrobe, environments. |
| **Dependencies** | Visual Director, Character Director. |
| **Compiler Pass Ownership** | Feeds Pass 11 (Lighting — environment subset) and Pass 16 (Prompt Compiler — design subset). |
| **PKP Ownership** | PKP-11 (Production Design Specification). |
| **Knowledge Graph Dependencies** | Set, prop, wardrobe, environment nodes. |
| **Constitution Dependencies** | GFS-002, GFS-003 (for cross-production reuse of design assets via ATLAS). |
| **Ontology Dependencies** | GO-105 (World & Environment). |

### 2.3.12 Audio Director

| Field | Value |
|-------|-------|
| **Mission** | Decide the sonic identity of the work: the relationship among music, sound, voice, and silence. |
| **Authority** | Owns audio integration. Supervises Music Director and Sound Director. Resolves music/sound conflicts. |
| **Responsibilities** | Sonic identity, audio-visual relationship philosophy, mix philosophy, silence policy. |
| **Inputs** | Story outline, narrative structure, emotional specifications. |
| **Outputs** | Audio philosophy node of the CIR. |
| **Decision Scope** | Integration of all sonic domains. |
| **Dependencies** | Chief Director; supervises Music Director, Sound Director; coordinates with Editorial Director. |
| **Compiler Pass Ownership** | Pass 12 (Music Compiler) and Pass 13 (Audio Compiler) in the integration sense. |
| **PKP Ownership** | PKP-12 (Audio Intent Specification) at the integration level. |
| **Knowledge Graph Dependencies** | Audio-philosophy, mix, silence nodes. |
| **Constitution Dependencies** | GFS-002. |
| **Ontology Dependencies** | GO-110 (Audio, Music, Sound Design & Silence). |

### 2.3.13 Music Director

| Field | Value |
|-------|-------|
| **Mission** | Decide the music: theme, instrumentation, tempo, intensity, transitions, silence, emotion per scene, music cues. |
| **Authority** | Owns musical decisions. Subordinate to Audio Director. May not contradict Dialogue Director on silence windows; conflicts go to Audio Director. |
| **Responsibilities** | Music theme, instrumentation, tempo, intensity, per-scene music cues, silence as music. |
| **Inputs** | Scene specifications, emotional specifications, narrative structure, audio philosophy node. |
| **Outputs** | Music node of the CIR. |
| **Decision Scope** | Music content, structure, cueing. |
| **Dependencies** | Audio Director, Psychology Director (for emotional alignment). |
| **Compiler Pass Ownership** | Pass 12 (Music Compiler). |
| **PKP Ownership** | PKP-12 (Audio Intent — music subset). |
| **Knowledge Graph Dependencies** | Music, cue, theme, instrumentation nodes. |
| **Constitution Dependencies** | GFS-002. |
| **Ontology Dependencies** | GO-110. |

### 2.3.14 Sound Director

| Field | Value |
|-------|-------|
| **Mission** | Decide the sound design: SFX, ambient soundscape, audio transitions, silence moments, sound design intent. |
| **Authority** | Owns non-musical sound. Subordinate to Audio Director. |
| **Responsibilities** | Per-scene SFX list, ambient soundscape, audio transitions, explicit silence moments, sound design intent. |
| **Inputs** | Scene specifications, music node, dialogue plans. |
| **Outputs** | Sound design node of the CIR. |
| **Decision Scope** | SFX, ambience, silence, transitions. |
| **Dependencies** | Audio Director, Music Director, Dialogue Director. |
| **Compiler Pass Ownership** | Pass 13 (Audio Compiler). |
| **PKP Ownership** | PKP-12 (Audio Intent — SFX/soundscape subset). |
| **Knowledge Graph Dependencies** | SFX, soundscape, silence nodes. |
| **Constitution Dependencies** | GFS-002. |
| **Ontology Dependencies** | GO-110. |

### 2.3.15 Editorial Director

| Field | Value |
|-------|-------|
| **Mission** | Decide the editing language: cut rhythm, transition philosophy, pacing, montage logic, parallel action, scene transition style. |
| **Authority** | Owns editorial logic. Coordinates with Narrative Director (pacing) and Cinematography Director (cut motivation). |
| **Responsibilities** | Cut rhythm, transition philosophy, pacing curve, montage logic, parallel action, transition style. |
| **Inputs** | Narrative structure, scene specifications, shot specifications, music node. |
| **Outputs** | Editing language node of the CIR. |
| **Decision Scope** | Editing rhythm, transitions, montage. |
| **Dependencies** | Narrative Director, Cinematography Director, Music Director. |
| **Compiler Pass Ownership** | Pass 15 (Timeline Compiler — editorial subset). |
| **PKP Ownership** | PKP-13 (Editing Language Specification). |
| **Knowledge Graph Dependencies** | Cut, transition, pacing nodes. |
| **Constitution Dependencies** | GFS-002. |
| **Ontology Dependencies** | GO-111 (Temporal Experience, Editing & Narrative Rhythm). |

### 2.3.16 Platform Director

| Field | Value |
|-------|-------|
| **Mission** | Decide platform-readiness: aspect ratio, duration envelope, content policy, audience expectations per target platform. |
| **Authority** | Owns platform constraints. May not invent creative content; may constrain it. Conflicts with creative directors escalate to Chief Director. |
| **Responsibilities** | Platform envelope (duration, aspect, codec), content-policy compliance, audience expectations, platform-specific pacing guidance. |
| **Inputs** | Production profile, target platform list. |
| **Outputs** | Platform constraints node of the CIR. |
| **Decision Scope** | Platform envelopes and constraints. |
| **Dependencies** | Chief Director; consumes profile. |
| **Compiler Pass Ownership** | Influences Pass 15 (Timeline Compiler) and Pass 16 (Prompt Compiler — aspect/format subset). |
| **PKP Ownership** | PKP-16 (Distribution Specification). |
| **Knowledge Graph Dependencies** | Platform, constraint, distribution nodes. |
| **Constitution Dependencies** | GFS-007 (Governance — for platform policy). |
| **Ontology Dependencies** | GO-102 (Audience Experience). |

### 2.3.17 Continuity Director

| Field | Value |
|-------|-------|
| **Mission** | Decide cross-scene consistency: blocking, wardrobe, props, lighting continuity, character state continuity, time-of-day continuity, eye-trace continuity. |
| **Authority** | Owns continuity. May veto any director's per-scene choice that breaks cross-scene continuity. |
| **Responsibilities** | Continuity rules across scenes; continuity validation of the CIR before freeze. |
| **Inputs** | All per-scene decisions from all directors. |
| **Outputs** | Continuity node of the CIR; continuity violation list (escalated to Chief Director if unresolved). |
| **Decision Scope** | Cross-scene consistency. |
| **Dependencies** | All other directors. |
| **Compiler Pass Ownership** | Cross-cutting; consumes all passes' outputs to validate continuity. |
| **PKP Ownership** | Cross-cuts all PKP specs; does not own a single PKP. |
| **Knowledge Graph Dependencies** | Continuity-rule, consistency-violation nodes. |
| **Constitution Dependencies** | GFS-006 (Validation — continuity as a validation concern). |
| **Ontology Dependencies** | GO-001 (Core — for identity continuity), GO-104, GO-105. |

### 2.3.18 Quality Director

| Field | Value |
|-------|-------|
| **Mission** | Decide creative quality: enforce creative quality criteria on the CIR before freeze and feed forward to ORACLE. |
| **Authority** | Owns pre-freeze creative quality assessment. May block freeze on quality grounds. Does not override creative content; reports quality. |
| **Responsibilities** | Apply Creative Metrics (Part 11) to the CIR before freeze; produce a pre-freeze quality report; identify low-confidence decisions requiring human review. |
| **Inputs** | The full CIR draft; the production profile; the chosen Creative Profile. |
| **Outputs** | Pre-freeze quality report; recommended human review points. |
| **Decision Scope** | Quality gating; not creative content. |
| **Dependencies** | All other directors; ORACLE (for forward validation contract). |
| **Compiler Pass Ownership** | Pass 18 (Validation Gate) — creative quality subset. |
| **PKP Ownership** | PKP-17 (Quality Specification). |
| **Knowledge Graph Dependencies** | Quality-metric, confidence, review-flag nodes. |
| **Constitution Dependencies** | GFS-006 (Validation). |
| **Ontology Dependencies** | GO-102 (Audience Experience — for engagement metrics). |

## 2.4 Communication, Consensus, and Escalation

### 2.4.1 Communication

Directors do not send ad-hoc messages. All inter-director communication is **structural**: a director publishes a proposed decision to the Creative Decision Graph (Part 4); other directors consume it as an input according to their declared Dependencies. This preserves the auditability invariant (DI-3) and the provenance invariant (DI-4).

Three communication modes are recognized:

| Mode | When | Mechanism |
|------|------|----------|
| **Publish** | A director emits a proposed decision. | A new node is appended to the Creative Decision Graph with provenance. |
| **Consume** | A dependent director reads a published decision. | The dependent director's reasoning references the upstream node by identifier. |
| **Object** | A dependent director finds an upstream decision incoherent with its own domain. | An objection edge is added to the graph, escalating the conflict (Part 8). |

### 2.4.2 Consensus

A decision is **in consensus** when:

1. Its home director has published it.
2. All declared dependent directors have either consumed it without objection or had their objections resolved.
3. The Continuity Director has not raised a continuity violation against it.
4. The Quality Director has not flagged it below the freeze confidence threshold.

Consensus does **not** require unanimity among all directors — only among the declared dependents of the decision. A camera decision does not require the Music Director's assent; it requires the Visual Director's, the Cinematography Director's home acceptance, the Continuity Director's continuity check, and the Quality Director's confidence check.

### 2.4.3 Escalation

A conflict that the home director and objecting dependent director cannot resolve between themselves escalates as follows:

1. **Parent director.** The home director's parent in the hierarchy adjudicates. (e.g., Cinematography ↔ Lighting escalates to Visual Director.)
2. **Chief Director.** If the parent cannot resolve, or if the conflict crosses top-level domains (e.g., Visual vs. Audio), the Chief Director adjudicates.
3. **Human.** If the Chief Director declares the conflict undecidable on creative grounds, or if a human review gate is configured, the conflict is presented to the human (Part 10). The human's decision is recorded as a `human_override` and is final.

Every escalation is recorded as an edge in the Creative Decision Graph with the resolution rationale. This is the decision audit trail required by Part 8.

---

# PART 3: CREATIVE DECISION LIFECYCLE

---

## 3.1 Lifecycle Stages

Every individual creative decision moves through the same lifecycle. The lifecycle is mandatory; no decision may be frozen until it has completed every stage. This operationalizes GFS-004 ("Discovery before Decision") and GFS-002 (the Reasoning Constitution).

```
Idea
  │
  ▼
Research
  │
  ▼
Context Analysis
  │
  ▼
Alternative Exploration
  │
  ▼
Trade-off Analysis
  │
  ▼
Creative Selection
  │
  ▼
Human Review (optional, conditional on Quality Director flag)
  │
  ▼
Creative Intent Record (CIR) entry
  │
  ▼
Compiler Input (the frozen decision feeds its owning compiler pass)
  │
  ▼
PKP Mapping (the compiler pass produces the corresponding PKP artifact)
  │
  ▼
Validation (Quality Director pre-freeze; ORACLE post-render)
  │
  ▼
Freeze
```

| Stage | What happens | Output recorded |
|-------|-------------|-----------------|
| **Idea** | A director proposes a candidate decision in its domain. | `idea` field: the proposed decision in domain terms. |
| **Research** | The director queries ATLAS, prior CIRs, the ontology, the production profile, and the Creative Profile for relevant precedent. | `evidence` field: list of cited sources with identifiers. |
| **Context Analysis** | The director evaluates the idea against the upstream decisions it depends on. | `context` field: upstream decision identifiers and alignment statement. |
| **Alternative Exploration** | The director generates at least two alternatives (the Board requires ≥2 for any non-trivial decision; trivial derivations may declare `single_option` with justification). | `alternatives` field: array of alternatives, each with rationale. |
| **Trade-off Analysis** | The director evaluates the alternatives against the decision's objective, the profile, and the upstream constraints. | `tradeoffs` field: per-alternative trade-off summary. |
| **Creative Selection** | The director selects one alternative. | `selected` field: the chosen alternative. |
| **Human Review (optional)** | If the Quality Director flags low confidence, or the profile mandates review for this decision class, the decision is presented to the human (Part 10). | `review` field: review outcome, reviewer identity, timestamp. |
| **CIR entry** | The decision is written into the CIR with full provenance. | The CIR node (Part 12). |
| **Compiler Input** | The frozen decision is consumed by its owning compiler pass. | The compiler pass reads the CIR node by identifier. |
| **PKP Mapping** | The compiler pass produces the corresponding PKP artifact. | A PKP artifact that references its originating CIR node. |
| **Validation** | Quality Director validates pre-freeze; ORACLE validates post-render. | Validation results attached to the CIR node and PKG. |
| **Freeze** | The decision is immutable. Amendment requires a new revision with new provenance. | `frozen_at` timestamp; `frozen_by` (Chief Director or human). |

## 3.2 Provenance, Confidence, and Rationale

Every CIR node carries:

- **Provenance**: home director, generating model (if any), input sources (CIR node identifiers, ontology IDs, profile fields, ATLAS references).
- **Confidence**: one of the five ADR-004 levels (`explicit / inferred / confirmed / assumed / unknown`). Decisions below `confirmed` for high-stakes domains (story, character psychology, continuity) trigger Human Review.
- **Rationale**: the trade-off analysis that justified the selection, in domain terms.
- **Evidence**: cited upstream decisions, ontology terms, and external references.
- **Alternatives**: the rejected alternatives, each with rejection rationale. Rejected options are first-class records — they enable future revision without re-rolling.
- **Assumptions**: explicit assumptions the decision depends on. If an assumption is later invalidated, the decision is auto-flagged for re-evaluation.

This set is the **decision record**. It is the unit of creative reasoning. It is what makes the Director's reasoning auditable end-to-end.

---

# PART 4: CREATIVE DECISION GRAPH

---

## 4.1 From Decision to Graph

Every creative decision becomes a node in the **Creative Decision Graph (CDG)** — a subgraph of the Production Knowledge Graph (PKG) dedicated to creative reasoning. The CDG is to creative intent what an AST is to source code: a structured, traversable, validating representation of every choice the Director made.

A typical causal chain in the CDG:

```
Theme
  │
  ▼
Character Arc
  │
  ▼
Scene Objective
  │
  ▼
Dialogue Style
  │
  ▼
Performance
  │
  ▼
Lighting
  │
  ▼
Camera
  │
  ▼
Music
  │
  ▼
Editing
  │
  ▼
Rendering (PROMETHEUS, downstream of the PKP)
```

Each arrow is a **dependency edge**: the downstream decision could not have been made without the upstream decision. The graph is not a tree; decisions have multiple parents (a lighting decision depends on mood, location, time-of-day, and character state).

## 4.2 Graph Properties

| Property | Definition |
|----------|-----------|
| **Dependency** | Edge `A → B` means B's reasoning references A as an input. B cannot be frozen before A is frozen. |
| **Causal link** | Edge `A ⇒ B` means A's existence causally motivates B. Causal links are a stronger subset of dependencies, tagged distinctly for explainability queries. |
| **Inheritance** | A child decision may inherit constraints from a parent (e.g., a scene's lighting inherits the production's color language). Inheritance edges are explicit. |
| **Constraints** | A decision may declare constraints it imposes on its dependents (e.g., "this scene is silent" constrains the Music Director to `silence_as_music`). |
| **Priority** | When two decisions could not both be honored, the higher-priority decision wins. Priority is set by the home director's authority level (Part 8). |
| **Confidence** | Each node carries a confidence level (Part 3.2). The graph's minimum-confidence path determines the freeze readiness. |
| **Traceability** | Any node can be traversed to its root (the synopsis) and to its leaves (the PKP artifacts it produced). This is the **explainability backbone**. |
| **Explainability** | For any node, the Director can answer "why?" by traversing its dependency subtree. This is the query interface the Board exposes to humans and to ORACLE. |
| **Conflict detection** | The graph is scanned for incompatible constraints (Part 8) before freeze. A graph with unresolved conflicts cannot be frozen. |

## 4.3 Integration with the Production Knowledge Graph

The CDG is **not** a parallel graph. It is a typed subgraph of the PKG (GFS-003), using the same node identity scheme, the same provenance rules, and the same immutable-revision semantics. Concretely:

- **Node identity**: CDG nodes use the PKG identifier scheme. A CIR node is a PKG node of type `creative_intent`.
- **Provenance**: GFS-003 provenance rules apply unchanged. Every CDG node carries full provenance.
- **Revisions**: Amending a frozen CIR node creates a new immutable revision (per GFS-003); the old revision is retained. This preserves the audit trail.
- **PKP cross-reference**: Every PKP artifact produced by a compiler pass carries a `cir_origin` reference to the CIR node that authorized it. The PKP-to-CDG link is bidirectional.
- **ORACLE cross-reference**: ORACLE drift reports (per `001` §2.1) reference CIR nodes by identifier. A drift report says "the rendered media diverges from CIR node X" — not "the media feels wrong."

This integration is consistent with PKP-18 (Knowledge Graph Specification, as expanded by `001` §3.3) and requires no new graph infrastructure. The CDG is the creative-intent partition of the PKG.

---

# PART 5: CREATIVE REASONING ENGINE

---

## 5.1 Reasoning Architecture

The Creative Reasoning Engine is the substrate the Board uses to produce decisions. It is **not** a single model. It is a set of reasoning modes, each grounded in the existing ontology, that compose into the lifecycle defined in Part 3.

The engine architecture:

```
┌─────────────────────────────────────────────────────────────────┐
│  CREATIVE REASONING ENGINE                                       │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ Idea         │  │ Alternative  │  │ Trade-off             │   │
│  │ Generation   │  │ Exploration  │  │ Evaluation            │   │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘   │
│         │                  │                      │              │
│         └──────────────────┴──────────────────────┘             │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  REASONING MODES (composable)                            │   │
│  │  Emotional · Symbolic · Psychological · Cinematic        │   │
│  │  Audience · Platform                                     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  ONTOLOGY GROUNDING (GO-001..GO-119)                      │   │
│  │  + PROFILE GROUNDING (Creative Profile, Part 9)          │   │
│  │  + CONSTITUTION GROUNDING (GFS-000..009)                  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                            │                                    │
│                            ▼                                    │
│                  Creative Selection (per lifecycle)             │
└─────────────────────────────────────────────────────────────────┘
```

- **Idea Generation** uses LLMs and the ontology to produce candidate decisions in a director's domain. Outputs are filtered by the director's Decision Scope.
- **Alternative Exploration** enforces the ≥2-alternatives rule (Part 3.1). Alternatives are generated by re-running the same reasoning mode with perturbed inputs (different seeds, different profile weights), not by re-rolling the model blindly.
- **Trade-off Evaluation** scores each alternative against the decision's objective and the upstream constraints. Scoring is grounded in the Creative Metrics (Part 11) where applicable.
- **Reasoning Modes** are the perspectives a director may invoke. They are composable: a music decision may invoke Emotional + Cinematic + Audience reasoning simultaneously.

### Reasoning Modes

| Mode | What it reasons about | Ontology grounding |
|------|----------------------|--------------------|
| **Emotional reasoning** | What the audience should feel and why. | GO-102 (Audience Experience), GO-103 (Human Psychology). |
| **Symbolic reasoning** | What objects, images, and sounds *mean* in the work's symbolic system. | GO-116 (Creativity), GO-107 (Knowledge, Information & Revelation). |
| **Psychological reasoning** | What is psychologically true for the characters in the scene. | GO-103. |
| **Cinematic reasoning** | What the camera, light, cut, and sound *do* cinematically (motivation, effect, convention). | GO-109, GO-110, GO-111. |
| **Audience reasoning** | What the target audience expects, needs, and will reject. | GO-102. |
| **Platform reasoning** | What the target platform rewards and forbids. | GO-102, GO-001, the production profile. |

## 5.2 Reasoning Models for Cinematic Phenomena

Each phenomenon below is a reasoning template the Board invokes. These are **not** hardcoded rules; they are ontology-grounded reasoning patterns the appropriate director applies, with the result recorded as a CIR node.

| Phenomenon | Owning Director | Reasoning Model (summary) |
|------------|------------------|----------------------------|
| **Suspense** | Narrative Director | Reveal schedule: information asymmetry between audience and characters; delay payoff; escalate stakes per act. Grounded in GO-107 (Revelation). |
| **Pacing** | Editorial Director + Narrative Director | Curve of emotional intensity over runtime; profile-driven envelope; cut rhythm matches narrative beat weight. GO-111. |
| **Silence** | Audio Director | Silence as music, silence as emotional beat, silence as reveal. Silence is explicit, never assumed (per `001` Pass 13 validation). GO-110. |
| **Emotional transitions** | Psychology Director | Per-scene emotional transition justified by character psychology and narrative purpose; transition shape (cut, dissolve, hold) chosen cinematically. GO-103, GO-111. |
| **Dialogue rhythm** | Dialogue Director | Speech pattern, register, and silence windows per character per scene; rhythm serves subtext. GO-108. |
| **Visual metaphors** | Visual Director | Object/image that carries symbolic weight; metaphor must trace to a Theme node. GO-116. |
| **Callbacks** | Narrative Director | A later scene element that explicitly references an earlier one; callback nodes link to their origin nodes in the CDG. GO-101, GO-107. |
| **Foreshadowing** | Narrative Director | An early-scene element that sets up a later payoff; foreshadow nodes carry `payoff_target` edges. GO-107. |
| **Emotional payoff** | Psychology Director + Narrative Director | A scene that delivers on an earlier setup; payoff nodes link to their foreshadow origins. GO-102. |
| **Scene transitions** | Editorial Director | Transition type (cut, dissolve, match-cut, audio bridge) chosen to serve the emotional transition. GO-111. |
| **Camera motivation** | Cinematography Director | Every camera move has a narratively-justified motivation; unmotivated moves are flagged. GO-109. |
| **Lighting motivation** | Lighting Director | Lighting choices serve scene mood, time-of-day continuity, and character state. GO-109. |
| **Music motivation** | Music Director | Music presence/absence serves emotional beat; music never decorates, it motivates. GO-110. |
| **Editing rhythm** | Editorial Director | Cut frequency and transition style match the scene's energy and the act's pacing curve. GO-111. |

## 5.3 From Reasoning to Deterministic Output

Reasoning becomes deterministic through four mechanisms:

1. **Ontology grounding.** Every decision is expressed in ontology terms. Two reasonings over the same inputs that produce different ontological terms are flagged as a conflict.
2. **Seed-based reproducibility.** Every LLM call in the reasoning engine carries an explicit seed recorded in provenance. The same seed + same inputs → same output (per `001` §3.1, the deterministic-compiler requirement extended to the reasoning layer).
3. **Alternative selection is recorded, not re-rolled.** The selected alternative is frozen in the CIR. Re-running the pipeline does not re-run the selection; it reads the frozen CIR.
4. **Conflict resolution is rule-bound.** Part 8 defines priority, precedence, and arbitration. The human may override, but the override is recorded. There is no "the model decided differently this time" path.

This is the **deterministic creative replay** invariant (DI-5, `00` §3.6) applied at the Director layer.

---

# PART 6: DIRECTOR MEMORY

---

## 6.1 Persistent Creative Memory

The Director maintains persistent creative memory across productions. Memory is partitioned into:

| Memory class | Contents | Owner | Authority to write |
|--------------|----------|-------|---------------------|
| **Accepted ideas** | CIR nodes that reached Freeze. | Each director (its own domain). | The home director. |
| **Rejected ideas** | Alternatives that were not selected. | Each director. | The home director. |
| **Revision history** | Immutable revisions of frozen CIR nodes. | ATLAS (storage); Director (semantics). | The home director, via the revision protocol. |
| **Creative rationale** | The trade-off analyses that justified selections. | Each director. | The home director. |
| **Inspirations** | External references (films, scores, scripts, images) cited during Research. | Any director. | The citing director. |
| **References** | Cross-production reusable assets (character hero images, voice profiles, style presets, music beds). | ATLAS Content Library (`001` §2.1). | ATLAS, on Director request. |
| **Cinematic motifs** | Recurring visual/sonic/narrative motifs across a director's history. | Each director. | The home director. |
| **Recurring themes** | Thematic patterns the director tends to favor. | Story Director, Chief Director. | The home director. |
| **Human overrides** | Every `human_override` record from every production. | Chief Director. | The human, via the override protocol. |
| **Style evolution** | Time-series of how a director's preferences changed. | Each director. | The home director, at checkpoint. |
| **Production history** | The set of CIRs from prior productions. | ATLAS. | The home director, at freeze. |

Memory is **not** free-form text. Every memory entry is a structured record with provenance, linkable from any future CIR node. This preserves the auditability invariant across productions, not only within one.

## 6.2 Integration with ATLAS

Director Memory is persisted by ATLAS (`001` §2.1). The Director never writes to disk; it issues store/retrieve requests to ATLAS. This preserves the four-pillar boundary: ATLAS is the only system that touches durable storage (`001` §2.3, invariant 4).

Concretely:

- The CIR for a production is stored in ATLAS at freeze, with full provenance and versioning.
- Director Memory entries (Part 6.1) are stored in ATLAS as a typed corpus, addressable by director domain, motif, theme, and provenance.
- The Research stage of the lifecycle (Part 3.1) queries ATLAS for relevant memory before generating alternatives.
- Cross-production character reuse (per `001` MA-7) is mediated by ATLAS: the Character Director queries ATLAS for prior character definitions and references them by identifier.
- Deterministic replay registry (`001` MA-8) is maintained by ATLAS; the Director seeds it with `(CIR version, PKP version, provider versions)` tuples at freeze.

This integration is consistent with GFS-003 (provenance mandatory) and requires no new persistence layer beyond ATLAS.

---

# PART 7: DIRECTOR ↔ COMPILER BOUNDARY

---

## 7.1 Responsibility Split

| Concern | Owner | Action |
|---------|-------|--------|
| Decide what the story means | Director | Produces the CIR. |
| Decide how a scene should feel | Director | Produces the CIR. |
| Decide what a character wants | Director | Produces the CIR. |
| Decide camera philosophy | Director | Produces the CIR. |
| Decide music philosophy | Director | Produces the CIR. |
| Decide editing philosophy | Director | Produces the CIR. |
| Compile the CIR into a PKP artifact | Compiler pass | Reads the CIR; writes the PKP. |
| Render the PKP as media | PROMETHEUS | Reads the PKP; writes media. |
| Validate media against the PKP | ORACLE | Reads PKP + media; writes validation. |

### Compiler passes may NEVER invent

Per `001` §4.2, the compiler passes execute. They may not invent:

- **Dialogue** (Pass 07 consumes the Dialogue Director's CIR node).
- **Symbolism** (Pass 04 consumes the Visual Director's CIR node; symbolism is grounded in Theme nodes).
- **Emotion** (Pass 08 consumes the Psychology Director's CIR node).
- **Pacing** (Pass 15 consumes the Editorial Director's CIR node).
- **Camera philosophy** (Pass 10 consumes the Cinematography Director's CIR node).
- **Music philosophy** (Pass 12 consumes the Music Director's CIR node).
- **Editing philosophy** (Pass 15 consumes the Editorial Director's CIR node).

If a compiler pass finds it cannot produce its output without a creative decision that is not in the CIR, the pass **fails loudly** (`00` §3.7) and re-enters the Director at the appropriate director. It does not invent.

## 7.2 Traceability Contract

Two traceability invariants are mandatory:

- **I-TC-1 — Every compiler pass output references its originating CIR node.** Each PKP artifact carries a `cir_origin` field naming the CIR node identifier that authorized it.
- **I-TC-2 — Every PKP artifact references its originating CIR node.** The PKP-level cross-reference is bidirectional: from CIR node, the set of PKP artifacts it authorized is enumerable; from PKP artifact, the authorizing CIR node is directly addressable.

These invariants give ORACLE a single mechanism for drift detection: for any rendered frame, traverse `frame → PKP artifact → cir_origin → CIR node`; compare the rendered content to the CIR node's intent. If they diverge beyond the confidence tolerance, the frame is flagged as drift.

---

# PART 8: CREATIVE DECISION CONFLICT RESOLUTION

---

## 8.1 Conflict Classes

A conflict is an objection edge in the Creative Decision Graph (Part 4) where a dependent director declares an upstream decision incoherent with its own domain. Three classes are recognized:

| Class | Example | Default resolver |
|-------|---------|------------------|
| **Intra-domain** | Cinematography Director wants a wide shot; Lighting Director says the wide shot cannot be lit at the chosen time of day. | Parent director (Visual Director). |
| **Cross-domain** | Music Director wants tension music under a scene; Dialogue Director wants the scene played in silence; both cannot hold. | Chief Director. |
| **Profile/Platform vs. Creative** | Visual Director wants dark, moody scenes; Platform Director says the target platform prefers brighter scenes for retention. | Chief Director, with profile precedence considered. |

## 8.2 Resolution Mechanisms

Conflicts are resolved through a layered mechanism. Each layer is tried in order; only when a layer fails to resolve does the next engage.

### 8.2.1 Priority Hierarchy

When two decisions cannot both hold, the higher-priority decision wins. Priority is determined by the home director's authority level for the conflict's domain:

1. **Human override** (highest; always wins; recorded).
2. **Chief Director** arbitration.
3. **Parent director** of the conflict's domain.
4. **Home director** of the contested decision.

A lower-priority director may not veto a higher-priority decision. The lower-priority decision is recorded as overridden with rationale.

### 8.2.2 Constitutional Precedence

When a conflict implicates a constitutional rule (e.g., GFS-004 "Discovery before Decision," GFS-003 "provenance mandatory," `00` §3.6 "Deterministic Creative Replay"), the constitutional rule wins regardless of priority. The constitution is above the Chief Director.

### 8.2.3 Weighted Reasoning

For conflicts where no priority is dispositive (e.g., Music vs. Dialogue both at the same authority level), the engine computes a weighted score per alternative, using:

- The Creative Profile's domain weights (Part 9).
- The decision's confidence level (ADR-004).
- The upstream constraint density (more constrained = higher weight, because changing it forces more downstream revision).

The higher-weighted alternative wins. The weights and the score are recorded in the CIR as the resolution rationale.

### 8.2.4 Voting Model

For genuinely balanced cross-domain conflicts with no clear weight winner, the Board uses a weighted vote among the directors whose Decision Scope intersects the conflict. Each director's vote is weighted by its domain authority for the conflict. A supermajority (≥⅔ of weighted votes) resolves the conflict. Ties escalate to the Chief Director.

### 8.2.5 Confidence Scoring

Decisions below `confirmed` confidence in high-stakes domains (story, character psychology, continuity, music philosophy) trigger Human Review (Part 10) before they can be used to resolve a conflict. A low-confidence decision may not override a high-confidence one.

### 8.2.6 Human Override

The human may override any resolution at any stage. Overrides are recorded as `human_override` edges in the CDG with the human's identity, timestamp, and stated rationale. Overrides are immutable once recorded.

### 8.2.7 Arbitration

When the Chief Director declares a conflict undecidable on creative grounds, or when the production's review policy requires it, the conflict enters **arbitration**: it is presented to the human (Part 10) with all alternatives, trade-offs, and the Board's recommendation. The human's arbitration decision is final and recorded.

### 8.2.8 Decision Audit Trail

Every conflict, every resolution mechanism tried, every weight, every vote, and every override is recorded in the CDG. The audit trail answers, for any frozen decision: "what conflicts touched this, how were they resolved, by whom, on what evidence?" This is the **explainability requirement** (Part 4.2) applied to conflict resolution.

---

# PART 9: CREATIVE PROFILES

---

## 9.1 Profile Semantics

A **Creative Profile** is a named reasoning posture that modifies how the Board reasons, what it prioritizes, and what cinematic language it favors. Profiles are **not** prompts. They **do not** directly modify any prompt sent to any model.

A Profile influences decisions by:

- Setting **domain weights** used in conflict resolution (Part 8.2.3).
- Setting **reasoning priorities** (e.g., Psychological Cinema prioritizes Psychology Director in cross-domain conflicts).
- Setting **cinematic language defaults** (e.g., Anime favors specific composition conventions, specific pacing curves, specific color-language defaults).
- Setting **pacing envelopes** (per-profile min/max act length, beat density).
- Setting **dialogue register defaults** (e.g., Devotional favors formal register; YouTube Premium favors direct address).
- Setting **visual language defaults** (e.g., Hollywood favors classical coverage; Documentary favors observational framing).
- Setting **music and editing defaults** (e.g., Commercial favors tight cuts and tempo-matched music; Devotional favors sustained tones and long holds).

Profiles modify **decisions**, not **prompts**. A profile never rewrites a model prompt; it shapes the reasoning that produces a CIR node, which the compiler pass then consumes.

This distinction is an architectural invariant (DI-5): the prompt is the compiler's instrument; the decision is the Director's instrument. Profiles operate at the Director layer.

## 9.2 Profile Catalog

The following profiles are recognized at specification level. New profiles may be added under the governance framework (GFS-007) without amending this document.

| Profile | Reasoning posture | Priority directors | Cinematic language | Pacing | Dialogue | Visual | Music | Editing |
|---------|------------------|--------------------|--------------------|---------|----------|--------|-------|---------|
| **Hollywood** | Classical narrative; broad audience clarity. | Story, Narrative, Visual. | Classical coverage, three-act structure, motivated camera. | Steady, escalating. | Clear, expository-when-needed. | Motivated, invisible cuts. | Thematic, leitmotif. | Invisible, continuity-driven. |
| **Psychological Cinema** | Interiority over plot. | Psychology, Performance, Dialogue. | Close, observational, slow build. | Slow, deliberate. | Subtext-heavy, sparse. | Intimate, held. | Diegetic-preferred, silence as music. | Long holds, deliberate cuts. |
| **Pixar** | Emotional clarity for all-ages audience. | Story, Psychology, Visual. | Clear staging, readable emotion, character-driven camera. | Brisk, act-bound. | Distinct voice per character. | Bright, readable. | Thematic, melodic. | Rhythmic, joke-aware. |
| **Anime** | Stylized emotion and image. | Visual, Psychology, Music. | Stylized composition, held frames, color-as-emotion. | Variable, beat-driven. | Stylized, register-flexible. | Stylized, color-bold. | Thematic, leitmotif, silence-as-beat. | Rhythmic, frame-held. |
| **Documentary** | Verisimilitude and witness. | Story, Continuity, Platform. | Observational, available light, motivated by subject. | Subject-driven. | Subject speech primary. | Naturalistic. | Sparse, diegetic. | Minimal, observational. |
| **Devotional** | Reverence and contemplation. | Psychology, Music, Visual. | Symmetric, held, liturgical. | Slow, sustained. | Formal, scriptural-when-relevant. | Reverent, soft. | Sustained, choral-preferred. | Long holds. |
| **Educational** | Clarity and retention. | Story, Narrative, Platform. | Clean staging, motivated by content. | Brisk, segmented. | Direct, explanatory. | Clear, illustrative. | Light, non-distracting. | Crisp, segment-bound. |
| **Historical** | Period fidelity and witness. | Story, Continuity, Visual. | Period-accurate composition, motivated blocking. | Measured. | Period register. | Period-accurate. | Period or period-evocative. | Continuity-driven. |
| **Kids** | Safety, clarity, engagement. | Story, Psychology, Visual. | Bright, readable, character-driven. | Brisk. | Simple, warm. | Bright, high-contrast. | Melodic, energetic. | Rhythmic, fast. |
| **Commercial** | Brand message and retention. | Platform, Visual, Music. | Brand-aligned composition, product-positive. | Tight. | On-message, concise. | Polished, brand-aligned. | Tempo-matched, brand-aware. | Tight, beat-matched. |
| **YouTube Premium** | Direct address and retention. | Platform, Narrative, Performance. | Direct-address framings, retention-aware cuts. | Variable, retention-driven. | Direct, conversational. | Web-native, bright. | Light, retention-aware. | Retention-driven. |

**Profile selection** is a Chief Director decision, informed by the synopsis, the production profile (`config/production_profiles.yaml`), and human input. The selected Creative Profile is recorded in the CIR root node and is immutable for that production's CIR (a production may not switch profiles mid-CIR; a profile switch starts a new CIR revision tree).

---

# PART 10: HUMAN COLLABORATION

---

## 10.1 Human Roles

| Role | Authority | Default scope |
|------|-----------|---------------|
| **Director (human)** | Creative co-author. May propose, amend, override, or lock any CIR node. | All domains. |
| **Producer** | Production authority. May set profile, runtime envelope, platform targets, and approve freezes. May not author creative content. | Profile, envelope, freeze approval. |
| **Reviewer** | Quality authority. May accept, reject, or request revision of any CIR node via the review workflow. May not author creative content. | Review and gating. |
| **Creative Partner** | Domain co-author. May propose and amend within a delegated domain (e.g., "Music Partner"). | Delegated domain only. |
| **Client** | Commissioning authority. May approve or reject at milestone gates; may set brief constraints. | Milestone gates and brief. |
| **Studio** | Institutional authority. May set policy constraints (content policy, brand guidelines, platform compliance) that the Board must honor as constitutional-equivalent for the production. | Policy constraints. |

### 10.2 Collaboration Workflow

The collaboration workflow is the human-facing surface of the lifecycle in Part 3. It is composed of six operations, each with explicit semantics and provenance.

| Operation | Semantics | Provenance recorded |
|-----------|-----------|---------------------|
| **Approval** | The human accepts a Director proposal. The proposal proceeds to the next lifecycle stage. | `approved_by`, `approved_at`, `approver_role`. |
| **Revision** | The human requests changes to a Director proposal. The Director re-enters the lifecycle at the affected stage. The original proposal is retained as a rejected alternative. | `revision_requested_by`, `revision_notes`, `revised_from`. |
| **Amendment** | The human directly edits a CIR node's content. The Director's original content is retained as a prior revision (GFS-003 immutable revisions). | `amended_by`, `amendment_diff`, `amended_from`. |
| **Override** | The human overrides a Board consensus or resolution. The override is final for that decision. | `override_by`, `override_of`, `override_rationale`. |
| **Decision locking** | The human locks a CIR node so the Board may not revise it without an explicit human unlock. Locks survive revision cycles. | `locked_by`, `locked_at`, `locked_until`. |
| **Collaborative editing** | The human and a Director co-edit a CIR node in a shared session. Each edit is attributed. | Per-edit `edited_by`, `edited_at`. |

The review workflow is gated by the Quality Director (Part 2.3.18): decisions flagged below the freeze confidence threshold, or in high-stakes domains, or in productions whose review policy requires it, enter Human Review before freeze. The review is presented with the decision's full lifecycle record (Part 3.2): provenance, confidence, rationale, evidence, alternatives, rejected options, assumptions.

The human may at any time:

- **Delegate** a domain to the Board ("let the Music Director decide all music") — the Board operates autonomously in that domain until the human re-engages.
- **Re-engage** a delegated domain — subsequent decisions in that domain require human review until the human delegates again.
- **Re-enter GENESIS** after ORACLE reports drift — the human amends the affected CIR nodes, and only the affected compiler passes re-run (per `001` §3.1, "GENESIS may be re-entered").

---

# PART 11: CREATIVE METRICS

---

## 11.1 Measurable Creative Quality

Creative quality is measurable. The metrics below are defined at the CIR layer (assessable pre-freeze) and re-assessed at the media layer by ORACLE (post-render). Each metric carries a target value or range, a measurement method, and an owning director.

| Metric | Target | Pre-freeze measurement (Quality Director) | Post-render validation (ORACLE) | Owning director |
|--------|--------|--------------------------------------------|-----------------------------------|------------------|
| **Emotional effectiveness** | The audience's emotional trajectory matches the intended arc. | Trajectory of Psychology Director's per-scene emotional targets plotted against the Narrative Director's emotional curve. | Detected emotion per scene (audio-visual model) compared to the CIR trajectory. | Psychology Director. |
| **Narrative coherence** | All scenes serve the central dramatic question. | Every scene's narrative purpose references the dramatic question (Story Director's CIR node). | Scene-level summary (model) checked against the CIR purpose. | Story Director, Narrative Director. |
| **Character depth** | Each major character has coherent interiority across the work. | Psychology Director's bible checked for cross-scene psychological consistency by the Continuity Director. | Character consistency across scenes (CLIP-extended per `001` §2.1). | Character Director, Psychology Director. |
| **Psychological realism** | Character behavior is plausible given established psychology. | Per-scene behavior cross-checked against the character's bible. | Behavior plausibility (model) given the CIR bible. | Psychology Director. |
| **Dialogue quality** | Dialogue serves subtext and rhythm; no exposition dumps. | Dialogue Director's rhythm and subtext checks; silence policy honored. | Dialogue quality (model) plus silence detection. | Dialogue Director. |
| **Pacing** | Runtime envelope honored; emotional intensity curve matches plan. | Editorial Director's pacing curve within Platform Director's envelope. | Pacing measured from the rendered cut compared to the CIR curve. | Editorial Director, Platform Director. |
| **Symbolism** | Each visual metaphor traces to a Theme node. | Visual Director's metaphor-to-theme traceability in the CDG. | Detected metaphors (model) compared to the CIR metaphor list. | Visual Director. |
| **Audience engagement** | Predicted retention within profile envelope. | Audience reasoning predictions per scene (Audience mode). | Retention prediction (model) per scene. | Narrative Director, Platform Director. |
| **Replay value** | The work rewards re-viewing (foreshadowing density, callbacks, layered subtext). | Foreshadow/callback node density in the CDG; subtext density per Dialogue Director. | N/A (pre-freeze metric only). | Narrative Director, Dialogue Director. |
| **Retention prediction** | Per-scene retention probability within the platform envelope. | Audience reasoning + Platform Director's envelope. | Per-scene retention model. | Platform Director. |
| **Continuity** | Cross-scene consistency in blocking, wardrobe, props, lighting, character state. | Continuity Director's pre-freeze continuity validation. | ORACLE Continuity Enforcement (`001` §2.1). | Continuity Director. |
| **Cinematic realism** | The work reads as cinematically coherent within its profile. | Visual + Editorial + Audio directors' coherence checks against profile language defaults. | Cinematic coherence model. | Visual Director, Editorial Director, Audio Director. |
| **Platform readiness** | The work satisfies the platform envelope (duration, aspect, content policy). | Platform Director's envelope check. | Platform-specific validation (per `001` ORACLE Platform Readiness). | Platform Director. |

## 11.2 ORACLE Validation of Creative Metrics

For each metric, ORACLE runs a post-render validation pass that compares the rendered media to the CIR node that authorized the relevant decision. The validation produces:

- A **per-scene score** for each applicable metric.
- A **production-level aggregate** for each metric.
- A **drift report** for any scene whose score falls outside the CIR-stated tolerance.

Drift reports reference CIR nodes by identifier (per the traceability contract, Part 7.2). GENESIS reads the drift reports to drive revision: only the CIR nodes flagged for drift re-enter the lifecycle (Part 3); only the compiler passes owning those nodes re-run. This is the surgical revision loop enabled by the CIR/PKP separation (Part 12.7).

---

# PART 12: THE CREATIVE INTENT RECORD (CIR)

---

## 12.1 Purpose

The **Creative Intent Record (CIR)** is the canonical representation of creative reasoning for a production. It captures **why every creative decision exists** before that decision becomes executable by the compiler.

The CIR is to filmmaking what an **Abstract Syntax Tree (AST)** is to a compiler:

- An AST captures the *structure* of a source program before code generation.
- The CIR captures the *reasoning* of a creative program before compilation.

- The AST is consumed by the compiler's code-generation passes.
- The CIR is consumed by GENESIS's compiler passes (`001` §4.2).

- The AST is validated by the type checker.
- The CIR is validated by the Quality Director pre-freeze and by ORACLE post-render.

- The AST is emitted by the parser.
- The CIR is emitted by the Directorial Board's reasoning (Part 5).

The CIR is **not** the PKP. The PKP is the compiled production knowledge. The CIR is the creative reasoning that authorizes the PKP. This separation is architectural (Part 12.7).

## 12.2 Lifecycle

The CIR is born at the start of GENESIS, grows as the Board publishes decisions, and is frozen by the Chief Director at the end of pre-compilation. The CIR is the input to every compiler pass.

```
Synopsis
   │
   ▼
Directorial Board reasoning (Parts 2–5)
   │
   ▼
Creative Intent Record (CIR) — draft
   │
   ▼
Conflict resolution (Part 8) + Human review (Part 10) + Quality validation (Part 11)
   │
   ▼
Creative Intent Record (CIR) — frozen
   │
   ▼
Compiler passes (001 §4.2) read CIR nodes by identifier
   │
   ▼
Production Knowledge Package (PKP)
   │
   ▼
PROMETHEUS
   │
   ▼
Generated media
   │
   ▼
ORACLE (validates media against CIR + PKP)
   │
   ▼
ATLAS (persists CIR, PKP, media, validation)
```

On revision (ORACLE drift or human amendment), only the affected CIR nodes re-enter the lifecycle (Part 3); the rest of the CIR remains frozen. New immutable revisions are created per GFS-003.

## 12.3 Schema Philosophy

The CIR is governed by these schema principles. (No schema language is specified here; the schema projection is a derived artifact under GFS-009.)

1. **Node-typed.** Every CIR node has a `type` drawn from the ontology (e.g., `theme`, `character_arc`, `scene_objective`, `dialogue_style`, `lighting`, `camera`, `music`, `editing`). Types map to ontology terms (GO-001..GO-119).
2. **Domain-owned.** Every node names its home director (Part 2.3).
3. **Provenance-structural.** Every node carries full provenance (Part 3.2) as a mandatory structural field, not a log.
4. **Revisioned.** Nodes are immutable once frozen; amendments create new revisions with new identifiers and an `amends` edge to the prior revision (GFS-003).
5. **Graph-native.** The CIR is a graph, not a document. Nodes reference each other by identifier. The CIR is a typed subgraph of the PKG (Part 4.3).
6. **Confidence-tagged.** Every node carries a confidence level (ADR-004).
7. **Alternative-preserving.** Rejected alternatives are first-class nodes linked to the selected decision by a `rejected_in_favor_of` edge. They enable revision without re-rolling.
8. **Assumption-explicit.** Every node declares its assumptions. Assumption invalidation auto-flags the node for re-evaluation.
9. **Profile-aware.** The CIR root carries the Creative Profile (Part 9) and the production profile; every node inherits profile context.
10. **Human-overridable.** Every node carries an `override` field that is null by default and populated when a human overrides the Board.

## 12.4 Identifiers and Versioning

- **Node identifier**: `cir:<production-id>:<director-slug>:<node-type>:<ordinal>`, e.g., `cir:ew001:story_director:theme:01`. Identifiers are stable across revisions; revisions add a `@<rev>` suffix.
- **CIR root identifier**: `cir:<production-id>:root`, carrying the production ID, Creative Profile, production profile, and freeze metadata.
- **Versioning**: CIR revisions are immutable per GFS-003. A frozen CIR has a content hash (per `001` §5.5). The hash is the basis for deterministic replay (DI-5, `00` §3.6).

## 12.5 Relationship Map

| Related artifact | Relationship | Direction | Mechanism |
|------------------|-------------|-----------|-----------|
| **Synopsis** | The CIR is derived from the synopsis. | synopsis → CIR | The synopsis is the root input to the Chief Director's vision node. |
| **PKP** | Each PKP artifact references its authorizing CIR node. | CIR → PKP | PKP artifacts carry `cir_origin`. |
| **PKG** | The CIR is a typed subgraph of the PKG. | CIR ⊆ PKG | CIR nodes are PKG nodes of type `creative_intent`. |
| **Compiler passes** | Each compiler pass reads its owning CIR nodes. | CIR → pass | The pass queries the CIR by node identifier. |
| **ATLAS** | The CIR is persisted by ATLAS. | CIR ↔ ATLAS | ATLAS stores and retrieves the CIR; the Director issues the requests. |
| **ORACLE** | ORACLE validates media against CIR intent. | media → ORACLE → CIR | Drift reports reference CIR nodes by identifier. |
| **Ontology** | CIR node types are ontology terms. | CIR ← ontology | Type and relation vocabulary drawn from GO-001..GO-119. |
| **Constitution** | The CIR obeys all constitutions. | CIR ← GFS-000..009 | Provenance, revisions, confidence, governance. |

## 12.6 Canonical Pipeline

The canonical pipeline including the CIR is:

```
Synopsis
   │
   ▼
Directorial Board (Director Intelligence, Creative Reasoning)
   │
   ▼
Creative Intent Record (CIR) — frozen, versioned, hashed
   │
   ▼
GENESIS Compiler Passes (001 §4.2)
   │
   ▼
Production Knowledge Package (PKP) — frozen, versioned, hashed
   │
   ▼
PROMETHEUS (renders the PKP)
   │
   ▼
Generated Media (images, clips, audio, final video)
   │
   ▼
ORACLE (validates media against PKP + CIR)
   │
   ▼
ATLAS (persists CIR, PKP, media, validation, asset references)
   │
   ▼
Revision loop (re-enter GENESIS for affected CIR nodes only)
```

## 12.7 Why CIR and PKP Are Separate Architectural Concepts

The CIR and the PKP are separate because they answer different questions and serve different consumers.

| Question | CIR answers | PKP answers |
|----------|-------------|------------|
| **What is this?** | The reasoning that authorized a creative decision. | The compiled production knowledge that PROMETHEUS executes. |
| **Who reads it?** | Humans (review, override), the Quality Director (pre-freeze), ORACLE (drift detection against intent), future productions (memory). | PROMETHEUS (renders), ORACLE (validates structure), ATLAS (persists). |
| **What does it contain?** | Ideas, alternatives, trade-offs, rationale, assumptions, rejected options, provenance, confidence, profile context. | Story specs, scene specs, shot specs, dialogue plans, camera specs, lighting specs, music specs, audio specs, timeline, prompts. |
| **When is it produced?** | Before compilation. | By compilation. |
| **How does it change?** | By Board reasoning and human amendment; immutable once frozen; revisions per GFS-003. | By compiler passes; immutable once frozen; revisions per `001` §5.6. |
| **What is its consumer contract?** | "Tell me why this decision was made and what else was considered." | "Tell me what to render." |

Keeping them separate yields four architectural properties a unified record could not provide:

1. **Surgical revision.** A drift report names a CIR node. Only that node re-enters the lifecycle. Only the compiler passes owning that node re-run. The rest of the PKP remains frozen. A unified record would force full recompilation on any revision.
2. **Explainability across the lifecycle.** The CIR's alternatives, rejected options, and rationale survive into production memory (Part 6). A PKP-only record would discard the reasoning at compile time, making future revisions start from scratch.
3. **Clean consumer contracts.** PROMETHEUS reads the PKP and only the PKP — it never has to reason about alternatives or rationale. ORACLE reads both, but its drift check is `media ↔ CIR` and its structural check is `media ↔ PKP`, two distinct operations.
4. **Deterministic replay at two layers.** The CIR hash enables creative replay (same synopsis + same profile + same reasoning seeds → same CIR). The PKP hash enables production replay (same CIR + same providers → same PKP → same media). The two replays are independently auditable.

This separation is consistent with `001` §5 (the PKP is the production package) and `00` §3.2 (compilation over generation): the CIR is the **source program**; the PKP is the **compiled binary**.

---

# PART 13: MIGRATION STRATEGY

---

## 13.1 Migration Path

The migration moves the repository from the current compiler-first posture established by `001` to the Director-first posture established by this specification.

```
Current (per 001):
   Synopsis → GENESIS Compiler Passes → PKP → PROMETHEUS → ORACLE → ATLAS

Target (per this specification):
   Synopsis
      ↓
   Directorial Board (Directorial Intelligence, Creative Reasoning)
      ↓
   Creative Intent Record (CIR)
      ↓
   GENESIS Compiler Passes (unchanged from 001 §4.2)
      ↓
   Production Knowledge Package (PKP) (unchanged from 001 §5)
      ↓
   PROMETHEUS
      ↓
   ORACLE
      ↓
   ATLAS
```

The compiler passes, the PKP schema, the PROMETHEUS contract, the ORACLE contract, and the ATLAS contract defined by `001` are **unchanged**. This specification inserts the Director and the CIR **above** the compiler. The compiler passes simply gain a new input: the CIR node identifier that authorizes each pass's creative decisions, referenced via the new `cir_origin` field on each PKP artifact.

## 13.2 Migration Phases

The migration is sequenced to preserve the `001` §7 migration principles: no breakage of the existing compiler contract, no loss of existing artifacts, no rewrite of the constitutional layer.

### Phase D-1 — Directorial Board Scaffolding (no behavior change)

- Define the 18 director specifications (Part 2.3) as documentation in `docs/genesis/agents/orchestrators/` (extending the existing agent catalog).
- Map each director to its owning compiler pass and PKP artifact (Parts 2.3 columns 9–10).
- No runtime change. The compiler passes continue to run as in `001`.

**Exit criteria:** All 18 director specs committed; cross-reference table to `001` §4.2 passes and PKP specs complete; ADR issued recording the Director-first decision.

### Phase D-2 — Creative Decision Graph as a PKG Subgraph

- Add the `creative_intent` node type to the PKG schema (PKP-18, as expanded by `001` §3.3).
- Add the CIR node identifier scheme (Part 12.4) to the PKG identity scheme (`001` §5.5).
- Add dependency, causal, inheritance, constraint, conflict, and override edge types to the PKG relation vocabulary (extending GO-002 Semantic Relationship Catalog).

**Exit criteria:** PKG schema extended; edge vocabulary documented; no existing PKG node invalidated.

### Phase D-3 — CIR Schema and Lifecycle

- Specify the CIR schema projection (Part 12.3) as a derived standard under GFS-009, in JSON Schema and YAML Schema projections in `docs/genesis/schemas/`.
- Implement the lifecycle (Part 3) as a workflow under GWS (extending `docs/genesis/workflows/`).
- Implement the freeze operation as a Chief Director responsibility (no compiler pass may freeze).

**Exit criteria:** CIR schema committed; lifecycle workflow committed; freeze operation exists.

### Phase D-4 — Director Reasoning Layer (fast mode)

- Implement the Creative Reasoning Engine (Part 5) in fast mode: each director produces a single CIR node per owned decision, with at least one alternative recorded, using existing LLM tiered routing (`config/llm_config.yaml`, `llm_factory.py`).
- Wire each compiler pass to read its owning CIR node and stamp its PKP output with `cir_origin` (Part 7.2).
- Preserve the existing fast-mode behavior (`001` §4.2 fast-mode column) as the fast-mode reasoning implementation.

**Exit criteria:** Every compiler pass consumes a CIR node; every PKP artifact carries `cir_origin`; deterministic replay still passes (same inputs → same CIR → same PKP).

### Phase D-5 — Deep Mode and Conflict Resolution

- Implement the deep-mode reasoning (alternatives exploration, trade-off evaluation) using the Genesis/Genesis2 PKP agents (`movie_os/genesis/pkp_agents/`, `movie_os/genesis2/phases/`) as the deep-mode implementations.
- Implement the conflict resolution mechanisms (Part 8) at the Board level.
- Implement the Quality Director's pre-freeze validation (Part 11).

**Exit criteria:** Deep mode produces a CIR with ≥2 alternatives per non-trivial decision; conflict resolution produces auditable resolutions; Quality Director blocks freeze on low-confidence high-stakes decisions.

### Phase D-6 — Human Collaboration and Profiles

- Implement the human collaboration operations (Part 10.2).
- Implement the Creative Profile catalog (Part 9.2) as an extension of `config/production_profiles.yaml`.
- Implement the profile-influences-decisions contract (Part 9.1): profiles modify Director reasoning weights, not model prompts.

**Exit criteria:** All six human operations functional; all 11 profiles implemented as reasoning postures; profile-to-prompt rewrite path **does not exist** (audited).

### Phase D-7 — ORACLE ↔ CIR Integration

- Extend ORACLE drift reports to reference CIR node identifiers (Part 7.2, Part 11.2).
- Implement the surgical revision loop: ORACLE drift names a CIR node; only that node re-enters the lifecycle; only the owning compiler pass re-runs.

**Exit criteria:** Drift reports reference CIR nodes; surgical revision re-runs only affected passes; non-affected PKP artifacts remain frozen.

### Phase D-8 — Director Memory via ATLAS

- Implement Director Memory (Part 6.1) as ATLAS-stored typed records.
- Wire the Research stage of the lifecycle (Part 3.1) to query ATLAS for relevant memory before generating alternatives.

**Exit criteria:** Director Memory persisted by ATLAS; Research stage consumes prior memory; cross-production character reuse mediated by ATLAS.

## 13.3 Backward Compatibility

| Existing artifact | Compatibility | Action |
|-------------------|---------------|--------|
| GFS-000..009 | **Preserved.** This specification extends, does not amend, the constitution. | None. New derived standards (e.g., the CIR schema) are issued under GFS-007/GFS-009. |
| `001` compiler passes | **Preserved.** Each pass gains a CIR input and a `cir_origin` output field. Pass internals unchanged. | Add `cir_origin` to PKP artifacts; passes read CIR by identifier. |
| `001` PKP schema | **Preserved.** Each PKP artifact gains a `cir_origin` reference. | Add `cir_origin` field; no other schema change. |
| `001` PROMETHEUS contract | **Preserved.** PROMETHEUS reads the PKP unchanged. | None. |
| `001` ORACLE contract | **Extended.** ORACLE additionally reads the CIR for drift detection against intent. | ORACLE drift reports reference CIR nodes. |
| `001` ATLAS contract | **Extended.** ATLAS additionally persists the CIR and Director Memory. | ATLAS stores the CIR alongside the PKP. |
| Existing 19 PKP specs | **Preserved.** | None. |
| Existing 28 ontology files | **Preserved.** The CIR uses ontology terms as node types. | None. New terms added only as derived ontology extensions under GFS-009. |
| Existing agent specs | **Preserved.** The 18 directors are documented in `docs/genesis/agents/orchestrators/` and map to existing PKP agents. | None. Existing agents are reclassified as director implementations. |
| `config/production_profiles.yaml` | **Extended.** Creative Profiles (Part 9.2) are added as a profile extension. | Add Creative Profile block; existing fields unchanged. |

## 13.4 Risks and Architectural Impacts

| Risk | Severity | Mitigation |
|------|----------|------------|
| **CIR/PKP conflation.** Implementers may treat the CIR as a PKP superset, collapsing the two layers. | High | The schema projection (Phase D-3) enforces separate node types (`creative_intent` vs PKP artifact types). The `cir_origin` field is the only structural link. Code review enforces the separation. |
| **Director-level non-determinism.** If LLM reasoning is not seed-controlled, the CIR becomes non-deterministic, breaking `00` §3.6. | High | Phase D-4 mandates seed-based reproducibility for every LLM call in the reasoning engine; seeds are recorded in provenance. |
| **Profile-to-prompt leakage.** Implementers may shortcut by having profiles rewrite prompts, violating DI-5. | High | Phase D-6 includes an audit that no profile-to-prompt rewrite path exists. Profiles modify Director reasoning weights only. |
| **Conflict-resolution complexity.** The Board's conflict resolution may produce deadlocks on balanced cross-domain conflicts. | Medium | The escalation ladder (Part 8.2) terminates at the human; arbitration is always available. The voting model (Part 8.2.4) resolves most balanced conflicts before escalation. |
| **Memory growth.** Director Memory may grow unbounded across productions. | Medium | ATLAS manages retention per its own policy; memory entries are typed and addressable, enabling garbage collection by domain and age. |
| **Reasoning latency.** Deep-mode reasoning over every decision may make the Director too slow for fast-mode use. | Medium | Fast mode (Phase D-4) produces single-alternative CIR nodes; deep mode (Phase D-5) is opt-in per decision class. |
| **Existing fast-mode pipelines bypass the CIR.** The backend 6-stage pipeline (`001` §4.2 fast-mode column) may not produce CIR nodes. | Medium | Phase D-4 wires fast mode to produce minimal CIR nodes (one per owned decision, single alternative with `single_option` justification). The compiler contract is preserved. |
| **Ontology extension pressure.** New node types may pressure the ontology. | Low | Extensions are issued under GFS-009; the ontology governance framework (GFS-007) handles this. |

---

## Architectural Rules (Restated)

This specification produced **no implementation code, no Python, no TypeScript, no YAML, no JSON schemas**. It produced a constitutional architecture specification. Every recommendation is grounded in the existing repository:

- The Directorial Board extends the distributed-director concept from `001` §3.1.
- The compiler passes are those defined by `001` §4.2, unchanged.
- The PKP is that defined by `001` §5, extended only by the `cir_origin` field.
- The CIR is a typed subgraph of the PKG (GFS-003, PKP-18).
- The ontology grounding is GO-001..GO-119 (all 28 ontology files preserved).
- The constitution layer (GFS-000..009) is preserved; new derived standards are issued under GFS-007/GFS-009.
- The four-pillar model (`001` §2) is preserved; the Director lives inside GENESIS and never crosses pillar boundaries.
- The Creative Profiles extend `config/production_profiles.yaml`, not replace it.

No parallel architecture is introduced. No existing concept is duplicated. The Director extends existing work; it does not invent beside it.

---

## Cross-References

| Reference | Location | Relevance |
|-----------|----------|-----------|
| Constitutional Architecture | `00 — Cinema Production Engine Vision, Philosophy & Reference Architecture.md` | Supreme authority. This specification derives from it. |
| Migration Blueprint | `001 — GENESIS 2.0 Migration Specification.md` | Defines the compiler, PKP, and four-pillar model this specification extends. |
| Constitutional Charter | `docs/genesis/constitutions/00-ConstitutionCharter.md` (GFS-000) | Supreme constitutional authority. |
| Identity Constitution | `docs/genesis/constitutions/01-identity-constitution.md` (GFS-001) | GENESIS identity (expanded by `001` §3.5). |
| Reasoning Constitution | `docs/genesis/constitutions/002 — Reasoning Constitution.md` (GFS-002) | Reasoning model used by the Board. |
| Knowledge Constitution | `docs/genesis/constitutions/003 – Knowledge Constitution.md` (GFS-003) | PKG as single source of truth; the CIR is a PKG subgraph. |
| Discovery Constitution | `docs/genesis/constitutions/004 Discovery Constitution.md` (GFS-004) | Discovery before decision (Research stage, Part 3.1). |
| Agent Constitution | `docs/genesis/constitutions/005 – Agent Constitution.md` (GFS-005) | Governs Director agents. |
| Validation Constitution | `docs/genesis/constitutions/006 – Validation Constitution.md` (GFS-006) | Governs Quality Director and ORACLE. |
| Governance Constitution | `docs/genesis/constitutions/007 – Governance Constitution.md` (GFS-007) | Governs new derived standards and profiles. |
| Constitutional Ontology Framework | `docs/genesis/constitutions/009 — Constitutional Ontology Framework.md` (GFS-009) | Governs CIR schema projection. |
| Core Ontology | `docs/genesis/ontology/core/001 — Genesis Core Ontology.md` (GO-001) | CIR node type vocabulary. |
| Semantic Relationship Catalog | `docs/genesis/ontology/semantic/002 — Genesis Semantic Relationship Catalog.md` (GO-002) | CIR edge vocabulary. |
| Narrative Ontology | `docs/genesis/ontology/core/101 — Narrative Ontology.md` (GO-101) | Story/Narrative Director grounding. |
| Audience Experience Ontology | `docs/genesis/ontology/experience/102 — Audience Experience Ontology.md` (GO-102) | Audience and Platform reasoning. |
| Human Psychology Ontology | `docs/genesis/ontology/experience/103 — Human Psychology & Behavior Ontology.md` (GO-103) | Psychology, Performance, Dialogue reasoning. |
| Character Ontology | `docs/genesis/ontology/core/104 — Character Ontology.md` (GO-104) | Character Director grounding. |
| World & Environment Ontology | `docs/genesis/ontology/core/105 — World & Environment Ontology.md` (GO-105) | Production Designer grounding. |
| Event, Action & Causality Ontology | `docs/genesis/ontology/semantic/106 — Event, Action & Causality Ontology.md` (GO-106) | Causal link vocabulary in the CDG. |
| Knowledge, Information & Revelation Ontology | `docs/genesis/ontology/semantic/107 — Knowledge, Information & Revelation Ontology.md` (GO-107) | Suspense, foreshadowing, callback reasoning. |
| Communication, Dialogue & Interaction Ontology | `docs/genesis/ontology/semantic/108 Communication, Dialogue & Interaction.md` (GO-108) | Dialogue Director grounding. |
| Visual Expression, Cinematography & Composition Ontology | `docs/genesis/ontology/experience/109 — Visual Expression, Cinematography & Composition Ontology.md` (GO-109) | Visual, Cinematography, Lighting reasoning. |
| Audio, Music, Sound Design & Silence Ontology | `docs/genesis/ontology/experience/110 — Audio, Music, Sound Design & Silence Ontology.md` (GO-110) | Audio, Music, Sound reasoning; silence policy. |
| Temporal Experience, Editing & Narrative Rhythm Ontology | `docs/genesis/ontology/experience/111 — Temporal Experience, Editing & Narrative Rhythm Ontology.md` (GO-111) | Editorial Director and pacing reasoning. |
| Creativity, Innovation & Design Reasoning Ontology | `docs/genesis/ontology/creativity/116 — Creativity, Innovation & Design Reasoning Ontology.md` (GO-116) | Creative Reasoning Engine grounding. |
| Knowledge Pattern Library | `docs/genesis/ontology/foundation/004 — Genesis Knowledge Pattern Library.md` (GO-004) | Reusable knowledge patterns. |
| Reasoning Pattern Library | `docs/genesis/ontology/foundation/005 — Genesis Reasoning Pattern Library.md` (GO-005) | Reusable reasoning patterns. |
| All 19 PKP Specifications | `docs/genesis/specifications/pkp/` | Outputs of the compiler passes the Director authorizes. |
| Production Knowledge Package Specification | `docs/genesis/architecture/008 — Production Knowledge Package Specification.md` | PKP definition (extended by `001` §5). |
| Knowledge Graph Specification | `docs/genesis/specifications/pkp/18 — Knowledge Graph Specification.md` (PKP-18) | PKG schema, of which the CIR is a subgraph. |
| Studio Handoff Specification | `docs/genesis/architecture/007 — Studio Handoff Specification.md` | GENESIS→PROMETHEUS handoff (the PKP boundary). |
| Existing agent specs | `docs/genesis/agents/orchestrators/`, `architects/`, `reviewers/` | Reclassified as Director implementations. |
| ADR-004 (Five Confidence Levels) | `docs/genesis/decisions/` | Confidence taxonomy used by every CIR node. |
| Production profiles | `config/production_profiles.yaml` | Extended by Creative Profiles (Part 9). |

---

**End of Specification.**