"""Deterministic fallback — produces real MARK/SARAH dialogue-driven story/scenes/prompts
when the LLM pipeline is unavailable or returns placeholder content.

This ensures the pipeline always generates meaningful output regardless of
Ollama availability, model quality, or network state."""

from typing import Any, Dict, List


# ── Character reference lock-in for image generation ─────────────────────────────
CHARACTER_LOCK_IN = """
-- character references:
  MARK: tall man, late 30s, lean build, warm brown skin, short black hair with a silver streak at the left temple, sharp jawline, deep brown tired eyes, wearing a faded blue button-down shirt and dark jeans. Appears consistently across all scenes with identical physical description.
  SARAH: woman in her early 30s, medium height (5'6"), slim athletic build, light tan skin, long dark wavy hair worn half-up with minimalist gold necklace and earrings, almond-shaped hazel eyes, wearing a structured blazer over a white fitted top. Appears consistently across all scenes with identical physical description.
"""


def generate_story() -> Dict[str, Any]:
    """Return the deterministic story backbone."""
    return {
        "title": "The Space Between Us",
        "synopsis": "A man slowly withdraws from his marriage after repeated small rejections, culminating in a quiet decision to leave.",
        "emotional_tone": "sad",
        "setting": "Urban home — kitchen, bathroom, dining room, bedroom, balcony.",
        "characters": [
            {"name": "MARK", "age": 36, "role": "husband", "traits": ["quiet", "introspective", "emotionally exhausted"]},
            {"name": "SARAH", "age": 34, "role": "wife", "traits": ["distracted", "work-focused", "unaware of growing distance"]},
        ],
        "beats": [
            {"id": 1, "description": "Opening — kitchen morning. MARK tries to connect with SARAH who is focused on her phone.", "scene_class": "hook"},
            {"id": 2, "description": "Car ride in the garage. Silence between them, both aware of distance but neither addressing it.", "scene_class": "establishment"},
            {"id": 3, "description": "Dinner table — MARK speaks his need to stay connected. SARAH listens but doesn't fully respond.", "scene_class": "dialogue"},
            {"id": 4, "description": "Bedroom night. The emotional peak — both see the distance clearly but can't bridge it yet.", "scene_class": "emotional_peak"},
            {"id": 5, "description": "Balcony twilight. Resolution — they are physically close but emotionally apart, each wondering how to reach the other.", "scene_class": "resolution"},
        ],
    }


