"""Rich Mock LLM — a MockLLMClient pre-loaded with valid responses.

Used by `python -m movie_os.genesis run --mock` so the pipeline can run
end-to-end without a real LLM. Returns valid JSON for every known agent.
"""

from __future__ import annotations

import json
from typing import Any

from .llm_client import MockLLMClient


# Each agent name -> JSON string that satisfies its validate() required fields.
DISCOVERY_RESPONSES: dict[str, str] = {
    "intent_analyst": json.dumps({
        "intent": "To make the audience feel the cost of emotional withdrawal",
        "emotional_transformation": "Recognition that silence is a choice",
        "territory": "The Quiet Marriage",
        "theme": "Withdrawal as a form of communication",
        "confidence": "inferred",
    }),
    "theme_analyst": json.dumps({
        "primary_theme": "Withdrawal as a form of communication",
        "secondary_themes": ["Silence as punishment", "Love expressed through absence"],
        "motifs": ["Empty chair", "Cold coffee", "Closed doors"],
        "psychological_truth": "The things we don't say shape us as much as the things we do",
        "confidence": "inferred",
    }),
    "emotion_analyst": json.dumps({
        "beginning_emotion": "Numb comfort",
        "middle_emotion": "Quiet resentment",
        "end_emotion": "Bittersweet recognition",
        "modulation_points": ["Job loss", "First argument", "Therapy session"],
        "irreversible_moment": "He leaves for the car and doesn't come back",
        "almost_moment": "She almost reaches for his hand at dinner",
        "confidence": "inferred",
    }),
    "conflict_analyst": json.dumps({
        "central_conflict": "Man withdraws after job loss; wife interprets as abandonment",
        "internal_conflicts": ["Shame vs. need for support", "Pride vs. vulnerability"],
        "external_conflicts": ["Man vs. wife", "Man vs. unemployment system"],
        "power_dynamics": "Wife holds emotional authority; man holds informational authority",
        "trigger": "Layoff notice",
        "confidence": "inferred",
    }),
    "audience_analyst": json.dumps({
        "target_audience": "Adults 30-55 who have experienced relationship strain",
        "emotional_state": "Reflective, possibly recognizing their own patterns",
        "desired_transformation": "Awareness that withdrawal is a choice with consequences",
        "objections": ["Too slow", "Too on-the-nose", "Unsympathetic protagonist"],
        "confidence": "inferred",
    }),
    "gap_analyst": json.dumps({
        "explicit": ["Man loses job", "Wife notices withdrawal"],
        "inferred": ["Couple has been married 12 years", "Man has avoidant attachment"],
        "confirmed": ["Setting is urban middle class"],
        "assumed": ["Therapy is a viable plot point"],
        "unknown": ["Specific city", "Names of secondary characters"],
        "critical_gaps": ["Whether couple has children", "Whether reconciliation occurs"],
        "confidence": "inferred",
    }),
    "question_planner": json.dumps({
        "questions": [
            {
                "question": "Does the couple have children?",
                "why_it_matters": "Determines scene composition and stakes",
                "confidence_pct": 40.0,
                "suggested_default": "No children",
            }
        ],
        "confidence": "inferred",
    }),
}


