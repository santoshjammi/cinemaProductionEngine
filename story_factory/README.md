# Story Factory

> Turn a free-form synopsis into a pipeline-ready video manifest using
> three specialized LLM agents.

## Architecture

```
synopsis.txt (1-5 sentences)
    │
    ├────────────────────────┐
    ▼                        ▼
[DNA Generator]      [Context Generator]   ← run in parallel
    │                        │
    ▼                        ▼
dna.yaml (~100 tokens)  context.md (~600 words)
    │                        │
    └────────────┬───────────┘
                 ▼
         [Story Generator]              ← the only creative writing stage
                 │
                 ▼
         story.md (~1200 words, 3 acts)
                 │
                 ▼
         [Scene Structurer]
                 │
                 ▼
         master_timeline.yaml
         (11 scenes with voiceover, dialogues, music, SFX)
                 │
                 ▼
         [Timeline → Manifest adapter]
                 │
                 ▼
         manifest.yaml
                 │
                 ▼
         [existing psychological pipeline]
                 │
                 ▼
         final.mp4
```

## Why this design

From `docs/generateStoryContextDna.md`:

> Each agent receives only the output of the previous one, keeping prompts
> small and focused. ... LLMs are much more consistent when they specialize.

From `docs/superpowers/plans/createOncePublishAnywhere.md`:

> The Master Timeline becomes the "movie." Every exporter reads it.

The `master_timeline.yaml` is the platform-agnostic source of truth. The
adapter produces a manifest for the existing 16:9 pipeline. Future 9:16
(Shorts) and 1:1 (Instagram) exporters can read the same Master Timeline
without regenerating the story.

## Files

| File | Purpose |
|------|---------|
| `__init__.py` | Public API |
| `llm_client.py` | Thin LMStudio HTTP wrapper |
| `master_timeline.py` | Master Timeline schema (dataclasses + YAML) |
| `dna_generator.py` | Agent 1: synopsis → dna.yaml |
| `context_generator.py` | Agent 2: synopsis → context.md |
| `story_generator.py` | Agent 3: synopsis + DNA + context → story.md |
| `scene_structurer.py` | Agent 4: story + DNA + context → master_timeline.yaml |
| `timeline_to_manifest.py` | Adapter: Master Timeline → pipeline manifest |
| `tests/` | 18 unit tests (all passing) |

## Usage

### Full pipeline (synopsis → video)

```bash
# 1. Generate all artifacts from a synopsis
./venv/bin/python scripts/story_factory.py \
  --synopsis "A man stops initiating intimacy after marriage..." \
  --output-dir stories/EmotionalWithdrawal/fear/ew001

# 2. Run the existing video pipeline with the generated manifest
./venv/bin/python scripts/psychological_pipeline.py \
  --playbook videoContentStructure/Psychology/psychological_cinema_standard.yaml \
  --manifest stories/EmotionalWithdrawal/fear/ew001/manifest.yaml \
  --topic-dir stories/EmotionalWithdrawal/fear \
  --output-dir output/videos \
  --auto-approve
```

### Step-by-step (re-run individual stages)

```bash
# Just DNA
python scripts/story_factory.py -s "..." -o stories/... --steps dna

# DNA + context (parallel)
python scripts/story_factory.py -s "..." -o stories/... --steps dna,context

# Re-run just the scene structurer (after editing story.md)
python scripts/story_factory.py -o stories/... --steps scenes

# Force overwrite
python scripts/story_factory.py -s "..." -o stories/... --force
```

### As a library

```python
from story_factory import (
    generate_dna,
    generate_context,
    generate_story,
    structure_scenes,
    MasterTimeline,
    timeline_to_manifest,
)

synopsis = "A man stops initiating intimacy after marriage..."

dna = generate_dna(synopsis)
context = generate_context(synopsis)
story = generate_story(synopsis, dna, context)
timeline = structure_scenes(dna, context, story)

# Inspect
print(f"Title: {timeline.metadata['title']}")
print(f"Scenes: {len(timeline.scenes)}")
for s in timeline.scenes:
    print(f"  {s.scene_number}. {s.title} — {s.voiceover[:60]}...")

# Export to manifest
manifest = timeline_to_manifest(timeline)
```

## Output artifacts

| File | Size | Purpose |
|------|------|---------|
| `dna.yaml` | ~300 bytes | Story identity (id, territory, cluster, mechanism, archetype, theme, premise, ending) |
| `context.md` | ~2KB | World, characters, setting, atmosphere, visual language |
| `story.md` | ~8KB | Narrative prose, 3 acts, 7 sections, ~1200 words |
| `master_timeline.yaml` | ~17KB | Structured scenes with voiceover, dialogues, music, SFX, shot language |
| `manifest.yaml` | ~14KB | Pipeline-ready manifest (consumed by psychological_pipeline.py) |

## Master Timeline schema (v1.0)

The Master Timeline is a SUPERSET of the current pipeline's manifest format.
It includes:

- `voiceover` — the narration text
- `dialogues` — list of `{character, line, timing, emotion}` (for dialogue scenes)
- `scene_description` — the visual moment
- `visual_cause_of_emotion` — the micro-behavior
- `shot_language` — `{shot_size, lighting_key, lens_mm, depth_of_field}`
- `music_cue` — `{zone, volume}`
- `ambient_cue` — `{beat, description}`
- `sfx_layers` — for the irreversible moment
- `silence_engine` — `{silence_before, silence_after, silence_instead}`
- `vocal_fracture`, `irreversible_moment`, `pre_moment`, `post_moment`, `shows_duality`
- `export_profiles` — schema field exists, exporters TBD

## Tests

```bash
cd /Users/santosh/Desktop/projects/videoGen
./venv/bin/python -m pytest story_factory/tests/ -v --override-ini="addopts="
```

18 tests covering:
- Master Timeline: construction, save/load, dialogue preservation, computed metadata
- Timeline→Manifest adapter: scene mapping, silence flags, characters, YAML output
- LLM client: error handling for unreachable LMStudio

## Performance

| Step | Time (typical) | Output |
|------|----------------|--------|
| DNA + Context (parallel) | ~12s | dna.yaml, context.md |
| Story | ~45s | story.md |
| Scene Structurer | ~125s | master_timeline.yaml |
| Manifest adapter | <1s | manifest.yaml |
| **Total factory** | **~3 min** | 5 files |

## Versioning

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-08 | Initial factory. 4 agents (DNA, Context, Story, Scene Structurer). Master Timeline schema v1.0. Timeline→Manifest adapter. 18 tests. CLI entry point. |