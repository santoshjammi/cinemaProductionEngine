"""Tests for the P0 bridge scene-preservation fix (REQ-006/REQ-008 loss).

The bridge previously only seeded scene_map from NarrativeExpansion when
ScenePlanning was empty, silently dropping every NarrativeExpansion scene
whose number exceeded the ScenePlanning count.  This collapsed a 6-scene arc
to 3, discarding the turning_point (REQ-006) and climax/resolution (REQ-008)
units.  The fix unions both sources so the full arc is preserved.
"""
from __future__ import annotations

import json

from movie_os.genesis2.bridge import Genesis2Bridge
from movie_os.genesis2.freeze_gate import reconcile_requirements, _requirements_from_brief
from movie_os.genesis2.models import (
    NarrativeExpansion,
    PhaseResult,
    PhaseStatus,
    ProductionKnowledgePackage,
    Scene,
    ScenePlan,
    ScenePlanning,
)
from movie_os.genesis2.requirement_manifest import compile_episode_requirements


def _make_pkg() -> ProductionKnowledgePackage:
    """A PKP with a 6-scene NarrativeExpansion arc and a 3-scene ScenePlanning."""
    ne = NarrativeExpansion(
        scenes=[
            Scene(scene_number=1, act="A1", objective="Mark loses his job, the causal trigger", narrative_beat="hook"),
            Scene(scene_number=2, act="A2", objective="Mark conceals and avoids discussing the job loss", narrative_beat="plot"),
            Scene(scene_number=3, act="A2", objective="Sarah detects Mark's withdrawal and distance", narrative_beat="plot"),
            Scene(scene_number=4, act="A2", objective="Mark withdraws further, the distance worsens", narrative_beat="plot"),
            Scene(scene_number=5, act="A3", objective="Sarah confronts Mark directly, his fear becomes visible", narrative_beat="turning_point"),
            Scene(scene_number=6, act="A3", objective="Mark and Sarah reconnect, reaching for each other", narrative_beat="climax"),
        ]
    )
    sp = ScenePlanning(
        scenes=[
            ScenePlan(scene_number=1, title="S1", narrative_beat="hook"),
            ScenePlan(scene_number=2, title="S2", narrative_beat="plot"),
            ScenePlan(scene_number=3, title="S3", narrative_beat="climax"),
        ]
    )
    return ProductionKnowledgePackage(
        episode_id="EP-1", run_id="RUN-1", policy_snapshot_id="POL-1",
        synopsis="Mark withdraws from Sarah after losing his job.",
        constraints={"mode": "RUNTIME"},
        narrative_expansion=ne,
        scene_planning=sp,
        phase_results=[
            PhaseResult(phase_number=5, phase_name="Narrative Expansion", status=PhaseStatus.COMPLETED),
            PhaseResult(phase_number=6, phase_name="Scene Planning", status=PhaseStatus.COMPLETED),
        ],
    )


def test_bridge_preserves_full_narrative_arc():
    pkg = _make_pkg()
    brief = Genesis2Bridge(pkg).to_brief()
    scenes = brief["scenes"]
    assert len(scenes) == 6, f"expected 6 scenes, got {len(scenes)}"
    beats = [s.get("narrative_beat") for s in scenes]
    assert "turning_point" in beats, f"turning_point dropped: {beats}"
    assert "climax" in beats, f"climax dropped: {beats}"


def test_bridge_does_not_drop_scenes_4_5_6():
    pkg = _make_pkg()
    brief = Genesis2Bridge(pkg).to_brief()
    nums = sorted(s.get("scene_number") for s in brief["scenes"])
    assert nums == [1, 2, 3, 4, 5, 6], f"scene numbers collapsed: {nums}"


def test_req006_and_req008_realized_after_fix():
    pkg = _make_pkg()
    brief = Genesis2Bridge(pkg).to_brief()
    manifest = compile_episode_requirements(
        episode_id="EP-1", synopsis=pkg.synopsis, contract={"working_title": "Test"}
    )
    brief["canonical_requirements"] = [r.to_dict() for r in manifest.requirements]
    reqs = _requirements_from_brief(brief)
    result = reconcile_requirements(pkg, reqs, brief)
    reqs_map = result.get("requirements", {})
    assert reqs_map.get("REQ-006", {}).get("realized") is True, "REQ-006 not realized"
    assert reqs_map.get("REQ-008", {}).get("realized") is True, "REQ-008 not realized"
    assert result.get("passed") is True, f"reconciliation failed: {result.get('missing_requirements')}"


def test_bridge_merges_sceneplanning_details():
    pkg = _make_pkg()
    brief = Genesis2Bridge(pkg).to_brief()
    scenes = {s.get("scene_number"): s for s in brief["scenes"]}
    # ScenePlanning titles applied to scenes 1-3
    assert scenes[1].get("title") == "S1"
    assert scenes[2].get("title") == "S2"
    assert scenes[3].get("title") == "S3"
    # Scenes 4-6 (NarrativeExpansion-only) still present with objective-derived title
    assert scenes[4].get("scene_number") == 4
    assert scenes[5].get("scene_number") == 5
    assert scenes[6].get("scene_number") == 6
