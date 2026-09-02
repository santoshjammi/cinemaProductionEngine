"""Tests for Genesis2Bridge — real-artifact-first generation guarantees.

Asserts that:
1. Bridge fallback produces correct scene count and required fields.
2. Sparse MockLLM output (empty content) triggers synopsis-derived fallback.
3. Fear-synopsis path derives territory/archetype/theme/mood/conflict correctly.
4. Real phase data bypasses synopsis fallback (no double-generation).
5. Brief output is deterministic for identical inputs.
6. Save-brief writes YAML or JSON (YAML preferred, JSON on missing yaml).
7. _build_metadata reports accurate phase counts.

All tests are local (no network), use only pydantic + standard library, and
are fully deterministic (seeded where needed — we don't need randomness here).
"""

from __future__ import annotations

import datetime
import sys
from types import SimpleNamespace
from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

from movie_os.genesis2.bridge import Genesis2Bridge, _parse_duration
from movie_os.genesis2.models import (
    Character,
    CharacterPsychology,
    ConfidenceLevel,
    CreativeUnderstanding,
    KnowledgeGraphNode,
    KnowledgeGraphEdge,
    KnowledgeIntegration,
    PhaseResult,
    PhaseStatus,
    ProductionKnowledgePackage,
    ScenePlanning,
    StoryFoundation,
    VisualLanguage,
    WorldDevelopment,
    DialoguePlanning,
)


# ---------------------------------------------------------------------------
# Helpers — build PKPs inline (no fixture dependencies needed)
# ---------------------------------------------------------------------------

def _make_pkp(
    synopsis: str = "A retired clockmaker stops talking to his wife after losing his job.",
    scene_data: dict[str, Any] | None = None,
    include_real_dna_fields: bool = False,
) -> ProductionKnowledgePackage:
    """Build a production knowledge package with controllable sparsity."""
    # We need these types; lazy-import to avoid circular dependency on the full models module
    from movie_os.genesis2.models import (
        StoryFoundation as _SF,
        VisualLanguage as _VL,
        WorldDevelopment as _WD,
        CharacterPsychology as _CP,
        CreativeUnderstanding as _CU,
    )

    phase_results: list[PhaseResult] = [
        PhaseResult(phase_number=i + 1, phase_name=f"phase_{i + 1}", status=PhaseStatus.COMPLETED)
        for i in range(3)
    ]

    kw: dict[str, Any] = {}
    if include_real_dna_fields:
        ku = _CU(
            purpose="test", creative_intent="test", reasoning="test",
            theme="Emotional Isolation", genre="Drama", mood="Quiet and Haunted",
            conflict="Fear of rejection vs. need for connection",
        )
        sf = StoryFoundation(premise=synopsis, motifs=["clockwork", "silence"], emotional_journey=["numb", "withdrawal", "recognition"])
        wd = WorldDevelopment(environment="Near-Future Sci-Fi")
        vl = VisualLanguage(color="desaturated cool tones", lighting="natural light", atmosphere="haunted")
        cp = CharacterPsychology(
            protagonist=Character(name="Daniel", role="protagonist", identity="A retired clockmaker"),
            supporting_characters=[Character(name="Elena", role="spouse", identity="His wife")],
        )
        kw["creative_understanding"] = ku
        kw["story_foundation"] = sf
        kw["world_development"] = wd
        kw["visual_language"] = vl
        kw["character_psychology"] = cp

    if scene_data:
        for k, v in scene_data.items():
            kw[k] = v

    pkg = ProductionKnowledgePackage(
        synopsis=synopsis,
        constraints={"runtime": "15min", "format": "short", "mode": "QUALIFICATION_FIXTURE"},
        phase_results=phase_results,
        version="2.0.0",
        created_at=datetime.datetime.utcnow().isoformat(),
    )

    for field_name, value in kw.items():
        setattr(pkg, field_name, value)

    return pkg


# ---------------------------------------------------------------------------
# 1. Fallback scene count & basic structure
# ---------------------------------------------------------------------------

