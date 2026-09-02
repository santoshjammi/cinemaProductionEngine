from __future__ import annotations

import copy

import pytest

from movie_os.frozen_pkp import build_frozen_pkp, freeze_from_brief, validate_frozen_pkp


def _brief():
    return {
        "scenes": [
            {
                "number": 1,
                "title": "Kitchen",
                "narrative_beat": "opening",
                "entry_state": "quiet",
                "turning_point": "Mark admits fear",
                "exit_state": "Sarah understands",
                "next_scene_cause": "new honesty",
                "emotional_progression": ["fearful", "supported", "resolved"],
            }
        ],
        "dialogues": [
            {
                "scene_number": 1,
                "lines": [
                    {"speaker": "MARK", "text": "I am scared to tell you this.", "emotion": "fearful"},
                    {"speaker": "SARAH", "text": "Tell me anyway.", "emotion": "supportive"},
                ],
            }
        ],
        "context": {
            "characters": [
                {"name": "MARK", "role": "protagonist", "visual_reference_id": "MSVI-MARK", "voice_reference_id": "MSVR-MARK", "approved_identity": "Mark canon"},
                {"name": "SARAH", "role": "supporting", "visual_reference_id": "MSVI-SARAH", "voice_reference_id": "MSVR-SARAH", "approved_identity": "Sarah canon"},
            ],
            "continuity": ["last_approved_episode_id: EP-0000"],
        },
        "characters": ["MARK", "SARAH"],
        "continuity": ["last_approved_episode_id: EP-0000"],
        "logline": "A man fears disappointing his wife.",
        "synopsis": "A man fears disappointing his wife.",
    }


def test_valid_pkp_creation_and_validation():
    pkp = freeze_from_brief(
        episode_id="EP-0001",
        policy_snapshot_id="POLICY-1",
        episode_contract_id="EP-0001",
        episode_contract_hash="c1",
        policy_snapshot_hash="p1",
        production={"episode_id": "EP-0001", "run_id": "RUN-1"},
        brief=_brief(),
    )
    validated = validate_frozen_pkp(pkp.model_dump())
    assert validated.pkp_id == "PKP-EP-0001-v1"
    assert validated.status == "FROZEN"
    assert [c["character_id"] for c in validated.characters["character_ids"]] == ["MARK", "SARAH"]
    assert validated.characters["visual_reference_ids"] == ["MSVI-MARK", "MSVI-SARAH"]
    assert validated.characters["voice_reference_ids"] == ["MSVR-MARK", "MSVR-SARAH"]
    assert validated.characters["voice_reference_ids"] == ["MSVR-MARK", "MSVR-SARAH"]
    assert validated.visual_bible["identity_controls"][0]["character_id"] == "MARK"
    assert validated.assets["required_references"] == ["MSVI-MARK", "MSVI-SARAH", "MSVR-MARK", "MSVR-SARAH"]
    assert validated.screenplay["scenes"][0]["dialogue_causality"]["effect"] == "Sarah understands"
    assert validated.scene_states["scenes"][0]["emotional_progression"] == ["fearful", "supported", "resolved"]
    assert validated.canonical_bible_bindings["Mark"]["character_bible_ref"].endswith("01_MARK_SARAH_CHARACTER_BIBLE_v2.yaml")
    assert validated.canonical_registry_bindings["voice_registry_refs"] == ["docs/10_psychology/10_mark_sarah/02_MARK_SARAH_VOICE_REGISTRY.yaml", "docs/10_psychology/10_mark_sarah/02_MARK_SARAH_VOICE_REGISTRY.yaml"]
    assert "mark_sarah" in validated.canonical_sources

def test_missing_critical_creative_field_rejected():
    brief = _brief()
    brief["dialogues"] = []
    with pytest.raises(ValueError, match="brief lacks required dialogue scenes"):
        freeze_from_brief(
            episode_id="EP-0001",
            policy_snapshot_id="POLICY-1",
            episode_contract_id="EP-0001",
            episode_contract_hash="c1",
            policy_snapshot_hash="p1",
            production={"episode_id": "EP-0001", "run_id": "RUN-1"},
            brief=brief,
        )


def test_dialogue_missing_causal_scene_state_gets_synthesized():
    brief = _brief()
    brief["scenes"][0].pop("exit_state")
    brief["dialogues"][0]["lines"][1]["emotion"] = "neutral"
    pkp = freeze_from_brief(
        episode_id="EP-0001",
        policy_snapshot_id="POLICY-1",
        episode_contract_id="EP-0001",
        episode_contract_hash="c1",
        policy_snapshot_hash="p1",
        production={"episode_id": "EP-0001", "run_id": "RUN-1"},
        brief=brief,
    )
    assert pkp.scene_states["scenes"][0]["exit"].startswith("Kitchen")
    assert pkp.scene_states["scenes"][0]["emotional_progression"] == ["fearful", "supported", "resolved"]


def test_frozen_pkp_mutation_rejected():
    pkp = freeze_from_brief(
        episode_id="EP-0001",
        policy_snapshot_id="POLICY-1",
        episode_contract_id="EP-0001",
        episode_contract_hash="c1",
        policy_snapshot_hash="p1",
        production={"episode_id": "EP-0001", "run_id": "RUN-1"},
        brief=_brief(),
    )
    with pytest.raises(ValueError, match="immutable"):
        pkp.mutate(story={"logline": "changed"})


def test_new_version_after_freeze_changes_hash():
    pkp = freeze_from_brief(
        episode_id="EP-0001",
        policy_snapshot_id="POLICY-1",
        episode_contract_id="EP-0001",
        episode_contract_hash="c1",
        policy_snapshot_hash="p1",
        production={"episode_id": "EP-0001", "run_id": "RUN-1"},
        brief=_brief(),
    )
    unfrozen = pkp.model_copy(update={"status": "DRAFT", "version": "2", "content_hash": ""})
    changed = unfrozen.mutate(story={"logline": "A different logline."})
    assert changed.version == "2"
    assert changed.content_hash != pkp.content_hash


def test_deterministic_hash_changes_with_content():
    pkp1 = freeze_from_brief(
        episode_id="EP-0001",
        policy_snapshot_id="POLICY-1",
        episode_contract_id="EP-0001",
        episode_contract_hash="c1",
        policy_snapshot_hash="p1",
        production={"episode_id": "EP-0001", "run_id": "RUN-1"},
        brief=_brief(),
    )
    brief2 = _brief()
    brief2["logline"] = "Changed."
    pkp2 = freeze_from_brief(
        episode_id="EP-0001",
        policy_snapshot_id="POLICY-1",
        episode_contract_id="EP-0001",
        episode_contract_hash="c1",
        policy_snapshot_hash="p1",
        production={"episode_id": "EP-0001", "run_id": "RUN-1"},
        brief=brief2,
    )
    assert pkp1.content_hash != pkp2.content_hash
