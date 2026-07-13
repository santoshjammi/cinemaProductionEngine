"""Tests for the Master Timeline schema and the timeline→manifest adapter.

These tests don't require the LLM — they only exercise the data structures
and the adapter logic. Run with:

    cd /Users/santosh/Desktop/projects/videoGen
    ./venv/bin/python -m pytest story_factory/tests/ -v --override-ini="addopts="
"""

import sys
import tempfile
import textwrap
from pathlib import Path

# Make story_factory importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import yaml

from story_factory import (
    MasterTimeline,
    Scene,
    Character,
    DialogueLine,
    MusicCue,
    AmbientCue,
    ShotLanguage,
    SilenceEngine,
    timeline_to_manifest,
    save_manifest,
)


def _make_sample_timeline() -> MasterTimeline:
    """Build a minimal valid MasterTimeline for testing."""
    return MasterTimeline(
        version="1.0",
        dna={
            "id": "EW-001",
            "territory": "emotional_withdrawal",
            "cluster": "fear_based_withdrawal",
            "mechanism": "anticipated_rejection",
            "archetype": "married_husband",
            "theme": "love_becomes_dangerous",
            "premise": "Stops initiating intimacy after repeated rejection.",
            "ending": "quiet_realization",
        },
        source={"dna": "dna.yaml", "context": "context.md", "story": "story.md"},
        metadata={
            "title": "Test Story",
            "id": "EW-001",
            "territory": "emotional_withdrawal",
            "cluster": "fear_based_withdrawal",
            "ending": "quiet_realization",
        },
        characters=[
            Character(key="husband", name="Arjun", role="protagonist",
                      anchors=["man mid-30s, dark hair, stubble, grey t-shirt"]),
            Character(key="wife", name="Maya", role="partner",
                      anchors=["woman early 30s, auburn hair, white shirt"]),
        ],
        scenes=[
            Scene(
                scene_number=1, title="Frozen Gesture",
                act="act_1_observation", phase="hook", beat="opening_hook",
                duration_seconds=12.0, duration_hint="20-30s",
                emotional_state="tense_restraint", energy=3,
                voiceover="No one notices the exact night it happens.",
                scene_description="He lies in bed. Phone glow. Hand hovers above her shoulder.",
                visual_cause_of_emotion="Hand starts to reach, then withdraws.",
                shot_language=ShotLanguage(shot_size="close-up", lighting_key="practical_lighting",
                                            lens_mm=50, depth_of_field="shallow"),
                characters_present=["husband", "wife"],
                ken_burns_effect="ken-burns",
                music_cue=MusicCue(zone="act_1", volume=0.35),
                ambient_cue=AmbientCue(beat="opening_hook",
                                        description="Bedroom at night — fan hum, breathing"),
            ),
            Scene(
                scene_number=7, title="Irreversible",
                act="act_2_inner_reality", phase="collapse", beat="irreversible_moment",
                duration_seconds=10.0, duration_hint="8-12s",
                emotional_state="silence", energy=1,
                voiceover="",
                scene_description="Empty room. Single chair. Window light.",
                silence_engine=SilenceEngine(silence_instead=True),
                irreversible_moment=True,
                music_cue=MusicCue(zone="none", volume=0.0),
                characters_present=[],
                ken_burns_effect="ken-burns",
            ),
            Scene(
                scene_number=11, title="Final Truth",
                act="act_3_psychological_truth", phase="climax", beat="final_truth",
                duration_seconds=25.0, duration_hint="25-40s",
                emotional_state="devastating_quiet", energy=1,
                voiceover="Not all distance is anger. Sometimes distance is grief.",
                scene_description="Same bedroom, same bed, same distance. The door is open.",
                shot_language=ShotLanguage(shot_size="wide", lighting_key="natural_shadows",
                                            lens_mm=35, depth_of_field="deep"),
                characters_present=["husband"],
                ken_burns_effect="ken-burns",
                music_cue=MusicCue(zone="act_3", volume=0.15),
            ),
        ],
    )


# ---------------------------------------------------------------------------
# MasterTimeline
# ---------------------------------------------------------------------------

