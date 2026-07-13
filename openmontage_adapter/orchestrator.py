"""RenderOrchestrator — selects the best backend for each scene, falls back on failure.

The orchestrator is the brains of the render layer. It:
1. Takes a SceneIntent
2. Picks the best available backend (cost-aware, quality-aware, capability-aware)
3. Calls backend.render()
4. If the backend fails, falls back to the next one
5. Returns the SceneAsset

Selection rules (in priority order):
1. If the scene has `backend_hint`, use that backend
2. If the scene is `irreversible_moment`, use the highest-quality backend
3. If `cost_priority == "free"`, use the cheapest backend
4. Otherwise, use the primary backend (default: sdxl-local)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

from .render_backend import BackendError, RenderBackend
from .scene_intent import SceneAsset, SceneIntent

logger = logging.getLogger("orchestrator")


@dataclass
class RenderDecision:
    """Records which backend was chosen and why. Useful for debugging."""

    scene_id: str
    chosen_backend: str
    reason: str
    tried_backends: list[str] = field(default_factory=list)
    fallback_used: bool = False
    cost_estimate: float = 0.0


class RenderOrchestrator:
    """Selects the best backend for each scene, falls back if needed.

    Usage:

        from openmontage_adapter import (
            RenderOrchestrator, SDXLLocalBackend, SceneIntent,
        )

        sdxl = SDXLLocalBackend(manifest_yaml="path/to/manifest.yaml")
        orchestrator = RenderOrchestrator(backends=[sdxl], primary="sdxl-local")

        intent = SceneIntent(scene_id="vid01-08", ...)
        asset = orchestrator.render_scene(intent)
    """

    def __init__(
        self,
        backends: list[RenderBackend],
        primary: str | None = None,
        max_budget_usd: float | None = None,
    ):
        """Initialize the orchestrator.

        Args:
            backends: List of available RenderBackend instances
            primary: Name of the default backend (defaults to the first)
            max_budget_usd: If set, the orchestrator will avoid backends
                that would exceed this budget for the remaining scenes
        """
        if not backends:
            raise ValueError("Orchestrator requires at least one backend")
        self.backends: dict[str, RenderBackend] = {b.name: b for b in backends}
        self.primary = primary or backends[0].name
        if self.primary not in self.backends:
            raise ValueError(f"Primary backend '{self.primary}' not in backends list")
        self.max_budget_usd = max_budget_usd
        self._spent: float = 0.0
        self._decisions: list[RenderDecision] = []

    def render_scene(
        self,
        scene_intent: SceneIntent,
        backend_name: str | None = None,
    ) -> SceneAsset:
        """Render a scene using the best available backend.

        Args:
            scene_intent: The scene to render
            backend_name: Override the backend choice (use this specific backend)

        Returns:
            A SceneAsset with the rendered image

        Raises:
            BackendError: If all backends fail
        """
        decision = RenderDecision(
            scene_id=scene_intent.scene_id,
            chosen_backend="",
            reason="",
        )

        # 1. Determine the backend selection order
        backend_order = self._select_backend_order(scene_intent, backend_name)
        decision.tried_backends = list(backend_order)

        # 2. Try each backend in order
        for name in backend_order:
            backend = self.backends[name]
            if not backend.can_render(scene_intent):
                decision.reason = f"{name} cannot render this scene"
                logger.debug("Backend %s cannot render scene %s", name, scene_intent.scene_id)
                continue

            # Check budget
            cost = backend.estimate_cost(scene_intent)
            if self.max_budget_usd is not None and self._spent + cost > self.max_budget_usd:
                decision.reason = f"{name} would exceed budget (${self._spent + cost:.2f} > ${self.max_budget_usd})"
                logger.debug("Backend %s exceeds budget for scene %s", name, scene_intent.scene_id)
                continue

            # Try to render
            decision.chosen_backend = name
            decision.cost_estimate = cost
            try:
                logger.info(
                    "Rendering scene %s with backend %s (cost=$%.4f)",
                    scene_intent.scene_id, name, cost,
                )
                asset = backend.render(scene_intent)
                self._spent += asset.cost_usd
                decision.reason = "success"
                self._decisions.append(decision)
                return asset
            except BackendError as e:
                decision.fallback_used = True
                decision.reason = f"{name} failed: {e.message}"
                logger.warning("Backend %s failed for scene %s: %s. Falling back.", name, scene_intent.scene_id, e.message)
                continue
            except Exception as e:
                decision.fallback_used = True
                decision.reason = f"{name} raised {type(e).__name__}: {e}"
                logger.warning("Backend %s raised for scene %s: %s. Falling back.", name, scene_intent.scene_id, e)
                continue

        # All backends failed
        self._decisions.append(decision)
        raise BackendError(
            "orchestrator",
            scene_intent.scene_id,
            f"All backends failed. Tried: {backend_order}. Last reason: {decision.reason}",
        )

    def render_scenes(self, scene_intents: list[SceneIntent]) -> list[SceneAsset]:
        """Render multiple scenes in order. Returns list of SceneAssets.

        If a scene fails, it's skipped (with a warning) and the rest continue.
        The caller can check for missing scenes afterward.
        """
        assets: list[SceneAsset] = []
        for intent in scene_intents:
            try:
                asset = self.render_scene(intent)
                assets.append(asset)
            except BackendError as e:
                logger.error("Failed to render scene %s: %s", intent.scene_id, e.message)
        return assets

    def get_decisions(self) -> list[RenderDecision]:
        """Return the list of render decisions made so far. For debugging."""
        return self._decisions

    def total_spent(self) -> float:
        """Return the total USD spent so far."""
        return self._spent

    def available_backends(self) -> list[str]:
        """Return the names of all registered backends."""
        return list(self.backends.keys())

    # ---------- PRIVATE METHODS ----------

    def _select_backend_order(
        self,
        scene_intent: SceneIntent,
        override: str | None = None,
    ) -> list[str]:
        """Determine the order in which to try backends.

        The order depends on:
        1. Explicit override (scene.backend_hint or override arg)
        2. irreversible_moment → highest quality first
        3. cost_priority → cheapest first
        4. Default → primary first, then others by cost
        """
        # 1. Explicit override
        requested = override or scene_intent.backend_hint
        if requested and requested in self.backends:
            # Requested first, then fall back to others (cheapest first)
            others = sorted(
                [n for n in self.backends if n != requested],
                key=lambda n: self.backends[n].cost_per_scene_usd,
            )
            return [requested] + others

        # 2. Irreversible moment → highest quality first
        if scene_intent.irreversible_moment:
            return sorted(
                self.backends.keys(),
                key=lambda n: (-self.backends[n].quality_score, self.backends[n].cost_per_scene_usd),
            )

        # 3. Cost priority
        if scene_intent.cost_priority == "free":
            return sorted(
                self.backends.keys(),
                key=lambda n: (self.backends[n].cost_per_scene_usd, -self.backends[n].quality_score),
            )

        # 4. Default: primary first, then others by cost
        others = sorted(
            [n for n in self.backends if n != self.primary],
            key=lambda n: self.backends[n].cost_per_scene_usd,
        )
        return [self.primary] + others