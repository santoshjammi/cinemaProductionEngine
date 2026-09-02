# 003 — Creative Intent Specification (CIS) Architecture

**Status:** Constitutional Architecture Specification — Supreme Authority for Human Creative Intent
**Version:** 1.0.0
**Date:** 2026-07-21
**Authority:** Derives from `00 — Cinema Production Engine Vision, Philosophy & Reference Architecture.md` (the Constitutional Architecture). Extends the migration blueprint of `001 — GENESIS 2.0 Migration Specification.md` and the Director Intelligence layer of `002 — Director Intelligence & Creative Reasoning Architecture Specification.md`. This document is the canonical contract between human creativity and GENESIS. It defines the **Creative Intent Specification (CIS)** — the structured input that replaces the traditional "synopsis" as the entry point of every production.
**Precedence:** Below the Constitutional Architecture (§00). Equal in tier to `001` and `002`. Above all domain specifications, ontology extensions, workflow definitions, PKP specifications, and implementation guides. When this document conflicts with an informal synopsis convention, a legacy input format, or an ad-hoc intent capture flow, this document wins unless the conflict is with the Constitutional Architecture itself.
**Scope:** The CIS philosophy, domain architecture, emotional architecture, audience model, creative constraints, presentation profiles, human authoring workflow, validation, the CIS→CIR→PKP relationship, the CIS lifecycle, and the migration from synopsis-based workflows to CIS-based workflows.

---

## Table of Contents