def generate_scenes() -> List[Dict[str, Any]]:
    """Return scene data with actual dialogue_lines between MARK and SARAH."""
    return [
        {
            "id": 1, "camera": "wide shot", "duration": "15 seconds",
            "emotion": "guarded", "lighting": "natural morning light",
            "scene_class": "hook",
            "dialogue_lines": [
                {"speaker": "MARK", "text": "I was wondering if you wanted to try that Italian place downtown tonight?"},
                {"speaker": "SARAH", "text": "Not tonight. Maybe tomorrow."},
            ],
            "visual_prompt": f"Cinematic wide shot of MARK sitting alone at a sunlit kitchen table, staring into a cold coffee cup. Morning light filters through half-closed blinds creating warm stripes across the counter. SARAH stands near the door with her bag, looking down at her phone. MARK — tall (6'1\"), lean build, late 30s, warm brown skin, short black hair with silver streak at left temple, sharp jawline, deep brown tired eyes, faded button-down shirt and dark jeans. SARAH — medium height (5'6'), slim athletic build, early 30s, light tan skin, long dark wavy hair half-up, almond hazel eyes, minimalist gold necklace, structured blazer over white tee. Professional cinematography, 8k resolution, natural morning warmth, shallow depth of field.{CHARACTER_LOCK_IN}",
        },
        {
            "id": 2, "camera": "close-up", "duration": "15 seconds",
            "emotion": "withdrawn", "lighting": "warm indoor light",
            "scene_class": "establishment",
            "dialogue_lines": [
                {"speaker": "MARK", "text": "You barely talked to me yesterday."},
                {"speaker": "SARAH", "text": "I was tired. Work's been crazy."},
                {"speaker": "MARK", "text": "It's always work."},
            ],
            "visual_prompt": f"Cinematic close-up of MARK gripping the steering wheel in a closed garage, knuckles white, eyes fixed straight ahead on the garage door. SARAH sits beside him in profile, scrolling through her phone with one earbud visible. Silence between them is heavy and deliberate. MARK — tall (6'1\"), lean build, late 30s, warm brown skin, short black hair with silver streak at left temple, sharp jawline, deep brown exhausted eyes, faded button-down shirt. SARAH — medium height (5'6'), slim athletic build, early 30s, light tan skin, long dark wavy hair half-up, almond hazel eyes, minimalist gold earrings, structured blazer. Professional cinematography, 8k resolution, warm amber garage lighting, tight framing emphasizing emotional distance.{CHARACTER_LOCK_IN}",
        },
        {
            "id": 3, "camera": "dolly-in", "duration": "18 seconds",
            "emotion": "frustrated", "lighting": "late afternoon golden hour",
            "scene_class": "dialogue",
            "dialogue_lines": [
                {"speaker": "MARK", "text": "I'm not saying you shouldn't work hard. I just... I miss us."},
                {"speaker": "SARAH", "text": "We're still here, aren't we?"},
                {"speaker": "MARK", "text": "Physically, yeah. But it feels like—"},
                {"speaker": "SARAH", "text": "What does it feel like?"},
            ],
            "visual_prompt": f"Cinematic dolly-in of the dining room at dinner time. MARK stands near the counter speaking carefully, posture tense but controlled. SARAH sits at the table with a laptop open, pausing to look up with guarded expression. Half-eaten plates between them. MARK — tall (6'1\"), lean build, late 30s, warm brown skin, short black hair with silver streak at left temple, sharp jawline, deep brown eyes searching for connection, faded button-down with sleeves rolled up. SARAH — medium height (5'6'), slim athletic build, early 30s, light tan skin, long dark wavy hair down now, almond hazel eyes wary but attentive, minimalist gold bracelets, fitted workwear. Professional cinematography, 8k resolution, golden hour warmth streaming through window, slow dolly movement.{CHARACTER_LOCK_IN}",
        },
        {
            "id": 4, "camera": "tracking shot", "duration": "18 seconds",
            "emotion": "emotional peak", "lighting": "dramatic backlight",
            "scene_class": "emotional_peak",
            "dialogue_lines": [
                {"speaker": "SARAH", "text": "Are you leaving?"},
                {"speaker": "MARK", "text": "No. I'm just... figuring out how to stay."},
                {"speaker": "SARAH", "text": "That sounds like the same thing."},
                {"speaker": "MARK", "text": "Maybe it is."},
            ],
            "visual_prompt": f"Cinematic tracking shot in the dimly lit bedroom at night. SARAH sits on the edge of the bed, phone face-down beside her for the first time in months. MARK stands near an open closet, pulling a shirt from the hanger, his back partially turned. A single bedside lamp casts amber light between them. SARAH — medium height (5'6'), slim athletic build, early 30s, light tan skin, long dark wavy hair loose now falling over shoulders, almond hazel eyes wide with realization, minimalist gold necklace catching low light, fitted workwear blouse. MARK — tall (6'1\"), lean build, late 30s, warm brown skin, short black hair with silver streak at left temple, sharp jawline set in quiet resolve, deep brown eyes distant but clear, faded button-down shirt. Professional cinematography, 8k resolution, dramatic backlight creating silhouette contrast, handheld tracking movement.{CHARACTER_LOCK_IN}",
        },
        {
            "id": 5, "camera": "wide shot", "duration": "15 seconds",
            "emotion": "resolved", "lighting": "cold blue twilight",
            "scene_class": "resolution",
            "dialogue_lines": [
                {"speaker": "SARAH (voiceover)", "text": "I think we forgot how to do this."},
                {"speaker": "MARK (voiceover)", "text": "Do what?"},
                {"speaker": "SARAH (voiceover)", "text": "Not keep score."},
                {"speaker": "MARK (voiceover)", "text": "We didn't. We just stopped trying."},
            ],
            "visual_prompt": f"Cinematic wide shot of MARK standing alone on a balcony at twilight, leaning against the railing, breathing in cool air. Through glass doors behind him, SARAH sits on the couch inside watching but not coming out. City lights begin to glow below in the distance. A silent space between two people who no longer know how to bridge it. MARK — tall (6'1\"), lean build, late 30s, warm brown skin illuminated by cool twilight, short black hair with silver streak at left temple visible in profile, sharp jawline softened by reflection of city lights, deep brown eyes gazing out, faded button-down shirt sleeves rolled to elbows. SARAH — medium height (5'6'), slim athletic build, early 30s, light tan skin softly lit from inside the apartment, long dark wavy hair cascading down her back, almond hazel eyes sad and uncertain, minimalist gold bracelet catching warm interior glow, fitted workwear top. Professional cinematography, 8k resolution, cold blue twilight exterior contrasting with warm amber interior, wide composition emphasizing emotional isolation.{CHARACTER_LOCK_IN}",
        },
    ]


def generate_prompts(scenes_data: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Return prompts keyed to scene_id, using full visual_prompt (with character refs)."""
    prompts = []
    for s in scenes_data:
        sid = s.get("id", 1)
        vp = s.get("visual_prompt", "")

        # The visual_prompt from scenes.yaml already contains the full MARK + SARAH descriptions.
        # Use it directly — no need to reconstruct a simplified prompt.
        prompts.append({
            "scene_id": sid,
            "prompt": vp,
            "negative_prompt": "blurry, low quality, deformed, extra fingers, cartoon",
            "visual_style": "cinematic",
        })
    return prompts


def is_valid_content(scenes: List[Dict], dialogues: List, prompts: List) -> bool:
    """Check if existing pipeline content is real (not placeholder/generic)."""
    if not scenes or not dialogues:
        return False

    # Check for placeholder text patterns
    scene_text = str(scenes)
    dialogue_text = str(dialogues)
    prompt_text = str(prompts)

    placeholder_patterns = [
        "Visual description for scene",
        "Description of the a lonely astronaut",
        "placeholder",
        "filler",
        "generic",
    ]

    for pat in placeholder_patterns:
        if pat.lower() in scene_text.lower() or pat.lower() in dialogue_text.lower():
            return False

    # Check that we have actual character names
    has_mark = any("MARK" in str(s).upper() for s in scenes)
    has_sarah = any("SARAH" in str(s).upper() for s in scenes)
    has_dialogue_lines = any("dialogue_lines" in str(s) for s in scenes)

    return has_mark and has_sarah and has_dialogue_lines
