"""Agent 4: Scene Structurer.

This is the agent that turns pure narrative (story.md) into a structured
Master Timeline (master_timeline.yaml) — the platform-agnostic source of
truth for production.

Why this is a separate agent:
- Story is pure narrative. No camera. No music. No timing.
- Master Timeline is structured data. Each scene has voiceover, dialogues,
  music cues, emotional state, shot language, duration, etc.
- Mixing them gives the LLM too much to do at once. Specializing improves
  quality.

Output: Master Timeline YAML with:
  - metadata (title, total scenes, total duration)
  - characters (extracted from context)
  - scenes (11 scenes with voiceover, dialogues, music, SFX, shot language)

The Master Timeline is a SUPERSET of the current pipeline's manifest format.
The adapter in master_timeline_to_manifest.py reads this and produces the
manifest the existing pipeline expects.

Input:  story.md + dna.yaml + context.md
Output: master_timeline.yaml
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml

from .llm_client import chat, LLMError
from .master_timeline import (
    AmbientCue,
    Character,
    DialogueLine,
    MasterTimeline,
    MusicCue,
    Scene,
    ShotLanguage,
    SilenceEngine,
)


SCENE_COUNT = 11  # Standard 3-act / 9-beat structure


SYSTEM_PROMPT = f"""You are a Scene Structurer for cinematic psychological storytelling. Your ONLY job is to convert a pure narrative story into a structured scene-by-scene production timeline.

Input you receive:
- A Story DNA (territory, mechanism, theme, ending)
- A Context document (characters, setting, visual language)
- A Story (the narrative prose, ~1200 words, with 3 acts and 7 sections)

Output: a YAML document representing a Master Timeline with EXACTLY {SCENE_COUNT} scenes.

For each scene, output this structure:

```yaml
scenes:
  - scene_number: 1
    title: <short_evocative_title>
    act: <act_1_observation | act_2_inner_reality | act_3_psychological_truth>
    phase: <hook | warmth | warmth | normalcy | crack | collapse | collapse | almost | retreat | duality | climax>
    beat: <opening_hook | contrast_memory | contrast_memory | outside_version | first_fracture | internal_collapse | irreversible_moment | almost_moment | defensive_retreat | her_truth | final_truth>
    duration_seconds: <number_8_to_30>
    emotional_state: <one_word_or_short_phrase>
    energy: <int_1_to_10>
    voiceover: "<1-3_sentences_max_30_words_IMPLY_don't_EXPLAIN>"
    dialogues: []   # or list of {{character, line, timing, emotion}}
    scene_description: "<ONE_concrete_visual_moment_with_micro_behaviors_and_environmental_messiness>"
    scene_description_alt: "<ONLY_for_irreversible_moment_scene:_a_2nd_visual_moment_with_a_hard_cut>"  # see v5.2
    visual_cause_of_emotion: "<the_micro_behavior_that_reveals_the_emotion>"
    shot_language: {{ shot_size: close-up|medium|wide, lighting_key: warm_low_light|natural_shadows|practical_lighting, lens_mm: <35|50|85>, depth_of_field: shallow|soft|deep }}
    characters_present: [<character_keys>]
    ken_burns_effect: <ken-burns|zoom-in|pan-left|pan-right|zoom-out>
    music_cue: {{ zone: act_1|act_2|act_3|none, volume: <0.0_to_0.5> }}
    ambient_cue: {{ beat: <beat_name>, description: "<one_sentence>" }}
    sfx_layers: []  # populate for irreversible_moment: [breathing, fabric, room_tone, ...]
    silence_engine: {{ silence_before: 0, silence_after: 0, silence_instead: false }}
    vocal_fracture: false
    irreversible_moment: false
    pre_moment: false
    post_moment: false
    shows_duality: false
```

The 3-act / 11-scene structure is FIXED:

  ACT 1 — Observation (4 scenes)
    Scene 1: hook, opening_hook (tense_restraint, energy 3)
    Scene 2-3: warmth, contrast_memory (warm_nostalgic, energy 7) — THE ONLY WARM SCENES
    Scene 4: normalcy, outside_version (flat_normal, energy 4)

  ACT 2 — Inner Reality (4 scenes)
    Scene 5: crack, first_fracture (quiet_unease, energy 3)
    Scene 6: collapse, internal_collapse (deepening_darkness, energy 2)
    Scene 7: collapse, irreversible_moment (silence, energy 1) — NO music, NO voice, ambient only. Set irreversible_moment: true, vocal_fracture: false, silence_instead: true
    Scene 8: almost, almost_moment (tension, energy 5) — THE ALMOST-TOUCHING CENTERPIECE

  ACT 3 — Psychological Truth (3 scenes)
    Scene 9: retreat, defensive_retreat (numb_protection, energy 2)
    Scene 10: duality, her_truth (quiet_grief, energy 3) — HER pain, not just his
    Scene 11: climax, final_truth (devastating_quiet, energy 1) — THE LAST LINE

Energy curve MUST descend: 3 → 7 → 7 → 4 → 3 → 2 → 1 → 5 → 2 → 3 → 1

