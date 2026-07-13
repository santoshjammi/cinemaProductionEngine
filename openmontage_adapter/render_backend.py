"""RenderBackend — the interface every render provider must implement.

The render abstraction layer (see ``grammar/render_abstraction.md``) defines
``RenderBackend`` as the contract between the orchestrator and providers.

A backend takes a ``SceneIntent`` and produces a ``SceneAsset``. The
orchestrator doesn't know or care whether the backend is SDXL, Flux,
OpenAI, Runway, Kling, or a human artist.

To add a new provider:
1. Subclass ``RenderBackend``
2. Implement ``can_render`` and ``render``
3. Register it with the orchestrator
4. (Optional) Implement ``estimate_cost`` for cost-aware selection
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar

from .scene_intent import SceneAsset, SceneIntent


class BackendError(Exception):
    """Raised when a render backend fails to produce an asset.

    The orchestrator catches this and falls back to the next backend.
    The error message should describe what went wrong (timeout, OOM, API
    error, etc.) so it can be logged for debugging.
    """

    def __init__(self, backend_name: str, scene_id: str, message: str, cause: Exception | None = None):
        self.backend_name = backend_name
        self.scene_id = scene_id
        self.message = message
        self.cause = cause
        super().__init__(f"[{backend_name}] scene {scene_id}: {message}")


class RenderBackend(ABC):
    """The interface every render provider must implement.

    Subclasses must define:
    - ``name``: a unique identifier (e.g. "sdxl-local", "flux", "openai")
    - ``cost_per_scene_usd``: the average cost per scene (for selection)
    - ``can_render``: return True if this backend can produce this scene
    - ``render``: do the actual rendering
    - ``estimate_cost``: estimate cost before rendering (optional but recommended)
    """

    # Class-level metadata
    name: ClassVar[str] = ""
    cost_per_scene_usd: ClassVar[float] = 0.0
    quality_score: ClassVar[float] = 0.7  # 0-1, used for "best quality" selection
    supports_img2img: ClassVar[bool] = False
    supports_character_consistency: ClassVar[bool] = False
    max_resolution: ClassVar[tuple] = (1024, 1024)

    @abstractmethod
    def can_render(self, scene_intent: SceneIntent) -> bool:
        """Return True if this backend can produce this scene.

        Some scenes may require capabilities the backend doesn't have
        (specific aspect ratio, character consistency, etc.). The
        orchestrator calls this before invoking ``render``.

        Examples:
        - SDXL local: always True
        - Flux: True if resolution is in (1024,1024) or (1024,576)
        - Stock footage: True only if scene has stock_search_terms
        """
        pass

    @abstractmethod
    def render(self, scene_intent: SceneIntent) -> SceneAsset:
        """Render the scene. Returns a SceneAsset with the image path.

        Implementations should:
        1. Build the actual provider prompt from SceneIntent
        2. Call the provider's API (or local model)
        3. Save the image to scene_intent.output_path
        4. Return SceneAsset with metadata (cost, model version, seed, etc.)

        Raise ``BackendError`` on failure (the orchestrator will fall back).
        """
        pass

    def estimate_cost(self, scene_intent: SceneIntent) -> float:
        """Return the estimated cost in USD for this scene.

        Default implementation returns ``cost_per_scene_usd``. Override for
        backends with variable pricing (e.g. per-token, per-step).
        """
        return self.cost_per_scene_usd

    def supports_resolution(self, resolution: tuple) -> bool:
        """Return True if this backend supports the given resolution."""
        return resolution[0] <= self.max_resolution[0] and resolution[1] <= self.max_resolution[1]

    def __repr__(self) -> str:
        return f"<RenderBackend name={self.name!r} cost=${self.cost_per_scene_usd:.4f} quality={self.quality_score:.2f}>"
