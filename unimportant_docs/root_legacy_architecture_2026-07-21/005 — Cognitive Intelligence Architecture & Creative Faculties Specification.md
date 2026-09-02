# 005 — Cognitive Intelligence Architecture & Creative Faculties Specification

**Status:** Constitutional Architecture Specification — Supreme Authority for the Artificial Creative Mind
**Version:** 1.0.0
**Date:** 2026-07-21
**Authority:** Derives from `00 — Cinema Production Engine Vision, Philosophy & Reference Architecture.md` (the Constitutional Architecture). Extends the migration blueprint of `001 — GENESIS 2.0 Migration Specification.md`, the Directorial Board of `002 — Director Intelligence & Creative Reasoning Architecture Specification.md`, the Creative Intent Specification of `003 — Creative Intent Specification (CIS) Architecture.md`, and the Creative Object Model of `004 — Creative Object Model (COM) & Semantic Architecture Specification.md`. This document defines the **Creative Mind** — the cognitive architecture of Artificial Creative Intelligence that performs reasoning before any creative decision is made.
**Precedence:** Below the Constitutional Architecture (§00). Equal in tier to `001`, `002`, `003`, and `004`. Above all ontology extensions, domain specifications, PKP specifications, workflow definitions, and implementation guides. When this document conflicts with an informal cognitive model, a runtime-specific reasoning convention, or a subsystem-private notion of "creativity," this document wins unless the conflict is with the Constitutional Architecture itself.
**Scope:** The Creative Mind, the Creative Faculties, Faculty Collaboration, Creative Deliberation, Creative Authority, the Creative Lifecycle, Integration with the existing architecture, Creative Evolution, Governance, and the Migration Strategy.

---

## Table of Contents

