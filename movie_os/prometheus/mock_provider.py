"""Mock image provider for PROMETHEUS tests.

Returns fake image paths so the full 6-stage pipeline can execute in
tests without needing a real ComfyUI or SDXL backend.
"""

from __future__ import annotations

import asyncio
from typing import Any


class MockFluxComfyUIProvider:
    """A no-op / deterministic provider that always returns placeholder paths."""

    name = "mock_flux_comfyui"
    backend = "mock"
    next_id = 0

    async def render(self, intent: Any) -> Any:
        """Render — always succeeds with a mock image path."""
        MockFluxComfyUIProvider.next_id += 1
        scene_num = (intent.metadata or {}).get("scene_number", MockFluxComfyUIProvider.next_id) if hasattr(intent, 'metadata') else MockFluxComfyUIProvider.next_id
        output_dir = (intent.metadata or {}).get("output_dir", "output/prometheus/images")  # type: ignore[union-attr]
        from pathlib import Path  # noqa
        path = Path(str(output_dir)) / f"scene_{scene_num:03d}.png"

        return MockAsset(path=path, backend="mock", metadata={"clip_score": 0.95})


class MockAsset:
    """A mock asset matching the minimal Asset interface."""

    def __init__(self, path: Any, backend: str = "mock", metadata: dict | None = None):
        self.path = path
        self.backend = backend
        self.metadata = metadata or {}
