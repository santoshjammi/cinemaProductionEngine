"""Cinematic prompt builder — converts VID01 scenes into SD-optimized image prompts.

Adapts OpenMontage's techniques for Stable Diffusion v1.5:
- 5-aspect skeleton (Subject / Motion / Scene / Spatial / Camera) condensed to SD limits
- Identity anchoring: repeat 3-6 disambiguating visual attributes verbatim per scene
- 3-part contextual prompt: scene-specific shot language + consistency anchor + concrete subject
- Replace emotional adjectives with visual causes
- One frame per prompt (no multi-action montages)
- Negative prompts tuned for cinematic photorealism
"""

from __future__ import annotations
from typing import Any

# Character identity anchors — repeated VERBATIM in every scene for consistency
CHARACTERS = {
    "husband": {
        "name": "James",
        "anchors": [
            "man mid-30s, short dark brown hair, stubble, grey t-shirt",
        ],
    },
    "wife": {
        "name": "Sarah",
        "anchors": [
            "woman early 30s, auburn hair, white sleep shirt",
        ],
    },
}

# Visual system anchors — keep scenes coherent without making them identical
VISUAL_SYSTEM = {
    "style": "cinematic photorealism, 35mm film grain, muted desaturated tones",
    "color_bias": "cool blue undertones with warm amber practical lights",
    "texture": "shallow depth of field, natural film grain, soft contrast",
    "negative": (
        "cartoon, anime, illustration, painting, 3d render, cgi, video game, "
        "blurry, low quality, distorted, deformed, disfigured, bad anatomy, "
        "extra limbs, watermark, signature, text, oversaturated, hdr, plastic skin"
    ),
}


def _anchor(character_key: str) -> str:
    """Return the verbatim identity anchor string for a character."""
    c = CHARACTERS.get(character_key)
    if not c:
        return ""
    return ", ".join(c["anchors"])


def _replace_emotion_with_visual(emotion: str) -> str:
    """Replace emotional adjectives with their visual causes."""
    mapping = {
        "melancholic": "shoulders slumped, eyes cast downward, dim lighting",
        "tension": "jaw clenched, hands gripping tightly, rigid posture",
        "restraint": "hand frozen mid-reach, fingers slightly curled, held breath stillness",
        "invisible distance": "two people facing same direction but not touching, gap between bodies",
        "accumulated shame": "head bowed, avoiding eye contact, hunched shoulders",
        "vulnerability": "raw unposed posture, eyes wet but not crying, lips slightly parted",
        "numbness": "blank thousand-yard stare, slack facial muscles, limp hands",
        "resigned": "shoulders dropped, slow heavy movements, eyes half-closed",
        "grief": "motionless, eyes open but unfocused, hand hovering without touching",
        "tragic stillness": "frozen pose, no motion blur, complete stillness",
    }
    for word, visual in mapping.items():
        if word in emotion.lower():
            return visual
    return ""


def build_cinematic_prompt(
    scene: dict[str, Any],
    shot_language: dict[str, Any] | None = None,
    characters_in_scene: list[str] | None = None,
) -> tuple[str, str]:
    """Build a SD-optimized prompt for a single scene frame.

    Returns (positive_prompt, negative_prompt).

    Args:
        scene: Scene dict with description, emotional_beat, etc.
        shot_language: Structured cinematography (shot_size, lighting_key, lens_mm, etc.)
        characters_in_scene: List of character keys present (e.g. ["husband", "wife"])
    """
    sl = shot_language or {}
    parts: list[str] = []

    # Part 1: Shot language (camera + lighting)
    shot_parts = []
    shot_size = sl.get("shot_size", "medium")
    shot_map = {
        "extreme_wide": "extreme wide establishing shot",
        "wide": "wide shot",
        "medium_wide": "medium-wide shot",
        "medium": "medium shot waist up",
        "medium_close": "medium close-up chest up",
        "close_up": "close-up on face",
        "extreme_close_up": "extreme close-up detail shot",
        "over_shoulder": "over-the-shoulder framing",
        "insert": "insert detail shot",
    }
    shot_parts.append(shot_map.get(shot_size, shot_size))

    lighting_key = sl.get("lighting_key", "low_key")
    light_map = {
        "high_key": "bright even high-key lighting",
        "low_key": "dramatic low-key lighting with deep shadows",
        "natural": "soft natural ambient light",
        "golden_hour": "warm golden hour sunlight",
        "blue_hour": "cool blue hour twilight",
        "tungsten_warm": "warm tungsten interior lamp glow",
        "neon": "neon-lit with color spill",
        "silhouette": "backlit silhouette",
        "rim_lit": "rim lighting on subject edges",
        "volumetric": "volumetric light rays through atmosphere",
        "overcast_soft": "soft overcast diffused light",
        "practical_phone": "phone screen glow as practical light source",
        "moonlight": "cool moonlight through curtains",
    }
    shot_parts.append(light_map.get(lighting_key, light_map.get(lighting_key, lighting_key)))

    if sl.get("lens_mm"):
        shot_parts.append(f"{sl['lens_mm']}mm lens")
    if sl.get("depth_of_field"):
        dof_map = {
            "shallow": "shallow depth of field with bokeh",
            "medium": "medium depth of field",
            "deep": "deep focus everything sharp",
        }
        shot_parts.append(dof_map.get(sl["depth_of_field"], sl["depth_of_field"]))

    parts.append(", ".join(shot_parts))

    # Part 2: Character identity anchors (verbatim for consistency)
    # Keep SHORT — just the key disambiguating features
    if characters_in_scene:
        for char_key in characters_in_scene:
            anchor = _anchor(char_key)
            if anchor:
                parts.append(anchor)

    # Part 3: Concrete scene subject — replace emotional words with visual causes
    description = scene.get("description", "")
    parts.append(description)

    positive = ", ".join(filter(None, parts))

    # SD v1.5 CLIP limit is 77 tokens (~300 chars).
    # Priority order: shot language > character anchors > scene description
    # If too long, truncate scene description from the end
    if len(positive) > 300:
        # Find description in parts and truncate
        for i, p in enumerate(parts):
            if description and description in p:
                # Calculate how much we need to cut
                other_parts = ", ".join(parts[:i] + parts[i+1:])
                max_desc_len = 300 - len(other_parts) - 2  # 2 for ", "
                if max_desc_len > 50:
                    parts[i] = description[:max_desc_len].rsplit(", ", 1)[0]
                else:
                    parts[i] = description[:max_desc_len]
                break
        positive = ", ".join(filter(None, parts))

    return positive, VISUAL_SYSTEM["negative"]


