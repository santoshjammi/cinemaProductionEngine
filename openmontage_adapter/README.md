# OpenMontage Adapter — Render Abstraction Layer

> **The interface between videoGen's psychological cinema engine and OpenMontage's
> orchestration layer.**

This module implements the render abstraction described in
`grammar/render_abstraction.md`. It lets videoGen act as a render backend for
OpenMontage (or any other orchestrator) while remaining provider-agnostic.

## Architecture

```
OpenMontage scene_plan  ──────►  OpenMontageAdapter  ──────►  SceneIntent
                                                              │
                                                              ▼
                                                       RenderOrchestrator
                                                              │
                                               ┌──────────────┼──────────────┐
                                               ▼              ▼              ▼
                                         SDXLLocal      FluxBackend    OpenAIBackend
                                         (free)         ($0.05)        ($0.08)
                                               │              │              │
                                               └──────────────┴──────────────┘
                                                              │
                                                              ▼
                                                         SceneAsset
```

## Files

| File | Purpose |
|------|---------|
| `__init__.py` | Public API — exports all classes |
| `scene_intent.py` | `SceneIntent` + `SceneAsset` dataclasses (the contract) |
| `render_backend.py` | `RenderBackend` abstract base class + `BackendError` |
| `orchestrator.py` | `RenderOrchestrator` (selects best backend, falls back) |
| `om_adapter.py` | `OpenMontageAdapter` (OM scene ↔ SceneIntent) |
| `videogen_adapter.py` | `manifest_to_intents()` (videoGen YAML → SceneIntents) |
| `backends/sdxl_local.py` | `SDXLLocalBackend` (the default M1 Max backend) |
| `tests/test_adapter.py` | 26 unit tests (all passing) |

## Usage

### As a library (from Python)

```python
from openmontage_adapter import (
    manifest_to_intents,
    SDXLLocalBackend,
    RenderOrchestrator,
)

# 1. Convert a videoGen manifest to SceneIntents
intents = manifest_to_intents(
    manifest_path="videoContentStructure/Psychology/EmotionalWithdrawal/VID01_template_refined.yaml",
)

# 2. Initialize the SDXL backend (default, free, local)
sdxl = SDXLLocalBackend(
    manifest_yaml="videoContentStructure/Psychology/EmotionalWithdrawal/VID01_template_refined.yaml",
    output_dir="output/videos",
)

# 3. Initialize the orchestrator
orchestrator = RenderOrchestrator(backends=[sdxl], primary="sdxl-local")

# 4. Render each scene
for intent in intents:
    asset = orchestrator.render_scene(intent)
    print(f"Scene {intent.index}: {asset.image_path} (score={asset.metadata.get('clip_score', 0):.3f})")
```

### As a pipeline flag (from CLI)

```bash
# Legacy mode (default — calls SDXLGenerator directly)
python scripts/psychological_pipeline.py \
  --playbook ... --manifest ... --auto-approve

# Adapter mode (routes through SceneIntent → Orchestrator → Backend)
python scripts/psychological_pipeline.py \
  --playbook ... --manifest ... --auto-approve --use-adapter
```

### From OpenMontage

When OpenMontage is the orchestrator, it produces scene dicts per its
`scene_plan.schema.json`. The `OpenMontageAdapter` translates those to
`SceneIntent` so videoGen can render them:

```python
from openmontage_adapter import OpenMontageAdapter, SDXLLocalBackend, RenderOrchestrator

adapter = OpenMontageAdapter(
    territory="emotional_withdrawal",
    archetype="slow_withdrawal",
    character_references={"wife": "characters/wife_hero.png"},
    character_anchors={"wife": ["woman early 30s, auburn hair, white shirt, cardigan half-off"]},
)

# om_scene is a dict from OpenMontage's scene_plan
intent = adapter.to_scene_intent(om_scene, index=8, pipeline_id="vid01")

# Render it
sdxl = SDXLLocalBackend(manifest_yaml="path/to/manifest.yaml")
orchestrator = RenderOrchestrator(backends=[sdxl])
asset = orchestrator.render_scene(intent)
```

## Adding a new backend

1. Create `backends/<name>.py`
2. Subclass `RenderBackend`:
   ```python
   class FluxBackend(RenderBackend):
       name = "flux"
       cost_per_scene_usd = 0.05
       quality_score = 0.85
       supports_img2img = True

       def can_render(self, scene_intent):
           return scene_intent.resolution in [(1024, 1024), (1024, 576)]

       def render(self, scene_intent):
           # Call fal.ai or replicate API
           # Save image to scene_intent.output_path
           return SceneAsset(
               scene_id=scene_intent.scene_id,
               image_path=scene_intent.output_path,
               backend=self.name,
               cost_usd=self.cost_per_scene_usd,
               metadata={"model": "flux-1.1-pro"},
           )
   ```
3. Export from `backends/__init__.py`
4. Register with the orchestrator: `RenderOrchestrator(backends=[sdxl, flux])`

## Tests

```bash
cd /Users/santosh/Desktop/projects/videoGen
./venv/bin/python -m pytest openmontage_adapter/tests/test_adapter.py -v --override-ini="addopts="
```

26 tests covering:
- SceneIntent / SceneAsset dataclasses
- Mock backend + BackendError
- Orchestrator: primary selection, fallback, irreversible moment quality, budget, hint override
- OpenMontageAdapter: OM→Intent, Intent→OM, asset manifest, emotion/action translation
- videogen_adapter: manifest_to_intents, break words, emphasis words
- SDXLLocalBackend: init, can_render, intent_to_scene_dict

## Versioning

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-07 | Initial adapter. SDXL local backend. 26 tests. Pipeline integration via --use-adapter flag. |