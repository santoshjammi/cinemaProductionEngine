# 004 — Creative Object Model (COM) & Semantic Architecture Specification

**Status:** Constitutional Architecture Specification — Supreme Authority for the Semantic Programming Model
**Version:** 1.0.0
**Date:** 2026-07-21
**Authority:** Derives from `00 — Cinema Production Engine Vision, Philosophy & Reference Architecture.md` (the Constitutional Architecture). Extends the migration blueprint of `001 — GENESIS 2.0 Migration Specification.md`, the Director Intelligence layer of `002 — Director Intelligence & Creative Reasoning Architecture Specification.md`, and the Creative Intent Specification of `003 — Creative Intent Specification (CIS) Architecture.md`. This document defines the **Creative Object Model (COM)** — the canonical semantic programming model spoken by every subsystem of the Cinema Production Engine.
**Precedence:** Below the Constitutional Architecture (§00). Equal in tier to `001`, `002`, and `003`. Above all ontology extensions, domain specifications, PKP specifications, workflow definitions, and implementation guides. When this document conflicts with an informal semantic convention, a local object definition, or a subsystem-private vocabulary, this document wins unless the conflict is with the Constitutional Architecture itself.
**Scope:** The Creative Object Model (the canonical typed objects of filmmaking), the Creative Relationship Model (the canonical predicates between objects), Creative Operations (the canonical mutations), Semantic Invariants (the always-true rules), the Creative State Model (lifecycle state machines), the Semantic Query Model (how subsystems reference objects), the Mapping Architecture (how objects flow through the pipeline), Compiler Semantics (how GENESIS compiles objects), Governance of the COM, and the Migration Strategy that integrates the COM into the existing architecture.

---

## Table of Contents