**PART 1: PHILOSOPHY**
- [1.1 Why the Synopsis Is Insufficient](#11-why-the-synopsis-is-insufficient)
- [1.2 Why Creative Intent Is Richer](#12-why-creative-intent-is-richer)
- [1.3 Why Creative Intent Must Be Explicit](#13-why-creative-intent-must-be-explicit)
- [1.4 Why Deterministic Production Requires Structured Intent](#14-why-deterministic-production-requires-structured-intent)
- [1.5 The Human → CIS → GENESIS Relationship](#15-the-human--cis--genesis-relationship)

**PART 2: CIS ARCHITECTURE**
- [2.1 Domain Model](#21-domain-model)
- [2.2 Core Domains](#22-core-domains)
- [2.3 Domain Relationships](#23-domain-relationships)

**PART 3: EMOTIONAL ARCHITECTURE**
- [3.1 Emotion as a First-Class Architectural Concept](#31-emotion-as-a-first-class-architectural-concept)
- [3.2 The Emotional Model](#32-the-emotional-model)
- [3.3 From Emotional Architecture to Director Intelligence](#33-from-emotional-architecture-to-director-intelligence)

**PART 4: AUDIENCE MODEL**
- [4.1 Audience as Architecture](#41-audience-as-architecture)
- [4.2 Audience Dimensions](#42-audience-dimensions)
- [4.3 Adaptation Without Intent Change](#43-adaptation-without-intent-change)

**PART 5: CREATIVE CONSTRAINTS**
- [5.1 Constraints Are Intent](#51-constraints-are-intent)
- [5.2 Constraint Catalog](#52-constraint-catalog)
- [5.3 Constraint Authority and Precedence](#53-constraint-authority-and-precedence)

**PART 6: PRESENTATION PROFILES**
- [6.1 Intent Versus Presentation](#61-intent-versus-presentation)
- [6.2 Presentation Profile Domains](#62-presentation-profile-domains)
- [6.3 Profiles Influence Execution, Not Intent](#63-profiles-influence-execution-not-intent)
- [6.4 Relationship to Creative Profiles](#64-relationship-to-creative-profiles)

**PART 7: HUMAN AUTHORING WORKFLOW**
- [7.1 Authoring Principles](#71-authoring-principles)
- [7.2 Progressive Refinement](#72-progressive-refinement)
- [7.3 Guided Authoring and Templates](#73-guided-authoring-and-templates)
- [7.4 Validation, Review, Approval, Revision](#74-validation-review-approval-revision)

**PART 8: CIS VALIDATION**
- [8.1 Architectural Validation](#81-architectural-validation)
- [8.2 Validation Dimensions](#82-validation-dimensions)
- [8.3 Readiness for GENESIS](#83-readiness-for-genesis)

**PART 9: CIS ↔ CIR ↔ PKP**
- [9.1 The Three-Artifact Chain](#91-the-three-artifact-chain)
- [9.2 Why All Three Artifacts Are Required](#92-why-all-three-artifacts-are-required)
- [9.3 The Ordering Invariant](#93-the-ordering-invariant)

**PART 10: LIFECYCLE**
- [10.1 Lifecycle Stages](#101-lifecycle-stages)
- [10.2 Versioning, Branching, and Reuse](#102-versioning-branching-and-reuse)

**PART 11: MIGRATION STRATEGY**
- [11.1 From Synopsis to CIS](#111-from-synopsis-to-cis)
- [11.2 Migration Principles](#112-migration-principles)
- [11.3 Migration Phases](#113-migration-phases)
- [11.4 Backward Compatibility](#114-backward-compatibility)
- [11.5 Risks and Architectural Impacts](#115-risks-and-architectural-impacts)

---

# PART 1: PHILOSOPHY

---

## 1.1 Why the Synopsis Is Insufficient

The synopsis is the repository's current input contract. The existing example (`synopsis/001-psychology-emotional-withdrawal.md`) is representative: a free-text paragraph describing a premise, plus a small set of optional key-value constraints (`runtime`, `platform`, `grammar`, `narration_voice`). This is the form GENESIS consumes today.

The synopsis is insufficient as the input contract for a deterministic production engine for five compounding reasons.

| # | Insufficiency | Consequence |
|---|---------------|-------------|
| S-1 | **Unstructured.** The synopsis is prose. Its semantics live in the reader's interpretation, not in the document. | Two readings of the same synopsis yield two different productions. The engine cannot determine what the human *meant*, only what the human *wrote*. |
| S-2 | **Incomplete.** A synopsis carries a premise; it does not carry theme, message, emotional journey, audience, constraints, accessibility intent, localization intent, or ending intent unless the human happens to mention them. | Every undocumented dimension is silently filled by the engine, producing untraceable creative decisions. The human cannot tell what was theirs and what was the engine's. |
| S-3 | **Unvalidated.** A synopsis cannot be checked for completeness, consistency, ambiguity, or contradiction because it has no structure to check. | Contradictory intent (e.g., "uplifting ending" and "tragic ending" both implied) reaches the compiler undetected and surfaces as incoherent media. |
| S-4 | **Unversioned.** A synopsis is a file, not a versioned artifact. Revisions are manual overwrites. | Creative intent history is lost. The engine cannot tell what changed, when, or why. Deterministic replay fails because the input is not pinned. |
| S-5 | **Un boundary.** A synopsis mixes what the human wants (intent) with how the engine should realize it (execution hints like `narration_voice: en-US-GuyNeural`). | The intent/execution boundary is blurred. The engine cannot tell which parts are inviolable creative intent and which are presentation preferences it may adapt. |

The synopsis was adequate for a prototype in which the engine inferred most decisions. It is inadequate for an architecture in which the human's creative intent is the supreme input and every downstream decision must trace back to it.

## 1.2 Why Creative Intent Is Richer

Creative intent is richer than a synopsis because it separates **what** the creator wants from **how** the engine realizes it, and makes the *what* explicit across every dimension that affects the finished work.

A synopsis answers one question: *what is the story about?* Creative intent answers a family of questions:

- What is the story about? *(Story Intent)*
- What does it mean? *(Theme, Message)*
- What should the audience feel, and in what order? *(Emotional Journey, Emotion Transition Graph)*
- Who is the audience? *(Audience Model)*
- What must be true of the finished work? *(Ending Intent, Educational/Entertainment Objectives, Reflection Goals)*
- What must not be true? *(Creative Constraints — ethical, historical, brand, platform, religious)*
- In what context will it be received? *(Cultural Context, Language Strategy, Accessibility, Localization)*
- What are the creator's expectations for image, sound, and music? *(Visual, Audio, Music Expectations — as intent, not as execution)*
- What runtime and platform goals apply? *(Runtime Goals, Platform Goals)*
- What narrative constraints does the creator impose? *(Narrative Constraints)*

Each of these is a first-class domain of the CIS (Part 2). A synopsis collapses them into prose; the CIS makes them explicit, named, validated, and versioned.

## 1.3 Why Creative Intent Must Be Explicit

Creative intent must be explicit because every implicit intent becomes a silent engine decision, and silent engine decisions are the precise failure mode the four-pillar architecture was built to eliminate.

The Constitutional Architecture (`00` §3.3) mandates "Separation of Creative and Technical Authority." The Migration Blueprint (`001` §3.1) redefines GENESIS as "the AI Film Director and Production Compiler." The Director Intelligence specification (`002` Part 1) establishes that "creative reasoning always precedes compilation" and that "every creative decision has a home director" (I-DI-3).

These three authorities converge on a single requirement: **the human's creative intent must be written down, in full, before the Director reasons.** If intent is implicit, the Director must invent it; if the Director invents it, the human's authority is lost; if the human's authority is lost, the engine is a generator, not a compiler.

The CIS is the instrument that makes creative intent explicit. It is the human's *written*, *validated*, *versioned* statement of what they want. The Director never guesses at CIS contents; the Director reasons *from* them.

## 1.4 Why Deterministic Production Requires Structured Intent

Deterministic production (`00` §3.6, "Deterministic Creative Replay") requires that the same inputs produce the same outputs. The deterministic chain defined by `002` Part 1.5 is:

```
synopsis → CIR (deterministic creative decisions) → PKP (deterministic compilation) → media (deterministic rendering)
```

This chain is only as deterministic as its first link. If the synopsis is unstructured prose, the first link is non-deterministic: the same prose may be interpreted differently across runs, across models, or across sessions. The CIR cannot be deterministic if its input is ambiguous.

The CIS replaces the synopsis as the first link:

```
CIS → CIR (deterministic creative decisions) → PKP (deterministic compilation) → media (deterministic rendering)
```

Structured intent makes the first link deterministic because:

- A structured CIS has a **defined domain set** (Part 2). The Director reads exactly those domains; nothing is implicit.
- A structured CIS has a **validation gate** (Part 8). Ambiguity, contradiction, and missing intent are detected before the Director runs.
- A structured CIS is **versioned and hashed** (Part 10). The CIR records which CIS version it reasoned from; replay pins the CIS version.
- A structured CIS **separates intent from presentation** (Part 6). The Director reasons from intent; PROMETHEUS executes presentation. Neither crosses the boundary.

Deterministic production therefore begins with deterministic intent. The CIS is the deterministic intent artifact.

## 1.5 The Human → CIS → GENESIS Relationship

The CIS sits between the human and GENESIS and defines their contract.

```
Human Creator
      │
      │ authors (Part 7)
      ▼
Creative Intent Specification (CIS)
      │
      │ validated (Part 8)
      │ approved (Part 7.4)
      ▼
GENESIS (Directorial Board, per 002)
      │
      │ reasons from the CIS
      ▼
Creative Intent Record (CIR, per 002 Part 12)
      │
      ▼
Production Knowledge Package (PKP, per 001 §5)
      │
      ▼
PROMETHEUS → Media → ORACLE → ATLAS
```

The relationship is defined by three invariants:

- **I-HC-1 — The human authors the CIS; the Director does not.** The Director may propose CIS amendments (Part 7.4), but the CIS is the human's artifact. The Director never silently rewrites intent.
- **I-HC-2 — GENESIS consumes only a validated, approved CIS.** GENESIS never reasons from unstructured text, from a draft CIS, or from a CIS with unresolved validation errors. The validation gate (Part 8) is the entry contract.
- **I-HC-3 — The CIS is immutable once GENESIS begins.** After GENESIS starts reasoning, the CIS is pinned to a specific version. Changes to intent require a new CIS version and a deliberate re-entry of GENESIS (`002` Part 10, "re-enter GENESIS for affected CIR nodes only").

This relationship is the architectural expression of `00` §3.8 ("The Human Is the Final Reviewer") at the input boundary: the human decides what to make; the engine decides how to make it.

---

# PART 2: CIS ARCHITECTURE

---

## 2.1 Domain Model

The CIS is a **typed, multi-domain intent document**. It is not a single prose block. It is a structured collection of intent domains, each with a defined purpose, each independently validatable, each traceable into the CIR and PKP.

The CIS is the **source program** of the Cinema Production Engine in the compiler metaphor established by `00` §3.2 and extended by `002` Part 12.7. Its domains are the source language's constructs. The Directorial Board (`002` Part 2) is the parser/front-end that reads the CIS and emits the CIR (the AST). The compiler passes (`001` §4.2) read the CIR and emit the PKP (the compiled binary).

The CIS is **not** a PKP specification. PKP specifications (`docs/genesis/specifications/pkp/00 — Vision Specification.md` through `18 — Knowledge Graph Specification.md`) are the *output* of compilation. CIS domains are the *input*. The two layers are distinct (Part 9).

## 2.2 Core Domains

The CIS contains the following domains. Each domain is mandatory in the sense that the CIS must *address* it; a domain may be addressed by declaring it `unspecified` with a rationale, which is itself an explicit intent statement ("the creator declines to constrain this dimension; the Director may reason freely within the constitution"). Silence and `unspecified` are not the same: silence is ambiguity; `unspecified` is a decision.

| # | Domain | Purpose | Primary consumer in the Directorial Board (per `002` Part 2.3) |
|---|--------|---------|---------------------------------------------------------------|
| D-1 | **Story Intent** | The premise, the dramatic situation, the core narrative impulse. What the story is, in the creator's words. | Story Director. |
| D-2 | **Theme** | What the story is *about* in the thematic sense (e.g., "the cost of intimacy lost to performance anxiety"). The thematic spine. | Story Director, Chief Director. |
| D-3 | **Message** | What the creator wants the audience to take away, if anything. May be `none` (the work is not didactic). Distinguished from theme: theme is what the story is about; message is what the audience should conclude. | Chief Director, Story Director. |
| D-4 | **Emotional Journey** | The macro emotional arc the audience should traverse (from-state, through-states, to-state). The high-level emotional contract. | Psychology Director, Narrative Director. |
| D-5 | **Emotion Transition Graph** | The structured graph of emotional transitions across the work: nodes (emotional states), edges (transitions), weights (intensity), with peaks, valleys, and resolution. Part 3. | Psychology Director, Editorial Director. |
| D-6 | **Audience** | The target audience and its characteristics. Part 4. | Platform Director, Psychology Director. |
| D-7 | **Educational Objectives** | If the work is educational, what the audience should learn. Observable, falsifiable objectives. `none` for non-educational works. | Story Director, Narrative Director. |
| D-8 | **Entertainment Objectives** | What the work should deliver as entertainment (suspense, laughter, awe, catharsis). Ranked. | Narrative Director, Editorial Director. |
| D-9 | **Platform Goals** | The target platform(s) and the goals specific to each (retention, completion, shareability). Distinguished from platform *constraints* (D-22). | Platform Director. |
| D-10 | **Runtime Goals** | The target runtime, the runtime envelope (min/max), and the runtime posture (fixed, flexible, segmented). | Platform Director, Editorial Director. |
| D-11 | **Narrative Constraints** | Structural constraints the creator imposes: act count, POV, non-linear vs. linear, frame story, unreliable narrator, open vs. closed ending. | Narrative Director. |
| D-12 | **Ethical Constraints** | Ethical boundaries the work must respect: depiction of minors, depiction of violence, consent themes, suicide portrayal, etc. Part 5. | Chief Director, Psychology Director. |
| D-13 | **Cultural Context** | The cultural setting and the cultural familiarity assumed of the audience. May inform symbol, idiom, and reference choice. | Story Director, Visual Director. |
| D-14 | **Language Strategy** | The primary language, any secondary languages, the register (formal, colloquial, period), and the language posture (monolingual, multilingual, subtitled cross-language). | Dialogue Director. |
| D-15 | **Accessibility Intent** | Accessibility goals: captioning, audio description, color-blind-safe palette, motion-sensitivity considerations, cognitive load targets. | Platform Director, Visual Director. |
| D-16 | **Localization Intent** | Localization goals: which locales are intended at authoring time, which are deferred, cultural-specific elements that must not be localized. | Platform Director, Dialogue Director. |
| D-17 | **Visual Expectations** | The creator's expectations for the visual dimension, expressed as *intent* (e.g., "intimate, close, low-light") not as execution (not "50mm lens, f/1.4"). Boundaries enforced by Part 6. | Visual Director. |
| D-18 | **Audio Expectations** | The creator's expectations for audio: sonic identity intent, silence intent, soundscape posture. Intent, not execution. | Audio Director. |
| D-19 | **Music Expectations** | The creator's expectations for music: thematic intent, emotional role of music, music presence/absence posture. Intent, not execution. | Music Director. |
| D-20 | **Ending Intent** | What the ending should be: resolved/unresolved, hopeful/bleak/ambiguous, open/closed, emotional target of the final beat. | Story Director, Psychology Director. |
| D-21 | **Reflection Goals** | What the audience should reflect on after the work ends. Distinguished from message: message is what to conclude; reflection is what to sit with. May be `none`. | Chief Director, Psychology Director. |
| D-22 | **Creative Constraints** | Cross-cutting constraints (budget, production limitations, historical accuracy, educational fidelity, religious sensitivity, brand, platform restrictions). Part 5. | All directors (constraint consumers). |
| D-23 | **Presentation Profile** | The presentation preferences (visual style, editing style, music style, voice style, narration style, pacing, color language, camera language). Separated from intent per Part 6. | All directors (as execution influence). |
| D-24 | **Provenance and Authority** | The creator's identity, the authoring context, the declared influences and references, the CIS version, the human approval record. | Chief Director (CIR root). |

### 2.2.1 Domain Notes

- **D-1 Story Intent** is the only domain that retains a prose form (a constrained prose block with a word envelope). It is the seed from which the Story Director reasons. All other domains are structured.
- **D-4 Emotional Journey** and **D-5 Emotion Transition Graph** are related but distinct: D-4 is the macro arc (three to five states); D-5 is the structured graph (nodes, edges, weights). D-5 is detailed in Part 3.
- **D-7 Educational Objectives** and **D-8 Entertainment Objectives** are not mutually exclusive. A work may have both (e.g., an educational documentary that is also entertaining). Each is independent.
- **D-20 Ending Intent** is called out separately from D-11 Narrative Constraints because the ending is the highest-stakes single creative decision and is the most often misinferred from a synopsis. Making it explicit eliminates the most common source of audience dissatisfaction.
- **D-23 Presentation Profile** is structurally part of the CIS but semantically separated (Part 6). It travels with the CIS but is marked as *execution-influencing*, not *intent-defining*.

## 2.3 Domain Relationships

CIS domains are not independent. They reference and constrain each other. The relationships are part of the CIS architecture and are validated (Part 8).

| Relationship | Example | Validation rule |
|--------------|---------|-----------------|
| **Theme ↔ Message** | A theme of "the cost of intimacy lost" may support a message of "performance anxiety is a relationship issue, not an individual flaw." A message of "men should try harder" would conflict with the theme. | The message must be derivable from or compatible with the theme. A contradiction is a validation error. |
| **Emotional Journey ↔ Ending Intent** | An emotional journey ending in "catharsis" requires an ending intent that can produce catharsis. An ending intent of "bleak, unresolved" contradicts a cathartic journey target. | The final emotional state of D-4 must be consistent with D-20. |
| **Emotion Transition Graph ↔ Emotional Journey** | D-5 is the structured refinement of D-4. D-5's peak/valley structure must realize D-4's macro arc. | D-5 must cover all states named in D-4. |
| **Audience ↔ Platform Goals** | A child audience constrains platform goals (e.g., no adult platforms). A platform goal of "YouTube Kids" constrains the audience. | Cross-consistency between D-6 and D-9. |
| **Audience ↔ Accessibility Intent** | A deaf audience requires captioning accessibility intent. A blind audience requires audio description. | D-6 implies accessibility requirements in D-15. |
| **Audience ↔ Language Strategy** | An audience with low proficiency in the primary language implies simpler register in D-14. | Cross-consistency between D-6 and D-14. |
| **Narrative Constraints ↔ Ending Intent** | D-11 "closed ending" is consistent with D-20 "resolved." D-11 "open ending" is consistent with D-20 "ambiguous." Cross-consistency required. | D-11 and D-20 must agree on closure posture. |
| **Cultural Context ↔ Localization Intent** | D-13 cultural context may name elements that D-16 marks as non-localizable. | D-16's non-localizable set must be present in D-13. |
| **Creative Constraints ↔ All** | D-22 constraints are cross-cutting. Any domain that violates a D-22 constraint is invalid. | Every domain is checked against every D-22 constraint. |
| **Presentation Profile ↔ Visual/Audio/Music Expectations** | D-23 presentation preferences must be consistent with D-17/D-18/D-19 expectations. A presentation profile of "fast cuts, bright palette" conflicts with a visual expectation of "contemplative, low-light." | Cross-consistency between D-23 and D-17/D-18/D-19. |
| **Provenance ↔ All** | D-24 provenance applies to every domain: every domain carries the CIS version and the authoring context. | Every domain is stamped with D-24 metadata. |

These relationships are the CIS's internal consistency model. Part 8 defines how they are validated.

---

# PART 3: EMOTIONAL ARCHITECTURE

---

## 3.1 Emotion as a First-Class Architectural Concept

In the synopsis era, emotion was implicit: the engine inferred an emotional arc from the prose. In the CIS era, emotion is a **first-class architectural concept**: the human authors the emotional architecture explicitly, and the Directorial Board's Psychology and Editorial directors reason from it.

This elevation is grounded in the existing ontology: GO-102 (Audience Experience) and GO-103 (Human Psychology & Behavior) already treat emotion as a structured domain, and `002` Part 5.2 already defines reasoning models for emotional transitions, suspense, silence, and payoff. The CIS makes the *input* side of those models structured.

Emotion is architectural because emotion is the primary deliverable of a cinematic work. A film that produces no intended emotion is a failure regardless of its technical quality. The CIS therefore treats the emotional architecture as co-equal with the story intent: D-1 says what happens; D-4 and D-5 say what the audience feels about it.

## 3.2 The Emotional Model

The CIS emotional architecture consists of eight components. Each is an authored input; none are inferred.

| Component | Definition | CIS domain |
|-----------|-----------|------------|
| **Emotional Baseline** | The neutral emotional state from which the work begins. The audience's assumed state at time zero. | D-4 (Journey from-state). |
| **Emotional Peaks** | The highest-intensity emotional states the audience will experience, and their positions in the work (by act or by beat). | D-5 nodes with `peak: true` and intensity ≥ threshold. |
| **Emotional Valleys** | The lowest-intensity emotional states (calm, dread, sadness), and their positions. Valleys are not absence of emotion; they are distinct emotional states. | D-5 nodes with `valley: true`. |
| **Emotional Transitions** | The directed edges between emotional states, each with a transition shape (cut, build, dissolve, collapse) and an intensity delta. | D-5 edges. |
| **Emotional Contrast** | The intended contrast between adjacent emotional states (e.g., joy → despair, tension → relief). Contrast is a directed design choice, not an emergent side effect. | D-5 edges with `contrast: high/medium/low`. |
| **Emotional Resolution** | The emotional state the audience is left in at the end. Distinct from the narrative ending (a narrative may end unresolved while the emotion resolves, and vice versa). | D-4 (Journey to-state) + D-20 (Ending Intent emotional target). |
| **Emotional Memory** | The emotional states the work is designed to leave the audience with after it ends — the affective aftertaste. Distinguished from resolution: resolution is the final state; memory is the persisting state. | D-4 (Journey to-state) + D-21 (Reflection Goals). |
| **Audience Emotional Journey** | The complete trajectory from baseline through peaks and valleys to resolution and memory, considered as a single designed curve. | D-4 + D-5 jointly. |

### 3.2.1 Emotion Transition Graph (D-5) Structure

The Emotion Transition Graph is the structured refinement of the Emotional Journey. Its architecture (not its schema — no schema is specified here):

- **Nodes**: emotional states, each named using GO-102/GO-103 vocabulary (e.g., `tension`, `dread`, `relief`, `grief`, `hope`, `unease`). Each node carries an intensity (normalized) and a position (by act or by beat).
- **Edges**: transitions, each with a shape (build, cut, dissolve, collapse, hold), an intensity delta, and a contrast rating.
- **Peaks and valleys**: nodes flagged as peaks or valleys, validated for coverage (the journey must have at least one peak and at least one valley unless the work is intentionally monotone, which must be declared).
- **Resolution node**: the final node, validated against D-20's emotional target.
- **Memory annotation**: the resolution node carries a `memory` field describing the intended persisting affect.

The graph is authored by the human, not generated. The Director's job is to realize it in the CIR's emotional nodes (`002` Part 2.3.5, Psychology Director) and to validate that the realized narrative and editing produce the authored transitions.

## 3.3 From Emotional Architecture to Director Intelligence

The emotional architecture is consumed by the Directorial Board as follows:

| Director | Consumes | Produces (in the CIR, per `002` Part 12) |
|-----------|----------|------------------------------------------|
| **Psychology Director** | D-4, D-5, D-20, D-21 | Per-scene emotional targets, emotional triggers per character, psychological realism constraints. |
| **Narrative Director** | D-4, D-5 | Act/sequence emotional curve, reveal schedule that serves emotional peaks, foreshadowing that sets up emotional payoffs. |
| **Editorial Director** | D-5 transitions, D-5 contrast | Pacing curve, cut rhythm that realizes transition shapes, transition style that realizes contrast. |
| **Music Director** | D-5 peaks, valleys, resolution | Music cue plan that reinforces peaks, respects valleys, resolves with the resolution node. |
| **Audio Director** | D-5 transitions, D-5 silence | Silence policy: where silence serves a transition or a valley. |
| **Visual Director** | D-4, D-5 | Color language and composition that serve the emotional states (e.g., desaturation for grief, warmth for hope). |
| **Story Director** | D-4, D-20 | Story beats that produce the authored peaks and valleys; ending that realizes D-20. |
| **Chief Director** | D-4, D-20, D-21 | Unified vision that integrates the emotional architecture with theme and message; conflict resolution when a director's proposal diverges from the authored emotion. |

The CIS emotional architecture is therefore not advisory. It is a binding input. A director proposal that would produce an emotion not in D-5 is a conflict (per `002` Part 8) and must be resolved by amendment, override, or escalation — not by silent acceptance.

---

# PART 4: AUDIENCE MODEL

---

## 4.1 Audience as Architecture

The audience is not a downstream concern; it is an input. The Constitutional Architecture (`00` §3.8) makes the human the final reviewer, but the human reviews *on behalf of an audience*. The CIS makes that audience explicit so the Director reasons for a known audience, not an assumed one.

This is grounded in GO-102 (Audience Experience Ontology), which already models audience as a structured domain. The CIS elevates the audience from an ontology concept to an authored input.

## 4.2 Audience Dimensions

The CIS audience model (D-6) is authored across seven dimensions.

| Dimension | Definition | Example values |
|-----------|-----------|----------------|
| **Target audience** | The primary intended audience. Named explicitly. | "Adults who have experienced relationship distance." |
| **Audience maturity** | The emotional/cognitive maturity assumed. Affects what themes may be direct vs. indirect, what may be shown vs. implied. | `adult`, `young-adult`, `youth`, `child`. |
| **Prior knowledge** | What the audience is assumed to know about the subject, setting, or culture. Affects exposition load. | `none`, `familiar`, `expert`. |
| **Cultural familiarity** | The audience's familiarity with the work's cultural context (D-13). Affects idiom, symbol, and reference choice. | `native`, `adjacent`, `foreign`. |
| **Language proficiency** | The audience's proficiency in the primary language (D-14). Affects register complexity and idiom density. | `native`, `fluent`, `intermediate`, `basic`. |
| **Attention expectations** | The audience's expected attention pattern. Affects pacing, segment length, and information density. | `sustained`, `intermittent`, `casual`. |
| **Platform consumption patterns** | How the audience consumes content on the target platform (D-9). Affects hook design, segment boundaries, and retention strategy. | `binge`, `single-session`, `background`, `commute`. |

## 4.3 Adaptation Without Intent Change

The audience model allows GENESIS to **adapt creative decisions without changing creative intent**. This is a critical distinction.

- **Intent** (D-1 through D-21) is what the creator wants. It is inviolable.
- **Adaptation** is how the Director realizes that intent *for* the audience. It is the Director's discretion within constitutional limits.

For example:

- The creator's intent (D-2 Theme): "the cost of intimacy lost to performance anxiety." This does not change with the audience.
- The audience (D-6): "young adults, intermittent attention, YouTube consumption." This shapes *how* the Director realizes the theme: tighter pacing, direct emotional cues, foregrounded conflict. It does not change the theme.

- The creator's intent (D-20 Ending Intent): "ambiguous, hopeful-bleak." This does not change.
- The audience (D-6): "adults, sustained attention, festival screening." This permits a slower build, more subtext, a more ambiguous final image. The ending intent is unchanged.

The separation is enforced by the CIS structure: audience is its own domain (D-6); intent domains do not reference the audience. The Director reads both and adapts realization to the audience *without* rewriting intent. If a realization would require changing intent to serve the audience, that is a conflict (Part 8, validation: "realization requires intent change") and must be escalated to the human, not silently resolved.

This invariant is **I-AD-1**: *Audience shapes realization; it never redefines intent.*

---

# PART 5: CREATIVE CONSTRAINTS

---

## 5.1 Constraints Are Intent

Constraints are conventionally treated as implementation concerns: budget, schedule, platform policy, brand guidelines. The CIS treats constraints as **intent**, not implementation, for a precise architectural reason.

A constraint that lives in implementation can be silently relaxed by the engine when convenient. A constraint that lives in the CIS cannot: it is validated (Part 8), it is versioned (Part 10), it is traceable into the CIR (`002` Part 12.5, `cir_origin`), and it is enforceable by ORACLE post-render (`001` §2.1, drift detection).

Treating constraints as intent means: if the creator says "no depiction of minors in distress," that is not a guideline PROMETHEUS may interpret; it is a constitutional-for-this-production rule the Director must honor, the compiler must compile against, PROMETHEUS must render against, and ORACLE must validate. A violation is drift, not a preference.

This is consistent with `00` §3.3 ("Separation of Creative and Technical Authority") and `002` Part 7 (Director↔Compiler boundary): constraints travel with intent, not with execution.

## 5.2 Constraint Catalog

The CIS constraint domain (D-22) contains the following constraint classes. Each is an authored input.

| Constraint class | Definition | Example |
|------------------|-----------|---------|
| **Budget assumptions** | The production's resource envelope as it affects creative choices (e.g., number of distinct locations, number of speaking characters, original music vs. library music). Expressed as creative assumptions, not as dollar amounts. | "Assume at most 3 distinct locations." |
| **Production limitations** | Technical or resource limitations that affect what may be attempted (e.g., no motion capture, no on-location shooting, limited character consistency budget). | "No complex crowd scenes." |
| **Ethical boundaries** | Ethical lines the work will not cross. Includes depiction of minors, depiction of violence, sexual content, suicide portrayal, self-harm, eating disorders, etc. | "No depiction of self-harm; reference only, off-screen." |
| **Historical accuracy** | If the work is historical, the accuracy standard it must meet. Names the historical period and the fidelity level. | "Period-accurate to 1940s Mumbai; clothing, language, technology." |
| **Educational fidelity** | If the work is educational (D-7), the fidelity standard the educational content must meet. Names the curriculum or standard, if any. | "Aligned to high-school psychology curriculum; no oversimplification of clinical terms." |
| **Religious sensitivity** | Religious sensibilities the work must respect. Names the religions and the sensitivity type (depiction, language, ritual). | "Respectful depiction of Hindu ritual; no mocking tone." |
| **Brand constraints** | Brand guidelines the work must honor, if commissioned by or associated with a brand. Names the brand and the guideline source. | "Brand X: no competitor logos visible; brand colors in set design where natural." |
| **Platform restrictions** | Platform policy constraints the work must satisfy (content policy, duration limits, aspect ratio, monetization eligibility). Distinguished from D-9 Platform Goals: goals are what the creator wants from the platform; restrictions are what the platform requires of the work. | "YouTube: no adult content; under 15 minutes; 16:9." |

## 5.3 Constraint Authority and Precedence

Constraints have precedence when they conflict. The precedence order is constitutional and fixed:

1. **Constitutional authority** (`00`, GFS-000..009). Always supreme.
2. **Ethical boundaries** (D-22 ethical). Above all other constraints and all intent domains. An ethical constraint overrides a creative preference.
3. **Legal and platform restrictions** (D-22 platform). Above creative intent and below ethical.
4. **Brand and religious constraints** (D-22 brand, religious). Above creative intent, below legal/platform.
5. **Historical and educational fidelity** (D-22 historical, educational). Above creative intent for the specific dimensions they govern (e.g., historical accuracy overrides creative preference on period detail), below brand/religious.
6. **Budget and production limitations** (D-22 budget, production). Below all of the above; these are the most flexible.
7. **Creative intent domains** (D-1..D-21). Below all constraints. Intent is what the creator wants; constraints are what the work must satisfy.

Precedence is enforced at validation (Part 8). A CIS in which a creative intent domain violates a higher-precedence constraint is invalid until the conflict is resolved (by amendment, by the human declaring an explicit override with rationale, or by escalation per `002` Part 8.2).

---

# PART 6: PRESENTATION PROFILES

---

## 6.1 Intent Versus Presentation

A recurring failure mode in AI-mediated production is the conflation of *what the creator wants* with *how it should look and sound*. The CIS separates these explicitly.

**Intent** (D-1..D-22) is what the creator wants the work to be and to do. It is inviolable and is the primary input to the Directorial Board's reasoning.

**Presentation** (D-23) is the creator's preferences for how the work should be executed visually, sonically, and rhythmically. It is influential but not binding in the same sense: the Director may depart from a presentation preference if doing so serves the intent better, and must record the departure as a CIR node with rationale.

The separation exists because:

- A presentation preference that is treated as intent prevents the Director from adapting to the audience (Part 4.3), to the constraints (Part 5), or to the discovered reality of the production.
- A presentation preference that is absent forces the Director to invent the entire presentation, which may not match the creator's taste.
- The separation lets the creator express taste without over-constraining execution.

This is the input-side counterpart of `002` Part 9 (Creative Profiles): Creative Profiles shape *Director reasoning*; Presentation Profiles shape *PROMETHEUS execution*. Neither redefines intent.

## 6.2 Presentation Profile Domains

The Presentation Profile (D-23) contains:

| Domain | What it expresses | Example |
|--------|------------------|---------|
| **Visual Style** | The visual presentation posture. | "Intimate, naturalistic, shallow depth." |
| **Editing Style** | The editing presentation posture. | "Slow, contemplative, long holds." |
| **Music Style** | The music presentation posture. | "Dielectric-preferred, sparse, strings-led." |
| **Voice Style** | The voice/narration presentation posture. | "Close-mic, conversational, low register." |
| **Narration Style** | The narration posture (if narration is intended). | "First-person, reflective, past tense." |
| **Pacing** | The pacing presentation posture. | "Slow build, deliberate, no rush." |
| **Color Language** | The color presentation posture. | "Desaturated, warm, earth tones." |
| **Camera Language** | The camera presentation posture. | "Handheld-observational, motivated moves only." |

## 6.3 Profiles Influence Execution, Not Intent

D-23 is structurally part of the CIS but semantically tagged as `execution_influencing`. The tag has three enforcement consequences:

1. **The Director reads D-23 as preference, not as constraint.** A director proposal that departs from D-23 is valid if it serves D-1..D-21 better. The departure is recorded in the CIR with rationale (per `002` Part 3.2, `alternatives` and `rationale`).
2. **PROMETHEUS reads D-23 (via the PKP) as execution guidance.** The PKP carries presentation preferences forward into rendering parameters where applicable (e.g., color grading guidance, cut rhythm guidance). PROMETHEUS may adapt within the preference envelope.
3. **ORACLE validates D-23 as a soft dimension.** A drift report may flag a presentation departure; it is advisory, not blocking, unless the departure also violates an intent domain.

This invariant is **I-PP-1**: *Presentation preferences influence execution; they do not redefine intent.*

## 6.4 Relationship to Creative Profiles

The Cinema Production Engine has two profile concepts, which must not be confused:

| Concept | Lives in | Author | Affects | Bound by |
|---------|----------|--------|---------|----------|
| **Creative Profile** (`002` Part 9) | The CIR (selected at Director reasoning time). | The Chief Director, from the synopsis/CIS and human input. | Director reasoning: weights, priorities, cinematic language defaults. | The CIS intent domains. |
| **Presentation Profile** (this document, D-23) | The CIS (authored at intent time). | The human creator. | PROMETHEUS execution: visual, audio, music, editing presentation. | The CIS intent domains. |

Both profiles are bounded by intent. Neither may rewrite intent. The Creative Profile shapes *how the Director reasons*; the Presentation Profile shapes *how PROMETHEUS executes*. They are complementary and non-overlapping.

---

# PART 7: HUMAN AUTHORING WORKFLOW

---

## 7.1 Authoring Principles

The CIS is authored by the human. The authoring workflow is governed by five principles:

| # | Principle | Statement |
|---|-----------|-----------|
| WA-1 | **Progressive refinement.** The human may begin with a single sentence and refine toward a complete CIS. The CIS is not required to be complete on first authoring; it is required to be complete before GENESIS begins. |
| WA-2 | **Guided authoring.** The engine may guide the human through the domains, propose defaults, and flag gaps. The engine never authors intent; it prompts for it. |
| WA-3 | **Defaults are explicit.** Any default the engine suggests is labeled as a default, recorded as a default, and may be replaced by the human at any time. Silent defaults are prohibited. |
| WA-4 | **Validation is continuous.** The CIS is validated as it is authored. The human sees completeness, consistency, and conflict status in real time, not only at the end. |
| WA-5 | **Approval is the human's.** The CIS enters GENESIS only when the human approves it. Approval is recorded and versioned. |

## 7.2 Progressive Refinement

The CIS is authored in layers, from a seed to a complete specification.

```
Layer 0: Seed
   │   (a sentence, a paragraph, an existing synopsis)
   ▼
Layer 1: Core Intent
   │   (D-1 Story Intent, D-2 Theme, D-4 Emotional Journey, D-20 Ending Intent)
   ▼
Layer 2: Audience and Constraints
   │   (D-6 Audience, D-22 Creative Constraints, D-9 Platform Goals, D-10 Runtime Goals)
   ▼
Layer 3: Emotional and Narrative Detail
   │   (D-5 Emotion Transition Graph, D-11 Narrative Constraints, D-7/D-8 Educational/Entertainment Objectives)
   ▼
Layer 4: Context and Reach
   │   (D-13 Cultural Context, D-14 Language Strategy, D-15 Accessibility, D-16 Localization, D-21 Reflection Goals)
   ▼
Layer 5: Expectations and Presentation
   │   (D-17/D-18/D-19 Visual/Audio/Music Expectations, D-23 Presentation Profile, D-3 Message)
   ▼
Layer 6: Provenance and Approval
   │   (D-24 Provenance and Authority; human approval)
   ▼
Validated, approved CIS → GENESIS
```

Each layer is independently validatable. The human may stop at any layer and resume later. The CIS is incomplete until Layer 6, but partial completion is a valid resting state.

This progressive structure preserves backward compatibility (Part 11): an existing synopsis is a Layer 0 seed; the engine may guide the human through Layers 1–6 to produce a full CIS.

## 7.3 Guided Authoring and Templates

The engine may assist authoring without authoring intent. Assistance is bounded:

| Assistance type | Permitted | Prohibited |
|----------------|-----------|------------|
| **Domain prompting** | "Would you like to specify the Ending Intent?" | Auto-filling the Ending Intent without asking. |
| **Default suggestion** | "A common ending intent for this theme is X. Use it?" — labeled as a default. | Silently adopting a default. |
| **Template population** | Providing a CIS template with fields and helper text. | Pre-filling intent fields with generated content. |
| **Constraint reminder** | "You declared a child audience; this implies an ethical constraint on violence. State it?" | Adding the constraint without the human's confirmation. |
| **Validation feedback** | "Your Emotional Journey ends in catharsis, but your Ending Intent is bleak. These conflict." | Auto-resolving the conflict. |
| **Reference and inspiration** | "You cited influence X; here are its emotional peaks for reference." | Copying the referenced work's intent. |

Templates live in `docs/genesis/templates/` (extending the existing template directory). The CIS template is a new template under the existing naming convention (`001 — Creative Intent Specification Template.md`), authored per the existing template standards (`docs/genesis/standards/003 — Documentation Standards.md`).

Defaults live in a CIS defaults file (not a schema) that names, for each domain, the default the engine suggests when the human declines to specify. Defaults are labeled, recorded, and revocable.

## 7.4 Validation, Review, Approval, Revision

Authoring culminates in a four-step gate:

1. **Validation** (Part 8). The CIS is checked for completeness, consistency, ambiguity, conflict, and missing intent. Validation produces a report. The CIS may not proceed with unresolved `blocking` validation errors.
2. **Review**. The human reviews the validated CIS. The human may amend any domain. Amendments re-trigger validation.
3. **Approval**. The human approves the CIS. Approval is recorded in D-24 with the human's identity, timestamp, and the approved CIS version. Approval is the entry contract for GENESIS (I-HC-2).
4. **Revision** (post-approval). After approval, the CIS is versioned and pinned. Later changes require a new version (Part 10) and a deliberate re-entry of GENESIS. Post-approval revisions are recorded with provenance per GFS-003.

The gate is the human-facing counterpart of the CIR freeze (`002` Part 12.2): the CIS is frozen at approval; the CIR is frozen at Director freeze. Both are immutable after freeze; both revision via GFS-003 immutable revisions.

---

# PART 8: CIS VALIDATION

---

## 8.1 Architectural Validation

CIS validation is **architectural**, not cosmetic. A CIS that passes validation is a contract: GENESIS may reason from it. A CIS that fails validation is not a contract; GENESIS may not reason from it. Validation is therefore the gate that enforces I-HC-2 ("GENESIS consumes only a validated, approved CIS").

Validation is performed by a CIS Validator, which is a pre-GENESIS component. It is not a Director; it is not a compiler pass; it is the gatekeeper that sits between the human and the Directorial Board. It owns no creative authority; it owns only the validation of the input contract.

This placement is consistent with `001` §4.1 (pre-compilation: profile loader, discovery, scene class planner) — the CIS Validator joins the pre-compilation stage as the first pre-compilation step. It is also consistent with `002` Part 3.1 (the lifecycle's Research stage consumes a validated CIS; the Director never consumes an unvalidated one).

## 8.2 Validation Dimensions

Validation covers six dimensions. Each produces findings classified as `blocking`, `warning`, or `advisory`. Blocking findings must be resolved before approval.

| Dimension | What is checked | Finding classes |
|-----------|----------------|-----------------|
| **Completeness** | Every domain (D-1..D-24) is addressed. A domain may be addressed by `unspecified` with rationale; silence is a completeness error. Required sub-fields of each domain are present. | `blocking` for missing required domains; `warning` for `unspecified` without rationale; `advisory` for recommended-but-optional fields. |
| **Consistency** | The cross-domain relationships (Part 2.3) hold. Theme ↔ Message, Emotional Journey ↔ Ending Intent, Audience ↔ Accessibility, Narrative Constraints ↔ Ending Intent, etc. | `blocking` for contradictions; `warning` for loose consistency (e.g., message is derivable from theme but not explicitly compatible). |
| **Ambiguity detection** | D-1 Story Intent is within its word envelope and is not internally ambiguous. D-17/D-18/D-19 expectations are intent-level (not execution-level). D-20 Ending Intent is unambiguous (one of resolved/unresolved, hopeful/bleak/ambiguous). | `blocking` for ambiguous required domains; `warning` for vague optional domains. |
| **Conflict detection** | No domain violates a higher-precedence constraint (Part 5.3). No two intent domains contradict each other in a way that cannot be reconciled by the Director. | `blocking` for precedence violations; `warning` for reconcilable contradictions that the Director must resolve. |
| **Missing intent** | The CIS does not leave a high-stakes dimension (theme, ending, emotional resolution, audience) to silent inference. | `blocking` for missing high-stakes intent; `advisory` for missing low-stakes intent. |
| **Human approval** | D-24 carries a recorded human approval. Approval exists, is timestamped, and names the approver. | `blocking` if approval is absent. |

### 8.2.1 Ambiguity Detection

Ambiguity detection is the dimension most specific to the CIS. It checks that the CIS does not silently delegate creative decisions to the engine. Examples:

- D-1 Story Intent that contains two incompatible premises (e.g., "a love story" and "a story about a man who never loves") is ambiguous.
- D-20 Ending Intent that says "the ending is sad but hopeful" without specifying *how* (resolved or unresolved, hopeful-bleak or hopeful-warm) is ambiguous.
- D-17 Visual Expectations that says "it should look like a Wong Kar-wai film" is ambiguous (which film, which period, which aspect?).
- D-5 Emotion Transition Graph that specifies peaks and valleys but no resolution node is ambiguous.

Ambiguity detection is conservative: when in doubt, flag. The human resolves the flag by amending the CIS, not by the engine inferring.

### 8.2.2 Conflict Detection and Precedence

Conflict detection applies the precedence order (Part 5.3) to the entire CIS. Examples:

- D-20 Ending Intent "explicit depiction of suicide as resolution" vs. D-22 Ethical Constraints "no depiction of self-harm." Ethical wins. Blocking conflict; the human must amend D-20 or D-22.
- D-9 Platform Goals "YouTube Kids" vs. D-6 Audience "adults." Platform restriction wins. Blocking conflict.
- D-17 Visual Expectations "period-accurate 1940s Mumbai" vs. D-22 Historical Accuracy "period-accurate to 1940s Mumbai." Consistent. No conflict.
- D-23 Presentation Profile "fast cuts, bright palette" vs. D-17 Visual Expectations "contemplative, low-light." Warning: the Director must reconcile.

Conflicts that cannot be resolved at validation are escalated to the human. The Director never resolves CIS-level conflicts; that is the human's authority (I-HC-1).

## 8.3 Readiness for GENESIS

A CIS is **ready for GENESIS** when:

1. Validation produces zero `blocking` findings.
2. All `warning` findings are either resolved or explicitly accepted by the human (recorded in D-24).
3. D-24 carries human approval.
4. The CIS is versioned and pinned (Part 10).

Readiness is recorded as a CIS state: `draft → validated → approved → pinned`. GENESIS consumes only `pinned` CIS versions. This state machine is the CIS-side counterpart of the CIR's `draft → frozen` state (`002` Part 12.2).

---

# PART 9: CIS ↔ CIR ↔ PKP

---

## 9.1 The Three-Artifact Chain

The Cinema Production Engine's creative front-end is a three-artifact chain. Each artifact has a distinct author, a distinct purpose, and a distinct consumer.

```
Creative Intent Specification (CIS)
   │
   │ authored by the Human
   │ validated by the CIS Validator
   │ approved by the Human
   │
   ▼
GENESIS Directorial Board (002 Part 2)
   │
   │ reasons from the CIS
   │ produces Creative Intent Records (CIR nodes)
   │
   ▼
Creative Intent Record (CIR)
   │
   │ authored by the Directorial Board
   │ frozen by the Chief Director
   │
   ▼
GENESIS Compiler Passes (001 §4.2)
   │
   │ compile the CIR into the PKP
   │
   ▼
Production Knowledge Package (PKP)
   │
   │ authored by the compiler passes
   │ frozen and hashed
   │
   ▼
PROMETHEUS → Media → ORACLE → ATLAS
```

| Artifact | Author | Content | Consumer | Question it answers |
|----------|--------|---------|----------|---------------------|
| **CIS** | Human (with engine guidance, never engine authorship) | What the creator wants: story, theme, emotion, audience, constraints, ending, presentation preferences. | The Directorial Board. | "What do you want?" |
| **CIR** | The Directorial Board (`002` Part 2.3, the 18 directors) | Why each creative decision exists: ideas, alternatives, trade-offs, rationale, assumptions, provenance. | The compiler passes; ORACLE (for drift detection against intent). | "Why was this decided?" |
| **PKP** | The compiler passes (`001` §4.2) | What to render: story specs, scene specs, shot specs, dialogue plans, camera specs, lighting specs, music specs, timeline, prompts. | PROMETHEUS (renders); ORACLE (validates structure). | "What do I render?" |

## 9.2 Why All Three Artifacts Are Required

A two-artifact chain (CIS → PKP, skipping the CIR) would lose the reasoning. The PKP would carry *what* to render but not *why*. Consequences:

- **No explainability.** The human could not ask "why this camera move?" and get an answer traceable to intent.
- **No surgical revision.** Without CIR nodes, ORACLE drift reports could not name a reasoning node to re-enter; the entire pipeline would re-run on any drift.
- **No alternative preservation.** Rejected alternatives would be lost. Revision would start from scratch instead of from the recorded reasoning.
- **No conflict audit.** Inter-director conflicts (`002` Part 8) would be invisible.

A two-artifact chain (Synopsis → CIR, skipping the CIS) would lose the input structure. Consequences:

- **Non-deterministic input.** The CIR's deterministic replay (`002` Part 1.5) would fail because the input is ambiguous.
- **No input validation.** Ambiguity, contradiction, and missing intent would reach the Director undetected.
- **No human intent authority.** The human's intent would be prose, not a contract; the Director would silently fill gaps.
- **No intent/execution separation.** Presentation would be mixed with intent (the synopsis failure mode, Part 1.1 S-5).

A two-artifact chain (CIS → CIR, skipping the PKP) would lose the executable specification. Consequences:

- **PROMETHEUS would have to reason.** It would read the CIR (reasoning) and invent the executable spec, violating `002` Part 7 (the compiler boundary) and `00` §3.3 (creative/technical separation).
- **No deterministic rendering.** Without a frozen PKP, deterministic replay (`00` §3.6) fails at the rendering layer.

All three artifacts are required. The CIS is the human's contract; the CIR is the Director's reasoning; the PKP is the executable. Removing any one breaks a different invariant.

## 9.3 The Ordering Invariant

The ordering of the three artifacts is not a sequence preference; it is an architectural invariant.

**I-OC-1 — CIS precedes CIR; CIR precedes PKP.** The CIS is authored before the Director reasons; the CIR is frozen before the compiler runs; the PKP is frozen before PROMETHEUS renders. No artifact may be produced out of order.

**I-OC-2 — Each artifact is the authoritative input to the next.** The CIR's authoritative input is the CIS (not a synopsis, not a free-form prompt). The PKP's authoritative input is the CIR (not the CIS directly — the compiler never reads the CIS; it reads the CIR, which the Director produced from the CIS). PROMETHEUS's authoritative input is the PKP (not the CIR; PROMETHEUS never reads reasoning).

**I-OC-3 — The chain is one-directional at production time.** At production time (GENESIS reasoning → compilation → rendering), the chain flows forward only. Re-entry for revision flows backward only through explicit revision protocols (`002` Part 10; this document Part 10), never through silent back-channels.

This ordering is why the specification sequence is `000 → 001 → 002 → 003 → (004 PKP) → (PROMETHEUS) → (ORACLE) → (ATLAS)`. Defining the CIS before the PKP establishes an unambiguous contract for every downstream component. Defining the PKP before the CIS would produce a PKP with no defined input contract — a renderer without a defined consumer. The CIS is the front-end of the creative front-end; it must be defined before the artifacts it authorizes.

---

# PART 10: LIFECYCLE

---

## 10.1 Lifecycle Stages

The CIS has a lifecycle that spans the full production history, not only the authoring moment.

```
Creation
   │
   ▼
Revision (within draft, before approval)
   │
   ▼
Validation
   │
   ▼
Approval
   │
   ▼
Versioning and Pinning
   │
   ▼
Production (GENESIS consumes the pinned version)
   │
   ▼
Reuse (as a template or reference for a new production)
   │
   ▼
Archival (ATLAS persists the CIS with the production)
   │
   ▼
Learning (Director Memory and future authoring consume the archived CIS)
```

| Stage | What happens | Owner | State transition |
|-------|-------------|-------|------------------|
| **Creation** | The human authors the CIS, layer by layer (Part 7.2). | Human. | `none → draft`. |
| **Revision** | The human amends the draft. Amendments within draft are not versioned; the draft is a working state. | Human. | `draft → draft`. |
| **Validation** | The CIS Validator runs (Part 8). | CIS Validator (engine). | `draft → validated` (zero blocking findings) or `draft → draft` (blocking findings remain). |
| **Approval** | The human approves the validated CIS. | Human. | `validated → approved`. |
| **Versioning and Pinning** | The approved CIS is assigned a version and pinned. The pinned version is immutable. | Engine (on human approval). | `approved → pinned`. |
| **Production** | GENESIS consumes the pinned CIS version. | Directorial Board. | `pinned → in-production`. |
| **Reuse** | The CIS (or a derived template) is used as the seed for a new production. Reuse creates a new CIS instance with a `derived_from` reference. | Human. | `pinned → reused` (the original remains `pinned`; the new instance starts at `draft`). |
| **Archival** | ATLAS persists the CIS with the production's CIR, PKP, media, and validation. | ATLAS (`001` §2.1). | `in-production → archived` (after production completes). |
| **Learning** | Director Memory (`002` Part 6) and future authoring assistance consume the archived CIS as precedent. | Directorial Board (memory); human (future authoring). | `archived → referenced` (the CIS remains `archived`; references are read-only). |

## 10.2 Versioning, Branching, and Reuse

### 10.2.1 Versioning

CIS versions follow GFS-003 (immutable revisions). A pinned CIS is immutable; any change produces a new version with a new identifier and an `amends` edge to the prior version.

Version identifiers: `cis:<production-id>:v<ordinal>`, e.g., `cis:ew001:v3`. The ordinal increments on each approved revision. Draft states do not have version ordinals; only pinned versions do.

The CIR records which CIS version it reasoned from (`002` Part 12.4, provenance). This pins the deterministic replay chain: a CIR replay requires the same CIS version.

### 10.2.2 Branching

A CIS may be **branched** to explore alternative creative directions without abandoning the original. A branch is a new CIS instance with a `branched_from` reference to the source version. Branches are independent CIS instances with their own lifecycles.

Use cases:

- The human wants to explore "what if the ending were hopeful instead of bleak?" without losing the original.
- The producer wants to evaluate two audience models for the same story.
- The studio wants a platform-specific variant (e.g., a YouTube cut and a festival cut) from the same creative core.

Branches are not merges. A branch is a new CIS; it does not re-converge with its source. If two branches are to be reconciled, the human authors a new CIS that supersedes both, with `supersedes` references.

### 10.2.3 Reuse

A CIS may be **reused** as the seed for a new production. Reuse creates a new CIS instance with a `derived_from` reference. The derived CIS is independent and may diverge freely.

Use cases:

- A series of productions on a theme (e.g., a series of psychological cinema shorts on different emotional subjects) may derive each from a template CIS.
- A production company may maintain template CISes for commercial work, with per-client derivation.
- An educational series may derive each episode from a pedagogical template CIS.

Reuse preserves the original; the original remains `pinned` or `archived`. The derived instance starts at `draft` and proceeds through its own lifecycle.

### 10.2.4 Learning

Archived CISes are available to Director Memory (`002` Part 6) and to future authoring assistance. The Research stage of the Creative Decision Lifecycle (`002` Part 3.1) may query prior CISes for precedent: "has this creator specified a similar audience before? what emotional journey did they author for a similar theme?"

Learning is read-only. The archived CIS is never modified by learning; it is only referenced. This preserves GFS-003 (immutable revisions) across the full lifecycle.

---

# PART 11: MIGRATION STRATEGY

---

## 11.1 From Synopsis to CIS

The repository's current input is the synopsis (`synopsis/001-psychology-emotional-withdrawal.md` is representative: a free-text paragraph plus optional constraints). The target input is the CIS. The migration must:

- Preserve every existing synopsis as a valid Layer 0 seed (Part 7.2).
- Provide a path from any existing synopsis to a full CIS without loss of the human's original intent.
- Not break any existing pipeline that consumes a synopsis until the CIS is ready to replace it.
- Not require the human to author a full CIS for productions that have already completed.

The migration is therefore **additive and progressive**, not disruptive.

## 11.2 Migration Principles

| # | Principle | Statement |
|---|-----------|-----------|
| MP-1 | **Synopsis is a CIS seed.** Every existing synopsis is a valid Layer 0 CIS. No synopsis is rejected; no synopsis must be rewritten. |
| MP-2 | **CIS authoring is optional for legacy productions.** Productions already in progress or completed under the synopsis workflow remain under that workflow. The CIS is the input for new productions and for revisions of legacy productions. |
| MP-3 | **GENESIS accepts both during migration.** During the migration period, GENESIS accepts either a synopsis (which is promoted to a CIS Layer 0 by the CIS Validator with engine-assisted domain inference, labeled as inferred) or a CIS. After migration completes, GENESIS accepts only a validated CIS. |
| MP-4 | **Inferred CIS domains are labeled.** When the engine infers a CIS domain from a synopsis (e.g., inferring D-6 Audience from D-9 Platform), the inferred domain is labeled `inferred`, not `authored`. The human may accept or replace it. |
| MP-5 | **No silent intent invention.** Even during migration, the engine never silently invents intent. Inferred domains are labeled, presented to the human, and require approval before the CIS is pinned. |
| MP-6 | **The CIS does not amend the constitution.** The CIS is a derived standard under GFS-007/GFS-009. GFS-000..009 are unchanged. |

## 11.3 Migration Phases

### Phase C-1 — CIS Domain Specification and Template

- Specify the 24 CIS domains (Part 2.2) as documentation in `docs/genesis/specifications/` (a new `intent/` subdirectory, or extending the existing `product/` subdirectory per the existing classification in `docs/genesis/AGENTS.md`).
- Author the CIS template (`docs/genesis/templates/specification/001 — Creative Intent Specification Template.md`) per the existing template standards.
- Author the CIS defaults file (not a schema; a documented defaults reference).
- No runtime change.

**Exit criteria:** CIS domain specifications committed; template committed; defaults documented; ADR issued recording the CIS-as-input decision and the ordering invariant (I-OC-1).

### Phase C-2 — CIS Validator

- Implement the CIS Validator (Part 8) as a pre-GENESIS component, joining the pre-compilation stage (`001` §4.1).
- Implement the six validation dimensions (Part 8.2) with the three finding classes (`blocking`, `warning`, `advisory`).
- Implement the readiness state machine (`draft → validated → approved → pinned`).

**Exit criteria:** Validator runs on a test CIS; produces findings; blocks on blocking findings; state machine transitions correctly.

### Phase C-3 — Synopsis → CIS Promoter

- Implement a promoter that reads an existing synopsis and produces a draft CIS at Layer 0 (Story Intent = the synopsis prose) with all other domains `unspecified`.
- Implement engine-assisted domain inference for the most common derivations (D-9 Platform from `platform:` constraint, D-10 Runtime from `runtime:` constraint, D-14 Language from `narration_voice:` constraint, etc.), with every inferred domain labeled `inferred`.
- Implement the human review flow for inferred domains (Part 7.4).

**Exit criteria:** An existing synopsis (e.g., `synopsis/001-psychology-emotional-withdrawal.md`) can be promoted to a draft CIS; inferred domains are labeled; the human can accept or replace them; the resulting CIS can be validated and pinned.

### Phase C-4 — Guided Authoring

- Implement the guided authoring workflow (Part 7.3): domain prompting, default suggestion, template population, constraint reminder, validation feedback, reference and inspiration.
- Implement progressive refinement (Part 7.2): the human may author layer by layer, with validation at each layer.

**Exit criteria:** A human can author a full CIS from a single-sentence seed, layer by layer, with guidance and validation, without the engine ever authoring intent.

### Phase C-5 — GENESIS CIS Consumption

- Wire the Directorial Board's Research stage (`002` Part 3.1) to consume a pinned CIS version as its authoritative input.
- Wire each director to read the CIS domains relevant to its Decision Scope (Part 2.2 column 4).
- Wire the CIR root node (`002` Part 12.4) to record the CIS version it reasoned from.

**Exit criteria:** The Directorial Board reads the CIS; each director consumes its domains; the CIR records the CIS version; deterministic replay with the same CIS version produces the same CIR.

### Phase C-6 — Synopsis Deprecation

- After a validation period, deprecate the synopsis as a direct GENESIS input.
- Existing synopses remain valid as Layer 0 CIS seeds (MP-1); they are promoted to a CIS before GENESIS consumes them.
- Update the frontend (`frontend/`) to present the CIS as the input surface, with the synopsis as a seed entry mode.

**Exit criteria:** GENESIS no longer accepts a raw synopsis; every production begins with a CIS (which may be seeded by a synopsis).

### Phase C-7 — Lifecycle and Reuse

- Implement CIS versioning, branching, and reuse (Part 10.2) via ATLAS persistence.
- Implement Director Memory consumption of archived CISes (`002` Part 6, Part 10.2.4 learning).

**Exit criteria:** CIS versions are persisted and immutable; branches are independent; reuse creates derived instances; Director Memory can reference archived CISes.

## 11.4 Backward Compatibility

| Existing artifact | Compatibility | Action |
|-------------------|---------------|--------|
| `synopsis/*.md` | **Preserved as Layer 0 CIS seeds.** No synopsis is rejected. | The promoter (Phase C-3) reads them; no rewrite required. |
| `config/production_profiles.yaml` | **Preserved.** The CIS D-10 Runtime Goals and D-9 Platform Goals are consumed alongside the production profile, not instead of it. | None. The CIS and the production profile are both GENESIS inputs; the production profile carries the engine-side runtime configuration, the CIS carries the human-side runtime goals. |
| `001` pre-compilation stage | **Extended.** The CIS Validator joins the pre-compilation stage as its first step. | Add CIS Validator to `001` §4.1 pre-compilation. |
| `001` compiler passes | **Preserved.** The compiler passes read the CIR, not the CIS. The CIS does not change the compiler contract. | None. |
| `001` PKP schema | **Preserved.** The PKP is unchanged by the CIS. | None. |
| `002` Directorial Board | **Extended.** Each director's Research stage reads the CIS domains in its scope. | Add CIS domain references to each director's Inputs field (Part 2.2 column 4). |
| `002` CIR schema | **Extended.** The CIR root node records the CIS version. | Add `cis_version` to the CIR root provenance (`002` Part 12.4). |
| GFS-000..009 | **Preserved.** The CIS is a derived standard under GFS-007/GFS-009. | None. |
| GO-001..GO-119 | **Preserved.** The CIS uses ontology terms for domain vocabulary (e.g., GO-102 for audience, GO-103 for emotion). | None. New terms added only as derived ontology extensions under GFS-009. |
| PKP-00 Vision Specification | **Preserved and repositioned.** PKP-00 remains the highest creative authority *within the PKP*. The CIS is the highest creative authority *above* the PKP; PKP-00 is the compiled projection of the CIS's D-2 Theme, D-3 Message, D-21 Reflection Goals, and D-24 Provenance. | Document the derivation: CIS D-2/D-3/D-21/D-24 → Director's Vision CIR node (`002` Part 2.3.1) → PKP-00. |
| Existing agent specs | **Preserved.** | None. |

## 11.5 Risks and Architectural Impacts

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Authoring burden.** A 24-domain CIS may overwhelm casual creators. | High | Progressive refinement (Part 7.2): the human may begin with a single sentence. Guided authoring (Part 7.3) prompts domain by domain. Defaults are labeled and revocable. The CIS is complete only when the human is ready, not upfront. |
| **Inferred-domain acceptance.** Humans may rubber-stamp inferred domains during migration, reintroducing silent intent. | High | MP-4 and MP-5: inferred domains are labeled `inferred` and require explicit acceptance. The validator flags a CIS with high inferred-domain density in high-stakes domains (D-2, D-4, D-20) as a warning. |
| **CIS/PKP-00 conflation.** Implementers may treat PKP-00 (Vision Specification) as the CIS, collapsing input and output. | Medium | The schema projection (Phase C-1) enforces separate artifact types. PKP-00 is a PKP artifact; the CIS is a pre-GENESIS artifact. The derivation chain (CIS → CIR Vision node → PKP-00) is documented and audited. |
| **CIS bloat.** The 24-domain set may grow unbounded over time. | Medium | New domains are added under GFS-007 governance, with architectural justification. The domain set is versioned with the CIS specification. |
| **Presentation/Intent leakage.** Implementers may permit D-23 Presentation Profile to rewrite D-17/D-18/D-19 expectations. | Medium | I-PP-1 (Part 6.3) is audited: the validator flags any D-23 field that contradicts an intent domain as a warning. |
| **CIS version drift.** A production may inadvertently run against the wrong CIS version after a revision. | Medium | The CIR records `cis_version` in provenance; the PKP records `cir_origin`; deterministic replay pins the CIS version. Version drift is detectable and blockable. |
| **Synopsis-era productions become unmaintainable.** Legacy productions authored from synopses may be hard to revise under the CIS workflow. | Low | MP-2: legacy productions remain under the synopsis workflow. Revision of a legacy production promotes its synopsis to a CIS (Phase C-3) at revision time, not retroactively. |
| **Audience model over-fitting.** A highly specific audience model may over-constrain the Director, producing works that cannot transcend their target audience. | Low | I-AD-1 (Part 4.3): audience shapes realization, never redefines intent. The Director may propose a broader realization if it serves the intent better; the human decides. |

---

## Architectural Rules (Restated)

This specification produced **no implementation code, no Python, no TypeScript, no YAML, no JSON schemas**. It produced a constitutional architecture specification. Every recommendation is grounded in the existing repository:

- The CIS replaces the synopsis as GENESIS's input contract; existing synopses are preserved as Layer 0 CIS seeds (Part 11.1).
- The CIS's 24 domains are grounded in the existing ontology (GO-102 audience, GO-103 emotion, GO-109 visual, GO-110 audio, GO-111 editing, GO-116 creativity).
- The CIS's validation dimensions extend the existing validation patterns (`docs/genesis/patterns/validation/001 — Structural Validation Pattern.md`, `002 — Semantic Validation Pattern.md`, `003 — Completeness Validation Pattern.md`).
- The CIS's authoring workflow extends the existing template system (`docs/genesis/templates/`).
- The CIS's lifecycle follows GFS-003 (immutable revisions) and the existing state/lifecycle ontology (GO-003).
- The CIS's constraint precedence is consistent with the constitutional hierarchy (GFS-000 supreme; `00` §3.3 creative/technical separation).
- The CIS's relationship to the CIR and PKP extends `002` Part 12 (CIR) and `001` §5 (PKP) without modifying either.
- The ordering invariant (I-OC-1) establishes the specification sequence `000 → 001 → 002 → 003 → 004 (PKP) → PROMETHEUS → ORACLE → ATLAS`, with the CIS as the front-end of the creative front-end.

No parallel architecture is introduced. No existing concept is duplicated. The CIS extends existing work; it does not invent beside it.

---

## Cross-References

| Reference | Location | Relevance |
|-----------|----------|-----------|
| Constitutional Architecture | `00 — Cinema Production Engine Vision, Philosophy & Reference Architecture.md` | Supreme authority. The CIS derives from it; the human-as-final-reviewer principle (§3.8) is the CIS's authoring authority. |
| Migration Blueprint | `001 — GENESIS 2.0 Migration Specification.md` | Defines the pre-compilation stage the CIS Validator joins (§4.1) and the PKP the CIS ultimately produces (§5). |
| Director Intelligence | `002 — Director Intelligence & Creative Reasoning Architecture Specification.md` | Defines the Directorial Board that consumes the CIS (Part 2) and the CIR the CIS authorizes (Part 12). The CIS is the input to the Director; the CIR is the output. |
| Constitutional Charter | `docs/genesis/constitutions/00-ConstitutionCharter.md` (GFS-000) | Supreme constitutional authority. |
| Knowledge Constitution | `docs/genesis/constitutions/003 – Knowledge Constitution.md` (GFS-003) | Immutable revisions; the CIS follows this for versioning (Part 10). |
| Discovery Constitution | `docs/genesis/constitutions/004 Discovery Constitution.md` (GFS-004) | Discovery before decision; the CIS makes intent explicit before the Director discovers. |
| Governance Constitution | `docs/genesis/constitutions/007 – Governance Constitution.md` (GFS-007) | Governs the CIS as a derived standard. |
| Constitutional Ontology Framework | `docs/genesis/constitutions/009 — Constitutional Ontology Framework.md` (GFS-009) | Governs the CIS schema projection. |
| Audience Experience Ontology | `docs/genesis/ontology/experience/102 — Audience Experience Ontology.md` (GO-102) | CIS D-6 Audience vocabulary. |
| Human Psychology & Behavior Ontology | `docs/genesis/ontology/experience/103 — Human Psychology & Behavior Ontology.md` (GO-103) | CIS D-4/D-5 Emotion vocabulary. |
| Visual Expression Ontology | `docs/genesis/ontology/experience/109 — Visual Expression, Cinematography & Composition Ontology.md` (GO-109) | CIS D-17 Visual Expectations vocabulary. |
| Audio, Music, Sound Design & Silence Ontology | `docs/genesis/ontology/experience/110 — Audio, Music, Sound Design & Silence Ontology.md` (GO-110) | CIS D-18/D-19 Audio/Music Expectations vocabulary. |
| Temporal Experience, Editing & Narrative Rhythm Ontology | `docs/genesis/ontology/experience/111 — Temporal Experience, Editing & Narrative Rhythm Ontology.md` (GO-111) | CIS D-23 Presentation Profile (pacing, editing) vocabulary. |
| Creativity, Innovation & Design Reasoning Ontology | `docs/genesis/ontology/creativity/116 — Creativity, Innovation & Design Reasoning Ontology.md` (GO-116) | CIS D-2 Theme, D-3 Message vocabulary. |
| Communication, Dialogue & Interaction Ontology | `docs/genesis/ontology/semantic/108 Communication, Dialogue & Interaction.md` (GO-108) | CIS D-14 Language Strategy vocabulary. |
| State & Lifecycle Ontology | `docs/genesis/ontology/core/003 — Genesis State & Lifecycle Ontology.md` (GO-003) | CIS lifecycle state machine (Part 10.1). |
| Structural Validation Pattern | `docs/genesis/patterns/validation/001 — Structural Validation Pattern.md` | CIS validation dimension: completeness. |
| Semantic Validation Pattern | `docs/genesis/patterns/validation/002 — Semantic Validation Pattern.md` | CIS validation dimension: consistency. |
| Completeness Validation Pattern | `docs/genesis/patterns/validation/003 — Completeness Validation Pattern.md` | CIS validation dimension: missing intent. |
| PKP-00 Vision Specification | `docs/genesis/specifications/pkp/00 — Vision Specification.md` | The compiled projection of the CIS's D-2/D-3/D-21/D-24 into the PKP. |
| Existing synopsis | `synopsis/001-psychology-emotional-withdrawal.md` | Representative legacy input; becomes a Layer 0 CIS seed under migration (Part 11.1). |
| Production profiles | `config/production_profiles.yaml` | Engine-side runtime configuration; the CIS D-9/D-10 carry the human-side runtime goals. Both are GENESIS inputs. |
| Documentation standards | `docs/genesis/standards/003 — Documentation Standards.md` | Governs the CIS template and domain specifications. |
| Template directory | `docs/genesis/templates/` | Location for the CIS template (Phase C-1). |

---

**End of Specification.**