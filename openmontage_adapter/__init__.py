"""OpenMontage Adapter — Render Abstraction Layer.

This module implements the render abstraction described in
``grammar/render_abstraction.md``. It provides:

- ``SceneIntent`` / ``SceneAsset`` dataclasses (provider-agnostic)
- ``RenderBackend`` abstract base class (every provider implements this)
- ``RenderOrchestrator`` (selects the best backend, falls back on failure)
- ``OpenMontageAdapter`` (translates OpenMontage scene_plan to SceneIntent)
- ``videogen_adapter`` (translates videoGen manifest YAML to SceneIntents)
- ``SDXLLocalBackend`` (the default M1 Max local backend)

The current default backend is ``SDXLLocalBackend`` (M1 Max, local, free).
Future backends (Flux, OpenAI, StockFootage) plug in by implementing
``RenderBackend``.

This is the adapter layer that lets videoGen act as OpenMontage's render
backend for cinematic psychological content.
"""

from .scene_intent import SceneIntent, SceneAsset
from .render_backend import RenderBackend, BackendError
from .orchestrator import RenderOrchestrator, RenderDecision
from .om_adapter import OpenMontageAdapter, OM_TO_VIDEOGEN_TRANSLATIONS
from .videogen_adapter import manifest_to_intents
from .backends import SDXLLocalBackend

__all__ = [
    "SceneIntent",
    "SceneAsset",
    "RenderBackend",
    "BackendError",
    "RenderOrchestrator",
    "RenderDecision",
    "OpenMontageAdapter",
    "OM_TO_VIDEOGEN_TRANSLATIONS",
    "manifest_to_intents",
    "SDXLLocalBackend",
]