PKP_RESPONSES: dict[str, dict[str, Any]] = {
    "vision_agent": {
        "vision_statement": "Illuminate the cost of emotional withdrawal in long-term relationships",
        "core_purpose": "Make the invisible labor of emotional avoidance visible",
        "intended_impact": "Audiences recognize their own patterns of silence",
        "audience_transformation": "From passive recognition to active choice",
        "creative_philosophy": "Restraint over exposition",
        "success_definition": "A single viewer changes how they argue",
        "non_negotiable_principles": ["Psychological truth over plot", "Silence is a character"],
        "confidence": "inferred",
    },
    "creative_strategy_agent": {
        "strategic_positioning": "Adult drama adjacent to Character Studies",
        "genre_tone_strategy": "Domestic realism with structural restraint",
        "thematic_priorities": ["Withdrawal", "Recognition", "Choice"],
        "audience_targeting": "Festival + streaming adults 30-55",
        "differentiation": "Anti-catharsis — withholds resolution",
        "emotional_journey": "Numb → Resentment → Recognition",
        "creative_pillars": ["Silence", "Interiority", "Daily ritual"],
        "confidence": "inferred",
    },
    "project_agent": {
        "title": "Quiet Rooms",
        "logline": "A man stops talking to his wife. She waits.",
        "format": "Short film",
        "target_runtime": "15 minutes",
        "language": "English",
        "target_audience": "Adults 30-55, festival programmers",
        "platform": "Festival + VOD",
        "budget_tier": "Indie",
        "production_scope": "Two leads, single location, 4 shoot days",
        "confidence": "inferred",
    },
    "research_agent": {
        "research_domains": ["Attachment theory", "Gottman methodology", "Withdrawal patterns"],
        "key_findings": [
            "Stonewalling is a predictable response to flooding",
            "Avoidant attachment is learned, not innate",
        ],
        "factual_anchors": [
            "Gottman identifies stonewalling as one of the Four Horsemen",
            "Bowlby: avoidant attachment forms in early childhood",
        ],
        "cultural_context": "Post-pandemic, urban, middle-class",
        "technical_references": ["Aftersun (2022)", "Marriage Story (2019)"],
        "confidence": "inferred",
    },
    "story_agent": {
        "premise": "A man withdraws after job loss; his wife interprets silence as abandonment",
        "central_conflict": "Silence as communication failure",
        "story_goal": "Force a reckoning between withdrawal and presence",
        "story_spine": "Begin: comfort → Middle: rupture → End: recognition without resolution",
        "plot_beats": ["Layoff", "First silent dinner", "Therapy referral", "Departure"],
        "thematic_spine": "What we don't say is what we become",
        "stakes": "The marriage",
        "confidence": "inferred",
    },
    "world_agent": {
        "world_premise": "A quiet urban marriage in slow rupture",
        "geography": "Pacific Northwest, US",
        "time_period": "Present day, autumn",
        "social_structures": "Dual-income professional class, no nearby family",
        "technology_level": "Contemporary, smartphone-saturated",
        "rules_of_the_world": "No third-act confession; the world stays unresolved",
        "key_locations": ["Apartment", "Car", "Therapist office", "Sidewalk"],
        "confidence": "inferred",
    },
    "character_agent": {
        "characters": [
            {
                "name": "Daniel", "age": 42, "role": "protagonist",
                "wound": "Father's emotional absence",
                "want": "Be left alone", "need": "Be reached",
                "arc": "From defended to exposed (not resolved)",
                "internal_obstacle": "Shame",
                "external_obstacle": "Unemployment",
            },
            {
                "name": "Elena", "age": 39, "role": "spouse",
                "wound": "Pattern of being left",
                "want": "Connection", "need": "Self-trust",
                "arc": "From pursuit to stillness",
            },
        ],
        "confidence": "inferred",
    },
    "relationship_agent": {
        "relationships": [
            {
                "names": ["Daniel", "Elena"],
                "type": "marriage",
                "duration_years": 12,
                "attachment_styles": {"Daniel": "avoidant", "Elena": "anxious"},
                "power_dynamics": "Elena holds emotional authority; Daniel holds information",
                "communication_patterns": "Stonewalling vs. pursuit",
                "turning_point": "Daniel sleeps in the guest room",
                "symbols": ["The dinner table", "The bed they no longer share"],
            }
        ],
        "confidence": "inferred",
    },
    "psychology_agent": {
        "psychology_profiles": [
            {
                "character": "Daniel",
                "framework": "Attachment theory",
                "attachment_style": "avoidant",
                "defense_mechanisms": ["Intellectualization", "Withdrawal", "Rationalization"],
                "triggers": ["Perceived criticism", "Feeling responsible for partner's pain"],
            },
            {
                "character": "Elena",
                "framework": "Attachment theory",
                "attachment_style": "anxious",
                "defense_mechanisms": ["Pursuit", "Hypervigilance"],
                "triggers": ["Silence", "Emotional distance"],
            },
        ],
        "confidence": "inferred",
    },
    "narrative_agent": {
        "narrative_structure": "Three-act with withheld catharsis",
        "scene_sequence": ["Open in silence", "Dinner", "Therapy", "Departure"],
        "pov_strategy": "Daniel close third",
        "pacing_curve": "Slow build, plateau, single escalation, open end",
        "dramatic_beats": ["Layoff reveal", "First silent meal", "Therapy session", "Departure"],
        "climax": "The car, in the parking lot",
        "resolution": "Open — no reconciliation",
        "confidence": "inferred",
    },
    "directorial_agent": {
        "directorial_vision": "Restraint as a creative force; hold past comfort",
        "visual_grammar": "Static frames, long takes, natural light",
        "shot_vocabulary": "Wide masters, late close-ups, held stares",
        "camera_movement": "Slow push-ins, mostly locked",
        "blocking_principles": "Distance between actors encodes emotional state",
        "performance_direction": "Quiet, breath-aware, interior",
        "confidence": "inferred",
    },
    "production_design_agent": {
        "design_concept": "Real locations, lived-in sets, no studio gloss",
        "color_palette": "Muted earth tones, cold blues, occasional amber",
        "set_design": "Two-bedroom apartment, kitchen as primary stage",
        "location_design": "Pacific Northwest urban, autumn light",
        "props_philosophy": "Every object earned; phones often silent",
        "costume_design": "Daniel: muted, slightly oversized; Elena: structured",
        "confidence": "inferred",
    },
    "audio_intent_agent": {
        "sonic_palette": "Room tone, distant city, near-absence of music",
        "music_philosophy": "Sparse, low strings, mostly absent",
        "score_motifs": ["Single cello line, only at climaxes"],
        "diegetic_sound": ["Refrigerator hum", "Clock tick", "Distant traffic"],
        "dialogue_treatment": "Quiet, breath-aware, never shouted",
        "audio_arc": "Near-silence throughout, single brief musical gesture in act three",
        "confidence": "inferred",
    },
    "editing_language_agent": {
        "cutting_philosophy": "Cut on action withheld, hold past comfort",
        "rhythm_principles": "3-5 second holds, hard cuts on emotional shifts",
        "transition_vocabulary": "Match cuts on objects, not faces",
        "montage_rules": "Daily rituals as compressed time",
        "continuity_conventions": "Time-of-day continuity, weather continuity",
        "emotional_pacing": "Long takes for emotional weight, fast cuts for anxiety",
        "confidence": "inferred",
    },
    "animation_intent_agent": {
        "animation_style": "None — live action only",
        "motion_principles": "Natural human movement, no stylized motion",
        "frame_rate_intent": "24fps, shutter 180°",
        "rigging_philosophy": "N/A — no CG characters",
        "effects_animation": "Subtle — falling leaves, condensation, breath vapor",
        "confidence": "inferred",
    },
    "blueprint_agent": {
        "scene_blueprint": [
            {"scene": 1, "location": "Apartment bedroom", "duration_sec": 90, "characters": ["Daniel"]},
            {"scene": 2, "location": "Apartment kitchen", "duration_sec": 120, "characters": ["Daniel", "Elena"]},
            {"scene": 3, "location": "Therapist office", "duration_sec": 180, "characters": ["Daniel", "Therapist"]},
            {"scene": 4, "location": "Car parking lot", "duration_sec": 60, "characters": ["Daniel", "Elena"]},
        ],
        "sequence_ordering": ["Scene 1", "Scene 2", "Scene 3", "Scene 4"],
        "asset_manifest": {
            "locations": ["Apartment", "Therapist office", "Car"],
            "wardrobe": ["Daniel casual", "Elena casual", "Daniel work", "Elena work"],
            "props": ["Phone (silent)", "Coffee mug", "Therapy notepad"],
        },
        "production_phases": ["Pre-production 2 weeks", "Shoot 4 days", "Post 6 weeks"],
        "delivery_milestones": ["Rough cut", "Fine cut", "Lock", "Master"],
        "confidence": "inferred",
    },
    "distribution_agent": {
        "target_platforms": ["Sundance", "Telluride", "TIFF shorts", "MUBI", "VOD"],
        "delivery_formats": ["DCP", "ProRes 422", "H.264 web"],
        "accessibility": ["Open captions", "Audio description"],
        "rating_expectations": "Unrated or TV-14 equivalent",
        "release_strategy": "Festival premiere Q4 2026, then platform release Q1 2027",
        "confidence": "inferred",
    },
    "quality_agent": {
        "quality_criteria": ["Each scene earns its silence", "No expository dialogue", "Sound is a character"],
        "consistency_checks": ["Time-of-day", "Wardrobe", "Wall art", "Weather"],
        "continuity_rules": ["Phone always silent", "Coffee always cooling", "Door always closing"],
        "performance_quality": "Subtext over text; breath as punctuation",
        "acceptance_gates": ["Rough cut review", "Sound mix approval", "Final lock"],
        "confidence": "inferred",
    },
    "knowledge_graph_agent": {
        "node_taxonomy": {
            "types": ["character", "location", "object", "event", "theme"],
            "subtypes": {
                "character": ["protagonist", "spouse", "supporting"],
                "location": ["interior", "exterior", "transit"],
            },
        },
        "edge_taxonomy": {
            "types": ["married_to", "lives_in", "avoids", "drives", "owns", "appears_in"],
        },
        "provenance_policy": "Every node/edge records source spec and confidence",
        "confidence_policy": "5-level (explicit/inferred/confirmed/assumed/unknown)",
        "query_patterns": ["All paths between two characters", "All locations for a character"],
        "graph_invariants": ["Every character must have a want and a need", "Every scene must reference at least one character and one location"],
        "confidence": "inferred",
    },
}


