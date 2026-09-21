"""Tests for the derived deliverables that close the GENESIS/PROMETHEUS gaps.

Covers SAI-86 (scene logic), SAI-92 (sealed PKP), SAI-93 (runtime config),
SAI-98 (voice profiles), SAI-100 (music policy), SAI-84/88 (screenplay +
shooting script artifacts).
"""
from __future__ import annotations

import yaml
from pathlib import Path

import pytest

from movie_os.genesis2.scene_logic import SCENE_LOGIC_CHAIN, build_scene_logic
from movie_os.providers.voice.voice_profiles import (
    VOICE_PROFILES,
    get_profile,
    resolve_voice,
)


ROOT = Path(__file__).resolve().parent.parent


# ── SAI-86 / TASK-006: Structured Scene Logic ──────────────────────────────
class TestSceneLogic:
    def test_complete_chain_is_valid(self):
        raw = {s: f"content for {s}" for s in SCENE_LOGIC_CHAIN}
        sl = build_scene_logic(1, raw)
        assert sl.is_complete()
        assert sl.validate() == []

    def test_missing_chain_fail_closed(self):
        raw = {s: "x" for s in SCENE_LOGIC_CHAIN[:4]}  # missing last 5 links
        sl = build_scene_logic(3, raw)
        missing = sl.validate()
        assert "outgoing_state" in missing
        assert "scene_turn" in missing
        assert not sl.is_complete()

    def test_chain_order_is_canonical(self):
        assert SCENE_LOGIC_CHAIN[0] == "incoming_state"
        assert SCENE_LOGIC_CHAIN[-1] == "outgoing_state"
        assert len(SCENE_LOGIC_CHAIN) == 9


# ── SAI-92 / TASK-012 + SAI-84/88: Sealed PKP + screenplay artifacts ──────
class TestSealedPackage:
    @pytest.fixture()
    def pkp_dir(self):
        return ROOT / "packages" / "ew001" / "pkp"

    def test_pkp_manifest_exists(self, pkp_dir):
        p = pkp_dir / "manifest.yaml"
        assert p.exists()
        m = yaml.safe_load(p.read_text())
        assert m["pkp_id"].startswith("PKP-EP")
        assert m["status"] == "FROZEN"

    def test_validation_report_passed(self, pkp_dir):
        p = pkp_dir / "validation_report.yaml"
        assert p.exists()
        vr = yaml.safe_load(p.read_text())
        assert vr["validation_status"] == "passed"

    def test_builder_handoff_exists(self, pkp_dir):
        assert (pkp_dir / "builder_handoff.yaml").exists()

    def test_frozen_pkp_plus_derived_artifacts(self):
        pkg = ROOT / "packages" / "ew001"
        for name in ["screenplay.yaml", "screenplay.md", "shooting_script.yaml", "pkp/PKP-EP-0006-v1.yaml"]:
            assert (pkg / name).exists(), f"missing {name}"

    def test_shooting_script_has_shots(self):
        p = ROOT / "packages" / "ew001" / "shooting_script.yaml"
        ss = yaml.safe_load(p.read_text())
        assert ss["production_id"] == "ew001"
        total = sum(len(sc["shots"]) for sc in ss["scenes"])
        assert total >= 30


# ── SAI-93 / TASK-013: Runtime config ─────────────────────────────────────
class TestRuntimeConfig:
    def test_runtime_config_defines_all_sections(self):
        p = ROOT / "config" / "runtime_config.yaml"
        assert p.exists()
        cfg = yaml.safe_load(p.read_text())
        for section in ["comfyui", "flux", "voice", "ffmpeg", "output", "fallback", "timeouts", "retry"]:
            assert section in cfg, f"missing {section}"


# ── SAI-98 / TASK-018: Voice profiles ──────────────────────────────────────
class TestVoiceProfiles:
    def test_canonical_profiles(self):
        assert "msvr-mark" in VOICE_PROFILES
        assert "msvr-sarah" in VOICE_PROFILES

    def test_mark_maps_to_edge(self):
        assert resolve_voice("MSVR-MARK", "edge_tts") == "en-US-BrianNeural"

    def test_unknown_profile_falls_back(self):
        assert resolve_voice("BOGUS", "edge", "FALLBACK") == "FALLBACK"

    def test_get_profile_normalizes_inner(self):
        assert get_profile("MARK_INNER").profile_id == "msvr-mark"


