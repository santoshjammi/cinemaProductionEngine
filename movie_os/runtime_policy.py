"""Canonical runtime contract and policy resolution for production runs.

P0-02 scope:
- validate an Episode Contract
- validate RPCO selection against the authoritative ontology
- resolve an immutable Effective Policy Snapshot
- persist both under productions/<episode_id>/
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, model_validator


ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"


class EpisodeContract(BaseModel):
    episode_id: str
    working_title: str

    niche: str
    domain: str
    problem_family: str
    sub_series: str
    mechanism_variant: str | None = None

    universe_id: str
    primary_characters: list[str] = Field(default_factory=list)

    primary_mechanism: str
    story_context: str
    viewer_recognition: str
    responsibility_pattern: str
    intended_resolution: str

    format_profile: str
    target_runtime_minutes: int
    continuity_required: bool = True
    status: dict[str, Any] = Field(default_factory=lambda: {"contract_state": "draft"})

    @model_validator(mode="before")
    @classmethod
    def _adapt_schema_aliases(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        result = dict(data)
        if "title" in result and "working_title" not in result:
            result["working_title"] = result["title"]
        if "classification" in result:
            classification = result.get("classification") or {}
            result.setdefault("niche", classification.get("niche"))
            result.setdefault("domain", classification.get("domain"))
            result.setdefault("problem_family", classification.get("problem_family") or classification.get("problem_family_id"))
            result.setdefault("sub_series", classification.get("sub_series") or classification.get("sub_series_id"))
        if "story" in result:
            story = result.get("story") or {}
            result.setdefault("primary_mechanism", story.get("primary_mechanism"))
            result.setdefault("story_context", story.get("story_context"))
            result.setdefault("viewer_recognition", story.get("viewer_recognition"))
            result.setdefault("responsibility_pattern", story.get("responsibility_pattern"))
            result.setdefault("intended_resolution", story.get("intended_resolution"))
        if "universe" in result:
            universe = result.get("universe") or {}
            result.setdefault("universe_id", universe.get("universe_id") or universe.get("id"))
            result.setdefault("primary_characters", universe.get("primary_characters", []))
        if "format" in result:
            fmt = result.get("format") or {}
            result.setdefault("format_profile", fmt.get("format_profile") or fmt.get("format_profile_id") or fmt.get("profile"))
            if "target_runtime" in fmt and "target_runtime_minutes" not in result:
                value = str(fmt.get("target_runtime", "")).rstrip("mM")
                try:
                    result["target_runtime_minutes"] = int(value)
                except Exception:
                    pass
        if "continuity" in result:
            continuity = result.get("continuity") or {}
            result.setdefault("continuity_required", bool(continuity.get("required", True)))
        return result


class EffectivePolicySnapshot(BaseModel):
    policy_snapshot_id: str
    episode_id: str
    created_at: str
    schema_version: str = "1.0"
    sources: list[dict[str, str]]
    ontology_selection: dict[str, str]
    format_profile: str
    universe_id: str
    resolved_rules: dict[str, Any]
    snapshot_hash: str
    status: str = "RESOLVED"


def _read_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256(data: Any) -> str:
    return hashlib.sha256(_canonical_json(data).encode("utf-8")).hexdigest()


def _load_ontology() -> dict[str, Any]:
    return _read_yaml(DOCS / "10_psychology" / "01_RELATIONSHIP_PSYCHOLOGY_CONTENT_ONTOLOGY.yaml")


def _find_problem_family(ontology: dict[str, Any], problem_family: str, sub_series: str) -> tuple[str, str]:
    families = ontology.get("problem_families", [])
    for family in families:
        family_matches = problem_family in {family.get("id"), family.get("name")}
        if family_matches:
            for sub in family.get("sub_series", []):
                if sub_series in {sub.get("id"), sub.get("name")}:
                    return family.get("id", problem_family), sub.get("id", sub_series)
            raise ValueError(f"Invalid RPCO sub-series: {sub_series}")
    raise ValueError(f"Invalid RPCO problem family: {problem_family}")


def validate_episode_contract(contract_data: dict[str, Any]) -> EpisodeContract:
    return EpisodeContract.model_validate(contract_data)


def resolve_policy(contract: EpisodeContract, ontology_selection: dict[str, str], format_profile: dict[str, Any] | None = None,
                   universe: dict[str, Any] | None = None, source_versions: dict[str, str] | None = None) -> EffectivePolicySnapshot:
    format_profile = format_profile or {}
    universe = universe or {"universe_id": contract.universe_id}
    source_versions = source_versions or {}

    ontology = _load_ontology()
    family_id, sub_series_id = _find_problem_family(
        ontology,
        ontology_selection["problem_family"],
        ontology_selection["sub_series"],
    )

    canonical_character_bindings = [
        {
            "character_id": "MARK",
            "display_name": "Mark",
            "character_bible_ref": "docs/10_psychology/10_mark_sarah/01_MARK_CHARACTER_BIBLE.md",
            "visual_identity_registry_ref": "movie_os/data/characters/MARK/character.yaml",
            "voice_registry_ref": "movie_os/data/voices/MARK/voice.yaml",
            "continuity_registry_ref": "movie_os/data/continuity/mark_sarah_continuity.yaml",
        },
        {
            "character_id": "SARAH",
            "display_name": "Sarah",
            "character_bible_ref": "docs/10_psychology/10_mark_sarah/01_SARAH_CHARACTER_BIBLE.md",
            "visual_identity_registry_ref": "movie_os/data/characters/SARAH/character.yaml",
            "voice_registry_ref": "movie_os/data/voices/SARAH/voice.yaml",
            "continuity_registry_ref": "movie_os/data/continuity/mark_sarah_continuity.yaml",
        },
    ]
    resolved_rules = {
        "niche": contract.niche,
        "domain": contract.domain,
        "problem_family_id": family_id,
        "sub_series_id": sub_series_id,
        "one_primary_mechanism": True,
        "dialogue_owner": "GENESIS",
        "production_creative_rewrite_allowed": False,
        "permanent_separation_allowed": False,
        "clinical_diagnosis_allowed": False,
        "selected_standards": [
            "DIALOGUE_AND_PERFORMANCE@1.0",
            "EMOTIONAL_CONTINUITY@1.0",
            "VISUAL_CHARACTER_CONTINUITY@1.0",
            "VOICE_AUDIO@1.0",
            "MOTION_AND_LIPSYNC@1.0",
            "CINEMATIC_SHOT_LANGUAGE@1.0",
            "ANTI_AI_SLOP@1.0",
        ],
        "multi_part_standard_applies": False,
        "selected_format_profile": contract.format_profile,
        "canonical_character_bindings": canonical_character_bindings,
        "canonical_continuity_binding": {
            "continuity_registry_ref": "movie_os/data/continuity/mark_sarah_continuity.yaml",
            "continuity_required": contract.continuity_required,
            "universe_id": contract.universe_id,
        },
    }

    payload = {
        "episode_contract": contract.model_dump(),
        "ontology_selection": ontology_selection,
        "format_profile": contract.format_profile,
        "universe_id": contract.universe_id,
        "resolved_rules": resolved_rules,
        "sources": source_versions,
    }
    snapshot_hash = _sha256(payload)
    snapshot_id = f"POLICY-{contract.episode_id}-{snapshot_hash[:12]}"
    created_at = datetime.now(timezone.utc).isoformat()
    return EffectivePolicySnapshot(
        policy_snapshot_id=snapshot_id,
        episode_id=contract.episode_id,
        created_at=created_at,
        sources=[{"path": k, "version_or_hash": v, "authority_class": "authoritative"} for k, v in source_versions.items()],
        ontology_selection=ontology_selection,
        format_profile=contract.format_profile,
        universe_id=contract.universe_id,
        resolved_rules=resolved_rules,
        snapshot_hash=snapshot_hash,
    )


def canonical_episode_contract() -> dict[str, Any]:
    return {
        "episode_id": "EP-0001",
        "working_title": "The Email Mark Wouldn't Open",
        "classification": {
            "niche": "Psychology",
            "domain": "Relationship & Emotional Psychology",
            "problem_family": "RP-01",
            "sub_series": "RP-01-S01",
        },
        "universe": {
            "universe_id": "UNIVERSE-MARK-SARAH",
            "primary_characters": ["Mark", "Sarah"],
        },
        "story": {
            "primary_mechanism": "fear-based withdrawal",
            "story_context": "Possible engineering-team cuts occur during an already busy family week.",
            "viewer_recognition": "Withdrawal can sometimes be an attempt to hide fear rather than rejection",
            "responsibility_pattern": "both",
            "intended_resolution": "Meaningful progress through honest disclosure and practical rebalancing.",
        },
        "format": {
            "format_profile": "YOUTUBE_LONGFORM_16X9",
            "target_runtime": "12m",
        },
        "continuity": {"required": True},
        "status": {"contract_state": "approved"},
    }


def canonical_ontology_selection() -> dict[str, str]:
    return {
        "niche": "Psychology",
        "domain": "Relationship & Emotional Psychology",
        "problem_family": "RP-01",
        "sub_series": "RP-01-S01",
    }


def persist_production_policy(contract: EpisodeContract, snapshot: EffectivePolicySnapshot) -> dict[str, Path]:
    production_root = Path("productions") / contract.episode_id
    contract_dir = production_root / "contract"
    policy_dir = production_root / "policy"
    contract_dir.mkdir(parents=True, exist_ok=True)
    policy_dir.mkdir(parents=True, exist_ok=True)

    contract_path = contract_dir / "episode_contract.yaml"
    policy_path = policy_dir / "effective_policy_snapshot.yaml"
    contract_path.write_text(yaml.safe_dump(contract.model_dump(), sort_keys=False), encoding="utf-8")
    policy_path.write_text(yaml.safe_dump(snapshot.model_dump(), sort_keys=False), encoding="utf-8")
    return {"contract_path": contract_path, "policy_path": policy_path}


def load_and_resolve_canonical_policy() -> tuple[EpisodeContract, EffectivePolicySnapshot, dict[str, Path]]:
    contract = validate_episode_contract(canonical_episode_contract())
    ontology_selection = canonical_ontology_selection()
    format_profile = _read_yaml(DOCS / "40_contracts" / "FORMAT_PROFILE.schema.yaml")
    source_versions = {
        "docs/00_governance/01_CINEMA_MASTER_CONSTITUTION.md": "2026-08-10",
        "docs/10_psychology/00_PSYCHOLOGY_SUB_CONSTITUTION.md": "2026-08-10",
        "docs/10_psychology/10_mark_sarah/00_MARK_SARAH_SERIES_CONSTITUTION.md": "2026-08-10",
        "docs/20_standards/DIALOGUE_AND_PERFORMANCE_STANDARD.md": "2026-08-10",
        "docs/20_standards/EMOTIONAL_CONTINUITY_STANDARD.md": "2026-08-10",
        "docs/20_standards/VISUAL_CHARACTER_CONTINUITY_STANDARD.md": "2026-08-10",
        "docs/20_standards/VOICE_AUDIO_STANDARD.md": "2026-08-10",
        "docs/20_standards/MOTION_AND_LIPSYNC_STANDARD.md": "2026-08-10",
        "docs/20_standards/CINEMATIC_SHOT_LANGUAGE_STANDARD.md": "2026-08-10",
        "docs/20_standards/ANTI_AI_SLOP_QUALITY_STANDARD.md": "2026-08-10",
        "docs/40_contracts/FORMAT_PROFILE.schema.yaml": _sha256(format_profile),
    }
    snapshot = resolve_policy(contract, ontology_selection, format_profile=format_profile, source_versions=source_versions)
    paths = persist_production_policy(contract, snapshot)
    return contract, snapshot, paths
