# Render Abstraction Layer — v1.0

> **The interface between scene blueprints and render backends.**
>
> A render backend takes a `SceneIntent` and produces a `SceneAsset`.
> The orchestrator (videoGen's pipeline) doesn't care which backend does the work.
> This is the abstraction that lets you swap SDXL for Flux, OpenAI, Runway, Kling, or
> any future provider without changing the scene blueprint.

---

## Why an abstraction layer

Every AI video pipeline that fails to scale fails the same way: it hardcodes the
provider. The pipeline becomes "the SDXL pipeline" or "the OpenAI pipeline" and
swapping means rewriting.

The abstraction:
- The pipeline reads `SceneIntent` (semantic description)
- The pipeline calls `backend.render(scene_intent) -> SceneAsset`
- The pipeline doesn't know whether the backend is SDXL, Flux, OpenAI, Runway, or a human artist

This is the standard for production systems. Your render backend is replaceable.

---

## The interface

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SceneIntent:
    """The semantic description of a scene to be rendered.

    This is the render-independent description. Every backend takes
    this and produces a SceneAsset.
    """
    scene_id: str
    emotional_state: str              # restrained, numb, grief, etc.
    visual_symbolism: list[str]       # [physical_distance, low_light, ...]
    camera_language: dict             # {shot_size, movement, framing, lighting_key, ...}
    duration_seconds: float

    # Render hints (provider-specific but expressed semantically)
    style_anchor: str                 # "cinematic photorealism, 35mm film grain"
    negative_prompts: list[str]
    micro_behaviors: list[str]        # unfinished_movements, hesitation, ...
    environmental_imperfections: list[str]

    # Character consistency
    character_references: list[Path]  # hero image paths for img2img
    character_anchors: list[str]      # condensed visual descriptors

    # Output specs
    resolution: tuple                # (width, height)
    output_path: Path


@dataclass
class SceneAsset:
    """The rendered output of a scene."""
    scene_id: str
    image_path: Path                  # rendered still frame
    duration_seconds: float
    metadata: dict                    # provider-specific (model, seed, cost, etc.)


class RenderBackend(ABC):
    """The interface every render provider must implement."""

    name: str
    cost_per_scene_usd: float

    @abstractmethod
    def can_render(self, scene_intent: SceneIntent) -> bool:
        """Return True if this backend can produce this scene.

        Some scenes may require capabilities the backend doesn't have
        (e.g. specific aspect ratio, character consistency, etc.).
        """
        pass

    @abstractmethod
    def render(self, scene_intent: SceneIntent) -> SceneAsset:
        """Render the scene. Returns a SceneAsset with the image path.

        Implementations should:
        - Build the actual provider prompt from SceneIntent
        - Call the provider's API (or local model)
        - Save the image to scene_intent.output_path
        - Return SceneAsset with metadata (cost, model version, etc.)
        """
        pass

    @abstractmethod
    def estimate_cost(self, scene_intent: SceneIntent) -> float:
        """Return the estimated cost in USD for this scene."""
        pass
```

---

## The orchestrator

```python
class RenderOrchestrator:
    """Selects the best backend for each scene, falls back if needed."""

    def __init__(self, backends: list[RenderBackend], primary: str = None):
        self.backends = {b.name: b for b in backends}
        self.primary = primary or backends[0].name

    def render_scene(self, scene_intent: SceneIntent, backend_name: str = None) -> SceneAsset:
        # Try the requested backend first
        backend_name = backend_name or self.primary
        backend = self.backends[backend_name]

        if backend.can_render(scene_intent):
            try:
                return backend.render(scene_intent)
            except Exception as e:
                logger.warning(f"Backend {backend_name} failed: {e}. Falling back.")

        # Fall back to other backends in order
        for name, b in self.backends.items():
            if name == backend_name:
                continue
            if b.can_render(scene_intent):
                try:
                    return b.render(scene_intent)
                except Exception as e:
                    logger.warning(f"Backend {name} failed: {e}. Trying next.")
                    continue

        raise RuntimeError(f"No backend could render scene {scene_intent.scene_id}")
```

---

## Built-in backends

### SDXLLocalBackend (the current M1 Max implementation)

```python
class SDXLLocalBackend(RenderBackend):
    name = "sdxl-local"
    cost_per_scene_usd = 0.0  # free, local

    def can_render(self, scene_intent):
        return True  # can render anything

    def render(self, scene_intent):
        from scripts.generate_from_yaml import SDXLGenerator
        # Build the SDXL prompt from SceneIntent
        # Generate 4 candidates
        # Score with CLIP
        # Return the best
        ...
```

### FluxBackend (future)

```python
class FluxBackend(RenderBackend):
    name = "flux"
    cost_per_scene_usd = 0.05

    def can_render(self, scene_intent):
        return scene_intent.resolution in [(1024, 1024), (1024, 576)]

    def render(self, scene_intent):
        # Call fal.ai or replicate API
        ...
```

### OpenAIBackend (future)

```python
class OpenAIBackend(RenderBackend):
    name = "openai"
    cost_per_scene_usd = 0.08

    def can_render(self, scene_intent):
        return scene_intent.resolution in [(1024, 1024), (1024, 576), (1536, 1024)]

    def render(self, scene_intent):
        # Call gpt-image-1
        ...
```

### StockFootageBackend (free real footage)

```python
class StockFootageBackend(RenderBackend):
    name = "stock-footage"
    cost_per_scene_usd = 0.0

    def can_render(self, scene_intent):
        # Only works for scenes that can be matched to stock footage
        # (e.g. "couple at dinner table", "man driving in car")
        return bool(scene_intent.stock_search_terms)

    def render(self, scene_intent):
        # Search Pexels/Unsplash/Pixabay for matching clip
        # Download and save as the scene image
        ...
```

---

## The OpenMontage adapter

OpenMontage has its own scene description format. The adapter translates between
SceneIntent and OpenMontage's format.

```python
class OpenMontageAdapter:
    """Translates SceneIntent to OpenMontage's scene description."""

    def to_openmontage_scene(self, scene_intent: SceneIntent) -> dict:
        return {
            "scene_id": scene_intent.scene_id,
            "description": self._build_description(scene_intent),
            "duration_seconds": scene_intent.duration_seconds,
            "camera": scene_intent.camera_language,
            "lighting": scene_intent.camera_language.get("lighting_key"),
            "mood": scene_intent.emotional_state,
            "assets_required": ["image"],
            "render_runtime": "remotion",  # or "hyperframes"
        }

    def _build_description(self, scene_intent):
        # Translate semantic tokens to OpenMontage-style description
        parts = [scene_intent.style_anchor]
        for token in scene_intent.visual_symbolism:
            parts.append(self._translate_symbol(token))
        return ", ".join(parts)
```

---

## How the orchestrator chooses a backend

Default: use the primary backend (SDXL local, free).
Override per-scene: `backend: flux` in the scene blueprint.
Fallback chain: if primary fails, try backends in order.

The orchestrator also considers:
- **Cost budget**: if the video has a max budget, use cheaper backends
- **Quality requirements**: certain scenes (irreversible moment) get the highest quality backend
- **Character consistency**: if the scene has a character reference, use a backend that supports img2img

```python
def select_backend(scene_intent, available_backends, budget_remaining):
    # Irreversible moment gets the best backend
    if scene_intent.is_irreversible_moment:
        for backend in sorted(available_backends, key=lambda b: -b.quality_score):
            if backend.can_render(scene_intent):
                return backend

    # Otherwise, prefer local (free)
    for backend in available_backends:
        if backend.cost_per_scene_usd == 0.0 and backend.can_render(scene_intent):
            return backend

    # Else, cheapest
    for backend in sorted(available_backends, key=lambda b: b.cost_per_scene_usd):
        if backend.can_render(scene_intent):
            return backend
```

---

## Versioning

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-07 | Initial abstraction layer. SDXL is the only implemented backend. Flux/OpenAI/StockFootage are stubbed. |

When you add a new backend, you implement the `RenderBackend` interface. The orchestrator
and the pipeline don't change.