class TestMasterTimeline:
    def test_basic_construction(self):
        t = _make_sample_timeline()
        assert t.version == "1.0"
        assert t.total_scenes == 3
        assert len(t.characters) == 2
        assert t.scenes[0].scene_number == 1

    def test_total_duration(self):
        t = _make_sample_timeline()
        # 12 + 10 + 25 = 47
        assert t.total_duration_seconds == 47.0

    def test_to_dict_roundtrip(self):
        t = _make_sample_timeline()
        d = t.to_dict()
        assert "master_timeline" in d
        assert d["master_timeline"]["version"] == "1.0"
        assert d["master_timeline"]["scenes"][0]["scene_number"] == 1
        assert d["master_timeline"]["scenes"][1]["silence_engine"]["silence_instead"] is True

    def test_save_and_load(self):
        t = _make_sample_timeline()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "timeline.yaml"
            t.save(path)
            assert path.exists()
            loaded = MasterTimeline.load(path)
            assert loaded.version == "1.0"
            assert len(loaded.scenes) == 3
            assert loaded.scenes[1].irreversible_moment is True
            assert loaded.scenes[1].silence_engine.silence_instead is True
            assert loaded.characters[0].key == "husband"

    def test_dialogue_preservation(self):
        t = _make_sample_timeline()
        t.scenes[0].dialogues = [
            DialogueLine(character="wife", line="Are you okay?", timing="early", emotion="worried"),
            DialogueLine(character="husband", line="Yeah.", timing="late", emotion="evasive"),
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "timeline.yaml"
            t.save(path)
            loaded = MasterTimeline.load(path)
            assert len(loaded.scenes[0].dialogues) == 2
            assert loaded.scenes[0].dialogues[0].character == "wife"
            assert loaded.scenes[0].dialogues[1].emotion == "evasive"

    def test_metadata_computed_fields(self):
        t = _make_sample_timeline()
        d = t.to_dict()
        # to_dict adds total_scenes and total_duration_seconds to metadata
        assert d["master_timeline"]["metadata"]["total_scenes"] == 3
        assert d["master_timeline"]["metadata"]["total_duration_seconds"] == 47.0


# ---------------------------------------------------------------------------
# timeline_to_manifest adapter
# ---------------------------------------------------------------------------

class TestTimelineToManifest:
    def test_basic_conversion(self):
        t = _make_sample_timeline()
        m = timeline_to_manifest(t)
        assert m["manifest_version"] == "4.0"
        assert m["playbook_file"] == "../psychological_cinema_standard.yaml"
        assert len(m["scenes"]) == 3
        assert "narrative_arc" in m

    def test_scene_field_mapping(self):
        t = _make_sample_timeline()
        m = timeline_to_manifest(t)
        s1 = m["scenes"][0]
        assert s1["scene_number"] == 1
        assert s1["title"] == "Frozen Gesture"
        assert s1["voiceover"] == "No one notices the exact night it happens."
        assert s1["shot_language"]["shot_size"] == "close-up"
        assert s1["ken_burns_effect"] == "ken-burns"
        assert s1["energy"] == 3

    def test_silence_engine_flags_propagate(self):
        t = _make_sample_timeline()
        m = timeline_to_manifest(t)
        s7 = m["scenes"][1]
        assert s7["silence_instead"] is True
        assert s7["irreversible_moment"] is True
        assert s7["_music_volume_override"] == 0.0

    def test_silence_before_after_only_when_set(self):
        t = _make_sample_timeline()
        t.scenes[0].silence_engine = SilenceEngine(silence_before=2.0, silence_after=1.5)
        m = timeline_to_manifest(t)
        s1 = m["scenes"][0]
        assert s1["silence_before"] == 2.0
        assert s1["silence_after"] == 1.5
        # Scene 3 has no silence — fields should not be present
        s3 = m["scenes"][2]
        assert "silence_before" not in s3
        assert "silence_after" not in s3

    def test_characters_converted(self):
        t = _make_sample_timeline()
        m = timeline_to_manifest(t)
        assert "husband" in m["characters"]
        assert m["characters"]["husband"]["name"] == "Arjun"
        assert m["characters"]["wife"]["name"] == "Maya"

    def test_story_factory_metadata(self):
        t = _make_sample_timeline()
        m = timeline_to_manifest(t)
        assert "story_factory" in m
        assert m["story_factory"]["dna_file"] == "dna.yaml"
        assert m["story_factory"]["master_timeline_id"] == "EW-001"
        assert m["story_factory"]["territory"] == "emotional_withdrawal"

    def test_story_factory_metadata_disabled(self):
        t = _make_sample_timeline()
        m = timeline_to_manifest(t, include_dna_context_story_refs=False)
        assert "story_factory" not in m

    def test_default_narrative_arc(self):
        t = _make_sample_timeline()
        m = timeline_to_manifest(t)
        arc = m["narrative_arc"]
        assert "act_1" in arc
        assert "act_2" in arc
        assert "act_3" in arc
        assert arc["act_1"]["title"] == "Observation"
        # The default arc has 9 beats summing to 11 scenes
        total = sum(s["scene_count"] for act in arc.values() for s in act["scenes"])
        assert total == 11

    def test_manifest_writes_valid_yaml(self):
        t = _make_sample_timeline()
        m = timeline_to_manifest(t)
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "manifest.yaml"
            save_manifest(m, path)
            assert path.exists()
            # Reload and check
            reloaded = yaml.safe_load(path.read_text())
            assert reloaded["manifest_version"] == "4.0"
            assert len(reloaded["scenes"]) == 3
            assert reloaded["scenes"][1]["silence_instead"] is True

    def test_yaml_format_is_pipeline_compatible(self):
        """The output should look like the existing VID01 manifests."""
        t = _make_sample_timeline()
        m = timeline_to_manifest(t)
        # Top-level keys the pipeline expects
        expected_keys = {
            "manifest_version", "story_file", "context_files", "playbook_file",
            "narrative_arc", "model", "generation", "characters",
            "visual_system", "scenes",
        }
        assert expected_keys <= set(m.keys())


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
