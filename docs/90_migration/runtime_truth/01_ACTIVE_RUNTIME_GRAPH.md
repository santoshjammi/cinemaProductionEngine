# 01_ACTIVE_RUNTIME_GRAPH

## Primary finding

**Closest currently executable complete-video command:**

```bash
python run_space_between_us.py
```

### Why this is the best evidence-backed answer

This script explicitly executes:

1. **Genesis2** creative analysis
2. **PKP → brief bridge**
3. **PrometheusPipeline** rendering stages
4. **final run artifacts** written under `output/space_between_us/`

Evidence:
- `run_space_between_us.py:39-145`
- `movie_os/genesis2/engine.py:31-149`
- `movie_os/genesis2/bridge.py:1-37` and `run_space_between_us.py:86-125`
- `movie_os/prometheus/pipeline.py:48-333`
- `movie_os/prometheus/stages/storyboard_stage.py:12-64`
- `movie_os/prometheus/stages/image_stage.py:19-217`
- `movie_os/prometheus/stages/voice_stage.py:115-304`
- `movie_os/prometheus/stages/music_stage.py:17-107`
- `movie_os/prometheus/stages/film_stage.py:165-328`

## Runtime graph

```text
python run_space_between_us.py
    ↓
movie_os.genesis2.Genesis2Engine
    ↓
movie_os.genesis2.phases.PHASE_CLASSES (12 phases)
    ↓
movie_os.genesis2.bridge.Genesis2Bridge
    ↓
movie_os.prometheus.pipeline.PrometheusPipeline
    ↓
StoryboardStage
    ↓
ImageGenerationStage
    ↓
VoiceStage
    ↓
MusicStage
    ↓
EditingStage
    ↓
FilmStage
    ↓
final MP4 + run JSON artifacts
```

## File-by-file execution trace

### 1) Entry command

`run_space_between_us.py`

- hardcodes synopsis and constraints
- builds `LLMConfig(provider="ollama", model="deepseek-coder-v2:latest")`
- instantiates `Genesis2Engine`
- saves `production_knowledge_package.json`
- converts PKP to brief with `Genesis2Bridge`
- instantiates `PrometheusPipeline`
- executes pipeline and writes `prometheus_result.json`

### 2) GENESIS2

`movie_os/genesis2/engine.py`

- iterates over `PHASE_CLASSES`
- each phase returns `PhaseResult`
- maps outputs back into `ProductionKnowledgePackage`
- optional `save_package()` persists PKP and phase JSONs

`movie_os/genesis2/phases/*.py`

- actual creative phases are the active narrative compiler path
- visible active set in `PHASE_CLASSES` is the 12-phase modern engine

### 3) Bridge

`movie_os/genesis2/bridge.py`

- converts PKP into the downstream `brief` dict
- this brief becomes the runtime contract for Prometheus stages

### 4) PROMETHEUS pipeline

`movie_os/prometheus/pipeline.py`

- `_create_stages()` instantiates exactly:
  - `StoryboardStage`
  - `ImageGenerationStage`
  - `VoiceStage`
  - `MusicStage`
  - `EditingStage`
  - `FilmStage`
- `execute()` runs them in order and accumulates artifacts
- `_build_result()` selects the final output path from the last film artifact

### 5) Stage responsibilities

- `movie_os/prometheus/stages/storyboard_stage.py` — storyboard artifacts
- `movie_os/prometheus/stages/image_stage.py` — FLUX/ComfyUI image generation
- `movie_os/prometheus/stages/voice_stage.py` — edge-tts dialogue audio
- `movie_os/prometheus/stages/music_stage.py` — background music selection/copy
- `movie_os/prometheus/stages/editing_stage.py` — timeline/edit assembly helper (present in pipeline graph)
- `movie_os/prometheus/stages/film_stage.py` — audio mix + Ken Burns scene render + final concatenation

## What the command actually reaches downstream

### Active runtime outputs observed in code

- `output/space_between_us/production_knowledge_package.json`
- `output/space_between_us/movie_os_brief.json`
- `output/space_between_us/prometheus_result.json`
- `output/prometheus/storyboard/*`
- `output/prometheus/images/*`
- `output/prometheus/voice/*`
- `output/prometheus/music/*`
- `output/prometheus/films/*`

### Final-video boundary

The final film stage writes to:

- `output/prometheus/films/{clean_name}_final.mp4`

Evidence:
- `movie_os/prometheus/stages/film_stage.py:182-241`

## Other plausible runners, but not primary

### `run_production.py`

A broader orchestrator that chains:
- Genesis2
- GENESIS3
- PrometheusEngine

Evidence:
- `run_production.py:34-37`
- `run_production.py:218-410`

This is a more generic path, but the codebase shows stronger direct video assembly evidence in `run_space_between_us.py` + `PrometheusPipeline` + `FilmStage`.

### `render_space_between_us.py`

A legacy/direct FFmpeg path that also assembles video.

Evidence:
- `render_space_between_us.py:1-31` and downstream helper functions

It is a valid alternate render path, but the main evidence-backed end-to-end runtime today is the `run_space_between_us.py` → Genesis2 → Prometheus pipeline chain.

## Step existence check

| Step | Status | Evidence |
|---|---|---|
| ENTRYPOINT | PASS | `run_space_between_us.py` |
| GENESIS | PASS | `movie_os.genesis2.engine.Genesis2Engine` |
| EPISODE / STORY ARTIFACTS | PASS | `Genesis2Bridge.to_brief()` + `brief` dict |
| PKP / HANDOFF | PASS | `production_knowledge_package.json` + bridge |
| PROMETHEUS | PASS | `PrometheusPipeline.execute()` |
| IMAGE | PASS | `ImageGenerationStage` |
| VOICE | PASS | `VoiceStage` |
| MOTION / LIP SYNC | PARTIAL | video assembly exists, but no dedicated lip-sync engine is evidenced in this path |
| MUSIC / AUDIO | PASS | `MusicStage` + `FilmStage.mix_scene_audio()` |
| ASSEMBLY | PASS | `FilmStage.render_scene_video()` + final concat |
| FINAL VIDEO | PASS | `output/prometheus/films/*_final.mp4` |
```