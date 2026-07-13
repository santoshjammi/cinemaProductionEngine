"""Procedural Music Provider — wraps the existing MusicGenerator.

Generates music tracks using numpy synthesis (the existing
`MusicGenerator` from `scripts/psychological_pipeline.py`). The
generated tracks are:
  - act_1: ambient piano (sparse, warm, melancholic)
  - act_2: dark drone (low rumble, dissonant notes)
  - act_3: near-silence (single sustained note fading to nothing)
  - sting: dramatic sub-bass + chord (for the irreversible moment)

This is a "procedural" provider because it doesn't call an external
model — it generates audio with pure numpy. Cheap, fast, offline.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

from movie_os.capabilities.base import MusicIntent
from movie_os.domain.asset import Asset, AssetType, RenderBackend
from movie_os.providers.base import MusicProvider, make_asset, run_sync


logger = logging.getLogger("movie_os.providers.music.procedural")


# Map our zone names to the legacy MusicGenerator methods
_ZONE_METHODS = {
    "act_1": "generate_act1",
    "act_2": "generate_act2",
    "act_3": "generate_act3",
    "sting": "generate_sting",  # via DramaticStingGenerator
}


class ProceduralMusicProvider(MusicProvider):
    """Procedural music generation using numpy synthesis.

    Wraps the MusicGenerator from scripts/psychological_pipeline.py.
    """

    name = "procedural"
    backend = RenderBackend.PROCEDURAL

    def __init__(self, sample_rate: int = 44100, default_volume: float = 0.3):
        self.sample_rate = sample_rate
        self.default_volume = default_volume
        self._generators: dict[str, Any] = {}  # zone -> generator instance

    def _ensure_generator(self, zone: str, output_dir: str):
        """Lazy-load the legacy MusicGenerator."""
        key = f"{zone}:{output_dir}"
        if key in self._generators:
            return self._generators[key]
        # Import the legacy MusicGenerator
        scripts_path = Path(__file__).parent.parent.parent.parent / "scripts"
        if str(scripts_path) not in sys.path:
            sys.path.insert(0, str(scripts_path))
        from psychological_pipeline import MusicGenerator, DramaticStingGenerator

        if zone == "sting":
            gen = DramaticStingGenerator(output_dir)
        else:
            gen = MusicGenerator(output_dir)
        self._generators[key] = gen
        return gen

    async def render(self, intent: MusicIntent) -> Asset:
        """Generate a music track for the given zone."""
        if not intent.zone:
            raise ValueError("MusicIntent.zone is required")

        # Resolve the output directory. The MusicGenerator expects an
        # output_dir and creates the file at {output_dir}/music/<filename>.
        # So we need to pass it the PARENT of the music dir.
        if intent.metadata and intent.metadata.get("output_dir"):
            parent_dir = intent.metadata["output_dir"]
        elif intent.output_path:
            # output_path might be a file or a dir
            p = Path(intent.output_path)
            if p.suffix:
                parent_dir = str(p.parent)
            else:
                parent_dir = str(p)
        else:
            parent_dir = "output/videos"

        # Run the sync generation in a thread
        asset = await run_sync(
            self._generate_sync, intent.zone, intent.duration_seconds, parent_dir
        )
        return asset

    def _generate_sync(self, zone: str, duration: float, parent_dir: str) -> Asset:
        """The actual sync generation call."""
        gen = self._ensure_generator(zone, parent_dir)
        method_name = _ZONE_METHODS.get(zone)
        if not method_name:
            raise ValueError(f"Unknown music zone: {zone}")
        method = getattr(gen, method_name, None)
        if method is None:
            raise ValueError(f"MusicGenerator has no method {method_name}")
        path = method(duration=duration)
        # The path is the actual file the generator wrote
        if not isinstance(path, Path):
            path = Path(path)
        # Get duration
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
            asset_type=AssetType.MUSIC,
            backend=self.backend,
            metadata={"zone": zone, "target_duration": duration},
            duration_seconds=actual_duration,
        )

    def can_handle(self, intent: MusicIntent) -> bool:
        return bool(intent.zone) and intent.zone in _ZONE_METHODS


def make(settings: dict, cost_per_call_usd: float = 0.0) -> ProceduralMusicProvider:
    """Build a ProceduralMusicProvider from config settings."""
    return ProceduralMusicProvider(
        sample_rate=settings.get("sample_rate", 44100),
        default_volume=settings.get("default_volume", 0.3),
    )