**PART 1: PHILOSOPHY**
- [1.1 Why Filmmaking Requires a Semantic Programming Model](#11-why-filmmaking-requires-a-semantic-programming-model)
- [1.2 Why Ontology Alone Is Insufficient](#12-why-ontology-alone-is-insufficient)
- [1.3 Why Prompts Are Insufficient](#13-why-prompts-are-insufficient)
- [1.4 Why Semantic Objects Are Required](#14-why-semantic-objects-are-required)
- [1.5 Why Every Component Must Share a Common Language](#15-why-every-component-must-share-a-common-language)
- [1.6 How the COM Differs from Adjacent Artifacts](#16-how-the-com-differs-from-adjacent-artifacts)

**PART 2: CREATIVE OBJECT MODEL**
- [2.1 Object Specification Contract](#21-object-specification-contract)
- [2.2 Object Catalog](#22-object-catalog)
- [2.3 Object Details](#23-object-details)

**PART 3: CREATIVE RELATIONSHIP MODEL**
- [3.1 Relationship Specification Contract](#31-relationship-specification-contract)
- [3.2 Relationship Catalog](#32-relationship-catalog)

**PART 4: CREATIVE OPERATIONS**
- [4.1 Operation Classification](#41-operation-classification)
- [4.2 Operation Catalog](#42-operation-catalog)
- [4.3 Operation Authority Matrix](#43-operation-authority-matrix)

**PART 5: SEMANTIC INVARIANTS**
- [5.1 Invariant Classification](#51-invariant-classification)
- [5.2 Invariant Catalog](#52-invariant-catalog)

**PART 6: CREATIVE STATE MODEL**
- [6.1 State Machine Principles](#61-state-machine-principles)
- [6.2 State Machines by Object Family](#62-state-machines-by-object-family)

**PART 7: SEMANTIC QUERY MODEL**
- [7.1 Query Primitives](#71-query-primitives)
- [7.2 Subsystem Query Contracts](#72-subsystem-query-contracts)

**PART 8: MAPPING ARCHITECTURE**
- [8.1 The Full Pipeline as Object Flow](#81-the-full-pipeline-as-object-flow)
- [8.2 Layer Ownership](#82-layer-ownership)
- [8.3 Immutability and Executability Across Layers](#83-immutability-and-executability-across-layers)

**PART 9: COMPILER SEMANTICS**
- [9.1 GENESIS as an Object Compiler](#91-genesis-as-an-object-compiler)
- [9.2 Compiler Phases on Objects](#92-compiler-phases-on-objects)
- [9.3 Deterministic and Incremental Compilation](#93-deterministic-and-incremental-compilation)

**PART 10: GOVERNANCE**
- [10.1 Governance Authority](#101-governance-authority)
- [10.2 Semantic Evolution](#102-semantic-evolution)
- [10.3 Compatibility, Deprecation, Migration](#103-compatibility-deprecation-migration)

**PART 11: MIGRATION STRATEGY**
- [11.1 Integration Principles](#111-integration-principles)
- [11.2 Migration Phases](#112-migration-phases)
- [11.3 Backward Compatibility](#113-backward-compatibility)
- [11.4 Risks and Architectural Impacts](#114-risks-and-architectural-impacts)

---

# PART 1: PHILOSOPHY

---

## 1.1 Why Filmmaking Requires a Semantic Programming Model

Filmmaking is the most semantically dense creative form. A single frame carries simultaneous decisions from narrative, character, psychology, performance, camera, lighting, color, composition, sound, music, editing, and platform domains. These decisions are not independent; they reference, constrain, contradict, and resolve each other. A camera move *motivated by* a character's emotional state; a music cue *resolving* a tension *set up* by a reveal; a callback *echoing* a prior motif — these are semantic relationships between creative objects, not strings of text.

A semantic programming model is required because the Cinema Production Engine treats filmmaking as compilation (`00` §3.2), and compilation requires a typed object model. A compiler does not operate on prose; it operates on an Abstract Syntax Tree of typed nodes with defined relationships. The Directorial Board (`002` Part 2) reasons about creative decisions; the compiler passes (`001` §4.2) compile those decisions; PROMETHEUS renders the compiled output; ORACLE validates it; ATLAS persists it. Every one of these subsystems must operate on the **same typed objects** or they cannot communicate, validate, or revise coherently.

The Creative Object Model is that typed object model. It is the language of the Cinema Production Engine in the precise sense that a programming language's type system is the language of its compiler: not a documentation convenience, but the structural contract that makes every higher-level operation well-defined.

## 1.2 Why Ontology Alone Is Insufficient

The repository already contains a deep ontology hierarchy: GO-001 (Core) through GO-119, plus generated ontologies GO-200/201/301 (`001` §1.1 S2). The ontology defines the **vocabulary** of filmmaking — the nouns (GO-001) and the predicates (GO-002). This is necessary and is preserved unchanged by this specification.

But ontology is insufficient as a programming model for four reasons:

| # | Insufficiency | Consequence |
|---|---------------|-------------|
| O-1 | **Ontology defines concepts, not object identity.** GO-104 defines what a Character is; it does not define how a specific Character instance is identified, owned, versioned, or traced across CIS → CIR → PKP → media. | Subsystems invent their own identity schemes; cross-subsystem reference fails. |
| O-2 | **Ontology defines predicates, not operations.** GO-002 defines `precedes` and `causes`; it does not define what it means to `Split` a Scene, `Escalate Emotion`, or `Rollback` a Creative Version. | Subsystems invent their own mutations; invariants break silently. |
| O-3 | **Ontology defines terms, not lifecycle.** GO-003 defines state and lifecycle concepts, but not the state machines of a Scene, a Creative Decision, or a Creative Branch. | Subsystems invent their own state transitions; freeze semantics diverge. |
| O-4 | **Ontology is governance-tier; a programming model is runtime-tier.** Ontology is amended under GFS-009 governance, slowly, by architects. A programming model must be applicable at runtime by the compiler, the Director, and ORACLE without amending the ontology. | Without a programming model, every runtime operation becomes an ontology amendment. |

The COM is **not** a replacement for the ontology. The COM is the programming model that **uses** the ontology's vocabulary. GO-001 defines what a Character is; the COM defines the Character object's identity, ownership, lifecycle, operations, invariants, and query interface. The two are complementary: ontology is the dictionary; the COM is the type system.

## 1.3 Why Prompts Are Insufficient

The repository's current pipeline (`pipeline/orchestrator.py`, `config/prompts.py`) operates substantially on prompts — text strings fed to LLMs to produce more text strings. Prompts are insufficient as the semantic substrate for the same reason prose synopses are insufficient (`003` Part 1.1): they carry semantics only in the reader's interpretation.

A prompt is a **projection** of a set of creative objects into text for the purpose of LLM consumption. The projection is lossy: two different object configurations may project to similar prompts, and one prompt may be reified into different objects by different LLM calls. If prompts are the substrate, the engine cannot validate, trace, or revise coherently.

The COM inverts the relationship: **objects are the substrate; prompts are a projection.** The compiler passes manipulate objects; the Prompt Compiler (`001` §4.2 Pass 16) projects objects into prompts as the final step before PROMETHEUS. PROMETHEUS reads the PKP (objects), not the prompts, for its deterministic execution. Prompts exist; they are not the substrate.

## 1.4 Why Semantic Objects Are Required

Semantic objects are required because the engine's invariants require structural enforcement, and structural enforcement requires typed objects.

Consider the invariant "Every Payoff references a prior Setup" (`002` Part 5.2, foreshadowing/payoff reasoning). To enforce this invariant, the engine must:

1. Recognize a Payoff as a typed object, distinct from a Setup.
2. Require a `references` edge from the Payoff to a Setup.
3. Require the Setup to `precedes` the Payoff.
4. Detect a Payoff with no `references` edge as an invariant violation.
5. Detect a Payoff whose referenced Setup does not `precedes` it as a temporal violation.

None of this is possible with prose or prompts. It requires a Payoff object type, a Setup object type, a `references` predicate, a `precedes` predicate, and a validator that traverses the graph. The COM provides the types; the Creative Relationship Model (Part 3) provides the predicates; the Semantic Invariants (Part 5) provide the rules; ORACLE provides the validation.

Every invariant in `002` Part 5.2 (suspense, pacing, silence, payoff, foreshadowing, callbacks, transitions, motivations) requires the same structural treatment. Semantic objects are the substrate that makes the Directorial Board's reasoning enforceable.

## 1.5 Why Every Component Must Share a Common Language

The five components that consume creative semantics — Human Authoring, GENESIS (Directorial Board + Compiler), PROMETHEUS, ORACLE, ATLAS — are architecturally separated (`001` §2.1 pillar boundaries). They communicate only through artifacts (CIS, CIR, PKP, media, validation reports) and never through direct calls (`001` §2.3).

If each component uses its own semantic vocabulary, every artifact boundary becomes a translation boundary, and every translation is a potential source of drift. A "Scene" in the CIS, a "Scene" in the CIR, a "Scene" in the PKP, and a "Scene" in ORACLE's drift report would be four different objects with four different identities, and reconciling them would require heuristic matching.

The COM eliminates this by being the **single shared language**. A Scene is the same typed object whether it appears in the CIS's Story Intent, the CIR's narrative reasoning, the PKP's scene specification, ORACLE's drift report, or ATLAS's archive. The identity scheme, the relationships, the invariants, and the operations are identical across all components. Translation is eliminated; only projection differs (a Scene in the CIS is an intent; a Scene in the PKP is an executable specification; the object type is the same).

This is the architectural expression of `00` §3.5 ("Provenance Is Mandatory") made practical: provenance requires a stable identity that survives across components, and stable identity requires a shared object model.

## 1.6 How the COM Differs from Adjacent Artifacts

| Artifact | What it is | Relationship to the COM |
|----------|-----------|--------------------------|
| **CIS** (`003`) | The human-authored statement of what the creator wants. | The CIS is authored **in** the COM's vocabulary. A CIS's Story Intent is a Story object; its Emotional Journey is an Emotion Transition Graph of Emotion objects; its Ending Intent is a Creative Intent object typed on an Ending. The CIS is a COM document. |
| **CIR** (`002` Part 12) | The Director's reasoning record: why each creative decision exists. | The CIR is a graph of Creative Decision objects, each referencing COM objects as the decided-upon subjects. The CIR's nodes are COM objects of type Creative Decision; the CIR's edges are COM relationships. |
| **PKP** (`001` §5) | The compiled production knowledge PROMETHEUS executes. | The PKP is a projection of COM objects into executable specifications. A PKP Scene Specification is a Scene object in its frozen, executable state. The PKP is the COM, compiled. |
| **Ontology** (GO-001..119) | The vocabulary of filmmaking: nouns (GO-001) and predicates (GO-002). | The ontology defines the terms the COM's types and relationships are named with. The COM is the programming model that uses the ontology's vocabulary. The COM does not redefine ontology terms; it binds them to object identity, lifecycle, and operations. |
| **Knowledge Graph** (PKG, GFS-003) | The graph store that holds instances and edges with provenance. | The PKG is **where** COM objects live. The COM is **what** the PKG stores. The PKG is the storage; the COM is the type system of the storage. |
| **Runtime** (PROMETHEUS, ORACLE, ATLAS) | The execution, validation, and persistence pillars. | The runtime operates on COM objects. PROMETHEUS reads PKP objects (compiled COM); ORACLE validates media against COM objects; ATLAS persists COM objects. The runtime never defines its own object types. |

The COM is the **semantic programming model**. The ontology is its vocabulary; the PKG is its store; the CIS, CIR, and PKP are its projections at different pipeline stages; the runtime is its executor, validator, and persistence layer.

---

# PART 2: CREATIVE OBJECT MODEL

---

## 2.1 Object Specification Contract

Every first-class Creative Object is specified by a fourteen-field contract. The contract is the architectural type declaration; it is not a schema (no schema language is specified here; schemas are derived projections under GFS-009).

| Field | Definition |
|-------|-----------|
| **Purpose** | What the object exists to represent, in one sentence. |
| **Architectural responsibility** | What the object is structurally accountable for. What is invalid if this object is absent. |
| **Identity** | How instances are uniquely identified. The identifier scheme (per `002` Part 12.4 and `003` Part 10.2.1, extended by this specification). |
| **Ownership** | Which director (`002` Part 2.3) or layer owns the object's semantics. Who is the authority. |
| **Lifecycle** | The state machine the object traverses (Part 6). |
| **Parent/Child relationships** | The structural composition hierarchy. |
| **Cardinality** | How many instances may exist in a given context (e.g., one Story per production; many Scenes per Story). |
| **Composition rules** | How instances may be composed from other instances. |
| **Traceability** | How the instance traces upstream (to its authoring source) and downstream (to its compilations and media). |
| **Versioning** | How the instance versions (per GFS-003 immutable revisions). |
| **Immutability rules** | When the instance becomes immutable (freeze), and what exceptions exist. |
| **Consumers** | Which subsystems read the object. |
| **Producers** | Which subsystems may author the object. |
| **Validation responsibilities** | Which invariants (Part 5) the object is responsible for satisfying. |

**Identity scheme (COM-wide):** `com:<production-id>:<object-type>:<ordinal>[:<revision>]`, e.g., `com:ew001:scene:07@3`. The scheme extends `002` Part 12.4 (CIR identifiers) and `003` Part 10.2.1 (CIS identifiers) so that the same object can be referenced identically across CIS, CIR, PKP, ORACLE, and ATLAS. The `<revision>` suffix is absent for the current revision and present for prior immutable revisions.

## 2.2 Object Catalog

The COM defines the following first-class Creative Objects, grouped by family. Each is detailed in §2.3. The catalog is closed: subsystems may not invent object types outside this catalog (Part 10). New types are added only under governance (Part 10.2).

| Family | Objects |
|--------|---------|
| **Production root** | Production, Creative Intent, Creative Decision, Creative Artifact, Creative Version, Creative Branch |
| **Story and narrative** | Story, Theme, Message, Narrative, Act, Sequence, Scene, Beat, Moment, Transition |
| **Character and psychology** | Character, Relationship, Goal, Need, Obstacle, Conflict, Decision, Memory, Flashback |
| **Dialogue and performance** | Dialogue, Monologue, Silence, Performance |
| **Emotion** | Emotion, Emotion Transition, Emotional Journey |
| **Reveal structure** | Reveal, Mystery, Setup, Payoff, Foreshadowing, Callback, Motif, Symbol |
| **Visual language** | Visual Language, Shot, Camera, Lighting, Environment, Location |
| **Audio language** | Music Theme, Soundscape, Silence (shared with dialogue family for silence-as-beat) |
| **Temporal** | Timeline, Runtime Segment |
| **Audience and intent** | Audience, Experience, Reflection, Learning Objective, Creative Constraint, Presentation Profile |
| **Revelation and reference** | Reveal, Mystery (cross-listed with reveal structure) |

## 2.3 Object Details

Each object is specified per the §2.1 contract. The details are dense by necessity: this is the language specification of the platform.

### 2.3.1 Production

| Field | Value |
|-------|-------|
| Purpose | The root object of a single cinematic work. |
| Architectural responsibility | Carries the production identity, the pinned CIS version, the frozen CIR version, the frozen PKP version, and the production's lifecycle state. Without Production, no other object has a container. |
| Identity | `com:<production-id>:production:01`. |
| Ownership | Chief Director (`002` Part 2.3.1); human author for CIS-side fields. |
| Lifecycle | `conceived → authored (CIS) → reasoning (CIR) → compiled (PKP) → rendering → validating → archived`. |
| Parent/Child | No parent. Contains exactly one Story, one Creative Intent, one CIR root, one PKP root. |
| Cardinality | Exactly one per production. |
| Composition rules | A Production is composed from one CIS (pinned), one CIR (frozen), one PKP (frozen), zero or more media artifacts, zero or more validation reports. |
| Traceability | Upstream: human author. Downstream: all media, all validation, all archives. |
| Versioning | The Production itself is immutable once archived; its contained artifacts version independently per their own rules. |
| Immutability rules | The Production's identity and its pinned CIS/CIR/PKR version references are immutable after `compiled`. |
| Consumers | All subsystems. |
| Producers | Human authoring (conceives); Directorial Board (reasons); Compiler (compiles); PROMETHEUS (renders); ORACLE (validates); ATLAS (archives). |
| Validation responsibilities | Must reference exactly one pinned CIS, one frozen CIR, one frozen PKP. |

### 2.3.2 Story

| Field | Value |
|-------|-------|
| Purpose | The narrative premise and thematic spine of the production. |
| Architectural responsibility | Carries the dramatic question, the central conflict, and the story-level beats. Invalid if absent: no narrative can be compiled. |
| Identity | `com:<production-id>:story:01`. |
| Ownership | Story Director (`002` Part 2.3.2). |
| Lifecycle | `proposed → selected → frozen → (revised)`. |
| Parent/Child | Parent: Production. Children: zero or more Acts, zero or more Themes, zero or more Messages, zero or more story-level Beats. |
| Cardinality | Exactly one per Production. |
| Composition rules | Composed from the CIS's Story Intent (D-1) and Theme (D-2), reasoned into a Story by the Story Director. |
| Traceability | Upstream: CIS D-1, D-2. Downstream: Narrative, Acts, Sequences, Scenes. |
| Versioning | GFS-003 immutable revisions. |
| Immutability rules | Frozen at CIR freeze (`002` Part 12.2). |
| Consumers | Narrative Director, Character Director, all downstream directors, all compiler passes. |
| Producers | Story Director (authors); human (amends). |
| Validation responsibilities | Must have a dramatic question; must have a central conflict; must have at least one Theme. |

### 2.3.3 Theme

| Field | Value |
|-------|-------|
| Purpose | What the story is about in the thematic sense (`003` D-2). |
| Architectural responsibility | The thematic spine that every Motif, Symbol, and visual metaphor must trace to. Invalid if absent: visual metaphors are unanchored. |
| Identity | `com:<production-id>:theme:<ordinal>`. |
| Ownership | Story Director (proposes); Chief Director (ratifies). |
| Lifecycle | `proposed → ratified → frozen → (revised)`. |
| Parent/Child | Parent: Story. Children: zero or more Motifs, zero or more Symbols. |
| Cardinality | One or more per Story. |
| Composition rules | Derived from CIS D-2; may reference GO-116 (Creativity, Innovation & Design Reasoning) vocabulary. |
| Traceability | Upstream: CIS D-2. Downstream: Motif, Symbol, Visual Language. |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | Visual Director (for metaphor grounding), Narrative Director, Chief Director. |
| Producers | Story Director. |
| Validation responsibilities | Every Symbol and visual Motif must `references` a Theme. |

### 2.3.4 Message

| Field | Value |
|-------|-------|
| Purpose | What the audience should take away (`003` D-3). May be `none`. |
| Architectural responsibility | The didactic stance of the production. Distinguished from Theme: Theme is what the story is about; Message is what the audience should conclude. |
| Identity | `com:<production-id>:message:<ordinal>` or `com:<production-id>:message:none`. |
| Ownership | Chief Director. |
| Lifecycle | `proposed → ratified → frozen → (revised)`. |
| Parent/Child | Parent: Story. |
| Cardinality | Zero or one explicit; `none` is a valid value. |
| Composition rules | Derived from CIS D-3; must be compatible with Theme (validation: consistency, `003` Part 2.3). |
| Traceability | Upstream: CIS D-3. Downstream: Reflection. |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | Chief Director, Psychology Director (for reflection alignment). |
| Producers | Chief Director. |
| Validation responsibilities | Must be compatible with Theme (not contradictory). |

### 2.3.5 Narrative

| Field | Value |
|-------|-------|
| Purpose | The ordering and structure through which the Story is told. |
| Architectural responsibility | Carries the act/sequence structure, emotional curve, conflict curve, reveal schedule. |
| Identity | `com:<production-id>:narrative:01`. |
| Ownership | Narrative Director (`002` Part 2.3.3). |
| Lifecycle | `proposed → structured → frozen → (revised)`. |
| Parent/Child | Parent: Story. Children: Acts. |
| Cardinality | Exactly one per Story. |
| Composition rules | Composed from the Story, with structure (acts, sequences) per the Narrative Director's reasoning. |
| Traceability | Upstream: Story. Downstream: Acts, Sequences, Scenes. |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | Editorial Director, Scene Compiler, all downstream. |
| Producers | Narrative Director. |
| Validation responsibilities | Must contain at least one Act; must have an emotional curve; must have a conflict curve. |

### 2.3.6 Act

| Field | Value |
|-------|-------|
| Purpose | A major structural division of the Narrative. |
| Architectural responsibility | Carries the act objective and the act's contribution to the emotional and conflict curves. |
| Identity | `com:<production-id>:act:<ordinal>`. |
| Ownership | Narrative Director. |
| Lifecycle | `proposed → structured → frozen → (revised)`. |
| Parent/Child | Parent: Narrative. Children: Sequences. |
| Cardinality | One or more per Narrative (typically 3–5; profile-influenced). |
| Composition rules | Composed from Sequences. |
| Traceability | Upstream: Narrative. Downstream: Sequences, Scenes. |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | Editorial Director, Scene Compiler. |
| Producers | Narrative Director. |
| Validation responsibilities | Must have an objective; must contribute to the emotional curve. |

### 2.3.7 Sequence

| Field | Value |
|-------|-------|
| Purpose | A narrative unit within an Act that pursues a sub-objective. |
| Architectural responsibility | Carries the sequence objective and its emotional transition. |
| Identity | `com:<production-id>:sequence:<act-ordinal>.<seq-ordinal>`. |
| Ownership | Narrative Director. |
| Lifecycle | `proposed → structured → frozen → (revised)`. |
| Parent/Child | Parent: Act. Children: Scenes. |
| Cardinality | One or more per Act. |
| Composition rules | Composed from Scenes. |
| Traceability | Upstream: Act. Downstream: Scenes. |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | Scene Compiler, Editorial Director. |
| Producers | Narrative Director. |
| Validation responsibilities | Must have an objective; must have an emotional transition. |

### 2.3.8 Scene

| Field | Value |
|-------|-------|
| Purpose | The atomic unit of dramatic action. |
| Architectural responsibility | Carries the scene objective, emotional goal, conflict, duration, and the composition root for Shots, Dialogue, Music, Lighting. The most central object in the COM. |
| Identity | `com:<production-id>:scene:<ordinal>`. |
| Ownership | Narrative Director (structure); Story Director (purpose); many directors own their projections into the Scene. |
| Lifecycle | `proposed → planned → frozen → (revised)`. See Part 6.2. |
| Parent/Child | Parent: Sequence. Children: Beats, Shots, Dialogue instances, Music cues, Lighting specs, Camera specs. |
| Cardinality | One or more per Sequence; total constrained by the production profile (`001` §4.1 scene class planner). |
| Composition rules | Composed from Beats; references one or more Characters; carries one Scene Objective. |
| Traceability | Upstream: Sequence, Story. Downstream: Beats, Shots, PKP Scene Specification, PROMETHEUS rendering units. |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | All directors with per-scene scope; all compiler passes from Pass 05 onward; PROMETHEUS; ORACLE; ATLAS. |
| Producers | Narrative Director (structure); many directors (their projections). |
| Validation responsibilities | Must have a Purpose; must have a Scene Objective; must have an emotional goal; must have a duration; must reference at least one Character (unless explicitly a no-character scene, declared). |

### 2.3.9 Beat

| Field | Value |
|-------|-------|
| Purpose | The smallest unit of narrative change within a Scene. |
| Architectural responsibility | Carries the beat's emotional shift and narrative payload. |
| Identity | `com:<production-id>:beat:<scene-ordinal>.<beat-ordinal>`. |
| Ownership | Narrative Director. |
| Lifecycle | `proposed → frozen → (revised)`. |
| Parent/Child | Parent: Scene. |
| Cardinality | One or more per Scene. |
| Composition rules | May reference a Reveal, a Setup, a Payoff, a Callback. |
| Traceability | Upstream: Scene. Downstream: Shots (beats motivate shot boundaries). |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | Editorial Director (cut rhythm), Cinematography Director (shot motivation). |
| Producers | Narrative Director. |
| Validation responsibilities | Must belong to exactly one Scene. |

### 2.3.10 Moment

| Field | Value |
|-------|-------|
| Purpose | A singularly emphasized point within a Beat (a look, a silence, a gesture). |
| Architectural responsibility | Carries the moment's emphasis and its emotional weight. |
| Identity | `com:<production-id>:moment:<scene>.<beat>.<moment>`. |
| Ownership | Psychology Director (emotional weight); Performance Director (gesture/look). |
| Lifecycle | `proposed → frozen → (revised)`. |
| Parent/Child | Parent: Beat. |
| Cardinality | Zero or more per Beat. |
| Composition rules | May coincide with a Silence or a Performance beat. |
| Traceability | Upstream: Beat. Downstream: Shot framing, Music cue. |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | Cinematography Director, Music Director. |
| Producers | Psychology Director, Performance Director. |
| Validation responsibilities | Must belong to exactly one Beat. |

### 2.3.11 Transition

| Field | Value |
|-------|-------|
| Purpose | The directed connection between two narrative states (Scenes or Sequences). |
| Architectural responsibility | Carries the transition shape (cut, dissolve, match-cut, audio bridge) and the emotional transition it realizes. |
| Identity | `com:<production-id>:transition:<from>.<to>`. |
| Ownership | Editorial Director. |
| Lifecycle | `proposed → frozen → (revised)`. |
| Parent/Child | No parent (it is a relationship object). Connects two Scenes or two Sequences. |
| Cardinality | One between each adjacent pair; zero or more non-adjacent (e.g., cross-act callbacks). |
| Composition rules | References a `from` state and a `to` state; carries an Emotion Transition. |
| Traceability | Upstream: the two connected states. Downstream: PROMETHEUS transition execution. |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | Editorial Director, PROMETHEUS. |
| Producers | Editorial Director. |
| Validation responsibilities | Must connect two valid narrative states; the `from` state must `precedes` the `to` state. |

### 2.3.12 Character

| Field | Value |
|-------|-------|
| Purpose | A person (or personified entity) in the Story. |
| Architectural responsibility | Carries identity, biography, psychology, voice, visual identity, growth arc. |
| Identity | `com:<production-id>:character:<ordinal>`. |
| Ownership | Character Director (`002` Part 2.3.4). |
| Lifecycle | `proposed → developed → frozen → (revised)`. |
| Parent/Child | Parent: Story. Children: Goals, Needs, Memory instances. |
| Cardinality | One or more per Story. |
| Composition rules | Composed from biography, psychology, voice identity, visual identity, growth arc; references other Characters via Relationship. |
| Traceability | Upstream: CIS (if named), Story. Downstream: Dialogue, Performance, Shot (blocking), PROMETHEUS character consistency. |
| Versioning | GFS-003. Cross-production reuse via ATLAS (`002` Part 6.2). |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | All directors with character scope; Dialogue, Performance, Cinematography, Lighting, Voice compilers; PROMETHEUS; ORACLE. |
| Producers | Character Director; Psychology Director (psychology subset). |
| Validation responsibilities | Must have a Motivation (Goal or Need); must have a visual identity; must have a voice identity (if speaking). |

### 2.3.13 Relationship

| Field | Value |
|-------|-------|
| Purpose | The directed relation between two Characters. |
| Architectural responsibility | Carries the relationship type, its valence, its evolution over the Story. |
| Identity | `com:<production-id>:relationship:<char-a>.<char-b>:<type>`. |
| Ownership | Character Director. |
| Lifecycle | `proposed → frozen → (revised)`. |
| Parent/Child | Parent: Story. Connects two Characters. |
| Cardinality | The relationship graph must be complete: every Character pair has a Relationship (including "no relationship" as an explicit value). |
| Composition rules | References two Characters; carries a type (familial, romantic, professional, antagonistic, etc.) and a valence. |
| Traceability | Upstream: Characters. Downstream: Dialogue (informs register), Performance (informs physicality). |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | Dialogue Director, Performance Director, Psychology Director. |
| Producers | Character Director. |
| Validation responsibilities | Must reference two valid Characters; the graph must be complete. |

### 2.3.14 Goal

| Field | Value |
|-------|-------|
| Purpose | What a Character wants to achieve. |
| Architectural responsibility | Drives the Character's behavior and the Conflict. |
| Identity | `com:<production-id>:goal:<character>:<ordinal>`. |
| Ownership | Character Director. |
| Lifecycle | `proposed → frozen → (revised)`. |
| Parent/Child | Parent: Character. |
| Cardinality | One or more per Character. |
| Composition rules | May conflict with another Character's Goal (producing Conflict). |
| Traceability | Upstream: Character. Downstream: Conflict, Beats (goals drive beats). |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | Narrative Director, Psychology Director. |
| Producers | Character Director. |
| Validation responsibilities | Must belong to a Character (Goal belongs to an Actor — invariant I-SI-13). |

### 2.3.15 Need

| Field | Value |
|-------|-------|
| Purpose | What a Character requires for psychological wholeness, whether they know it or not. |
| Architectural responsibility | The psychological depth beneath the Goal. Distinguished from Goal: Goal is what the Character pursues; Need is what the Character actually requires. |
| Identity | `com:<production-id>:need:<character>:<ordinal>`. |
| Ownership | Psychology Director. |
| Lifecycle | `proposed → frozen → (revised)`. |
| Parent/Child | Parent: Character. |
| Cardinality | Zero or more per Character. |
| Composition rules | May be unaligned with the Character's Goal (a classic dramatic structure). |
| Traceability | Upstream: Character. Downstream: Reflection, emotional arc. |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | Psychology Director, Narrative Director. |
| Producers | Psychology Director. |
| Validation responsibilities | If present, must belong to a Character. |

### 2.3.16 Obstacle

| Field | Value |
|-------|-------|
| Purpose | What stands between a Character and their Goal. |
| Architectural responsibility | Generates Conflict. |
| Identity | `com:<production-id>:obstacle:<character>:<ordinal>`. |
| Ownership | Narrative Director. |
| Lifecycle | `proposed → frozen → (revised)`. |
| Parent/Child | Parent: Character (the obstructed character) or Story (a structural obstacle). |
| Cardinality | One or more per Goal. |
| Composition rules | May be external (another Character, the environment) or internal (the Character's own psychology). |
| Traceability | Upstream: Goal. Downstream: Conflict. |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | Narrative Director, Psychology Director. |
| Producers | Narrative Director. |
| Validation responsibilities | Must oppose a Goal. |

### 2.3.17 Conflict

| Field | Value |
|-------|-------|
| Purpose | The dramatic engine produced by Goal against Obstacle (or Goal against Goal). |
| Architectural responsibility | The central driver of narrative progression. |
| Identity | `com:<production-id>:conflict:<ordinal>`. |
| Ownership | Narrative Director. |
| Lifecycle | `proposed → frozen → (revised)`. |
| Parent/Child | Parent: Story (story-level conflict) or Scene (scene-level conflict). |
| Cardinality | One or more per Story; zero or more per Scene. |
| Composition rules | References at least one participant (Character or Goal or Obstacle). |
| Traceability | Upstream: Goals, Obstacles. Downstream: Beats (conflict drives beats). |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | Narrative Director, Psychology Director, Story Director. |
| Producers | Narrative Director. |
| Validation responsibilities | Must have at least one participant (invariant I-SI-12). |

### 2.3.18 Decision (Character)

| Field | Value |
|-------|-------|
| Purpose | A Character's choice within the Story. |
| Architectural responsibility | The point at which the Character's will commits; drives the narrative forward. |
| Identity | `com:<production-id>:character_decision:<character>:<ordinal>`. |
| Ownership | Character Director (will); Psychology Director (motivation). |
| Lifecycle | `proposed → frozen → (revised)`. |
| Parent/Child | Parent: Character. |
| Cardinality | Zero or more per Character. |
| Composition rules | Resolves (or fails to resolve) a Conflict; may fulfill or frustrate a Goal. |
| Traceability | Upstream: Character, Conflict, Goal. Downstream: Beats. |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | Narrative Director, Psychology Director. |
| Producers | Character Director. |
| Validation responsibilities | Must belong to a Character. |

### 2.3.19 Dialogue

| Field | Value |
|-------|-------|
| Purpose | Spoken words by a Character. |
| Architectural responsibility | The verbal content of a Scene; carries subtext and register. |
| Identity | `com:<production-id>:dialogue:<scene>:<line>`. |
| Ownership | Dialogue Director (`002` Part 2.3.7). |
| Lifecycle | `proposed → frozen → (revised)`. |
| Parent/Child | Parent: Scene. |
| Cardinality | Zero or more per Scene. |
| Composition rules | Has exactly one speaker (a Character); may carry subtext; may be part of a conversation. |
| Traceability | Upstream: Scene, Character. Downstream: Voice Compiler, PROMETHEUS Voice Realization. |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | Voice Compiler, PROMETHEUS, ORACLE (dialogue quality). |
| Producers | Dialogue Director. |
| Validation responsibilities | Must have a speaker (invariant I-SI-8). |

### 2.3.20 Monologue

| Field | Value |
|-------|-------|
| Purpose | Extended speech by a single Character, typically interior or direct-address. |
| Architectural responsibility | Carries the Character's interiority or direct-address intent. |
| Identity | `com:<production-id>:monologue:<scene>:<ordinal>`. |
| Ownership | Dialogue Director. |
| Lifecycle | `proposed → frozen → (revised)`. |
| Parent/Child | Parent: Scene. |
| Cardinality | Zero or more per Scene. |
| Composition rules | Has one speaker; may serve as narration. |
| Traceability | Upstream: Scene, Character. Downstream: Voice Compiler. |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | Voice Compiler, PROMETHEUS. |
| Producers | Dialogue Director. |
| Validation responsibilities | Must have a speaker. |

### 2.3.21 Performance

| Field | Value |
|-------|-------|
| Purpose | The physical and vocal performance direction for a Character in a Scene: body language, facial expressions, energy, posture, micro-expressions. |
| Architectural responsibility | Carries the non-verbal performance layer that complements Dialogue and realizes the Psychology Director's emotional targets physically. |
| Identity | `com:<production-id>:performance:<scene>:<character>:<ordinal>`. |
| Ownership | Performance Director (`002` Part 2.3.6). |
| Lifecycle | `proposed → frozen → (revised)`. |
| Parent/Child | Parent: Scene. References a Character. |
| Cardinality | Zero or more per Scene per Character. |
| Composition rules | Constrained by the Character's psychology (Psychology Director); coordinates with Dialogue for verbal delivery; motivates Shot framing (close-ups on micro-expressions). |
| Traceability | Upstream: Character, Psychology, Scene. Downstream: Shot (blocking, close-up motivation), Voice Compiler (delivery subset), PROMETHEUS. |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | Cinematography Director (blocking, close-up motivation), Voice Compiler (delivery), PROMETHEUS, ORACLE (performance consistency). |
| Producers | Performance Director. |
| Validation responsibilities | Must belong to a Scene; must reference a Character; must be psychologically coherent with the Character's bible (invariant I-SI-3). |

### 2.3.22 Silence

| Field | Value |
|-------|-------|
| Purpose | An intentional absence of sound (dialogue, music, or ambient) serving a dramatic purpose. |
| Architectural responsibility | Silence is explicit, never assumed (per `001` §4.2 Pass 13 validation). |
| Identity | `com:<production-id>:silence:<scene>:<ordinal>`. |
| Ownership | Audio Director (`002` Part 2.3.12); shared with Dialogue Director (silence-as-beat). |
| Lifecycle | `proposed → frozen → (revised)`. |
| Parent/Child | Parent: Scene. |
| Cardinality | Zero or more per Scene. |
| Composition rules | Carries a silence purpose (beat, reveal, transition, emotional). |
| Traceability | Upstream: Scene. Downstream: Audio Compiler, Music Compiler (silence-as-music). |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | Audio Director, Music Director, PROMETHEUS. |
| Producers | Audio Director. |
| Validation responsibilities | Must have a purpose (silence is never "nothing"). |

### 2.3.23 Emotion

| Field | Value |
|-------|-------|
| Purpose | An emotional state, named using GO-102/GO-103 vocabulary. |
| Architectural responsibility | The atomic unit of the emotional architecture (`003` Part 3). |
| Identity | `com:<production-id>:emotion:<scene>:<ordinal>` (per-scene) or `com:<production-id>:emotion:journey:<ordinal>` (journey-level). |
| Ownership | Psychology Director. |
| Lifecycle | `proposed → frozen → (revised)`. |
| Parent/Child | Parent: Scene (per-scene) or Story (journey-level). |
| Cardinality | One or more per Scene; one Emotional Journey per Story. |
| Composition rules | Carries an intensity (normalized) and a position (by beat or act). |
| Traceability | Upstream: CIS D-4/D-5. Downstream: Music cues, lighting, color, editorial pacing. |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | Psychology Director, Music Director, Visual Director, Editorial Director. |
| Producers | Psychology Director. |
| Validation responsibilities | Must be named using GO-102/GO-103 vocabulary. |

### 2.3.24 Emotion Transition

| Field | Value |
|-------|-------|
| Purpose | The directed transition between two Emotions. |
| Architectural responsibility | The edge in the Emotion Transition Graph (`003` Part 3.2.1). |
| Identity | `com:<production-id>:emotion_transition:<from>.<to>`. |
| Ownership | Psychology Director (emotional); Editorial Director (transition shape). |
| Lifecycle | `proposed → frozen → (revised)`. |
| Parent/Child | No parent (relationship object). Connects two Emotions. |
| Cardinality | One or more per Emotional Journey. |
| Composition rules | Carries a shape (build, cut, dissolve, collapse, hold) and a contrast rating. |
| Traceability | Upstream: CIS D-5. Downstream: Transition (narrative), editorial pacing. |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | Editorial Director, Music Director. |
| Producers | Psychology Director. |
| Validation responsibilities | Must have a source and a target (invariant I-SI-7). |

### 2.3.25 Emotional Journey

| Field | Value |
|-------|-------|
| Purpose | The macro emotional arc of the production (`003` D-4). |
| Architectural responsibility | The high-level emotional contract; the container for the Emotion Transition Graph. |
| Identity | `com:<production-id>:emotional_journey:01`. |
| Ownership | Psychology Director. |
| Lifecycle | `proposed → frozen → (revised)`. |
| Parent/Child | Parent: Story. Children: Emotions, Emotion Transitions. |
| Cardinality | Exactly one per Story. |
| Composition rules | Composed from a baseline, peaks, valleys, transitions, resolution, memory. |
| Traceability | Upstream: CIS D-4, D-5. Downstream: per-scene Emotions. |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | All directors with emotional scope. |
| Producers | Psychology Director. |
| Validation responsibilities | Must have a baseline; must have a resolution; must have at least one peak and one valley unless declared monotone. |

### 2.3.26 Memory (Character)

| Field | Value |
|-------|-------|
| Purpose | A Character's recollection of a past event, represented as a narrative element. |
| Architectural responsibility | The substrate for Flashback and for psychological motivation. |
| Identity | `com:<production-id>:memory:<character>:<ordinal>`. |
| Ownership | Psychology Director. |
| Lifecycle | `proposed → frozen → (revised)`. |
| Parent/Child | Parent: Character. |
| Cardinality | Zero or more per Character. |
| Composition rules | References a past Beat or Scene (the remembered event). |
| Traceability | Upstream: Character, the remembered event. Downstream: Flashback, psychology. |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | Psychology Director, Narrative Director. |
| Producers | Psychology Director. |
| Validation responsibilities | Must belong to a Character; must reference a prior event. |

### 2.3.27 Flashback

| Field | Value |
|-------|-------|
| Purpose | A narrative device that depicts a Memory. |
| Architectural responsibility | The structural representation of a Memory in the Narrative. |
| Identity | `com:<production-id>:flashback:<scene>:<ordinal>`. |
| Ownership | Narrative Director. |
| Lifecycle | `proposed → frozen → (revised)`. |
| Parent/Child | Parent: Scene (the scene containing the flashback). |
| Cardinality | Zero or more per Scene. |
| Composition rules | References a Memory; references the original event (the past Beat/Scene). |
| Traceability | Upstream: Memory. Downstream: editorial structure. |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | Narrative Director, Editorial Director. |
| Producers | Narrative Director. |
| Validation responsibilities | Must reference a Memory; the referenced event must `precedes` the containing Scene. |

### 2.3.28 Reveal

| Field | Value |
|-------|-------|
| Purpose | The disclosure of information to the audience or to a Character. |
| Architectural responsibility | The unit of narrative information change. |
| Identity | `com:<production-id>:reveal:<ordinal>`. |
| Ownership | Narrative Director. |
| Lifecycle | `proposed → frozen → (revised)`. |
| Parent/Child | Parent: Scene (the scene of disclosure) or Story (a story-level reveal). |
| Cardinality | Zero or more per Story. |
| Composition rules | May resolve a Mystery; may be a Payoff of a Setup. |
| Traceability | Upstream: Mystery (if any), Setup (if any). Downstream: Beats. |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | Narrative Director, Psychology Director. |
| Producers | Narrative Director. |
| Validation responsibilities | If declared as a Payoff, must reference a prior Setup. |

### 2.3.29 Mystery

| Field | Value |
|-------|-------|
| Purpose | An explicit question posed to the audience. |
| Architectural responsibility | The driver of suspense (`002` Part 5.2). |
| Identity | `com:<production-id>:mystery:<ordinal>`. |
| Ownership | Narrative Director. |
| Lifecycle | `posed → resolved → frozen → (revised)`. May remain `posed` at freeze if intentionally unresolved. |
| Parent/Child | Parent: Story. |
| Cardinality | Zero or more per Story. |
| Composition rules | Resolved by a Reveal; may be set up by a Setup. |
| Traceability | Upstream: Story. Downstream: Reveal, Setup. |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | Narrative Director, Psychology Director. |
| Producers | Narrative Director. |
| Validation responsibilities | If `resolved`, must reference the resolving Reveal. |

### 2.3.30 Setup

| Field | Value |
|-------|-------|
| Purpose | An early-scene element that prepares a later Payoff. |
| Architectural responsibility | The foundation of foreshadowing. |
| Identity | `com:<production-id>:setup:<ordinal>`. |
| Ownership | Narrative Director. |
| Lifecycle | `proposed → frozen → (revised)`. |
| Parent/Child | Parent: Scene (the scene containing the setup) or Story. |
| Cardinality | Zero or more per Story. |
| Composition rules | Must `precedes` its Payoff. |
| Traceability | Upstream: Story. Downstream: Payoff. |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | Narrative Director, Editorial Director. |
| Producers | Narrative Director. |
| Validation responsibilities | Must have a corresponding Payoff (or be declared `unresolved_setup` with rationale). |

### 2.3.31 Payoff

| Field | Value |
|-------|-------|
| Purpose | A later-scene element that delivers on a prior Setup. |
| Architectural responsibility | The fulfillment of foreshadowing. |
| Identity | `com:<production-id>:payoff:<ordinal>`. |
| Ownership | Narrative Director. |
| Lifecycle | `proposed → frozen → (revised)`. |
| Parent/Child | Parent: Scene. |
| Cardinality | Zero or more per Story. |
| Composition rules | Must `references` a prior Setup. |
| Traceability | Upstream: Setup. Downstream: Reveal (if the payoff is also a reveal). |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | Narrative Director, Psychology Director. |
| Producers | Narrative Director. |
| Validation responsibilities | Must reference a prior Setup (invariant I-SI-5). |

### 2.3.32 Foreshadowing

| Field | Value |
|-------|-------|
| Purpose | The narrative technique of implying a future event; the relationship between a Setup and its Payoff. |
| Architectural responsibility | A relationship object, not a content object. |
| Identity | `com:<production-id>:foreshadowing:<setup>.<payoff>`. |
| Ownership | Narrative Director. |
| Lifecycle | `proposed → frozen → (revised)`. |
| Parent/Child | No parent (relationship object). Connects Setup and Payoff. |
| Cardinality | Zero or more per Story. |
| Composition rules | References a Setup and a Payoff. |
| Traceability | Upstream: Setup, Payoff. Downstream: narrative reasoning. |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | Narrative Director. |
| Producers | Narrative Director. |
| Validation responsibilities | The Setup must `precedes` the Payoff. |

### 2.3.33 Callback

| Field | Value |
|-------|-------|
| Purpose | A later-scene element that explicitly references an earlier event, line, or image. |
| Architectural responsibility | The structural unit of narrative echoing. |
| Identity | `com:<production-id>:callback:<ordinal>`. |
| Ownership | Narrative Director. |
| Lifecycle | `proposed → frozen → (revised)`. |
| Parent/Child | Parent: Scene (the scene containing the callback). |
| Cardinality | Zero or more per Story. |
| Composition rules | Must `references` a prior Beat, Scene, Dialogue, or Motif. |
| Traceability | Upstream: the referenced prior element. Downstream: narrative reasoning. |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | Narrative Director, Psychology Director. |
| Producers | Narrative Director. |
| Validation responsibilities | Must reference an earlier element (invariant I-SI-6). |

### 2.3.34 Motif

| Field | Value |
|-------|-------|
| Purpose | A recurring element (visual, sonic, narrative) that accrues meaning through repetition. |
| Architectural responsibility | The carrier of thematic resonance. |
| Identity | `com:<production-id>:motif:<ordinal>`. |
| Ownership | Visual Director (visual motifs), Audio Director (sonic motifs), Narrative Director (narrative motifs). |
| Lifecycle | `proposed → frozen → (revised)`. |
| Parent/Child | Parent: Story. |
| Cardinality | Zero or more per Story. |
| Composition rules | Must appear multiple times (invariant I-SI-10); must `references` a Theme. |
| Traceability | Upstream: Theme. Downstream: Shots, Music cues, Beats. |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | All directors with motif scope. |
| Producers | The owning director per motif type. |
| Validation responsibilities | Must appear multiple times; must reference a Theme. |

### 2.3.35 Symbol

| Field | Value |
|-------|-------|
| Purpose | An element that stands for something beyond its literal self. |
| Architectural responsibility | The carrier of symbolic meaning. |
| Identity | `com:<production-id>:symbol:<ordinal>`. |
| Ownership | Visual Director (visual symbols), Narrative Director (narrative symbols). |
| Lifecycle | `proposed → frozen → (revised)`. |
| Parent/Child | Parent: Story. |
| Cardinality | Zero or more per Story. |
| Composition rules | Must `references` a Theme. |
| Traceability | Upstream: Theme. Downstream: Shots, Beats. |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | Visual Director, Narrative Director. |
| Producers | The owning director per symbol type. |
| Validation responsibilities | Must reference a Theme. |

### 2.3.36 Visual Language

| Field | Value |
|-------|-------|
| Purpose | The overarching visual philosophy of the production. |
| Architectural responsibility | Carries camera philosophy, color language, composition principles, visual metaphors. |
| Identity | `com:<production-id>:visual_language:01`. |
| Ownership | Visual Director (`002` Part 2.3.8). |
| Lifecycle | `proposed → frozen → (revised)`. |
| Parent/Child | Parent: Story. Children: per-scene camera/lighting/production design projections. |
| Cardinality | Exactly one per Story. |
| Composition rules | Derived from the Story, Theme, and CIS D-17 Visual Expectations. |
| Traceability | Upstream: Story, Theme, CIS D-17. Downstream: Shots, Lighting, Production Design. |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | Cinematography Director, Lighting Director, Production Designer. |
| Producers | Visual Director. |
| Validation responsibilities | Must have a camera philosophy; must have a color language. |

### 2.3.37 Shot

| Field | Value |
|-------|-------|
| Purpose | The atomic unit of visual rendering. |
| Architectural responsibility | Carries framing, camera movement, lens, composition, blocking. |
| Identity | `com:<production-id>:shot:<scene>.<shot>`. |
| Ownership | Cinematography Director. |
| Lifecycle | `proposed → frozen → (revised)`. |
| Parent/Child | Parent: Scene. |
| Cardinality | One or more per Scene. |
| Composition rules | Motivated by a Beat or a Moment (camera motivation, `002` Part 5.2). |
| Traceability | Upstream: Scene, Beat. Downstream: PKP Shot Specification, PROMETHEUS Image Realization. |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | PROMETHEUS, ORACLE (visual consistency). |
| Producers | Cinematography Director. |
| Validation responsibilities | Must belong to exactly one Scene (invariant I-SI-9); must have a motivation. |

### 2.3.38 Camera

| Field | Value |
|-------|-------|
| Purpose | The camera direction for a Shot (lens, movement, angle, framing). |
| Architectural responsibility | The visual point of view and motion. |
| Identity | `com:<production-id>:camera:<scene>.<shot>`. |
| Ownership | Cinematography Director. |
| Lifecycle | `proposed → frozen → (revised)`. |
| Parent/Child | Parent: Shot. |
| Cardinality | Exactly one per Shot. |
| Composition rules | Constrained by Visual Language; motivated by Beat/Moment. |
| Traceability | Upstream: Shot, Visual Language. Downstream: PKP camera spec. |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | PROMETHEUS. |
| Producers | Cinematography Director. |
| Validation responsibilities | Must have a movement type; must have a framing. |

### 2.3.39 Lighting

| Field | Value |
|-------|-------|
| Purpose | The lighting direction for a Scene or Shot. |
| Architectural responsibility | Carries lighting style, palette, mood, atmosphere, time of day. |
| Identity | `com:<production-id>:lighting:<scene>.<ordinal>`. |
| Ownership | Lighting Director. |
| Lifecycle | `proposed → frozen → (revised)`. |
| Parent/Child | Parent: Scene. |
| Cardinality | One or more per Scene. |
| Composition rules | Constrained by Visual Language; serves the scene's Emotion. |
| Traceability | Upstream: Visual Language, Emotion. Downstream: PKP lighting spec. |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | PROMETHEUS, ORACLE (continuity). |
| Producers | Lighting Director. |
| Validation responsibilities | Must have a lighting style; must have a mood. |

### 2.3.40 Environment

| Field | Value |
|-------|-------|
| Purpose | The world-state in which a Scene takes place. |
| Architectural responsibility | Carries the environmental context: weather, time, atmosphere, social setting. |
| Identity | `com:<production-id>:environment:<scene>:<ordinal>`. |
| Ownership | Production Designer. |
| Lifecycle | `proposed → frozen → (revised)`. |
| Parent/Child | Parent: Scene. |
| Cardinality | One or more per Scene. |
| Composition rules | References a Location; carries environmental attributes. |
| Traceability | Upstream: Location, Production Design. Downstream: Lighting, Camera, PROMETHEUS. |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | Lighting Director, Cinematography Director, PROMETHEUS. |
| Producers | Production Designer. |
| Validation responsibilities | Must reference a Location. |

### 2.3.41 Location

| Field | Value |
|-------|-------|
| Purpose | A reusable place in the world. |
| Architectural responsibility | The spatial identity for cross-scene continuity and for ATLAS reuse. |
| Identity | `com:<production-id>:location:<ordinal>`; cross-production identity via ATLAS (`002` Part 6.2). |
| Ownership | Production Designer. |
| Lifecycle | `proposed → frozen → (revised)`. |
| Parent/Child | Parent: Story. |
| Cardinality | One or more per Story. |
| Composition rules | May be reused across Scenes; carries visual and acoustic identity. |
| Traceability | Upstream: Story, World (PKP-05). Downstream: Environments. |
| Versioning | GFS-003. Cross-production reuse via ATLAS. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | Production Designer, Continuity Director, PROMETHEUS. |
| Producers | Production Designer. |
| Validation responsibilities | Must have a visual identity; must have an acoustic identity. |

### 2.3.42 Music Theme

| Field | Value |
|-------|-------|
| Purpose | A recurring musical identity (a leitmotif, a thematic motif). |
| Architectural responsibility | The carrier of musical-thematic meaning. |
| Identity | `com:<production-id>:music_theme:<ordinal>`. |
| Ownership | Music Director. |
| Lifecycle | `proposed → frozen → (revised)`. |
| Parent/Child | Parent: Story. |
| Cardinality | Zero or more per Story. |
| Composition rules | Associated with a Character, a Theme, or an Emotion. |
| Traceability | Upstream: Character, Theme, Emotion. Downstream: Music cues. |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | Music Director, PROMETHEUS Music Realization. |
| Producers | Music Director. |
| Validation responsibilities | If associated with a Character or Theme, must `references` that object. |

### 2.3.43 Soundscape

| Field | Value |
|-------|-------|
| Purpose | The sonic environment of a Scene. |
| Architectural responsibility | Carries ambient sound, SFX, and the non-musical sonic identity. |
| Identity | `com:<production-id>:soundscape:<scene>:<ordinal>`. |
| Ownership | Sound Director. |
| Lifecycle | `proposed → frozen → (revised)`. |
| Parent/Child | Parent: Scene. |
| Cardinality | One or more per Scene. |
| Composition rules | Includes Silence objects (silence is explicit, `002` Part 5.2). |
| Traceability | Upstream: Scene, Environment. Downstream: PKP audio spec, PROMETHEUS Audio Assembly. |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | PROMETHEUS, ORACLE (audio quality). |
| Producers | Sound Director. |
| Validation responsibilities | Must include explicit Silence objects where silence is intended. |

### 2.3.44 Timeline

| Field | Value |
|-------|-------|
| Purpose | The temporal arrangement of all Scenes and their parallel tracks. |
| Architectural responsibility | The master temporal structure. |
| Identity | `com:<production-id>:timeline:01`. |
| Ownership | Editorial Director. |
| Lifecycle | `proposed → frozen → (revised)`. |
| Parent/Child | Parent: Production. Children: Runtime Segments. |
| Cardinality | Exactly one per Production. |
| Composition rules | Composed from Runtime Segments; carries parallel tracks (video, audio, music, SFX, subtitle). |
| Traceability | Upstream: Scenes, Shots, Music, Audio, Voice. Downstream: PKP timeline, PROMETHEUS. |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | PROMETHEUS, ORACLE. |
| Producers | Editorial Director (via Timeline Compiler, `001` Pass 15). |
| Validation responsibilities | Total runtime within profile policy; every Scene has a duration. |

### 2.3.45 Runtime Segment

| Field | Value |
|-------|-------|
| Purpose | A timed segment within the Timeline. |
| Architectural responsibility | The atomic unit of the rendered timeline. |
| Identity | `com:<production-id>:runtime_segment:<ordinal>`. |
| Ownership | Editorial Director. |
| Lifecycle | `proposed → frozen → (revised)`. |
| Parent/Child | Parent: Timeline. |
| Cardinality | One or more per Timeline. |
| Composition rules | Carries start, end, duration, transition duration, track assignments. |
| Traceability | Upstream: Scene. Downstream: PROMETHEUS. |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | PROMETHEUS. |
| Producers | Editorial Director. |
| Validation responsibilities | Durations must sum to total runtime. |

### 2.3.46 Audience

| Field | Value |
|-------|-------|
| Purpose | The target audience of the production (`003` D-6). |
| Architectural responsibility | The audience model that shapes realization without redefining intent (`003` I-AD-1). |
| Identity | `com:<production-id>:audience:01`. |
| Ownership | Platform Director (`002` Part 2.3.16). |
| Lifecycle | `proposed → frozen → (revised)`. |
| Parent/Child | Parent: Production. |
| Cardinality | Exactly one per Production. |
| Composition rules | Composed from the seven audience dimensions (`003` Part 4.2). |
| Traceability | Upstream: CIS D-6. Downstream: all directors (adaptation). |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | All directors (for adaptation); Platform Director. |
| Producers | Platform Director. |
| Validation responsibilities | Must address all seven audience dimensions. |

### 2.3.47 Experience

| Field | Value |
|-------|-------|
| Purpose | The intended audience experience as a whole. |
| Architectural responsibility | The integration of Emotional Journey, Audience, and Reflection into a single experience contract. |
| Identity | `com:<production-id>:experience:01`. |
| Ownership | Chief Director. |
| Lifecycle | `proposed → frozen → (revised)`. |
| Parent/Child | Parent: Production. |
| Cardinality | Exactly one per Production. |
| Composition rules | References the Emotional Journey, the Audience, and the Reflection. |
| Traceability | Upstream: Emotional Journey, Audience, Reflection. Downstream: validation, archival. |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | Chief Director, ORACLE (experience validation). |
| Producers | Chief Director. |
| Validation responsibilities | Must be consistent with Emotional Journey and Reflection. |

### 2.3.48 Reflection

| Field | Value |
|-------|-------|
| Purpose | What the audience should reflect on after the work ends (`003` D-21). |
| Architectural responsibility | The post-viewing cognitive/affective target. |
| Identity | `com:<production-id>:reflection:01`. |
| Ownership | Chief Director. |
| Lifecycle | `proposed → frozen → (revised)`. |
| Parent/Child | Parent: Production. |
| Cardinality | Zero or one per Production (`none` is valid). |
| Composition rules | Derived from CIS D-21; consistent with Message and Ending Intent. |
| Traceability | Upstream: CIS D-21, Message, Ending Intent. Downstream: Experience, ORACLE. |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | Chief Director, Psychology Director. |
| Producers | Chief Director. |
| Validation responsibilities | Must be consistent with Message (not contradictory). |

### 2.3.49 Learning Objective

| Field | Value |
|-------|-------|
| Purpose | An observable, falsifiable educational outcome (`003` D-7). |
| Architectural responsibility | The educational contract; `none` for non-educational works. |
| Identity | `com:<production-id>:learning_objective:<ordinal>` or `com:<production-id>:learning_objective:none`. |
| Ownership | Story Director (content); Narrative Director (delivery). |
| Lifecycle | `proposed → frozen → (revised)`. |
| Parent/Child | Parent: Production. |
| Cardinality | Zero or more per Production. |
| Composition rules | Derived from CIS D-7; validated against CIS D-22 Educational Fidelity constraints. |
| Traceability | Upstream: CIS D-7, D-22. Downstream: Story, Narrative. |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | Story Director, Narrative Director, ORACLE (educational fidelity). |
| Producers | Story Director. |
| Validation responsibilities | Must be observable and falsifiable (per `003` D-7). |

### 2.3.50 Creative Constraint

| Field | Value |
|-------|-------|
| Purpose | A constraint the production must honor (`003` D-22). |
| Architectural responsibility | The enforcement of ethical, historical, brand, platform, religious, and production boundaries. |
| Identity | `com:<production-id>:constraint:<class>:<ordinal>`. |
| Ownership | The director whose scope the constraint class falls under (per `003` Part 5.2). |
| Lifecycle | `authored → validated → frozen → (revised)`. Authored at CIS time; validated at CIS validation; frozen at CIR freeze. |
| Parent/Child | Parent: Production. |
| Cardinality | Zero or more per Production. |
| Composition rules | Carries a class, a precedence (`003` Part 5.3), and an enforcement scope. |
| Traceability | Upstream: CIS D-22. Downstream: all directors (constraint consumers), ORACLE. |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | All directors; Compiler passes; PROMETHEUS; ORACLE. |
| Producers | Human (authored); CIS Validator (validated). |
| Validation responsibilities | Enforced at validation; violations are blocking (`003` Part 8.2). |

### 2.3.51 Presentation Profile

| Field | Value |
|-------|-------|
| Purpose | The creator's presentation preferences (`003` D-23). |
| Architectural responsibility | Execution-influencing preferences, not intent (`003` I-PP-1). |
| Identity | `com:<production-id>:presentation_profile:01`. |
| Ownership | Human (authored); PROMETHEUS (consumer). |
| Lifecycle | `authored → validated → frozen → (revised)`. |
| Parent/Child | Parent: Production. |
| Cardinality | Exactly one per Production. |
| Composition rules | Composed from the eight presentation domains (`003` Part 6.2). |
| Traceability | Upstream: CIS D-23. Downstream: PROMETHEUS execution. |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | PROMETHEUS (execution guidance); ORACLE (soft validation). |
| Producers | Human. |
| Validation responsibilities | Must not contradict intent domains (`003` Part 6.3). |

### 2.3.52 Creative Intent

| Field | Value |
|-------|-------|
| Purpose | The human-authored statement of what the creator wants, as a structured object. |
| Architectural responsibility | The CIS, as a COM object. The root of the intent layer. |
| Identity | `com:<production-id>:creative_intent:<version>`. |
| Ownership | Human. |
| Lifecycle | `draft → validated → approved → pinned → (revised)` (`003` Part 8.3). |
| Parent/Child | Parent: Production. Children: all CIS domain objects (Story Intent, Theme, etc.). |
| Cardinality | Exactly one per Production (per version). |
| Composition rules | Composed from the 24 CIS domains (`003` Part 2.2). |
| Traceability | Upstream: human author. Downstream: Creative Decisions (in the CIR). |
| Versioning | `003` Part 10.2.1. |
| Immutability rules | Pinned at approval (`003` Part 8.3). |
| Consumers | Directorial Board. |
| Producers | Human. |
| Validation responsibilities | Must pass CIS validation (`003` Part 8). |

### 2.3.53 Creative Decision

| Field | Value |
|-------|-------|
| Purpose | A single creative decision made by the Directorial Board, with full reasoning (`002` Part 3). |
| Architectural responsibility | The unit of creative reasoning. The CIR is a graph of Creative Decisions. |
| Identity | `cir:<production-id>:<director-slug>:<node-type>:<ordinal>` (per `002` Part 12.4). |
| Ownership | The home director (`002` Part 2.3). |
| Lifecycle | `idea → research → context → alternatives → tradeoff → selected → reviewed → recorded → frozen` (`002` Part 3.1). |
| Parent/Child | Parent: CIR root. Children: none (it references COM objects as subjects). |
| Cardinality | Many per Production. |
| Composition rules | Carries provenance, confidence, rationale, evidence, alternatives, assumptions (`002` Part 3.2). |
| Traceability | Upstream: Creative Intent (the CIS domain it reasons from). Downstream: the COM object it authorizes (e.g., a Scene, a Shot). |
| Versioning | GFS-003. |
| Immutability rules | Frozen at CIR freeze. |
| Consumers | Compiler passes; ORACLE (drift detection against the decision's intent). |
| Producers | The Directorial Board. |
| Validation responsibilities | Must have provenance (invariant I-SI-14); must have a home director. |

### 2.3.54 Creative Artifact

| Field | Value |
|-------|-------|
| Purpose | A produced artifact of the production (a PKP artifact, a media file, a validation report). |
| Architectural responsibility | The output side of the pipeline. |
| Identity | `com:<production-id>:artifact:<type>:<ordinal>`. |
| Ownership | The producing subsystem (Compiler for PKP artifacts; PROMETHEUS for media; ORACLE for reports). |
| Lifecycle | `produced → validated → archived`. |
| Parent/Child | Parent: Production. |
| Cardinality | Many per Production. |
| Composition rules | Each artifact carries `cir_origin` (per `002` Part 7.2) and `cis_origin` (transitively). |
| Traceability | Upstream: Creative Decision. Downstream: ATLAS archive, ORACLE validation. |
| Versioning | GFS-003. |
| Immutability rules | Frozen at production. |
| Consumers | ATLAS, ORACLE, human (review). |
| Producers | Compiler, PROMETHEUS, ORACLE. |
| Validation responsibilities | Must carry `cir_origin` (I-TC-1, `002` Part 7.2). |

### 2.3.55 Creative Version

| Field | Value |
|-------|-------|
| Purpose | An immutable version of a COM object or artifact, per GFS-003. |
| Architectural responsibility | The unit of revision and replay. |
| Identity | `<object-identity>@<revision-ordinal>`. |
| Ownership | The owning director or subsystem. |
| Lifecycle | `created → (superseded)`. |
| Parent/Child | No parent. |
| Cardinality | One per revision. |
| Composition rules | References the prior version it amends (`amends` edge). |
| Traceability | Upstream: the prior version. Downstream: the next version, if any. |
| Versioning | Is the version. |
| Immutability rules | Always immutable (GFS-003). |
| Consumers | All subsystems (for replay, audit, revision). |
| Producers | The owning subsystem. |
| Validation responsibilities | Must carry the prior version reference (if not the first). |

### 2.3.56 Creative Branch

| Field | Value |
|-------|-------|
| Purpose | A divergent line of creative development from a source version (`003` Part 10.2.2). |
| Architectural responsibility | The unit of parallel creative exploration. |
| Identity | `com:<production-id>:branch:<ordinal>`. |
| Ownership | Human. |
| Lifecycle | `branched → authored → (merged-or-abandoned)`. |
| Parent/Child | No parent (references a source version via `branched_from`). |
| Cardinality | Zero or more per Production. |
| Composition rules | References a source version; independent lifecycle. |
| Traceability | Upstream: the branched-from version. Downstream: its own versions. |
| Versioning | Independent of the source. |
| Immutability rules | The branch point is immutable; the branch's own versions are independently immutable. |
| Consumers | Human; Directorial Board (for the branch's CIR). |
| Producers | Human. |
| Validation responsibilities | Must carry `branched_from` reference. |

---

# PART 3: CREATIVE RELATIONSHIP MODEL

---

## 3.1 Relationship Specification Contract

Every legal relationship between Creative Objects is specified by an eleven-field contract, extending the GO-002 specification model with COM-specific lifecycle and ownership semantics. The COM Relationship Model is **not** a replacement for GO-002; it is the COM's binding of GO-002 predicates to COM object types with lifecycle and ownership semantics.

| Field | Definition |
|-------|-----------|
| **Canonical name** | The predicate name (from GO-002 where available). |
| **Directionality** | Unidirectional or bidirectional. |
| **Cardinality** | One-to-one, one-to-many, many-to-many. |
| **Domain** | The valid source object types (from Part 2.2). |
| **Range** | The valid target object types. |
| **Inverse** | The canonical inverse, if any. |
| **Ownership** | Which director owns the relationship's semantics. |
| **Lifecycle implication** | Whether the relationship affects lifecycle state (e.g., `depends_on` blocks freeze). |
| **Validation rule** | The invariant(s) the relationship enforces (Part 5). |
| **Examples** | Concrete instances. |

## 3.2 Relationship Catalog

The COM recognizes the following relationships. Names align with GO-002 where GO-002 defines the predicate; COM-specific relationships are marked.

| Relationship | Directionality | Cardinality | Domain → Range | Inverse | Owner | Lifecycle | Validation | Examples |
|--------------|---------------|-------------|----------------|---------|-------|-----------|------------|----------|
| **contains** | Unidirectional | 1-to-many | Parent → Child (composition) | `part_of` | The parent's owner | A child cannot be frozen before its parent | A child has exactly one parent (where cardinality mandates) | Story contains Acts; Scene contains Beats |
| **references** | Unidirectional | many-to-many | Any → Any | `referenced_by` | The source's owner | None | The referenced object must exist | Callback references prior Beat; Symbol references Theme |
| **depends_on** | Unidirectional | many-to-many | Any → Any | `required_by` | The source's owner | The dependent cannot be frozen before its dependency | The dependency must be frozen first (I-SI-15) | Shot depends_on Beat; Payoff depends_on Setup |
| **causes** | Unidirectional | many-to-many | Event/Decision → Event/Beat | `caused_by` | Narrative Director | None | The cause must precedes the effect | Character Decision causes a Beat |
| **creates** | Unidirectional | many-to-many | Director/Character → Object | `created_by` | The creator's owner | None | The creator must exist | Character creates Goal; Director creates Creative Decision |
| **resolves** | Unidirectional | many-to-many | Reveal/Payoff/Decision → Mystery/Conflict/Setup | `resolved_by` | Narrative Director | None | The resolved object must exist | Reveal resolves Mystery; Payoff resolves Setup |
| **transitions_to** | Unidirectional | 1-to-many | Emotion/Scene/Sequence → Emotion/Scene/Sequence | `transitioned_from` | Psychology Director / Editorial Director | None | The source must precedes the target (I-SI-7) | Emotion transitions_to Emotion; Scene transitions_to Scene |
| **mirrors** | Bidirectional | many-to-many | Any → Any | (symmetric) | The owner of the initiating object | None | Both objects must exist | Scene mirrors Scene (structural echo) |
| **contrasts** | Bidirectional | many-to-many | Any → Any | (symmetric) | The owner of the initiating object | None | Both objects must exist | Emotion contrasts Emotion; Visual Language contrasts Visual Language |
| **echoes** | Unidirectional | many-to-many | Any → Any | `echoed_by` | Narrative Director | None | The echoed object must precedes the echoing object | Callback echoes prior Motif |
| **extends** | Unidirectional | many-to-many | Any → Any | `extended_by` | The source's owner | None | The extended object must exist | Motif extends Motif |
| **specializes** | Unidirectional | 1-to-many | General → Specific | `specialized_by` | The source's owner | None | The general must exist | Symbol specializes Motif |
| **inherits** | Unidirectional | many-to-many | Child → Parent (constraint inheritance) | `inherited_by` | The parent's owner | None | The parent must be frozen first | Scene inherits Visual Language constraints |
| **precedes** | Unidirectional | many-to-many | Temporal object → Temporal object | `follows` | Narrative Director / Editorial Director | None | The source must not follow the target (I-SI-15) | Scene precedes Scene; Beat precedes Beat |
| **follows** | Unidirectional | many-to-many | Temporal object → Temporal object | `precedes` | Narrative Director / Editorial Director | None | The source must not precede the target | Scene follows Scene (inverse of precedes) |
| **belongs_to** | Unidirectional | many-to-1 | Child → Parent | `owns` | The parent's owner | None | The parent must exist | Beat belongs_to Scene; Shot belongs_to Scene |
| **produces** | Unidirectional | many-to-many | Producer → Artifact | `produced_by` | The producer's owner | None | The artifact must carry the producer's `cir_origin` | Director produces Creative Decision; Compiler produces PKP Artifact |
| **consumes** | Unidirectional | many-to-many | Consumer → Input | `consumed_by` | The consumer's owner | None | The input must be frozen | Compiler consumes CIR; PROMETHEUS consumes PKP |
| **validates** | Unidirectional | many-to-many | Validator → Object/Artifact | `validated_by` | ORACLE | None | The validation report references the object | ORACLE validates Media; Quality Director validates CIR |
| **learns_from** | Unidirectional | many-to-many | Director → Archived Object | `learned_by` | The learning director | None | The archived object must be `archived` | Story Director learns_from prior Story |
| **archives** | Unidirectional | many-to-1 | ATLAS → Object/Artifact | `archived_by` | ATLAS | Transitions the object to `archived` | The object must be frozen | ATLAS archives CIR |
| **motivates** (COM-specific) | Unidirectional | many-to-many | Beat/Moment/Emotion → Shot/Camera/Music/Lighting | `motivated_by` | The source's owner | None | The motivated object must reference its motivation | Beat motivates Shot; Emotion motivates Lighting |
| **constrains** (COM-specific) | Unidirectional | many-to-many | Creative Constraint → Any | `constrained_by` | The constraint's owner | None | The constrained object must satisfy the constraint | Ethical Constraint constrains Scene |
| **authorizes** (COM-specific) | Unidirectional | many-to-many | Creative Decision → COM Object | `authorized_by` | The decision's home director | The authorized object cannot be frozen before the authorizing decision | The object must carry `cir_origin` | Creative Decision authorizes Scene |
| **adapts_to** (COM-specific) | Unidirectional | many-to-1 | Any → Audience | `adapted_by` | Platform Director | None | The adaptation must not redefine intent (I-AD-1, `003`) | Scene adapts_to Audience |

Relationships not in this catalog may not be used between COM objects. New relationships are added under governance (Part 10.2).

---

# PART 4: CREATIVE OPERATIONS

---

## 4.1 Operation Classification

Operations are mutations on COM objects. Every operation is classified by its **intent-preservation** (does it preserve the CIS's intent?) and its **authority requirement** (who must approve it?).

| Class | Definition | Intent preserved? | Authority |
|-------|-----------|-------------------|-----------|
| **Structural** | Reorganizes objects without changing their semantic content. | Yes | Director approval. |
| **Emotional** | Modifies the emotional architecture. | Depends — may require CIS amendment if the Emotional Journey changes. | Director approval; human approval if CIS-amending. |
| **Narrative** | Adds, removes, or restructures narrative elements. | Depends — may require CIS amendment if Story/Ending Intent changes. | Director approval; human approval if CIS-amending. |
| **Temporal** | Modifies the timeline or runtime. | Yes, within the CIS D-10 runtime envelope. | Director approval. |
| **Adaptation** | Adapts realization to audience/platform/locale without changing intent. | Yes (I-AD-1). | Director approval. |
| **Versioning** | Creates, branches, rolls back, or restores versions. | Yes (versions are immutable; rollback restores a prior version). | Director approval; human approval for branch creation. |
| **Lifecycle** | Freezes, archives, deprecates. | Yes. | Authority per the object's owner. |

## 4.2 Operation Catalog

| Operation | Class | Acts on | Effect | Invalidates CIR? | Invalidates PKP? | Requires regeneration? |
|-----------|-------|---------|--------|------------------|------------------|------------------------|
| **Create** | Structural | Any | Creates a new object instance. | Yes (if post-freeze) | Yes (if post-freeze) | Yes |
| **Delete** | Structural | Any | Removes an object; its relationships must be re-resolved. | Yes | Yes | Yes |
| **Split** | Structural | Scene, Beat, Act, Sequence | Divides one object into two or more. | Yes | Yes | Yes |
| **Merge** | Structural | Scene, Beat, Act, Sequence | Combines two or more into one. | Yes | Yes | Yes |
| **Replace** | Structural | Any | Substitutes one object for another. | Yes | Yes | Yes |
| **Duplicate** | Structural | Any | Creates a copy (for branching). | No (creates a new instance in a new branch) | No | No |
| **Branch** | Versioning | Creative Version, Production | Creates a divergent line. | No (the source is unaffected) | No | No |
| **Freeze** | Lifecycle | Any freezable | Makes the object immutable. | No (it is the freeze) | No | No |
| **Archive** | Lifecycle | Any | Transitions to `archived`; persisted by ATLAS. | No | No | No |
| **Restore** | Versioning | Creative Version | Restores a prior version as the current. | Yes (replaces current) | Yes | Yes |
| **Escalate Emotion** | Emotional | Emotion, Emotion Transition | Increases intensity or sharpens contrast. | Yes (if it changes the Emotional Journey) | Yes | Yes |
| **Reduce Tension** | Emotional | Emotion, Emotion Transition | Decreases intensity. | Yes (if it changes the Emotional Journey) | Yes | Yes |
| **Insert Beat** | Narrative | Scene | Adds a Beat to a Scene. | Yes | Yes | Yes |
| **Delete Beat** | Narrative | Scene | Removes a Beat. | Yes | Yes | Yes |
| **Insert Scene** | Narrative | Sequence | Adds a Scene. | Yes | Yes | Yes |
| **Merge Scenes** | Structural | Scene | Combines two Scenes. | Yes | Yes | Yes |
| **Shift POV** | Narrative | Camera, Shot | Changes the point of view. | Yes (if it changes Visual Language) | Yes | Yes |
| **Add Reveal** | Narrative | Story, Scene | Adds a Reveal. | Yes | Yes | Yes |
| **Remove Reveal** | Narrative | Story, Scene | Removes a Reveal; its Mystery must be re-resolved. | Yes | Yes | Yes |
| **Insert Callback** | Narrative | Scene | Adds a Callback; must reference a prior element. | Yes | Yes | Yes |
| **Resolve Conflict** | Narrative | Conflict | Marks the Conflict resolved. | Yes (if it changes Story) | Yes | Yes |
| **Compress Runtime** | Temporal | Timeline, Runtime Segment | Reduces total runtime; must stay within CIS D-10 envelope. | Yes (if it breaks the envelope) | Yes | Yes |
| **Expand Runtime** | Temporal | Timeline, Runtime Segment | Increases total runtime; must stay within envelope. | Yes (if it breaks the envelope) | Yes | Yes |
| **Localize** | Adaptation | Dialogue, Visual Language, Symbol | Adapts for a locale; must not localize non-localizable elements (`003` D-16). | No (adaptation, not intent change) | Yes (PKP is recompiled for the locale) | Yes (for the locale) |
| **Translate** | Adaptation | Dialogue, Monologue | Translates language; per CIS D-14. | No | Yes | Yes |
| **Adapt** | Adaptation | Any | Adapts realization to Audience (`003` I-AD-1). | No | Yes | Yes |
| **Version** | Versioning | Any | Creates a new immutable version (GFS-003). | No (creates a new version; does not mutate the prior) | No | No |
| **Rollback** | Versioning | Creative Version | Restores a prior version. | Yes (replaces current) | Yes | Yes |

## 4.3 Operation Authority Matrix

| Operation | Director approval | Human approval | CIS amendment required |
|-----------|------------------|----------------|------------------------|
| Create, Delete, Split, Merge, Replace (pre-freeze) | Yes | No | No |
| Create, Delete, Split, Merge, Replace (post-freeze) | Yes | Yes | If intent-changing |
| Branch | Yes (Chief Director) | Yes | No |
| Freeze | Yes (object owner) | No (unless high-stakes, per `002` Part 8.2.5) | No |
| Archive | Yes (ATLAS, on Director request) | No | No |
| Restore, Rollback | Yes | Yes | If intent-changing |
| Escalate/Reduce Emotion | Yes | Yes if Emotional Journey changes | Yes if Emotional Journey changes |
| Insert/Delete Beat, Insert Scene, Merge Scenes | Yes | Yes if Story changes | Yes if Story changes |
| Shift POV | Yes (Cinematography + Visual) | Yes if Visual Language changes | Yes if Visual Language changes |
| Add/Remove Reveal, Insert Callback, Resolve Conflict | Yes (Narrative) | Yes if Story changes | Yes if Story changes |
| Compress/Expand Runtime | Yes (Editorial + Platform) | Yes if envelope broken | Yes if envelope broken |
| Localize, Translate, Adapt | Yes | No | No |
| Version | Yes (object owner) | No | No |

The matrix operationalizes `002` Part 8 (conflict resolution) and `003` Part 7.4 (human approval) at the operation level.

---

# PART 5: SEMANTIC INVARIANTS

---

## 5.1 Invariant Classification

Semantic invariants are rules that must always hold for the COM to be valid. They are enforced at three points:

1. **At authoring** (CIS validation, `003` Part 8) — for intent-side invariants.
2. **At freeze** (CIR freeze, `002` Part 12.2) — for reasoning-side invariants.
3. **At validation** (ORACLE, `001` §2.1) — for media-side invariants.

Invariants are classified by severity:

- **Blocking**: violation prevents freeze or invalidates the production.
- **Warning**: violation is flagged for review but does not block.
- **Advisory**: violation is recorded for learning but does not block.

All invariants below are **blocking** unless marked otherwise.

## 5.2 Invariant Catalog

| ID | Invariant | Enforced at | Owner |
|----|-----------|-------------|-------|
| I-SI-1 | Every Scene has a Purpose. | CIR freeze | Story Director |
| I-SI-2 | Every Beat belongs to exactly one Scene. | CIR freeze | Narrative Director |
| I-SI-3 | Every Character has a Motivation (Goal or Need). | CIR freeze | Character Director |
| I-SI-4 | Every Reveal has a Setup (if declared as a Payoff-bearing Reveal). | CIR freeze | Narrative Director |
| I-SI-5 | Every Payoff references a prior Setup. | CIR freeze | Narrative Director |
| I-SI-6 | Every Callback references an earlier element. | CIR freeze | Narrative Director |
| I-SI-7 | Every Emotion Transition has a source and a target. | CIR freeze | Psychology Director |
| I-SI-8 | Every Dialogue has a speaker. | CIR freeze | Dialogue Director |
| I-SI-9 | Every Shot belongs to exactly one Scene. | CIR freeze | Cinematography Director |
| I-SI-10 | Every Transition connects two valid narrative states. | CIR freeze | Editorial Director |
| I-SI-11 | Every Motif appears multiple times. | CIR freeze | The motif's owner |
| I-SI-12 | Every Conflict has at least one participant. | CIR freeze | Narrative Director |
| I-SI-13 | Every Goal belongs to an Actor (Character or entity). | CIR freeze | Character Director |
| I-SI-14 | Every Creative Decision has provenance. | CIR freeze | Chief Director |
| I-SI-15 | Every `depends_on` edge points to a frozen object before the dependent freezes. | CIR freeze | Chief Director |
| I-SI-16 | Every `precedes` edge is consistent with the Timeline. | CIR freeze | Editorial Director |
| I-SI-17 | Every Symbol references a Theme. | CIR freeze | Visual Director |
| I-SI-18 | Every Visual Motif references a Theme. | CIR freeze | Visual Director |
| I-SI-19 | Every Silence has a purpose. | CIR freeze | Audio Director |
| I-SI-20 | Every Shot has a motivation (references a Beat or Moment via `motivates`). | CIR freeze | Cinematography Director |
| I-SI-21 | Every Creative Artifact carries `cir_origin`. | Compilation | Compiler |
| I-SI-22 | Every Character has a visual identity and a voice identity (if speaking). | CIR freeze | Character Director |
| I-SI-23 | Every Scene has a duration. | CIR freeze | Editorial Director |
| I-SI-24 | Every Act has an objective. | CIR freeze | Narrative Director |
| I-SI-25 | Every Sequence has an objective. | CIR freeze | Narrative Director |
| I-SI-26 | Every Emotional Journey has a baseline, at least one peak, at least one valley (unless declared monotone), and a resolution. | CIR freeze | Psychology Director |
| I-SI-27 | Every Mystery, if `resolved`, references the resolving Reveal. | CIR freeze | Narrative Director |
| I-SI-28 | Every Relationship references two valid Characters. | CIR freeze | Character Director |
| I-SI-29 | The Character relationship graph is complete (every pair has a Relationship, including "none"). | CIR freeze | Character Director |
| I-SI-30 | Every Adaptation (`adapts_to`) does not redefine intent (I-AD-1, `003`). | CIR freeze | Platform Director |
| I-SI-31 | Every Presentation Profile preference does not contradict an intent domain (I-PP-1, `003`). | CIS validation | CIS Validator |
| I-SI-32 | Every Creative Constraint of precedence class `ethical` overrides any conflicting intent domain. | CIS validation | CIS Validator |
| I-SI-33 | Every Composer pass consumes a frozen CIR node (I-TC-1, `002`). | Compilation | Compiler |
| I-SI-34 | Every Flashback references a Memory, and the referenced event `precedes` the containing Scene. | CIR freeze | Narrative Director |
| I-SI-35 | Every Music Theme that references a Character or Theme uses `references`. | CIR freeze | Music Director |
| I-SI-36 | Every Creative Version carries `amends` (if not the first). | Versioning | The versioning subsystem |
| I-SI-37 | Every Creative Branch carries `branched_from`. | Versioning | Human |
| I-SI-38 | Every Location has a visual identity and an acoustic identity. | CIR freeze | Production Designer |
| I-SI-39 | Every Runtime Segment's duration is positive. | CIR freeze | Editorial Director |
| I-SI-40 | The sum of Runtime Segment durations equals the Timeline total runtime. | CIR freeze | Editorial Director |

These invariants are the COM's contribution to ORACLE's validation rules (`002` Part 11.2). ORACLE validates the media-side projection of these invariants; the CIR-freeze validator validates the reasoning-side projection; the CIS Validator validates the intent-side projection.

---

# PART 6: CREATIVE STATE MODEL

---

## 6.1 State Machine Principles

Every COM object has a lifecycle state machine. The principles:

1. **State is explicit.** An object is always in exactly one state.
2. **Transitions are guarded.** A transition may require validation, approval, or upstream state.
3. **Frozen is irreversible except by versioning.** A frozen object can only change by creating a new version (GFS-003), not by mutation.
4. **Archived is terminal.** An archived object may be referenced (`learns_from`) but not mutated.
5. **State is consistent across layers.** A Scene's state in the CIS, CIR, and PKP is the same state (the object is shared, per Part 1.5).

## 6.2 State Machines by Object Family

### 6.2.1 Production

```
conceived → authored → reasoning → compiled → rendering → validating → archived
                                                              │
                                                              ▼
                                                         (revision loop)
```

### 6.2.2 Story / Narrative / Act / Sequence / Scene / Beat

```
proposed → structured → planned → frozen → (revised) → archived
```

- `proposed`: the object has been authored (in CIS or by a director).
- `structured`: the object's composition is defined (children identified).
- `planned`: the object's content is fully specified.
- `frozen`: immutable.
- `revised`: a new version has been created; the prior version remains.
- `archived`: terminal.

### 6.2.3 Character

```
proposed → developed → frozen → (revised) → archived
```

### 6.2.4 Dialogue / Monologue / Silence

```
proposed → frozen → (revised) → archived
```

### 6.2.5 Creative Decision (the CIR node lifecycle, per `002` Part 3.1)

```
idea → research → context → alternatives → tradeoff → selected → reviewed → recorded → frozen → archived
```

### 6.2.6 Creative Artifact (PKP artifact, media, validation report)

```
produced → validated → archived
```

### 6.2.7 Creative Version

```
created → (superseded)
```

A version is created immutable; it may be superseded by a later version but never mutated.

### 6.2.8 Creative Branch

```
branched → authored → (merged or abandoned)
```

A branch is independent of its source; merging creates a new object that supersedes both, not a mutation of either.

### 6.2.9 Creative Constraint

```
authored → validated → frozen → (revised) → archived
```

Authored in the CIS; validated by the CIS Validator; frozen at CIR freeze.

### 6.2.10 Mystery

```
posed → resolved → frozen → (revised) → archived
```

A Mystery may be frozen in the `posed` state (intentionally unresolved) or in the `resolved` state.

---

# PART 7: SEMANTIC QUERY MODEL

---

## 7.1 Query Primitives

Every subsystem references COM objects through a standard set of query primitives. The primitives are operations on the PKG (the COM's store), not direct memory access.

| Primitive | Definition | Example |
|-----------|-----------|---------|
| **lookup** | Fetch an object by identity. | `lookup(com:ew001:scene:07)` |
| **traceability** | Traverse upstream to the authoring source. | `traceability(Shot) → Scene → Sequence → Act → Story → Creative Intent → Human` |
| **dependency traversal** | Traverse `depends_on` edges. | `dependency_traversal(Payoff) → Setup` |
| **lineage** | Traverse `amends` edges across versions. | `lineage(Story@3) → Story@2 → Story@1` |
| **provenance** | Fetch the Creative Decision that authorized an object. | `provenance(Scene) → Creative Decision → Director → CIS domain` |
| **impact analysis** | Traverse downstream to find all objects that depend on a given object. | `impact_analysis(Setup) → [Payoff-1, Payoff-2, Callback-3]` |
| **semantic search** | Find objects by type, relationship, or attribute (using GO-002 predicates). | `semantic_search(Scene, has_emotion, dread)` |
| **reverse lookup** | Find objects that reference a given object. | `reverse_lookup(Motif) → [Scene-3, Scene-7, Callback-12]` |

## 7.2 Subsystem Query Contracts

| Subsystem | Queries it uses | Why |
|-----------|----------------|-----|
| **Human Authoring (CIS)** | `lookup`, `lineage`, `traceability` | To show the human what they have authored and what it derives from. |
| **Directorial Board** | `lookup`, `dependency_traversal`, `impact_analysis`, `provenance`, `semantic_search` | To reason with full knowledge of upstream and downstream. |
| **Compiler Passes** | `lookup`, `dependency_traversal`, `traceability` | To compile an object, the pass must traverse its dependencies and trace its intent. |
| **PROMETHEUS** | `lookup` (PKP objects only) | To render, PROMETHEUS reads the compiled objects. It does not traverse reasoning. |
| **ORACLE** | `lookup`, `traceability`, `provenance`, `impact_analysis`, `reverse_lookup` | To validate media against intent, ORACLE traces from media → PKP artifact → CIR node → CIS domain. To detect drift, ORACLE uses `impact_analysis` to find all objects affected by a detected divergence. |
| **ATLAS** | `lookup`, `lineage`, `semantic_search` (over archived objects) | To persist and retrieve; to support `learns_from` queries. |

The query model is the COM's read interface. The operation model (Part 4) is the COM's write interface. Together they form the COM's API.

---

# PART 8: MAPPING ARCHITECTURE

---

## 8.1 The Full Pipeline as Object Flow

The pipeline is a flow of COM objects through layers, where each layer produces a projection of the same objects in a different state.

```
Human
   │
   │ authors COM objects in intent state
   ▼
Creative Intent Specification (CIS)
   │   (COM objects: Creative Intent, Story Intent, Theme, Message, Emotional Journey,
   │    Emotion Transition, Audience, Constraints, Presentation Profile, etc.)
   │
   │ validated, approved, pinned
   ▼
GENESIS Directorial Board (002 Part 2)
   │
   │ reasons from intent-state objects
   │ produces Creative Decisions
   │
   ▼
Creative Intent Record (CIR)
   │   (COM objects: Creative Decisions, each authorizing an intent-state object
   │    to become a reasoning-state object)
   │
   │ frozen
   ▼
GENESIS Compiler Passes (001 §4.2)
   │
   │ compiles reasoning-state objects into executable-state objects
   │
   ▼
Production Knowledge Package (PKP)
   │   (COM objects in executable state: Scenes with Shots, Dialogue, Music, Lighting,
   │    Camera, Timeline, Runtime Segments)
   │
   │ frozen, hashed
   ▼
PROMETHEUS
   │
   │ renders executable-state objects into media
   │
   ▼
Media (Creative Artifacts)
   │
   ▼
ORACLE
   │
   │ validates media against the executable-state and reasoning-state objects
   │ produces Validation Reports (Creative Artifacts)
   │
   ▼
ATLAS
   │
   │ archives all objects in all states (intent, reasoning, executable, media, validation)
   │
   ▼
Learning (Director Memory consumes archived objects)
```

## 8.2 Layer Ownership

| Layer | Owns | Does not own |
|-------|------|--------------|
| **Human** | COM objects in intent state (the CIS). | Reasoning, compilation, rendering, validation. |
| **Directorial Board** | Creative Decisions (the CIR). | The intent-state objects (those are the human's); the executable-state objects (those are the compiler's). |
| **Compiler** | COM objects in executable state (the PKP). | The intent or reasoning states. |
| **PROMETHEUS** | Media (Creative Artifacts). | The COM objects (it reads them). |
| **ORACLE** | Validation Reports (Creative Artifacts). | The COM objects (it validates them). |
| **ATLAS** | All archived objects. | The live objects (it persists them on behalf of the owners). |

## 8.3 Immutability and Executability Across Layers

| Layer | Object state | Immutable? | Executable? |
|-------|-------------|-----------|-------------|
| CIS | intent | After pinning (`003` Part 8.3) | No |
| CIR | reasoning | After freeze (`002` Part 12.2) | No (it is reasoning, not executable) |
| PKP | executable | After freeze and hash (`001` §5) | Yes (PROMETHEUS reads it) |
| Media | rendered | Always (immutable per `00` §3.5) | No (it is the output) |
| Validation | report | Always | No |

What remains immutable across all layers: the object **identity** (a Scene is `com:ew001:scene:07` whether in CIS, CIR, PKP, or ORACLE's report). What changes across layers: the object's **state** (intent → reasoning → executable → rendered). What becomes executable: the PKP projection. What becomes knowledge: the archived objects in ATLAS.

---

# PART 9: COMPILER SEMANTICS

---

## 9.1 GENESIS as an Object Compiler

GENESIS is a compiler that operates on COM objects. This is the architectural realization of `00` §3.2 ("Compilation Over Generation") at the object level.

A traditional compiler:
- Parses source text into an AST.
- Performs semantic analysis on the AST.
- Transforms the AST through optimization passes.
- Emits executable code.

GENESIS as an object compiler:
- Reads COM objects in intent state (the CIS).
- Produces COM objects in reasoning state (the CIR) via the Directorial Board's reasoning (`002` Part 5).
- Performs semantic analysis (Part 5 invariants) and dependency resolution on the reasoning-state objects.
- Transforms reasoning-state objects through compiler passes (`001` §4.2) into executable-state objects (the PKP).
- Emits executable COM objects that PROMETHEUS renders.

The compiler does not manipulate raw text. It manipulates typed COM objects. The Prompt Compiler (`001` Pass 16) is the only pass that projects objects into text (prompts), and it does so as the final step before PROMETHEUS, not as the substrate of compilation.

## 9.2 Compiler Phases on Objects

| Phase | What it does to objects | Passes (`001` §4.2) |
|-------|------------------------|---------------------|
| **Semantic analysis** | Checks invariants (Part 5); checks cross-object consistency; checks constraint satisfaction. | Pass 18 (Validation Gate) — creative quality subset. |
| **Object validation** | Validates each object against its §2.1 contract and the invariants it owns. | Each pass validates its own output. |
| **Dependency resolution** | Resolves `depends_on` edges; ensures the dependency graph is acyclic; ensures all dependencies are frozen. | Pre-compilation; Pass 17 (Production Package Assembly). |
| **Creative transformations** | Transforms intent-state objects into reasoning-state objects (Director) and reasoning-state into executable-state (compiler passes). | Passes 01–16. |
| **Optimization** | Within the profile envelope and the CIS constraints, optimizes for the Creative Metrics (`002` Part 11). E.g., pacing optimization within the runtime envelope. | Passes 04, 15. |
| **Deterministic compilation** | Same inputs → same outputs. Seed-based reproducibility (`002` Part 5.3). | All passes. |
| **Incremental compilation** | On revision, only the objects whose `cir_origin` has changed are recompiled; downstream objects are recompiled only if their inputs changed. | Passes 01–16, supporting partial regeneration. |
| **Partial regeneration** | When ORACLE reports drift on a specific object, only that object and its downstream dependents are regenerated. | The surgical revision loop (`002` Part 11.2). |

## 9.3 Deterministic and Incremental Compilation

Deterministic compilation (per `00` §3.6, `002` Part 5.3) at the object level means:

- Given the same pinned CIS, the same Directorial Board reasoning seeds, and the same provider versions, the compiler produces the same PKP.
- Each COM object's `cir_origin` records the Creative Decision and the CIS version that authorized it; replay pins all three.

Incremental compilation at the object level means:

- A revision creates new versions of the affected COM objects (per GFS-003).
- The compiler traverses the `depends_on` graph from the changed objects; only objects reachable via `depends_on` from a changed object are recompiled.
- Unreachable objects remain frozen; their media is not regenerated.
- This is the surgical revision loop (`002` Part 11.2) implemented at the object level.

This is why the COM has a typed dependency graph: without it, incremental compilation is impossible, and every revision would re-run the entire pipeline.

---

# PART 10: GOVERNANCE

---

## 10.1 Governance Authority

The COM is governed under the constitutional framework:

- **GFS-000 (Constitutional Charter)** is supreme. The COM does not amend it.
- **GFS-007 (Governance Constitution)** governs changes to the COM.
- **GFS-009 (Constitutional Ontology Framework)** governs the COM's relationship to the ontology (the COM uses ontology terms; it does not redefine them).
- **This specification** is the COM's canonical definition. Changes to the COM's object set, relationship set, operation set, or invariant set require an amendment to this specification, issued under GFS-007.

## 10.2 Semantic Evolution

| Change type | Authority | Process |
|--------------|-----------|---------|
| **New object type** | GFS-007 governance. | Proposed as an amendment to this specification; must specify the full §2.1 contract; must not duplicate an existing type; must be grounded in ontology (a GO term). |
| **New relationship type** | GFS-007 governance. | Proposed as an amendment; must specify the full §3.1 contract; must be grounded in GO-002 (a GO predicate or a COM-specific extension marked as such). |
| **New operation** | GFS-007 governance. | Proposed as an amendment; must specify the operation's class, effect, and authority matrix. |
| **New invariant** | GFS-007 governance. | Proposed as an amendment; must specify the enforcement point and owner. |
| **Object deprecation** | GFS-007 governance. | Deprecated objects remain valid in archived productions; new productions may not author them. A deprecation cycle is defined (Part 10.3). |
| **Object specialization** | GFS-007 governance. | A new type may `specializes` an existing type; the new type inherits the parent's invariants. |

## 10.3 Compatibility, Deprecation, Migration

| Concern | Rule |
|---------|------|
| **Version compatibility** | A COM version is identified by the specification version (e.g., COM 1.0). A production pinned against COM 1.0 remains valid under COM 1.x; breaking changes require COM 2.0. |
| **Backward compatibility** | New object types and relationships are additive; they do not break existing productions. Removed or renamed types are deprecation-cycled. |
| **Deprecation cycle** | A deprecated type is marked `deprecated` for one specification version; in the following version it is marked `obsolete`; in the version after that it is removed from the catalog. Archived productions using the type remain valid. |
| **Migration** | When a type is deprecated, a migration path is documented (which new type replaces it, how existing instances are re-typed). Migration of archived productions is optional; migration of in-progress productions is required at the next revision. |
| **Validation** | Every COM version ships with an invariant set; validators are versioned with the COM. A production validated against COM 1.0 may be re-validated against COM 1.x; re-validation against COM 2.0 may flag new violations. |
| **Constitutional precedence** | The COM is below GFS-000..009. If a COM type, relationship, or invariant conflicts with a constitution, the constitution wins and the COM is amended. |

---

# PART 11: MIGRATION STRATEGY

---

## 11.1 Integration Principles

The COM integrates into the existing architecture under these principles:

| # | Principle | Statement |
|---|-----------|-----------|
| MI-1 | **The COM is additive.** It defines the programming model; it does not replace the ontology, the PKG, the PKP, the CIR, or the CIS. |
| MI-2 | **The COM binds ontology to identity.** GO-001 defines what a Character is; the COM defines how a Character instance is identified, owned, versioned, and operated on. The COM does not redefine GO-104. |
| MI-3 | **The COM is the single semantic programming model.** No subsystem may define a competing object model. Existing subsystem-specific vocabularies are re-typed as COM projections. |
| MI-4 | **The COM preserves the four-pillar boundaries.** The COM is shared; the pillars' contracts (`001` §2.2) are unchanged. The COM is the language they speak, not a new pillar. |
| MI-5 | **The COM does not invent concepts.** Every COM object is grounded in an existing ontology term (GO-001..119) or an existing specification concept (PKP-00..18, `001`, `002`, `003`). |
| MI-6 | **No duplicate concepts.** Where the existing architecture has a concept (e.g., a PKP Scene Specification), the COM does not redefine it; the COM types it. |

## 11.2 Migration Phases

### Phase M-1 — COM Catalog Documentation

- Document the 56 COM object types (Part 2.3) and the 24 relationship types (Part 3.2) in `docs/genesis/specifications/` (a new `semantic/` subdirectory, or extending the existing `ontology/` subdirectory per the existing classification).
- Cross-reference each COM type to its grounding ontology term (GO-NNN) and to its appearance in the PKP specs (PKP-NN).
- No runtime change.

**Exit criteria:** COM catalog committed; cross-reference tables complete; ADR issued recording the COM-as-programming-model decision.

### Phase M-2 — Identity Scheme Unification

- Adopt the COM identity scheme (`com:<production-id>:<object-type>:<ordinal>[:<revision>]`, Part 2.1) as the canonical identifier for all objects across CIS, CIR, PKP, ORACLE, ATLAS.
- Map existing identifiers (CIS `cis:<production-id>:v<ordinal>`, CIR `cir:<production-id>:<director-slug>:<node-type>:<ordinal>`) to the COM scheme as supertypes; the existing identifiers remain valid as COM sub-identifiers.
- No existing identifier is invalidated.

**Exit criteria:** Identity scheme unified; existing identifiers mapped; cross-subsystem reference is consistent.

### Phase M-3 — Invariant Enforcement

- Implement the 40 invariants (Part 5.2) at the three enforcement points (CIS validation, CIR freeze, ORACLE validation).
- Map each invariant to its owner and enforcement point.

**Exit criteria:** Invariants enforced; violations produce blocking findings at the correct enforcement point.

### Phase M-4 — Operation and Authority Matrix Implementation

- Implement the 28 operations (Part 4.2) with the authority matrix (Part 4.3).
- Enforce the operation classification (intent-preserving vs. intent-changing; CIS-amending vs. not).

**Exit criteria:** Operations are available; authority is enforced; intent-changing operations require CIS amendment.

### Phase M-5 — Relationship Model Implementation

- Implement the 24 relationship types (Part 3.2) as the canonical PKG edge vocabulary, extending GO-002.
- Map existing GO-002 predicates to COM relationships (e.g., GO-002 `contains` → COM `contains`); add COM-specific relationships (`motivates`, `constrains`, `authorizes`, `adapts_to`) as extensions under GFS-009.

**Exit criteria:** Relationship vocabulary unified; GO-002 preserved and extended; PKG edges use COM relationships.

### Phase M-6 — Compiler Object Semantics

- Wire the compiler passes (`001` §4.2) to consume and produce COM objects (rather than ad-hoc structures).
- Implement incremental compilation (Part 9.3) via `depends_on` traversal.
- Implement partial regeneration via the surgical revision loop.

**Exit criteria:** Compiler passes operate on COM objects; incremental compilation works; partial regeneration works.

### Phase M-7 — Subsystem Re-typing

- Re-type the Directorial Board's CIR nodes as COM objects of type Creative Decision.
- Re-type the PKP artifacts as COM objects in executable state.
- Re-type ORACLE's validation reports as COM objects of type Creative Artifact.
- Re-type ATLAS's archived assets as COM objects in archived state.

**Exit criteria:** All subsystems speak COM; no subsystem defines a competing object model.

## 11.3 Backward Compatibility

| Existing artifact | Compatibility | Action |
|-------------------|---------------|--------|
| GFS-000..009 | **Preserved.** The COM is a derived standard under GFS-007/GFS-009. | None. |
| GO-001..GO-119 | **Preserved.** The COM uses ontology terms; it does not redefine them. | None. New terms added only as derived ontology extensions under GFS-009. |
| GO-002 Semantic Relationship Catalog | **Preserved and extended.** COM relationships map to GO-002 predicates where GO-002 defines them; COM-specific relationships are added as extensions. | Add COM-specific relationships to GO-002 as extensions. |
| `001` compiler passes | **Preserved.** The passes operate on COM objects instead of ad-hoc structures; their pass contract is unchanged. | Wire passes to COM objects (Phase M-6). |
| `001` PKP schema | **Preserved.** PKP artifacts are COM objects in executable state; the PKP schema is a projection of the COM. | None. |
| `002` Directorial Board | **Preserved.** Directors produce COM objects of type Creative Decision. | None. |
| `002` CIR | **Preserved.** The CIR is a graph of Creative Decision objects; the CIR's structure is unchanged. | None. |
| `003` CIS | **Preserved.** The CIS is authored in COM vocabulary; the CIS's 24 domains map to COM object types. | None. |
| PKP-00..18 | **Preserved.** Each PKP spec is a projection of one or more COM object types into executable state. | Document the mapping (Phase M-1). |
| Existing agent specs | **Preserved.** Agents are re-typed as COM producers/consumers. | None. |
| Existing schemas (`docs/genesis/schemas/`) | **Preserved.** Schemas are projections of the COM; the COM is the source. | Schemas are re-generated from the COM as needed. |
| Existing patterns (`docs/genesis/patterns/`) | **Preserved.** Patterns are COM operations or validations. | None. |

## 11.4 Risks and Architectural Impacts

| Risk | Severity | Mitigation |
|------|----------|------------|
| **COM bloat.** The 55-object catalog may grow unbounded. | Medium | Governance (Part 10.2): new types require architectural justification and GO grounding. The catalog is versioned. |
| **COM/ontology conflation.** Implementers may treat the COM as the ontology, duplicating GO-001..119. | High | MI-2: the COM binds ontology to identity; it does not redefine ontology terms. Code review enforces the separation. |
| **Subsystem resistance.** Subsystems may resist re-typing their private vocabularies as COM projections. | Medium | MI-3: no competing object model is permitted. Migration Phase M-7 re-types all subsystems; the COM is the single programming model. |
| **Identity scheme migration.** Existing identifiers may not cleanly map to the COM scheme. | Medium | Phase M-2: existing identifiers are mapped as COM sub-identifiers; no existing identifier is invalidated. |
| **Invariant enforcement gaps.** Some invariants may not be enforceable at all three points. | Medium | Phase M-3 maps each invariant to its enforcement point; invariants that cannot be enforced at a point are recorded as advisory at that point. |
| **Incremental compilation complexity.** `depends_on` traversal may be expensive for large productions. | Low | The graph is typed and bounded; traversal is well-defined. ATLAS indexes the graph for query performance. |
| **COM version drift.** A production pinned against COM 1.0 may break under COM 2.0. | Low | Part 10.3: breaking changes require a major version; deprecated types are cycled; archived productions remain valid under their pinned COM version. |

---

## Architectural Rules (Restated)

This specification produced **no implementation code, no Python, no TypeScript, no YAML, no JSON schemas, no source code**. It produced a constitutional architecture specification — the language specification of the Cinema Production Engine's semantic programming model. Every recommendation is grounded in the existing repository:

- The COM's 56 object types are grounded in GO-001..GO-119 (ontology nouns) and in the PKP-00..18 concepts (compiled outputs).
- The COM's 24 relationship types are grounded in GO-002 (semantic predicates), extended with COM-specific relationships marked as such.
- The COM's 40 invariants are the structural form of the reasoning models in `002` Part 5.2 and the validation rules in `003` Part 8.
- The COM's 28 operations are the structural form of the lifecycle and revision operations in `002` Part 10 and `003` Part 10.
- The COM's identity scheme extends the schemes in `002` Part 12.4 and `003` Part 10.2.1.
- The COM's compiler semantics extend `001` §4.2 and `00` §3.2.
- The COM's governance follows GFS-007 and GFS-009.
- The COM preserves the four-pillar boundaries (`001` §2).

No parallel architecture is introduced. No existing concept is duplicated. The COM is the semantic programming model that binds the ontology to identity, lifecycle, operations, and invariants. It extends existing work; it does not invent beside it.

---

## Cross-References

| Reference | Location | Relevance |
|-----------|----------|-----------|
| Constitutional Architecture | `00 — Cinema Production Engine Vision, Philosophy & Reference Architecture.md` | Supreme authority. The COM derives from §3.2 (compilation over generation), §3.5 (provenance mandatory), §3.6 (deterministic replay), §3.3 (creative/technical separation). |
| Migration Blueprint | `001 — GENESIS 2.0 Migration Specification.md` | Defines the compiler passes (§4.2) that operate on COM objects, the PKP (§5) that is the COM in executable state, and the four-pillar boundaries (§2) the COM respects. |
| Director Intelligence | `002 — Director Intelligence & Creative Reasoning Architecture Specification.md` | Defines the Directorial Board (Part 2) that produces Creative Decision objects, the CIR (Part 12) that is a graph of Creative Decisions, and the reasoning models (Part 5.2) that the COM's invariants structuralize. |
| Creative Intent Specification | `003 — Creative Intent Specification (CIS) Architecture.md` | Defines the CIS, authored in COM vocabulary. The CIS's 24 domains map to COM object types; the CIS's validation (Part 8) enforces COM intent-side invariants. |
| Constitutional Charter | `docs/genesis/constitutions/00-ConstitutionCharter.md` (GFS-000) | Supreme constitutional authority. |
| Governance Constitution | `docs/genesis/constitutions/007 – Governance Constitution.md` (GFS-007) | Governs COM evolution. |
| Constitutional Ontology Framework | `docs/genesis/constitutions/009 — Constitutional Ontology Framework.md` (GFS-009) | Governs the COM's relationship to the ontology. |
| Core Ontology | `docs/genesis/ontology/core/001 — Genesis Core Ontology.md` (GO-001) | The noun vocabulary the COM's object types are named with. |
| Semantic Relationship Catalog | `docs/genesis/ontology/semantic/002 — Genesis Semantic Relationship Catalog.md` (GO-002) | The predicate vocabulary the COM's relationships are named with. |
| State & Lifecycle Ontology | `docs/genesis/ontology/core/003 — Genesis State & Lifecycle Ontology.md` (GO-003) | The lifecycle vocabulary the COM's state machines use. |
| Narrative Ontology | `docs/genesis/ontology/core/101 — Narrative Ontology.md` (GO-101) | Story, Narrative, Act, Sequence, Scene, Beat vocabulary. |
| Audience Experience Ontology | `docs/genesis/ontology/experience/102 — Audience Experience Ontology.md` (GO-102) | Audience, Experience, Reflection vocabulary. |
| Human Psychology & Behavior Ontology | `docs/genesis/ontology/experience/103 — Human Psychology & Behavior Ontology.md` (GO-103) | Emotion, Emotion Transition, Need, Memory vocabulary. |
| Character Ontology | `docs/genesis/ontology/core/104 — Character Ontology.md` (GO-104) | Character, Relationship, Goal vocabulary. |
| World & Environment Ontology | `docs/genesis/ontology/core/105 — World & Environment Ontology.md` (GO-105) | Location, Environment vocabulary. |
| Event, Action & Causality Ontology | `docs/genesis/ontology/semantic/106 — Event, Action & Causality Ontology.md` (GO-106) | Conflict, Decision, causes vocabulary. |
| Knowledge, Information & Revelation Ontology | `docs/genesis/ontology/semantic/107 — Knowledge, Information & Revelation Ontology.md` (GO-107) | Reveal, Mystery, Setup, Payoff, Foreshadowing vocabulary. |
| Communication, Dialogue & Interaction Ontology | `docs/genesis/ontology/semantic/108 Communication, Dialogue & Interaction.md` (GO-108) | Dialogue, Monologue, Silence vocabulary. |
| Visual Expression Ontology | `docs/genesis/ontology/experience/109 — Visual Expression, Cinematography & Composition Ontology.md` (GO-109) | Visual Language, Shot, Camera, Lighting vocabulary. |
| Audio, Music, Sound Design & Silence Ontology | `docs/genesis/ontology/experience/110 — Audio, Music, Sound Design & Silence Ontology.md` (GO-110) | Music Theme, Soundscape vocabulary. |
| Temporal Experience, Editing & Narrative Rhythm Ontology | `docs/genesis/ontology/experience/111 — Temporal Experience, Editing & Narrative Rhythm Ontology.md` (GO-111) | Timeline, Runtime Segment, Transition vocabulary. |
| Creativity, Innovation & Design Reasoning Ontology | `docs/genesis/ontology/creativity/116 — Creativity, Innovation & Design Reasoning Ontology.md` (GO-116) | Theme, Message, Motif, Symbol vocabulary. |
| All 19 PKP Specifications | `docs/genesis/specifications/pkp/` | Each PKP spec is a projection of COM object types into executable state. |
| Existing agent specs | `docs/genesis/agents/` | Agents are COM producers and consumers. |
| Existing schemas | `docs/genesis/schemas/` | Schemas are projections of the COM. |
| Existing patterns | `docs/genesis/patterns/` | Patterns are COM operations or validations. |

---

**End of Specification.**