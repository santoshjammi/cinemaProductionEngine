# Movie OS — Local AI Movie Operating System

> A reusable, capability-centric production pipeline for cinematic
> psychological storytelling. Every AI capability is a plug-in.

## Architecture

```
Domain Model          (Pydantic schemas — the vocabulary)
    ↓
Capability Registry   (the abstraction — "what can I ask for?")
    ↓
Provider              (the impl — "how is it done?")
    ↓
Workflow              (ComfyUI / programmatic — "what's the recipe?")
    ↓
Model                 (FLUX, SDXL, EdgeTTS, etc. — "what runs it?")
    ↓
Multi-Agent Layer     (Phase 8 — LangGraph orchestration)
    ↓
Asset Store           (Phase 9 — SQLite + embeddings + versioning)
```

See `docs/enhancementFluxComfyUI.md` for the full design rationale.

## Phase 0 — Foundation (this phase)

Phase 0 ships the **vocabulary** and the **abstraction layer** — the
foundation everything else builds on. No providers, no workflows, no
models. Just the schemas and the registry.

### What's in Phase 0

| Module | Purpose |
|--------|---------|
| `domain/story.py` | Story → Act → Sequence → Scene → Shot → Frame (Pydantic) |
| `domain/character.py` | CharacterDNA — 9 facets (physical, psychological, speech, voice, wardrobe, expressions, relationships, history, arc) |
| `domain/environment.py` | EnvironmentDNA — 8 facets (lighting, palette, ambience, camera positions, variants) |
| `domain/asset.py` | Asset, Render, Reference — the output objects |
| `domain/prompt.py` | PromptTemplate — structured prompts with metadata, variables, constraints, examples |
| `capabilities/base.py` | Capability ABC + 7 Intent/Result types |
| `capabilities/registry.py` | CapabilityRegistry — the central dispatcher |
| `capabilities/image.py` | ImageCapability (with provider lookup) |
| `capabilities/video.py` | VideoCapability (stub) |
| `capabilities/voice.py` | VoiceCapability (stub) |
| `capabilities/music.py` | MusicCapability (stub) |
| `capabilities/story.py` | StoryCapability (stub) |
| `capabilities/translation.py` | TranslationCapability (stub) |
| `capabilities/research.py` | ResearchCapability (stub) |
| `prompts/loader.py` | Load/save PromptTemplate from YAML |
| `prompts/builder.py` | Build context from domain objects |
| `prompts/optimizer.py` | Tune the prompt (stub in Phase 0) |
| `prompts/validator.py` | Check constraints |
| `prompts/renderer.py` | End-to-end render |
| `prompts/image/cinematic.yaml` | Example prompt template |

### What's in Phase 1 (Configuration backbone)

| Module | Purpose |
|--------|---------|
| `config/schema.py` | Pydantic schema — `MovieOSConfig` with all sections |
| `config/loader.py` | `load_config(path)`, `load_config_from_dict()`, `write_default_config()` |
| `config/defaults.py` | Built-in defaults |
| `config/examples/movie_os.yaml` | Fully-commented example |
| `cli.py` | CLI entry point with `config show/validate/init` and `capabilities list` |
| `__main__.py` | `python -m movie_os` entry point |
| Updates to `capabilities/registry.py` | `CapabilityRegistry.from_config()` actually populates from config |

### What's in Phase 2 (Prompt system expansion)

| File | Purpose |
|------|---------|
| `prompts/repository.py` | `PromptRepository` — central index, lookup by id/capability/model/tag |
| `prompts/story/dna.yaml` | Story DNA generator prompt (extracted from `story_factory/dna_generator.py`) |
| `prompts/story/context.yaml` | Story context generator prompt (extracted from `story_factory/context_generator.py`) |
| `prompts/story/narrative.yaml` | Story narrative generator prompt (extracted from `story_factory/story_generator.py`) |
| `prompts/story/scenes.yaml` | Scene structurer prompt (extracted from `story_factory/scene_structurer.py`) |
| `prompts/story/refiner.yaml` | Emotional refinement prompt (extracted from `psychological_pipeline.py`) |
| `prompts/story/narrative-architect.yaml` | The big playbook-driven prompt (extracted from `psychological_pipeline.py`) |
| `prompts/image/portrait.yaml` | Character portrait hero image prompt |
| `prompts/image/environment.yaml` | Environment hero image prompt |
| `prompts/voice/narration-prosody.yaml` | TTS prosody hints per scene |
| `prompts/metadata/title.yaml` | YouTube title generator |
| `prompts/metadata/description.yaml` | YouTube description generator |
| `prompts/metadata/thumbnail.yaml` | Thumbnail prompt generator |

13 prompt templates total, all loaded by the default `PromptRepository`.