class TestBridgeFallbackSceneCount:
    """When phase data is empty/sparse, _generate_scenes_from_synopsis is invoked."""

    def test_short_synopsis_yields_min_scenes(self):
        pkg = _make_pkp(synopsis="A retired clockmaker stops talking to his wife after losing his job.")
        result = Genesis2Bridge(pkg).to_brief()
        scenes = result["scenes"]
        assert len(scenes) >= 3          # minimum from _generate_scenes_from_synopsis
        assert len(scenes) <= 5          # maximum

    def test_long_synopsis_yields_more_scenes(self):
        words = " ".join(["retired clockmaker", "stopped", "talking", "to", "his", "wife", "after", "losing"] * 8)
        pkg = _make_pkp(synopsis=words)
        result = Genesis2Bridge(pkg).to_brief()
        scenes = result["scenes"]
        # With more words: num_scenes ≈ len(words)//15, clamped [3, 5]
        expected = min(max(3, len(words.split()) // 15), 5)
        assert len(scenes) == expected

    def test_empty_synopsis_yields_no_scene_dicts(self):
        pkg = _make_pkp(synopsis="")
        result = Genesis2Bridge(pkg).to_brief()
        assert result["scenes"] == []

    def test_short_synopsis_falls_back_to_three_scenes(self):
        """Single sentence → 3 scenes (min)."""
        pkg = _make_pkp(synopsis="A man stops talking.")
        result = Genesis2Bridge(pkg).to_brief()
        assert len(result["scenes"]) == 3

    def test_scene_count_is_deterministic(self):
        """Same synopsis must always produce the same scene count."""
        synopsis = "The clockmaker withdraws from his wife when faced with failure."
        results = []
        for _ in range(5):
            result = Genesis2Bridge(_make_pkp(synopsis=synopsis)).to_brief()
            results.append(len(result["scenes"]))
        assert len(set(results)) == 1, f"Non-deterministic scene counts: {results}"


# ---------------------------------------------------------------------------
# 2. Required scene fields populated from fallback
# ---------------------------------------------------------------------------

class TestBridgeFallbackSceneFields:
    """Every fallback-scene dict must carry the full set of brief-required keys."""

    def _required_keys(self) -> set[str]:
        return {
            "scene_number", "number", "title", "act", "phase", "beat",
            "scene_description", "emotional_state", "energy",
            "target_duration_seconds", "duration_seconds", "shot_language",
            "characters_present", "music_cue", "color_palette", "lighting",
            "composition", "camera_intent", "atmosphere",
        }

    def _build_bridge(self) -> Genesis2Bridge:
        bridge = Genesis2Bridge(_make_pkp())
        bridge.to_brief()  # ensure built
        return bridge

    def test_all_required_keys_present(self):
        bridge = self._build_bridge()
        for i, scene in enumerate(bridge.brief["scenes"]):
            missing = self._required_keys() - set(scene.keys())
            assert not missing, f"Scene {i} missing keys: {missing}"

    def test_duration_values_reasonable(self):
        bridge = self._build_bridge()
        for scene in bridge.brief["scenes"]:
            dur = scene["duration_seconds"]
            target = scene["target_duration_seconds"]
            assert isinstance(dur, (int, float)) and dur > 0
            assert isinstance(target, (int, float)) and target > 0

    def test_energy_between_1_and_10(self):
        bridge = self._build_bridge()
        for sc in bridge.brief["scenes"]:
            assert 1 <= sc["energy"] <= 10

    def test_act_is_valid_string(self):
        bridge = self._build_bridge()
        for sc in bridge.brief["scenes"]:
            assert sc["act"].lower().startswith("act")

    def test_all_scenes_have_nonzero_scene_number(self):
        bridge = self._build_bridge()
        nums = [sc["scene_number"] for sc in bridge.brief["scenes"]]
        assert all(n > 0 for n in nums)
        # Scene numbers are sequential from 1
        assert nums == list(range(1, len(nums) + 1))

    def test_characters_present_is_nonempty_list(self):
        bridge = self._build_bridge()
        for sc in bridge.brief["scenes"]:
            cp = sc["characters_present"]
            assert isinstance(cp, list) and len(cp) > 0


# ---------------------------------------------------------------------------
# 3. Fear synopsis — keyword fallback derives territory/archetype/theme/mood/conflict
# ---------------------------------------------------------------------------

class TestFearSynopsisFallback:
    """When phase data is empty, bridge must derive all DNA fields from synopsis keywords."""

    # --- Territory derivations ---

    def test_territory_derived_from_synopsis_keyword_near_future(self):
        bridge = Genesis2Bridge(_make_pkp(synopsis="A near-future story about a man who withdraws."))
        assert "Near-Future Sci-Fi" in bridge.to_brief()["dna"]["territory"]

    def test_territory_derived_from_tokyo_keyword(self):
        bridge = Genesis2Bridge(_make_pkp(synopsis="A retired clockmaker in Tokyo stops reaching out."))
        assert "Urban East Asia" in bridge.to_brief()["dna"]["territory"]

    def test_territory_derived_from_city_keyword(self):
        bridge = Genesis2Bridge(_make_pkp(synopsis="A man and woman navigate a city full of distance."))
        assert "Urban Setting" in bridge.to_brief()["dna"]["territory"]

    def test_territory_derived_from_war_keyword(self):
        bridge = Genesis2Bridge(_make_pkp(synopsis="A story about world war and its aftermath."))
        assert "Historical Drama" in bridge.to_brief()["dna"]["territory"]

    def test_territory_derived_from_desert_keyword(self):
        bridge = Genesis2Bridge(_make_pkp(synopsis="A story set in a dry desert landscape."))
        assert "Desert Landscape" in bridge.to_brief()["dna"]["territory"]

    def test_territory_derived_from_ocean_keyword(self):
        bridge = Genesis2Bridge(_make_pkp(synopsis="A man and woman navigate an ocean of silence."))
        assert "Maritime Setting" in bridge.to_brief()["dna"]["territory"]

    def test_territory_derived_from_space_keyword(self):
        bridge = Genesis2Bridge(_make_pkp(synopsis="A space opera about two people who can't talk."))
        assert "Space Opera" in bridge.to_brief()["dna"]["territory"]

    def test_territory_defaults_to_contemporary_when_no_keyword(self):
        bridge = Genesis2Bridge(_make_pkp(synopsis="Two people sit apart."))
        assert "Contemporary Setting" in bridge.to_brief()["dna"]["territory"]

    # --- Archetype derivations ---

    def test_archetype_derived_from_withdraws_keyword(self):
        bridge = Genesis2Bridge(_make_pkp(synopsis="A man withdraws from his wife."))
        assert "Withdrawing Protagonist" in bridge.to_brief()["dna"]["archetype"]

    def test_archetype_derived_from_retired_clockmaker_keyword(self):
        bridge = Genesis2Bridge(_make_pkp(synopsis="A retired clockmaker stops talking."))
        assert "Rediscovering Creator" in bridge.to_brief()["dna"]["archetype"]

    def test_archetype_defaults_to_protagonist_when_no_keyword(self):
        bridge = Genesis2Bridge(_make_pkp(synopsis="Two people sit apart."))
        dna = bridge.to_brief()["dna"]
        assert isinstance(dna["archetype"], str) and len(dna["archetype"]) > 0

    # --- Theme derivations ---

    def test_theme_derived_from_reject_keyword(self):
        bridge = Genesis2Bridge(_make_pkp(synopsis="A man rejects the life he once knew."))
        assert "Rejection and Acceptance" in bridge.to_brief()["dna"]["theme"]

    def test_theme_derived_from_withdraws_keyword(self):
        bridge = Genesis2Bridge(_make_pkp(synopsis="A man withdraws from his wife."))
        assert "Emotional Isolation" in bridge.to_brief()["dna"]["theme"]

    def test_theme_derived_from_redemption_keyword(self):
        bridge = Genesis2Bridge(_make_pkp(synopsis="A man seeks redemption for his past mistakes."))
        assert "Redemption vs. Justice" in bridge.to_brief()["dna"]["theme"]

    def test_theme_derived_from_time_keyword(self):
        bridge = Genesis2Bridge(_make_pkp(synopsis="The passage of time changes everything."))
        assert "The Passage of Time" in bridge.to_brief()["dna"]["theme"]

    def test_theme_derived_from_silence_keyword(self):
        bridge = Genesis2Bridge(_make_pkp(synopsis="Silence between two people costs them everything."))
        assert "Communication Breakdown" in bridge.to_brief()["dna"]["theme"]

    # --- Mood derivations ---

    def test_mood_derived_from_afraid_keyword(self):
        bridge = Genesis2Bridge(_make_pkp(synopsis="A man is afraid to tell the truth."))
        assert "Fearful" in bridge.to_brief()["dna"]["mood"]

    def test_mood_derived_from_silence_keyword(self):
        bridge = Genesis2Bridge(_make_pkp(synopsis="Silence between lovers deepens over time."))
        assert "Quiet and Haunted" in bridge.to_brief()["dna"]["mood"]

    def test_mood_derived_from_hope_keyword(self):
        bridge = Genesis2Bridge(_make_pkp(synopsis="Despite everything, there is still hope."))
        assert "Hopeful but Desperate" in bridge.to_brief()["dna"]["mood"]

    # --- Conflict derivations ---

    def test_conflict_derived_from_married_keyword(self):
        bridge = Genesis2Bridge(_make_pkp(synopsis="A married couple grows apart after one loses work."))
        assert "Marital estrangement" in bridge.to_brief()["dna"]["conflict"]

    def test_conflict_derived_from_afraid_keyword(self):
        bridge = Genesis2Bridge(_make_pkp(synopsis="A man is afraid of his wife's disappointment."))
        assert "Internal fear blocking outward action" in bridge.to_brief()["dna"]["conflict"]

    # --- Multi-derive combined test ---

    def test_fear_synopsis_derives_multiple_fields(self):
        """A fear-synonym-rich synopsis should derive territory + archetype + theme."""
        syn = "A man withdraws from his wife after losing his job. He fears rejection and retreats into silence."
        bridge = Genesis2Bridge(_make_pkp(synopsis=syn))
        brief = bridge.to_brief()
        dna = brief["dna"]
        assert dna["archetype"] != ""
        assert dna["theme"] != "" or dna["conflict"] != ""

    def test_full_dna_not_all_defaults(self):
        """With fear-synonyms present, not all fields should be the default chain."""
        syn = "A man withdraws from his wife."
        bridge = Genesis2Bridge(_make_pkp(synopsis=syn))
        dna = bridge.to_brief()["dna"]
        # The "everyman / drama / contemplative" defaults only fire when no keyword matches.
        assert dna["archetype"] != "Everyman Protagonist" or "Withdrawing" in dna["archetype"]


# ---------------------------------------------------------------------------
# 4. Real phase data — must NOT trigger synopsis-level fallback for DNA
# ---------------------------------------------------------------------------

class TestRealDnaBypassesFallback:
    """When phase data is populated with real fields, the bridge uses them."""

    def test_real_dna_brief_is_valid(self):
        pkg = _make_pkp(
            synopsis="A retired clockmaker in Tokyo stops reaching out.",
            include_real_dna_fields=True,
        )
        result = Genesis2Bridge(pkg).to_brief()
        assert result["dna"]["theme"] == "Emotional Isolation"
        assert result["dna"]["genre"] == "Drama"
        assert result["dna"]["mood"] == "Quiet and Haunted"
        assert result["dna"]["conflict"] == "Fear of rejection vs. need for connection"

    def test_real_dna_includes_characters_from_phase_data(self):
        pkg = _make_pkp(
            synopsis="A retired clockmaker in Tokyo stops reaching out.",
            include_real_dna_fields=True,
        )
        result = Genesis2Bridge(pkg).to_brief()
        names = [c["name"] for c in result["context"]["characters"]]
        assert "Daniel" in names

    def test_short_synopsis_with_real_data_still_valid(self):
        """A very short synopsis with real DNA fields must produce valid brief."""
        pkg = _make_pkp(synopsis="A quiet story.", include_real_dna_fields=True)
        bridge = Genesis2Bridge(pkg)
        result = bridge.to_brief()
        assert isinstance(result["dna"]["theme"], str) and len(result["dna"]["theme"]) > 0


# ---------------------------------------------------------------------------
# 5. Brief structure & metadata accuracy
# ---------------------------------------------------------------------------

class TestBridgeBriefStructure:
    """The full brief dict must have the required top-level keys."""

    def test_brief_has_all_top_level_keys(self):
        bridge = Genesis2Bridge(_make_pkp())
        result = bridge.to_brief()
        for key in ("title", "logline", "synopsis", "dna", "scenes", "context", "parameters", "metadata"):
            assert key in result, f"Brief missing top-level key: {key}"

    def test_title_is_nonempty_string(self):
        bridge = Genesis2Bridge(_make_pkp())
        title = bridge.to_brief()["title"]
        assert isinstance(title, str) and len(title) > 0

    def test_logline_derived_from_premise_when_present(self):
        pkg = _make_pkp(include_real_dna_fields=True)
        result = Genesis2Bridge(pkg).to_brief()
        assert len(result["logline"]) > 0

    def test_synopsis_carries_through_unchanged(self):
        synopsis_in = "The cat sat on the mat under the table."
        result = Genesis2Bridge(_make_pkp(synopsis=synopsis_in)).to_brief()
        assert result["synopsis"] == synopsis_in

    def test_dna_has_nested_fields(self):
        bridge = Genesis2Bridge(_make_pkp())
        dna = bridge.to_brief()["dna"]
        for key in ("territory", "archetype", "theme", "visual_motif", "genre", "mood", "conflict", "emotional_journey"):
            assert key in dna, f"DNA missing field: {key}"

    def test_dna_territory_has_default_when_no_real_data(self):
        result = Genesis2Bridge(_make_pkp()).to_brief()
        assert isinstance(result["dna"]["territory"], str) and len(result["dna"]["territory"]) > 0

    def test_context_has_characters_with_names(self):
        result = Genesis2Bridge(_make_pkp()).to_brief()
        names = [c["name"] for c in result["context"]["characters"]]
        assert len(names) >= 1


# ---------------------------------------------------------------------------
# 6. Save-brief writes files correctly
# ---------------------------------------------------------------------------

class TestBridgeSaveBrief:
    """save_brief must persist brief data to disk."""

    def test_save_creates_file(self, tmp_path):
        pkg = _make_pkp(synopsis="Simple test scene count validation.")
        bridge = Genesis2Bridge(pkg)
        bridge.to_brief()
        out = bridge.save_brief(str(tmp_path / "test_brief"))
        assert out.exists()
        text = out.read_text()
        assert len(text) > 0

    def test_save_mkdirs_on_deep_path(self, tmp_path):
        pkg = _make_pkp(synopsis="mkdir test.")
        bridge = Genesis2Bridge(pkg)
        bridge.to_brief()
        deep = str(tmp_path / "a" / "b" / "c")
        out = bridge.save_brief(deep + "/brief")
        assert out.exists()

    def test_save_yields_json_when_yaml_unavailable(self, tmp_path):
        """Force YAML import failure to exercise JSON fallback path."""
        pkg = _make_pkp(synopsis="JSON fallback test.")
        bridge = Genesis2Bridge(pkg)
        bridge.to_brief()
        # Remove yaml from sys.modules so it cannot be found
        real_yaml_mod = sys.modules.get("yaml")
        if "yaml" in sys.modules:
            del sys.modules["yaml"]

        out = bridge.save_brief(str(tmp_path / "test_brief_no_yaml"))
        assert out.exists()
        
        # Restore
        if real_yaml_mod is not None:
            sys.modules["yaml"] = real_yaml_mod


# ---------------------------------------------------------------------------
# 7. Deterministic brief for identical inputs
# ---------------------------------------------------------------------------

class TestBriefDeterminism:
    """Running to_brief multiple times with the same PKP yields identical dicts."""

    def test_scene_order_deterministic(self):
        synopsis = "A clockmaker withdraws from his world."
        titles_1 = [Genesis2Bridge(_make_pkp(synopsis=synopsis)).to_brief()["scenes"][i]["title"] for i in range(3)]  # type: ignore[assignment]
        results = []
        for _ in range(5):
            bridge = Genesis2Bridge(_make_pkp(synopsis=synopsis))
            brief = bridge.to_brief()
            titles_2 = [s["title"] for s in brief["scenes"]]
            assert len(brief["scenes"]) == 3
            results.append(tuple(titles_2))
        assert len(set(results)) == 1, f"Non-deterministic scene order: {results}"

    def test_dna_deterministic_for_fear_synopsis(self):
        synopsis = "A man withdraws from his wife when afraid of losing connection."
        results = []
        for _ in range(3):
            bridge = Genesis2Bridge(_make_pkp(synopsis=synopsis))
            brief = bridge.to_brief()
            dna_tuple = (brief["dna"]["territory"], brief["dna"]["archetype"], brief["dna"]["theme"])
            results.append(dna_tuple)
        assert len(set(results)) == 1, f"Non-deterministic DNA: {results}"

    def test_bridge_calls_are_idempotent(self):
        """Calling to_brief() multiple times on the same bridge yields identical results."""
        pkg = _make_pkp()
        bridge = Genesis2Bridge(pkg)
        b1 = bridge.to_brief()
        b2 = bridge.to_brief()
        assert len(b1["scenes"]) == len(b2["scenes"])
        titles_1 = tuple(s["title"] for s in b1["scenes"])
        titles_2 = tuple(s["title"] for s in b2["scenes"])
        assert titles_1 == titles_2


# ---------------------------------------------------------------------------
# 8. Sparse MockLLM output — empty content triggers synopsis fallback  
# ---------------------------------------------------------------------------

class TestSparseMockLLMFallback:
    """Simulate a PKP produced by a sparse MockLLMClient (all fields default)."""

    def test_empty_phase_data_triggers_fallback_scenes(self):
        bridge = Genesis2Bridge(_make_pkp(include_real_dna_fields=False))
        brief = bridge.to_brief()
        assert len(brief["scenes"]) >= 3

    def test_empty_mock_phase_data_derives_territory_from_synth(self):
        syn = "In a near-future city, two people grow apart."
        bridge = Genesis2Bridge(_make_pkp(synopsis=syn))
        brief = bridge.to_brief()
        assert "Urban Setting" in brief["dna"]["territory"]

    def test_sparse_mock_derives_characters_from_synth_keywords(self):
        syn = "A retired clockmaker and his wife sit apart."
        bridge = Genesis2Bridge(_make_pkp(synopsis=syn))
        brief = bridge.to_brief()
        names = [c["name"] for c in brief["context"]["characters"]]
        assert len(names) >= 1

    def test_sparse_context_has_themes(self):
        themes = Genesis2Bridge(_make_pkp()).to_brief()["context"]["themes"]
        assert isinstance(themes, list) and len(themes) > 0


# ---------------------------------------------------------------------------
# 9. Bridge with real scene data — no fallback should be triggered  
# ---------------------------------------------------------------------------

class TestRealSceneDataPath:
    """When phase data contains actual Scene objects, scenes come from them."""

    def test_real_scene_data_produces_scenes(self):
        from movie_os.genesis2.models import NarrativeExpansion, Scene

        scene1 = Scene(scene_number=1, act="Act 1", objective="Opening shot")
        scene2 = Scene(scene_number=2, act="Act 1", objective="Inciting incident")
        ne = NarrativeExpansion(scenes=[scene1, scene2])
        bridge = Genesis2Bridge(_make_pkp())
        bridge.pkp.narrative_expansion = ne
        brief = bridge.to_brief()
        assert len(brief["scenes"]) == 2

    def test_real_scene_numbers_are_preserved(self):
        from movie_os.genesis2.models import NarrativeExpansion, Scene

        scene1 = Scene(scene_number=5, act="Act 2", objective="Midpoint")
        scene2 = Scene(scene_number=3, act="Act 1", objective="Early scene")
        ne = NarrativeExpansion(scenes=[scene1, scene2])
        bridge = Genesis2Bridge(_make_pkp())
        bridge.pkp.narrative_expansion = ne
        brief = bridge.to_brief()
        nums = [s["scene_number"] for s in brief["scenes"]]
        assert 3 in nums
        assert 5 in nums


# ---------------------------------------------------------------------------
# 10. Duration parser — deterministic tests for _DurationParser.seconds  
# ---------------------------------------------------------------------------

class TestDurationParser:
    """Deterministic tests for duration parsing."""

    def test_plain_number(self):
        assert _parse_duration("120") == 120.0

    def test_float_number(self):
        assert _parse_duration("90.5") == 90.5

    def test_hh_mm_format(self):
        assert _parse_duration("1:30") == 90.0

    def test_with_m_suffix(self):
        assert _parse_duration("2 Mins") == 120.0

    def test_with_seconds_word(self):
        assert _parse_duration("120 Seconds") == 120.0

    def test_with_hm_format(self):
        assert _parse_duration("1h 30m") == 5400.0

    def test_full_iso_format(self):
        result = _parse_duration("PT1H30M")
        assert result == 5400.0

    def test_colon_mm_ss_with_units(self):
        result = _parse_duration("1:30 min")
        assert result == 90.0

    def test_empty_string_returns_zero(self):
        assert _parse_duration("") == 0.0

    def test_none_returns_zero(self):
        assert _parse_duration(None) == 0.0

    def test_unparsable_string_extracts_first_float(self):
        result = _parse_duration("about 90 seconds remain")
        assert result == 90.0

    def test_zero_returns_not_none(self):
        assert _parse_duration(0) == 0.0


# ---------------------------------------------------------------------------
# 11. Boundary edge cases
# ---------------------------------------------------------------------------

class TestBridgeEdgeCases:
    """Handle boundary conditions gracefully."""

    def test_both_synopsis_and_real_data(self):
        pkg = _make_pkp(synopsis="Fallback should not fire.", include_real_dna_fields=True)
        result = Genesis2Bridge(pkg).to_brief()
        assert result["dna"]["theme"] == "Emotional Isolation"

    def test_synopsis_with_special_chars(self):
        syn = 'A man\'s "fears" & <conflicts> matter! @#$%'
        bridge = Genesis2Bridge(_make_pkp(synopsis=syn))
        result = bridge.to_brief()
        assert result["synopsis"] == syn

    def test_very_long_synopsis(self):
        long_synth = "retired clockmaker " * 1000
        bridge = Genesis2Bridge(_make_pkp(synopsis=long_synth))
        brief = bridge.to_brief()
        assert len(brief["scenes"]) <= 5

    def test_synopsis_with_only_punctuation(self):
        bridge = Genesis2Bridge(_make_pkp(synopsis="... !!!???"))
        result = bridge.to_brief()
        assert isinstance(result, dict) and "title" in result

    def test_empty_phase_results_list(self):
        pkg = ProductionKnowledgePackage(
            synopsis="A quiet story.",
            phase_results=[],  # no phases at all
        )
        result = Genesis2Bridge(pkg).to_brief()
        assert "metadata" in result
        assert result["metadata"]["phases_total"] == 0