# ── SAI-90 / TASK-010: Medium-specific prompts ─────────────────────────────
class TestMediumPrompts:
    def test_build_medium_prompts_all_types(self):
        from movie_os.genesis2.medium_prompts import build_medium_prompts, _MEDIUM_PREFIX
        scene = {
            "character_lore": "MARK [tall, grey sweater]",
            "visual_action": "sets down mug",
            "cinematic_style": "warm golden light, photorealistic, Alexa 35mm",
            "audio_goal": "gentle kitchen ambience",
            "music_intent": "sparse cello",
            "foley": "mug on ceramic",
        }
        shot = {"camera": "slow push-in", "visual_subject": "Sarah and Mark at table"}
        lines = [{"text": "Mark, please say something.", "delivery_intent": "pleading", "emotion": "urgent"}]
        prompts = build_medium_prompts(scene, shot, lines)
        assert prompts["image"], "image prompt missing"
        assert prompts["video"], "video prompt missing"
        assert prompts["tts"], "tts prompt missing"
        assert prompts["ambience"], "ambience prompt missing"
        assert prompts["image"][0].startswith(_MEDIUM_PREFIX["image"])
        assert prompts["video"][0].startswith(_MEDIUM_PREFIX["video"])
        assert prompts["tts"][0].startswith(_MEDIUM_PREFIX["tts"])
        assert "ffmpeg" in prompts["video"][0].lower() or "ken burns" in prompts["video"][0].lower()


# ── SAI-104 / TASK-024: Structured media validation ────────────────────────
class TestMediaValidation:
    def test_missing_asset_fails_closed(self):
        from movie_os.prometheus.media_validation import validate_artifact
        check = validate_artifact({"path": "/nonexistent/x.mp4", "type": "final_video"})
        assert not check.passed
        assert check.reason == "missing"

    def test_real_audio_passes(self):
        from movie_os.prometheus.media_validation import validate_artifact
        path = ROOT / "packages" / "ew001" / "scene_4" / "music" / "ambience.wav"
        if not path.exists():
            pytest.skip("ambience.wav not present")
        check = validate_artifact({"path": str(path), "type": "audio"})
        assert check.exists
        assert check.passed
        assert check.duration_seconds and check.duration_seconds > 0

    def test_real_scene_image_passes(self):
        from movie_os.prometheus.media_validation import validate_artifact
        path = ROOT / "packages" / "ew001" / "scene_4" / "image" / "scene_04_generated.png"
        if not path.exists():
            pytest.skip("scene_04_generated.png not present")
        check = validate_artifact({"path": str(path), "type": "image"})
        assert check.passed
        assert check.width and check.width > 0

    def test_workflow_json_validation(self):
        from movie_os.prometheus.media_validation import validate_artifact
        path = ROOT / "packages" / "ew001" / "scene_4" / "comfyui_workflow.json"
        if not path.exists():
            pytest.skip("workflow json not present")
        check = validate_artifact({"path": str(path), "type": "workflow"})
        assert check.passed


# ── SAI-85 / TASK-005: Context Manager (all 9 capsule types) ──────────────
class TestContextManager:
    def test_supports_all_nine_task_types(self):
        from pipeline.architect.context_manager import ALL_TASK_TYPES, ContextManager
        contract = {
            "production_id": "ew001", "contract_id": "EP-0006", "contract_version": "1.0",
            "characters": [{"id": "MARK"}, {"id": "SARAH"}],
            "ending": "separation", "core_conflict": {"withdrawal_mechanism": "fear-based withdrawal"},
            "tone": ["melancholic"],
            "exact_dialogue_text": [{"line_id": "1:D001", "text": "hi"}],
        }
        cm = ContextManager(contract)
        assert len(ALL_TASK_TYPES) == 9
        for t in ALL_TASK_TYPES:
            caps = cm.get_capsule(t, contract)
            assert caps["task_type"] == t
            assert "immutable_constraints" in caps
            assert "parent_memory" in caps  # always carried from approved parent

    def test_dialogue_capsule_constraints(self):
        from pipeline.architect.context_manager import ContextManager
        contract = {
            "characters": [], "ending": "x", "tone": [],
            "exact_dialogue_text": [] if False else [{"line_id": "1", "text": "hi"}],
        }
        caps = ContextManager(contract).get_capsule("generate_dialogue", contract)
        assert caps["constraints"]["new_characters_forbidden"] is True
        assert caps["constraints"]["max_words"] == 28


# ── SAI-100 / TASK-020: Music policy ─────────────────────────────────────────
class TestMusicPolicy:
    def test_policy_allows_cc0_only(self):
        p = ROOT / "pipeline" / "music_policy.yaml"
        assert p.exists()
        pol = yaml.safe_load(p.read_text())
        sources = {s["type"] for s in pol["allowed_sources"]}
        assert all(t in sources for t in ["cc0", "local_original", "silence"])
        assert "procedural_tones" in {f["type"] for f in pol["forbidden_sources"]}