### What's NOT yet done

| Phase | What |
|-------|------|
| **Phase 7** | Scene → Shot → Frame hierarchy at full granularity |
| **Phase 8** | Multi-agent orchestration (in parallel) |
| **Phase 9** | Asset & Knowledge Management |

### What's in Phase 6 (Character & Environment Memory)

| File | Purpose |
|------|---------|
| `data_layer/storage.py` | `EntityStorage` — filesystem CRUD (YAML manifest + reference images) |
| `data_layer/character_registry.py` | `CharacterRegistry` — persistent CharacterDNA store with hero image lookup |
| `data_layer/environment_registry.py` | `EnvironmentRegistry` — persistent EnvironmentDNA store with hero + variant images |
| `data_layer/seeds.py` | Default characters (Ethan Morrison, Claire Morrison) + environments (bedroom) |
| `data_layer/__init__.py` | Public API + `get_character_registry()` / `get_environment_registry()` |
| Updates to `cli.py` | `character list/show/delete` + `environment list/show/delete` commands |

Characters are now **persistent across stories**. A new story can reference `ethan_morrison` by key, the registry looks up his full DNA + hero image, and the ImageProvider uses IPAdapter for visual consistency. The same pattern applies to environments.

CLI usage:

```bash
# Seed the default emotional_withdrawal characters
./venv/bin/python -c "from movie_os.data_layer import *; seed_default_characters(get_character_registry()); seed_default_environments(get_environment_registry())"

# List all characters
./venv/bin/python -m movie_os character list

# Show a character's full DNA
./venv/bin/python -m movie_os character show ethan_morrison

# List environments
./venv/bin/python -m movie_os environment list
```

### What's in Phase 5 (ComfyUI + FLUX)

| File | Purpose |
|------|---------|
| `workflows/comfyui_client.py` | `ComfyUIClient` — HTTP client for ComfyUI's REST API (submit, poll, download) |
| `workflows/__init__.py` | `load_workflow()`, `list_workflows()`, `fill_placeholders()` |
| `workflows/flux/flux_txt2img.json` | Basic FLUX text-to-image workflow |
| `workflows/flux/flux_img2img.json` | FLUX with reference image (img2img) |
| `workflows/flux/flux_with_ipadapter.json` | FLUX with IPAdapter (character consistency) |
| `workflows/flux/flux_with_lora.json` | FLUX + LoRA (high quality mode) |
| `providers/image/flux_comfyui.py` | `FluxComfyUIProvider` — implements `ImageProvider` ABC, dispatches to ComfyUI |
| Updates to `providers/registry.py` | `flux_comfyui` registered as a built-in |

3 quality modes supported:
- **draft** — FLUX Schnell (4 steps, fast iteration)
- **production** — FLUX Dev (20 steps, balanced) [default]
- **high_quality** — FLUX Dev + LoRA (28 steps, best)

To enable FLUX:
1. Install ComfyUI: https://github.com/comfyanonymous/ComfyUI
2. Download a FLUX checkpoint (e.g., `flux1-dev-fp8.safetensors`)
3. Start ComfyUI: `python main.py --port 8188`
4. Set `image.flux_comfyui.enabled: true` in `config/movie_os.yaml`
5. Switch `image.default: flux_comfyui` to use it

### What's in Phase 3+4 (Provider ABCs + wrapping)

| File | Purpose |
|------|---------|
| `providers/base.py` | 8 Provider ABCs (Image, Video, Voice, Music, SFX, Story, Translation, Research) + `make_asset()` and `run_sync()` helpers |
| `providers/registry.py` | Provider registry — `(capability, label) -> Provider` index |
| `providers/image/sdxl_local.py` | `SDXLLocalProvider` — wraps the legacy `SDXLGenerator` from `scripts/generate_from_yaml.py` |
| `providers/voice/edge_tts.py` | `EdgeTTSProvider` — wraps the `TTSService` from `backend/app/services/tts_service.py` |
| `providers/music/procedural.py` | `ProceduralMusicProvider` — wraps `MusicGenerator` and `DramaticStingGenerator` from `psychological_pipeline.py` |
| `providers/sfx/procedural.py` | `ProceduralSFXProvider` — wraps `AmbientSFXGenerator` from `psychological_pipeline.py` |
| `providers/story/lmstudio.py` | `LMStudioStoryProvider` — wraps the story_factory's 4 functions (DNA, context, narrative, scenes) |

5 built-in providers, all auto-registered on import. The capability
registry's `from_config()` works end-to-end: load a config, the
built-in factory wires up the providers, and capabilities have
real working backends.

### Quick start

