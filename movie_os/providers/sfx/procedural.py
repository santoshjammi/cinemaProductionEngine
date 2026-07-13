"""Procedural SFX Provider — wraps the existing AmbientSFXGenerator.

Generates per-beat ambient SFX using numpy synthesis. The legacy
AmbientSFXGenerator has a BEAT_PROFILES dict that maps each scene
beat to a specific sound design:

  - opening_hook: bedroom fan hum, breathing, sheets rustling
  - contrast_memory: warm morning, birds, kitchen, cutlery
  - outside_version: domestic routine, kitchen, traffic, dishes
  - first_fracture: parked car, engine hum, rain on windshield
  - internal_collapse: empty room, clock, breathing, chair creak
  - irreversible_moment: breathing, fabric, chair, room hum, fan
  - almost_moment: proximity, breath, fabric, pause
  - defensive_retreat: TV hum, controller, isolation
  - her_truth: rain, uneven breathing, tears
  - final_truth: bedroom fan, breathing, nothing left

This is the "ambient bed" the scene plays over.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

from movie_os.domain.asset import Asset, AssetType, RenderBackend
from movie_os.providers.base import SFXProvider, make_asset, run_sync


logger = logging.getLogger("movie_os.providers.sfx.procedural")


class ProceduralSFXProvider(SFXProvider):
    """Per-beat ambient SFX using numpy synthesis.

    Wraps the AmbientSFXGenerator from scripts/psychological_pipeline.py.
    """

    name = "procedural"
    backend = RenderBackend.PROCEDURAL

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self._generators: dict[str, Any] = {}

    def _ensure_generator(self, beat: str, output_dir: str):
        """Lazy-load the legacy AmbientSFXGenerator."""
        key = f"{beat}:{output_dir}"
        if key in self._generators:
            return self._generators[key]
        scripts_path = Path(__file__).parent.parent.parent.parent / "scripts"
        if str(scripts_path) not in sys.path:
            sys.path.insert(0, str(scripts_path))
        from psychological_pipeline import AmbientSFXGenerator
        gen = AmbientSFXGenerator(output_dir)
        self._generators[key] = gen
        return gen

    async def render(self, intent: Any) -> Asset:
        """Generate ambient SFX for a beat.

        The intent is a duck-typed object with a `beat` attribute and
        a `duration` (or `duration_seconds`) attribute.
        """
        beat = getattr(intent, "beat", None) or (intent.metadata.get("beat") if intent.metadata else None)
        if not beat:
            raise ValueError("SFX intent must have a `beat` attribute")

        # Resolve the output directory. The AmbientSFXGenerator expects
        # an output_dir and saves to {output_dir}/sfx/<filename>.
        if intent.metadata and intent.metadata.get("output_dir"):
            parent_dir = intent.metadata["output_dir"]
        elif getattr(intent, "output_path", None):
            p = Path(intent.output_path)
            if p.suffix:
                parent_dir = str(p.parent)
            else:
                parent_dir = str(p)
        else:
            parent_dir = "output/videos"

        duration = (
            getattr(intent, "duration", None)
            or getattr(intent, "duration_seconds", None)
            or (intent.metadata.get("duration") if intent.metadata else None)
            or 15.0
        )

        asset = await run_sync(
            self._generate_sync, beat, duration, parent_dir
        )
        return asset

    def _generate_sync(self, beat: str, duration: float, parent_dir: str) -> Asset:
        """The actual sync generation call."""
        gen = self._ensure_generator(beat, parent_dir)
        path = gen.generate_for_beat(beat, duration)
        if not isinstance(path, Path):
            path = Path(path)
        actual_duration = duration
        if path.exists():
            try:
                import subprocess
                r = subprocess.run(
                    ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                     "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
                    capture_output=True, text=True, timeout=5,
                )
                actual_duration = float(r.stdout.strip())
            except Exception:
                pass
        return make_asset(
            path=path,
            asset_type=AssetType.SFX,
            backend=self.backend,
            metadata={"beat": beat, "target_duration": duration},
            duration_seconds=actual_duration,
        )

    def can_handle(self, intent: Any) -> bool:
        beat = getattr(intent, "beat", None)
        return bool(beat)


def make(settings: dict, cost_per_call_usd: float = 0.0) -> ProceduralSFXProvider:
    """Build a ProceduralSFXProvider from config settings."""
    return ProceduralSFXProvider(
        sample_rate=settings.get("sample_rate", 44100),
    )
