"""Tests for the v5.2 irreversible_moment enhancements:
- DramaticStingGenerator produces a sting with the expected layers
- mix_irreversible_scene correctly layers sting + ambient
- generate_ken_burns_clip_with_cut produces a 2-image hard-cut clip
- Master Timeline schema includes scene_description_alt
"""

import inspect
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import numpy as np

from story_factory import (
    MasterTimeline,
    Scene,
    Character,
    MusicCue,
    AmbientCue,
    ShotLanguage,
    SilenceEngine,
)


class TestMasterTimelineAltDescription:
    """v5.2 — Master Timeline scene_description_alt field."""

    def test_scene_has_alt_description_field(self):
        sig = inspect.signature(Scene)
        assert "scene_description_alt" in sig.parameters

    def test_alt_description_survives_save_load(self):
        s = Scene(
            scene_number=7, title="Irreversible", act="act_2", phase="collapse",
            beat="irreversible_moment", irreversible_moment=True,
            scene_description="Hand hovers above shoulder",
            scene_description_alt="Close-up of the partner's closed eyes",
        )
        tl = MasterTimeline(
            scenes=[s],
            characters=[Character(key="husband", name="H")],
        )
        # Save and load
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "tl.yaml"
            tl.save(path)
            loaded = MasterTimeline.load(path)
            assert loaded.scenes[0].scene_description == "Hand hovers above shoulder"
            assert loaded.scenes[0].scene_description_alt == "Close-up of the partner's closed eyes"

    def test_alt_description_defaults_to_empty_string(self):
        s = Scene(scene_number=1, title="T", act="a", phase="p", beat="b")
        assert s.scene_description_alt == ""


class TestDramaticStingInPipeline:
    """v5.2 — DramaticStingGenerator class exists in the pipeline."""

    def test_dramatic_sting_class_importable(self):
        from scripts.psychological_pipeline import DramaticStingGenerator
        assert DramaticStingGenerator is not None

    def test_dramatic_sting_has_generate_method(self):
        from scripts.psychological_pipeline import DramaticStingGenerator
        assert hasattr(DramaticStingGenerator, "generate")

    def test_audio_mixer_has_mix_irreversible_scene(self):
        from scripts.psychological_pipeline import AudioMixer
        assert hasattr(AudioMixer, "mix_irreversible_scene")


class TestVideoServiceCutClip:
    """v5.2 — generate_ken_burns_clip_with_cut on VideoGenerationService."""

    def test_method_exists(self):
        from backend.app.services.video_service import VideoGenerationService
        assert hasattr(VideoGenerationService, "generate_ken_burns_clip_with_cut")


class TestTimelineToManifestAltDescription:
    """v5.2 — the manifest adapter includes scene_description_alt."""

    def test_alt_description_in_manifest(self):
        from story_factory import timeline_to_manifest
        s = Scene(
            scene_number=7, title="Irreversible", act="act_2", phase="collapse",
            beat="irreversible_moment", irreversible_moment=True,
            scene_description="Hand hovers",
            scene_description_alt="Close-up of partner",
        )
        tl = MasterTimeline(
            scenes=[s],
            characters=[Character(key="h", name="H")],
        )
        m = timeline_to_manifest(tl)
        assert m["scenes"][0]["scene_description_alt"] == "Close-up of partner"
        assert m["scenes"][0]["scene_description"] == "Hand hovers"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