```python
from movie_os.domain import (
    Story, Act, Sequence, Scene, Shot, Frame,
    CharacterDNA, EnvironmentDNA, PromptTemplate,
)
from movie_os.capabilities import (
    CapabilityRegistry, ImageCapability, ImageIntent,
)
from movie_os.prompts import (
    load_prompt_template, PromptBuilder, PromptRenderer,
)

# 1. Build a domain object (Story)
story = Story(
    title="The Night He Stopped Reaching",
    logline="A man stops reaching for his wife.",
    territory="emotional_withdrawal",
    ending="quiet_realization",
)
act = Act(number=1, title="Observation", viewer_response="I know this feeling.")
story.acts.append(act)
seq = Sequence(title="The night it happens")
act.sequences.append(seq)
scene = Scene(
    number=1, title="The Frozen Hand", phase="hook", beat="opening_hook",
    scene_description="He lies in bed, hand hovering above her shoulder.",
    emotional_state="tense_restraint", energy=3,
    shot_language={"shot_size": "close-up", "lens_mm": 50, "lighting_key": "practical_lighting"},
    characters_present=["husband"],
    target_duration_seconds=15.0,
)
seq.scenes.append(scene)

# 2. Load a prompt template
template = load_prompt_template("movie_os/prompts/image/cinematic.yaml")

# 3. Build context from the scene
renderer = PromptRenderer(template)
rendered, validation = renderer.render_from_scene(scene)
print(rendered)
print(f"Validation: {validation.passed}")

# 4. Register a capability (when you have a provider in Phase 4+)
registry = CapabilityRegistry()
# registry.register(ImageCapability(provider=my_flux_provider))
# result = await registry.get("image").execute(ImageIntent(prompt=rendered))
```

### Tests

```bash
cd /Users/santosh/Desktop/projects/videoGen
./venv/bin/python -m pytest movie_os/tests/ -v --override-ini="addopts="
```

36 tests covering:
- Domain model instantiation + JSON roundtrip
- CapabilityRegistry register/get/list/has/unregister
- Capability stubs can_handle correctly and raise NotImplementedError on execute
- PromptTemplate load, validate, render, default-filling, undeclared-variable detection
- PromptBuilder builds context from Scene objects
- PromptValidator catches constraint violations
- PromptRenderer end-to-end pipeline
- Whole-system integration

### Backward compatibility

Phase 0 does NOT break anything. The existing code keeps working:
- `story_factory/` — unchanged
- `openmontage_adapter/` — unchanged
- `scripts/psychological_pipeline.py` — unchanged

The new `movie_os/` is additive. Phases 1-4 will gradually wrap the
existing code into the new abstractions (with the old paths becoming
thin shims). Phases 5+ add new capabilities.

## Versioning

| Version | Date | Change |
|---------|------|--------|
| 0.1.0 | 2026-07-08 | Phase 0 — domain model + capability registry + prompt system. 36 tests passing. |
| 0.2.0 | 2026-07-08 | Phase 1 — configuration backbone. 33 new tests. MovieOSConfig + CLI. |
| 0.3.0 | 2026-07-08 | Phase 2 — prompt system expansion. 77 new tests. 13 prompt templates in the repository. |
| 0.4.0 | 2026-07-08 | Phase 3+4 — provider ABCs + wrap existing. 32 new tests. 5 built-in providers (SDXL, EdgeTTS, Procedural Music/SFX, LMStudio Story). |
| 0.5.0 | 2026-07-08 | Phase 5 — ComfyUI + FLUX. 32 new tests. ComfyUIClient, 4 FLUX workflow templates, FluxComfyUIProvider with 3 quality modes. |
| 0.6.0 | 2026-07-08 | Phase 6 — Character & Environment Memory. 30 new tests. Persistent CharacterRegistry + EnvironmentRegistry with hero images, default seeds (Ethan, Claire, bedroom). |
| 0.7.0 | 2026-07-08 | Phase 7+8+9 — Shot/Frame hierarchy (29 tests), Multi-Agent LangGraph orchestration (25 tests, 8 agents: Movie/Story/Visual/Voice/Music/SFX/QA/Publishing, SQLite checkpointing), Asset & Knowledge Store (42 tests, SQLite + sqlite-vec + sentence-transformers, tag + semantic search, full version history + rollback, migration from CharacterRegistry/EnvironmentRegistry). **399 tests pass.** |
| 0.8.0 | 2026-07-08 | Phase 10+ — Asset-aware agents (visual/voice/music/sfx auto-register outputs in AssetStore with auto-derived tags), real FLUX via ComfyUI in the visual agent (4-step draft / 20-step production), ffmpeg compositor with Ken Burns + audio mixing (9 tests), full 9-scene end-to-end test (51s video, 40 assets, real EdgeTTS voice + procedural music + FLUX images). **408 tests pass.** |