# === VID01 Scene Definitions ===

VID01_SCENES = [
    {
        "scene_number": 1,
        "title": "Opening Hook",
        "description": "Dark bedroom at night, phone screen glow as only light source, illuminating half of his face, wife asleep beside him under white sheets, his hand reaching toward her shoulder but frozen mid-gesture, fingers slightly curled, gap between his hand and her shoulder",
        "emotional_beat": "restraint",
        "duration": "14s",
        "shot_language": {
            "shot_size": "close_up",
            "lighting_key": "practical_phone",
            "lens_mm": 50,
            "depth_of_field": "shallow",
        },
        "characters": ["husband", "wife"],
    },
    {
        "scene_number": 2,
        "title": "The Outside Version",
        "description": "Man and woman sitting at a kitchen table eating dinner in silence, plates of food between them, both looking down at their plates, not making eye contact, gap between their hands on the table, plain suburban kitchen with overhead fluorescent light",
        "emotional_beat": "invisible distance",
        "duration": "28s",
        "shot_language": {
            "shot_size": "medium",
            "lighting_key": "tungsten_warm",
            "lens_mm": 35,
            "depth_of_field": "medium",
        },
        "characters": ["husband", "wife"],
    },
    {
        "scene_number": 3,
        "title": "The Internal Collapse",
        "description": "Man sitting alone in his parked car at night, streetlights outside, staring straight ahead at the dark windshield, hands gripping the steering wheel, head bowed slightly forward, empty passenger seat, rain droplets on side window",
        "emotional_beat": "accumulated shame",
        "duration": "35s",
        "shot_language": {
            "shot_size": "medium_close",
            "lighting_key": "low_key",
            "lens_mm": 85,
            "depth_of_field": "shallow",
        },
        "characters": ["husband"],
    },
    {
        "scene_number": 4,
        "title": "The Defensive Retreat",
        "description": "Man sitting alone on a living room couch in darkness, blue TV glow illuminating his face, game controller in his hands, slack jaw, blank thousand-yard stare at the screen, empty couch beside him, dim room with only screen light",
        "emotional_beat": "numbness",
        "duration": "20s",
        "shot_language": {
            "shot_size": "medium",
            "lighting_key": "practical_phone",
            "lens_mm": 35,
            "depth_of_field": "shallow",
        },
        "characters": ["husband"],
    },
    {
        "scene_number": 5,
        "title": "The Final Truth",
        "description": "Dark bedroom at night, both lying in bed facing the ceiling, moonlight through curtains, his hand resting on the white sheet near her hand but not touching, two inches of space between their fingers, frozen stillness, cool blue moonlight on white sheets",
        "emotional_beat": "tragic stillness",
        "duration": "21s",
        "shot_language": {
            "shot_size": "close_up",
            "lighting_key": "moonlight",
            "lens_mm": 50,
            "depth_of_field": "shallow",
        },
        "characters": ["husband", "wife"],
    },
]


def get_vid01_prompts() -> list[dict]:
    """Return full prompt dicts for all VID01 scenes."""
    results = []
    for scene in VID01_SCENES:
        positive, negative = build_cinematic_prompt(
            scene=scene,
            shot_language=scene.get("shot_language", {}),
            characters_in_scene=scene.get("characters", []),
        )
        results.append({
            "scene_number": scene["scene_number"],
            "title": scene["title"],
            "positive_prompt": positive,
            "negative_prompt": negative,
            "shot_language": scene.get("shot_language", {}),
            "characters": scene.get("characters", []),
            "emotional_beat": scene.get("emotional_beat", ""),
        })
    return results


if __name__ == "__main__":
    for p in get_vid01_prompts():
        print(f"\n{'='*70}")
        print(f"Scene {p['scene_number']}: {p['title']}")
        print(f"Characters: {p['characters']}")
        print(f"Emotional beat: {p['emotional_beat']}")
        print(f"Shot: {p['shot_language']}")
        print(f"\nPROMPT:\n{p['positive_prompt']}")
        print(f"\nNEGATIVE:\n{p['negative_prompt']}")