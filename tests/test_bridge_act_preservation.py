"""Regression test for the bridge act-flattening bug (P0-03).

The bridge's acts/sequences fallback used the per-act sequence index as the
scene key, so every act overwrote the same scenes (1,2,3) and the LAST act
iterated won — reversing act order and dropping titles. After the fix, scenes
flatten in narrative order with stable increasing indices and preserved act
labels.
"""
from __future__ import annotations

import json

from movie_os.genesis2.bridge import Genesis2Bridge, _normalize_act_label


def test_act_label_normalization():
    assert _normalize_act_label("Act I: The Silent Wall") == "Act I"
    assert _normalize_act_label("Act III: The Truth or Nothing") == "Act III"
    assert _normalize_act_label("Act 2") == "Act 2"
    assert _normalize_act_label("") == "Act I"


def _pkg_with_nested_acts():
    """A PKP whose narrative_expansion has only nested acts/sequences (no flat scenes)."""
    from movie_os.genesis2.models import (
        ProductionKnowledgePackage,
        NarrativeExpansion,
        CreativeUnderstanding,
        StoryFoundation,
        ScenePlanning,
        DialoguePlanning,
    )

    # narrative_expansion holds acts with sequences; scene_planning is EMPTY,
    # so the bridge must flatten the acts in order.
    ne = NarrativeExpansion(
        purpose="x", creative_intent="y", reasoning="z", confidence="inferred",
        acts=[
            {
                "name": "Act I: The Silent Wall",
                "act": "Act I",
                "sequences": [{"name": "Sequence 1: The Morning Routine"}],
            },
            {
                "name": "Act II: The Unraveling",
                "act": "Act II",
                "sequences": [{"name": "Sequence 2: The Impossible Choice"}],
            },
            {
                "name": "Act III: The Truth or Nothing",
                "act": "Act III",
                "sequences": [{"name": "Sequence 3: The Confrontation"}],
            },
        ],
        sequences=[], scenes=[],
    )
    pkg = ProductionKnowledgePackage(
        synopsis="A man withdraws after job loss.",
        narrative_expansion=ne,
        scene_planning=ScenePlanning(scenes=[]),
        dialogue_planning=DialoguePlanning(dialogues=[]),
        creative_understanding=CreativeUnderstanding(),
        story_foundation=StoryFoundation(),
    )
    return pkg


def test_bridge_preserves_act_order_and_titles():
    from movie_os.genesis2.models import ProductionKnowledgePackage

    pkg = _pkg_with_nested_acts()
    bridge = Genesis2Bridge(pkg)
    brief = bridge.to_brief()
    scenes = brief.get("scenes", [])
    assert len(scenes) == 3
    # Order must be Act I -> II -> III (NOT reversed).
    acts = [str(s.get("act")) for s in scenes]
    assert acts[0] == "Act I"
    assert acts[1] == "Act II"
    assert acts[2] == "Act III"
    # Titles preserved.
    titles = [str(s.get("title")) for s in scenes]
    assert "The Morning Routine" in titles[0]
    assert "The Impossible Choice" in titles[1]
    assert "The Confrontation" in titles[2]
