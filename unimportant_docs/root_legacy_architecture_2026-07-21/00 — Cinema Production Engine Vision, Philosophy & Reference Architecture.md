# 00 — Cinema Production Engine: Vision, Philosophy & Reference Architecture

**Status:** Constitutional — Supreme Architectural Authority
**Version:** 1.0.0
**Date:** 2026-07-21
**Precedence:** This document supersedes all informal architecture notes. Every future specification, agent design, pipeline change, and module boundary decision in this repository must trace its justification back to a principle defined here. When this document conflicts with an informal comment, README, or legacy naming convention, this document wins.

---

## Table of Contents

1. [Vision](#1-vision)
2. [Mission](#2-mission)
3. [Design Philosophy](#3-design-philosophy)
4. [Architectural Principles](#4-architectural-principles)
5. [System Boundaries](#5-system-boundaries)
6. [Long-Term Objectives](#6-long-term-objectives)
7. [Reference Architecture](#7-reference-architecture)
8. [Core Components](#8-core-components)
9. [The Four Pillars: GENESIS, PROMETHEUS, ATLAS, ORACLE](#9-the-four-pillars-genesis-prometheus-atlas-oracle)
10. [Compiler Philosophy](#10-compiler-philosophy)
11. [Production Package Philosophy](#11-production-package-philosophy)
12. [Model Independence](#12-model-independence)
13. [Human Creativity Philosophy](#13-human-creativity-philosophy)
14. [AI Film Director Philosophy](#14-ai-film-director-philosophy)
15. [Knowledge Graph Philosophy](#15-knowledge-graph-philosophy)
16. [Extensibility Philosophy](#16-extensibility-philosophy)
17. [Enterprise Architecture Principles](#17-enterprise-architecture-principles)
18. [Future Roadmap](#18-future-roadmap)
19. [Glossary](#19-glossary)
20. [Cross-References to Existing Repository](#20-cross-references-to-existing-repository)

---

## 1. Vision

**The Cinema Production Engine is a local-first, model-independent, knowledge-driven operating system for AI-mediated cinematic production.**

It transforms incomplete human creative intent into complete, validated, internally consistent, production-ready cinematic works — and then realizes those works as finished media — without surrendering creative authority to any single AI provider, rendering pipeline, or cloud platform.

The engine treats film production as a compilation problem, not a generation problem. A human expresses intent. The engine compiles that intent through a deterministic pipeline of creative-intelligence stages, producing a Production Knowledge Package that is the single source of truth. Downstream rendering systems read that package and emit media. The knowledge outlives every model, every framework, and every runtime used to produce it.

The Cinema Production Engine is not a video generator. It is a production operating system that governs the full lifecycle of a cinematic work: from the first spark of an idea, through creative pre-production, through media realization, through quality validation, through asset archival — and back again for revision.

### What the Vision Excludes

- The engine is not a cloud SaaS. It runs locally first. Cloud deployment is an option, not the architecture.
- The engine is not a single-model system. No model owns the pipeline. Models are swappable providers behind capability interfaces.
- The engine is not a black box. Every creative decision is explicit, traceable, and revisable in the Production Knowledge Graph.
- The engine is not a replacement for human creativity. It is an amplifier. The human is the author; the engine is the studio.

---

## 2. Mission

**To eliminate every creative ambiguity between human intent and finished cinematic output such that any compliant downstream system can produce a feature-quality work without making a single creative decision.**

This mission has a precise completion criterion: at the moment the Production Knowledge Package is signed off, another AI system — or a human production team — should be capable of producing the final cinematic work by executing instructions, not by exercising creative judgment. Every creative decision has already been made, validated, and recorded.

The mission is bounded:

| Phase | What the engine does | What it does not do |
|-------|---------------------|---------------------|
| Pre-production (GENESIS) | Resolves every creative decision into structured knowledge | Generates no media |
| Production (PROMETHEUS) | Realizes the knowledge package as media | Makes no creative decisions |
| Persistence (ATLAS) | Stores knowledge and assets for reuse | Forgets nothing that matters |
| Validation (ORACLE) | Verifies media against the knowledge package | Overrides human intent |

---

## 3. Design Philosophy

The Cinema Production Engine is built on eight philosophical commitments. These are not guidelines; they are constraints that every architectural decision must satisfy.

### 3.1 Knowledge Over Media

Media is ephemeral; knowledge is durable. A generated image can be lost, a model can be deprecated, a rendering pipeline can be replaced — but the creative knowledge that defined why that image existed, what it depicted, and how it served the story must survive. The engine separates knowledge (which is canonical and immutable once committed) from media (which is a derived projection and may be regenerated at any time).

This principle is already established in the repository's Genesis Foundational Standard GFS-003: *"The PKG is the single source of truth. Every mutation creates a new immutable revision. Provenance is mandatory."* The Cinema Production Engine extends this from pre-production to the entire lifecycle.

### 3.2 Compilation Over Generation

The engine does not "generate" a film. It **compiles** a film from a knowledge specification. The distinction is architectural:

- **Generation** implies the model is the author. The output is emergent, unpredictable, and unrepeatable.
- **Compilation** implies the specification is the author. The output is deterministic given the same specification and the same providers. The model is a compiler pass, not a creative agent.

This metaphor is already present in the repository: `docs/generateStoryContextDna.md` states *"your 'Story Factory' becomes a compiler: the DNA defines what the story is, the Context defines where and why it exists, and the Story defines what actually happens. Everything after that is production, not creativity."*

The Cinema Production Engine formalizes this: the Production Knowledge Package is the source program. PROMETHEUS is the compiler backend. ORACLE is the type checker. The final video is the compiled binary.

### 3.3 Separation of Creative and Technical Authority

Creative decisions (what the story means, how a character feels, why a scene exists) belong to GENESIS and the human author. Technical decisions (which model renders the image, what codec encodes the video, what resolution is output) belong to the capability layer and are invisible to the creative specification.

The interface between these two domains is the Production Knowledge Package. It is written in creative terms and read in technical terms. Neither side crosses the boundary.

### 3.4 Local-First, Cloud-Optional

The engine runs on a single machine. It uses local LLMs (Ollama), local image models (Stable Diffusion via diffusers), local video models (SVD-XT), local TTS (edge-tts), and local rendering (FFmpeg). Cloud providers may be plugged in behind the capability registry, but the default architecture assumes no network dependency for core operation.

This is a sovereignty principle: the creator must not be dependent on a third party's API quota, model availability, or pricing to produce their own work.

### 3.5 Provenance Is Mandatory

Every fact, every creative decision, every generated asset, and every model invocation must carry provenance metadata: who decided this, when, on what evidence, at what confidence level, using which model. Provenance is not optional logging; it is a structural invariant of the knowledge graph. Without provenance, a node cannot be committed.

This is established in GFS-003 and the Genesis master prompt's confidence taxonomy (`explicit / inferred / confirmed / assumed / unknown`). The Cinema Production Engine extends provenance from pre-production knowledge to produced media: every rendered frame must trace back to a scene specification, which traces back to a story beat, which traces back to a creative intent, which traces back to a human author.

### 3.6 Deterministic Creative Replay

Given the same Production Knowledge Package and the same set of provider versions, the engine must produce a bit-identical (or perceptually identical) output on recompilation. Creative decisions do not change on re-render. If the output must change, the knowledge package must be amended — not the rendering parameters silently overridden.

This makes creative work reproducible, auditable, and archivable. It also makes revision safe: you can change one scene's knowledge and recompile only the affected media, knowing the rest is stable.

### 3.7 Graceful Degradation, Not Silent Failure

Every component must fail loudly and degrade gracefully. If the research stage cannot reach the internet, the pipeline continues with a warning and generates from internal knowledge. If a specific image model is unavailable, the system falls back to an alternative provider behind the same capability interface. If a scene fails validation, the pipeline halts and reports — it does not silently produce a broken scene.

### 3.8 The Human Is the Final Reviewer

No creative output is final until a human signs off. The engine can produce, validate, and score — but the completion gate is a human act. The engine's job is to make the human's review as efficient as possible by eliminating ambiguity, not to make the human unnecessary.

---

## 4. Architectural Principles

### 4.1 Layered Architecture

The engine is organized into strict layers. Each layer depends only on the layer below it. Dependencies never flow upward.

```
┌─────────────────────────────────────────────────────┐
│  Layer 7: Experience (UI, CLI, API surface)          │
├─────────────────────────────────────────────────────┤
│  Layer 6: Orchestration (pipeline, workflows, gates) │
├─────────────────────────────────────────────────────┤
│  Layer 5: Intelligence (GENESIS, PROMETHEUS,         │
│           ATLAS, ORACLE agent systems)               │
├─────────────────────────────────────────────────────┤
│  Layer 4: Knowledge (PKG, PKP, Ontology, Compiler)   │
├─────────────────────────────────────────────────────┤
│  Layer 3: Capability Registry (abstract interfaces)  │
├─────────────────────────────────────────────────────┤
│  Layer 2: Provider (concrete models, renderers)      │
├─────────────────────────────────────────────────────┤
│  Layer 1: Domain Model (Pydantic types, enums,        │
│           validation — the type system of the engine)│
├─────────────────────────────────────────────────────┤
│  Layer 0: Foundation (filesystem, process, network,  │
│            logging — the substrate the engine runs on) │
└─────────────────────────────────────────────────────┘
```

**Layer 1 (Domain Model)** is the type system. Every concept in the engine — Story, Scene, Character, Location, Dialogue, Prompt, Clip, Asset — is a Pydantic model with validation. This layer is already present in `config/models.py` and `backend/app/models/schemas.py`. The Cinema Production Engine requires that the domain model be the single authoritative type definition; no layer above may define a competing type for the same concept.

**Layer 2 (Provider)** holds concrete implementations: OllamaClient for LLMs, StableDiffusionPipeline for images, SVD-XT for video, edge-tts for voice, FFmpeg for rendering. Providers are replaceable. No layer above imports a provider directly; it goes through the capability registry.

**Layer 3 (Capability Registry)** defines abstract interfaces: `LLMProvider`, `ImageGenerator`, `VideoGenerator`, `VoiceSynthesizer`, `MusicComposer`, `Renderer`. Each interface declares inputs in creative terms and outputs in structured terms. The registry maps each capability to a concrete provider at configuration time. This layer already exists in `config/movie_os.yaml` (the provider configuration) and is referenced in `.ai/architecture.yaml` as the "Capability Registry" layer.

**Layer 4 (Knowledge)** is the constitutional core: the Production Knowledge Graph, the Production Knowledge Package, the Ontology, and the Compiler. This layer is already established in `docs/genesis/05_KnowledgeGraph.md`, `docs/genesis/07_Compiler.md`, and `movie_os/genesis/pkg.py`. The Cinema Production Engine elevates this layer from a Genesis-specific concern to a platform-wide concern: all four pillars read and write the knowledge graph.

**Layer 5 (Intelligence)** holds the four agent systems: GENESIS (pre-production), PROMETHEUS (production), ATLAS (persistence), ORACLE (validation). Each is a multi-agent system with its own internal architecture but shares the same knowledge graph and capability registry. See §9.

**Layer 6 (Orchestration)** is the pipeline layer: the FastAPI pipeline service, the Movie OS workflow engine, the Genesis completion gate. This layer coordinates agents, manages state, enforces ordering, and applies gates. It already exists in `backend/app/services/pipeline_service.py` and `config/movie_os.yaml` (`pipeline.steps`).

**Layer 7 (Experience)** is the surface: the Next.js frontend, the CLI, the REST API. This layer presents the engine to humans and external systems. It must never contain business logic.

### 4.2 Single Source of Truth

For any given concept, there is exactly one authoritative definition:

| Concept | Authority |
|---------|-----------|
| Type definitions | Layer 1 Domain Model (`config/models.py`, `backend/app/models/schemas.py`) |
| Creative knowledge | Layer 4 Production Knowledge Graph |
| Production specification | Layer 4 Production Knowledge Package |
| Provider configuration | Layer 3 Capability Registry (`config/movie_os.yaml`) |
| Pipeline stage definitions | Layer 6 Orchestration (`backend/app/services/pipeline_service.py`) |
| Production profiles | `config/production_profiles.yaml` |
| LLM prompt templates | `config/prompts.py` |
| Constitutional standards | `docs/genesis/02_Constitution.md` (GFS-000..009) |
| Ontology | `docs/genesis/04_GO.md` (GO ontology) |

When a concept is defined in multiple places (as currently happens with the three parallel pre-production paths — the backend pipeline, `movie_os/genesis`, and `movie_os/genesis2`), the Cinema Production Engine mandates convergence: the constitutional definition wins, and the others are either refactored to delegate to it or explicitly scoped as experimental.

### 4.3 Interface Stability, Implementation Fluidity

Interfaces between layers are stable contracts. Implementations behind those interfaces are fluid and replaceable. The capability registry is the primary mechanism: `ImageGenerator` is a stable interface; `StableDiffusionV15`, `FLUXComfyUI`, and `DallE3` are fluid implementations. The knowledge graph schema is a stable interface; the LLM that populates it is a fluid implementation.

### 4.4 Idempotent Operations

Every pipeline stage, every agent invocation, every rendering job must be idempotent: running it twice with the same input produces the same output (or a no-op if the output already exists). This is already partially implemented (the image service checks if an image exists before regenerating), but must be a universal invariant.

### 4.5 Explicit State, No Hidden Context

All pipeline state is explicit and inspectable. The in-memory `_pipelines` dict in `pipeline_service.py` and the `_generation_states` dict in `video_service.py` are acceptable for the current single-node architecture, but state must never be implicit (e.g., a global variable that silently changes behavior). The `.project-ai/` operational memory system established in `AGENTS.md` is the model: state is written down, not remembered.

### 4.6 Fail at Boundaries, Not at Centers

Validation happens at layer boundaries, not inside agents. When GENESIS produces a story, the completion gate validates it before it enters the knowledge graph. When PROMETHEUS renders a clip, ORACLE validates it before it enters the asset store. Agents are trusted to produce; boundaries are trusted to verify.

---

## 5. System Boundaries

### 5.1 What the Cinema Production Engine Is

The engine is the entire system that governs the lifecycle of a cinematic production: creative pre-production, media realization, asset persistence, and quality validation. It includes:

- The domain model and type system
- The capability registry and provider layer
- The knowledge graph, ontology, and compiler
- The four intelligence pillars (GENESIS, PROMETHEUS, ATLAS, ORACLE)
- The orchestration and pipeline layer
- The experience layer (UI, CLI, API)
- The operational memory system (`.project-ai/`)
- The skills system (`skills/`)
- The configuration files (`config/`)

### 5.2 What the Cinema Production Engine Is Not

| Not the engine | Why |
|----------------|-----|
| The LLM models themselves | Models are providers behind the capability registry. The engine uses them; it is not them. |
| ComfyUI / FLUX / SVD-XT / edge-tts | These are rendering providers. The engine orchestrates them; it is not them. |
| The frontend (Next.js app) | The frontend is an experience surface. It presents the engine; it is not the engine. |
| Any single pipeline (backend 6-stage, Genesis 4-stage, Genesis2 12-phase) | These are implementations within the intelligence layer. The engine is the system that contains and governs them. |
| The `.aios/` cognitive backbone | This is a parallel agent-orchestration layer that must be either absorbed into the engine's architecture or explicitly scoped as an external system. The constitutional document takes no position on its disposition beyond requiring that the relationship be made explicit. |

### 5.3 Boundary with External Systems

The engine has well-defined boundaries with external systems:

- **External LLM APIs** (OpenAI, Anthropic, cloud Ollama): accessed through the capability registry. The engine never calls an LLM API directly from an agent or pipeline stage.
- **External rendering systems** (ComfyUI, FLUX, cloud renderers): accessed through the capability registry. The engine never imports a rendering library directly from the orchestration layer.
- **External storage** (cloud buckets, databases): accessed through the asset store interface. The engine's default storage is local filesystem.
- **External knowledge sources** (Wikipedia, DuckDuckGo, web crawlers): accessed through the research capability. The engine's default research uses free, no-API-key sources.

---

## 6. Long-Term Objectives

### 6.1 Unification of Pre-Production Paths

The repository currently contains three parallel pre-production implementations:

1. **The backend 6-stage text pipeline** (`backend/app/services/pipeline_service.py`) — research → story → scenes → dialogues → prompts → validation. This is the live web-app pipeline. It is lightweight, fast, and produces a usable output for the current frontend.

2. **The constitutional Genesis engine** (`movie_os/genesis/`) — Discovery (7 agents) → PKP Generation (19 agents) → Review (4 reviewers + ChiefArchitect) → Completion Gate (8 criteria). This is the full pre-production intelligence system with the Production Knowledge Graph, the GFS constitution, and the ontology compiler.

3. **The Genesis2 12-phase pipeline** (`movie_os/genesis2/`) — CreativeUnderstanding → StoryFoundation → CharacterPsychology → WorldDevelopment → NarrativeExpansion → ScenePlanning → DialoguePlanning → VisualLanguage → ProductionSpecifications → Validation → CreativeCritique → KnowledgeIntegration. Each phase runs Draft→Review→Critique→Improve→Validate→Freeze.

**Objective:** Unify these into a single canonical pre-production path while preserving the strengths of each. The constitutional Genesis engine's knowledge graph and completion gate become the canonical output. The backend pipeline becomes a "fast mode" that produces a subset of the full PKP for rapid prototyping. Genesis2's 12-phase structure becomes the "deep mode" that produces the full PKP with maximum creative rigor. Both modes write to the same knowledge graph and produce the same PKP schema.

The production profile system (`config/production_profiles.yaml`) is the first convergence point: it is already shared between the backend pipeline and the Genesis branding, and it will be consumed by all three paths.

### 6.2 Production Intelligence (PROMETHEUS)

The repository currently has media generation scattered across `backend/app/services/image_service.py`, `backend/app/services/video_service.py`, `backend/app/services/tts_service.py`, and the `config/movie_os.yaml` pipeline steps (`narrative, images, audio, music, sfx, mix, video`). These are capable but uncoordinated: there is no unified production intelligence that reads a PKP and orchestrates the full rendering pipeline.

**Objective:** Establish PROMETHEUS as the unified production intelligence. PROMETHEUS reads the PKP, plans the rendering pipeline, allocates capabilities to providers, executes rendering, and writes produced media into the asset store. PROMETHEUS does not make creative decisions; it executes the creative decisions encoded in the PKP.

### 6.3 Asset and Knowledge Persistence (ATLAS)

The repository currently uses in-memory dicts for pipeline state (`_pipelines`, `_generation_states`, `_image_states`) and local filesystem for output (`output/`, `output/videos/`). There is no persistent asset store, no cross-production knowledge retention, and no model registry.

**Objective:** Establish ATLAS as the persistence layer. ATLAS holds the asset store (images, clips, audio, final videos), the knowledge graph persistence (surviving across sessions), the model registry (tracking which models produced which assets), and the content library (reusable characters, locations, styles, music). ATLAS makes the engine's memory permanent.

### 6.4 Quality and Validation Intelligence (ORACLE)

The repository currently has validation in two places: the backend `YAMLValidator` (checks scene fields) and the Genesis completion gate (8 criteria for pre-production). There is no validation of produced media against the PKP.

**Objective:** Establish ORACLE as the validation intelligence. ORACLE compares rendered media against the scene specification, scores visual consistency, detects character drift, measures emotional arc adherence, verifies continuity, and produces a quality report. ORACLE's output feeds back into the PKP as validation provenance.

### 6.5 Full Lifecycle Compilation

**Objective:** A user expresses a story idea. GENESIS compiles it into a validated PKP. PROMETHEUS renders the PKP into media. ORACLE validates the media against the PKP. ATLAS persists everything. The user reviews, amends the PKP, and recompiles only the affected parts. This is the full lifecycle, and it is the north star.

---

## 7. Reference Architecture

```
                    ┌──────────────────────────────────┐
                    │         EXPERIENCE LAYER          │
                    │  (Next.js UI · CLI · REST API)     │
                    └───────────────┬──────────────────┘
                                    │
                    ┌───────────────┴──────────────────┐
                    │      ORCHESTRATION LAYER           │
                    │  (Pipeline Service · Workflows ·   │
                    │   Completion Gates · State Mgmt)   │
                    └───────────────┬──────────────────┘
                                    │
          ┌─────────────────────────┼─────────────────────────┐
          │                         │                         │
   ┌──────┴──────┐          ┌───────┴───────┐          ┌───────┴──────┐
   │   GENESIS    │          │  PROMETHEUS   │          │   ORACLE     │
   │  Pre-Prod    │          │  Production   │          │  Validation  │
   │ Intelligence │          │ Intelligence  │          │ Intelligence  │
   │              │          │               │          │              │
   │ Discovery    │          │ Image Gen     │          │ Media vs PKP │
   │ PKP Gen (19) │          │ Video Synth   │          │ Continuity  │
   │ Review (4)   │          │ Voice Synth   │          │ Emotion Arc │
   │ Gate (8)     │          │ Music Comp    │          │ Drift Det.  │
   │ Genesis2     │          │ Render/Compose│          │ Quality Rep │
   │ (12 phases)  │          │               │          │              │
   └──────┬───────┘          └───────┬───────┘          └───────┬──────┘
          │                         │                         │
          └─────────────────────────┼─────────────────────────┘
                                    │
                    ┌───────────────┴──────────────────┐
                    │         KNOWLEDGE LAYER            │
                    │  ┌──────────┐  ┌──────────────┐   │
                    │  │   PKG    │  │     PKP      │   │
                    │  │ (Graph)  │  │  (Package)   │   │
                    │  └──────────┘  └──────────────┘   │
                    │  ┌──────────┐  ┌──────────────┐   │
                    │  │ Ontology │  │  Compiler    │   │
                    │  │  (GO)    │  │  (CodeGen)   │   │
                    │  └──────────┘  └──────────────┘   │
                    └───────────────┬──────────────────┘
                                    │
                    ┌───────────────┴──────────────────┐
                    │     CAPABILITY REGISTRY LAYER     │
                    │  LLMProvider · ImageGenerator ·   │
                    │  VideoGenerator · VoiceSynth ·    │
                    │  MusicComposer · Renderer ·       │
                    │  ResearchProvider                 │
                    └───────────────┬──────────────────┘
                                    │
                    ┌───────────────┴──────────────────┐
                    │        PROVIDER LAYER              │
                    │  Ollama · SD v1.5 · SVD-XT ·       │
                    │  edge-tts · FFmpeg · FLUX/ComfyUI │
                    │  (all swappable, all optional)    │
                    └───────────────┬──────────────────┘
                                    │
                    ┌───────────────┴──────────────────┐
                    │        DOMAIN MODEL LAYER          │
                    │  Story · Scene · Character ·      │
                    │  Dialogue · Prompt · Clip ·        │
                    │  Asset · Profile · Stage           │
                    │  (Pydantic — the type system)     │
                    └───────────────┬──────────────────┘
                                    │
                    ┌───────────────┴──────────────────┐
                    │         FOUNDATION LAYER           │
                    │  Filesystem · Process · Network ·  │
                    │  Logging · .project-ai/ memory     │
                    └───────────────────────────────────┘

          ╔═══════════════════════════════════════════╗
          ║              ATLAS                        ║
          ║  Spans all layers:                        ║
          ║  Asset Store · Knowledge Persistence ·    ║
          ║  Model Registry · Content Library         ║
          ║  (The memory of the engine)               ║
          ╚═══════════════════════════════════════════╝
```

### Architectural Invariants

1. **Data flows downward through layers.** The UI calls orchestration; orchestration calls intelligence; intelligence calls knowledge; knowledge calls capability; capability calls provider. No layer calls upward.
2. **Intelligence pillars share the knowledge layer but do not call each other directly.** GENESIS writes the PKP; PROMETHEUS reads it; ORACLE reads both the PKP and PROMETHEUS's output. They communicate through the knowledge graph, not through function calls.
3. **ATLAS is orthogonal.** It spans all layers because persistence is needed at every level: domain model persistence (schemas), knowledge persistence (PKG), asset persistence (media), and configuration persistence (profiles).
4. **The compiler is part of the knowledge layer.** It compiles ontology sources into schemas, code, and validators. It does not compile media. Media compilation is PROMETHEUS's job.

---

## 8. Core Components

### 8.1 Domain Model (Layer 1)

The type system of the engine. Currently distributed across `config/models.py` (Python dataclasses: `InputConfig`, `Scene`, `PipelineOutput`, `EmotionalTone`, `Platform`) and `backend/app/models/schemas.py` (Pydantic models: `PipelineStartRequest`, `PipelineResponse`, `StoryResponse`, `SceneResponse`, etc.). The frontend mirror is `frontend/src/lib/types.ts`.

**Convergence requirement:** The backend Pydantic models and the frontend TypeScript types must remain synchronized. The Axios response interceptor (`frontend/src/lib/api.ts`, `toCamelCase`) currently bridges the snake_case ↔ camelCase gap. Long-term, the ontology compiler should generate both the Pydantic models and the TypeScript types from a single ontology source, eliminating manual synchronization.

### 8.2 Capability Registry (Layer 3)

Abstract interfaces for every externalizable capability:

| Capability | Interface (proposed) | Current Provider | Future Providers |
|------------|---------------------|-----------------|-----------------|
| LLM (orchestrator) | `LLMProvider` | OllamaClient (qwen2.5:32b) | HF, OpenAI, Anthropic, cloud Ollama |
| LLM (creative writer) | `LLMProvider` | OllamaClient (deepseek-coder-v2) | HF, OpenAI, Anthropic |
| Image generation | `ImageGenerator` | StableDiffusionPipeline (SD v1.5) | FLUX/ComfyUI, SDXL, DALL-E, Midjourney API |
| Video generation | `VideoGenerator` | SVD-XT, Ken Burns (FFmpeg) | AnimateDiff, CogVideo, Kling, Runway |
| Voice synthesis | `VoiceSynthesizer` | edge-tts (AndrewMultilingualNeural) | XTTS, ElevenLabs, Coqui |
| Music composition | `MusicComposer` | (procedural, currently minimal) | MusicGen, AudioLDM, Suno |
| Rendering | `Renderer` | FFmpeg (libx264, Ken Burns effects) | Remotion, cloud render farms |
| Research | `ResearchProvider` | DuckDuckGo + Wikipedia + BeautifulSoup | Google, Bing, Perplexity |

The capability registry is configured in `config/movie_os.yaml` (provider assignments). The Cinema Production Engine requires that no intelligence-layer agent or orchestration-stage component import a provider directly; all access is through the registry.

### 8.3 Knowledge Graph (Layer 4)

The Production Knowledge Graph (PKG) is the canonical data structure. It stores instances of every ontology concept, their relationships, confidence levels, provenance, and lifecycle state. It is:

- **Canonical:** The single source of truth. All other representations (documents, manifests, prompts, scenes) are derived projections.
- **Immutable:** Every mutation creates a new revision. History is preserved.
- **Provenance-bearing:** Every node carries metadata about its origin, confidence, and validation state.
- **Regenerable:** The graph can be rebuilt from its sources.

The PKG is already implemented in `movie_os/genesis/pkg.py` (`ProductionKnowledgeGraph`) and specified in `docs/genesis/05_KnowledgeGraph.md`. The Cinema Production Engine extends its scope from pre-production-only to full-lifecycle: produced media, validation results, and asset references are all nodes in the graph.

### 8.4 Production Knowledge Package (Layer 4)

The PKP is the materialized, frozen output of GENESIS — a self-contained, validated specification that PROMETHEUS can execute without further creative input. It is:

- **Complete:** Every creative decision is made. No ambiguity remains.
- **Validated:** The completion gate has certified it (8 criteria).
- **Versioned:** It carries a version number and a content hash.
- **Executable:** PROMETHEUS can read it and produce media deterministically.

The PKP is already defined in the Genesis system (`movie_os/genesis/completion_gate.py` — 19 PKP specifications PKP-00 through PKP-18) and in Genesis2 (`movie_os/genesis2/models.py` — `ProductionKnowledgePackage`). The Cinema Production Engine requires that the PKP become the universal interface between GENESIS and PROMETHEUS.

### 8.5 Ontology (Layer 4)

The Genesis Ontology (GO) defines every concept in the cinematic production domain: story, scene, character, location, dialogue, prompt, visual style, emotional tone, scene class, production profile, etc. The ontology is:

- **Hierarchical:** GO-001 (core) → GO-101..119 (domain) → GO-201+ (specialized) → GO-200+ (generated).
- **Compiled:** The ontology compiler (`docs/genesis/07_Compiler.md`) parses ontology sources and generates code, schemas, and documentation.
- **Extensible:** New ontologies can be added without modifying existing ones.

### 8.6 Compiler (Layer 4)

The Ontology Compiler bridges human-authored ontology specifications and machine-readable artifacts. It:

- **Parses** ontology source files (YAML/Markdown).
- **Validates** them against the meta-ontology.
- **Generates** an Intermediate Representation (normalized graph).
- **Emits** TypeScript types, Python Pydantic models, JSON/YAML schemas, and Markdown projections.
- **Registers** generated ontologies (GO-200+) in a Generated Ontology Registry.

The compiler is deterministic: same input → same output. It resolves inheritance at compile time. It is specified in `docs/genesis/07_Compiler.md` and `docs/genesis/specifications/compiler/001 — Ontology Compiler Specification.md`.

### 8.7 Pipeline Orchestrator (Layer 6)

The pipeline service coordinates the execution of stages. The current backend pipeline has 6 stages:

| Stage | Order | Agent/Service | LLM | Output |
|-------|-------|--------------|-----|--------|
| Research | 0 | `ResearchStage` | — | `ResearchContext` |
| Story | 1 | `StoryGenerator` | orchestrator | Story outline (title, narrative, emotional arc, beats) |
| Scenes | 2 | `SceneDecomposer` | orchestrator | Scene list (narration, emotion, camera, lighting, visual prompt, scene_class, duration) |
| Dialogues | 3 | `DialogueGenerator` | creative_writer | Per-scene dialogue lines |
| Prompts | 4 | `CinematicPromptGenerator` | orchestrator | Per-scene cinematic prompts |
| Validation | 5 | `YAMLValidator` + `MetricsCollector` | — | Validation pass + quality metrics |

The production profile system (`config/production_profiles.yaml`) feeds target scene count, duration ranges, and scene class guidance into stages 1 and 2.

### 8.8 Production Profiles (Layer 4 / Configuration)

Production profiles define runtime targets, scene policies, and scene classes. They are the first shared configuration between the backend pipeline and the Genesis branding. Five profiles are currently defined:

| Profile | Runtime | Scenes | Scene Duration |
|---------|---------|--------|----------------|
| youtube_longform (default) | 15-20 min | 12-16 | 75-90s |
| short_documentary | 20-30 min | 16-22 | 80-100s |
| childrens_story | 8-15 min | 9-14 | 60-80s |
| devotional_story | 12-18 min | 11-16 | 70-90s |
| feature_episode | 30-45 min | 22-32 | 85-110s |

Nine scene classes provide soft guidance: hook, establishment, dialogue, emotional_peak, montage, reflection, transition, climax, epilogue.

### 8.9 Experience Layer (Layer 7)

The Next.js 14 frontend presents the engine through a tab-based interface:

| Tab | Maps to | Content |
|-----|---------|---------|
| Input | Pre-pipeline | Story input form, production profile selector, director's brief |
| Genesis | Pre-production engine | Genesis config panel |
| Genesis2 | 12-phase engine | Genesis2 panel |
| Story | research + story + dialogues + validation | Story viewer, research panel, dialogue panel, metrics |
| Scenes | scenes + prompts | Scene timeline with cinematic prompts |
| Images | post-pipeline media | Image gallery with synopsis, generate/regenerate |
| Video | post-pipeline media | Video player, clip generator, mode selector (Ken Burns / SVD-XT) |

### 8.10 Operational Memory (Foundation)

The `.project-ai/` directory holds the engine's runtime memory:

| File | Purpose |
|------|---------|
| `PROJECT_MEMORY.yaml` | Stable long-term project memory (architecture, tech stack, decisions) |
| `SESSION_STATE.yaml` | Compressed operational state (completed/pending work, blockers, next actions) |
| `CURRENT_TASK.md` | Active scoped task (objective, constraints, done conditions, files in scope) |
| `RESTART_PROMPT.md` | Minimal bootstrap to resume work in a new session |

The checkpoint protocol (every 30 minutes or after meaningful task completion) ensures the engine's operational state is always recoverable.

---

## 9. The Four Pillars: GENESIS, PROMETHEUS, ATLAS, ORACLE

The Cinema Production Engine is organized around four intelligence pillars. Each pillar is a self-contained multi-agent system with its own internal architecture, but all four share the same knowledge graph, capability registry, and domain model. They communicate through the knowledge graph, not through direct calls.

### 9.1 GENESIS — Pre-Production Intelligence (Exists)

**Role:** The "Know" pillar. GENESIS transforms incomplete human creative intent into a complete, validated, internally consistent Production Knowledge Package.

**Status:** Exists and is constitutionally governed. Implemented in `movie_os/genesis/` (the constitutional engine with 30 agents, PKG, completion gate) and `movie_os/genesis2/` (the 12-phase creative intelligence pipeline). The backend pipeline (`backend/app/services/pipeline_service.py`) is a lighter implementation that shares the production profile system.

**Boundary:** GENESIS ends at the conclusion of pre-production. GENESIS produces no media. GENESIS owns knowledge, not pixels.

**Internal Architecture:**

```
GENESIS
├── Discovery (7 agents)
│   ├── IntentAnalyst — what does the human want?
│   ├── ThemeAnalyst — what is this about?
│   ├── EmotionAnalyst — what should the audience feel?
│   ├── ConflictAnalyst — what is the tension?
│   ├── AudienceAnalyst — who is this for?
│   ├── GapAnalyst — what is missing from the input?
│   └── QuestionPlanner — what must GENESIS decide?
│
├── PKP Generation (19 agents, in dependency order)
│   ├── Vision, CreativeStrategy, Project
│   ├── Research, Story, World
│   ├── Character, Relationship, Psychology
│   ├── Narrative, Directorial, ProductionDesign
│   ├── AudioIntent, EditingLanguage, AnimationIntent
│   ├── Blueprint, Distribution, Quality
│   └── KnowledgeGraph
│
├── Review (4 reviewers + ChiefArchitect)
│   ├── StoryReviewer, CharacterReviewer
│   ├── NarrativeReviewer, PsychologyReviewer
│   └── ChiefArchitect (final supervisor)
│
└── Completion Gate (8 criteria)
    ├── All 19 PKP specifications exist
    ├── All dependencies satisfied
    ├── Validation passed
    ├── No critical contradictions
    ├── Confidence thresholds met
    ├── Reviews completed
    ├── Knowledge graph complete
    └── Blueprint derived
```

**Genesis2 (deep mode):** The 12-phase Creative Intelligence pipeline (CreativeUnderstanding → StoryFoundation → CharacterPsychology → WorldDevelopment → NarrativeExpansion → ScenePlanning → DialoguePlanning → VisualLanguage → ProductionSpecifications → Validation → CreativeCritique → KnowledgeIntegration), each running Draft→Review→Critique→Improve→Validate→Freeze.

**Constitutional Governance:** GENESIS is governed by the Genesis Foundational Standards (GFS-000..009), established in `docs/genesis/02_Constitution.md`. Key invariants:

- GFS-000: The Constitutional Charter is supreme authority.
- GFS-001: GENESIS is provider-agnostic, implementation-agnostic, medium-agnostic.
- GFS-003: The PKG is the single source of truth. Provenance is mandatory.
- GFS-004: GENESIS produces no media.

**Convergence Mandate:** The three parallel pre-production paths (backend pipeline, Genesis, Genesis2) must converge into a single canonical path with two modes (fast/deep), both writing to the same PKG and producing the same PKP schema. The production profile system is the first shared component.

### 9.2 PROMETHEUS — Production Intelligence (Proposed)

**Role:** The "Make" pillar. PROMETHEUS reads the Production Knowledge Package and realizes it as media. It is the compiler backend that turns creative knowledge into pixels, frames, and waveforms.

**Status:** Does not yet exist as a unified system. Its capabilities are currently scattered across `image_service.py`, `video_service.py`, `tts_service.py`, and the `config/movie_os.yaml` pipeline steps. The Cinema Production Engine establishes PROMETHEUS as the unifying intelligence for all media production.

**Etymology:** Prometheus (Greek: "forethought") is the titan who stole fire from the gods and gave it to humanity. Fire is the power of creation realized. PROMETHEUS takes the creative knowledge (the fire's blueprint) and brings it into material existence.

**Boundary:** PROMETHEUS makes no creative decisions. It reads the PKP and executes. If the PKP says "Scene 3 is a close-up of Arjun's face, warm golden-hour lighting, 80 seconds, emotion: melancholy," PROMETHEUS generates that image, renders that clip, synthesizes that voice — but it does not decide what the scene should be. That decision was made by GENESIS and recorded in the PKP.

**Internal Architecture (Proposed):**

```
PROMETHEUS
├── Production Planner
│   Reads the PKP and produces a rendering plan:
│   which scenes, which assets, which capabilities,
│   which providers, in what order, with what dependencies.
│
├── Image Realization
│   For each scene: generates the scene image using the
│   cinematic prompt, visual style, camera angle, and
│   lighting from the PKP. Supports hero image generation
│   for character consistency, img2img with character
│   references, and CLIP-based verification.
│
├── Video Realization
│   For each scene: applies Ken Burns effects or SVD-XT
│   motion to the scene image. Duration driven by TTS
│   audio length or scene specification. Merges audio.
│
├── Voice Realization
│   For each scene: synthesizes TTS from dialogue.
│   Per-character voice identity, emotional prosody,
│   breathing, pace from the PKP's voice direction.
│
├── Music Realization (future)
│   Generates or selects music cues per the PKP's
│   music direction. Tempo, instrumentation, intensity
│   transitions mapped to scene emotional beats.
│
├── Assembly
│   Concatenates clips, mixes audio tracks, applies
│   transitions, produces the final video file.
│   FFmpeg is the primary renderer.
│
└── Asset Emission
    Writes all produced media into ATLAS with full
    provenance: which PKP version, which providers,
    which models, which parameters, which timestamps.
```

**Key Principle:** PROMETHEUS is deterministic given the same PKP and the same provider versions. Re-rendering with the same PKP produces the same output. Changing the output requires amending the PKP, not adjusting PROMETHEUS.

### 9.3 ATLAS — Persistence Intelligence (Proposed)

**Role:** The "Remember" pillar. ATLAS holds the engine's memory across productions, sessions, and model changes. It is the asset store, the knowledge persistence layer, the model registry, and the content library.

**Status:** Does not yet exist as a unified system. Its functions are currently scattered: in-memory dicts for pipeline state (`_pipelines`, `_generation_states`, `_image_states`), local filesystem for output (`output/`, `output/videos/`), and the `.project-ai/` operational memory for session state.

**Etymology:** Atlas is the titan who holds up the world. ATLAS holds up the engine by persisting everything that must survive: knowledge, assets, models, and reusable creative elements.

**Boundary:** ATLAS is orthogonal to the four-layer stack. It spans all layers because persistence is needed at every level. ATLAS does not make creative decisions and does not render media; it stores and retrieves.

**Internal Architecture (Proposed):**

```
ATLAS
├── Asset Store
│   Images, clips, audio files, final videos.
│   Each asset carries provenance metadata:
│   source PKP, source scene, generating provider,
│   model version, generation parameters, timestamps.
│
├── Knowledge Persistence
│   The Production Knowledge Graph survives across
│   sessions. Today it is in-memory; ATLAS persists
│   it to disk (SQLite/PostgreSQL/DuckDB) with full
│   revision history.
│
├── Model Registry
│   Tracks which models produced which assets.
│   Enables reproducibility: given an asset, ATLAS
│   can tell you exactly which model, which version,
│   which parameters produced it.
│
├── Content Library
│   Reusable creative elements: character hero images,
│   location references, style presets, music beds,
│   voice profiles. These survive across productions
│   and can be shared between them.
│
└── Session Memory
│   The .project-ai/ operational memory system,
│   elevated from a convention to a managed service.
│   Checkpoint protocol becomes an ATLAS feature,
│   not a manual discipline.
```

### 9.4 ORACLE — Validation Intelligence (Proposed)

**Role:** The "Judge" pillar. ORACLE validates produced media against the Production Knowledge Package, scores quality, detects drift, enforces continuity, and produces a quality report that feeds back into the PKP.

**Status:** Does not yet exist as a unified system. Its functions are partially implemented in the backend `YAMLValidator` (checks scene field completeness) and the Genesis completion gate (validates pre-production output). The evaluation agents in `movie_os/agents/` (audio_mix, character_consistency, dialogue_quality, emotion_score, story_quality, visual_consistency, youtube_readiness) are proto-ORACLE components.

**Etymology:** The Oracle at Delphi saw truth that others could not. ORACLE sees the gap between creative intent (the PKP) and creative realization (the media) and speaks it plainly.

**Boundary:** ORACLE does not override human intent. It reports. The human decides whether to accept, revise, or re-render. ORACLE's output is a validation report, not a command.

**Internal Architecture (Proposed):**

```
ORACLE
├── Structural Validation
│   Does the media match the PKP structurally?
│   Right number of scenes? Right durations?
│   All characters present? All locations depicted?
│
├── Visual Consistency
│   Does the character look the same across scenes?
│   Does the location maintain its identity?
│   CLIP-based verification (already prototyped in
│   image_verifier.py) extended to full production.
│
├── Emotional Arc Adherence
│   Does the rendered video's emotional trajectory
│   match the PKP's emotional arc specification?
│   Scene-by-scene emotion scoring against the
│   declared emotional_beat.
│
├── Continuity Enforcement
│   Props, wardrobe, blocking, lighting continuity
│   across scenes. Detects jarring transitions.
│
├── Drift Detection
│   Compares the final output against the PKP and
│   flags any creative decisions that PROMETHEUS
│   made silently (without PKP authorization).
│
├── Quality Scoring
│   Aggregate quality score across dimensions:
│   visual quality, audio quality, narrative
│   coherence, emotional impact, technical
│   correctness.
│
└── Validation Report
│   Written into the PKP as validation provenance.
│   Feeds back into GENESIS for revision if needed.
```

### 9.5 Pillar Interaction Model

The four pillars communicate exclusively through the knowledge graph:

```
    Human Intent
         │
         ▼
    ┌─────────┐
    │ GENESIS  │──── writes ────►  PKG / PKP
    └─────────┘                      │
         ▲                           │
         │ reads (for revision)      │ reads
         │                           ▼
    ┌─────────┐                  ┌───────────┐
    │ ORACLE   │◄── reads ──────│ PROMETHEUS │
    └─────────┘    (media +     └───────────┘
         │          PKP)              │
         │                           │
         └── writes ──────────────────┘
            (validation               │
             provenance)              │
                                 writes (assets
                                      + provenance)
                                      │
                                      ▼
                                 ┌─────────┐
                                 │  ATLAS   │
                                 └─────────┘
```

**Invariants:**

1. GENESIS never calls PROMETHEUS. It writes the PKP and signs off.
2. PROMETHEUS never calls GENESIS. It reads the PKP and executes.
3. ORACLE never calls PROMETHEUS or GENESIS. It reads both their outputs and writes validation provenance.
4. ATLAS never calls any pillar. It is called by them (to store and retrieve).
5. The human can intervene at any boundary: amend the PKP (re-enter GENESIS), re-render (re-enter PROMETHEUS), override ORACLE's report, or query ATLAS.

---

## 10. Compiler Philosophy

### 10.1 The Engine Is a Compiler, Not a Generator

The fundamental metaphor of the Cinema Production Engine is compilation, not generation. This is not a poetic analogy; it is an architectural constraint.

| Compiler Concept | Cinema Production Engine Equivalent |
|-----------------|--------------------------------------|
| Source program | Human creative intent (synopsis, idea, screenplay) |
| Frontend (parser, type checker) | GENESIS (Discovery + PKP Generation + Review + Gate) |
| Intermediate Representation (IR) | Production Knowledge Graph (PKG) |
| Compiled artifact | Production Knowledge Package (PKP) |
| Backend (code generation) | PROMETHEUS (rendering pipeline) |
| Binary / output | Final video (MP4) |
| Type checker | ORACLE (validation) |
| Linker | PROMETHEUS Assembly (clip concatenation, audio mixing) |
| Build system | Orchestration layer (pipeline service, workflows) |
| Compiler toolchain | Capability registry + provider layer |
| Determinism property | Same PKP + same providers → same output |
| Reproducible builds | Re-rendering with frozen PKP and frozen provider versions |

### 10.2 What This Means in Practice

1. **The PKP is the IR.** It is stable, inspectable, and portable. You can serialize it, transmit it, and recompile it on a different machine with different providers.

2. **Re-rendering is recompilation.** If you don't like how a scene looks, you don't change the renderer's parameters — you amend the PKP (which changes the IR) and recompile. If you just want a different visual style without changing the creative intent, you swap the provider (which changes the compiler backend) and recompile.

3. **The compiler is deterministic.** Given the same PKP and the same provider versions, the output is the same. This is the "deterministic creative replay" principle (§3.6).

4. **The ontology compiler is a meta-compiler.** It compiles the ontology (the type definitions) into code (Pydantic models, TypeScript types), schemas (JSON Schema, YAML), and documentation (Markdown). It is the compiler that builds the compiler. It already exists in `docs/genesis/07_Compiler.md`.

### 10.3 What the Compiler Philosophy Excludes

- **No creative emergence.** The output is not "inspired" by the input; it is a deterministic transformation of it. If the output surprises, it is because the PKP contained more than the human realized — not because the model "got creative."
- **No silent parameter drift.** If a rendering parameter changes, it must be recorded in the PKP or the provider configuration. Silent changes break reproducibility.
- **No non-deterministic providers in the critical path.** LLMs are inherently stochastic, but GENESIS uses temperature/top_p to control this and records the parameters in provenance. Image generators use fixed seeds (already implemented in `image_service.py` with `generator.manual_seed(seed)`). Video generators must do the same.

---

## 11. Production Package Philosophy

### 11.1 The PKP Is a Contract

The Production Knowledge Package is a contract between GENESIS and PROMETHEUS. GENESIS guarantees that every creative decision is made. PROMETHEUS guarantees that it will execute those decisions faithfully. The PKP is the artifact that enforces this contract.

### 11.2 PKP Completeness Criterion

A PKP is complete when:

1. **Every scene is specified.** Scene goal, emotional goal, conflict, beginning/middle/ending, transition, visual progression, dialogue progression, music progression, lighting progression, camera progression, character movement, silence moments, reaction shots, close-ups, environmental details, narrative purpose, production complexity. (From the GENESIS Scene Blueprint specification.)

2. **Every character is specified.** Biography, psychology, motivations, fear, desires, secrets, strengths, weaknesses, speaking style, vocabulary, body language, facial expressions, emotional triggers, relationships, growth arc, wardrobe, visual identity, color identity, voice identity, camera preference, lighting preference, reference objects, consistency rules. (From the GENESIS Character Bible specification.)

3. **Every location is specified.** Architecture, mood, lighting, time of day, textures, soundscape, weather, props, symbolism, transitions, camera possibilities. (From the GENESIS Location Bible specification.)

4. **Every dialogue is specified.** Written by experienced screenwriter standards: no robotic text, no exposition dumps, characters interrupt, hesitate, change opinions, react emotionally, use silence and subtext. Duration naturally 60-100 seconds per scene. (From the GENESIS Dialogue specification.)

5. **Every visual direction is specified.** Mood, camera language, lens, composition, movement, blocking, lighting, color palette, symbolism, depth, foreground, background, textures, atmospherics, visual metaphors. (From the GENESIS Visual Direction specification.)

6. **Every music direction is specified.** Theme, instrumentation, tempo, intensity, transitions, silence, emotion. (From the GENESIS Music Direction specification.)

7. **Every voice direction is specified.** Per character: tone, energy, pace, breathing, emotion, accent, age, delivery style. (From the GENESIS Voice Direction specification.)

8. **Production metadata is complete.** Scene IDs, dependencies, continuity IDs, characters, props, assets required, wardrobe, music cue, voice cue, visual cue, difficulty, estimated runtime, estimated cost, risk, priority. (From the GENESIS Production Metadata specification.)

9. **Validation has passed.** Character consistency, dialogue consistency, narrative consistency, world consistency, visual consistency, emotional consistency, timeline consistency, continuity, scene duration, story pacing. (From the GENESIS Validation specification.)

10. **The completion gate has certified.** All 8 criteria (see §9.1) are satisfied.

### 11.3 PKP Immutability

Once the completion gate passes, the PKP is frozen. It carries a version number and a content hash. Any amendment creates a new version. PROMETHEUS renders against a specific version. This ensures that "the video I made last week" and "the video I make today" are traceable to the same PKP version unless the human explicitly amended it.

### 11.4 PKP Portability

The PKP is a self-contained artifact. It can be:

- Serialized to JSON/YAML and stored in ATLAS.
- Transmitted to another machine for rendering with different providers.
- Version-controlled in git alongside the source story.
- Published as a creative work in its own right (the "screenplay" of the AI era).
- Used as input to a different Cinema Production Engine instance with different models.

---

## 12. Model Independence

### 12.1 The Principle

The Cinema Production Engine must remain valid whether it runs on qwen2.5:32b, deepseek-coder-v2, GPT-12, Claude-7, Llama-5, or a completely different architecture 20 years from now. This is already established in the Genesis Foundational Standards: GFS-001 states GENESIS is "provider-agnostic, implementation-agnostic, medium-agnostic."

### 12.2 How Model Independence Is Achieved

1. **Capability registry.** Every model access goes through an abstract interface (`LLMProvider`, `ImageGenerator`, etc.). No intelligence-layer agent imports a model directly.

2. **Provider configuration.** `config/movie_os.yaml` and `config/llm_config.yaml` map capabilities to providers. Changing the provider is a configuration change, not a code change.

3. **Tiered model routing.** Already implemented in `movie_os/genesis/llm_factory.py`: different model tiers (discovery, pkp, reviewer, chief) can use different models. A cheap model can do discovery; an expensive model can do the final review.

4. **Prompt template independence.** `config/prompts.py` defines prompt templates that are model-agnostic. They describe what the LLM should produce, not how the LLM should be called. The OllamaClient (`config/ollama_client.py`) handles the transport.

5. **Seed-based reproducibility.** Image and video generators use fixed seeds (`generator.manual_seed(seed)`). The same seed + same model + same prompt = same output. If the model changes, the output changes — but the creative intent (in the PKP) does not.

### 12.3 What Model Independence Does Not Mean

- It does not mean all models produce the same output. Different models will produce different quality. The engine does not guarantee quality; it guarantees that the creative decisions are model-independent.
- It does not mean the engine works without models. The engine requires at least one provider per capability. "Model independence" means the specific model is replaceable, not that models are optional.
- It does not mean prompts are portable across models without adjustment. Prompt engineering is model-specific. The engine accommodates this through provider-specific prompt adapters (a future capability).

---

## 13. Human Creativity Philosophy

### 13.1 The Human Is the Author

The human is the author of the creative work. The engine is the studio that realizes the human's vision. This is not a courtesy; it is an architectural principle:

- The human provides the creative intent (synopsis, idea, screenplay).
- GENESIS amplifies the human's intent into a complete specification, but does not replace the human's judgment.
- The completion gate requires human sign-off (or explicit auto-approval configuration).
- The human can amend the PKP at any point and recompile.
- The human can override any creative decision GENESIS makes.

### 13.2 The Engine Eliminates Ambiguity, Not Authorship

The engine's job is to eliminate the gap between "what the human meant" and "what the system produced." It does this by making every creative decision explicit, not by making creative decisions on the human's behalf.

When GENESIS encounters ambiguity in the human's input, it does not guess silently. The Discovery agents (IntentAnalyst, GapAnalyst, QuestionPlanner) identify the ambiguity, and GENESIS either infers a decision (with a confidence level) or asks the human. The confidence taxonomy (`explicit / inferred / confirmed / assumed / unknown`) from the Genesis master prompt is the mechanism.

### 13.3 Creative Authority Hierarchy

```
1. Human author (supreme)
2. Constitutional standards (GFS-000..009) — the rules of the game
3. Production Knowledge Package — the human's intent, elaborated
4. GENESIS agents — execute the elaboration
5. PROMETHEUS — executes the PKP
6. ORACLE — validates the execution
7. ATLAS — remembers everything
```

No entity in tier 4-7 can override a decision in tier 1-3. The human can always override the PKP. The constitution can only be amended through the governance workflow (established in `docs/genesis/workflows/governance/`).

### 13.4 Family-Safe by Default

The engine defaults to family-safe content: no gratuitous profanity, no obscenity, no explicit sexual content, no graphic violence. This is already encoded in the Genesis system prompt rules ("Avoid unnecessary profanity. Avoid obscenity. Avoid explicit sexual descriptions. The emotional intensity should come from psychology rather than graphic content.") and in the image service's negative prompts ("cartoon, painting, illustration, blurry, low quality, distorted, deformed").

The engine supports explicit configuration overrides for adult content (via production profiles or content ratings), but the default is safe. This is a design philosophy, not a censorship policy: the engine serves the broadest audience by default and allows opt-in for narrower audiences.

---

## 14. AI Film Director Philosophy

### 14.1 The Director Is a Role, Not a Person

The "AI Film Director" is not a single agent or a single model. It is a role distributed across the four pillars:

| Directorial Function | Pillar | Agent(s) |
|---------------------|--------|----------|
| Understanding the human's vision | GENESIS | IntentAnalyst, ThemeAnalyst, EmotionAnalyst |
| Planning the narrative structure | GENESIS | StoryAgent, NarrativeAgent, ScenePlanning phase |
| Directing character performance | GENESIS | CharacterAgent, PsychologyAgent, DialoguePlanning phase |
| Defining visual language | GENESIS | DirectorialAgent, ProductionDesignAgent, VisualLanguage phase |
| Defining audio language | GENESIS | AudioIntentAgent, EditingLanguageAgent |
| Executing the direction | PROMETHEUS | Image Realization, Video Realization, Voice Realization |
| Verifying the direction was followed | ORACLE | Visual Consistency, Emotional Arc Adherence, Drift Detection |
| Remembering the direction for future productions | ATLAS | Content Library, Model Registry |

### 14.2 The Director Does Not Improvise

A human film director on a set makes real-time creative decisions: "move the camera left," "say the line again with more sadness," "change the lighting to golden hour." The AI Film Director does not do this. It makes all directorial decisions in pre-production (GENESIS), records them in the PKP, and then PROMETHEUS executes them faithfully.

This is the compilation philosophy applied to directing: the director's vision is the source program; the film is the compiled binary. You don't direct while compiling; you direct before compiling.

### 14.3 The Director Respects the Human

The AI Film Director serves the human's creative intent. It does not impose its own vision. When GENESIS's DirectorialAgent proposes a visual style, it is proposing — not deciding. The human can accept, reject, or modify. The PKP records the human's decision, not the agent's proposal.

### 14.4 The Existing cinema_director Persona

The repository already contains a `cinema_director` persona (`.aios/agents/cinema_director.md`) described as a "Visual & Narrative Stylist" that "translates high-level creative prompts into strict cinemaProductiondesignInputs." This is a proto-directorial function. The Cinema Production Engine formalizes the directorial role as distributed across GENESIS's agents (particularly DirectorialAgent, ProductionDesignAgent, and the Genesis2 VisualLanguage phase), rather than as a single persona.

---

## 15. Knowledge Graph Philosophy

### 15.1 The Graph Is the Engine's Memory

The Production Knowledge Graph (PKG) is the engine's memory. Without it, the engine is stateless — every production starts from scratch, no learning transfers, no characters persist. With it, the engine accumulates knowledge: character identities, location definitions, style presets, provenance chains, and validation results.

### 15.2 Graph Properties

The PKG is:

- **Canonical:** The single source of truth. All other representations are projections.
- **Immutable:** Every mutation creates a new revision. History is preserved.
- **Provenance-bearing:** Every node carries metadata about its origin, confidence, and validation state.
- **Queryable:** The graph supports queries ("what characters appear in scene 3?", "what locations are used in this production?", "what is the provenance of this image?").
- **Regenerable:** The graph can be rebuilt from its sources (the PKP specifications and the human input).
- **Extensible:** New ontology concepts can be added without modifying existing nodes.

### 15.3 Graph Topology

The PKG contains:

- **Nodes:** Instances of ontology concepts (Story, Scene, Character, Location, Dialogue, Prompt, Image, Clip, Video, etc.).
- **Edges:** Relationships between nodes (Scene features Character, Scene occurs at Location, Image depicts Scene, Clip is derived from Image, Video is assembled from Clips).
- **Properties:** Metadata on nodes and edges (confidence level, provenance, timestamps, version).
- **Revisions:** Immutable history of every mutation.

### 15.4 Graph Lifecycle

```
1. GENESIS populates the graph during pre-production.
2. The completion gate validates the graph's completeness.
3. PROMETHEUS reads the graph to plan rendering.
4. PROMETHEUS writes produced media references into the graph.
5. ORACLE reads the graph and produced media to validate.
6. ORACLE writes validation results into the graph.
7. ATLAS persists the graph to disk.
8. The human amends the graph (creating a new revision).
9. PROMETHEUS re-renders only the affected nodes.
```

### 15.5 Current Implementation

The PKG is implemented in `movie_os/genesis/pkg.py` (`ProductionKnowledgeGraph`) and specified in `docs/genesis/05_KnowledgeGraph.md`. The Genesis2 system produces a `ProductionKnowledgePackage` (`movie_os/genesis2/models.py`). The Cinema Production Engine requires that the PKG's scope be extended from pre-production-only to full-lifecycle, and that it be persisted by ATLAS rather than held in memory.

---

## 16. Extensibility Philosophy

### 16.1 Extension Points

The engine is designed for extension at every layer:

| Layer | Extension Point | How to Extend |
|-------|----------------|---------------|
| Domain Model | New Pydantic types | Add to `config/models.py` or `schemas.py` |
| Provider | New model/renderer | Implement the capability interface, register in `movie_os.yaml` |
| Capability | New capability | Define abstract interface, add to registry |
| Knowledge | New ontology concept | Define in GO ontology, compile with ontology compiler |
| Intelligence | New agent | Implement agent class, register in GENESIS/PROMETHEUS/ORACLE/ATLAS |
| Orchestration | New pipeline stage | Add to `pipeline_service.py`, update frontend tabs |
| Experience | New UI surface | Add tab, CLI command, or API endpoint |
| Configuration | New production profile | Add to `production_profiles.yaml` |

### 16.2 Extension Rules

1. **Extensions must not break existing interfaces.** A new image provider must implement `ImageGenerator`; it must not require changes to `ImageGenerator`.
2. **Extensions must declare their dependencies.** A new agent must declare which PKP specifications it consumes and produces.
3. **Extensions must carry provenance.** A new provider must record its identity, version, and parameters in every asset it produces.
4. **Extensions must be configurable.** A new capability must be enabled/disabled through configuration, not through code changes.
5. **Extensions must respect the constitutional hierarchy.** A new agent must obey the GFS standards (no media in GENESIS, no creative decisions in PROMETHEUS, etc.).

### 16.3 Plugin Architecture (Future)

The long-term goal is a plugin architecture where extensions are self-contained packages:

```
plugins/
  flux-comfyui-provider/     # New image provider
  elevenlabs-voice/          # New voice provider
  animate-diff-video/        # New video provider
  character-consistency-agent/  # New ORACLE agent
  bollywood-style-profile/  # New production profile
```

Each plugin declares its capabilities, dependencies, and configuration schema. The engine loads plugins at startup and registers them in the capability registry. This is a future objective, not a current implementation.

---

## 17. Enterprise Architecture Principles

### 17.1 Separation of Concerns

Each layer, each pillar, each component has exactly one responsibility. Violations of separation of concerns are architectural bugs:

- The frontend must not contain pipeline logic. (Currently: the frontend's `store.ts` contains polling logic — acceptable as an orchestration concern, but pipeline stage logic must stay in the backend.)
- The pipeline service must not call LLM providers directly. (Currently: it goes through `StoryGenerator`, `SceneDecomposer`, etc., which use `OllamaClient` — correct.)
- The knowledge graph must not depend on any specific LLM. (Currently: correct — the PKG is model-agnostic.)
- GENESIS must not render media. (Currently: correct — GFS-004.)

### 17.2 Dependency Inversion

Dependencies point toward abstractions, not concretions. The intelligence layer depends on the capability registry (abstraction), not on OllamaClient (concretion). The orchestration layer depends on the intelligence layer's interfaces, not on specific agent implementations.

### 17.3 Single Responsibility Per Stage

Each pipeline stage does one thing:

| Stage | Responsibility | Does NOT do |
|-------|---------------|------------|
| Research | Gather external knowledge | Generate story content |
| Story | Generate narrative structure | Break into scenes |
| Scenes | Decompose into scenes | Write dialogue |
| Dialogues | Write spoken words | Generate visual prompts |
| Prompts | Generate cinematic prompts | Render images |
| Validation | Validate structure + metrics | Make creative decisions |

### 17.4 Observability

Every component must be observable: its inputs, outputs, timing, errors, and decisions must be logged and inspectable. The engine uses Python's `logging` module (already established: `logger = logging.getLogger("pipeline")`, `"image_service"`, `"video_service"`, etc.). The future goal is structured logging (JSON) that feeds into ORACLE's validation pipeline.

### 17.5 Testability

Every component must be testable in isolation. The current test infrastructure includes Vitest (frontend unit), Playwright (e2e), and Pytest (backend). The Genesis engine includes `MockLLMClient` for deterministic testing without LLM dependencies. The Cinema Production Engine requires that every new component ship with tests and that the test suite must be able to run without any external model dependencies (using mock providers).

### 17.6 Versioning

| What | Versioning Scheme | Current |
|------|-------------------|---------|
| This document | Semantic (MAJOR.MINOR.PATCH) | 1.0.0 |
| Production Knowledge Package | Content hash + version number | Per-production |
| Genesis Foundational Standards | GFS-NNN (immutable once ratified) | GFS-000..009 |
| Genesis Ontology | GO-NNN (immutable once ratified) | GO-001..GO-200+ |
| Production profiles | Semantic | In `production_profiles.yaml` |
| Pipeline stages | Named, ordered | 6 stages (research..validation) |
| API | URL-versioned | `/api/v1/` |

### 17.7 Backward Compatibility

The engine must not break existing productions. A PKP produced by version 1.0 must be renderable by version 1.5. Schema migrations must be automatic. Deprecated features must be documented with a sunset timeline. This is the "deterministic creative replay" principle applied across versions.

---

## 18. Future Roadmap

### Phase 1: Convergence (Current → Unified Pre-Production)

**Goal:** Unify the three parallel pre-production paths into a single canonical path with two modes.

- [ ] Define the canonical PKP schema that both fast mode and deep mode produce.
- [ ] Refactor the backend pipeline to produce the canonical PKP (fast mode).
- [ ] Refactor Genesis2 to produce the canonical PKP (deep mode).
- [ ] Make the production profile system the shared input to both modes.
- [ ] Establish the completion gate as the universal pre-production boundary.

### Phase 2: PROMETHEUS (Production Intelligence)

**Goal:** Establish PROMETHEUS as the unified production engine.

- [ ] Define the PROMETHEUS interface (reads PKP, writes to ATLAS).
- [ ] Refactor `image_service.py`, `video_service.py`, `tts_service.py` into PROMETHEUS components.
- [ ] Implement the Production Planner (reads PKP, produces rendering plan).
- [ ] Implement the Asset Emitter (writes to ATLAS with provenance).
- [ ] Make PROMETHEUS deterministic: same PKP + same providers → same output.

### Phase 3: ATLAS (Persistence)

**Goal:** Make the engine's memory permanent.

- [ ] Define the ATLAS interface (store, retrieve, query, persist).
- [ ] Persist the PKG to disk (SQLite or DuckDB).
- [ ] Implement the Asset Store with provenance metadata.
- [ ] Implement the Model Registry.
- [ ] Implement the Content Library (reusable characters, locations, styles).
- [ ] Elevate `.project-ai/` operational memory from convention to service.

### Phase 4: ORACLE (Validation)

**Goal:** Close the validation loop.

- [ ] Define the ORACLE interface (reads PKP + media, writes validation report).
- [ ] Implement Structural Validation (media matches PKP structure).
- [ ] Implement Visual Consistency (CLIP-based character/location identity).
- [ ] Implement Emotional Arc Adherence (scene-by-scene emotion scoring).
- [ ] Implement Continuity Enforcement (prop/wardrobe/lighting continuity).
- [ ] Implement Drift Detection (PROMETHEUS made no unauthorized decisions).
- [ ] Feed validation results back into the PKP.

### Phase 5: Full Lifecycle Compilation

**Goal:** The north star — full lifecycle from idea to finished film.

- [ ] Human expresses intent → GENESIS compiles PKP → PROMETHEUS renders → ORACLE validates → ATLAS persists.
- [ ] Human amends PKP → recompile only affected parts.
- [ ] Human can query ATLAS for any past production's PKP, assets, and provenance.
- [ ] Human can reuse characters, locations, and styles across productions via ATLAS Content Library.
- [ ] The entire production is reproducible from the PKP + provider versions.

### Phase 6: Plugin Architecture

**Goal:** Third-party extensibility.

- [ ] Define the plugin manifest schema.
- [ ] Implement plugin loading and registration.
- [ ] Ship reference plugins (FLUX/ComfyUI provider, ElevenLabs voice, AnimateDiff video).
- [ ] Document the plugin development guide.

### Phase 7: Enterprise Scale

**Goal:** Multi-user, multi-production, cloud-optional.

- [ ] Multi-user workspace (PKP ownership, permissions).
- [ ] Cloud deployment option (providers in cloud, knowledge on-premises).
- [ ] Distributed rendering (PROMETHEUS across multiple machines).
- [ ] Production queue (multiple PKPs rendering in parallel).
- [ ] Enterprise governance (audit trails, approval workflows, compliance reporting).

---

## 19. Glossary

| Term | Definition |
|------|-----------|
| **Cinema Production Engine** | The full system described in this document. The evolution of "Movie OS" and "Text Cinema Engine." |
| **GENESIS** | Pre-Production Intelligence. The "Know" pillar. Transforms creative intent into a PKP. Exists. |
| **PROMETHEUS** | Production Intelligence. The "Make" pillar. Realizes the PKP as media. Proposed. |
| **ATLAS** | Persistence Intelligence. The "Remember" pillar. Holds the asset store, knowledge persistence, model registry, and content library. Proposed. |
| **ORACLE** | Validation Intelligence. The "Judge" pillar. Validates media against the PKP. Proposed. |
| **PKG** | Production Knowledge Graph. The canonical, immutable, provenance-bearing graph of all creative knowledge. |
| **PKP** | Production Knowledge Package. The materialized, frozen, validated output of GENESIS. The contract between GENESIS and PROMETHEUS. |
| **GO** | Genesis Ontology. The type system of the cinematic production domain. |
| **GFS** | Genesis Foundational Standards (GFS-000..009). The constitutional layer of the engine. |
| **Ontology Compiler** | The system that compiles ontology sources into code, schemas, and documentation. |
| **Capability Registry** | The layer of abstract interfaces that decouples intelligence from providers. |
| **Production Profile** | A runtime target definition (e.g., youtube_longform 15-20 min) that drives scene count and duration policy. |
| **Scene Class** | A soft-guidance category for scenes (hook, dialogue, climax, etc.) with duration targets. |
| **Completion Gate** | The 8-criteria certification that a PKP is complete and ready for production. |
| **Provenance** | Metadata recording who decided what, when, on what evidence, at what confidence, using which model. |
| **Deterministic Creative Replay** | The property that the same PKP + same providers → same output. |
| **Fast Mode** | The backend 6-stage pipeline producing a subset PKP for rapid prototyping. |
| **Deep Mode** | The Genesis2 12-phase pipeline producing the full PKP with maximum creative rigor. |

---

## 20. Cross-References to Existing Repository

This section maps the constitutional concepts in this document to the specific files, directories, and artifacts that already exist in the repository. This is the grounding that makes this document implementation-grade rather than aspirational.

### 20.1 GENESIS (Exists)

| Constitutional Concept | Repository Location |
|----------------------|---------------------|
| Genesis constitutional standards (GFS-000..009) | `docs/genesis/02_Constitution.md`, `docs/genesis/03_GFS.md` |
| Genesis vision | `docs/genesis/00_Vision.md` |
| Genesis architecture | `docs/genesis/01_Architecture.md` |
| Genesis ontology (GO) | `docs/genesis/04_GO.md` |
| Production Knowledge Graph | `docs/genesis/05_KnowledgeGraph.md`, `movie_os/genesis/pkg.py` |
| Genesis runtime | `docs/genesis/06_Runtime.md` |
| Ontology compiler | `docs/genesis/07_Compiler.md`, `docs/genesis/specifications/compiler/001 — Ontology Compiler Specification.md` |
| Code generators | `docs/genesis/08_Generators.md` |
| Genesis engine (4 stages, 30 agents) | `movie_os/genesis/engine.py` |
| Genesis discovery agents | `movie_os/genesis/discovery/` |
| Genesis PKP agents (19) | `movie_os/genesis/pkp_agents/` |
| Genesis reviewers (4 + ChiefArchitect) | `movie_os/genesis/reviewers/`, `movie_os/genesis/chief_architect.py` |
| Genesis completion gate (8 criteria) | `movie_os/genesis/completion_gate.py` |
| Genesis master prompt (6 rules, confidence levels) | `movie_os/genesis/master_prompt.py` |
| Genesis2 (12-phase pipeline) | `movie_os/genesis2/` |
| Genesis2 models (ProductionKnowledgePackage) | `movie_os/genesis2/models.py` |
| Genesis2 phases | `movie_os/genesis2/phases/` |
| Genesis2 engine | `movie_os/genesis2/engine.py` |
| Genesis agent guide | `docs/genesis/AGENTS.md` |
| Genesis config/registry | `docs/genesis/genesis.yaml` |
| Original design conversation | `docs/genesisChatGPTCnversation-v1.md` |
| Backend Genesis agents (lighter) | `backend/app/services/genesis/` |
| Storyteller agent | `backend/app/services/genesis/storyteller_agent.py` |
| Prompt engineer agent | `backend/app/services/genesis/prompt_engineer_agent.py` |
| Audio director agent | `backend/app/services/genesis/audio_director_agent.py` |
| Manifest generator | `backend/app/services/genesis/manifest_generator.py` |
| Genesis prompt config | `backend/app/services/genesis/prompt_config.py` |
| Generated PKP artifact | `output/production_knowledge_package.json` |
| Generated Genesis2 phase artifacts | `output/phases/phase_01..phase_12.json` |

### 20.2 Backend Pipeline (Current Fast Mode)

| Constitutional Concept | Repository Location |
|----------------------|---------------------|
| Pipeline service (6 stages) | `backend/app/services/pipeline_service.py` |
| Pipeline API routes | `backend/app/api/v1/pipeline.py` |
| Pydantic schemas | `backend/app/models/schemas.py` |
| Domain models (Python dataclasses) | `config/models.py` |
| Prompt templates | `config/prompts.py` |
| LLM config | `config/llm_config.yaml` |
| Ollama client | `config/ollama_client.py` |
| Pipeline orchestrator (legacy) | `pipeline/orchestrator.py` |
| Research stage | `pipeline/research.py` |
| Output saver | `pipeline/output_saver.py` |
| Scene file writer | `pipeline/scene_file_writer.py` |
| Backend config | `backend/app/core/config.py` |
| FastAPI main | `backend/app/main.py` |

### 20.3 Production Profile System (Shared)

| Constitutional Concept | Repository Location |
|----------------------|---------------------|
| Production profiles config | `config/production_profiles.yaml` |
| Profile service | `backend/app/services/profile_service.py` |
| Profile API routes | `backend/app/api/v1/profiles.py` |

### 20.4 Media Generation (Proto-PROMETHEUS)

| Constitutional Concept | Repository Location |
|----------------------|---------------------|
| Image generation service | `backend/app/services/image_service.py` |
| Video generation service | `backend/app/services/video_service.py` |
| TTS service | `backend/app/services/tts_service.py` |
| Image verifier (CLIP-based, proto-ORACLE) | `backend/app/services/image_verifier.py` |
| Cinematic prompt builder | `backend/app/services/cinematic_prompts.py` |
| Movie OS config (provider assignments) | `config/movie_os.yaml` |
| Movie OS implementation | `movie_os/` (27 subdirectories) |
| Movie OS README (architecture) | `movie_os/README.md` |

### 20.5 Frontend (Experience Layer)

| Constitutional Concept | Repository Location |
|----------------------|---------------------|
| Pipeline view (7 tabs) | `frontend/src/components/pipeline/PipelineView.tsx` |
| Story input (profile selector) | `frontend/src/components/pipeline/StoryInput.tsx` |
| Story viewer | `frontend/src/components/story/StoryViewer.tsx` |
| Scene timeline | `frontend/src/components/scenes/SceneTimeline.tsx` |
| Image gallery (with synopsis) | `frontend/src/components/scenes/ImageGallery.tsx` |
| Video player | `frontend/src/components/video/VideoPlayer.tsx` |
| Clip generator | `frontend/src/components/video/ClipGenerator.tsx` |
| Frontend types | `frontend/src/lib/types.ts` |
| API client (with camelCase interceptor) | `frontend/src/lib/api.ts` |
| Zustand store | `frontend/src/lib/store.ts` |
| Utils (toCamelCase, stage labels) | `frontend/src/lib/utils.ts` |
| Home page | `frontend/src/app/page.tsx` |
| Pipeline detail page | `frontend/src/app/pipeline/[id]/page.tsx` |
| Projects pages | `frontend/src/app/projects/` |

### 20.6 Operational Memory

| Constitutional Concept | Repository Location |
|----------------------|---------------------|
| Operational memory system | `.project-ai/` |
| Project memory | `.project-ai/PROJECT_MEMORY.yaml` |
| Session state | `.project-ai/SESSION_STATE.yaml` |
| Current task | `.project-ai/CURRENT_TASK.md` |
| Restart prompt | `.project-ai/RESTART_PROMPT.md` |
| Agent instructions | `AGENTS.md` (root) |

### 20.7 Architecture Documents

| Constitutional Concept | Repository Location |
|----------------------|---------------------|
| Architecture stub | `ARCHITECTURE.md` |
| Machine-readable architecture | `.ai/architecture.yaml` |
| Architecture principles | `.ai/principles.yaml` |
| Identity | `.ai/identity.yaml` |
| Domain model (AI) | `.ai/domain_model.yaml` |
| Design patterns | `.ai/design_patterns.yaml` |
| Technical stack | `.ai/technical_stack.yaml` |
| Coding standards | `.ai/coding_standards.yaml` |
| Glossary | `.ai/glossary.yaml` |
| Roadmap stub | `ROADMAP.md` |
| Decision log stub | `DECISIONS.md` |
| Spec | `SPEC.md` |
| PRD | `docs/PRD_v1.yaml` |
| Story Context DNA methodology | `docs/generateStoryContextDna.md` |
| Cinema production design inputs | `docs/cinemaProductiondesignInputs*.md` |

### 20.8 Multi-Agent System (Proto-Pillars)

| Constitutional Concept | Repository Location |
|----------------------|---------------------|
| Movie OS agents (26 agents) | `movie_os/agents/` |
| Movie agent | `movie_os/agents/movie_agent.py` |
| AIOS cognitive backbone | `.aios/` |
| AIOS manifest | `.aios/AGENTS.md` |
| AIOS cinema_director persona | `.aios/agents/cinema_director.md` |
| Evaluation agents (proto-ORACLE) | `movie_os/agents/` (audio_mix, character_consistency, dialogue_quality, emotion_score, story_quality, visual_consistency, youtube_readiness) |
| Skills system (43 skills) | `skills/` |

---

## Document Authority

This document is the supreme architectural authority for the Cinema Production Engine repository. It is versioned semantically (currently 1.0.0). Amendments require a constitutional review process (to be defined in a future governance specification, following the Genesis governance workflow model in `docs/genesis/workflows/governance/`).

Every specification, design document, and implementation plan created in this repository after the ratification of this document must include a reference to the principle(s) from this document that authorize it. Specifications that cannot trace their justification to a principle in this document are architecturally orphaned and must either be amended to establish such a trace or be deprecated.

---

*"The engine treats film production as a compilation problem, not a generation problem. The human is the author; the engine is the studio. Knowledge outlives every model, every framework, and every runtime used to produce it."*

— Cinema Production Engine, Constitutional Architecture, §1