**PART 1: PHILOSOPHY**
- [1.1 Creativity Is Fundamentally a Cognitive Process](#11-creativity-is-fundamentally-a-cognitive-process)
- [1.2 Faculties, Not Agents](#12-faculties-not-agents)
- [1.3 Artificial Creativity vs. Traditional Generative AI](#13-artificial-creativity-vs-traditional-generative-ai)
- [1.4 The Creative Cognition Chain](#14-the-creative-cognition-chain)
- [1.5 Position in the Constitutional Architecture](#15-position-in-the-constitutional-architecture)
- [1.6 Differentiation from Adjacent Artifacts](#16-differentiation-from-adjacent-artifacts)

**PART 2: THE CREATIVE MIND**
- [2.1 Purpose and Responsibilities](#21-purpose-and-responsibilities)
- [2.2 Boundaries](#22-boundaries)
- [2.3 Lifecycle](#23-lifecycle)
- [2.4 Authority](#24-authority)
- [2.5 Relationship Map](#25-relationship-map)
- [2.6 Runtime Independence](#26-runtime-independence)

**PART 3: CREATIVE FACULTIES**
- [3.1 Faculty Specification Contract](#31-faculty-specification-contract)
- [3.2 Faculty Catalog](#32-faculty-catalog)
- [3.3 Faculty Details](#33-faculty-details)

**PART 4: FACULTY COLLABORATION ARCHITECTURE**
- [4.1 Cognitive Interaction, Not Workflow](#41-cognitive-interaction-not-workflow)
- [4.2 Knowledge Exchange](#42-knowledge-exchange)
- [4.3 COM Enrichment](#43-com-enrichment)
- [4.4 Disagreement and Resolution](#44-disagreement-and-resolution)
- [4.5 Consensus and Convergence](#45-consensus-and-convergence)
- [4.6 Uncertainty and Confidence Propagation](#46-uncertainty-and-confidence-propagation)
- [4.7 Creative Deadlock and Creative Convergence](#47-creative-deadlock-and-creative-convergence)

**PART 5: CREATIVE DELIBERATION**
- [5.1 Why Internal Deliberation](#51-why-internal-deliberation)
- [5.2 The Deliberation Arc](#52-the-deliberation-arc)
- [5.3 Iterative Creativity](#53-iterative-creativity)

**PART 6: CREATIVE AUTHORITY**
- [6.1 Faculty Ownership Map](#61-faculty-ownership-map)
- [6.2 Authority Types](#62-authority-types)

**PART 7: CREATIVE LIFECYCLE**
- [7.1 Lifecycle Stages](#71-lifecycle-stages)
- [7.2 Faculty Participation Across Stages](#72-faculty-participation-across-stages)

**PART 8: INTEGRATION WITH EXISTING ARCHITECTURE**
- [8.1 The Full Cognitive-Pipeline Map](#81-the-full-cognitive-pipeline-map)
- [8.2 Layer Ownership and Flow](#82-layer-ownership-and-flow)

**PART 9: CREATIVE EVOLUTION**
- [9.1 Evolution Kinds](#91-evolution-kinds)
- [9.2 Constitutional Compatibility](#92-constitutional-compatibility)

**PART 10: GOVERNANCE**
- [10.1 Governance Authority](#101-governance-authority)
- [10.2 Faculty Evolution Governance](#102-faculty-evolution-governance)

**PART 11: MIGRATION STRATEGY**
- [11.1 Integration Principles](#111-integration-principles)
- [11.2 Migration Phases](#112-migration-phases)
- [11.3 Backward Compatibility](#113-backward-compatibility)
- [11.4 Risks and Architectural Impacts](#114-risks-and-architectural-impacts)

---

# PART 1: PHILOSOPHY

---

## 1.1 Creativity Is Fundamentally a Cognitive Process

Creativity is not an output. It is not a style. It is not a model. Creativity is a **cognitive process** — a structured internal activity that transforms intent into understanding, understanding into options, options into choices, and choices into artifacts. The output (a film, a scene, a line of dialogue) is the *product* of creativity, not creativity itself.

This matters architecturally because the Cinema Production Engine has committed to compilation over generation (`00` §3.2) and to deterministic creative replay (`00` §3.6). Both commitments require that the creative process be **structurable, auditable, and reproducible** — properties that belong to a cognitive process, not to an emergent output. If creativity were an opaque output, the engine could not explain why a decision was made, could not revise it surgically, and could not replay it deterministically.

The Creative Reasoning Engine defined in `002` Part 5 already treats reasoning as a structured activity with modes (emotional, symbolic, psychological, cinematic, audience, platform) and models (suspense, pacing, silence, payoff, etc.). This specification generalizes that structure: reasoning is not a single engine but a **Mind** composed of **Faculties**, each a stable cognitive capability that contributes a distinct mode of understanding to the creative process.

## 1.2 Faculties, Not Agents

The repository already has an agent architecture (`docs/genesis/agents/`, `movie_os/agents/`, the Directorial Board of `002` Part 2). Adding another layer of "creative agents" would duplicate that architecture and produce the exact overlapping-responsibility defect the coherence review of 000–004 was conducted to eliminate.

Instead, the Creative Mind is modeled as a set of **Creative Faculties** — stable cognitive capabilities analogous to the faculties of the human mind (memory, reasoning, imagination, planning, reflection). The faculty model differs from the agent model in five architectural respects:

| # | Agents (existing) | Faculties (this specification) |
|---|-------------------|--------------------------------|
| F-1 | Goal-directed actors that produce artifacts. | Cognitive capabilities that produce **understanding**, not artifacts. |
| F-2 | Have authority over a domain and make decisions. | Have **no decision authority**; they inform decisions made by the Directorial Board. |
| F-3 | Communicate through published artifacts and messages. | Communicate through **enriched COM objects** and **deliberation state**, not through messages. |
| F-4 | Map to compiler passes and PKP artifacts. | Map to **modes of understanding** that the Board consumes before deciding. |
| F-5 | Are cinema-specific (the 18 directors of `002`). | Are **runtime-independent** (the same faculties serve cinema, games, books, education, etc.). |

The distinction is constitutional: **Faculties provide cognition; the Directorial Board provides decisions.** A faculty does not decide the camera angle; the Cinematography Director (`002` Part 2.3.9) decides. The Visual Faculty provides the understanding (visual coherence, metaphor grounding, composition reasoning) that the Cinematography Director consumes to decide. The faculty is the *thinking*; the director is the *choosing*.

This separation is what makes the Creative Mind runtime-independent (Part 2.6) and what prevents this specification from duplicating `002`.

## 1.3 Artificial Creativity vs. Traditional Generative AI

Traditional generative AI (a text-to-video model, a text-to-image model, a chatbot) treats creativity as **emergent output**: given a prompt, the model produces an artifact, and the artifact *is* the creativity. There is no separate cognitive process; the generation is the process.

Artificial Creative Intelligence (this specification) treats creativity as a **structured cognitive process that precedes output**. The output is the product of the process, not the process itself. The process is:

- **Understand** the intent (CIS, `003`).
- **Reason** about the intent's implications across cognitive domains (Faculties).
- **Deliberate** over alternatives (Part 5).
- **Decide** (Directorial Board, `002`).
- **Compile** the decision (Compiler, `001` §4.2).
- **Render** the compilation (PROMETHEUS, `001` §2.1).
- **Validate** the rendering (ORACLE, `001` §2.1).
- **Persist** everything (ATLAS, `001` §2.1).

Generative AI collapses steps 1–5 into a single opaque step. The Cinema Production Engine decomposes them, making each step auditable, revisable, and replayable. The Creative Mind owns step 2 (reasoning) and the cognitive portion of step 3 (deliberation). It does not own step 4 (decision) — that is the Board's. It does not own steps 5–8 — those are the compiler, PROMETHEUS, ORACLE, and ATLAS.

## 1.4 The Creative Cognition Chain

The Creative Mind operates within a longer chain that begins with human creativity and ends with creative production:

```
Human Creativity
      │
      │ expressed as
      ▼
Creative Intent Specification (CIS)   [003]
      │
      │ interpreted by
      ▼
Creative Cognition                     [this specification]
      │  (Faculties reason about the CIS, enrich COM objects,
      │   deliberate over alternatives, produce understanding)
      │
      │ consumed by
      ▼
Creative Decisions                     [002]
      │  (Directorial Board turns understanding into
      │   Creative Decisions recorded in the CIR)
      │
      │ compiled by
      ▼
Creative Production                    [001 §4.2, PROMETHEUS]
      │  (Compiler produces PKP; PROMETHEUS renders media)
      │
      ▼
Media → ORACLE → ATLAS
```

The Creative Mind sits between the CIS and the Directorial Board. It does not decide; it prepares the understanding with which the Board decides. This is the architectural separation that makes the Mind runtime-independent (the Board is cinema-specific; the Mind is not) and that prevents the Mind from duplicating the Board.

## 1.5 Position in the Constitutional Architecture

The Creative Mind is a **cognitive layer**, not a pillar, not an agent, not a compiler pass, and not a runtime. It sits between the CIS (input) and the Directorial Board (decision), enriching COM objects with the understanding the Board needs to decide.

```
00  Constitutional Architecture (supreme)
001 Migration Blueprint
002 Directorial Board (cinematic decision authority)
003 CIS (human intent)
004 COM (semantic programming model)
005 Creative Mind (cognitive faculties)        ← this specification
    │
    │ will be followed by
    ▼
006 PKP Architecture (compiled output)
007 PROMETHEUS (rendering runtime)
008 ORACLE (validation)
009 ATLAS (persistence)
```

005 is the last specification that defines the **creative front-end** of the Cinema Production Engine. 006 onward define the **production back-end** (compilation output, rendering, validation, persistence). The Creative Mind is the last layer of reasoning before the compiler takes over.

## 1.6 Differentiation from Adjacent Artifacts

| Artifact | What it is | How the Creative Mind differs |
|----------|-----------|-------------------------------|
| **Director Intelligence (`002`)** | The Directorial Board: 18 cinema-specific directors that make creative decisions and produce the CIR. | The Mind provides the **cognition** the Board consumes to decide. Faculties have no decision authority; directors do. The Board is cinema-specific; the Mind is runtime-independent. The Mind does not produce CIR nodes; the Board does. |
| **COM (`004`)** | The typed object model: the shared language all subsystems speak. | The Mind operates **on** COM objects. Faculties enrich COM objects with understanding (e.g., a Character object enriched with psychological coherence; a Scene object enriched with emotional subtext). The Mind does not define object types; the COM does. |
| **CIR (`002` Part 12)** | The canonical record of creative reasoning: why each decision exists. | The Mind produces the **understanding** that the Board records in the CIR. The CIR is the artifact of the Board's decisions; the Mind's deliberation is the cognitive process that precedes those decisions. The Mind does not write to the CIR; the Board does. |
| **PKP (`001` §5)** | The compiled production knowledge PROMETHEUS executes. | The Mind never touches the PKP. The Mind operates before compilation; the PKP is the output of compilation. |
| **Runtime (PROMETHEUS/ORACLE/ATLAS)** | The execution, validation, and persistence pillars. | The Mind is runtime-independent. It does not render, validate, or persist. It reasons. |
| **Learning (`002` Part 6, Director Memory)** | Persistent creative memory across productions. | The Learning Faculty (Part 3.3.11) produces the cognitive content of Director Memory. ATLAS persists it. The Mind produces; ATLAS stores. |
| **Ontology (GO-001..119)** | The vocabulary of filmmaking: nouns and predicates. | The Mind uses ontology terms in its reasoning. The Meaning Faculty (Part 3.3.1) grounds reasoning in the ontology. The Mind does not define ontology terms; it uses them. |

---

# PART 2: THE CREATIVE MIND

---

## 2.1 Purpose and Responsibilities

**Purpose:** The Creative Mind is the cognitive architecture that transforms human creative intent (CIS) into the enriched understanding the Directorial Board consumes to make creative decisions (CIR). It is the layer of **thinking** between intent and decision.

**Responsibilities:**

1. Interpret the CIS across cognitive domains (meaning, narrative, character, psychology, audience, visual, musical, aesthetic).
2. Enrich COM objects with understanding that is not present in the CIS but is implied by it (e.g., psychological coherence implied by a character's stated goals; emotional subtext implied by a scene's stated objective).
3. Generate alternatives across cognitive domains (the Mind proposes; the Board disposes).
4. Deliberate internally over alternatives, producing trade-off analyses and confidence assessments.
5. Propagate uncertainty and confidence across faculties (a low-confidence psychological interpretation lowers the confidence of downstream narrative interpretations).
6. Surface conflicts between cognitive domains (e.g., a visual interpretation that contradicts a psychological interpretation) for the Board to resolve.
7. Consume ORACLE drift reports and ATLAS memory to refine future reasoning (learning).

**Non-responsibilities (explicit):**

- The Mind does not decide. The Board decides.
- The Mind does not compile. The compiler compiles.
- The Mind does not render. PROMETHEUS renders.
- The Mind does not validate media. ORACLE validates.
- The Mind does not persist. ATLAS persists.
- The Mind does not write to the CIR. The Board writes.
- The Mind does not amend the CIS. The human amends.

## 2.2 Boundaries

| Boundary | Mind authority | Counterparty authority |
|----------|----------------|------------------------|
| Mind ↔ CIS | Reads the CIS; does not amend it. | Human authors and amends the CIS. |
| Mind ↔ COM | Enriches COM objects with understanding; does not define new types. | The COM defines types; the Mind populates them. |
| Mind ↔ Directorial Board | Produces understanding for the Board; does not decide. | The Board decides and writes the CIR. |
| Mind ↔ Compiler | Not directly involved. The compiler reads the CIR, not the Mind's deliberation. | The compiler compiles the Board's decisions. |
| Mind ↔ PROMETHEUS | No relationship. | PROMETHEUS renders the PKP. |
| Mind ↔ ORACLE | Consumes drift reports (for learning); does not validate. | ORACLE validates and reports. |
| Mind ↔ ATLAS | Consumes memory (for reasoning); does not persist. | ATLAS persists. |
| Mind ↔ Ontology | Uses ontology terms; does not define them. | The ontology defines vocabulary. |
| Mind ↔ Constitution | Obeys GFS-000..009. | The constitution governs the Mind. |

## 2.3 Lifecycle

The Creative Mind's lifecycle parallels the production lifecycle but is cognitive, not cal:

```
quiescent → engaged → interpreting → reasoning → deliberating → proposing → (Board decides) → reflecting → learning → quiescent
```

- **quiescent**: no active production.
- **engaged**: a CIS has been pinned; the Mind begins reading it.
- **interpreting**: faculties interpret the CIS across their domains.
- **reasoning**: faculties enrich COM objects and generate alternatives.
- **deliberating**: faculties deliberate internally and with each other (Part 5).
- **proposing**: the Mind presents enriched COM objects and alternatives to the Board.
- **(Board decides)**: the Board produces the CIR; the Mind is not active during decision but may be re-engaged for re-deliberation on conflicts.
- **reflecting**: after the Board's decision (and after ORACLE's validation), the Mind reflects on the quality of its understanding.
- **learning**: the Mind updates its cognitive patterns based on reflection.
- **quiescent**: the production is archived; the Mind returns to rest.

## 2.4 Authority

The Creative Mind has **cognitive authority** — the authority to produce understanding — and **no decision authority**. Cognitive authority means:

- The Mind may enrich COM objects with understanding (e.g., marking a Character's unspoken need, identifying a Scene's emotional subtext).
- The Mind may generate alternatives and trade-off analyses.
- The Mind may flag conflicts between cognitive domains for the Board.
- The Mind may assign confidence levels to its interpretations (using the ADR-004 five-level taxonomy: `explicit / inferred / confirmed / assumed / unknown`).
- The Mind may **not** freeze a COM object, may not authorize a compiler pass, may not override the Board, and may not amend the CIS.

This is the constitutional separation encoded in invariant **I-CM-1**: *The Creative Mind has cognitive authority; the Directorial Board has decision authority. Neither crosses the other's boundary.*

## 2.5 Relationship Map

| Related artifact | Relationship | Direction | Mechanism |
|------------------|-------------|-----------|-----------|
| **CIS** | The Mind reads the CIS to interpret intent. | CIS → Mind | The Mind consumes the pinned CIS version. |
| **COM** | The Mind enriches COM objects with understanding. | Mind → COM | Faculties populate understanding fields on COM objects; the COM defines the types. |
| **Directorial Board** | The Mind produces understanding the Board consumes. | Mind → Board | The Board reads enriched COM objects and the Mind's proposed alternatives. |
| **CIR** | The Mind does not write to the CIR; the Board does. | (none) | The Mind's deliberation is the cognitive precursor to the CIR. |
| **PKP** | The Mind does not touch the PKP. | (none) | The compiler produces the PKP from the CIR. |
| **PROMETHEUS** | No relationship. | (none) | PROMETHEUS renders the PKP. |
| **ORACLE** | The Mind consumes ORACLE's drift reports for learning. | ORACLE → Mind (learning) | Drift reports inform the Reflective and Learning faculties. |
| **ATLAS** | The Mind consumes ATLAS's memory for reasoning. | ATLAS → Mind | The Learning Faculty queries ATLAS for prior understanding. |
| **Ontology** | The Mind uses ontology terms in reasoning. | Ontology → Mind | Faculty reasoning is grounded in GO-001..119 vocabulary. |
| **Constitution** | The Mind obeys the constitution. | Constitution → Mind | GFS-000..009 govern the Mind. |

## 2.6 Runtime Independence

The Creative Mind is **runtime-independent**. It is not specific to cinema. The same faculties that reason about a film's meaning, narrative, characters, psychology, audience, visual language, music, and aesthetics can reason about:

- A **video game's** narrative, characters, emotional arc, visual language, and music.
- A **book's** narrative, characters, psychology, and meaning (with no visual or musical faculties engaged, or engaged differently).
- An **educational course's** learning objectives, narrative (pedagogical structure), audience, and reflection goals.
- A **podcast's** narrative, dialogue, psychology, audience, and audio language.
- A **devotional story's** meaning, narrative, characters, reflection, and music.
- A **commercial's** message, audience, visual language, and aesthetic.

The runtime-specific decision authority is the **Directorial Board** (for cinema) or an analogous decision body for other runtimes (a future "Editorial Board" for books, a "Game Design Board" for games, etc.). The Mind is the shared cognitive layer beneath all such boards.

This is the architectural invariant **I-CM-2**: *The Creative Mind is runtime-independent. Runtime-specific decision authority lives in the Board, not in the Mind.*

The cinema-specific bindings in this specification (e.g., the Visual Faculty's relationship to the Visual Director, the Musical Faculty's relationship to the Music Director) are **projection contracts**: they describe how the cinema runtime's Board consumes each faculty's understanding. Other runtimes define their own projection contracts. The faculties themselves do not change.

This invariant is what makes the Cinema Production Engine's creative architecture generalizable to an Artificial Creative Intelligence platform: the Mind is the platform; the Boards are the runtime-specific applications.

---

# PART 3: CREATIVE FACULTIES

---

## 3.1 Faculty Specification Contract

Every Creative Faculty is specified by a nineteen-field contract. The contract is the cognitive analog of the COM's fourteen-field object contract (`004` Part 2.1) and the Directorial Board's twelve-field director contract (`002` Part 2.3).

| Field | Definition |
|-------|-----------|
| **Purpose** | What cognitive capability the faculty provides, in one sentence. |
| **Mission** | The faculty's enduring mission across all productions and runtimes. |
| **Questions it answers** | The cognitive questions the faculty is equipped to answer. |
| **Responsibilities** | What the faculty is structurally accountable for. |
| **Authority** | The faculty's cognitive authority (always cognitive, never decisional). |
| **Boundaries** | What the faculty may not do. |
| **Consumers** | Which directors (or other runtime decision bodies) consume the faculty's output. |
| **Producers** | Which faculties (or other sources) produce the inputs the faculty consumes. |
| **Inputs** | What the faculty reads (CIS domains, COM objects, ATLAS memory, other faculties' outputs). |
| **Outputs** | What the faculty produces (enriched COM objects, alternatives, trade-off analyses, confidence assessments). |
| **Dependencies** | Which other faculties must reason before this one can. |
| **Knowledge sources** | Ontology terms, ATLAS memory, prior productions, external references the faculty draws on. |
| **Reasoning style** | How the faculty reasons (deductive, inductive, abductive, analogical, intuitive, reflective). |
| **Decision style** | How the faculty's output is shaped for the consuming director (none — faculties do not decide; this field records the *form* of the cognitive output: a ranked alternative set, a confidence-tagged interpretation, a conflict surface). |
| **Collaboration responsibilities** | What the faculty owes to other faculties (e.g., the Psychology Faculty owes the Narrative Faculty a coherent character-state interpretation). |
| **Constraints** | What limits the faculty's reasoning (the CIS's constraints, the constitution, the ontology, the profile). |
| **Examples** | Concrete instances of the faculty's reasoning. |
| **Failure modes** | How the faculty fails (and how failure is detected). |
| **Success metrics** | How the faculty's cognitive quality is assessed (by the Reflective Faculty and by ORACLE's downstream validation). |

## 3.2 Faculty Catalog

The Creative Mind comprises the following first-class Creative Faculties. The catalog is closed: new faculties are added only under governance (Part 10.2). The eleven faculties are the minimum cognitive capability set for the Cinema Production Engine; future runtimes may require additional faculties (e.g., an Interactive Faculty for games), added under governance.

| # | Faculty | Cognitive domain |
|---|---------|------------------|
| F-1 | **Meaning Faculty** | Theme, message, symbolic meaning, the "what it is about" of a work. |
| F-2 | **Narrative Faculty** | Structure, pacing, reveal, setup/payoff, narrative reasoning. |
| F-3 | **Character Faculty** | Character identity, biography, relationships, growth arcs. |
| F-4 | **Psychology Faculty** | Interior life, motivation, emotion, psychological realism. |
| F-5 | **Audience Faculty** | Audience model, reception, engagement, adaptation reasoning. |
| F-6 | **Visual Faculty** | Visual language, composition, color, metaphor, visual coherence. |
| F-7 | **Musical Faculty** | Music's emotional and thematic role, silence as music, sonic identity. |
| F-8 | **Aesthetic Faculty** | The unity of the work's aesthetic across all sensory and narrative domains. |
| F-9 | **Directorial Faculty** | The integration of all faculties' outputs into a coherent directorial understanding. |
| F-10 | **Reflective Faculty** | Self-criticism, quality assessment, learning from the Mind's own reasoning. |
| F-11 | **Learning Faculty** | Memory, precedent, cross-production learning, taste evolution. |

## 3.3 Faculty Details

### 3.3.1 Meaning Faculty

| Field | Value |
|-------|-------|
| Purpose | To determine what a work is *about* — its theme, its message, its symbolic system. |
| Mission | Ensure every creative decision serves the work's meaning; ensure no decision is semantically unanchored. |
| Questions it answers | What is this work about? What does it mean? What does the audience take away? What symbols carry the meaning? Is a proposed decision consistent with the work's meaning? |
| Responsibilities | Interpret the CIS's Theme (D-2) and Message (D-3); ground Motifs and Symbols (`004` §2.3.33–34) in Themes; validate that visual/sonic/narrative metaphors trace to a Theme; flag meaning-drift in any faculty's proposal. |
| Authority | Cognitive authority over meaning. May flag any proposal as meaning-incoherent; may not override the proposal. |
| Boundaries | Does not decide which theme is chosen (the Board decides); does not author symbols (the Visual/Narrative faculties propose them); does not amend the CIS. |
| Consumers | Chief Director (`002` Part 2.3.1), Story Director, Visual Director (for metaphor grounding), Narrative Director. |
| Producers | CIS (D-2, D-3); ATLAS (prior themes via the Learning Faculty); the ontology (GO-116 Creativity, GO-107 Revelation). |
| Inputs | CIS D-2 Theme, D-3 Message, D-21 Reflection Goals; COM Theme, Message, Symbol, Motif objects; ATLAS memory of prior themes. |
| Outputs | Enriched Theme/Message/Symbol/Motif COM objects with meaning-coherence assessments; meaning-drift flags on other faculties' proposals. |
| Dependencies | None (the Meaning Faculty reasons first; other faculties depend on its output). |
| Knowledge sources | GO-116 (Creativity, Innovation & Design Reasoning), GO-107 (Knowledge, Information & Revelation), ATLAS memory. |
| Reasoning style | Interpretive and analogical: the Meaning Faculty reasons by analogy to prior works, by symbolic association, and by thematic coherence checking. |
| Decision style | Outputs a meaning-coherence assessment per COM object, with a confidence level. Does not rank alternatives (that is the Board's job). |
| Collaboration responsibilities | Provides the thematic ground that the Visual, Narrative, and Musical faculties reference. Flags meaning-drift in any faculty's proposal. |
| Constraints | May not contradict the CIS's stated Theme (D-2); if a faculty proposal implies a theme the CIS did not state, the Meaning Faculty flags it for the Board, which may escalate to the human for a CIS amendment. |
| Examples | Given a CIS theme of "the cost of intimacy lost to performance anxiety," the Meaning Faculty interprets a proposed visual motif (a closed door) as consistent (the door symbolizes withdrawal) and flags a proposed upbeat music cue as meaning-incoherent (it contradicts the theme of loss). |
| Failure modes | Over-interpreting (finding meaning the creator did not intend); under-interpreting (missing the theme's implications); meaning-drift (failing to flag a proposal that drifts from the theme). Detected by the Reflective Faculty and by ORACLE's meaning-coherence validation. |
| Success metrics | Every Symbol and Motif traces to a Theme (invariant I-SI-17/18, `004`); zero meaning-drift flags at freeze; ORACLE's meaning-coherence metric (`002` Part 11) within tolerance. |

### 3.3.2 Narrative Faculty

| Field | Value |
|-------|-------|
| Purpose | To reason about narrative structure — how the story is told, in what order, with what reveals and payoffs. |
| Mission | Ensure the narrative structure serves the meaning and produces the intended emotional journey. |
| Questions it answers | How should this story be ordered? Where does this reveal belong? What does this scene's narrative purpose imply for adjacent scenes? Is the pacing curve coherent? Is the setup/payoff graph complete? |
| Responsibilities | Interpret the CIS's Narrative Constraints (D-11) and Emotional Journey (D-4); reason about Act/Sequence/Scene/Beat structure (`004` §2.3.5–9); reason about Reveal/Mystery/Setup/Payoff/Foreshadowing/Callback (`004` §2.3.27–32); validate the setup/payoff graph (invariant I-SI-5); validate that every Scene has a Purpose (I-SI-1). |
| Authority | Cognitive authority over narrative structure. May flag a proposal as structurally incoherent; may not override. |
| Boundaries | Does not decide the narrative structure (the Narrative Director decides); does not author dialogue (the Dialogue Director decides, consuming the Narrative Faculty's understanding of scene purpose). |
| Consumers | Narrative Director (`002` Part 2.3.3), Story Director, Editorial Director. |
| Producers | CIS (D-4, D-11); COM Story, Narrative, Act, Sequence, Scene, Beat, Reveal, Setup, Payoff objects; the Meaning Faculty (for thematic grounding of reveals); ATLAS (prior narrative structures). |
| Inputs | CIS narrative and emotional domains; COM narrative objects; Meaning Faculty's theme interpretations; Psychology Faculty's character-state interpretations (for reveal timing). |
| Outputs | Enriched narrative COM objects with structural-coherence assessments; setup/payoff graph validation; pacing curve analysis; alternative narrative structures with trade-offs. |
| Dependencies | Meaning Faculty (for thematic grounding); Psychology Faculty (for reveal timing relative to character knowledge). |
| Knowledge sources | GO-101 (Narrative), GO-107 (Revelation), GO-111 (Temporal Experience, Editing & Narrative Rhythm), ATLAS memory. |
| Reasoning style | Structural and deductive: the Narrative Faculty reasons about graph completeness (setup→payoff), temporal consistency (precedes), and pacing curves. |
| Decision style | Outputs a structural-coherence assessment and a set of alternative structures with trade-offs. |
| Collaboration responsibilities | Provides the structural ground the Editorial Faculty (if present) and the Directorial Faculty consume. Coordinates with the Psychology Faculty on reveal timing. |
| Constraints | Must honor the CIS's Narrative Constraints (D-11) and Ending Intent (D-20); must satisfy the setup/payoff invariants (I-SI-4/5/6). |
| Examples | Given a CIS with a non-linear constraint, the Narrative Faculty reasons that a flashback structure is consistent and proposes two alternative flashback orderings with trade-offs. It flags a Payoff with no Setup as an invariant violation. |
| Failure modes | Structural incoherence (a setup with no payoff); pacing drift (a curve that violates the CIS's emotional journey); reveal mistiming (a reveal placed before the audience has the context to understand it). Detected by invariant validation and by ORACLE's narrative-coherence metric. |
| Success metrics | Zero structural invariant violations at freeze; pacing curve within the CIS's emotional journey envelope; ORACLE's narrative-coherence metric within tolerance. |

### 3.3.3 Character Faculty

| Field | Value |
|-------|-------|
| Purpose | To reason about who the characters are — identity, biography, relationships, growth arcs. |
| Mission | Ensure every character is a coherent, motivated, distinct entity whose arc serves the meaning. |
| Questions it answers | Who is this character? What do they want? What do they need? How do they relate to others? How do they change? Is a proposed character action consistent with who they are? |
| Responsibilities | Interpret the CIS's Story Intent (D-1) for character implications; reason about Character, Relationship, Goal, Need, Obstacle, Conflict, Decision objects (`004` §2.3.12–18); validate that every Character has a Motivation (I-SI-3); validate the relationship graph is complete (I-SI-29). |
| Authority | Cognitive authority over character identity and coherence. May flag a proposal as character-incoherent; may not override. |
| Boundaries | Does not decide character content (the Character Director decides); does not author dialogue (the Dialogue Director decides). |
| Consumers | Character Director (`002` Part 2.3.4), Psychology Director, Narrative Director, Dialogue Director, Performance Director. |
| Producers | CIS (D-1 for named characters); COM Character, Relationship objects; ATLAS (prior character definitions for reuse). |
| Inputs | CIS story intent; COM character objects; Meaning Faculty's theme interpretations (for arc-thematic alignment); ATLAS memory. |
| Outputs | Enriched Character/Relationship COM objects with coherence assessments; character arc analyses; alternative character interpretations with trade-offs. |
| Dependencies | Meaning Faculty (for arc-thematic alignment). |
| Knowledge sources | GO-104 (Character), GO-105 (World & Environment), ATLAS memory. |
| Reasoning style | Constructive and analogical: the Character Faculty constructs character identity from fragments (biography, goal, voice) and reasons by analogy to prior characters. |
| Decision style | Outputs a coherence assessment and alternative character interpretations. |
| Collaboration responsibilities | Provides the character ground the Psychology, Dialogue, and Performance faculties consume. Coordinates with the Narrative Faculty on arc-narrative alignment. |
| Constraints | Must honor the CIS's stated characters (if any); must satisfy the character invariants (I-SI-3, I-SI-22, I-SI-28, I-SI-29). |
| Examples | Given a CIS with a protagonist named "Aman," the Character Faculty reasons that his stated goal (reconnect with his wife) implies a need (psychological safety) that he does not name, and enriches the Character object with the Need, flagged as `inferred`. |
| Failure modes | Character incoherence (a character acting against their established identity); relationship graph gaps (a missing relationship entry); arc-internal contradiction (a character growing and un-growing without cause). Detected by invariant validation and by ORACLE's character-depth and consistency metrics. |
| Success metrics | Zero character invariant violations at freeze; relationship graph complete; ORACLE's character-depth and consistency metrics within tolerance. |

### 3.3.4 Psychology Faculty

| Field | Value |
|-------|-------|
| Purpose | To reason about the interior life of characters and the psychological realism of the work. |
| Mission | Ensure the work is psychologically credible and that the emotional architecture is internally consistent. |
| Questions it answers | What does this character feel here? Why? Is this emotional transition plausible? What is the subtext of this scene? Is the character's behavior psychologically realistic given their established psychology? |
| Responsibilities | Interpret the CIS's Emotional Journey (D-4) and Emotion Transition Graph (D-5); reason about Emotion, Emotion Transition, Emotional Journey, Need, Memory objects (`004` §2.3.22–25); validate that every Emotion Transition has a source and target (I-SI-7); validate the Emotional Journey's coverage (I-SI-26). |
| Authority | Cognitive authority over psychological interpretation. May flag a proposal as psychologically implausible; may not override. |
| Boundaries | Does not decide psychological content (the Psychology Director decides); does not author dialogue (the Dialogue Director decides, consuming the Psychology Faculty's subtext interpretations). |
| Consumers | Psychology Director (`002` Part 2.3.5), Performance Director, Dialogue Director, Narrative Director. |
| Producers | CIS (D-4, D-5); COM Emotion, Emotion Transition, Need, Memory objects; Character Faculty (for character identity grounding). |
| Inputs | CIS emotional domains; COM emotional objects; Character Faculty's character interpretations; Meaning Faculty's thematic grounding. |
| Outputs | Enriched Emotion/Emotion Transition COM objects with plausibility assessments; subtext interpretations for scenes; psychological-realism flags on character actions. |
| Dependencies | Character Faculty (for character grounding); Meaning Faculty (for emotional-thematic alignment). |
| Knowledge sources | GO-103 (Human Psychology & Behavior), GO-102 (Audience Experience), ATLAS memory. |
| Reasoning style | Empathic and abductive: the Psychology Faculty reasons from observed behavior to inferred interior state (abduction) and from stated emotion to plausible transition (empathic simulation). |
| Decision style | Outputs a plausibility assessment and subtext interpretation per scene. |
| Collaboration responsibilities | Provides the psychological ground the Dialogue, Performance, and Narrative faculties consume. Coordinates with the Audience Faculty on whether the emotional journey is achievable for the target audience. |
| Constraints | Must honor the CIS's Emotional Journey (D-4) and Emotion Transition Graph (D-5); must satisfy the emotional invariants (I-SI-7, I-SI-26). |
| Examples | Given a scene where a character says "I'm fine," the Psychology Faculty interprets the subtext as "I am not fine but cannot admit it" based on the character's established avoidant attachment style, and enriches the Dialogue object with the subtext, flagged as `inferred`. |
| Failure modes | Psychological implausibility (a character's emotional transition has no psychological path); subtext misattribution (reading subtext that the character's psychology does not support); emotional-journey drift (the interpreted journey diverges from the CIS's stated journey). Detected by the Reflective Faculty and by ORACLE's psychological-realism metric. |
| Success metrics | Zero emotional invariant violations at freeze; emotional journey within the CIS's envelope; ORACLE's psychological-realism metric within tolerance. |

### 3.3.5 Audience Faculty

| Field | Value |
|-------|-------|
| Purpose | To reason about the audience — who they are, what they expect, how they will receive the work. |
| Mission | Ensure the work is receivable by its intended audience without redefining the creator's intent. |
| Questions it answers | Will this audience understand this? Will this audience feel this? Is this pacing appropriate for this audience's attention pattern? Is this cultural reference accessible? Does this adaptation preserve intent? |
| Responsibilities | Interpret the CIS's Audience (D-6); reason about the Audience COM object (`004` §2.3.45); validate that adaptations do not redefine intent (I-AD-1, I-SI-30); reason about audience-specific pacing, register, and cultural accessibility. |
| Authority | Cognitive authority over audience reception. May flag a proposal as audience-inaccessible; may not override. |
| Boundaries | Does not decide audience adaptations (the Platform Director decides); does not redefine intent (the audience shapes realization, not intent — `003` I-AD-1). |
| Consumers | Platform Director (`002` Part 2.3.16), Psychology Director, Narrative Director, Dialogue Director. |
| Producers | CIS (D-6); COM Audience object; ATLAS (prior audience models). |
| Inputs | CIS audience domain; COM Audience object; Psychology Faculty's emotional journey (for receivability); Narrative Faculty's pacing curve (for attention-pattern fit). |
| Outputs | Audience-receivability assessments per scene/element; adaptation recommendations (without intent change); cultural-accessibility flags. |
| Dependencies | Psychology Faculty (for emotional receivability); Narrative Faculty (for pacing fit). |
| Knowledge sources | GO-102 (Audience Experience), ATLAS memory. |
| Reasoning style | Empathic and inductive: the Audience Faculty reasons from the audience's stated characteristics to likely reception patterns. |
| Decision style | Outputs a receivability assessment and adaptation recommendations. |
| Collaboration responsibilities | Provides the audience ground all faculties consume for adaptation. Coordinates with the Aesthetic Faculty on whether the work's aesthetic is accessible to the audience. |
| Constraints | Must honor the CIS's Audience (D-6); must not propose adaptations that redefine intent (I-AD-1). |
| Examples | Given a CIS audience of "young adults, intermittent attention, YouTube consumption," the Audience Faculty flags a proposed 90-second static shot as audience-inaccessible and recommends a tighter cut, without changing the scene's emotional intent. |
| Failure modes | Audience misjudgment (overestimating the audience's patience or cultural familiarity); intent-drift in adaptation (proposing an adaptation that changes intent); receivability failure (the work is inaccessible to its audience). Detected by the Reflective Faculty and by ORACLE's audience-engagement and retention metrics. |
| Success metrics | Zero intent-drift flags; ORACLE's audience-engagement and retention-prediction metrics within tolerance. |

### 3.3.6 Visual Faculty

| Field | Value |
|-------|-------|
| Purpose | To reason about the visual language of the work — composition, color, metaphor, visual coherence. |
| Mission | Ensure the visual language serves the meaning, the emotion, and the audience without inventing creative decisions. |
| Questions it answers | What visual language suits this theme? Does this composition serve the scene's emotional goal? Is this color language consistent across scenes? Does this visual metaphor trace to a theme? |
| Responsibilities | Interpret the CIS's Visual Expectations (D-17); reason about Visual Language, Shot, Camera, Lighting, Motif, Symbol objects (`004` §2.3.35–38, 33–34); validate that every Shot has a motivation (I-SI-20); validate that Symbols and Visual Motifs reference a Theme (I-SI-17/18). |
| Authority | Cognitive authority over visual interpretation. May flag a proposal as visually incoherent; may not override. |
| Boundaries | Does not decide visual content (the Visual/Cinematography/Lighting Directors decide); does not author prompts (the Prompt Compiler projects, late). |
| Consumers | Visual Director (`002` Part 2.3.8), Cinematography Director, Lighting Director, Production Designer. |
| Producers | CIS (D-17); COM Visual Language, Shot, Camera, Lighting, Motif, Symbol objects; Meaning Faculty (for metaphor grounding); Psychology Faculty (for emotion-color alignment). |
| Inputs | CIS visual expectations; COM visual objects; Meaning Faculty's theme interpretations; Psychology Faculty's emotional interpretations. |
| Outputs | Enriched visual COM objects with coherence assessments; visual-metaphor grounding (linking metaphors to themes); alternative visual languages with trade-offs. |
| Dependencies | Meaning Faculty (for metaphor grounding); Psychology Faculty (for emotion-visual alignment). |
| Knowledge sources | GO-109 (Visual Expression, Cinematography & Composition), GO-116 (Creativity), ATLAS memory. |
| Reasoning style | Analogical and aesthetic: the Visual Faculty reasons by analogy to visual traditions and by aesthetic coherence. |
| Decision style | Outputs a visual-coherence assessment and alternative visual languages. |
| Collaboration responsibilities | Provides the visual ground the Directorial Faculty integrates. Coordinates with the Musical Faculty on audio-visual coherence. |
| Constraints | Must honor the CIS's Visual Expectations (D-17) and Presentation Profile (D-23); must satisfy the visual invariants (I-SI-9, I-SI-17/18, I-SI-20). |
| Examples | Given a scene with emotional goal "grief," the Visual Faculty reasons that a desaturated color language and a static, wide composition serve the emotion, and enriches the Scene's Visual Language with these interpretations, flagged as `inferred` from the emotional goal. |
| Failure modes | Visual incoherence (a visual language that contradicts the scene's emotion); ungrounded metaphor (a visual metaphor with no theme); visual drift across scenes (inconsistent color language). Detected by invariant validation and by ORACLE's visual-consistency and cinematic-realism metrics. |
| Success metrics | Zero visual invariant violations at freeze; visual coherence across scenes; ORACLE's visual-consistency metric within tolerance. |

### 3.3.7 Musical Faculty

| Field | Value |
|-------|-------|
| Purpose | To reason about the role of music and sound in the work — the sonic identity, the emotional function of music, silence as music. |
| Mission | Ensure the sonic language serves the meaning, the emotion, and the narrative without inventing creative decisions. |
| Questions it answers | Where does music belong? Where does silence belong? What is the emotional function of music here? Is the sonic identity consistent? Does the music serve the theme? |
| Responsibilities | Interpret the CIS's Music Expectations (D-19) and Audio Expectations (D-18); reason about Music Theme, Soundscape, Silence objects (`004` §2.3.41–42, 21); validate that every Silence has a purpose (I-SI-19); reason about silence-as-music and silence-as-beat (`002` Part 5.2). |
| Authority | Cognitive authority over musical interpretation. May flag a proposal as sonically incoherent; may not override. |
| Boundaries | Does not decide musical content (the Music/Sound Directors decide); does not author music (PROMETHEUS realizes). |
| Consumers | Music Director (`002` Part 2.3.13), Sound Director, Audio Director. |
| Producers | CIS (D-18, D-19); COM Music Theme, Soundscape, Silence objects; Psychology Faculty (for emotion-music alignment); Narrative Faculty (for cue timing). |
| Inputs | CIS audio/music domains; COM audio objects; Psychology Faculty's emotional interpretations; Narrative Faculty's pacing and beat structure. |
| Outputs | Enriched audio COM objects with coherence assessments; music/silence cue reasoning; alternative sonic identities with trade-offs. |
| Dependencies | Psychology Faculty (for emotion-music alignment); Narrative Faculty (for cue timing). |
| Knowledge sources | GO-110 (Audio, Music, Sound Design & Silence), ATLAS memory. |
| Reasoning style | Emotional and structural: the Musical Faculty reasons about music's emotional function and its structural timing. |
| Decision style | Outputs a sonic-coherence assessment and alternative sonic identities. |
| Collaboration responsibilities | Provides the sonic ground the Directorial Faculty integrates. Coordinates with the Visual Faculty on audio-visual coherence and with the Narrative Faculty on cue timing. |
| Constraints | Must honor the CIS's Audio/Music Expectations (D-18/D-19) and Presentation Profile (D-23); must satisfy the silence invariant (I-SI-19). |
| Examples | Given a scene with emotional goal "tension," the Musical Faculty reasons that a low, sustained drone serves the tension and that a silence at the scene's midpoint would amplify it, and enriches the Scene's Soundscape with these interpretations. |
| Failure modes | Sonic incoherence (music that contradicts the scene's emotion); silence misplacement (silence without purpose); sonic drift across scenes. Detected by invariant validation and by ORACLE's audio-quality metric. |
| Success metrics | Zero silence invariant violations at freeze; sonic coherence across scenes; ORACLE's audio-quality metric within tolerance. |

### 3.3.8 Aesthetic Faculty

| Field | Value |
|-------|-------|
| Purpose | To reason about the aesthetic unity of the work — the coherence across all sensory and narrative domains. |
| Mission | Ensure the work is aesthetically one, not a collage of unrelated domain choices. |
| Questions it answers | Do the visual, sonic, narrative, and emotional languages cohere? Is there a unified aesthetic? Does each domain's choice serve the others? Is the work's tone consistent? |
| Responsibilities | Integrate the interpretations of the Visual, Musical, Narrative, and Psychology faculties into an aesthetic-whole assessment; reason about cross-domain coherence; flag aesthetic disunity. |
| Authority | Cognitive authority over aesthetic coherence. May flag a proposal as aesthetically disunified; may not override. |
| Boundaries | Does not decide any domain's content (the domain directors decide); does not impose an aesthetic (the Board decides). |
| Consumers | Chief Director (`002` Part 2.3.1), Visual Director, Audio Director, Editorial Director. |
| Producers | All other faculties (the Aesthetic Faculty is a meta-faculty that integrates). |
| Inputs | All faculties' enriched COM objects; the CIS's Theme and Presentation Profile. |
| Outputs | Aesthetic-coherence assessments; cross-domain coherence flags; unified-aesthetic proposals. |
| Dependencies | All other faculties (it integrates their outputs). |
| Knowledge sources | GO-116 (Creativity), GO-109 (Visual), GO-110 (Audio), GO-111 (Temporal), ATLAS memory. |
| Reasoning style | Integrative and holistic: the Aesthetic Faculty reasons about the whole, not any part. |
| Decision style | Outputs an aesthetic-coherence assessment per production and per scene. |
| Collaboration responsibilities | Synthesizes all faculties' outputs into an aesthetic-whole view for the Directorial Faculty. |
| Constraints | Must honor the CIS's Theme (D-2) and Presentation Profile (D-23); must not impose an aesthetic the CIS contradicts. |
| Examples | Given a Visual Faculty proposal for a desaturated, static language and a Musical Faculty proposal for an upbeat, rhythmic language, the Aesthetic Faculty flags the combination as aesthetically disunified and recommends the Board resolve the conflict. |
| Failure modes | Aesthetic disunity (domains pulling in different directions); over-imposition (the faculty imposing an aesthetic that contradicts the CIS); false coherence (declaring coherence where there is none). Detected by the Reflective Faculty and by ORACLE's cinematic-realism metric. |
| Success metrics | Zero aesthetic-disunity flags at freeze; ORACLE's cinematic-realism metric within tolerance. |

### 3.3.9 Directorial Faculty

| Field | Value |
|-------|-------|
| Purpose | To integrate all faculties' outputs into a coherent directorial understanding the Board can consume. |
| Mission | Be the cognitive bridge between the faculties' understanding and the Board's decisions. |
| Questions it answers | What does the totality of the faculties' understanding imply for the directorial choices? Which alternatives are most coherent across all domains? Where do the faculties disagree, and what does the Board need to resolve? |
| Responsibilities | Synthesize the faculties' enriched COM objects and alternatives into a unified directorial understanding; surface cross-faculty conflicts for the Board; present the trade-off landscape the Board decides within. |
| Authority | Cognitive authority over integration. May not decide; may only integrate. |
| Boundaries | Does not decide (the Board decides); does not impose a synthesis (the Board may reject it). |
| Consumers | The Directorial Board (all directors, via the Chief Director). |
| Producers | All other faculties (it integrates their outputs). |
| Inputs | All faculties' enriched COM objects; all faculties' alternatives and trade-off analyses; the Aesthetic Faculty's coherence assessments. |
| Outputs | A unified directorial understanding per production and per scene; a conflict surface listing cross-faculty disagreements; a ranked alternative set per decision point. |
| Dependencies | All other faculties (it integrates their outputs). |
| Knowledge sources | All faculty knowledge sources; GO-116 (Creativity). |
| Reasoning style | Integrative and prioritizing: the Directorial Faculty reasons about which alternatives best satisfy the totality of the faculties' understanding. |
| Decision style | Outputs a ranked alternative set and a conflict surface. The Board chooses. |
| Collaboration responsibilities | Presents the faculties' understanding to the Board in a form the Board can decide on. |
| Constraints | Must present all alternatives, not only the faculty's preferred one; must surface all conflicts, not hide them. |
| Examples | Given the Visual Faculty's proposal for desaturated visuals and the Musical Faculty's proposal for an upbeat score, the Directorial Faculty presents both to the Board as a conflict, with the Aesthetic Faculty's disunity flag, and ranks three resolution alternatives (adjust the visuals, adjust the music, accept the contrast as intentional). |
| Failure modes | Integration failure (missing a faculty's output); conflict suppression (hiding a disagreement); premature convergence (presenting one alternative as the only option). Detected by the Reflective Faculty and by Board feedback. |
| Success metrics | All faculties' outputs represented in the directorial understanding; all conflicts surfaced; the Board's decisions traceable to the faculty understanding that informed them. |

### 3.3.10 Reflective Faculty

| Field | Value |
|-------|-------|
| Purpose | To reason about the quality of the Mind's own reasoning — self-criticism, quality assessment, learning preparation. |
| Mission | Ensure the Mind's cognitive output is as good as it can be, and that the Mind learns from its own successes and failures. |
| Questions it answers | Was this interpretation well-supported? Was this alternative set rich enough? Did we miss a conflict? Did we converge too early? What should we learn from this production? |
| Responsibilities | Review the Mind's enriched COM objects, alternatives, and conflict surfaces for cognitive quality; flag low-confidence interpretations for the Board's attention; prepare learning inputs for the Learning Faculty. |
| Authority | Cognitive authority over self-assessment. May flag the Mind's own output as low-quality; may not override the Board. |
| Boundaries | Does not decide (the Board decides); does not amend the CIS; does not rewrite other faculties' outputs (it flags, they revise). |
| Consumers | The Learning Faculty; the Directorial Board (for low-confidence flags); the Chief Director. |
| Producers | All other faculties (it reviews their outputs). |
| Inputs | All faculties' enriched COM objects and alternatives; ORACLE's drift reports (post-render, for learning); the Board's decisions (for understanding how the Mind's output was used). |
| Outputs | Cognitive-quality assessments; low-confidence flags; learning inputs for the Learning Faculty. |
| Dependencies | All other faculties (it reviews their outputs). |
| Knowledge sources | GO-116 (Creativity), ATLAS memory (prior reflections). |
| Reasoning style | Critical and metacognitive: the Reflective Faculty reasons about the Mind's own reasoning. |
| Decision style | Outputs a quality assessment and learning inputs. |
| Collaboration responsibilities | Provides the self-assessment the Learning Faculty consumes to update the Mind's cognitive patterns. |
| Constraints | Must be honest (may not suppress a low-confidence flag); must be constructive (flagging for improvement, not blame). |
| Examples | After the Mind proposes a character interpretation, the Reflective Faculty reviews the interpretation's evidence, finds it supported by only one CIS passage (low confidence), flags it as `assumed`, and prepares a learning input: "character interpretations grounded in a single CIS passage should be flagged `assumed`." |
| Failure modes | Self-criticism failure (failing to flag a low-quality output); over-criticism (flagging high-quality outputs, paralyzing the Mind); learning-input absence (failing to prepare learning inputs). Detected by the Learning Faculty and by ORACLE's downstream validation. |
| Success metrics | All low-confidence interpretations flagged; zero unflagged low-quality outputs at freeze; learning inputs produced for every production. |

### 3.3.11 Learning Faculty

| Field | Value |
|-------|-------|
| Purpose | To reason about what the Mind should learn from this and prior productions — memory, precedent, taste evolution. |
| Mission | Ensure the Mind's cognitive quality improves over time and across productions. |
| Questions it answers | What should we remember from this production? What patterns recur? What did we get wrong? How should our reasoning evolve? What prior productions are relevant to the current one? |
| Responsibilities | Consume the Reflective Faculty's learning inputs; query ATLAS for prior productions; provide precedent to other faculties during reasoning; update the Mind's cognitive patterns (stored in ATLAS). |
| Authority | Cognitive authority over learning. May propose cognitive-pattern updates; may not impose them without governance (Part 10.2). |
| Boundaries | Does not decide (the Board decides); does not persist (ATLAS persists); does not amend the constitution or the ontology. |
| Consumers | All other faculties (for precedent during reasoning); the governance framework (for cognitive-pattern evolution). |
| Producers | The Reflective Faculty (learning inputs); ATLAS (prior productions); ORACLE (drift reports). |
| Inputs | Reflective Faculty's learning inputs; ATLAS memory; ORACLE's drift reports. |
| Outputs | Precedent provided to faculties during reasoning; cognitive-pattern update proposals (governed). |
| Dependencies | The Reflective Faculty (for learning inputs); ATLAS (for memory). |
| Knowledge sources | ATLAS memory; the ontology (for grounding learning in vocabulary). |
| Reasoning style | Inductive and evolutionary: the Learning Faculty reasons from instances to patterns and from patterns to updated cognitive defaults. |
| Decision style | Outputs precedent (during reasoning) and pattern-update proposals (post-production). |
| Collaboration responsibilities | Provides precedent to all faculties; ensures the Mind's reasoning is informed by prior productions. |
| Constraints | Must not propose patterns that contradict the constitution or the ontology; pattern updates require governance approval. |
| Examples | During reasoning on a new production, the Learning Faculty provides the Character Faculty with three prior character interpretations from ATLAS that share the new character's attachment style, enabling the Character Faculty to reason by analogy. Post-production, the Learning Faculty proposes a cognitive-pattern update: "characters with avoidant attachment benefit from subtext-flagged dialogue." |
| Failure modes | Learning failure (failing to update patterns from evidence); precedent misapplication (applying a prior production's pattern where it does not fit); memory overload (providing too much precedent, drowning the reasoning faculty). Detected by the Reflective Faculty and by long-term quality trends. |
| Success metrics | Cognitive quality improves across productions; precedent provided where relevant; pattern updates governed and traceable. |

---

# PART 4: FACULTY COLLABORATION ARCHITECTURE

---

## 4.1 Cognitive Interaction, Not Workflow

Faculty collaboration is **not a workflow**. A workflow is a sequence of steps with control flow; faculty collaboration is a **cognitive interaction model** — a set of interactions through which faculties enrich each other's understanding. The distinction matters because a workflow would impose a fixed order (Meaning → Narrative → Character → ...), while real cognition is iterative, recursive, and concurrent: the Narrative Faculty may reason, then the Psychology Faculty, then the Narrative Faculty re-reasons with the Psychology Faculty's output, then the Meaning Faculty re-grounds the Narrative Faculty's revised structure.

The collaboration model defines *how* faculties interact, not *when*. The order is emergent, driven by dependencies (Part 3.3 "Dependencies" field) and by deliberation (Part 5).

## 4.2 Knowledge Exchange

Faculties exchange knowledge through **enriched COM objects**, not through messages. When the Psychology Faculty interprets a character's subtext, it does not send a message to the Dialogue Faculty; it enriches the relevant Dialogue COM object with a `subtext` field (flagged as `inferred` with a confidence level). The Dialogue Faculty reads the enriched object and reasons from it.

This is the cognitive-layer application of `004` Part 1.5: the COM is the shared language; faculties communicate by enriching the same objects. The benefit is that faculty interaction is fully traceable: every enrichment carries provenance (which faculty enriched it, when, from what evidence), and the Board sees the full enrichment history when it decides.

Knowledge exchange is governed by three rules:

1. **Enrichment is additive.** A faculty may add an interpretation; it may not overwrite another faculty's interpretation. Conflicting interpretations coexist as alternatives; the Board resolves.
2. **Enrichment is provenanced.** Every enrichment carries the enriching faculty's identity, the input it reasoned from, and a confidence level.
3. **Enrichment is visible.** All faculties see all enrichments. There are no private faculty states.

## 4.3 COM Enrichment

COM enrichment is the primary product of faculty collaboration. The enrichment model:

| Enrichment type | What it adds | Example | By which faculty |
|-----------------|-------------|---------|------------------|
| **Interpretation** | A cognitive interpretation of a COM object's meaning. | A Dialogue object enriched with `subtext: "I am not fine but cannot admit it"`. | Psychology Faculty. |
| **Implication** | An implication of a COM object that the CIS did not state. | A Character object enriched with `need: "psychological safety"`, implied by the stated goal of "reconnect." | Character Faculty. |
| **Coherence assessment** | A judgment of the object's coherence with its dependencies. | A Shot object enriched with `coherence: "consistent with the scene's emotional goal"`. | Visual Faculty. |
| **Alternative** | An alternative interpretation or structure. | A Scene object enriched with `alternative_structures: [linear, flashback, parallel]`. | Narrative Faculty. |
| **Conflict flag** | A flag indicating a conflict with another faculty's enrichment. | A Music cue enriched with `conflict: "contradicts the Visual Faculty's static-composition interpretation"`. | Aesthetic Faculty. |
| **Confidence assessment** | A confidence level for the enrichment. | Any enrichment carrying `confidence: inferred`. | All faculties. |

Enrichments are the cognitive layer's contribution to the COM. The Board reads the enriched COM objects and decides; the compiler compiles the Board's decisions; the COM's enrichment history is preserved in ATLAS for learning.

## 4.4 Disagreement and Resolution

Faculty disagreements are **cognitive**, not procedural. A disagreement occurs when two faculties' enrichments of the same or related COM objects are incompatible (e.g., the Visual Faculty proposes a static composition; the Musical Faculty proposes an upbeat score; the Aesthetic Faculty flags the combination as disunified).

Resolution mechanisms, in order:

1. **Negotiation.** The disagreeing faculties re-reason with each other's enrichments visible. One may revise its enrichment in light of the other's. This is the default; most disagreements resolve here.
2. **Aesthetic Faculty mediation.** If negotiation does not resolve, the Aesthetic Faculty reasons about the disagreement from an integrative perspective and proposes a coherence-preserving resolution.
3. **Directorial Faculty surfacing.** If mediation does not resolve, the Directorial Faculty surfaces the disagreement to the Board as a conflict (per `002` Part 8, conflict resolution). The Board resolves; the faculties do not.
4. **Human intervention.** If the Board declares the conflict undecidable on creative grounds, the conflict escalates to the human (`002` Part 8.2.7).

At no point does a faculty override another faculty. Faculties have cognitive authority, not decision authority (I-CM-1).

## 4.5 Consensus and Convergence

**Consensus** among faculties is the state in which no faculty flags a conflict with the current set of enrichments. Consensus does not require unanimity of interpretation — multiple interpretations may coexist as alternatives. Consensus requires only that no faculty declares another's enrichment incompatible with its own domain.

**Convergence** is the process by which the Mind moves from many alternatives to a smaller set the Board can decide among. Convergence is driven by:

- The faculties' trade-off analyses (eliminating alternatives that serve fewer domains).
- The Aesthetic Faculty's coherence assessments (eliminating aesthetically disunified alternatives).
- The Reflective Faculty's confidence assessments (eliminating low-confidence alternatives).

Convergence does not reach a single option — the Board chooses. The Mind's job is to converge to a *decidable set*, not to a *decision*.

## 4.6 Uncertainty and Confidence Propagation

Every faculty enrichment carries a confidence level (ADR-004: `explicit / inferred / confirmed / assumed / unknown`). Confidence propagates:

- **Downstream.** A low-confidence enrichment lowers the confidence of enrichments that depend on it. If the Character Faculty's `need` enrichment is `inferred`, the Psychology Faculty's subtext enrichment grounded on that need is at most `inferred`.
- **Across domains.** A low-confidence enrichment in one domain flags related enrichments in other domains. A low-confidence character interpretation flags the dialogue that character speaks.

Propagation is tracked by the Directorial Faculty, which presents the confidence landscape to the Board. The Board may require higher confidence for high-stakes decisions (per `002` Part 8.2.5).

## 4.7 Creative Deadlock and Creative Convergence

**Creative deadlock** is the state in which faculties disagree, negotiation and mediation fail, and the Directorial Faculty cannot surface a decidable set to the Board. Deadlock is not a failure; it is a signal that the CIS does not contain enough intent to decide. Deadlock escalates to the Board and, if the Board cannot resolve, to the human for a CIS amendment.

**Creative convergence** is the state in which the faculties have enriched the COM objects, converged to a decidable alternative set, surfaced all conflicts, and propagated confidence. At convergence, the Directorial Faculty presents the understanding to the Board, and the Board decides.

---

# PART 5: CREATIVE DELIBERATION

---

## 5.1 Why Internal Deliberation

Great creativity is not instantaneous. A first interpretation is rarely the best; a first alternative is rarely the only one. Internal deliberation — the Mind's structured process of generating, evaluating, and refining interpretations — is what separates considered creativity from reflexive generation.

Deliberation is also what makes creativity auditable. A first interpretation is opaque (why this one?); a deliberated interpretation carries the alternatives considered, the trade-offs evaluated, and the confidence assessed. This is the cognitive-layer counterpart of the CIR's `alternatives` and `rationale` fields (`002` Part 3.2): the Mind's deliberation produces the cognitive content the Board records in the CIR.

## 5.2 The Deliberation Arc

The Mind's internal deliberation follows an arc. The arc is not a workflow (it is iterative and recursive); it is a description of the cognitive moves the Mind makes.

| Move | What it does | COM effect |
|------|-------------|------------|
| **Observation** | The Mind reads the CIS and the current COM state. | None (read-only). |
| **Interpretation** | Faculties interpret the CIS across their domains. | COM objects enriched with interpretations. |
| **Analysis** | Faculties analyze the interpretations for coherence, conflict, and gaps. | Coherence assessments; conflict flags; gap flags. |
| **Alternative generation** | Faculties generate alternatives to their interpretations. | COM objects enriched with alternatives. |
| **Evaluation** | Faculties evaluate alternatives against the CIS, the ontology, and each other. | Trade-off analyses attached to alternatives. |
| **Trade-off analysis** | The Directorial Faculty synthesizes evaluations into a trade-off landscape. | A ranked alternative set per decision point. |
| **Reflection** | The Reflective Faculty reviews the Mind's output for quality. | Quality assessments; low-confidence flags. |
| **Selection (cognitive)** | The Directorial Faculty converges to a decidable set. | A decidable alternative set presented to the Board. |
| **Confidence** | All enrichments carry confidence levels. | Confidence propagated across enrichments. |
| **Approval (cognitive)** | The Mind's cognitive output is ready for the Board. | The Directorial Faculty declares readiness. |
| **Revision** | On Board feedback or conflict, the Mind re-deliberates. | Enrichments revised; alternatives regenerated. |
| **Self-criticism** | The Reflective Faculty criticizes the Mind's output. | Criticism recorded for learning. |
| **Self-improvement** | The Learning Faculty updates cognitive patterns. | Patterns updated (governed). |
| **Creative debate** | Faculties debate alternatives (Part 4.4). | Debate recorded in enrichment provenance. |
| **Creative convergence** | The Mind converges to a decidable set (Part 4.7). | Converged set presented to the Board. |
| **Creative intuition** | A faculty forms an interpretation that is not fully deductive — an intuitive leap grounded in experience (ATLAS memory). | Intuitive enrichments flagged as `assumed` or `inferred` with the intuition's source. |

The arc is not linear. Observation may recur after interpretation (the Mind sees new implications). Alternative generation may recur after evaluation (new alternatives emerge from evaluation). Reflection may trigger revision at any point. The arc is a description of the cognitive moves available to the Mind, not a sequence imposed on it.

## 5.3 Iterative Creativity

Creativity is iterative because understanding deepens with each pass. The first interpretation of a character may be shallow (based on the CIS's stated goal); the second, after the Psychology Faculty reasons about the character's implied need, is deeper; the third, after the Narrative Faculty reasons about the character's arc, is deeper still.

Iteration is bounded by convergence: the Mind iterates until the Directorial Faculty declares a decidable set, or until creative deadlock. Iteration is not infinite; the Reflective Faculty flags diminishing returns, and the Directorial Faculty may declare "good enough to decide" when further iteration would not improve the Board's decision.

---

# PART 6: CREATIVE AUTHORITY

---

## 6.1 Faculty Ownership Map

Each cognitive domain has a home faculty that owns the authoritative interpretation. Other faculties may contribute, but the home faculty's interpretation is the default the Board reads.

| Domain | Home faculty | Consuming director(s) (`002` Part 2.3) |
|--------|-------------|----------------------------------------|
| Meaning (theme, message, symbolism) | Meaning Faculty | Chief Director, Story Director, Visual Director. |
| Narrative (structure, pacing, reveals) | Narrative Faculty | Narrative Director, Editorial Director, Story Director. |
| Characters (identity, relationships, arcs) | Character Faculty | Character Director, Narrative Director. |
| Psychology (interiority, emotion, subtext) | Psychology Faculty | Psychology Director, Performance Director, Dialogue Director. |
| Emotion (emotional journey, transitions) | Psychology Faculty | Psychology Director, Editorial Director, Music Director. |
| Audience (reception, adaptation) | Audience Faculty | Platform Director, Psychology Director. |
| Visual language (composition, color, metaphor) | Visual Faculty | Visual Director, Cinematography Director, Lighting Director, Production Designer. |
| Music (sonic identity, music's role) | Musical Faculty | Music Director, Sound Director, Audio Director. |
| Aesthetics (cross-domain unity) | Aesthetic Faculty | Chief Director, Visual Director, Audio Director, Editorial Director. |
| Directorial integration | Directorial Faculty | The Directorial Board (all directors). |
| Reflection (self-assessment) | Reflective Faculty | The Learning Faculty; the Board (for low-confidence flags). |
| Learning (memory, precedent) | Learning Faculty | All faculties (for precedent); governance (for pattern updates). |
| Memory (character memory, cross-production memory) | Learning Faculty (cross-production) and Psychology Faculty (character memory) | Character Director, Psychology Director. |
| Experience (audience experience whole) | Aesthetic Faculty + Audience Faculty | Chief Director. |
| Innovation (novel alternatives) | All faculties (the Mind's creative evolution); the Learning Faculty (for pattern updates). | The Board (which may select novel alternatives). |
| Ethics (ethical coherence) | Meaning Faculty (for ethical meaning) + the CIS's Ethical Constraints (D-22) | Chief Director; the CIS Validator (pre-Mind). |
| Constraints (creative constraints) | Not a faculty responsibility — constraints are CIS-authored (`003` D-22) and enforced by the CIS Validator, the Board, and ORACLE. The Mind honors constraints; it does not own them. | CIS Validator; Board; ORACLE. |

## 6.2 Authority Types

| Authority type | Holder | Scope |
|----------------|--------|-------|
| **Cognitive authority** | Faculties | Producing understanding (interpretations, alternatives, trade-offs, confidence). |
| **Decision authority** | The Directorial Board | Making creative decisions; writing the CIR. |
| **Shared ownership** | Multiple faculties over a domain | When a domain spans multiple faculties (e.g., Emotion is shared by Psychology and Narrative). The home faculty owns the default; others contribute alternatives. |
| **Delegated authority** | A faculty may delegate a sub-domain to another faculty | E.g., the Psychology Faculty delegates character-memory reasoning to the Learning Faculty for cross-production patterns. |
| **Conflict authority** | The Board | Resolving cross-faculty conflicts (`002` Part 8). |
| **Final authority** | The Board (for creative decisions); the human (for intent changes) | The Mind never has final authority. |
| **Human authority** | The human | Over the CIS (intent); over overrides (`002` Part 8.2.6); over CIS amendments (`003` Part 7.4). |
| **Director authority** | The directors | Over their domains (`002` Part 2.3). |

---

# PART 7: CREATIVE LIFECYCLE

---

## 7.1 Lifecycle Stages

The Creative Mind participates in a lifecycle that spans the production and extends beyond it. The stages are cognitive, not cal:

| Stage | What it means | Mind's role |
|-------|---------------|-------------|
| **Inspiration** | The spark: the human conceives the work and authors the CIS. | The Mind is quiescent; the human authors. |
| **Exploration** | The Mind reads the CIS and begins to interpret it across faculties. | Faculties interpret; enrichments begin. |
| **Expansion** | The Mind generates alternatives and implications beyond what the CIS states. | Faculties generate alternatives; enrichments grow. |
| **Experimentation** | The Mind tests alternatives against the CIS, the ontology, and each other. | Trade-off analyses; conflict detection. |
| **Evaluation** | The Mind evaluates the alternative set for coherence and confidence. | Aesthetic and Reflective assessments. |
| **Convergence** | The Mind converges to a decidable set. | Directorial Faculty synthesis. |
| **Commitment** | The Board decides; the CIR is written. | The Mind is not active (the Board decides). |
| **Production** | The compiler produces the PKP; PROMETHEUS renders. | The Mind is not active. |
| **Reflection** | The Mind reflects on its reasoning and the production's outcome. | Reflective Faculty active; learning inputs prepared. |
| **Learning** | The Mind updates its cognitive patterns. | Learning Faculty active; patterns updated (governed). |
| **Evolution** | Over many productions, the Mind's faculties evolve (Part 9). | Governance-governed faculty evolution. |

## 7.2 Faculty Participation Across Stages

| Stage | Active faculties |
|-------|------------------|
| Inspiration | None (human authors). |
| Exploration | Meaning, Narrative, Character, Psychology, Audience. |
| Expansion | All faculties (generating alternatives and implications). |
| Experimentation | All faculties (testing alternatives). |
| Evaluation | Aesthetic, Reflective. |
| Convergence | Directorial. |
| Commitment | None (Board decides). |
| Production | None. |
| Reflection | Reflective. |
| Learning | Learning. |
| Evolution | Governance + Learning. |

---

# PART 8: INTEGRATION WITH EXISTING ARCHITECTURE

---

## 8.1 The Full Cognitive-Pipeline Map

```
Human
   │
   │ authors
   ▼
Creative Intent Specification (CIS)              [003]
   │
   │ interpreted by
   ▼
Creative Object Model (COM) objects              [004]
   │  (in intent state, per 004 Part 8.3)
   │
   │ enriched by
   ▼
Creative Faculties                               [this specification]
   │  (faculties enrich COM objects with understanding,
   │   generate alternatives, deliberate, converge)
   │
   │ consumed by
   ▼
Directorial Board                                [002]
   │  (the Board decides, producing Creative Decisions)
   │
   │ recorded in
   ▼
Creative Intent Record (CIR)                     [002 Part 12]
   │
   │ compiled by
   ▼
GENESIS Compiler Passes                          [001 §4.2]
   │
   │ produces
   ▼
Production Knowledge Package (PKP)               [001 §5]
   │
   │ rendered by
   ▼
PROMETHEUS                                       [001 §2.1]
   │
   │ produces
   ▼
Media
   │
   │ validated by
   ▼
ORACLE                                           [001 §2.1]
   │
   │ persisted by
   ▼
ATLAS                                            [001 §2.1]
   │
   │ feeds back to
   ▼
Creative Faculties (Learning Faculty)            [this specification]
```

## 8.2 Layer Ownership and Flow

| Layer | Owns | Does not own |
|-------|------|--------------|
| **CIS** | Human intent. | Reasoning, decisions, compilation. |
| **COM (intent state)** | The typed objects carrying intent. | Enrichments (those are the Mind's). |
| **Creative Faculties** | Cognitive enrichments, alternatives, deliberation. | Decisions (those are the Board's). |
| **Directorial Board** | Creative Decisions (the CIR). | Cognitive enrichments (those are the Mind's). |
| **CIR** | The reasoning record (why each decision exists). | The cognitive enrichments (those are the Mind's; the CIR references them via `cir_origin`). |
| **Compiler** | The PKP (compiled decisions). | Decisions or enrichments. |
| **PKP** | Executable production knowledge. | Reasoning or intent. |
| **PROMETHEUS** | Media. | Any of the above. |
| **ORACLE** | Validation reports. | Any of the above. |
| **ATLAS** | All persisted artifacts. | Any live object. |

**What remains immutable:** object identity (per `004` Part 8.3); the pinned CIS; the frozen CIR; the frozen PKP; archived media.

**What evolves:** the Mind's cognitive enrichments (during reasoning); the Board's decisions (during revision, via new CIR versions); the Mind's cognitive patterns (during learning, via governance).

**How knowledge flows:** CIS → COM (intent state) → Mind enrichments → Board decisions → CIR → PKP → media → ORACLE reports → ATLAS → Mind (Learning Faculty, next production).

**How reasoning flows:** Faculties enrich COM objects; the Directorial Faculty synthesizes; the Board decides; the CIR records. Reasoning is the Mind's; decisions are the Board's.

**How authority flows:** Human (CIS) → Mind (cognitive) → Board (decision) → Compiler (compilation) → PROMETHEUS (rendering) → ORACLE (validation) → ATLAS (persistence). Authority is never shared across layers; it is delegated downward and consumed.

**How provenance is maintained:** Every enrichment carries the enriching faculty's identity and evidence (`004` Part 2.1, "Traceability"); every CIR node references the enrichments it consumed (`002` Part 12.5, `cir_origin`); every PKP artifact references its CIR node (`002` Part 7.2); every media artifact references its PKP artifact; every ATLAS entry carries full provenance (GFS-003). The chain is unbroken from CIS to archive.

---

# PART 9: CREATIVE EVOLUTION

---

## 9.1 Evolution Kinds

The Creative Mind evolves across several dimensions. All evolution is governed (Part 10.2).

| Kind | What evolves | Trigger | Governance |
|------|-------------|---------|------------|
| **Adding faculties** | A new cognitive capability is added (e.g., an Interactive Faculty for game runtimes). | A new runtime requires a cognitive capability the existing faculties do not provide. | GFS-007; new faculty requires a full §3.1 contract and a constitutional amendment to this specification. |
| **Deprecating faculties** | A faculty is retired. | A faculty is found to duplicate another's capability or to be unused across all runtimes. | GFS-007; deprecation cycle (Part 10.2). |
| **Specializing faculties** | A faculty gains a runtime-specific sub-faculty (e.g., a Visual-Cinema sub-faculty). | A runtime requires specialized reasoning within a faculty's domain. | GFS-007; the sub-faculty inherits the parent faculty's contract and adds runtime-specific fields. |
| **Generalizing faculties** | A runtime-specific faculty is generalized to serve multiple runtimes. | A faculty built for cinema is found to apply to other runtimes. | GFS-007; the faculty's contract is abstracted. |
| **Cross-runtime learning** | The Learning Faculty learns patterns that apply across runtimes. | A pattern observed in cinema is found to apply to games or books. | The Learning Faculty proposes; governance approves. |
| **Creative maturity** | The Mind's overall cognitive quality improves. | Accumulated learning across productions. | Tracked by the Reflective Faculty's long-term quality trends. |
| **Knowledge accumulation** | ATLAS memory grows. | Every production contributes memory. | ATLAS manages storage; the Learning Faculty manages retrieval. |
| **Taste evolution** | The Mind's aesthetic defaults shift. | The human's preferences evolve; ORACLE's feedback accumulates. | The Learning Faculty proposes; governance approves; the human may lock defaults. |
| **Reasoning evolution** | The Mind's reasoning patterns improve. | The Reflective Faculty's learning inputs. | The Learning Faculty proposes; governance approves. |
| **Architectural evolution** | The Mind's structure evolves (new faculties, new relationships). | The architecture's needs change. | This specification is amended under GFS-007. |
| **Constitutional evolution** | The constitution itself evolves. | The platform's foundational principles change. | GFS-000..009 are amended per their own governance. The Mind follows; it does not lead. |

## 9.2 Constitutional Compatibility

The Creative Mind's evolution is bounded by constitutional compatibility:

- **I-CE-1**: Faculty evolution may not break the COM's object types (`004` Part 2). A new faculty enriches existing types or proposes new types under `004` Part 10.2 governance.
- **I-CE-2**: Faculty evolution may not break the Directorial Board's decision authority (`002` I-DI-2). A new faculty has cognitive authority only.
- **I-CE-3**: Faculty evolution may not break the CIS's intent authority (`003` I-HC-1). A new faculty reads the CIS; it does not amend it.
- **I-CE-4**: Faculty evolution may not break the four-pillar boundaries (`001` §2.2). The Mind is not a pillar; it is a cognitive layer inside GENESIS.
- **I-CE-5**: Faculty evolution may not break runtime independence (I-CM-2). A new faculty is runtime-independent; runtime-specific bindings are projection contracts, not faculty definitions.

---

# PART 10: GOVERNANCE

---

## 10.1 Governance Authority

The Creative Mind is governed under the constitutional framework:

- **GFS-000 (Constitutional Charter)** is supreme. The Mind does not amend it.
- **GFS-007 (Governance Constitution)** governs changes to the Mind's faculty set, collaboration model, deliberation arc, and authority map.
- **GFS-009 (Constitutional Ontology Framework)** governs the Mind's use of ontology terms.
- **This specification** is the Mind's canonical definition. Changes require an amendment to this specification, issued under GFS-007.

## 10.2 Faculty Evolution Governance

| Change type | Authority | Process |
|--------------|-----------|---------|
| **New faculty** | GFS-007 governance. | Proposed as an amendment to this specification; must specify the full §3.1 contract; must not duplicate an existing faculty's cognitive domain; must be grounded in the ontology; must declare its runtime independence. |
| **Faculty deprecation** | GFS-007 governance. | Deprecated faculties remain valid in archived productions; new productions may not invoke them. Deprecation cycle: `deprecated` for one specification version, `obsolete` for the next, removed in the version after. |
| **Faculty specialization** | GFS-007 governance. | A sub-faculty inherits the parent's contract and adds runtime-specific fields; the sub-faculty is marked with its runtime binding. |
| **Faculty generalization** | GFS-007 governance. | The faculty's contract is abstracted; runtime-specific fields become projection contracts. |
| **Cognitive-pattern update** | The Learning Faculty proposes; governance approves. | A pattern update is recorded with provenance; it is applied to future productions only; archived productions are not retroactively re-reasoned. |
| **Collaboration model change** | GFS-007 governance. | Changes to the collaboration model (Part 4) require a constitutional amendment; they affect all faculties. |
| **Deliberation arc change** | GFS-007 governance. | Changes to the deliberation arc (Part 5) require a constitutional amendment; they affect all productions. |

## 10.3 Architectural Integrity

Architectural integrity is protected by five invariants, which governance must preserve in every evolution:

1. **I-CM-1**: Cognitive authority (Mind) and decision authority (Board) are separated.
2. **I-CM-2**: The Mind is runtime-independent.
3. **I-CE-1..5**: Faculty evolution may not break the COM, the Board, the CIS, the pillars, or runtime independence.

Any proposed evolution that would violate an invariant is rejected. Governance's first question is always: "Does this preserve the invariants?"

## 10.4 Future-Runtime Compatibility

Future creative runtimes (games, books, education, podcasts, devotionals, etc.) are compatible with the Creative Mind by design:

- The faculties are runtime-independent; a new runtime consumes them via its own decision body (analogous to the Directorial Board for cinema).
- A new runtime may require a new faculty (e.g., an Interactive Faculty for games) or a new sub-faculty; both are added under governance.
- A new runtime's decision body is specified in its own constitutional document (analogous to `002` for cinema); it consumes the Mind's enrichments via its own projection contracts.
- The Mind's evolution does not require runtimes to change; runtimes' evolution does not require the Mind to change. They are coupled only through projection contracts.

This is the architectural expression of the platform's name: the Artificial Creative Intelligence platform powers the Cinema Production Engine; cinema is the first runtime, not the only one.

---

# PART 11: MIGRATION STRATEGY

---

## 11.1 Integration Principles

The Creative Mind integrates into the existing architecture under these principles:

| # | Principle | Statement |
|---|-----------|-----------|
| MI-1 | **The Mind is additive.** It adds a cognitive layer; it does not replace the Directorial Board, the COM, the CIR, the PKP, or any runtime. |
| MI-2 | **The Mind does not replace Director Intelligence.** The Board remains the cinematic decision authority (`002`). The Mind provides the cognition the Board consumes. |
| MI-3 | **The Mind operates on the COM.** Faculties enrich COM objects; they do not define new types (`004` owns types). |
| MI-4 | **The Mind is runtime-independent.** The cinema-specific bindings in this specification are projection contracts, not faculty definitions. |
| MI-5 | **The Mind preserves the four-pillar boundaries.** The Mind is a cognitive layer inside GENESIS; it is not a pillar. |
| MI-6 | **The Mind invents no parallel architecture.** Faculties are not agents; they are not directors; they are not compiler passes. They are cognitive capabilities, distinct from all existing components. |
| MI-7 | **The Mind strengthens the existing architecture, not complicates it.** The Mind deepens the Board's decisions by providing richer understanding; it does not add a competing decision path. |

## 11.2 Migration Phases

### Phase CM-1 — Faculty Catalog Documentation

- Document the 11 Creative Faculties (Part 3.3) as constitutional definitions in `docs/genesis/specifications/` (a new `cognitive/` subdirectory, per the existing classification in `docs/genesis/AGENTS.md`).
- Cross-reference each faculty to its consuming directors (`002` Part 2.3) and to the COM objects it enriches (`004` Part 2.3).
- No runtime change.

**Exit criteria:** 11 faculty specs committed; cross-reference tables complete; ADR issued recording the Creative-Mind-as-cognitive-layer decision.

### Phase CM-2 — COM Enrichment Model

- Define the COM enrichment model (Part 4.3) as an extension of the COM's object contract (`004` Part 2.1).
- Add enrichment fields (interpretation, implication, coherence assessment, alternative, conflict flag, confidence) to the COM's object specification as optional cognitive-layer fields.
- Enrichments are additive and provenanced; they do not change the COM's object types.

**Exit criteria:** COM enrichment model documented; enrichment fields specified; the COM's type system unchanged.

### Phase CM-3 — Faculty Reasoning (Fast Mode)

- Implement the 11 faculties in fast mode: each faculty produces a single enrichment per owned domain, with at least one alternative recorded, using existing LLM tiered routing (`config/llm_config.yaml`, `llm_factory.py`).
- Wire each faculty to its consuming directors: the directors read enriched COM objects in addition to the CIS domains they already read.

**Exit criteria:** Faculties produce enrichments; directors consume enriched COM objects; deterministic replay still passes (same CIS + same faculty seeds → same enrichments → same CIR).

### Phase CM-4 — Deliberation and Collaboration

- Implement the deliberation arc (Part 5.2) and the collaboration model (Part 4).
- Implement conflict surfacing (Part 4.4) and the Directorial Faculty's synthesis.
- Wire the Directorial Faculty's output to the Board's conflict resolution (`002` Part 8).

**Exit criteria:** Faculties deliberate; conflicts surface; the Directorial Faculty presents a decidable set; the Board resolves conflicts with the Mind's understanding visible.

### Phase CM-5 — Reflection and Learning

- Implement the Reflective Faculty's self-assessment (Part 3.3.10).
- Implement the Learning Faculty's precedent retrieval and pattern-update proposals (Part 3.3.11).
- Wire the Learning Faculty to ATLAS for memory and to governance for pattern updates.

**Exit criteria:** Reflection produces quality assessments and low-confidence flags; learning provides precedent during reasoning; pattern updates are governed and traceable.

### Phase CM-6 — ORACLE Feedback Loop

- Wire ORACLE's drift reports to the Reflective and Learning faculties (Part 2.5).
- The Mind consumes drift reports as learning inputs: "the Board's decision based on our interpretation X produced drift; what should we learn?"

**Exit criteria:** ORACLE drift reports inform the Mind's learning; the Mind's cognitive quality improves across productions.

### Phase CM-7 — Runtime-Independent Projection

- Document the cinema-runtime projection contracts (which directors consume which faculties) as the cinema-specific binding.
- Verify that the faculty definitions themselves contain no cinema-specific content; all cinema-specificity is in the projection contracts.

**Exit criteria:** Faculties are runtime-independent; cinema-specificity is isolated in projection contracts; a future runtime (e.g., books) can define its own projection contracts without amending the faculties.

## 11.3 Backward Compatibility

| Existing artifact | Compatibility | Action |
|-------------------|---------------|--------|
| GFS-000..009 | **Preserved.** The Mind is a derived standard under GFS-007/GFS-009. | None. |
| `001` four-pillar model | **Preserved.** The Mind is inside GENESIS; it is not a pillar. | None. |
| `001` compiler passes | **Preserved.** The compiler reads the CIR, not the Mind's enrichments. | None. |
| `002` Directorial Board | **Preserved and strengthened.** The Board gains richer understanding (enriched COM objects) to decide with. The Board's authority is unchanged. | None. The Board reads enriched COM objects in addition to CIS domains. |
| `002` CIR | **Preserved.** The CIR references the Mind's enrichments via provenance; the CIR's structure is unchanged. | Add enrichment references to CIR provenance. |
| `003` CIS | **Preserved.** The Mind reads the CIS; it does not amend it. | None. |
| `004` COM | **Preserved and extended.** The COM's object types are unchanged; enrichment fields are additive. | Add enrichment fields as optional cognitive-layer fields. |
| GO-001..119 | **Preserved.** The Mind uses ontology terms; it does not define them. | None. |
| PKP-00..18 | **Preserved.** The Mind does not touch the PKP. | None. |
| Existing agent specs | **Preserved.** Agents (directors) are the decision authority; faculties are the cognitive layer. The two are distinct. | None. |

## 11.4 Risks and Architectural Impacts

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Mind/Board conflation.** Implementers may treat faculties as a second Board, duplicating decision authority. | High | I-CM-1: cognitive authority and decision authority are separated. Code review enforces: faculties enrich; directors decide. |
| **Faculty/agent conflation.** Implementers may treat faculties as agents, duplicating the agent architecture. | High | Part 1.2: faculties are cognitive capabilities, not goal-directed actors. Faculties have no decision authority; agents do. |
| **Enrichment overload.** Faculties may over-enrich COM objects, drowning the Board in alternatives. | Medium | The Directorial Faculty converges to a decidable set (Part 4.7); the Reflective Faculty flags diminishing returns (Part 5.3). |
| **Runtime leakage.** Cinema-specific content may leak into faculty definitions, breaking runtime independence. | Medium | Phase CM-7: faculty definitions are audited for cinema-specific content; all cinema-specificity is isolated in projection contracts. |
| **Learning runaway.** The Learning Faculty may propose pattern updates that drift from the constitution or the ontology. | Medium | Pattern updates require governance approval (Part 10.2); the Learning Faculty proposes, governance disposes. |
| **Deliberation latency.** Deep deliberation may make the Mind too slow for fast-mode use. | Medium | Phase CM-3: fast mode produces single-enrichment outputs; deep deliberation is opt-in per decision class. |
| **CIR enrichment-reference burden.** CIR nodes may become verbose if they reference every enrichment they consumed. | Low | Enrichment references are summarized in the CIR's provenance; the full enrichment history is in ATLAS, referenced by identifier. |

---

## Architectural Rules (Restated)

This specification produced **no implementation code, no Python, no TypeScript, no YAML, no JSON schemas, no prompts, no APIs, no database structures, no technology choices, no model-specific recommendations, and no LLM discussions**. It produced a constitutional architecture specification — the cognitive architecture of the Artificial Creative Intelligence that powers the Cinema Production Engine.

Every recommendation is grounded in the existing repository:

- The Creative Mind extends the reasoning architecture of `002` Part 5 (Creative Reasoning Engine) into a faculty-based cognitive model.
- The Mind operates on the COM (`004`) by enriching its objects.
- The Mind reads the CIS (`003`) and does not amend it.
- The Mind consumes ORACLE drift reports (`001` §2.1) for learning.
- The Mind consumes ATLAS memory (`001` §2.1, `002` Part 6) for precedent.
- The Mind's faculties use GO-001..119 vocabulary.
- The Mind obeys GFS-000..009.
- The Mind preserves the four-pillar boundaries (`001` §2).
- The Mind does not replace the Directorial Board (`002`); it provides the cognition the Board consumes.

No parallel architecture is introduced. No existing concept is duplicated. Faculties are not agents; they are not directors; they are not compiler passes. They are a new architectural kind — cognitive capabilities — that deepens the existing architecture into a coherent model of Artificial Creative Intelligence capable of supporting multiple future creative runtimes beyond cinema.

---

## Cross-References

| Reference | Location | Relevance |
|-----------|----------|-----------|
| Constitutional Architecture | `00 — Cinema Production Engine Vision, Philosophy & Reference Architecture.md` | Supreme authority. The Mind derives from §3.2 (compilation over generation), §3.3 (creative/technical separation), §3.5 (provenance), §3.8 (human as final reviewer). |
| Migration Blueprint | `001 — GENESIS 2.0 Migration Specification.md` | Defines the four-pillar boundaries the Mind respects (§2) and the compiler the Mind precedes (§4.2). |
| Director Intelligence | `002 — Director Intelligence & Creative Reasoning Architecture Specification.md` | Defines the Directorial Board (Part 2) that consumes the Mind's cognition, the Creative Reasoning Engine (Part 5) the Mind generalizes, the CIR (Part 12) the Mind's enrichments inform, and the conflict resolution (Part 8) the Mind's conflicts feed. |
| Creative Intent Specification | `003 — Creative Intent Specification (CIS) Architecture.md` | Defines the CIS the Mind reads and does not amend. The Mind's faculties map to the CIS's 24 domains. |
| Creative Object Model | `004 — Creative Object Model (COM) & Semantic Architecture Specification.md` | Defines the COM objects the Mind enriches. The Mind's enrichments are additive to the COM's type system. |
| Constitutional Charter | `docs/genesis/constitutions/00-ConstitutionCharter.md` (GFS-000) | Supreme constitutional authority. |
| Governance Constitution | `docs/genesis/constitutions/007 – Governance Constitution.md` (GFS-007) | Governs Mind evolution. |
| Constitutional Ontology Framework | `docs/genesis/constitutions/009 — Constitutional Ontology Framework.md` (GFS-009) | Governs the Mind's use of ontology. |
| Core Ontology | `docs/genesis/ontology/core/001 — Genesis Core Ontology.md` (GO-001) | The noun vocabulary the faculties use. |
| Semantic Relationship Catalog | `docs/genesis/ontology/semantic/002 — Genesis Semantic Relationship Catalog.md` (GO-002) | The predicate vocabulary the faculties use. |
| Narrative Ontology | `docs/genesis/ontology/core/101 — Narrative Ontology.md` (GO-101) | Narrative Faculty grounding. |
| Audience Experience Ontology | `docs/genesis/ontology/experience/102 — Audience Experience Ontology.md` (GO-102) | Audience Faculty grounding. |
| Human Psychology & Behavior Ontology | `docs/genesis/ontology/experience/103 — Human Psychology & Behavior Ontology.md` (GO-103) | Psychology Faculty grounding. |
| Character Ontology | `docs/genesis/ontology/core/104 — Character Ontology.md` (GO-104) | Character Faculty grounding. |
| Visual Expression Ontology | `docs/genesis/ontology/experience/109 — Visual Expression, Cinematography & Composition Ontology.md` (GO-109) | Visual Faculty grounding. |
| Audio, Music, Sound Design & Silence Ontology | `docs/genesis/ontology/experience/110 — Audio, Music, Sound Design & Silence Ontology.md` (GO-110) | Musical Faculty grounding. |
| Temporal Experience, Editing & Narrative Rhythm Ontology | `docs/genesis/ontology/experience/111 — Temporal Experience, Editing & Narrative Rhythm Ontology.md` (GO-111) | Narrative and Directorial Faculty grounding. |
| Creativity, Innovation & Design Reasoning Ontology | `docs/genesis/ontology/creativity/116 — Creativity, Innovation & Design Reasoning Ontology.md` (GO-116) | Meaning, Aesthetic, Directorial, and Reflective Faculty grounding. |
| Knowledge Pattern Library | `docs/genesis/ontology/foundation/004 — Genesis Knowledge Pattern Library.md` (GO-004) | Learning Faculty knowledge source. |
| Reasoning Pattern Library | `docs/genesis/ontology/foundation/005 — Genesis Reasoning Pattern Library.md` (GO-005) | All faculties' reasoning patterns. |
| ADR-004 (Five Confidence Levels) | `docs/genesis/decisions/` | Confidence taxonomy used by every faculty enrichment. |
| All 19 PKP Specifications | `docs/genesis/specifications/pkp/` | The Mind does not touch the PKP; these are the compiled outputs of the Board's decisions. |
| Constitutional Prompts | `genesis/constitutional-prompts/` | The design history of this and the preceding constitutional specifications. |

---

**End of Specification.**