REVIEWER_RESPONSES: dict[str, str] = {
    "story_reviewer": json.dumps({
        "contradictions": [],
        "recommendations": ["Consider a stronger inciting incident"],
        "confidence": "confirmed",
    }),
    "character_reviewer": json.dumps({
        "contradictions": [],
        "recommendations": ["Elena's interiority could be more developed"],
        "confidence": "confirmed",
    }),
    "narrative_reviewer": json.dumps({
        "contradictions": [],
        "recommendations": ["Act two pacing tightens around minute 8"],
        "confidence": "confirmed",
    }),
    "psychology_reviewer": json.dumps({
        "contradictions": [],
        "psychological_issues": [],
        "recommendations": ["Consider showing Daniel's body during stress"],
        "confidence": "confirmed",
    }),
}


CHIEF_ARCHITECT_RESPONSE: str = json.dumps({
    "overall_assessment": "Production ready. Cross-spec consistency confirmed.",
    "consistency_issues": [],
    "scope_drift": [],
    "readiness": True,
    "confidence": "confirmed",
})


def build_rich_mock_llm() -> MockLLMClient:
    """Build a MockLLMClient pre-loaded with valid responses for every agent.

    The mock uses keyword matching on the agent name (which appears in the
    prompt via build_agent_prompt's "# Agent: {name}" header).
    """
    mock = MockLLMClient()

    for name, response in DISCOVERY_RESPONSES.items():
        mock.set_response(name, response)

    for name, payload in PKP_RESPONSES.items():
        mock.set_response(name, json.dumps(payload))

    for name, response in REVIEWER_RESPONSES.items():
        mock.set_response(name, response)

    mock.set_response("chief_architect", CHIEF_ARCHITECT_RESPONSE)

    # Safety net: default returns a valid empty-ish payload
    mock.set_default(json.dumps({"confidence": "unknown", "content": {}}))

    return mock
