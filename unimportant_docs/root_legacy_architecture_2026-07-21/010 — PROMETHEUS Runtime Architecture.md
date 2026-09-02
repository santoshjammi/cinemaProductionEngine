# 010 — PROMETHEUS Runtime Architecture

**Status:** Architectural Specification — Phase II
**Version:** 1.0.0
**Date:** 2026-07-21
**Derives Authority From:** `006` (Constitution, Tier 0); `001` §2.1 (PROMETHEUS pillar definition, Tier 2); `009` (PKP, the runtime's input, Tier 2); `004` (COM, the object model the runtime renders, Tier 2).
**Precedence:** Below the Constitution. This specification is the full architectural realization of the PROMETHEUS pillar introduced in `001` §2.1 and constitutionalized by `006` (L-14, L-15, L-18).
**Scope:** The runtime's philosophy, execution model, media rendering, resource scheduling, services, contracts, optimization, error handling, deterministic rendering, extensibility, platform independence, and governance.

---

## Table of Contents

1. [Runtime Philosophy](#1-runtime-philosophy)
2. [Execution Model](#2-execution-model)
3. [Media Rendering](#3-media-rendering)
4. [Resource Scheduling](#4-resource-scheduling)
5. [Runtime Services](#5-runtime-services)
6. [Execution Contracts](#6-execution-contracts)
7. [Runtime Optimization](#7-runtime-optimization)
8. [Error Handling](#8-error-handling)
9. [Deterministic Rendering](#9-deterministic-rendering)
10. [Runtime Extensibility](#10-runtime-extensibility)
11. [Platform Independence](#11-platform-independence)
12. [Governance](#12-governance)

---

# 1. Runtime Philosophy

## 1.1 The Runtime Is a Pure Executor

PROMETHEUS is the ACI Platform's execution engine. It reads the Production Knowledge Package (`009`) — the compiled, executable specification of a creative work — and renders it into media (images, video, audio, final rendered work). The runtime is a **pure executor**: it has zero creative authority (`006` L-15) and zero authority to alter the PKP (`006` L-14).

The runtime's role in the platform's compiler metaphor (`00` §3.2):

| Compiler stage | ACI Platform analog |
|----------------|---------------------|
| Source program | CIS (`003`) |
| AST / IR | CIR (`007`) |
| Compiled binary | PKP (`009`) |
| **Runtime execution** | **PROMETHEUS (this specification)** |
| Program output | Media (images, video, audio) |

The runtime is to the PKP what a program loader is to a compiled binary: it loads the specification and executes it, without exercising judgment about what the program should do.

## 1.2 Zero Creative Authority

The runtime is constitutionally prohibited from:

- **Inventing creative content** (`006` L-15): no dialogue, no symbolism, no emotion, no pacing, no camera philosophy, no music philosophy, no editing philosophy may originate in the runtime.
- **Altering the PKP** (`006` L-14): the runtime reads the PKP; it may not modify it.
- **Making creative decisions**: the runtime renders what the PKP specifies; if the PKP is silent on a detail, the runtime does not invent it — it reports a rendering gap (Part 8).

If the runtime finds it cannot render a PKP artifact without a creative decision that is not in the PKP, it **fails loudly** (`00` §3.7) and reports the gap to ORACLE (`011`) and to the Directorial Board (`002`) for CIR amendment. It does not invent.

## 1.3 Determinism

The runtime is deterministic (`006` L-14): given the same frozen PKP and the same provider versions, it produces the same media. Determinism is the final link in the platform's deterministic replay chain:

```
CIS (deterministic intent) → CIR (deterministic decisions) → PKP (deterministic compilation) → media (deterministic rendering)
```

If any link is non-deterministic, the entire chain is non-deterministic, and the platform cannot satisfy L-13 (compiled, not generated) or L-18 (knowledge outlives media, because media could not be regenerated reliably). The runtime's determinism is therefore constitutionally mandatory.

## 1.4 Constitutional Derivation

| Law | How it governs the runtime |
|-----|----------------------------|
| L-14 (Execution Never Changes Intent) | The runtime may not alter the PKP; the PKP is the frozen executable. |
| L-15 (Execution Never Invents Creativity) | The runtime makes zero creative decisions. |
| L-18 (Knowledge Outlives Media) | Media is a derived projection of the PKP; the PKP (knowledge) is canonical. |

---

# 2. Execution Model

## 2.1 The Execution Pipeline

The runtime reads the frozen PKP from ATLAS (`012`) and produces media through a pipeline of rendering components. The pipeline mirrors the Movie OS pipeline steps already in the repository (`config/movie_os.yaml: pipeline.steps`), architecturalized:

```
Frozen PKP (009) — read from ATLAS
   │
   ▼
┌─────────────────────────────────────────────────────────────┐
│  EXECUTION PLANNING                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ PKP Loader    │  │ Rendering     │  │ Resource         │   │
│  │               │  │ Planner       │  │ Scheduler        │   │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────┘   │
│         └──────────────────┴──────────────────────┘         │
└────────────────────────────┼────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  RENDERING COMPONENTS (per the PKP's artifacts)               │
│                                                              │
│  Image Realization    — renders scene images from prompts    │
│  Video Realization    — applies motion to scene images       │
│  Voice Realization    — synthesizes speech from dialogue     │
│  Music Realization    — generates music per music direction  │
│  Audio Assembly       — mixes voice, music, SFX              │
│  Video Assembly       — concatenates clips, applies trans.   │
│  Subtitle Realization — produces subtitles from dialogue     │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  ASSET EMISSION                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ Provenance    │  │ ATLAS Writer  │  │ Execution Report │   │
│  │ Stamping      │  │               │  │                  │   │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────┘   │
│         └──────────────────┴──────────────────────┘         │
└────────────────────────────┼────────────────────────────────┘
                             │
                             ▼
                     Media (in ATLAS)
                     + Execution Report (in ATLAS)
```

## 2.2 Execution Planning

Before rendering, the runtime plans the execution:

| Step | What it does |
|------|-------------|
| **PKP Loader** | Loads the frozen PKP from ATLAS; verifies the PKP hash; verifies the PKP is in the `frozen` state. |
| **Rendering Planner** | Reads the PKP's artifacts and produces a rendering plan: which artifacts, which rendering components, in what order, with which providers. |
| **Resource Scheduler** | Schedules the rendering components based on the dependency graph and available resources (Part 4). |

The execution plan is recorded in the execution report (Part 2.4) for audit and replay.

## 2.3 Rendering

Each rendering component (Part 3) reads its input PKP artifacts, invokes the appropriate provider (Part 5.1), and produces media. The rendering component:

1. Reads its input PKP artifacts (e.g., Image Realization reads Scene and Shot artifacts, including the cinematic prompts from Pass 16).
2. Resolves the provider (from the capability registry, Part 5.1).
3. Invokes the provider with the PKP-specified parameters and the seed recorded in the PKP's provenance.
4. Receives the provider's output (an image, a clip, an audio file).
5. Stamps the output with provenance (the PKP artifact rendered, the provider version, the seed, the timestamp).
6. Emits the output to the Asset Emission stage.

## 2.4 Asset Emission

The Asset Emission stage:

1. **Provenance Stamping**: every media item is stamped with the PKP artifact it was rendered from, the PKP hash, the provider version, and the seed.
2. **ATLAS Writer**: the media is written to ATLAS (`012`) with full provenance.
3. **Execution Report**: a structured record of the execution (which artifacts were rendered, which providers were used, which seeds were used, any errors or fallbacks) is written to ATLAS.

The execution report is the runtime's analog of the compiler's compilation report (`008` Part 10.3). It is the basis for replay verification and audit.

---

# 3. Media Rendering

## 3.1 The Rendering Components

The runtime's rendering components map to the existing Movie OS services (`001` §2.1, classified as MERGE into PROMETHEUS), architecturalized:

| Component | What it renders | Input PKP artifacts | Provider (cinema runtime) |
|-----------|----------------|---------------------|---------------------------|
| **Image Realization** | Scene images | Scene, Shot, Prompt artifacts | Stable Diffusion / FLUX (local) or cloud provider |
| **Video Realization** | Motion clips | Scene, Shot, Timeline artifacts (motion subset) | SVD-XT (local) or cloud provider |
| **Voice Realization** | Speech audio | Dialogue, Character (voice identity), Voice artifacts | edge-tts (local) or cloud provider |
| **Music Realization** | Music audio | Music, Timeline artifacts (music cues) | procedural (numpy) or MusicGen / AudioLDM |
| **Audio Assembly** | Mixed audio | Voice, Music, Soundscape, Timeline artifacts (audio tracks) | FFmpeg |
| **Video Assembly** | Final video | Video clips, Audio, Timeline artifacts (transitions) | FFmpeg |
| **Subtitle Realization** | Subtitle files | Dialogue, Timeline artifacts (subtitle track) | (text generation) |

## 3.2 The Rendering Component Contract

Each rendering component is specified by a six-field contract:

| Field | Definition |
|-------|-----------|
| **Input artifacts** | The PKP artifact types the component reads. |
| **Output media** | The media type the component produces. |
| **Provider interface** | The abstract interface the component uses to invoke a provider (Part 5.1). |
| **Determinism requirements** | The seed and provider-version requirements for deterministic replay. |
| **Fallback** | The fallback provider if the primary is unavailable (Part 8). |
| **Validation** | What the component checks on its output before emission (e.g., image resolution, audio duration). |

## 3.3 Rendering and the COM

Rendering components read PKP artifacts, which are COM objects (`004` Part 2) in executable state. The components do not read the CIR, the CIS, or the faculty enrichments. The component's input is strictly the executable specification; its output is media. This is the architectural enforcement of the separation of execution from cognition (`006` Part 4.3).

---

# 4. Resource Scheduling

## 4.1 Dependency-Driven Scheduling

Rendering components are scheduled based on the PKP's dependency graph (`009` Part 3):

1. **Dependency order**: a component may not render an artifact until the artifacts it depends on are rendered (e.g., Video Assembly may not run until Video Realization and Audio Assembly have produced their outputs).
2. **Parallelism**: components rendering independent artifacts may run concurrently (e.g., Image Realization for Scene 1 and Image Realization for Scene 2 may run in parallel).
3. **Deterministic merge**: when concurrent components produce outputs that are merged (e.g., images from parallel scenes are merged into a timeline), the merge order is deterministic (by scene ordinal).

## 4.2 Resource Constraints

The scheduler respects resource constraints:

- **Local-first** (`00` §3.4): the scheduler prioritizes local providers (Ollama, Stable Diffusion, SVD-XT, edge-tts) over cloud providers.
- **Provider availability**: if a local provider is unavailable, the scheduler falls back to a cloud provider behind the same capability interface (Part 8).
- **Memory and compute**: the scheduler may serialize rendering jobs that exceed available memory or compute, preserving determinism (the order is deterministic; the timing is not).

## 4.3 Scheduling and the Execution Plan

The scheduler's decisions are recorded in the execution plan (Part 2.2), which is part of the execution report. This enables replay: a subsequent execution with the same PKP and the same scheduler configuration produces the same execution plan (modulo timing, which does not affect output).

---

# 5. Runtime Services

## 5.1 The Capability Registry

The runtime accesses providers through a **capability registry** — an abstract interface that decouples the runtime from specific providers. The capability registry is the architectural realization of `001` S5 (capability registry pattern) and `00` §3.4 (local-first, cloud-optional).

The capability registry defines:

| Capability | Abstract interface | Local provider (cinema) | Cloud provider (optional) |
|------------|-------------------|-------------------------|---------------------------|
| Image generation | `generate_image(prompt, seed, params) → image` | Stable Diffusion / FLUX | (cloud image API) |
| Video generation | `generate_video(image, motion_params, seed) → video` | SVD-XT | (cloud video API) |
| Voice synthesis | `synthesize_voice(text, voice_profile, seed) → audio` | edge-tts | (cloud TTS API) |
| Music generation | `generate_music(music_direction, seed) → audio` | procedural (numpy) | MusicGen / AudioLDM |
| Audio mixing | `mix_audio(tracks, mix_params) → audio` | FFmpeg | (cloud mixing API) |
| Video assembly | `assemble_video(clips, audio, transitions) → video` | FFmpeg | (cloud assembly API) |

The runtime invokes providers through the abstract interface; the registry resolves the interface to a specific provider (local or cloud). The provider version is recorded in the execution report for replay.

## 5.2 Provider Abstraction

The capability registry abstracts providers:

- The runtime does not know whether a provider is local or cloud; it knows only the interface.
- A provider may be swapped (e.g., Stable Diffusion replaced by a newer model) by updating the registry, without changing the runtime.
- The runtime records the provider version used, enabling replay with the same version or regeneration with a different version.

## 5.3 Asset Emission Service

The Asset Emission service (Part 2.4) is the runtime's interface to ATLAS (`012`). It:

- Writes media to ATLAS with full provenance (PKP artifact, PKP hash, provider version, seed, timestamp).
- Writes the execution report to ATLAS.
- Does not write to the PKP, CIR, or CIS (the runtime is read-only for those artifacts, L-14).

---

# 6. Execution Contracts

## 6.1 The PKP-PROMETHEUS Contract

(From `009` Part 12.1, restated here as the runtime's inbound contract.)

| Aspect | PROMETHEUS's obligation |
|--------|------------------------|
| **Read access** | PROMETHEUS reads the PKP from ATLAS by identity and version. |
| **Write access** | PROMETHEUS writes media (not the PKP) to ATLAS. |
| **Completeness** | PROMETHEUS may assume the PKP is complete (frozen, validated). |
| **Determinism** | PROMETHEUS is deterministic: same PKP + same providers → same media. |
| **`cir_origin`** | PROMETHEUS records the PKP artifact each media item was rendered from. |
| **No creativity** | PROMETHEUS makes zero creative decisions (L-15). |

## 6.2 The PROMETHEUS-ATLAS Contract

| Aspect | PROMETHEUS's obligation | ATLAS's obligation |
|--------|------------------------|---------------------|
| **Read** | Reads the PKP from ATLAS. | Provides the PKP by identity and version. |
| **Write** | Writes media and the execution report to ATLAS. | Persists media and reports with provenance. |
| **Provenance** | Stamps every media item with PKP artifact, PKP hash, provider version, seed. | Preserves the provenance chain. |
| **No cross-pillar calls** | PROMETHEUS does not call GENESIS, ORACLE, or the human. | ATLAS mediates all persistence. |

## 6.3 The PROMETHEUS-ORACLE Contract (Indirect)

PROMETHEUS does not call ORACLE directly (`001` §2.3). ORACLE reads PROMETHEUS's output (media) from ATLAS and validates it against the PKP. The contract is indirect, mediated by ATLAS:

- PROMETHEUS writes media + execution report to ATLAS.
- ORACLE reads media + PKP from ATLAS and validates.
- ORACLE writes validation reports to ATLAS.
- The Directorial Board reads validation reports from ATLAS and re-enters the CIR if drift is detected.

---

# 7. Runtime Optimization

## 7.1 Performance Optimization

The runtime may optimize performance within the bounds of determinism:

- **Parallel rendering**: independent artifacts rendered concurrently (Part 4.1).
- **Caching**: rendered media is cached by (PKP artifact hash, provider version, seed). A cache hit reuses the prior media; a cache miss re-renders. The cache is persisted in ATLAS.
- **Provider selection**: the scheduler may select a faster provider behind the same capability interface, provided the output quality is acceptable (the selection is recorded for replay).

## 7.2 What Optimization May Not Do

Optimization may not:

- Alter the PKP (L-14).
- Invent creative content (L-15).
- Change the seed (the seed is in the PKP's provenance; changing it would break determinism).
- Skip an artifact (every PKP artifact must be rendered, unless the human explicitly marks it `skipped` with rationale).

## 7.3 Optimization and Quality

Provider selection (Part 7.1) involves a quality trade-off: a faster provider may produce lower-quality output. The runtime records the provider used; ORACLE (`011`) validates the quality. If ORACLE's quality score is below threshold, the runtime re-renders with a higher-quality provider. This loop is governed by the revision cycle (`007` Part 10.5, `011`).

---

# 8. Error Handling

## 8.1 Rendering Failure

When a rendering component fails (a provider returns an error, or the output fails validation), the runtime:

1. Records the failure in the execution report.
2. Determines whether a fallback provider is available (Part 8.2).
3. If a fallback is available, re-renders with the fallback provider.
4. If no fallback is available, marks the artifact as `rendering_failed` and continues rendering other artifacts.

## 8.2 Fallback Providers

The capability registry (Part 5.1) defines fallback providers for each capability:

| Capability | Primary (local) | Fallback (cloud) |
|------------|-----------------|------------------|
| Image generation | Stable Diffusion / FLUX | Cloud image API |
| Video generation | SVD-XT | Cloud video API |
| Voice synthesis | edge-tts | Cloud TTS API |
| Music generation | procedural | MusicGen / AudioLDM |

Fallback is automatic: the runtime falls back without human intervention, records the fallback in the execution report, and ORACLE validates the fallback output. If the fallback output is also unacceptable, the artifact is marked `rendering_failed` and the Board is notified (via ORACLE's drift report) for CIR amendment.

## 8.3 The Rendering Gap

A **rendering gap** occurs when the PKP does not specify a detail the runtime needs to render (e.g., a Scene artifact has no lighting specification for a particular shot). The runtime does not invent the missing detail (L-15); it:

1. Records the gap in the execution report.
2. Marks the artifact as `rendering_gap`.
3. Continues rendering other artifacts.
4. The gap is reported to ORACLE, which reports it to the Board for CIR amendment.

A rendering gap is not a runtime failure; it is a PKP completeness failure. The runtime reports it; the Board amends the CIR; the compiler recompiles the PKP; the runtime re-renders.

## 8.4 Graceful Degradation

The runtime follows `00` §3.7 (graceful degradation, not silent failure): every failure is reported loudly; the runtime does not silently produce broken media. An artifact marked `rendering_failed` or `rendering_gap` is not included in the final video assembly; the final video is not produced until all artifacts are successfully rendered (or the human explicitly accepts the gaps).

---

# 9. Deterministic Rendering

## 9.1 The Determinism Contract

The runtime's determinism contract (`006` L-14): given the same frozen PKP and the same provider versions, the runtime produces the same media. This is the architectural basis for:

- **Replay**: re-rendering an archived PKP produces the same media.
- **Audit**: ORACLE can verify that the media matches what the runtime should have produced.
- **Regeneration**: media can be regenerated from the PKP with the same or different providers.

## 9.2 Seed-Based Reproducibility

Every provider invocation carries a seed, recorded in the PKP's provenance (from the compiler, `008` Part 1.2) and in the execution report. The same seed + same provider version → same output, for providers that support seeding.

For providers that support seeding (most image, video, and music generation models), determinism is achieved through seed-based reproducibility.

## 9.3 The Provider Non-Determinism Fallback

For providers that are **irreducibly non-deterministic** (some cloud APIs, some TTS systems), seed-based reproducibility is insufficient. In these cases, the runtime uses the **recorded-output fallback**:

1. On first render, the runtime invokes the provider and records the specific output (the media file) in ATLAS, with the provider version and the invocation parameters.
2. On replay, the runtime does not re-invoke the provider; it reads the recorded output from ATLAS.
3. The recorded output is the deterministic result for that (PKP artifact, provider version, parameters) tuple.

This fallback ensures determinism even for non-deterministic providers, at the cost of storing the output. The stored output is the media itself (which is stored in ATLAS regardless), so the fallback adds no storage overhead beyond what the runtime already does.

This addresses the provider non-determinism gap flagged in reviews 008 and 009: the runtime's determinism does not depend on the provider's determinism; it depends on the runtime's recording of the provider's output.

## 9.4 Determinism and Provider Swapping

When a provider is swapped (e.g., Stable Diffusion replaced by a newer model), the runtime produces **different media** (the new model's output differs). This is not a determinism violation; it is a provider-version change. The new media is a new version of the production's media, recorded with the new provider version. The prior media (with the prior provider) is retained in ATLAS (L-19).

This enables the platform's model independence (`00` §3.4): the creative work (CIS, CIR, PKP) is provider-independent; the media is provider-specific but regenerable with any provider.

---

# 10. Runtime Extensibility

## 10.1 New Providers

A new provider is added by:

1. Implementing the capability interface (Part 5.1) for the new provider.
2. Registering the provider in the capability registry.
3. The runtime picks up the new provider automatically (through the registry); no runtime code changes.

New providers are governed under the Constitution (`006` Part 8.1): a new provider must satisfy the determinism requirements (Part 9) and must be behind the capability interface (not called directly).

## 10.2 New Media Types

A new media type (e.g., 3D models, interactive elements, VR scenes) is added by:

1. Defining a new rendering component (Part 3.1) for the media type.
2. Defining the component's input PKP artifact types (which requires a COM extension, `004` Part 10.2, and a PKP specification extension, `009` Part 13).
3. Registering the component in the runtime.

New media types are governed: they require COM, PKP, and runtime amendments, coordinated under the Constitution.

## 10.3 New Runtimes

A new creative runtime (e.g., a game runtime, a book runtime) does not use PROMETHEUS; it defines its own execution runtime, using the architecture in this specification (execution model, capability registry, determinism, error handling) but its own rendering components. The architecture is runtime-independent; the rendering components are runtime-specific.

---

# 11. Platform Independence

## 11.1 No OS, Cloud, or Hardware Dependencies

The runtime is platform-independent:

- **OS independence**: the runtime runs on any OS that supports its providers (local LLMs, local image models, FFmpeg). The runtime itself does not depend on a specific OS.
- **Cloud independence**: the runtime runs locally first (`00` §3.4); cloud providers are optional, behind the capability registry.
- **Hardware independence**: the runtime runs on any hardware that supports its providers (CPU, GPU, TPU). The runtime itself does not depend on specific hardware.

## 11.2 The Sovereignty Principle

The runtime's platform independence is the architectural realization of `00` §3.4 (local-first, cloud-optional) and the sovereignty principle: the creator must not be dependent on a third party's API quota, model availability, or pricing to produce their own work. The runtime's default configuration uses local providers; cloud providers are opt-in.

## 11.3 Platform Independence and the Constitution

The Constitution (`006`) does not name a platform; it names invariants (L-14, L-15, L-18). The runtime satisfies these invariants on any platform. A future runtime on a different platform (e.g., a cloud-native runtime, a mobile runtime) is constitutionally compliant if it satisfies the same invariants.

---

# 12. Governance

## 12.1 Runtime Evolution

The runtime's architecture evolves under the Constitution:

| Change type | Authority |
|--------------|-----------|
| **New rendering component** | Architectural amendment to this specification, coordinated with COM (`004`) and PKP (`009`) amendments. |
| **New capability** | Architectural amendment to this specification. |
| **Determinism policy change** | Constitutional amendment (affects L-14). |
| **Provider swap** | No amendment; providers are swapped via the registry. |

## 12.2 Compatibility

| Concern | Rule |
|---------|------|
| **Backward compatibility** | A new runtime version must be able to render an archived PKP (producing the same media, given the same provider versions). |
| **Forward compatibility** | The runtime leaves extension points (new components, new capabilities, new providers) for future media types. |
| **Cross-runtime compatibility** | The runtime's architecture (execution model, capability registry, determinism, error handling) is runtime-independent; the rendering components are cinema-specific. A future runtime uses the architecture with its own components. |

## 12.3 Constitutional Compliance

| Law | Compliance |
|-----|------------|
| L-14 (Execution Never Changes Intent) | Part 1.2, Part 6.1 (PKP is read-only). |
| L-15 (Execution Never Invents Creativity) | Part 1.2, Part 8.3 (rendering gaps reported, not invented). |
| L-18 (Knowledge Outlives Media) | Part 9 (media is regenerable from the PKP). |

---

## Architectural Rules (Restated)

This specification produced no implementation code. It architecturalizes PROMETHEUS as a pure executor with zero creative authority, governed by constitutional laws L-14, L-15, and L-18. The runtime reads the PKP, renders media through provider-abstracted components, and writes media with full provenance to ATLAS. The runtime's determinism (Part 9) is the final link in the platform's deterministic replay chain.

---

## Cross-References

| Reference | Relevance |
|-----------|-----------|
| `006` (Constitution) | L-14, L-15, L-18 govern the runtime. |
| `001` §2.1 | The PROMETHEUS pillar definition; architecturalized here. |
| `009` (PKP) | The runtime's input; the PKP-PROMETHEUS contract (Part 6.1). |
| `004` (COM) | The object model the runtime renders (executable state). |
| `011` (ORACLE) | The validator that checks the runtime's output. |
| `012` (ATLAS) | The persistence layer for the PKP, media, and execution report. |
| `00` §3.4 | Local-first, cloud-optional; the capability registry. |
| `00` §3.7 | Graceful degradation; error handling (Part 8). |
| `002` Part 7 | The Director↔Compiler↔Runtime boundary; L-15 enforcement. |

---

**End of Specification.**