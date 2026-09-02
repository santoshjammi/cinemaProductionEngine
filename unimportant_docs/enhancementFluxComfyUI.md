# Mission

You are joining an existing AI Movie Studio project that generates emotionally cinematic YouTube videos completely using local open-source AI models.

Your responsibility is NOT to build a single feature.

Your responsibility is to evolve the architecture into a reusable production pipeline that can continuously improve as better open-source models become available.

Think like a Principal AI Architect.

Do not hardcode model names, prompts, workflows, or providers.

Everything should be configurable and replaceable.

---

# Existing Vision

The project has evolved into a Local AI Movie Studio capable of producing long-form psychological storytelling videos.

Current focus:

* Psychological Cinema
* Emotional Storytelling
* Devotional Storytelling
* Multi-language content
* Local-first inference
* Open-source models only

Target hardware:

* Apple M1 Max
* 64 GB Unified Memory
* macOS
* Ollama
* Local inference only

Cloud APIs should never be required.

---

# Primary Design Principle

Every AI capability must be treated as a plug-in.

Never build logic around a specific model.

Instead, define interfaces.

Examples:

StoryModel

ImageModel

VideoModel

VoiceModel

MusicModel

ReasoningModel

PlanningModel

EmbeddingModel

Every implementation should satisfy these interfaces.

The pipeline must remain functional if a model is replaced.

---

# New Architecture

The production pipeline should become:

Idea

↓

Research

↓

Story Planning

↓

Scene Planning

↓

Shot Planning

↓

Prompt Generation

↓

Image Generation (NEW)

↓

Video Animation

↓

Voice Generation

↓

Music

↓

Editing

↓

Rendering

↓

Publishing

---

# New Image Generation Stage

A dedicated image generation stage must now become part of the production pipeline.

This stage is responsible for generating the master cinematic frame for every shot before any animation occurs.

Responsibilities include:

* Character generation
* Character consistency
* Environment generation
* Lighting
* Composition
* Camera angle
* Emotional atmosphere
* Color grading
* Style consistency

Outputs should be reusable by downstream video generation models.

---

# Image Generation Stack

Preferred UI:

ComfyUI

Preferred image model:

FLUX.1 Dev

Optional fast iteration:

FLUX.1 Schnell

The architecture must not depend specifically on FLUX.

Instead create:

ImageProvider

that can later support

* FLUX
* SDXL
* SD3
* HiDream
* Future open-source image models

without architectural changes.

---

# Prompt Generation

The project must no longer contain hardcoded prompts.

Instead implement Prompt Providers.

Every stage should request prompts from a Prompt Engine.

Example:

Story Prompt

↓

Scene Prompt

↓

Shot Prompt

↓

Image Prompt

↓

Video Prompt

↓

Voice Prompt

↓

Music Prompt

↓

Subtitle Prompt

↓

Metadata Prompt

Each prompt should be generated dynamically from structured context.

---

# Prompt Context

Prompt generation should use structured metadata.

Examples:

Story

Scene

Characters

Relationships

Mood

Emotion

Camera

Lens

Time of day

Weather

Lighting

Architecture

Movement

Dialogue

Subtext

Narrative purpose

Psychological state

Color palette

Target duration

Language

Target audience

Platform

The prompt engine should assemble prompts rather than concatenate strings.

---

# Character Memory

Introduce persistent character definitions.

Each character should have:

Unique ID

Appearance

Age

Gender

Clothing

Expressions

Emotional tendencies

Speaking style

Voice

Relationships

Historical continuity

This information must persist across scenes.

---

# Environment Memory

Likewise environments should become reusable assets.

Example:

Apartment

Therapist Office

Temple

Village

School

Bedroom

Hospital

Forest

Each environment should include reusable visual metadata.

---

# Scene Blueprint

Each scene should become structured data.

Example:

Goal

Conflict

Emotion

Narrative Function

Visual Style

Camera

Movement

Lighting

Music

Voice

Image Prompt

Video Prompt

Duration

Assets

---

# ComfyUI Integration

Integrate ComfyUI as a service within the pipeline.

Responsibilities include:

* Workflow execution
* Workflow templates
* Model selection
* LoRA selection
* ControlNet support
* IPAdapter support
* Batch generation
* Queue management
* Metadata persistence
* Output versioning

Avoid tightly coupling business logic to ComfyUI internals.

Use adapters so another backend could replace ComfyUI later.

---

# FLUX Integration

FLUX should become the default image generation implementation.

Support:

Draft mode

Production mode

High Quality mode

Seed locking

Reference images

Character consistency

Negative prompts

Resolution presets

Do not expose FLUX-specific assumptions to higher layers.

---

# Video Generation

Video generation must consume image outputs rather than raw text whenever possible.

The Image Provider should become the primary creative stage.

Video models are responsible for motion, not composition.

Video providers should be interchangeable.

---

# Voice Pipeline

Voice generation must become modular.

Current preferred direction:

Voicebox

Future support:

Kokoro

Qwen TTS

Chatterbox

Future local TTS models

Voice selection should be configuration-driven.

---

# Prompt Repository

Create a prompt repository.

Organize prompts by capability.

Example:

story/

scene/

shot/

image/

video/

voice/

music/

metadata/

translation/

Do not hardcode prompts inside source code.

---

# Configuration

Everything should become configurable.

Models

Workflow

Prompt Provider

Voice Provider

Image Provider

Video Provider

Language

Rendering presets

Aspect ratio

Quality

Output directory

Never require source code changes to swap models.

---

# Long-Term Objective

Transform this repository from a collection of scripts into a reusable Local AI Movie Studio platform.

The architecture should be:

Composable

Extensible

Model-agnostic

Prompt-driven

Configuration-first

Workflow-oriented

Future-proof

Every major subsystem should be replaceable without rewriting the rest of the pipeline.

When making design decisions, always prefer abstraction over implementation-specific logic.

Produce an implementation plan first before modifying any code.

Then identify all architectural changes required.

Then implement them incrementally while preserving backward compatibility.