CRITICAL RULES:
1. Each voiceover is 1-3 sentences, MAX 30 words. Less is more. The viewer should FEEL the meaning before consciously understanding it. Sound lived, not written.
2. scene_description is ONE concrete visual moment with micro-behaviors (hand starts to reach, then stops) and environmental messiness (unwashed mug, mail on counter). NOT "sad man alone" — that's explanation.
3. visual_cause_of_emotion is the micro-behavior that reveals the emotion. "Hand starts to reach, then withdraws; eyes flick to her, then back to phone." NOT "feeling sad."
4. The "almost moment" (Scene 8) is the emotional centerpiece. Almost touching. Almost speaking. Almost vulnerable. The interruption IS the story.
5. The "contrast memory" (Scenes 2-3) is what makes the audience mourn. Show warmth, laughter, tenderness. Golden hour.
6. Show duality — both partners hurt, not just one.
7. The final line (Scene 11 voiceover) must be UNFORGETTABLE. A quiet truth. Not advice.
8. Scene 7 (irreversible_moment): no voiceover, no music. Ambient only. duration_seconds: 8-12. This is the visual carrying the moment. v5.2 — also populate `scene_description_alt` with a 2nd visual moment that the video hard-cuts to at the midpoint. Same characters, same location, but a slightly different angle/composition that creates visual disturbance when the cut happens (e.g., close-up of the partner's face vs. close-up of the hand hovering). The cut is meant to feel like the moment the relationship shifted.

Output format: pure YAML. No commentary. No fences (or use ```yaml fences which we'll strip).

Characters: extract from the Context. Use short keys (husband, wife, partner, etc). Set characters_present per scene.

The output MUST be valid YAML that parses without error.
"""


def structure_scenes(
    dna: dict[str, Any],
    context: str,
    story: str,
    *,
    output_path: str | Path | None = None,
    temperature: float = 0.3,
    max_tokens: int = 5000,
    base_url: str = "http://localhost:1234",
    api_key: str = "sk-lm-TkM3NqaZ:CQdNsDjxGRm17O3Gg59W",
) -> MasterTimeline:
    """Convert a story narrative into a Master Timeline.

    Args:
        dna: Story DNA dict.
        context: Context markdown.
        story: Story markdown.
        output_path: If given, write the Master Timeline YAML to this path.
        temperature: LLM sampling temperature. Low for structural consistency.
        max_tokens: Maximum tokens in the response.
        base_url: LMStudio base URL. Override for non-default deployments.
        api_key: LMStudio API key.

    Returns:
        A MasterTimeline object.

    Raises:
        LLMError: If the LLM call fails or returns unparseable YAML.
    """
    # Extract character names from the context. The Context Generator formats
    # characters as `**Marcus Chen (34)**` (bold) or as `## Marcus Chen (34)`
    # (heading). We try both.
    char_patterns = [
        re.compile(r"\*\*([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)\s*\((\d+)\)\*\*"),
        re.compile(r"^##\s*([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)\s*\((\d+)\)", re.MULTILINE),
        re.compile(r"^#\s*([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)\s*\((\d+)\)", re.MULTILINE),
    ]
    raw_chars: list[tuple[str, str]] = []
    for pat in char_patterns:
        raw_chars.extend(pat.findall(context))
    # Dedupe by name
    seen = set()
    characters = []
    for i, (name, age) in enumerate(raw_chars):
        if name in seen:
            continue
        seen.add(name)
        # Use a normalized key (lowercase first word)
        key = name.split()[0].lower()
        # Default role: protagonist for the first character, partner for the second
        role = "protagonist" if i == 0 else "partner"
        characters.append(Character(
            key=key,
            name=name,
            role=role,
            anchors=[
                f"{name} ({age}), real person with lived-in appearance, imperfect and human",
            ],
            emotional_range=[
                "restraint: hand frozen mid-reach",
                "tired: heavy eyes, posture not straight",
                "awkward: one sleeve half-rolled, off-center",
                "distracted: looking away mid-thought",
                "delayed: emotional response 5 seconds too long",
            ],
        ))

    user_prompt = f"""Story DNA:
{yaml.dump(dna, default_flow_style=False, sort_keys=False).strip()}

Context:
{context}

Story:
{story}

Now produce the Master Timeline YAML with exactly {SCENE_COUNT} scenes. Output pure YAML:"""

    raw = chat(
        system=SYSTEM_PROMPT,
        user=user_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        base_url=base_url,
        api_key=api_key,
    )

    # Strip markdown fences
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("yaml"):
            text = text[4:]
        text = text.strip()
        if text.endswith("```"):
            text = text[:-3].strip()

    # Try to parse as YAML
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as e:
        raise LLMError(f"Scene Structurer returned invalid YAML:\n{text[:2000]}\n\nError: {e}") from e

    if not isinstance(data, dict):
        raise LLMError(f"Scene Structurer returned non-dict YAML: {type(data)}")

    # Handle both wrapped and unwrapped formats
    root = data.get("master_timeline", data)
    if "scenes" not in root:
        # Maybe the LLM put scenes at top level
        if "scenes" in data:
            root = data

    # Build the MasterTimeline
    timeline = MasterTimeline(
        version="1.0",
        dna=dna,
        source={
            "dna": "dna.yaml",
            "context": "context.md",
            "story": "story.md",
        },
        metadata={
            "title": dna.get("title") or root.get("title") or f"Story {dna.get('id', 'unknown')}",
            "id": dna.get("id", "UNKNOWN"),
            "territory": dna.get("territory", ""),
            "cluster": dna.get("cluster", ""),
            "mechanism": dna.get("mechanism", ""),
            "archetype": dna.get("archetype", ""),
            "ending": dna.get("ending", ""),
        },
        characters=characters,
    )

    # Parse scenes
    # Build a mapping from generic references (husband, wife, he, she, him, her)
    # to the actual character keys. The LLM often uses generic pronouns while
    # the characters block has real names — we reconcile them here.
    char_keys = [c.key for c in characters]
    generic_to_key: dict[str, str] = {}
    if len(char_keys) >= 1:
        generic_to_key.update({
            "husband": char_keys[0], "him": char_keys[0], "he": char_keys[0],
            "his": char_keys[0], "himself": char_keys[0],
            "protagonist": char_keys[0], "main": char_keys[0],
        })
    if len(char_keys) >= 2:
        generic_to_key.update({
            "wife": char_keys[1], "her": char_keys[1], "she": char_keys[1],
            "hers": char_keys[1], "herself": char_keys[1],
            "partner": char_keys[1], "woman": char_keys[1],
        })

    def _resolve_char(ref: str) -> str:
        """Map a generic character reference to the actual character key."""
        r = ref.strip().lower()
        if r in generic_to_key:
            return generic_to_key[r]
        # Already a real name?
        if r in [k.lower() for k in char_keys]:
            return ref.strip()
        return ref.strip()

    for s in root.get("scenes", []):
        shot = s.get("shot_language", {})
        music = s.get("music_cue", {})
        ambient = s.get("ambient_cue", {})
        silence = s.get("silence_engine", {})

        dialogues = []
        for d in s.get("dialogues", []):
            if isinstance(d, dict) and d.get("line"):
                dialogues.append(DialogueLine(
                    character=_resolve_char(d.get("character", "")),
                    line=d.get("line", ""),
                    timing=d.get("timing", ""),
                    emotion=d.get("emotion", ""),
                ))

        # Resolve characters_present to actual keys
        chars_present_raw = s.get("characters_present", [])
        chars_present = [_resolve_char(c) for c in chars_present_raw]

        timeline.scenes.append(Scene(
            scene_number=s["scene_number"],
            title=s.get("title", f"Scene {s['scene_number']}"),
            act=s.get("act", "act_1_observation"),
            phase=s.get("phase", ""),
            beat=s.get("beat", ""),
            duration_seconds=float(s.get("duration_seconds", 12.0)),
            duration_hint=s.get("duration_hint", "20-30s"),
            emotional_state=s.get("emotional_state", "neutral"),
            energy=int(s.get("energy", 5)),
            voiceover=s.get("voiceover", ""),
            dialogues=dialogues,
            scene_description=s.get("scene_description", ""),
            scene_description_alt=s.get("scene_description_alt", ""),
            visual_cause_of_emotion=s.get("visual_cause_of_emotion", ""),
            shot_language=ShotLanguage(
                shot_size=shot.get("shot_size", "medium"),
                lighting_key=shot.get("lighting_key", "natural_shadows"),
                lens_mm=int(shot.get("lens_mm", 50)),
                depth_of_field=shot.get("depth_of_field", "shallow"),
            ),
            characters_present=chars_present,
            ken_burns_effect=s.get("ken_burns_effect", "ken-burns"),
            music_cue=MusicCue(
                zone=music.get("zone", "act_1"),
                volume=float(music.get("volume", 0.3)),
            ),
            ambient_cue=AmbientCue(
                beat=ambient.get("beat", ""),
                description=ambient.get("description", ""),
            ),
            sfx_layers=s.get("sfx_layers", []),
            silence_engine=SilenceEngine(
                silence_before=float(silence.get("silence_before", 0.0)),
                silence_after=float(silence.get("silence_after", 0.0)),
                silence_instead=bool(silence.get("silence_instead", False)),
            ),
            vocal_fracture=bool(s.get("vocal_fracture", False)),
            irreversible_moment=bool(s.get("irreversible_moment", False)),
            pre_moment=bool(s.get("pre_moment", False)),
            post_moment=bool(s.get("post_moment", False)),
            shows_duality=bool(s.get("shows_duality", False)),
        ))

    if len(timeline.scenes) != SCENE_COUNT:
        raise LLMError(
            f"Scene Structurer produced {len(timeline.scenes)} scenes, expected {SCENE_COUNT}. "
            f"Got: {[s.title for s in timeline.scenes]}"
        )

    if output_path is not None:
        timeline.save(output_path)

    return timeline
