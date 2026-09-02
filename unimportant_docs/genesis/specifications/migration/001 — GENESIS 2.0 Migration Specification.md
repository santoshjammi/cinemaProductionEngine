# GENESIS 2.0 Migration Specification

**Status:** Constitutional Migration Blueprint — Implementation-Grade
**Version:** 1.0.0
**Date:** 2026-07-21
**Authority:** Derives from `00 — Cinema Production Engine Vision, Philosophy & Reference Architecture.md` (the Constitutional Architecture). This document is the master migration blueprint. All future implementation work follows the ordering and classification defined here.
**Precedence:** Below the Constitutional Architecture (§00). Above all domain specifications, workflow definitions, and implementation guides. When this document conflicts with an informal convention or legacy naming, this document wins unless the conflict is with the Constitutional Architecture itself.

---

## Table of Contents

**PART 1: CURRENT ARCHITECTURE ANALYSIS**
- [1.1 Strengths](#11-strengths)
- [1.2 Weaknesses](#12-weaknesses)
- [1.3 Duplication Map](#13-duplication-map)
- [1.4 Technical Debt Register](#14-technical-debt-register)
- [1.5 Architectural Inconsistencies](#15-architectural-inconsistencies)
- [1.6 Overlapping Responsibilities](#16-overlapping-responsibilities)
- [1.7 Missing Abstractions](#17-missing-abstractions)

**PART 2: TARGET ARCHITECTURE**
- [2.1 The Four-Pillar Model](#21-the-four-pillar-model)
- [2.2 Pillar Boundary Contracts](#22-pillar-boundary-contracts)
- [2.3 Cross-Pillar Communication](#23-cross-pillar-communication)
- [2.4 Subsystem Classification](#24-subsystem-classification)

**PART 3: GENESIS EVOLUTION**
- [3.1 Redefinition: From Pre-Production System to AI Film Director](#31-redefinition-from-pre-production-system-to-ai-film-director)
- [3.2 Specification Preservation Analysis](#32-specification-preservation-analysis)
- [3.3 Specification Expansion Analysis](#33-specification-expansion-analysis)
- [3.4 Specification Obsolescence Analysis](#34-specification-obsolescence-analysis)
- [3.5 Constitutional Amendments Required](#35-constitutional-amendments-required)

**PART 4: COMPILER ARCHITECTURE**
- [4.1 The Canonical Compiler Pipeline](#41-the-canonical-compiler-pipeline)
- [4.2 Compiler Pass Specifications](#42-compiler-pass-specifications)
- [4.3 Compiler Dependency Graph](#43-compiler-dependency-graph)
- [4.4 Compiler Validation Model](#44-compiler-validation-model)

**PART 5: PRODUCTION PACKAGE**
- [5.1 Canonical Production Package Definition](#51-canonical-production-package-definition)
- [5.2 Artifact Inventory](#52-artifact-inventory)
- [5.3 Ownership Model](#53-ownership-model)
- [5.4 Lifecycle](#54-lifecycle)
- [5.5 Identifier Scheme](#55-identifier-scheme)
- [5.6 Dependency Graph](#56-dependency-graph)
- [5.7 Regeneration Rules](#57-regeneration-rules)

**PART 6: NEW CONSTITUTIONS**
- [6.1 Existing Constitution Inventory](#61-existing-constitution-inventory)
- [6.2 New Constitutions Required](#62-new-constitutions-required)
- [6.3 Constitution Extension Map](#63-constitution-extension-map)

**PART 7: ROADMAP**
- [7.1 Migration Principles](#71-migration-principles)
- [7.2 Migration Phases](#72-migration-phases)
- [7.3 Risk Classification](#73-risk-classification)
- [7.4 Backward Compatibility Contract](#74-backward-compatibility-contract)

---

# PART 1: CURRENT ARCHITECTURE ANALYSIS

---

## 1.1 Strengths

The existing repository contains substantial architectural capital. These are decisions that are correct and must be preserved through the migration.

| # | Strength | Evidence | Preservation Requirement |
|---|----------|----------|-------------------------|
| S1 | **Constitutional governance layer is complete.** GFS-000..009 are full-text, self-consistent, and hierarchically ordered. | `docs/genesis/constitutions/` (10 files), `docs/genesis/02_Constitution.md` | Keep all 10 constitutions verbatim. New constitutions extend, never amend, the core 10. |
| S2 | **Ontology hierarchy is deep and domain-rich.** 28 ontology files across 10 subdirectories covering narrative, psychology, visual expression, audio, temporal experience, production planning, asset lineage, evaluation, governance, creativity, strategy, wisdom/ethics, and meta-ontology. | `docs/genesis/ontology/` (GO-001..GO-119, GO-200, GO-201, GO-301) | Keep all ontologies. Extend with production-tier ontologies (GO-302+) for rendering, validation, and persistence domains. |
| S3 | **Production Knowledge Graph (PKG) is constitutionally canonical.** GFS-003 mandates the PKG as the single source of truth with mandatory provenance and immutable revisions. | `docs/genesis/05_KnowledgeGraph.md`, `movie_os/genesis/pkg.py` | The PKG becomes the communication bus for all four pillars. No architectural change; scope expansion only. |
| S4 | **Completion Gate enforces 8 criteria with 19 PKP specifications.** Pre-production output is certifiably complete before handoff. | `movie_os/genesis/completion_gate.py` (8 criteria), 19 PKP agent/spec pairs | Extend the gate for the expanded GENESIS scope (AI Film Director) but preserve the existing 8 criteria as the pre-production subset. |
| S5 | **Capability registry pattern decouples providers from intelligence.** `config/movie_os.yaml` defines 7 provider categories (image, video, voice, music, story, translation, research) with swappable implementations. | `config/movie_os.yaml`, `movie_os/capabilities/` | Elevate from configuration convention to constitutional interface (see §6.2 — Rendering Constitution). |
| S6 | **Production profile system is shared across pre-production paths.** 5 profiles, 9 scene classes, runtime/scene-count/duration policy — already consumed by both the backend pipeline and Genesis branding. | `config/production_profiles.yaml`, `backend/app/services/profile_service.py` | This is the first convergence point. Extend it to be the input to all compiler passes. |
| S7 | **Local-first inference is a stated principle.** `.ai/principles.yaml` declares "Local-First Inference" as an operating principle. Ollama, Stable Diffusion, SVD-XT, edge-tts all run locally. | `.ai/principles.yaml`, `config/llm_config.yaml`, `config/movie_os.yaml` | Preserve. Cloud providers are optional plugins behind the capability registry. |
| S8 | **Dual-model architecture is proven.** Orchestrator (qwen2.5:32b) handles structure; creative writer (deepseek-coder-v2) handles dialogue. Per-stage temperature/token/top_p tuning. | `config/llm_config.yaml` (stage_settings) | Preserve the tiered model concept. Generalize to N tiers via the existing `llm_factory.py` tiered routing. |
| S9 | **Operational memory system is actively maintained.** `.project-ai/` with checkpoint protocol is in current use (dated Jul 20 2026). | `.project-ai/PROJECT_MEMORY.yaml`, `SESSION_STATE.yaml`, `CURRENT_TASK.md`, `RESTART_PROMPT.md` | Elevate from convention to ATLAS-managed service. |
| S10 | **ADRs exist with constitutional justification.** 4 ADRs each trace to a GFS principle. | `docs/genesis/decisions/` (ADR-001..004 + template) | Preserve and extend. Every migration step in §7 generates an ADR. |
| S11 | **Workflow definitions exist for 8 workflow types.** Authoring, generation, review, validation, publication, deployment, governance, learning. | `docs/genesis/workflows/` (GWS-001..013) | Preserve. Extend with PROMETHEUS execution workflow and ORACLE validation workflow. |
| S12 | **Frontend tab structure maps cleanly to pipeline stages.** 7 tabs (input, genesis, genesis2, story, scenes, images, video) with disabled-state logic per stage. | `frontend/src/components/pipeline/PipelineView.tsx` | Preserve tab structure. Add pillar-aware routing (GENESIS tab → director mode selector, Video tab → PROMETHEUS status). |

---

## 1.2 Weaknesses

| # | Weakness | Impact | Root Cause |
|---|----------|--------|------------|
| W1 | **Three parallel pre-production paths produce incompatible outputs.** The backend 6-stage pipeline, the constitutional Genesis engine (4-stage, 30 agents), and Genesis2 (12-phase) all produce "pre-production output" but none produces the same schema. | Cannot swap between fast and deep modes. Frontend has separate tabs for each. PROMETHEUS cannot consume any of them uniformly. | Organic growth: the backend pipeline was built for the web app; Genesis and Genesis2 were built as standalone engines. No unification was mandated. |
| W2 | **PROMETHEUS does not exist.** Media generation is scattered across 3 services (`image_service.py`, `video_service.py`, `tts_service.py`) with no shared interface, no PKP consumption, and no deterministic replay guarantee. | No production intelligence. Rendering is ad-hoc per-service. Cannot re-render deterministically. Cannot validate media against creative intent. | Media services were built as web-app endpoints, not as pillar components. |
| W3 | **ATLAS does not exist.** Pipeline state is in-memory (`_pipelines` dict, `_generation_states` dict, `_image_states` dict). Knowledge is lost on restart. No asset store, no model registry, no content library. | No cross-production memory. Characters cannot persist. No reproducibility. Server restart loses all state. | Single-node prototype architecture was never upgraded. |
| W4 | **ORACLE does not exist as a unified system.** Proto-ORACLE evaluation agents exist in `movie_os/agents/evaluation/` (7 agents) and `image_verifier.py` (CLIP-based), but they are disconnected from the PKP and from each other. | No validation of media against creative intent. No drift detection. No quality report feeding back into the PKG. | Evaluation agents were built as Movie OS components, not as a pillar. |
| W5 | **No canonical Production Package schema.** The PKP concept exists in Genesis (19 specs) and Genesis2 (`ProductionKnowledgePackage` model), but there is no single schema that PROMETHEUS can consume. | PROMETHEUS cannot be built until the PKP schema is unified. | The PKP was specified constitutionally but never materialized as a single executable schema across all pre-production paths. |
| W6 | **In-memory state is not persistent.** `PipelineService._pipelines`, `GenerationState`, `ImageGenerationState` are all process-local dicts. | Server restart loses all pipelines. No history. No resumption. | Prototype architecture; persistence was deferred. |
| W7 | **Snake_case / camelCase mismatch between backend and frontend.** Backend returns snake_case; frontend expects camelCase. Required an Axios interceptor to bridge. | Fragile coupling. If either side changes field names, the interceptor breaks silently. | Backend uses Python/Pydantic (snake_case); frontend uses TypeScript (camelCase). No code generation from a single source. |
| W8 | **Plaintext API key committed in configuration.** `config/movie_os.yaml` line 778: `api_key: sk-lm-TkM3NqaZ:CQdNsDjxGRm17O3Gg59W`. | Security vulnerability. | Configuration-as-code without secret management. |
| W9 | **No unified compiler pipeline.** The "compiler" metaphor is documented (`docs/generateStoryContextDna.md`, `docs/genesis/07_Compiler.md`) but the ontology compiler only compiles ontology sources, not stories. There is no story-to-PKP compiler. | The "compilation over generation" philosophy cannot be enforced because there is no compiler. | The compiler concept was specified but never built for the creative pipeline. |
| W10 | **GFS-010 is referenced but does not exist.** PKP-18 (`specifications/pkp/18 — Knowledge Graph Specification.md`) references "GFS-010 — Production Knowledge Graph Specification" as a dependency. No file exists. | The PKG specification lacks constitutional authority. | A derived standard was referenced before being written. |
| W11 | **`.aios/` cognitive backbone is unscoped relative to the four-pillar architecture.** It overlaps with skills, Movie OS agents, and Genesis agents without a clear boundary. | Confusion about which orchestration layer owns what. | `.aios/` was built as a parallel cognitive layer without integration into the constitutional architecture. |
| W12 | **Frontend has no pillar awareness.** The UI presents "genesis" and "genesis2" as separate tabs rather than presenting GENESIS as one pillar with two modes. | User confusion. The architecture is invisible to the user. | The UI was built before the four-pillar architecture was defined. |

---

## 1.3 Duplication Map

| # | Concept | Location 1 | Location 2 | Location 3 | Resolution |
|---|---------|-----------|-----------|-----------|------------|
| D1 | Story generation | `pipeline/orchestrator.py` `StoryGenerator` | `movie_os/genesis/pkp_agents/story_agent.py` `StoryAgent` | `movie_os/genesis2/phases/phase02_story_foundation.py` | MERGE: All three become compiler passes within GENESIS. The backend pipeline's `StoryGenerator` becomes the "fast mode" implementation; Genesis's `StoryAgent` and Genesis2's `StoryFoundationPhase` become the "deep mode" implementation. Both produce the same PKP-04 Story Specification output. |
| D2 | Scene decomposition | `pipeline/orchestrator.py` `SceneDecomposer` | `movie_os/genesis/pkp_agents/blueprint_agent.py` | `movie_os/genesis2/phases/phase05_narrative_expansion.py` + `phase06_scene_planning.py` | MERGE: The backend `SceneDecomposer` and Genesis2's two phases (NarrativeExpansion + ScenePlanning) both produce scene specifications. They become the Scene Compiler pass with fast/deep modes. |
| D3 | Dialogue generation | `pipeline/orchestrator.py` `DialogueGenerator` | `movie_os/genesis2/phases/phase07_dialogue_planning.py` | `movie_os/agents/creative/dialogue_writer_agent.py` | MERGE: Three implementations of dialogue. The backend `DialogueGenerator` is the fast mode; Genesis2's DialoguePlanning is the deep mode. The Movie OS `DialogueWriterAgent` is a rendering-time concern (it writes the actual spoken words; the compiler pass plans the dialogue intent). Separate the planning (GENESIS) from the execution (PROMETHEUS). |
| D4 | Cinematic prompt generation | `pipeline/orchestrator.py` `CinematicPromptGenerator` | `backend/app/services/genesis/prompt_engineer_agent.py` | `movie_os/agents/planning/prompt_builder_agent.py` | MERGE: Three prompt builders. The backend `CinematicPromptGenerator` and the Genesis `PromptEngineerAgent` are the same function. The Movie OS `PromptBuilderAgent` is a planning-stage agent. All become the Prompt Compiler pass. |
| D5 | Image generation | `backend/app/services/image_service.py` | `movie_os/agents/creative/image_generator_agent.py` | `movie_os/agents/generation/image_generator_agent.py` | MERGE: Three image generation implementations. The backend `ImageGenerationService` is the web-app implementation. The two Movie OS agents are duplicate implementations (creative vs generation subpackages). All move to PROMETHEUS as the Image Realization component. |
| D6 | Video generation | `backend/app/services/video_service.py` | `movie_os/agents/creative/video_composer_agent.py` | `movie_os/agents/post_production/video_composer_agent.py` | MERGE: The backend `VideoGenerationService` handles SVD-XT + Ken Burns. The two Movie OS agents are duplicates. All move to PROMETHEUS as Video Realization. |
| D7 | Voice synthesis | `backend/app/services/tts_service.py` | `movie_os/agents/creative/voice_generator_agent.py` | `movie_os/agents/generation/voice_generator_agent.py` | MERGE: All move to PROMETHEUS as Voice Realization. |
| D8 | Audio mixing | (no backend service) | `movie_os/agents/creative/audio_mixer_agent.py` | `movie_os/agents/post_production/audio_mixing_agent.py` | MERGE: Two duplicate implementations. Both move to PROMETHEUS as Audio Assembly. |
| D9 | Quality evaluation | `backend/app/services/image_verifier.py` | `movie_os/agents/evaluation/` (7 agents) | `movie_os/genesis2/phases/phase10_validation.py` + `phase11_creative_critique.py` | MERGE: All move to ORACLE. The backend CLIP verifier, the 7 evaluation agents, and the 2 Genesis2 validation phases become ORACLE's validation passes. |
| D10 | Character specification | `docs/genesis/specifications/pkp/06 — Character Specification.md` (PKP-06) | `movie_os/genesis2/phases/phase03_character_psychology.py` | `docs/genesis/models/003 — Character Domain Model.md` | KEEP: PKP-06 is the specification; Genesis2's phase produces it; the domain model defines the types. These are correctly layered. No merge needed — they are specification, implementation, and type definition. |
| D11 | Production profile | `config/production_profiles.yaml` | `backend/app/services/profile_service.py` | (no other location) | KEEP: Single source. Already correct. |
| D12 | Music composition | `movie_os/agents/planning/music_composer_agent.py` | `movie_os/agents/creative/music_generator_agent.py` | `movie_os/agents/generation/music_generator_agent.py` + `movie_os/agents/music_agent.py` | MERGE: Four music implementations. The planning agent moves to GENESIS (Music Compiler pass). The three generation agents move to PROMETHEUS (Music Realization). |

---

## 1.4 Technical Debt Register

| ID | Debt Item | Severity | Location | Migration Action |
|----|-----------|----------|----------|-----------------|
| TD-001 | Plaintext API key in config | Critical | `config/movie_os.yaml:778` | Move to `.env` / environment variable. Remove from version control. |
| TD-002 | In-memory pipeline state (no persistence) | High | `pipeline_service.py:_pipelines`, `video_service.py:_generation_states`, `image_service.py:_image_states` | Replace with ATLAS-managed persistence. Phase 3 of roadmap. |
| TD-003 | `prompt_engineer_agent.py` has ~140 duplicated import lines | Medium | `backend/app/services/genesis/prompt_engineer_agent.py:11-153` | Clean up. The actual class is at line 156. |
| TD-004 | `prompt_engineer_agent.py` references undefined `visual_style_guides` variable | Medium | `backend/app/services/genesis/prompt_engineer_agent.py:184` | Fix or remove the dead code path. |
| TD-005 | `models.py` has duplicate `producer_brief` field | Low | `config/models.py:42-43` (two identical lines) | Remove duplicate. |
| TD-006 | Constitution filename naming inconsistency | Low | `docs/genesis/constitutions/` (mixed: `00-`, `01-`, `002 —`, `004 `, `003 –`) | Normalize to `NNN-Name.md` (zero-padded, hyphen-separated). |
| TD-007 | GO-004/GO-005 taxonomy mismatch | Medium | `docs/genesis/04_GO.md` (index says "Confidence and Provenance" / "Creative Intent"; files are "Knowledge Pattern Library" / "Reasoning Pattern Library") | Correct the index to match the files, or rename the files to match the index. Recommend: keep the files (they are richer) and correct the index. |
| TD-008 | GO-201/GO-301 placement ambiguity | Low | `docs/genesis/04_GO.md` labels GO-201 as "Specialized", GO-200 as "Generated", but both GO-201 and GO-301 physically live in `ontology/generated/` | Reconcile taxonomy. Recommend: GO-200 = "Generated Registry", GO-201..299 = "Specialized (derived)", GO-301..399 = "Production (derived)". All live in `ontology/generated/` but the index clarifies the tier. |
| TD-009 | GFS-010 referenced but not written | Medium | `docs/genesis/specifications/pkp/18 — Knowledge Graph Specification.md` references GFS-010 | Write GFS-010 as a derived standard (see §6.2). |
| TD-010 | `_rerun_from_stage` hardcodes `story_length: "medium"` | Medium | `backend/app/services/pipeline_service.py:428` | Use the actual pipeline's production profile. |
| TD-011 | Frontend camelCase interceptor is a band-aid | Low | `frontend/src/lib/api.ts` (`toCamelCase` interceptor) | Long-term: ontology compiler generates both Python and TypeScript types from a single source, eliminating the mismatch. |
| TD-012 | `README.md` is boilerplate from AI Studio | Low | `README.md` (20 lines) | Replace with the Cinema Production Engine overview. |
| TD-013 | `ARCHITECTURE.md` is a 3-line stub | Low | `ARCHITECTURE.md` | Replace with a pointer to the Constitutional Architecture (§00) and this document. |
| TD-014 | `.ai/decision_log.yaml` has single entry | Low | `.ai/decision_log.yaml` | Consolidate with `docs/genesis/decisions/` ADRs into a unified decision registry. |

---

## 1.5 Architectural Inconsistencies

| # | Inconsistency | Detail | Resolution |
|---|---------------|--------|------------|
| AI-1 | **Identity fragmentation.** The system is called "Text Cinema Engine" (`SPEC.md`), "Movie OS" (`movie_os/`, `.ai/identity.yaml`), "Cinema Production Engine" (§00 Constitutional Architecture), and "GENESIS" (the pre-production subsystem). | `.ai/identity.yaml` says `name: "Movie OS"`, `role: "Cinema Production Engine"`. The Constitutional Architecture says "Cinema Production Engine." `SPEC.md` says "Text Cinema Engine." | **Adopt "Cinema Production Engine" as the platform name.** "Movie OS" becomes a legacy alias. "Text Cinema Engine" is deprecated. GENESIS remains a pillar name, not the platform name. |
| AI-2 | **Three orchestration layers coexist without scoping.** The root `AGENTS.md` (OpenCode skills), `docs/genesis/AGENTS.md` (Genesis docs repo), and `.aios/AGENTS.md` (AIOS cognitive backbone) all define agent conventions. | Root AGENTS.md governs coding-agent workflow. Genesis AGENTS.md governs Genesis docs conventions. AIOS AGENTS.md governs the cognitive backbone. They don't conflict but they don't reference each other. | **Scope each explicitly:** root AGENTS.md = codebase engineering; Genesis AGENTS.md = Genesis specification authoring; AIOS AGENTS.md = runtime cognitive orchestration. Add cross-references. |
| AI-3 | **Pipeline stage naming varies across implementations.** Backend: research, story, scenes, dialogues, prompts, validation. Genesis: Discovery, PKP Generation, Review, Gate. Genesis2: 12 phases. Movie OS: narrative, images, audio, music, sfx, mix, video. | Four different stage vocabularies for overlapping work. | **Adopt the compiler pass vocabulary** (§4.1) as the canonical stage naming. Backend 6-stage, Genesis 4-stage, and Genesis2 12-phase become implementation modes of the compiler passes. |
| AI-4 | **Provider configuration lives in two places.** `config/llm_config.yaml` (LLM models, stage settings) and `config/movie_os.yaml` (image/video/voice/music providers, rendering, pipeline). | LLM config is separate from media config. Both define providers. No shared capability registry interface. | **Unify under a single capability registry** (§4.1 of Constitutional Architecture). `llm_config.yaml` and `movie_os.yaml` become provider-specific config files behind the registry. |
| AI-5 | **Frontend tabs expose implementation details.** Separate "Genesis" and "Genesis2" tabs reveal two engines to the user. | The user should see "GENESIS" (the pillar) with a mode selector (fast/deep), not two separate tabs. | **Merge genesis + genesis2 tabs** into a single GENESIS tab with mode selector. |

---

## 1.6 Overlapping Responsibilities

| # | Overlap | Systems Involved | Boundary Violation | Resolution |
|---|---------|-----------------|---------------------|------------|
| OR-1 | Story generation vs story specification | Backend `StoryGenerator` produces a story outline (narrative + beats). Genesis `StoryAgent` produces PKP-04 Story Specification. Genesis2 `StoryFoundationPhase` produces premise + acts + beats + rhythm. | All three produce "the story" but at different depths. The backend version is a shallow outline; the Genesis version is a full specification; Genesis2 is between. | **Define compiler pass depths:** The Story Compiler pass has a fast mode (backend: narrative + beats) and a deep mode (Genesis: full PKP-04 spec). Both produce the same PKP-04 output schema; fast mode fills fewer fields with lower confidence. |
| OR-2 | Scene decomposition vs scene planning | Backend `SceneDecomposer` produces scenes with narration/emotion/camera/lighting/visual_prompt. Genesis2 `ScenePlanningPhase` produces per-scene purpose/conflict/emotion/goals/transition/duration. Genesis `BlueprintAgent` produces shots/assets/characters/environments. | The backend produces "scenes"; Genesis2 produces "scene plans"; Genesis produces "blueprints." These are different abstraction levels of the same concept. | **Define three compiler passes:** Scene Compiler (scene structure), Shot Compiler (shot-level breakdown), Timeline Compiler (temporal arrangement). The backend's decomposer maps to Scene Compiler; Genesis2's planning maps to Scene + Shot; Genesis's blueprint maps to Shot + Timeline. |
| OR-3 | Dialogue writing vs dialogue planning | Backend `DialogueGenerator` writes actual spoken words. Genesis2 `DialoguePlanningPhase` plans dialogue intent/subtext/rhythm. Movie OS `DialogueWriterAgent` writes dialogue. | Planning (what the dialogue should achieve) and execution (the actual words) are conflated. | **Separate:** Dialogue Compiler (GENESIS) plans dialogue intent. PROMETHEUS Voice Realization generates the actual spoken words from the plan. The current backend `DialogueGenerator` output becomes the fast-modeDialogue Compiler output. |
| OR-4 | Prompt generation vs prompt engineering | Backend `CinematicPromptGenerator` generates visual prompts. Genesis `PromptEngineerAgent` engineers prompts for FLUX/ComfyUI. Movie OS `PromptBuilderAgent` builds prompts. | Three prompt builders with different targets (visual, FLUX, general). | **Unify under the Prompt Compiler pass.** The compiler produces medium-agnostic creative prompts (in the PKP). PROMETHEUS translates these into provider-specific prompts at render time. |
| OR-5 | Evaluation vs validation | Backend `YAMLValidator` validates structure. Genesis2 `ValidationPhase` + `CreativeCritiquePhase` validate content. Movie OS evaluation agents (7) evaluate quality. Genesis completion gate enforces 8 criteria. | Validation (structural) and evaluation (qualitative) are separate concerns scattered across systems. | **Unify under ORACLE.** Structural validation = ORACLE Structural Validation. Qualitative evaluation = ORACLE Quality Scoring. Pre-production gate = GENESIS completion gate (preserved). Media validation = ORACLE Drift Detection. |

---

## 1.7 Missing Abstractions

| # | Missing Abstraction | What It Would Do | Why It's Missing | Migration Action |
|---|---------------------|-----------------|------------------|-----------------|
| MA-1 | **Production Package schema (unified)** | A single, versioned, hashable JSON/YAML schema that all pre-production paths produce and PROMETHEUS consumes. | Three paths evolved independently; no one defined the shared schema. | §5 defines the canonical Production Package. |
| MA-2 | **PROMETHEUS interface** | An abstract interface that reads a PKP and produces media with provenance. | Media services were built as web-app endpoints, not as pillar components. | §2.1 defines the PROMETHEUS pillar boundary. |
| MA-3 | **ATLAS interface** | An abstract interface for asset storage, knowledge persistence, and retrieval with provenance. | In-memory dicts were sufficient for the prototype. | §2.1 defines the ATLAS pillar boundary. |
| MA-4 | **ORACLE interface** | An abstract interface that reads PKP + media and produces validation reports. | Evaluation was an afterthought; evaluation agents are disconnected. | §2.1 defines the ORACLE pillar boundary. |
| MA-5 | **Compiler pass interface** | An abstract interface for each compiler pass (Story, Scene, Dialogue, etc.) with standard input/output/validation. | The compiler concept was specified but never implemented for the creative pipeline. | §4 defines the compiler pass interface. |
| MA-6 | **Provider-agnostic prompt adapter** | A layer that translates PKP creative prompts into provider-specific prompts (FLUX, SD, SVD, etc.). | Prompts were hardcoded per service. | PROMETHEUS prompt adapter (Phase 2 of roadmap). |
| MA-7 | **Cross-production character registry** | A persistent registry of character identities, hero images, and voice profiles reusable across productions. | No persistence layer exists. | ATLAS Content Library (Phase 3 of roadmap). |
| MA-8 | **Deterministic replay registry** | A registry of (PKP version, provider versions) → output hash tuples, enabling verification of deterministic replay. | No one has needed replay yet because there is no PROMETHEUS. | ATLAS Model Registry (Phase 3 of roadmap). |

---

# PART 2: TARGET ARCHITECTURE

---

## 2.1 The Four-Pillar Model

The Cinema Production Engine v2.0 is organized around four intelligence pillars. Each is a self-contained system with its own internal architecture. All four share the same domain model, capability registry, and knowledge graph. They communicate exclusively through the Production Knowledge Graph and the Production Knowledge Package.

### GENESIS — Creative Intelligence, AI Film Director, Production Compiler

**Current state:** Exists as three parallel pre-production systems.
**Target state:** Unified AI Film Director and Production Compiler. Transforms creative intent into a validated Production Knowledge Package through a deterministic pipeline of compiler passes.

**Expanded responsibilities (from current):**
- AI Film Directorial Intelligence: makes every creative decision (visual, audio, narrative, performance) in pre-production, not during rendering.
- Production Compiler: compiles creative intent through a pipeline of passes (Story → Narrative → Screenplay → Director → Scene → Shot → Dialogue → Emotion → Character → Camera → Lighting → Music → Audio → Voice → Timeline → Prompt → Package).
- Two execution modes: Fast Mode (backend 6-stage pipeline, ~30 seconds) and Deep Mode (Genesis2 12-phase pipeline, ~30 minutes). Both produce the same PKP schema.
- Profile-driven planning: the production profile determines scene count, duration targets, and scene class distribution before compilation begins.

**Preserved responsibilities:**
- GFS-000..009 constitutional governance (all 10 constitutions remain in force).
- PKG as single source of truth (GFS-003).
- Completion gate (8 criteria, 19 PKP specifications).
- Discovery before decision (GFS-004).
- Provenance and confidence levels (GFS-003, master prompt).

**New boundaries:**
- GENESIS no longer ends at "pre-production" in the narrow sense. It ends at "creative decision completion." The AI Film Director makes every directorial decision; PROMETHEUS executes them. The boundary is the PKP, not an arbitrary phase line.
- GENESIS does not render media (preserved from GFS-004).
- GENESIS does not validate media (that is ORACLE's domain).
- GENESIS does not persist assets (that is ATLAS's domain).

### PROMETHEUS — Rendering Runtime, Media Generation, Execution Engine

**Current state:** Does not exist as a unified system. Media generation is scattered across `image_service.py`, `video_service.py`, `tts_service.py`, and Movie OS agents.
**Target state:** The unified production intelligence that reads a PKP and realizes it as media. The compiler backend that turns creative knowledge into pixels, frames, and waveforms.

**Responsibilities:**
- Production Planning: reads the PKP and produces a rendering plan (which scenes, which assets, which capabilities, which providers, in what order).
- Image Realization: generates scene images from cinematic prompts, visual styles, camera angles, and lighting specified in the PKP. Supports character consistency via hero image references.
- Video Realization: applies motion (Ken Burns, SVD-XT, or future providers) to scene images. Duration driven by TTS audio or scene specification.
- Voice Realization: synthesizes speech from dialogue plans in the PKP, using per-character voice identity and emotional prosody.
- Music Realization: generates or selects music per the PKP's music direction. (Currently procedural/numpy; future: MusicGen, AudioLDM.)
- Audio Assembly: mixes voice, music, SFX into per-scene audio tracks.
- Video Assembly: concatenates clips, applies transitions, produces the final video file.
- Asset Emission: writes all produced media into ATLAS with full provenance (PKP version, provider versions, model versions, parameters, timestamps).

**Boundaries:**
- PROMETHEUS makes zero creative decisions. It reads the PKP and executes.
- PROMETHEUS does not modify the PKG. It reads only.
- PROMETHEUS does not validate its own output. ORACLE does that.
- PROMETHEUS is deterministic: same PKP + same provider versions → same output.

### ATLAS — Persistent Knowledge, Characters, Assets, Styles, Continuity, Registries

**Current state:** Does not exist. State is in-memory; output is on local filesystem.
**Target state:** The persistence layer that spans all pillars. Holds the asset store, knowledge graph persistence, model registry, and content library.

**Responsibilities:**
- Asset Store: images, clips, audio files, final videos — each with provenance metadata.
- Knowledge Persistence: the PKG survives across sessions. Persisted to disk (SQLite/DuckDB) with full revision history.
- Model Registry: tracks which models produced which assets. Enables reproducibility.
- Content Library: reusable character hero images, location references, style presets, music beds, voice profiles — reusable across productions.
- Session Memory: the `.project-ai/` operational memory, elevated from convention to managed service.

**Boundaries:**
- ATLAS is orthogonal to the layered stack. It is called by all pillars to store and retrieve.
- ATLAS makes no creative decisions.
- ATLAS does not render or validate.
- ATLAS is the only system that writes to persistent storage on behalf of the engine.

### ORACLE — Validation, Quality, Evaluation, Knowledge Graph Intelligence, Drift Detection

**Current state:** Does not exist as a unified system. Proto-components: 7 evaluation agents in `movie_os/agents/evaluation/`, CLIP-based `image_verifier.py`, Genesis2 `ValidationPhase` + `CreativeCritiquePhase`.
**Target state:** The validation intelligence that compares produced media against the PKP and produces quality reports.

**Responsibilities:**
- Structural Validation: does the media match the PKP structurally (right scene count, right durations, all characters present)?
- Visual Consistency: does the character look the same across scenes? CLIP-based verification extended to full production.
- Emotional Arc Adherence: does the rendered video's emotional trajectory match the PKP's emotional arc specification?
- Continuity Enforcement: props, wardrobe, blocking, lighting continuity across scenes.
- Drift Detection: did PROMETHEUS make any creative decisions not authorized by the PKP?
- Quality Scoring: aggregate score across visual quality, audio quality, narrative coherence, emotional impact, technical correctness.
- Validation Report: written into the PKG as validation provenance. Feeds back into GENESIS for revision if needed.

**Boundaries:**
- ORACLE does not override human intent. It reports.
- ORACLE does not render. It validates.
- ORACLE reads the PKP (creative intent) and PROMETHEUS output (media) and writes validation results into the PKG.
- ORACLE's report is advisory. The human decides whether to accept, revise, or re-render.

---

## 2.2 Pillar Boundary Contracts

Each pillar has a formal input/output contract. Violations of these contracts are architectural bugs.

| Pillar | Input | Output | Writes To | Reads From | Prohibited Actions |
|--------|-------|--------|-----------|------------|---------------------|
| GENESIS | Human creative intent (synopsis, idea, screenplay) + production profile | Production Knowledge Package (PKP) — frozen, versioned, hashed | PKG (knowledge graph), ATLAS (PKP persistence) | PKG (prior revisions), ATLAS (content library for reuse), capability registry (provider availability) | Render media. Validate media. Modify PKP after gate. Call PROMETHEUS or ORACLE. |
| PROMETHEUS | Production Knowledge Package (PKP) — specific version | Rendered media (images, clips, audio, final video) + asset references | ATLAS (asset store + provenance) | PKP (from ATLAS), capability registry (provider config), ATLAS (hero images, style presets) | Make creative decisions. Modify PKG. Call GENESIS. Call ORACLE. Validate its own output. |
| ATLAS | Store/retrieve/query requests from any pillar | Stored assets, persisted knowledge, registry entries, retrieval results | Persistent storage (disk, DB) | All pillars (on request) | Make creative decisions. Render media. Validate media. Call any pillar. |
| ORACLE | PKP (creative intent) + PROMETHEUS output (media) | Validation report (structural, visual, emotional, continuity, drift, quality score) | PKG (validation provenance) | PKP (from ATLAS), PROMETHEUS output (from ATLAS), PKG (prior validation results) | Render media. Make creative decisions. Override human judgment. Call GENESIS or PROMETHEUS. |

---

## 2.3 Cross-Pillar Communication

The four pillars communicate exclusively through the knowledge graph and the asset store. There are no direct function calls between pillars.

```
    Human Intent
         │
         ▼
    ┌──────────┐                    ┌──────────────┐
    │  GENESIS  │── writes PKP ───►│   ATLAS      │
    │  (compile)│                    │  (persist)   │
    └──────────┘                    └──────┬───────┘
         ▲                                  │
         │ reads (for revision)             │ reads PKP
         │                                  ▼
    ┌──────────┐                    ┌──────────────┐
    │  ORACLE   │◄── reads media ──│ PROMETHEUS    │
    │ (validate)│    + PKP          │ (render)      │
    └────┬─────┘                    └──────┬───────┘
         │                                  │
         │ writes validation                 │ writes assets
         │ provenance to PKG                 │ + provenance to ATLAS
         │                                  │
         └──────────┬───────────────────────┘
                    │
                    ▼
              ┌──────────┐
              │  ATLAS   │
              │ (persist)│
              └──────────┘
```

**Communication invariants:**

1. GENESIS writes the PKP. PROMETHEUS reads it. They never communicate directly.
2. PROMETHEUS writes assets. ORACLE reads them. They never communicate directly.
3. ORACLE writes validation results. GENESIS reads them for revision. They never communicate directly.
4. ATLAS mediates all persistence. It is the only system that touches durable storage.
5. The human can intervene at any boundary: amend the PKP (re-enter GENESIS), re-render (re-enter PROMETHEUS), override ORACLE's report, or query ATLAS.

---

## 2.4 Subsystem Classification

Every existing subsystem, file, and component is classified into one of seven categories: KEEP, EXPAND, MERGE, SPLIT, RENAME, DEPRECATE, REPLACE.

### GENESIS Subsystems

| Subsystem | Location | Classification | Rationale |
|----------|----------|---------------|-----------|
| Constitutional Charter (GFS-000) | `constitutions/00-ConstitutionCharter.md` | KEEP | Supreme authority. Immutable. |
| Identity Constitution (GFS-001) | `constitutions/01-identity-constitution.md` | EXPAND | Expand scope from "pre-production only" to "creative decision authority." The identity evolves from "Pre-Production Intelligence System" to "AI Film Director + Production Compiler." |
| Reasoning Constitution (GFS-002) | `constitutions/002 — Reasoning Constitution.md` | KEEP | Reasoning model is universal. Applies to all pillars. |
| Knowledge Constitution (GFS-003) | `constitutions/003 – Knowledge Constitution.md` | EXPAND | Expand from pre-production knowledge to full-lifecycle knowledge (including media provenance and validation results). |
| Discovery Constitution (GFS-004) | `constitutions/004 Discovery Constitution.md` | KEEP | Discovery before decision is universal. |
| Agent Constitution (GFS-005) | `constitutions/005 – Agent Constitution.md` | EXPAND | Expand to govern PROMETHEUS, ATLAS, and ORACLE agents, not just GENESIS agents. |
| Validation Constitution (GFS-006) | `constitutions/006 – Validation Constitution.md` | EXPAND | Expand from pre-production validation to include media validation (ORACLE's domain). |
| Governance Constitution (GFS-007) | `constitutions/007 – Governance Constitution.md` | KEEP | Governance model is universal. |
| Constitutional Meta-Model (GFS-008) | `constitutions/008 — Constitutional Meta-Model.md` | KEEP | Universal conceptual model. |
| Constitutional Ontology Framework (GFS-009) | `constitutions/009 — Constitutional Ontology Framework.md` | KEEP | Ontology governance is universal. |
| Genesis Engine (4-stage) | `movie_os/genesis/engine.py` | MERGE | Merge with Genesis2 into unified GENESIS with two modes. The 4-stage engine becomes Deep Mode. |
| Genesis2 Engine (12-phase) | `movie_os/genesis2/engine.py` | MERGE | Merge with Genesis into unified GENESIS. The 12-phase pipeline becomes Deep Mode's internal structure. |
| Backend pipeline (6-stage) | `backend/app/services/pipeline_service.py` | MERGE | Becomes Fast Mode of the unified GENESIS. |
| Genesis Discovery agents (7) | `movie_os/genesis/discovery/` | KEEP | Discovery agents are the entry point for both modes. |
| Genesis PKP agents (19) | `movie_os/genesis/pkp_agents/` | KEEP | 19 PKP agents produce the 19 PKP specifications. These are the deep mode implementations. |
| Genesis2 phases (12) | `movie_os/genesis2/phases/` | MERGE | Each phase maps to a compiler pass. The phase implementations become the deep-mode compiler pass implementations. |
| Genesis Reviewers (4 + ChiefArchitect) | `movie_os/genesis/reviewers/` | KEEP | Review is a universal step. Extend to review PROMETHEUS output (as ORACLE). |
| Completion Gate (8 criteria) | `movie_os/genesis/completion_gate.py` | EXPAND | Extend to validate the expanded PKP schema. Existing 8 criteria preserved as the pre-production subset. |
| Master Prompt | `movie_os/genesis/master_prompt.py` | KEEP | 6 rules + confidence levels are universal. |
| Genesis Ontology (GO-001..119) | `docs/genesis/ontology/` | KEEP | All 28 ontology files preserved. |
| Ontology Compiler | `docs/genesis/07_Compiler.md` | EXPAND | Expand from ontology-only compilation to include creative pipeline compilation (the compiler passes in §4). |
| Genesis Workflows (GWS-001..013) | `docs/genesis/workflows/` | KEEP | 8 workflows preserved. Extend with PROMETHEUS execution workflow and ORACLE validation workflow. |
| Genesis ADRs (ADR-001..004) | `docs/genesis/decisions/` | KEEP | 4 ADRs preserved. Each migration step generates new ADRs. |
| Genesis schemas | `docs/genesis/schemas/` | KEEP | JSON Schema, YAML Schema, SHACL, RDF, OWL, Protobuf, GraphQL, OpenAPI — all preserved as schema projections. |
| Genesis agent specs | `docs/genesis/agents/` | KEEP | Agent specifications (architects, engineers, governance, learning, orchestrators, publishers, researchers, reviewers, shared, validators) — preserved. Reclassified into pillars. |
| Production profiles | `config/production_profiles.yaml` | KEEP | Already shared. Becomes the input to all compiler passes. |
| Profile service | `backend/app/services/profile_service.py` | KEEP | Already correct. |
| Profile API | `backend/app/api/v1/profiles.py` | KEEP | |
| Backend Genesis agents (4) | `backend/app/services/genesis/` | MERGE | Storyteller → Story Compiler (fast mode). PromptEngineer → Prompt Compiler (fast mode). AudioDirector → Audio/Music Compiler (fast mode). ManifestGenerator → Timeline Compiler (fast mode). |
| Prompt templates | `config/prompts.py` | KEEP | Templates are the fast-mode prompt implementations. Deep mode has richer prompts in the PKP agents. |

### PROMETHEUS Subsystems (Currently Scattered)

| Subsystem | Location | Classification | Rationale |
|----------|----------|---------------|-----------|
| Image Generation Service | `backend/app/services/image_service.py` | RENAME + MERGE | Rename to `prometheus/image_realization.py`. Merge with Movie OS image agents. |
| Video Generation Service | `backend/app/services/video_service.py` | RENAME + MERGE | Rename to `prometheus/video_realization.py`. Merge with Movie OS video agents. |
| TTS Service | `backend/app/services/tts_service.py` | RENAME + MERGE | Rename to `prometheus/voice_realization.py`. Merge with Movie OS voice agents. |
| Image Verifier (CLIP) | `backend/app/services/image_verifier.py` | SPLIT | The CLIP verification logic moves to ORACLE (Visual Consistency). The image generation logic stays in PROMETHEUS. |
| Cinematic Prompt Builder | `backend/app/services/cinematic_prompts.py` | RENAME | Rename to `prometheus/prompt_adapter.py`. This translates PKP creative prompts into provider-specific prompts. |
| Movie OS image agents (2) | `movie_os/agents/creative/image_generator_agent.py`, `movie_os/agents/generation/image_generator_agent.py` | MERGE | Merge into single PROMETHEUS Image Realization component. Remove duplicate. |
| Movie OS video agents (2) | `movie_os/agents/creative/video_composer_agent.py`, `movie_os/agents/post_production/video_composer_agent.py` | MERGE | Merge into single PROMETHEUS Video Realization component. Remove duplicate. |
| Movie OS voice agents (2) | `movie_os/agents/creative/voice_generator_agent.py`, `movie_os/agents/generation/voice_generator_agent.py` | MERGE | Merge into single PROMETHEUS Voice Realization component. Remove duplicate. |
| Movie OS music agents (3 + 1) | `movie_os/agents/creative/music_generator_agent.py`, `movie_os/agents/generation/music_generator_agent.py`, `movie_os/agents/music_agent.py`, `movie_os/agents/planning/music_composer_agent.py` | SPLIT + MERGE | Planning agent → GENESIS Music Compiler. Generation agents → PROMETHEUS Music Realization. Remove duplicates. |
| Movie OS audio mixer agents (2) | `movie_os/agents/creative/audio_mixer_agent.py`, `movie_os/agents/post_production/audio_mixing_agent.py` | MERGE | Merge into single PROMETHEUS Audio Assembly component. |
| Movie OS subtitle agent | `movie_os/agents/post_production/subtitle_agent.py` | RENAME | Rename to `prometheus/subtitle_realization.py`. |
| Movie OS SFX agent | `movie_os/agents/sfx_agent.py` | RENAME | Rename to `prometheus/sfx_realization.py`. |
| Movie OS pipeline steps | `config/movie_os.yaml: pipeline.steps` | KEEP | The 7-step rendering pipeline (narrative, images, audio, music, sfx, mix, video) becomes PROMETHEUS's execution plan template. |
| Movie OS provider config | `config/movie_os.yaml: providers` | KEEP | Provider definitions move behind the capability registry. The config file remains as provider configuration. |
| Movie OS rendering config | `config/movie_os.yaml: rendering` | KEEP | Rendering parameters (16:9, 1280x720, 24fps, libx264, aac) become PROMETHEUS defaults. |

### ATLAS Subsystems (Currently Minimal)

| Subsystem | Location | Classification | Rationale |
|----------|----------|---------------|-----------|
| In-memory pipeline state | `pipeline_service.py: _pipelines` | REPLACE | Replace with ATLAS-managed persistence (SQLite/DuckDB). |
| In-memory generation state | `video_service.py: _generation_states` | REPLACE | Replace with ATLAS-managed persistence. |
| In-memory image state | `image_service.py: _image_states` | REPLACE | Replace with ATLAS-managed persistence. |
| Output directory | `output/` | KEEP + EXPAND | Expand from ad-hoc output to structured asset store with provenance metadata. |
| `.project-ai/` operational memory | `.project-ai/` | KEEP + EXPAND | Elevate from convention to ATLAS-managed service. |
| PKG (in-memory) | `movie_os/genesis/pkg.py` | EXPAND | Expand from in-memory to ATLAS-persisted. The PKG class remains; persistence is added. |

### ORACLE Subsystems (Currently Fragmented)

| Subsystem | Location | Classification | Rationale |
|----------|----------|---------------|-----------|
| YAML Validator | `pipeline/orchestrator.py: YAMLValidator` | RENAME | Becomes ORACLE Structural Validation (pre-production subset). |
| Metrics Collector | `pipeline/orchestrator.py: MetricsCollector` | RENAME | Becomes ORACLE Quality Scoring (pre-production subset). |
| Image Verifier (CLIP) | `backend/app/services/image_verifier.py` | RENAME | Becomes ORACLE Visual Consistency. |
| Evaluation agents (7) | `movie_os/agents/evaluation/` | MERGE | All 7 merge into ORACLE. AudioMixAgent → ORACLE Audio Quality. CharacterConsistencyAgent → ORACLE Visual Consistency. DialogueQualityAgent → ORACLE Dialogue Quality. EmotionScoreAgent → ORACLE Emotional Arc Adherence. StoryQualityAgent → ORACLE Narrative Coherence. VisualConsistencyAgent → ORACLE Visual Consistency. YouTubeReadinessAgent → ORACLE Platform Readiness. |
| Genesis2 Validation Phase | `movie_os/genesis2/phases/phase10_validation.py` | RENAME | Becomes ORACLE Pre-Production Validation. |
| Genesis2 Creative Critique Phase | `movie_os/genesis2/phases/phase11_creative_critique.py` | RENAME | Becomes ORACLE Creative Critique. |
| Genesis Reviewers (4) | `movie_os/genesis/reviewers/` | KEEP | Remain as GENESIS internal review. ORACLE is the external validator. |
| Genesis Completion Gate | `movie_os/genesis/completion_gate.py` | KEEP | Remains as GENESIS internal gate. ORACLE validates post-production. |
| QAAgent | `movie_os/agents/qa_agent.py` | MERGE | Merges into ORACLE as the top-level validation orchestrator. |

### Cross-Cutting Subsystems

| Subsystem | Location | Classification | Rationale |
|----------|----------|---------------|-----------|
| Root AGENTS.md | `AGENTS.md` | KEEP | OpenCode skills/orchestration/memory conventions. Governs engineering work. |
| Genesis AGENTS.md | `docs/genesis/AGENTS.md` | KEEP | Genesis docs repository conventions. Governs specification authoring. |
| AIOS AGENTS.md | `.aios/AGENTS.md` | KEEP + SCOPE | Cognitive backbone. Scope explicitly as runtime cognitive orchestration layer. Add cross-references to root AGENTS.md and Genesis AGENTS.md. |
| Skills system (43 skills) | `skills/` | KEEP | Engineering skills for coding agents. Orthogonal to the four pillars. |
| Domain models | `config/models.py` | KEEP | Python domain model. Becomes Layer 1 of the architecture. |
| Backend schemas | `backend/app/models/schemas.py` | KEEP | Pydantic API schemas. These are API-layer projections of the domain model. |
| Frontend types | `frontend/src/lib/types.ts` | KEEP | TypeScript types. These are frontend projections of the domain model. Long-term: generated by the ontology compiler. |
| `.ai/` architecture files | `.ai/*.yaml` | KEEP | Machine-readable architecture state. Preserved. |
| `.aios/` cognitive layer | `.aios/` | KEEP + SCOPE | Scoped as runtime cognitive orchestration. Not a pillar; a cross-cutting concern. |
| Frontend (Next.js) | `frontend/` | EXPAND | Expand from 7 tabs to pillar-aware UI. Merge genesis + genesis2 tabs. Add PROMETHEUS status and ORACLE report views. |
| FastAPI backend | `backend/app/` | EXPAND | Expand from pipeline-only API to four-pillar API surface. |
| Pipeline orchestrator | `pipeline/orchestrator.py` | SPLIT | Split into: GENESIS compiler passes (Story, Scene, Dialogue, Prompt) and ORACLE validators (YAMLValidator, MetricsCollector). |
| Research stage | `pipeline/research.py` | KEEP | Research remains a GENESIS Discovery function. |
| Output saver | `pipeline/output_saver.py` | RENAME | Becomes ATLAS asset writer. |
| Scene file writer | `pipeline/scene_file_writer.py` | RENAME | Becomes ATLAS PKP serializer. |

---

# PART 3: GENESIS EVOLUTION

---

## 3.1 Redefinition: From Pre-Production System to AI Film Director

### Current Definition

GENESIS is defined in GFS-001 as the "Pre-Production Intelligence System of Movie OS." Its boundary is explicitly stated: "Genesis ends at the conclusion of pre-production. Genesis produces no media. Genesis owns knowledge, not pixels."

This definition is correct in its constraints (no media, knowledge only) but insufficient in its scope. It frames GENESIS as a phase-gate ("pre-production") rather than as a role ("the director who makes every creative decision").

### Target Definition

**GENESIS is the AI Film Director and Production Compiler.**

It is the creative intelligence that makes every directorial decision — narrative, visual, audio, performance, pacing — and compiles those decisions into a Production Knowledge Package that PROMETHEUS can execute without further creative input.

GENESIS is not "pre-production" as a phase. It is "creative decision authority" as a role. The distinction matters:

- **Phase framing** implies GENESIS stops at an arbitrary calendar point ("when pre-production ends").
- **Role framing** implies GENESIS stops when every creative decision is made, regardless of what calendar phase that occurs in.

The phase framing is preserved as a default workflow (pre-production → production → post-production), but the role framing governs the boundary: GENESIS's job is done when the PKP is complete, validated, and frozen. That may happen during "pre-production," or it may require revision after ORACLE reports issues with the rendered media.

### Architectural Implications of the Redefinition

| Implication | Detail |
|-------------|--------|
| **GENESIS may be re-entered.** When ORACLE reports drift or quality issues, the human amends the PKP and re-enters GENESIS for the affected compiler passes only. GENESIS is not "done" until the human accepts the final output. | This is already partially supported by the Genesis2 revision workflow (`workflows/validation/004 — Revision-Only Workflow.md`). The migration formalizes it as the standard revision loop. |
| **The AI Film Director is distributed.** No single agent is "the director." The directorial function is distributed across compiler passes: the Story Compiler decides narrative structure, the Director Compiler decides visual language, the Dialogue Compiler decides performance, the Music Compiler decides sonic identity. | This is already how the 19 PKP agents work (DirectorialAgent, ProductionDesignAgent, AudioIntentAgent, EditingLanguageAgent, AnimationIntentAgent). The migration formalizes them as compiler passes. |
| **The Production Compiler is deterministic.** Given the same input (synopsis + profile + provider versions), the compiler produces the same PKP. Creative decisions are not re-rolled on recompilation; they are frozen in the PKP. | This requires seed-based reproducibility for all LLM calls. Already partially implemented (image seeds). Must be extended to all LLM calls in the compiler. |
| **The boundary with PROMETHEUS is the PKP, not a phase.** GENESIS writes the PKP; PROMETHEUS reads it. The boundary is the artifact, not the calendar. | This is already the architectural intent (Studio Handoff Specification, `architecture/007`). The migration makes it the architectural law. |

---

## 3.2 Specification Preservation Analysis

Which existing Genesis specifications remain valid without modification.

| Specification | Location | Verdict | Reasoning |
|-------------|----------|---------|-----------|
| GFS-000 Constitutional Charter | `constitutions/00-ConstitutionCharter.md` | **VALID** | Supreme authority. The charter's invariants (Genesis produces no media, PKG is canonical, provenance is mandatory) are preserved. |
| GFS-002 Reasoning Constitution | `constitutions/002 — Reasoning Constitution.md` | **VALID** | The reasoning model (discover, analyze, infer, validate, question, decide, formalize) is universal. No change needed. |
| GFS-004 Discovery Constitution | `constitutions/004 Discovery Constitution.md` | **VALID** | Discovery before decision. Universal. |
| GFS-007 Governance Constitution | `constitutions/007 – Governance Constitution.md` | **VALID** | Governance model. Universal. |
| GFS-008 Constitutional Meta-Model | `constitutions/008 — Constitutional Meta-Model.md` | **VALID** | Universal conceptual model. |
| GFS-009 Constitutional Ontology Framework | `constitutions/009 — Constitutional Ontology Framework.md` | **VALID** | Ontology governance. Universal. |
| ADR-001 (Genesis is Pre-Production Only) | `decisions/001 — ADR-001 Why Genesis is Pre-Production Only.md` | **VALID with annotation** | The decision's constraints (no media, knowledge only) remain valid. The framing ("pre-production only") is superseded by "creative decision authority." Add an annotation, not a revocation. |
| ADR-002 (Knowledge Graph Not Relational) | `decisions/002 — ADR-002 Why Knowledge Graph Not Relational.md` | **VALID** | The PKG remains a graph. |
| ADR-003 (Constitutional Hierarchy) | `decisions/003 — ADR-003 Why Constitutional Hierarchy.md` | **VALID** | Hierarchy preserved. |
| ADR-004 (Five Confidence Levels) | `decisions/004 — ADR-004 Why Five Confidence Levels.md` | **VALID** | Confidence taxonomy preserved. |
| GO-001..GO-119 (all 28 ontologies) | `docs/genesis/ontology/` | **VALID** | All ontologies preserved. The ontology hierarchy is the deepest existing architectural asset. |
| GO-200 (Generated Ontology Registry) | `ontology/generated/001 — Generated Ontology Registry.md` | **VALID** | Registry preserved. |
| GO-201 (Psychological Cinema Ontology) | `ontology/generated/201 — Psychological Cinema Ontology.md` | **VALID** | Preserved. |
| GO-301 (Production Ontology) | `ontology/generated/301 — Production Ontology.md` | **VALID** | Preserved. |
| PKP-00..PKP-18 (all 19 specifications) | `specifications/pkp/` | **VALID** | All 19 PKP specifications remain the output of the 19 PKP agents. The compiler passes produce these specifications. |
| GWS-001 (Full Production Workflow) | `workflows/authoring/001` | **VALID** | Baseline workflow. Extended, not replaced. |
| GWS-002 (Scene-Only Workflow) | `workflows/generation/002` | **VALID** | Scene-level iteration. Preserved. |
| GWS-003 (Evaluation-Only Workflow) | `workflows/review/003` | **VALID** | Becomes ORACLE's evaluation workflow. |
| GWS-004 (Revision-Only Workflow) | `workflows/validation/004` | **VALID** | Becomes the standard revision loop. |
| GWS-010 (Publication Workflow) | `workflows/publication/001` | **VALID** | PKP packaging and distribution. Preserved. |
| GWS-011 (Deployment Workflow) | `workflows/deployment/001` | **VALID** | Engine deployment. Preserved. |
| GWS-012 (Governance Workflow) | `workflows/governance/001` | **VALID** | Governance. Preserved. |
| GWS-013 (Learning Workflow) | `workflows/learning/001` | **VALID** | Learning. Preserved. |
| Studio Handoff Specification | `architecture/007 — Studio Handoff Specification.md` | **VALID** | The GENESIS→PROMETHEUS handoff. Preserved. The "Studio Engine" becomes "PROMETHEUS." |
| Production Knowledge Package Specification | `architecture/008 — Production Knowledge Package Specification.md` | **VALID** | PKP definition. Preserved and expanded (§5). |
| Core Ontology Specification | `architecture/009 — Core Ontology Specification.md` | **VALID** | Core ontology. Preserved. |
| Agent Communication Protocol | `specifications/agents/011` | **VALID** | Agent communication. Preserved. |
| Ontology Compiler Specification | `specifications/compiler/001` | **VALID** | Ontology compiler. Preserved. Extended by the creative compiler (§4). |
| All schema files | `docs/genesis/schemas/` | **VALID** | JSON Schema, YAML Schema, SHACL, RDF, OWL, Protobuf, GraphQL, OpenAPI. All preserved as schema projections. |
| All pattern files | `docs/genesis/patterns/` | **VALID** | Architecture, design, governance, ontology, reasoning, validation, workflow patterns. All preserved. |
| All template files | `docs/genesis/templates/` | **VALID** | Agent, architecture, ADR, documentation, ontology, prompt, schema, specification, workflow templates. All preserved. |
| All validation files | `docs/genesis/validation/` | **VALID** | PKG Validator, Ontology Validator, Quality Gates. Preserved. Extended by ORACLE. |

---

## 3.3 Specification Expansion Analysis

Which existing Genesis specifications need expansion and what the expansion entails.

| Specification | Location | Expansion Required | Detail |
|-------------|----------|-------------------|--------|
| GFS-001 Identity Constitution | `constitutions/01-identity-constitution.md` | **EXPAND scope** | Add: "GENESIS is the AI Film Director and Production Compiler. Its identity is creative decision authority, not a calendar phase. It may be re-entered for revision when ORACLE reports issues." The existing invariants (medium-agnostic, provider-agnostic, implementation-agnostic, no media) remain. |
| GFS-003 Knowledge Constitution | `constitutions/003 – Knowledge Constitution.md` | **EXPAND scope** | Add: "The PKG stores full-lifecycle knowledge, including media provenance (written by PROMETHEUS), validation results (written by ORACLE), and asset references (written by ATLAS). The PKG is the communication bus for all four pillars." |
| GFS-005 Agent Constitution | `constitutions/005 – Agent Constitution.md` | **EXPAND scope** | Add: "This constitution governs agents in all four pillars: GENESIS (creative), PROMETHEUS (rendering), ATLAS (persistence), ORACLE (validation). Each pillar may define pillar-specific agent sub-constitutions, but all inherit this base." |
| GFS-006 Validation Constitution | `constitutions/006 – Validation Constitution.md` | **EXPAND scope** | Add: "Validation applies to both pre-production knowledge (GENESIS output) and produced media (PROMETHEUS output). ORACLE is the validation pillar. Pre-production validation is a subset of ORACLE's scope." |
| Ontology Compiler Specification | `specifications/compiler/001` | **EXPAND scope** | Add the creative compiler pipeline (§4) as a parallel compilation concern. The ontology compiler compiles ontologies; the creative compiler compiles stories. Both are "compilers" in the constitutional sense. |
| PKP-18 Knowledge Graph Specification | `specifications/pkp/18` | **EXPAND scope** | Add media nodes, validation nodes, and asset nodes to the PKG schema. The graph currently stores only pre-production knowledge; it must store full-lifecycle knowledge. |
| Completion Gate | `movie_os/genesis/completion_gate.py` | **EXPAND scope** | Add criteria for the expanded PKP (§5). The existing 8 criteria are the pre-production subset. New criteria: media rendering plan derived, asset requirements enumerated, provider assignments validated. |
| Studio Handoff Specification | `architecture/007` | **EXPAND scope** | Rename "Studio Engine" to "PROMETHEUS." Add: "PROMETHEUS reads the PKP and executes it deterministically. The handoff is the PKP artifact, not a calendar event." |
| Production Knowledge Package Specification | `architecture/008` | **EXPAND scope** | Add the canonical PKP schema (§5) with all artifacts, identifiers, lifecycle, and regeneration rules. |
| Genesis Agent Catalog | `architecture/005` | **EXPAND scope** | Add PROMETHEUS, ATLAS, and ORACLE agents to the catalog. Currently only lists Genesis agents. |
| Genesis Orchestration Specification | `architecture/006` | **EXPAND scope** | Add PROMETHEUS execution orchestration and ORACLE validation orchestration. |

---

## 3.4 Specification Obsolescence Analysis

Which existing specifications become obsolete or are superseded. (Very few — the existing architecture is strong.)

| Specification | Location | Verdict | Reasoning | Replacement |
|-------------|----------|---------|-----------|-------------|
| `.ai/identity.yaml` (name: "Movie OS") | `.ai/identity.yaml` | **SUPERSEDED** | The platform name changes from "Movie OS" to "Cinema Production Engine." | Update identity.yaml: `name: "Cinema Production Engine"`, `legacy_name: "Movie OS"`. |
| `SPEC.md` (Text Cinema Engine) | `SPEC.md` | **SUPERSEDED** | The spec name is outdated. The content is partially valid (pipeline description, tech stack) but the framing is wrong. | Replace with a Cinema Production Engine overview that references the Constitutional Architecture and this document. |
| `README.md` (AI Studio boilerplate) | `README.md` | **SUPERSEDED** | Boilerplate. | Replace with Cinema Production Engine README. |
| `ARCHITECTURE.md` (3-line stub) | `ARCHITECTURE.md` | **SUPERSEDED** | Stub. | Replace with pointer to §00 and this document. |
| `ROADMAP.md` (3-line stub) | `ROADMAP.md` | **SUPERSEDED** | Stub pointing to `.ai/roadmap.yaml`. | Replace with §7 of this document. |
| `DECISIONS.md` (3-line stub) | `DECISIONS.md` | **SUPERSEDED** | Stub. | Replace with pointer to `docs/genesis/decisions/` ADR registry. |
| `config/models.py` duplicate `producer_brief` | `config/models.py:42-43` | **OBSOLETE** | Duplicate field. | Remove duplicate line. |
| Movie OS legacy top-level agents | `movie_os/agents/story_agent.py`, `visual_agent.py`, `voice_agent.py`, `music_agent.py`, `sfx_agent.py`, `qa_agent.py`, `publishing_agent.py`, `movie_agent.py` | **DEPRECATED** | These are superseded by the subpackaged agents (`creative/`, `generation/`, `evaluation/`, `planning/`, `orchestration/`, `post_production/`) which are themselves being merged into pillars. | The functionality moves to pillars. The files are deprecated after the migration is complete. |

---

## 3.5 Constitutional Amendments Required

The constitutional layer (GFS-000..009) is preserved. No core constitution is amended. However, the constitutional layer is **extended** with new derived standards (GFS-010+) issued under the governance framework (GFS-007). See §6 for the full new constitution inventory.

---

# PART 4: COMPILER ARCHITECTURE

---

## 4.1 The Canonical Compiler Pipeline

GENESIS 2.0 formalizes the "Production Compiler" — a deterministic pipeline of compiler passes that transforms a synopsis into a Production Knowledge Package. Each pass has defined inputs, outputs, dependencies, and validation.

The compiler is the architectural realization of the "compilation over generation" philosophy from the Constitutional Architecture.

```
Synopsis (human creative intent)
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  PRE-COMPILATION                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ Profile       │  │ Discovery    │  │ Scene Class          │   │
│  │ Loader        │  │ (7 agents)   │  │ Planner              │   │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘   │
│         │                  │                      │              │
│         └──────────────────┴──────────────────────┘             │
│                            │                                    │
└────────────────────────────┼────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  COMPILER PASSES (in dependency order)                           │
│                                                                  │
│  01. Story Compiler                                              │
│      │                                                           │
│      ▼                                                           │
│  02. Narrative Compiler                                          │
│      │                                                           │
│      ▼                                                           │
│  03. Screenplay Compiler                                         │
│      │                                                           │
│      ▼                                                           │
│  04. Director Compiler                                           │
│      │                                                           │
│      ▼                                                           │
│  05. Scene Compiler                                              │
│      │                                                           │
│      ▼                                                           │
│  06. Shot Compiler                                              │
│      │                                                           │
│      ▼                                                           │
│  07. Dialogue Compiler                                           │
│      │                                                           │
│      ▼                                                           │
│  08. Emotion Compiler                                            │
│      │                                                           │
│      ▼                                                           │
│  09. Character Compiler                                          │
│      │                                                           │
│      ▼                                                           │
│  10. Camera Compiler                                             │
│      │                                                           │
│      ▼                                                           │
│  11. Lighting Compiler                                           │
│      │                                                           │
│      ▼                                                           │
│  12. Music Compiler                                              │
│      │                                                           │
│      ▼                                                           │
│  13. Audio Compiler                                              │
│      │                                                           │
│      ▼                                                           │
│  14. Voice Compiler                                              │
│      │                                                           │
│      ▼                                                           │
│  15. Timeline Compiler                                          │
│      │                                                           │
│      ▼                                                           │
│  16. Prompt Compiler                                            │
│      │                                                           │
│      ▼                                                           │
│  17. Production Package Assembly                                 │
│      │                                                           │
│      ▼                                                           │
│  18. Validation Gate                                             │
│      │                                                           │
│      ▼                                                           │
│  19. Freeze + Hash                                               │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
                    Production Knowledge Package (PKP)
                    (frozen, versioned, hashed)
```

---

## 4.2 Compiler Pass Specifications

Each compiler pass is defined by: **Input** (what it consumes from prior passes), **Output** (what it produces), **Dependencies** (which passes must complete first), **Validation** (what is checked), **Fast Mode** (the backend pipeline equivalent), **Deep Mode** (the Genesis/Genesis2 equivalent), and **PKP Mapping** (which PKP specification it produces).

### Pass 01: Story Compiler

| Aspect | Detail |
|--------|--------|
| **Input** | Synopsis (human creative intent) + production profile (runtime target, scene count, scene class guidance) + discovery output (theme, emotion, conflict, audience, gaps) |
| **Output** | Story outline: title, premise, theme, dramatic question, logline, central conflict, symbolic structure, resolution posture, motifs, narrative (present-tense text), emotional arc (beginning/middle/end), story beats (with scene_class tags) |
| **Dependencies** | Pre-compilation (profile loader, discovery, scene class planner) |
| **Validation** | Title present, premise present, at least N beats (profile-derived), each beat has scene_class, emotional arc has beginning/middle/end |
| **Fast Mode** | Backend `StoryGenerator.generate()` — produces title, narrative, emotional_arc, beats. ~10 seconds. |
| **Deep Mode** | Genesis `StoryAgent` (PKP-04) + Genesis2 `StoryFoundationPhase` — produces full PKP-04 Story Specification. ~2 minutes. |
| **PKP Mapping** | PKP-04 (Story Specification) |

### Pass 02: Narrative Compiler

| Aspect | Detail |
|--------|--------|
| **Input** | Story outline (from Pass 01) |
| **Output** | Narrative structure: acts (with act objectives), sequences (with sequence objectives), emotional curve, conflict curve, character curve, reveal timeline, mystery timeline, foreshadowing plan, callbacks plan |
| **Dependencies** | Pass 01 (Story Compiler) |
| **Validation** | At least 3 acts, each act has objective, emotional curve covers all acts, conflict curve covers all acts |
| **Fast Mode** | Derived from story beats (no separate LLM call — acts are inferred from beat grouping) |
| **Deep Mode** | Genesis `NarrativeAgent` (PKP-09) + Genesis2 `NarrativeExpansionPhase` — full narrative structure |
| **PKP Mapping** | PKP-09 (Narrative Specification) |

### Pass 03: Screenplay Compiler

| Aspect | Detail |
|--------|--------|
| **Input** | Story outline + narrative structure |
| **Output** | Screenplay text: per-scene narration, scene transitions, scene objectives, dramatic questions per scene |
| **Dependencies** | Pass 01, Pass 02 |
| **Validation** | Every scene has narration, every scene has a transition, every scene has an objective |
| **Fast Mode** | Backend `SceneDecomposer.decompose()` — produces scenes with narration. |
| **Deep Mode** | Genesis2 `NarrativeExpansionPhase` — produces acts, sequences, scenes with objectives. |
| **PKP Mapping** | PKP-09 (Narrative Specification, screenplay subset) |

### Pass 04: Director Compiler

| Aspect | Detail |
|--------|--------|
| **Input** | Story outline + narrative structure + screenplay |
| **Output** | Directing intent: camera philosophy, composition principles, color language, blocking philosophy, performance style, lighting intent, visual metaphors, visual style guide |
| **Dependencies** | Pass 01, Pass 02, Pass 03 |
| **Validation** | Camera philosophy present, color language present, lighting intent present, visual style guide present |
| **Fast Mode** | Derived from production profile + tone (no separate LLM call — directorial defaults from profile) |
| **Deep Mode** | Genesis `DirectorialAgent` (PKP-10) + Genesis2 `VisualLanguagePhase` — full directorial language specification |
| **PKP Mapping** | PKP-10 (Directorial Language Specification) |

### Pass 05: Scene Compiler

| Aspect | Detail |
|--------|--------|
| **Input** | Screenplay + narrative structure + directing intent |
| **Output** | Scene specifications: per-scene goal, emotional goal, conflict, beginning/middle/ending, transition, visual progression, dialogue progression, music progression, lighting progression, camera progression, character movement, silence moments, reaction shots, close-ups, environmental details, narrative purpose, production complexity, scene_class, duration |
| **Dependencies** | Pass 01, 02, 03, 04 |
| **Validation** | Every scene has goal, emotional goal, conflict, duration, scene_class. Duration within profile policy. Scene count within profile policy. |
| **Fast Mode** | Backend `SceneDecomposer.decompose()` — produces scenes with narration, emotion, camera, lighting, visual_prompt, scene_class, duration. |
| **Deep Mode** | Genesis2 `ScenePlanningPhase` — full scene planning with purpose/conflict/emotion/goals/transition/duration/dependencies. |
| **PKP Mapping** | PKP-09 (Narrative Specification, scene subset) + PKP-15 (Production Blueprint, scene subset) |

### Pass 06: Shot Compiler

| Aspect | Detail |
|--------|--------|
| **Input** | Scene specifications + directing intent |
| **Output** | Shot specifications: per-shot framing, camera movement, lens, composition, blocking, depth, foreground, background, textures, atmosphere, visual metaphors |
| **Dependencies** | Pass 04, Pass 05 |
| **Validation** | Every scene has at least one shot. Every shot has framing and camera movement. |
| **Fast Mode** | Not executed (shots are implicit in the scene's camera field) |
| **Deep Mode** | Genesis `BlueprintAgent` (PKP-15) — full shot-level breakdown |
| **PKP Mapping** | PKP-15 (Production Blueprint, shot subset) |

### Pass 07: Dialogue Compiler

| Aspect | Detail |
|--------|--------|
| **Input** | Scene specifications + character specifications |
| **Output** | Dialogue plans: per-scene conversation intent, subtext, emotional state, silence opportunities, dialogue rhythm, speech patterns, voice direction, actual dialogue lines (character, dialogue, emotion, delivery) |
| **Dependencies** | Pass 05, Pass 09 (Character Compiler — may run in parallel) |
| **Validation** | Every dialogue scene has dialogue lines. Dialogue is spoken words, not visual descriptions (validated against the rule from `config/prompts.py` DIALOGUE_GENERATION_SYSTEM). Duration naturally 60-100 seconds per scene. |
| **Fast Mode** | Backend `DialogueGenerator.generate()` — produces per-scene dialogue lines. |
| **Deep Mode** | Genesis2 `DialoguePlanningPhase` — full dialogue planning with intent/subtext/silence/rhythm + dialogue lines. |
| **PKP Mapping** | PKP-12 (Audio Intent Specification, dialogue subset) |

### Pass 08: Emotion Compiler

| Aspect | Detail |
|--------|--------|
| **Input** | Scene specifications + narrative structure + character psychology |
| **Output** | Emotional specifications: per-scene dominant emotion, emotional transition within scene, audience emotional target, emotional intensity curve, emotional triggers per character |
| **Dependencies** | Pass 02, Pass 05, Pass 09 |
| **Validation** | Every scene has a dominant emotion. Emotional arc covers all scenes. |
| **Fast Mode** | Derived from scene's `emotion` field (no separate LLM call) |
| **Deep Mode** | Genesis `PsychologyAgent` (PKP-08) — full psychological depth including emotional triggers and behavioral patterns. |
| **PKP Mapping** | PKP-08 (Psychology Specification, emotion subset) |

### Pass 09: Character Compiler

| Aspect | Detail |
|--------|--------|
| **Input** | Story outline + narrative structure + discovery output |
| **Output** | Character specifications: per-character biography, psychology, motivations, fear, desires, secrets, strengths, weaknesses, speaking style, vocabulary, body language, facial expressions, emotional triggers, relationships, growth arc, wardrobe, visual identity, color identity, voice identity, camera preference, lighting preference, reference objects, consistency rules |
| **Dependencies** | Pass 01, Pass 02 |
| **Validation** | Every named character has biography, psychology, motivation, fear, speaking style, visual identity, voice identity. Relationship graph is complete (every character pair has a relationship entry). |
| **Fast Mode** | Not executed (characters are implicit in the story — no separate character generation in the backend pipeline) |
| **Deep Mode** | Genesis `CharacterAgent` (PKP-06) + `RelationshipAgent` (PKP-07) + `PsychologyAgent` (PKP-08) + Genesis2 `CharacterPsychologyPhase` — full character bible |
| **PKP Mapping** | PKP-06 (Character), PKP-07 (Relationship), PKP-08 (Psychology) |

### Pass 10: Camera Compiler

| Aspect | Detail |
|--------|--------|
| **Input** | Scene specifications + shot specifications + directing intent |
| **Output** | Camera specifications: per-scene camera language, lens, composition, movement, blocking, depth |
| **Dependencies** | Pass 04, Pass 05, Pass 06 |
| **Validation** | Every scene has camera language. Camera movement is valid (wide shot, close-up, tracking, dolly-in, pan, etc.). |
| **Fast Mode** | Derived from scene's `camera` field |
| **Deep Mode** | Genesis `DirectorialAgent` (PKP-10) — full camera language specification. Genesis2 `VisualLanguagePhase` — camera intent, lens suggestions, movement philosophy. |
| **PKP Mapping** | PKP-10 (Directorial Language, camera subset) |

### Pass 11: Lighting Compiler

| Aspect | Detail |
|--------|--------|
| **Input** | Scene specifications + directing intent + location specifications |
| **Output** | Lighting specifications: per-scene lighting style, color palette, mood, atmosphere, time of day, textures |
| **Dependencies** | Pass 04, Pass 05, Pass 09 (for location derivation) |
| **Validation** | Every scene has lighting style. Lighting is valid (natural, dramatic backlight, low-key, soft fill, neon, golden hour, etc.). |
| **Fast Mode** | Derived from scene's `lighting` field |
| **Deep Mode** | Genesis2 `VisualLanguagePhase` — color, lighting, composition, textures, atmosphere. |
| **PKP Mapping** | PKP-10 (Directorial Language, lighting subset) + PKP-11 (Production Design, lighting subset) |

### Pass 12: Music Compiler

| Aspect | Detail |
|--------|--------|
| **Input** | Scene specifications + emotional specifications + narrative structure |
| **Output** | Music direction: theme, instrumentation, tempo, intensity, transitions, silence, emotion per scene. Music cues per scene. |
| **Dependencies** | Pass 02, Pass 05, Pass 08 |
| **Validation** | Music direction present. At least one music cue per scene (including silence as a valid cue). |
| **Fast Mode** | Derived from production profile's `musicMood` (no separate LLM call) |
| **Deep Mode** | Genesis `AudioIntentAgent` (PKP-12) + Genesis2 `ProductionSpecificationsPhase` (music_specs subset) + Movie OS `MusicComposerAgent` (planning) |
| **PKP Mapping** | PKP-12 (Audio Intent, music subset) |

### Pass 13: Audio Compiler

| Aspect | Detail |
|--------|--------|
| **Input** | Scene specifications + music direction + dialogue plans |
| **Output** | Audio direction: per-scene SFX list, ambient soundscape, audio transitions, silence moments, sound design intent |
| **Dependencies** | Pass 05, Pass 07, Pass 12 |
| **Validation** | Every scene has a soundscape. Silence is explicitly specified, not assumed. |
| **Fast Mode** | Not executed (audio is implicit) |
| **Deep Mode** | Genesis `AudioIntentAgent` (PKP-12) — full sonic identity including SFX, silence, sound design. |
| **PKP Mapping** | PKP-12 (Audio Intent, SFX/soundscape subset) |

### Pass 14: Voice Compiler

| Aspect | Detail |
|--------|--------|
| **Input** | Character specifications + dialogue plans + scene specifications |
| **Output** | Voice direction: per-character tone, energy, pace, breathing, emotion, accent, age, delivery style. Per-scene voiceover script. |
| **Dependencies** | Pass 07, Pass 09 |
| **Validation** | Every speaking character has voice direction. Voiceover scripts match dialogue plans. |
| **Fast Mode** | Derived from production profile's `voiceOverStyle` (no separate LLM call) |
| **Deep Mode** | Genesis `AudioIntentAgent` (PKP-12, voice subset) + Genesis2 `DialoguePlanningPhase` (voice_direction subset) |
| **PKP Mapping** | PKP-12 (Audio Intent, voice subset) |

### Pass 15: Timeline Compiler

| Aspect | Detail |
|--------|--------|
| **Input** | All prior passes (scenes, shots, dialogue, music, audio, voice) |
| **Output** | Timeline: per-scene start time, end time, duration, transition duration, total runtime, scene ordering, parallel tracks (video, audio, music, SFX, subtitle) |
| **Dependencies** | Pass 05, 06, 07, 12, 13, 14 |
| **Validation** | Total runtime within profile policy (min/max minutes). Every scene has a duration. Durations sum to total runtime. Scene ordering is valid. |
| **Fast Mode** | Derived from scene durations (no separate LLM call) |
| **Deep Mode** | Genesis `BlueprintAgent` (PKP-15) — full production blueprint with timeline. Genesis2 `KnowledgeIntegrationPhase` — asset registry, dependencies, cross-references. |
| **PKP Mapping** | PKP-15 (Production Blueprint, timeline subset) + PKP-18 (Knowledge Graph, timeline nodes) |

### Pass 16: Prompt Compiler

| Aspect | Detail |
|--------|--------|
| **Input** | Scene specifications + shot specifications + camera + lighting + character visual identities + directing intent |
| **Output** | Per-scene cinematic prompts: medium-agnostic creative prompts (visual description suitable for any image/video provider). Per-scene negative prompts. Per-scene provider-specific prompt hints (FLUX, SD, SVD). |
| **Dependencies** | Pass 05, 06, 09, 10, 11 |
| **Validation** | Every scene has a cinematic prompt. Prompts are visual descriptions, not dialogue. Prompts include camera, lighting, and visual style. |
| **Fast Mode** | Backend `CinematicPromptGenerator.generate()` — produces per-scene cinematic prompts. |
| **Deep Mode** | Genesis `BlueprintAgent` (PKP-15, prompt subset) + backend `PromptEngineerAgent` (FLUX/ComfyUI translation) |
| **PKP Mapping** | PKP-15 (Production Blueprint, prompt subset) |

### Pass 17: Production Package Assembly

| Aspect | Detail |
|--------|--------|
| **Input** | All prior pass outputs |
| **Output** | Assembled PKP: all 19 PKP specifications (PKP-00..PKP-18), versioned, with cross-references and dependency graph |
| **Dependencies** | All passes 01-16 |
| **Validation** | All 19 PKP specifications present. Cross-references valid. Dependency graph complete. |
| **Fast Mode** | Assembles from the backend pipeline's output (story, scenes, dialogues, prompts, metrics). Fills missing PKP specs with defaults/assumed confidence. |
| **Deep Mode** | Genesis `KnowledgeGraphAgent` (PKP-18) + Genesis2 `KnowledgeIntegrationPhase` — full knowledge graph with nodes, edges, asset registry, dependencies, cross-references, version history. |
| **PKP Mapping** | PKP-18 (Knowledge Graph Specification) + all PKP-00..17 |

### Pass 18: Validation Gate

| Aspect | Detail |
|--------|--------|
| **Input** | Assembled PKP |
| **Output** | Gate decision: PASS or FAIL with findings |
| **Dependencies** | Pass 17 |
| **Validation** | The existing 8 completion gate criteria (all 19 specs exist, dependencies satisfied, cross-validation passed, no critical contradictions, confidence thresholds met, reviews completed, knowledge graph complete, blueprint derived). Extended with: media rendering plan derived, asset requirements enumerated, provider assignments validated, runtime within profile policy. |
| **Fast Mode** | Backend `YAMLValidator.validate()` + `MetricsCollector` — structural validation + metrics. |
| **Deep Mode** | Genesis `completion_gate.py` — full 8-criteria gate. Genesis2 `ValidationPhase` + `CreativeCritiquePhase`. |
| **PKP Mapping** | PKP-17 (Quality Specification) |

### Pass 19: Freeze + Hash

| Aspect | Detail |
|--------|--------|
| **Input** | Validated PKP |
| **Output** | Frozen PKP: immutable, versioned, content-hashed, persisted to ATLAS |
| **Dependencies** | Pass 18 (gate passed) |
| **Validation** | Content hash computed. Version number assigned. PKP is read-only after freeze. |
| **Fast Mode** | Not applicable (freezing is a constant-time operation) |
| **Deep Mode** | Not applicable |
| **PKP Mapping** | PKP-18 (Knowledge Graph, version history subset) |

---

## 4.3 Compiler Dependency Graph

```
                    ┌──────────────────────────┐
                    │  Pre-Compilation          │
                    │  (Profile, Discovery,     │
                    │   Scene Class Planner)    │
                    └────────────┬─────────────┘
                                 │
                    ┌────────────▼─────────────┐
                    │  01. Story Compiler        │
                    └────────────┬─────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
   ┌──────────▼───────┐  ┌──────▼───────┐  ┌──────▼──────────┐
   │ 02. Narrative    │  │ 09. Character│  │ 04. Director    │
   │     Compiler     │  │    Compiler  │  │    Compiler     │
   └──────────┬───────┘  └──────┬───────┘  └──────┬──────────┘
              │                  │                  │
              │                  │                  │
   ┌──────────▼───────┐  ┌──────▼───────┐  ┌──────▼──────────┐
   │ 03. Screenplay   │  │ 08. Emotion  │  │ 10. Camera     │
   │     Compiler     │  │    Compiler  │  │    Compiler    │
   └──────────┬───────┘  └──────┬───────┘  └──────┬──────────┘
              │                  │                  │
              │                  │                  │
   ┌──────────▼───────┐  ┌──────▼───────┐  ┌──────▼──────────┐
   │ 05. Scene         │  │ 07. Dialogue │  │ 11. Lighting   │
   │    Compiler      │  │    Compiler  │  │    Compiler    │
   └──────────┬───────┘  └──────┬───────┘  └──────┬──────────┘
              │                  │                  │
              │           ┌──────▼───────┐          │
              │           │ 14. Voice    │          │
              │           │    Compiler  │          │
              │           └──────┬───────┘          │
              │                  │                  │
              │           ┌──────▼───────┐          │
              │           │ 12. Music    │          │
              │           │    Compiler  │          │
              │           └──────┬───────┘          │
              │                  │                  │
              │           ┌──────▼───────┐          │
              │           │ 13. Audio    │          │
              │           │    Compiler  │          │
              │           └──────┬───────┘          │
              │                  │                  │
   ┌──────────▼───────┐          │          ┌──────▼──────────┐
   │ 06. Shot         │          │          │ 16. Prompt      │
   │    Compiler      │          │          │    Compiler      │
   └──────────┬───────┘          │          └──────┬──────────┘
              │                  │                  │
              └──────────────────┼──────────────────┘
                                 │
                    ┌────────────▼─────────────┐
                    │  15. Timeline Compiler   │
                    └────────────┬─────────────┘
                                 │
                    ┌────────────▼─────────────┐
                    │  17. Package Assembly     │
                    └────────────┬─────────────┘
                                 │
                    ┌────────────▼─────────────┐
                    │  18. Validation Gate       │
                    └────────────┬─────────────┘
                                 │
                    ┌────────────▼─────────────┐
                    │  19. Freeze + Hash         │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    Production Knowledge Package
```

**Parallelization opportunities:** Passes 02, 09, and 04 can run in parallel after Pass 01. Passes 05, 07, and 11 can run in parallel after their dependencies. Passes 06, 12, 13, 14, and 16 can run in parallel after their dependencies. Only Passes 15, 17, 18, 19 are strictly sequential.

---

## 4.4 Compiler Validation Model

Each pass has three validation tiers:

| Tier | When | What | Who |
|------|------|------|-----|
| **Structural** | After each pass | Field presence, type correctness, value constraints | The pass itself (inline validation) |
| **Cross-Pass** | After all passes | Cross-reference integrity, dependency graph completeness, timeline consistency | Pass 17 (Package Assembly) |
| **Gate** | After assembly | The 8+ completion gate criteria | Pass 18 (Validation Gate) |

If any tier fails, the compiler halts and reports. The human can:
1. Amend the input (re-enter the failing pass with corrected input).
2. Override the validation (with a recorded waiver in the PKG).
3. Abort the compilation.

---

# PART 5: PRODUCTION PACKAGE

---

## 5.1 Canonical Production Package Definition

The Production Knowledge Package (PKP) is the single output of GENESIS and the single input to PROMETHEUS. It is:

- **Complete:** Every creative decision is made. No ambiguity remains for PROMETHEUS.
- **Validated:** The validation gate (Pass 18) has certified it.
- **Frozen:** Immutable after Pass 19. Any amendment creates a new version.
- **Versioned:** Carries a semantic version number and a content hash.
- **Portable:** Serializable to JSON/YAML. Can be transmitted, stored, and recompiled on a different machine.
- **Executable:** PROMETHEUS can read it and produce media deterministically.

The PKP replaces all ad-hoc generated outputs (the backend pipeline's story/scenes/dialogues/prompts dicts, the Genesis engine's PKG dump, the Genesis2 phase JSON files). There is one PKP schema, produced by all compilation modes, consumed by PROMETHEUS.

---

## 5.2 Artifact Inventory

The PKP contains the following artifacts, each mapped to a PKP specification and a compiler pass:

| Artifact | PKP Spec | Compiler Pass | Owner | Description |
|---------|----------|---------------|-------|-------------|
| Vision | PKP-00 | Pre-compilation (Discovery) | GENESIS | Irreducible reason the production exists. Highest creative authority. |
| Creative Strategy | PKP-01 | Pre-compilation (Discovery) | GENESIS | Genre, emotional mechanics, narrative positioning, success metrics. |
| Project | PKP-02 | Pre-compilation (Profile) | GENESIS | Title, format, runtime, language, platform, audience, rating, scope. |
| Research | PKP-03 | Pre-compilation (Discovery) | GENESIS | Factual knowledge for credibility. Evidentiary foundation. |
| Story | PKP-04 | Pass 01 | GENESIS | Premise, theme, dramatic question, logline, conflict, symbolic structure, motifs. |
| World | PKP-05 | Pass 01 (derived) | GENESIS | Geography, timeline, locations, society, rules, technology, environment, culture. |
| Characters | PKP-06 | Pass 09 | GENESIS | Per-character: identity, biography, psychology, motivation, fear, goal, appearance, voice, arc. |
| Relationships | PKP-07 | Pass 09 | GENESIS | Interpersonal dynamics: trust, power, conflict, history, hidden motivation, dependency, evolution. |
| Psychology | PKP-08 | Pass 08 + Pass 09 | GENESIS | Attachment styles, defense mechanisms, trauma, cognitive biases, emotional triggers, behavioral patterns, transformation. |
| Narrative | PKP-09 | Pass 02 + Pass 03 | GENESIS | Acts, sequences, scenes, pacing, foreshadowing, callbacks, emotional rhythm, scene objectives. |
| Directorial Language | PKP-10 | Pass 04 + Pass 10 + Pass 11 | GENESIS | Camera philosophy, composition, color language, blocking, performance style, lighting intent, visual metaphors. |
| Production Design | PKP-11 | Pass 11 (derived) | GENESIS | Architecture, props, wardrobe, costumes, set dressing, vehicles, technology, materials. |
| Audio Intent | PKP-12 | Pass 12 + Pass 13 + Pass 14 | GENESIS | Voice style, narration philosophy, dialogue style, music intent, silence, sound design, emotional audio. |
| Editing Language | PKP-13 | Pass 15 (derived) | GENESIS | Rhythm, montage, transition rules, flashback policy, time compression, titles, credits. |
| Animation Intent | PKP-14 | Pass 06 (derived) | GENESIS | Motion principles, gesture style, facial performance, lip sync intent, physics, effects philosophy. |
| Production Blueprint | PKP-15 | Pass 06 + Pass 15 + Pass 16 | GENESIS | Shots, assets, characters, environments, camera, lighting, rendering, prompt requirements. |
| Distribution | PKP-16 | Pre-compilation (Profile) | GENESIS | Platforms, aspect ratios, localization, accessibility, metadata, release strategy, packaging. |
| Quality | PKP-17 | Pass 18 | GENESIS | Acceptance criteria: story quality, character quality, continuity, emotional effectiveness, technical readiness. |
| Knowledge Graph | PKP-18 | Pass 17 | GENESIS | Canonical map: entities, relationships, dependencies, lineage, versioning, confidence, evidence, traceability. |
| Timeline | (new) | Pass 15 | GENESIS | Per-scene start/end time, duration, transitions, total runtime, parallel tracks. |
| Cinematic Prompts | (new) | Pass 16 | GENESIS | Per-scene medium-agnostic creative prompts + provider-specific hints + negative prompts. |
| Rendering Plan | (new) | Pass 17 (derived) | GENESIS | Which scenes, which assets, which capabilities, which providers, in what order. |
| Asset Requirements | (new) | Pass 17 (derived) | GENESIS | Enumerated assets to be produced: images, clips, audio, final video. |
| PKP Metadata | (new) | Pass 19 | GENESIS | Version, content hash, creation timestamp, compiler version, profile ID, mode (fast/deep). |

---

## 5.3 Ownership Model

| Artifact | Written By | Read By | Modified By |
|----------|-----------|--------|-------------|
| All PKP artifacts (PKP-00..18 + new) | GENESIS (compiler passes) | PROMETHEUS (rendering), ORACLE (validation), ATLAS (persistence), Human (review) | No one after freeze. Amendment creates a new version. |
| Validation results (written by ORACLE) | ORACLE | GENESIS (for revision), Human (for review) | ORACLE (appends new validation results as new PKG revisions) |
| Asset references (written by PROMETHEUS) | PROMETHEUS | ATLAS (persistence), ORACLE (validation), Human (review) | PROMETHEUS (on re-render, creates new references) |

---

## 5.4 Lifecycle

```
    ┌──────────┐
    │  Draft    │  Compiler passes running. PKP is mutable.
    └────┬─────┘
         │
    ┌────▼─────┐
    │ Validated│  Pass 18 passed. PKP is complete.
    └────┬─────┘
         │
    ┌────▼─────┐
    │  Frozen  │  Pass 19. PKP is immutable. Versioned. Hashed.
    └────┬─────┘
         │
    ┌────▼─────┐
    │ Rendered │  PROMETHEUS has produced media from this PKP version.
    └────┬─────┘
         │
    ┌────▼─────┐
    │ Validated│  ORACLE has validated the media against this PKP version.
    └────┬─────┘
         │
    ┌────▼─────┐
    │ Accepted │  Human has accepted the output. Production is complete.
    └────┬─────┘
         │
    ┌────▼─────┐
    │ Archived │  ATLAS has persisted the PKP + media + validation.
    └──────────┘

    Alternative: at any point after Frozen, the human may Amend:
    ┌──────────┐
    │ Amended  │  Human modifies the PKP. New version created.
    └────┬─────┘
         │
         └──► Returns to Draft for affected passes only.
```

---

## 5.5 Identifier Scheme

| Identifier | Format | Example | Scope |
|-----------|--------|---------|-------|
| PKP ID | `pkp-{uuid}` | `pkp-550e8400-e29b-41d4-a716-446655440000` | Unique per production. |
| PKP Version | `pkp-{uuid}@{major}.{minor}` | `pkp-550e8400...@1.0` | Semantic version. Major = creative change. Minor = technical fix. |
| PKP Hash | `sha256:{hex}` | `sha256:a1b2c3d4...` | Content hash of the serialized PKP. Changes on any content modification. |
| Scene ID | `scene-{NNN}` | `scene-001` | Unique within PKP. Zero-padded. |
| Shot ID | `shot-{sceneNNN}-{NN}` | `shot-scene001-01` | Unique within scene. |
| Character ID | `char-{key}` | `char-arjun` | Unique within PKP. kebab-case. |
| Location ID | `loc-{key}` | `loc-lighthouse` | Unique within PKP. kebab-case. |
| Asset ID | `asset-{type}-{NNN}` | `asset-image-001` | Unique within PKP. Assigned by PROMETHEUS. |
| Clip ID | `clip-{sceneNNN}` | `clip-scene001` | Unique within PKP. One per scene. |

---

## 5.6 Dependency Graph

The PKP contains an internal dependency graph that maps which artifacts depend on which:

```
PKP-00 (Vision) ──────► PKP-01 (Creative Strategy) ──────► PKP-02 (Project)
     │                                                        │
     │                                                        ▼
     ▼                                                   PKP-03 (Research)
 PKP-04 (Story) ◄─────────────────────────────────────────────┤
     │                                                        │
     ├──► PKP-05 (World)                                      │
     ├──► PKP-06 (Characters) ──► PKP-07 (Relationships)     │
     │         │                                              │
     │         └──► PKP-08 (Psychology) ◄──────────────────────┘
     │
     ├──► PKP-09 (Narrative) ──► PKP-10 (Directorial Language)
     │         │                        │
     │         │                        ├──► PKP-11 (Production Design)
     │         │                        │
     │         │                   PKP-12 (Audio Intent)
     │         │                        │
     │         │                   PKP-13 (Editing Language)
     │         │                        │
     │         │                   PKP-14 (Animation Intent)
     │         │
     │         └──► PKP-15 (Production Blueprint) ◄──┘
     │                        │
     │                        ▼
     │                   PKP-16 (Distribution)
     │
     └──► PKP-17 (Quality) ◄── (validates all)
              │
              ▼
         PKP-18 (Knowledge Graph) ◄── (indexes all)
```

---

## 5.7 Regeneration Rules

| Rule | Detail |
|------|--------|
| **Full regeneration** | If PKP-00 (Vision) or PKP-04 (Story) changes, all downstream passes must recompile. The entire PKP is re-versioned (major version bump). |
| **Partial regeneration** | If PKP-10 (Directorial Language) changes, only Passes 10, 11, 15, 16, 17, 18, 19 recompile. PKP minor version bump. |
| **Scene-level regeneration** | If one scene's specification changes, only that scene's downstream artifacts (shot, prompt, timeline entry) recompile. PKP patch version bump. |
| **Media regeneration** | If the PKP is unchanged but the provider changes, PROMETHEUS re-renders all affected assets. The PKP version is unchanged; the asset references and provenance are updated. |
| **Validation regeneration** | ORACLE re-runs validation without recompiling the PKP. Validation results are appended to the PKG as a new revision. |
| **Deterministic replay** | Same PKP version + same provider versions = same output. Verified by comparing output hashes. |

---

# PART 6: NEW CONSTITUTIONS

---

## 6.1 Existing Constitution Inventory

The constitutional layer currently has 10 core constitutions (GFS-000..009), all of which exist as full-text files and are preserved without amendment:

| ID | Title | Status |
|----|-------|--------|
| GFS-000 | Constitutional Charter | PRESERVED — Supreme authority |
| GFS-001 | Identity Constitution | PRESERVED — Expanded in scope (see §3.3), not amended |
| GFS-002 | Reasoning Constitution | PRESERVED |
| GFS-003 | Knowledge Constitution | PRESERVED — Expanded in scope, not amended |
| GFS-004 | Discovery Constitution | PRESERVED |
| GFS-005 | Agent Constitution | PRESERVED — Expanded in scope, not amended |
| GFS-006 | Validation Constitution | PRESERVED — Expanded in scope, not amended |
| GFS-007 | Governance Constitution | PRESERVED |
| GFS-008 | Constitutional Meta-Model | PRESERVED |
| GFS-009 | Constitutional Ontology Framework | PRESERVED |

Additionally, GFS-010 is referenced in PKP-18 but does not exist as a file. This is a gap to be filled.

---

## 6.2 New Constitutions Required

New constitutions are issued as **derived standards** (GFS-010+) under the governance framework (GFS-007). They extend the core 10; they do not amend them. Each new constitution governs a domain that currently lacks constitutional authority.

### GFS-010: Production Knowledge Graph Specification

| Aspect | Detail |
|--------|--------|
| **Status** | Referenced in PKP-18 but not written. This is the first new constitution to ratify. |
| **Domain** | The canonical structure, lifecycle, and governance of the Production Knowledge Graph. |
| **Authority** | Derived from GFS-003 (Knowledge Constitution). |
| **Scope** | Defines: the PKG as a directed labeled graph; node types (entity, decision, asset, validation); edge types (depends-on, derives-from, validates, produces); provenance fields; confidence levels; revision immutability; query interface; persistence requirements. |
| **Key invariants** | The PKG is the single source of truth for all four pillars. The PKG is immutable after commit. Every node carries provenance. The PKG is regenerable from PKP-00..17. The PKG is persisted by ATLAS. |
| **Dependencies** | GFS-003 (Knowledge Constitution), GFS-009 (Ontology Framework) |

### GFS-011: Director Constitution

| Aspect | Detail |
|--------|--------|
| **Status** | New. No existing constitution governs the directorial function. |
| **Domain** | The AI Film Director: how creative decisions are made, who makes them, what authority they have, and how they are recorded. |
| **Authority** | Derived from GFS-001 (Identity), GFS-005 (Agent). |
| **Scope** | Defines: the directorial function as distributed across compiler passes; the Director Compiler (Pass 04) as the primary directorial authority; the requirement that every directorial decision is recorded in the PKP with provenance; the prohibition against PROMETHEUS making directorial decisions; the human's right to override any directorial decision. |
| **Key invariants** | Every visual, audio, and performance decision is made in GENESIS. PROMETHEUS executes, never directs. The human is the final director. Directorial decisions are immutable after PKP freeze. |
| **Dependencies** | GFS-001 (Identity), GFS-005 (Agent), GFS-003 (Knowledge) |

### GFS-012: Music Constitution

| Aspect | Detail |
|--------|--------|
| **Status** | New. Music is referenced in PKP-12 (Audio Intent) and GO-110 (Audio Ontology) but has no constitutional authority. |
| **Domain** | Music direction: theme, instrumentation, tempo, intensity, transitions, silence. |
| **Authority** | Derived from GFS-003 (Knowledge), GFS-005 (Agent). |
| **Scope** | Defines: the Music Compiler (Pass 12) as the constitutional authority for music direction; the requirement that every scene has a music cue (including silence as a valid cue); the prohibition against PROMETHEUS selecting music not authorized by the PKP; the music direction's immutability after PKP freeze. |
| **Key invariants** | Every scene has a music direction. Silence is explicit, not assumed. Music selection is a creative decision made by GENESIS, not PROMETHEUS. |
| **Dependencies** | GFS-003 (Knowledge), GFS-005 (Agent), GO-110 (Audio Ontology) |

### GFS-013: Audio Constitution

| Aspect | Detail |
|--------|--------|
| **Status** | New. Audio is referenced in PKP-12 and GO-110 but has no constitutional authority. |
| **Domain** | Sound design: SFX, ambient soundscape, audio transitions, silence. |
| **Authority** | Derived from GFS-003, GFS-005. |
| **Scope** | Defines: the Audio Compiler (Pass 13) as the authority for sound design; the requirement that every scene has a soundscape; the "no auditory voids" principle (from `.ai/identity.yaml: "without visual or auditory voids"`); the prohibition against PROMETHEUS adding sounds not in the PKP. |
| **Key invariants** | Every scene has a soundscape. No auditory voids. SFX are creative decisions made by GENESIS. |
| **Dependencies** | GFS-003, GFS-005, GO-110 |

### GFS-014: Prompt Constitution

| Aspect | Detail |
|--------|--------|
| **Status** | New. Prompts are generated by the backend pipeline and the Genesis PromptEngineerAgent but have no constitutional authority. |
| **Domain** | Cinematic prompts: the medium-agnostic creative instructions that PROMETHEUS translates into provider-specific prompts. |
| **Authority** | Derived from GFS-003, GFS-005. |
| **Scope** | Defines: the Prompt Compiler (Pass 16) as the authority for prompt generation; the requirement that prompts are medium-agnostic (not tied to FLUX, SD, or SVD); the requirement that provider-specific prompt translation happens in PROMETHEUS, not GENESIS; the requirement that prompts include camera, lighting, and visual style. |
| **Key invariants** | Prompts are medium-agnostic. Provider-specific translation is PROMETHEUS's job. Prompts are creative decisions. |
| **Dependencies** | GFS-003, GFS-005, GO-109 (Visual Expression Ontology) |

### GFS-015: Platform Constitution

| Aspect | Detail |
|--------|--------|
| **Status** | New. Platform is referenced in PKP-02 (Project) and PKP-16 (Distribution) but has no constitutional authority. |
| **Domain** | Platform targeting: aspect ratio, resolution, codec, bitrate, fps, duration policy. |
| **Authority** | Derived from GFS-001 (Identity — medium-agnostic), GFS-003. |
| **Scope** | Defines: the production profile as the constitutional authority for platform targeting; the requirement that the profile is selected before compilation begins; the requirement that PROMETHEUS respects the profile's rendering parameters; the prohibition against changing the profile mid-compilation. |
| **Key invariants** | The profile is selected before compilation. The profile governs runtime, scene count, and scene duration. PROMETHEUS must respect the profile's rendering parameters. |
| **Dependencies** | GFS-001, GFS-003, `config/production_profiles.yaml` |

### GFS-016: Continuity Constitution

| Aspect | Detail |
|--------|--------|
| **Status** | New. Continuity is referenced in PKP-17 (Quality) and GO-113 (Asset Ontology) but has no constitutional authority. |
| **Domain** | Continuity: character identity, location identity, prop tracking, wardrobe tracking, lighting continuity, blocking continuity across scenes. |
| **Authority** | Derived from GFS-003, GFS-006 (Validation). |
| **Scope** | Defines: continuity as a first-class creative concern; the requirement that the Character Compiler (Pass 09) defines character visual identity and consistency rules; the requirement that ORACLE validates continuity; the requirement that ATLAS persists character hero images for cross-scene consistency. |
| **Key invariants** | Characters look the same across scenes (within provider capability). Locations maintain identity. Props and wardrobe are tracked. ORACLE detects continuity breaks. |
| **Dependencies** | GFS-003, GFS-006, GO-113, GO-104 (Character Ontology), GO-105 (World Ontology) |

### GFS-017: Quality Constitution

| Aspect | Detail |
|--------|--------|
| **Status** | New. Quality is referenced in PKP-17 and GFS-006 but has no dedicated constitution. |
| **Domain** | Quality: acceptance criteria, quality scoring, quality reporting, quality feedback into revision. |
| **Authority** | Derived from GFS-006 (Validation), GFS-007 (Governance). |
| **Scope** | Defines: ORACLE as the quality authority; the quality dimensions (visual, audio, narrative, emotional, technical); the quality scoring scale; the quality report format; the requirement that quality reports feed back into the PKG; the human's right to override quality findings. |
| **Key invariants** | Quality is measured, not asserted. Quality reports are advisory, not binding. The human decides. Quality findings are persisted with provenance. |
| **Dependencies** | GFS-006, GFS-007, GO-114 (Evaluation Ontology) |

### GFS-018: Rendering Constitution

| Aspect | Detail |
|--------|--------|
| **Status** | New. Rendering is currently ungoverned (by design — GFS-001 says Genesis is pre-production only). With PROMETHEUS as a pillar, rendering needs constitutional authority. |
| **Domain** | Rendering: the execution of the PKP as media. Deterministic replay. Provider independence. Provenance for produced assets. |
| **Authority** | Derived from GFS-001 (Identity — provider-agnostic), GFS-003 (Knowledge — provenance). |
| **Scope** | Defines: PROMETHEUS as the rendering authority; the requirement that PROMETHEUS reads the PKP and executes without creative decisions; the deterministic replay invariant (same PKP + same providers = same output); the requirement that every produced asset carries provenance; the capability registry as the constitutional interface between PROMETHEUS and providers; the prohibition against PROMETHEUS modifying the PKG. |
| **Key invariants** | PROMETHEUS makes no creative decisions. Deterministic replay is guaranteed. Every asset has provenance. Providers are behind the capability registry. |
| **Dependencies** | GFS-001, GFS-003, GFS-005, `config/movie_os.yaml` (provider config) |

---

## 6.3 Constitution Extension Map

```
GFS-000 (Charter) ──────────────────────────────────────────────┐
                                                                 │
GFS-001 (Identity) ──────► GFS-011 (Director)                   │
                     │                    └─► GFS-015 (Platform)  │
                     │                    └─► GFS-018 (Rendering)│
                     │                                           │
GFS-002 (Reasoning) ────────────────────────────────────────────┤
                                                                 │
GFS-003 (Knowledge) ──────► GFS-010 (PKG Spec)                  │
                     │                    └─► GFS-011 (Director) │
                     │                    └─► GFS-012 (Music)    │
                     │                    └─► GFS-013 (Audio)    │
                     │                    └─► GFS-014 (Prompt)   │
                     │                    └─► GFS-016 (Continuity)│
                     │                    └─► GFS-018 (Rendering)│
                     │                                           │
GFS-004 (Discovery) ────────────────────────────────────────────┤
                                                                 │
GFS-005 (Agent) ──────────► GFS-011 (Director)                  │
                     │                    └─► GFS-012 (Music)    │
                     │                    └─► GFS-013 (Audio)    │
                     │                    └─► GFS-014 (Prompt)   │
                     │                    └─► GFS-018 (Rendering)│
                     │                                           │
GFS-006 (Validation) ─────► GFS-016 (Continuity)                │
                     │                    └─► GFS-017 (Quality)  │
                     │                                           │
GFS-007 (Governance) ─────► GFS-017 (Quality)                  │
                     │                                           │
GFS-008 (Meta-Model) ───────────────────────────────────────────┤
                                                                 │
GFS-009 (Ontology) ───────► GFS-010 (PKG Spec)                  │
                                                                 │
                                                                 ▼
                                                          [Governed by
                                                           GFS-007]
```

**Total constitutions after migration:** 10 core (GFS-000..009, preserved) + 9 new derived (GFS-010..018) = **19 constitutions**.

---

# PART 7: ROADMAP

---

## 7.1 Migration Principles

| # | Principle | Detail |
|---|-----------|--------|
| MP-1 | **Preserve the constitutional layer.** GFS-000..009 are not amended. New constitutions extend. | The core 10 constitutions are the foundation. Breaking them breaks the engine's identity. |
| MP-2 | **Converge before extending.** Unify the three pre-production paths before building PROMETHEUS. | You cannot build a consumer (PROMETHEUS) without a stable producer output (the PKP schema). |
| MP-3 | **Low risk first, high risk later.** Start with naming, configuration, and documentation. End with pillar construction. | Minimize disruption to the working backend pipeline. |
| MP-4 | **Backward compatibility at every step.** Each migration step must leave the system in a working state. | The backend pipeline must continue to function throughout the migration. |
| MP-5 | **Generate an ADR for every architectural decision.** Each migration step generates an ADR in `docs/genesis/decisions/`. | The migration is auditable. |
| MP-6 | **Test before moving.** Each step has a verification criterion before the next step begins. | No blind migrations. |
| MP-7 | **The human is the final reviewer.** No migration step is "done" until the human verifies it. | Consistent with §3.6 of the Constitutional Architecture. |

---

## 7.2 Migration Phases

### Phase 0: Foundation (Low Risk — Documentation, Naming, Configuration)

**Goal:** Align naming, identity, and documentation with the Cinema Production Engine vision. No code changes.

| Step | Action | Verification | ADR |
|------|--------|-------------|-----|
| 0.1 | Update `.ai/identity.yaml`: `name: "Cinema Production Engine"`, add `legacy_name: "Movie OS"`. | Identity file reflects new name. | ADR-005 |
| 0.2 | Replace `README.md` with Cinema Production Engine overview referencing §00. | README is accurate. | ADR-006 |
| 0.3 | Replace `ARCHITECTURE.md` with pointer to §00 and this document. | Architecture pointer is correct. | ADR-007 |
| 0.4 | Replace `ROADMAP.md` with §7 of this document. | Roadmap is current. | ADR-008 |
| 0.5 | Replace `DECISIONS.md` with pointer to `docs/genesis/decisions/` ADR registry. | Decision log is unified. | ADR-009 |
| 0.6 | Remove plaintext API key from `config/movie_os.yaml`. Move to environment variable. | `git grep "sk-lm-"` returns no results in tracked files. | ADR-010 |
| 0.7 | Remove duplicate `producer_brief` field in `config/models.py:42-43`. | No duplicate fields. | ADR-011 |
| 0.8 | Clean up `prompt_engineer_agent.py` duplicated import lines (11-153) and undefined `visual_style_guides` variable. | File has no duplicated imports. | ADR-012 |
| 0.9 | Normalize constitution filenames in `docs/genesis/constitutions/` to `NNN-Name.md`. | All filenames follow `NNN-Name.md` pattern. | ADR-013 |
| 0.10 | Correct GO-004/GO-005 taxonomy in `docs/genesis/04_GO.md` to match actual files. | Index matches files. | ADR-014 |
| 0.11 | Reconcile GO-201/GO-301 taxonomy placement in `docs/genesis/04_GO.md`. | Taxonomy is unambiguous. | ADR-015 |

### Phase 1: Constitutional Extension (Low Risk — Specification Only)

**Goal:** Ratify the 9 new derived constitutions (GFS-010..018). No code changes.

| Step | Action | Verification | ADR |
|------|--------|-------------|-----|
| 1.1 | Write GFS-010 (Production Knowledge Graph Specification). | File exists at `constitutions/010-PKG-Specification.md`. Referenced by PKP-18. | ADR-016 |
| 1.2 | Write GFS-011 (Director Constitution). | File exists. | ADR-017 |
| 1.3 | Write GFS-012 (Music Constitution). | File exists. | ADR-018 |
| 1.4 | Write GFS-013 (Audio Constitution). | File exists. | ADR-019 |
| 1.5 | Write GFS-014 (Prompt Constitution). | File exists. | ADR-020 |
| 1.6 | Write GFS-015 (Platform Constitution). | File exists. | ADR-021 |
| 1.7 | Write GFS-016 (Continuity Constitution). | File exists. | ADR-022 |
| 1.8 | Write GFS-017 (Quality Constitution). | File exists. | ADR-023 |
| 1.9 | Write GFS-018 (Rendering Constitution). | File exists. | ADR-024 |
| 1.10 | Update `docs/genesis/03_GFS.md` index to include GFS-010..018. | Index lists all 19 constitutions. | ADR-025 |

### Phase 2: PKP Schema Unification (Medium Risk — Schema Definition)

**Goal:** Define the canonical PKP schema that all pre-production paths produce. No existing code is broken; the schema is defined but not yet enforced.

| Step | Action | Verification | ADR |
|------|--------|-------------|-----|
| 2.1 | Define the canonical PKP JSON Schema based on §5. | Schema file exists at `docs/genesis/schemas/json-schema/003-PKP-Canonical.json`. | ADR-026 |
| 2.2 | Map each existing PKP specification (PKP-00..18) to the canonical schema. | Mapping document exists. All 19 PKP specs have a schema mapping. | ADR-027 |
| 2.3 | Define the new artifacts (Timeline, Cinematic Prompts, Rendering Plan, Asset Requirements, PKP Metadata) as schema extensions. | Schema extensions validated. | ADR-028 |
| 2.4 | Define the compiler pass interface (abstract input/output/validation per pass). | Interface file exists. | ADR-029 |
| 2.5 | Write the Compiler Architecture Specification (§4 as a Genesis specification). | Specification file exists at `docs/genesis/specifications/compiler/002-Creative-Compiler.md`. | ADR-030 |

### Phase 3: Pre-Production Convergence (Medium Risk — Code Changes Begin)

**Goal:** Unify the three pre-production paths into a single GENESIS with two modes. The backend pipeline continues to work; it now produces the canonical PKP schema.

| Step | Action | Verification | ADR |
|------|--------|-------------|-----|
| 3.1 | Refactor `pipeline_service.py` to produce canonical PKP output (fast mode). The existing 6-stage pipeline remains but outputs the unified schema. | Backend pipeline produces canonical PKP. Existing frontend still works. | ADR-031 |
| 3.2 | Refactor `movie_os/genesis/engine.py` to produce canonical PKP output (deep mode). | Genesis engine produces canonical PKP. | ADR-032 |
| 3.3 | Refactor `movie_os/genesis2/engine.py` to produce canonical PKP output (deep mode). | Genesis2 produces canonical PKP. | ADR-033 |
| 3.4 | Implement the compiler pass interface for each of the 19 passes. Fast mode uses backend pipeline implementations; deep mode uses Genesis/Genesis2 implementations. | All 19 passes have fast and deep mode implementations. | ADR-034 |
| 3.5 | Implement the pre-compilation step (profile loader + discovery + scene class planner) as the shared entry point. | All modes use the same pre-compilation. | ADR-035 |
| 3.6 | Implement the validation gate (Pass 18) with the extended criteria. | Gate enforces all criteria (existing 8 + new). | ADR-036 |
| 3.7 | Implement the freeze + hash step (Pass 19). | PKP is frozen, versioned, hashed. | ADR-037 |
| 3.8 | Merge frontend genesis + genesis2 tabs into a single GENESIS tab with mode selector (fast/deep). | UI shows one GENESIS tab with mode selector. | ADR-038 |
| 3.9 | Fix `_rerun_from_stage` to use the actual production profile instead of hardcoded `"medium"`. | Retry uses the correct profile. | ADR-039 |

### Phase 4: PROMETHEUS Construction (High Risk — New Pillar)

**Goal:** Build PROMETHEUS as the unified production intelligence. Media services are refactored but continue to work.

| Step | Action | Verification | ADR |
|------|--------|-------------|-----|
| 4.1 | Define the PROMETHEUS interface (reads PKP, writes to ATLAS). | Interface specification exists. | ADR-040 |
| 4.2 | Implement the Production Planner (reads PKP, produces rendering plan). | Planner produces a rendering plan from a test PKP. | ADR-041 |
| 4.3 | Refactor `image_service.py` into PROMETHEUS Image Realization. Existing API endpoints continue to work. | Image generation works through PROMETHEUS. | ADR-042 |
| 4.4 | Refactor `video_service.py` into PROMETHEUS Video Realization. | Video generation works through PROMETHEUS. | ADR-043 |
| 4.5 | Refactor `tts_service.py` into PROMETHEUS Voice Realization. | TTS works through PROMETHEUS. | ADR-044 |
| 4.6 | Implement PROMETHEUS Music Realization (currently procedural/numpy; future providers behind capability registry). | Music generation works through PROMETHEUS. | ADR-045 |
| 4.7 | Implement PROMETHEUS Audio Assembly (mix voice, music, SFX). | Audio mixing works through PROMETHEUS. | ADR-046 |
| 4.8 | Implement PROMETHEUS Video Assembly (concatenate clips, apply transitions). | Final video assembly works through PROMETHEUS. | ADR-047 |
| 4.9 | Implement the Asset Emitter (writes to ATLAS with provenance). | All produced assets have provenance metadata. | ADR-048 |
| 4.10 | Implement the provider-specific prompt adapter (translates PKP creative prompts into FLUX/SD/SVD prompts). | Prompts are provider-translated at render time, not compile time. | ADR-049 |
| 4.11 | Merge duplicate Movie OS image/video/voice/music agents into single PROMETHEUS components. | No duplicate agent implementations. | ADR-050 |
| 4.12 | Verify deterministic replay: same PKP + same providers = same output hash. | Deterministic replay test passes. | ADR-051 |

### Phase 5: ATLAS Construction (Medium-High Risk — Persistence)

**Goal:** Build ATLAS as the persistence layer. Replace in-memory state.

| Step | Action | Verification | ADR |
|------|--------|-------------|-----|
| 5.1 | Define the ATLAS interface (store, retrieve, query, persist). | Interface specification exists. | ADR-052 |
| 5.2 | Implement ATLAS Asset Store with provenance metadata. | Assets are stored with provenance. | ADR-053 |
| 5.3 | Implement ATLAS Knowledge Persistence (PKG to disk). | PKG survives restart. | ADR-054 |
| 5.4 | Implement ATLAS Model Registry. | Model versions are tracked. | ADR-055 |
| 5.5 | Implement ATLAS Content Library (reusable characters, locations, styles, voice profiles). | Content is reusable across productions. | ADR-056 |
| 5.6 | Replace in-memory `_pipelines` dict with ATLAS-managed persistence. | Pipeline state survives restart. | ADR-057 |
| 5.7 | Replace in-memory `_generation_states` dict with ATLAS-managed persistence. | Generation state survives restart. | ADR-058 |
| 5.8 | Replace in-memory `_image_states` dict with ATLAS-managed persistence. | Image state survives restart. | ADR-059 |
| 5.9 | Elevate `.project-ai/` operational memory from convention to ATLAS-managed service. | Checkpoint protocol is automated. | ADR-060 |

### Phase 6: ORACLE Construction (High Risk — New Pillar)

**Goal:** Build ORACLE as the validation intelligence. Close the validation loop.

| Step | Action | Verification | ADR |
|------|--------|-------------|-----|
| 6.1 | Define the ORACLE interface (reads PKP + media, writes validation report). | Interface specification exists. | ADR-061 |
| 6.2 | Implement ORACLE Structural Validation (media matches PKP structure). | Structural validation works. | ADR-062 |
| 6.3 | Refactor `image_verifier.py` CLIP logic into ORACLE Visual Consistency. | Visual consistency validation works. | ADR-063 |
| 6.4 | Merge 7 evaluation agents from `movie_os/agents/evaluation/` into ORACLE. | All evaluation is unified. | ADR-064 |
| 6.5 | Implement ORACLE Emotional Arc Adherence. | Emotional arc validation works. | ADR-065 |
| 6.6 | Implement ORACLE Continuity Enforcement. | Continuity validation works. | ADR-066 |
| 6.7 | Implement ORACLE Drift Detection (PROMETHEUS made no unauthorized decisions). | Drift detection works. | ADR-067 |
| 6.8 | Implement ORACLE Quality Scoring (aggregate score). | Quality score is computed. | ADR-068 |
| 6.9 | Implement ORACLE Validation Report (written into PKG). | Reports are persisted with provenance. | ADR-069 |
| 6.10 | Implement the revision loop: ORACLE report → human review → PKP amendment → recompile → re-render. | Full lifecycle works end-to-end. | ADR-070 |

### Phase 7: Full Lifecycle Integration (High Risk — End-to-End)

**Goal:** The north star — full lifecycle from idea to finished film.

| Step | Action | Verification | ADR |
|------|--------|-------------|-----|
| 7.1 | Implement the full lifecycle: human intent → GENESIS compile → PROMETHEUS render → ORACLE validate → ATLAS persist. | End-to-end pipeline works. | ADR-071 |
| 7.2 | Implement partial regeneration: human amends PKP → recompile affected passes only → re-render affected assets only. | Partial regeneration is faster than full regeneration. | ADR-072 |
| 7.3 | Implement cross-production reuse: ATLAS Content Library provides characters, locations, styles to new productions. | A character from production A is reused in production B. | ADR-073 |
| 7.4 | Verify deterministic creative replay across the full lifecycle. | Same PKP + same providers = same final video hash. | ADR-074 |
| 7.5 | Deprecate Movie OS legacy top-level agents (`story_agent.py`, `visual_agent.py`, `voice_agent.py`, `music_agent.py`, `sfx_agent.py`, `qa_agent.py`, `publishing_agent.py`, `movie_agent.py`). | Legacy files are removed. Functionality is in pillars. | ADR-075 |
| 7.6 | Update frontend to show all four pillars: GENESIS (compile), PROMETHEUS (render), ORACLE (validate), ATLAS (persist). | UI is pillar-aware. | ADR-076 |

---

## 7.3 Risk Classification

| Phase | Risk Level | Why | Mitigation |
|-------|-----------|-----|------------|
| Phase 0 | Low | Documentation and naming only. No code changes. | N/A. |
| Phase 1 | Low | Specification only. No code changes. | N/A. |
| Phase 2 | Medium | Schema definition. No code changes, but the schema governs future code. | Schema is reviewed by the human before Phase 3. |
| Phase 3 | Medium | First code changes. Backend pipeline is refactored but must continue to work. | Each step is verified before the next begins. The frontend continues to work throughout. |
| Phase 4 | High | New pillar (PROMETHEUS). Media services are refactored. Risk of breaking image/video/TTS generation. | PROMETHEUS is built alongside existing services. Existing services are not removed until PROMETHEUS is verified. |
| Phase 5 | Medium-High | Persistence replaces in-memory state. Risk of data loss on migration. | In-memory state is kept as a fallback during migration. ATLAS persistence is verified before in-memory dicts are removed. |
| Phase 6 | High | New pillar (ORACLE). Validation logic is complex. Risk of false positives blocking valid productions. | ORACLE's reports are advisory, not blocking, during initial deployment. The human can override. |
| Phase 7 | High | End-to-end integration. Risk of integration bugs. | Full lifecycle test with a known-good production before deprecating legacy systems. |

---

## 7.4 Backward Compatibility Contract

| What | Guarantee | Duration |
|------|-----------|----------|
| Backend 6-stage pipeline | Continues to function through Phase 3. After Phase 3, it becomes GENESIS Fast Mode (same API, same output format, now canonical PKP). | Forever (as Fast Mode) |
| Frontend 7-tab structure | Continues to function through Phase 3.8. After that, genesis + genesis2 tabs merge. The other 5 tabs remain. | Forever (6 tabs after merge) |
| `config/production_profiles.yaml` | Unchanged. | Forever |
| `config/llm_config.yaml` | Unchanged through Phase 3. May be restructured in Phase 4 as provider config moves behind the capability registry. | Through Phase 3 |
| `config/movie_os.yaml` | Unchanged through Phase 4. Provider config is restructured in Phase 4. Rendering config moves to PROMETHEUS defaults. | Through Phase 4 |
| `docs/genesis/` constitutions | GFS-000..009 unchanged forever. GFS-010..018 added in Phase 1. | Forever |
| `docs/genesis/ontology/` | All 28 ontology files unchanged. | Forever |
| `docs/genesis/specifications/pkp/` | All 19 PKP specs unchanged. | Forever |
| `docs/genesis/workflows/` | All 8 workflows unchanged. Extended in Phase 4 and 6. | Forever |
| `docs/genesis/decisions/` | All 4 ADRs unchanged. New ADRs added per step. | Forever |
| REST API (`/api/v1/`) | Endpoints continue to function. New endpoints added for PROMETHEUS, ATLAS, ORACLE. | Forever (v1) |
| `frontend/src/lib/types.ts` | Types are additive (new fields, new interfaces). No existing type is removed. | Forever |
| `frontend/src/lib/api.ts` | API functions are additive. Existing functions continue to work. | Forever |

---

**End of GENESIS 2.0 Migration Specification**

This document is the constitutional migration blueprint. All future implementation work follows the phase ordering and subsystem classifications defined here. Every architectural decision made during the migration generates an ADR traceable to a principle in this document or in the Constitutional Architecture (§00).

*"The engine treats film production as a compilation problem, not a generation problem. GENESIS is the AI Film Director and Production Compiler. PROMETHEUS is the rendering runtime. ATLAS is the persistent memory. ORACLE is the validation intelligence. The Production Knowledge Package is the contract between them. The human is the final reviewer."*

— GENESIS 2.0 Migration Specification, §7