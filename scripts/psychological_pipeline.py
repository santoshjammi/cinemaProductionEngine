"""Psychological Cinema Pipeline — full video generation engine.

Reads the playbook + topic context + video manifest, then runs:
  1. Narrative generation (Qwen3-Coder via LMStudio)
  2. Emotional refinement (second LLM pass)
  3. Scene visualization (SDXL + CLIP verification)
  4. Narration (edge-tts)
  5. Background music (ambient generation)
  6. Ambient SFX (room tone, rain)
  7. Audio mixing (narration + music + ambient)
  8. Video assembly (Ken Burns + FFmpeg)

Usage:
    python psychological_pipeline.py \
        --playbook ../psychological_cinema_playbook.yaml \
        --manifest VID01_revised.yaml \
        [--topic-dir .] \
        [--output-dir output/videos] \
        [--skip-narrative]  # skip step 1-2 if manifest already has scenes
"""
import argparse
import json
import logging
import os
import subprocess
import sys
import urllib.request
import urllib.error
from pathlib import Path

# v1.1.4 — ensure project root is on sys.path so openmontage_adapter can be
# imported when this script is run from anywhere (e.g. from scripts/ dir).
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
from typing import Any

import numpy as np
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
os.environ.setdefault("COQUI_TOS_AGREED", "1")

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("pipeline")


# ============================================================
# Step 1: Narrative Generation (Qwen3-Coder via LMStudio)
# ============================================================

class NarrativeGenerator:
    """Generates scene structure and narration using a configurable LLM model."""

    def __init__(
        self,
        playbook: dict,
        topic_dir: Path,
        manifest: dict,
        api_key: str,
        base_url: str,
        model: str = "qwen3-coder-30b-a3b-instruct-mlx",
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ):
        self.playbook = playbook
        self.topic_dir = topic_dir
        self.manifest = manifest
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Load context files referenced in the manifest
        self.context_md = ""
        self.feedback_md = ""
        self.style_guide = {}
        self.prompt_library = {}

        for ctx_file in manifest.get("context_files", []):
            path = topic_dir / ctx_file
            if not path.exists():
                continue
            if ctx_file == "CONTEXT.md":
                self.context_md = path.read_text()
            elif ctx_file == "FEEDBACK_DIGEST.md":
                self.feedback_md = path.read_text()
            elif ctx_file == "STYLE_GUIDE.yaml":
                self.style_guide = yaml.safe_load(path.read_text())
            elif ctx_file == "PROMPT_LIBRARY.yaml":
                self.prompt_library = yaml.safe_load(path.read_text())

    def _call_llm(self, system_prompt: str, user_prompt: str, max_tokens: int | None = None) -> str:
        """Call LMStudio API."""
        if max_tokens is None:
            max_tokens = self.max_tokens
        payload = json.dumps({
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": self.temperature,
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{self.base_url}/v1/chat/completions",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=600) as resp:
            result = json.loads(resp.read())
            return result["choices"][0]["message"]["content"]

    def generate_scenes(self, story_md: str) -> list[dict]:
        """Generate structured scenes from a story markdown file."""
        # Handle both old (psychological_cinema_playbook) and new (psychological_cinema_standard) keys
        if "psychological_cinema_playbook" in self.playbook:
            pe = self.playbook["psychological_cinema_playbook"]
        elif "psychological_cinema_standard" in self.playbook:
            pe = self.playbook["psychological_cinema_standard"]
        else:
            pe = self.playbook  # use the whole thing

        chars = self.manifest.get("characters", {})

        # Build character descriptions for the prompt
        char_desc = ""
        for key, char in chars.items():
            char_desc += f"  {key} ({char.get('name', key)}):\n"
            char_desc += f"    anchors: {', '.join(char.get('anchors', []))}\n"
            char_desc += f"    role: {char.get('role', '')}\n"

        system_prompt = f"""You are a psychological cinema narrative architect for "{pe['brand']['name']}".

GENRE: {pe['brand']['genre']}
EMOTIONAL IDENTITY: {pe['brand']['core_feelings']}

You must follow this NARRATIVE ARC EXACTLY. Generate exactly the number
of scenes specified for each phase, in this order, with these moods.

NARRATIVE ARC:
{json.dumps(self.manifest.get('narrative_arc', {}), indent=2)}

ACT 1 (Observation): Viewer thinks "I know this feeling."
  - Phase 1 (hook, 1 scene): Tense restraint. A frozen moment of withdrawal.
  - Phase 2 (warmth, 2 scenes): WARM and NOSTALGIC. Laughter, tenderness. The ONLY warm scenes. Golden hour light.
  - Phase 3 (normalcy, 1 scene): Flat. Polite. Functional. Invisible from outside.

ACT 2 (Inner Reality): Viewer thinks "I didn't realize this was underneath it."
  - Phase 4 (crack, 1 scene): First visible fracture. Small but seismic.
  - Phase 5 (collapse, 2 scenes): DEEPENING DARKNESS. Reveal the truth: not desire that disappears — safety.
  - Phase 6 (almost, 1 scene): THE CENTERPIECE. Almost touching. The interruption IS the story.

ACT 3 (Psychological Truth): Viewer thinks "That truth hurts."
  - Phase 7 (retreat, 1 scene): Numb self-protection. Both retreat.
  - Phase 8 (duality, 1 scene): HER grief. Not just his. Both hurting.
  - Phase 9 (climax, 1 scene): THE DEVASTATING FINAL LINE. Not advice. A quiet truth that drops like a stone.

TOTAL: 11 scenes. Target 4-7 minutes.

ENERGY SCALE (1=quiet, 10=intense):
  Hook=3, Warmth=7, Normalcy=4, Crack=3, Collapse=2, Almost=5, Retreat=2, Duality=3, Climax=1
  The arc MUST descend from warmth (7) down to climax (1). Emotional modulation, not flatline.

NARRATION RULES:
{json.dumps(pe['narration_engine']['narration_rules'], indent=2)}

NARRATION STYLE — avoid:
{json.dumps(pe['narration_engine']['avoid'], indent=2)}

PREFERRED SENTENCE STYLE:
{json.dumps(pe['narration_engine']['preferred_sentence_style'], indent=2)}

TENSION MODEL — preferred: {pe['narration_engine']['tension_model']['preferred']}
TENSION MODEL — avoid: {pe['narration_engine']['tension_model']['avoid']}

VISUAL MOTIFS: {pe['visual_engine']['themes']}
RECURRING MOTIFS: {pe['visual_engine']['recurring_motifs']}
LIGHTING: {pe['visual_engine']['lighting_style']['preferred']}
CAMERA: {pe['visual_engine']['camera_style']['movement']}, {pe['visual_engine']['camera_style']['framing']}

CRITICAL — VISUAL IMPLICATION RULES (from expert feedback):
{json.dumps(pe['visual_engine'].get('implication_rules', []), indent=2)}

CRITICAL — ENVIRONMENTAL DETAIL (make scenes feel lived-in):
{json.dumps(pe['visual_engine'].get('environmental_details', []), indent=2)}

CRITICAL — CAMERA PSYCHOLOGY:
{pe['visual_engine'].get('camera_style', {}).get('psychology', 'Camera is an observer, not a narrator.')}

EMOTIONAL RULESET — mandatory:
{json.dumps(pe['brand'].get('forbidden', []), indent=2)}

EMOTIONAL RULESET — forbidden:
{json.dumps(pe['brand'].get('forbidden', []), indent=2)}

SOUND DESIGN:
  Narration voice: {pe['sound_design_engine']['narration_audio']['voice_style']}
  Music zones: Act1={pe['sound_design_engine']['music_zones']['act_1']['name']}, Act2={pe['sound_design_engine']['music_zones']['act_2']['name']}, Act3={pe['sound_design_engine']['music_zones']['act_3']['name']}
  Silence rules: {pe['sound_design_engine']['silence_rules']}

CHARACTERS (use these exact keys in characters_present):
{char_desc}

FEEDBACK RULES (NON-NEGOTIABLE):
{self.feedback_md[:2000]}

CRITICAL RULES FOR THE CLIMAX SCENE (Phase 9, final scene):
- Must be a RECOGNITION, not a prescription
- No advice. No "you should". No "this is why".
- A quiet truth that lands: "Not all distance is anger. Sometimes distance is grief."
- Or: "They still love each other. But love without safety becomes performance."
- Or: "They still live in the same house. They just don't live in the same life."
- The last sentence must be UNFORGETTABLE.
- The viewer should feel it in their chest.

OUTPUT FORMAT: Return a YAML list of 11 scenes. Each scene MUST have:
  - scene_number: int (1-11)
  - title: string (short, evocative)
  - phase: the phase name from the arc (hook, warmth, normalcy, crack, collapse, almost, retreat, duality, climax)
  - beat: the beat name from the arc
  - act: one of [act_1_observation, act_2_inner_reality, act_3_psychological_truth]
  - mood: the mood from the arc
  - energy: the energy level from the arc (1-10)
  - voiceover: 1-3 sentences ONLY. Maximum 30 words. LESS IS MORE. The narration should IMPLY, not explain. Let the visual carry the emotion. The viewer should FEEL the meaning before consciously understanding it. Sound lived, not written.
  - scene_description: ONE concrete visual moment. CRITICAL RULES:
    1. Show IMPLICATION not EXPLANATION — "empty chair, coffee gone cold" not "sad man alone"
    2. Include MICRO-BEHAVIORS — awkward glance timing, interrupted gesture, nervous hand movement, distracted eye contact, unfinished movement, checking phone instead of speaking. NOT emotional posing.
    3. Include ENVIRONMENTAL MESSINESS — unwashed mug, shoes kicked off, mail on counter, wrinkles, dust, clutter. Spaces must feel INHABITED, not staged.
    4. Example: "He almost says something, changes his mind, checks his phone instead. She notices, pretends not to. An unwashed mug sits between them on the cluttered counter."
  - visual_cause_of_emotion: micro-behavior that reveals the emotion — "hand starts to reach, then withdraws; eyes flick to her, then back to phone" — NOT "feeling sad"
  - shot_language: {{shot_size, lighting_key, lens_mm, depth_of_field}}
  - characters_present: list of character keys
  - ken_burns_effect: from the arc
  - duration_hint: from the arc target duration

Return ONLY the YAML. No commentary. No markdown fences."""

        user_prompt = f"""Write the scene structure for this story:

{story_md[:3000]}

UNIVERSE CONTEXT:
{self.context_md[:1500]}

Remember:
- Include a contrast/warmth scene early (something to lose — warmth, memory, laughter)
- Include an "almost moment" (almost touching, almost speaking) as the emotional centerpiece
- Show duality — both partners hurt, not just one gender suffering
- Narration must sound internally discovered, not like psychology analysis
- Each scene is ONE frame for image generation — describe a single visual moment
- Use the exact character keys defined above in characters_present
- Silence is part of the soundtrack — some voiceovers should be short, leaving space

Return the YAML scene list:"""

        logger.info("Generating narrative with Qwen3-Coder-30B...")
        response = self._call_llm(system_prompt, user_prompt, max_tokens=4000)

        # Parse YAML from response
        try:
            # Strip markdown code fences if present
            if "```yaml" in response:
                response = response.split("```yaml")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]

            # Try direct parse first
            try:
                scenes = yaml.safe_load(response)
                if isinstance(scenes, dict):
                    # LLM returned numbered dict instead of list — convert
                    scenes = [scenes[k] for k in sorted(scenes.keys(), key=lambda x: int(x) if str(x).isdigit() else 0)]
                if not isinstance(scenes, list):
                    raise ValueError("Expected a list")
            except (yaml.YAMLError, ValueError):
                # Fallback: fix common LLM YAML issues
                # Convert "1. " or "1:" numbered items to "- " YAML list format
                import re as _re
                fixed_lines = []
                for line in response.split("\n"):
                    # Convert "1. " or "1:" at start of line to "- "
                    line = _re.sub(r'^(\d+)\.\s', '- ', line)
                    line = _re.sub(r'^(\d+):\s*$', '- ', line)
                    # Quote unquoted string values that contain special chars
                    if ":" in line and not line.strip().startswith("#") and not line.strip().startswith("- "):
                        key, _, val = line.partition(":")
                        val = val.strip()
                        if val and not val.startswith('"') and not val.startswith("'") and not val.startswith("[") and not val.startswith("{"):
                            if len(val) > 50 or "…" in val or "'" in val or '"' in val or ":" in val:
                                val_escaped = val.replace('"', '\\"')
                                line = f'{key}: "{val_escaped}"'
                    fixed_lines.append(line)
                response_fixed = "\n".join(fixed_lines)
                scenes = yaml.safe_load(response_fixed)
                if not isinstance(scenes, list):
                    raise ValueError("Expected a list of scenes")

            # Clean LLM artifacts from voiceovers
            import re
            for scene in scenes:
                vo = scene.get("voiceover", "")
                vo = re.sub(r'<[^>]+>', '', vo).strip()
                scene["voiceover"] = vo

            logger.info(f"Generated {len(scenes)} scenes")
            return scenes
        except Exception as e:
            logger.error(f"Failed to parse YAML: {e}")
            logger.error(f"Raw response:\n{response[:1000]}")

            # Last resort: save raw response and ask user to fix
            raw_path = self.topic_dir / f"{self.manifest.get('story_file', 'scenes')}_raw_response.txt"
            raw_path.write_text(response)
            logger.error(f"Raw response saved to: {raw_path}")
            raise


# ============================================================
# Step 2: Emotional Refinement (second LLM pass)
# ============================================================

class EmotionalRefiner:
    """Refines narration for emotional depth using a second LLM pass."""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str = "supergemma4-26b-uncensored-mlx-v2",
        temperature: float = 0.6,
        max_tokens: int = 2000,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def _call_llm(self, system_prompt: str, user_prompt: str, max_tokens: int | None = None) -> str:
        if max_tokens is None:
            max_tokens = self.max_tokens
        payload = json.dumps({
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": self.temperature,
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{self.base_url}/v1/chat/completions",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=600) as resp:
            result = json.loads(resp.read())
            return result["choices"][0]["message"]["content"]

    def refine_narration(self, scenes: list[dict], playbook: dict) -> list[dict]:
        """Refine each scene's voiceover for emotional depth."""
        # Handle both old and new key names
        if "psychological_cinema_playbook" in playbook:
            pe = playbook["psychological_cinema_playbook"]
        elif "psychological_cinema_standard" in playbook:
            pe = playbook["psychological_cinema_standard"]
        else:
            pe = playbook

        system_prompt = f"""You are an emotional refinement editor for "{pe['brand']['name']}".
Your job: rewrite narration so it sounds LIVED, not WRITTEN. And make it SHORTER.

CRITICAL RULES (from expert feedback 01 + 02):
- The narration currently sounds "authored" — it must sound "internally discovered."
- Sound like someone thinking inside the experience, not observing it from outside.
- Replace analytical observations with embodied ones: "he stopped knowing" not "he experienced."
- Add ambiguity. Add ache. Add humanity. Remove certainty.
- Use implication over exposition. Pain should feel observed, not dramatized.
- Sentences should feel human, not optimized. Use pauses intentionally (...).
- AVOID: therapy language, motivational energy, podcast energy, educational exposition, clinical descriptions.

EXPERT FEEDBACK 02 — THE MOST IMPORTANT NEW RULE:
- The video explains TOO MUCH. The audience should FEEL the meaning before consciously understanding it.
- LESS NARRATION. More silence. Let the VISUAL carry the emotion.
- Maximum 1-3 sentences per scene. Maximum 25 words. SHORTER IS BETTER.
- If the visual shows hesitation before touching, the narration should NOT say "he hesitated."
  Instead narrate something adjacent: "After a while, even small moments started feeling risky."
- The narration should NOT describe what's on screen. It should add a layer the visual can't.

PREFERRED STYLE (write like this):
- "After a while, he stopped reaching for her first." (10 words)
- "The silence didn't arrive suddenly." (5 words)
- "They still spoke every day. Just not honestly." (8 words)
- "Even small moments started feeling risky." (6 words)

FORBIDDEN PATTERNS (never write like this):
- "Maybe he started feeling unwanted." (too analytical)
- "This is what happens when..." (too explanatory)
- "He was experiencing..." (too clinical)
- "Let's talk about..." (too podcast)
- "In this video..." (too YouTube)
- Any sentence that describes what the viewer can already see on screen

CRITICAL — The final scene MUST be a devastating conclusion:
- Not advice. Not a lesson. Not a summary.
- A quiet, painful truth that lands like a stone dropping.
- Something the viewer recognizes in their own life.
- Maximum 2 sentences. Example: "Not all distance is anger. Sometimes distance is grief."

Rewrite each scene's voiceover. Make it SHORTER. Make it IMPLY, not explain.
Make it sound like internal truth discovery — lived, painful, human.

Return ONLY the rewritten voiceover text for each scene, numbered.
Format:
1: [rewritten text]
2: [rewritten text]
..."""

        user_prompt = "Rewrite these narration lines:\n\n"
        for s in scenes:
            user_prompt += f"{s['scene_number']}: {s.get('voiceover', '').strip()}\n\n"

        logger.info("Refining narration with second LLM pass...")
        response = self._call_llm(system_prompt, user_prompt, max_tokens=2000)

        # Parse numbered lines
        lines = {}
        for line in response.strip().split("\n"):
            line = line.strip()
            if ":" in line and line[0].isdigit():
                num_str, text = line.split(":", 1)
                try:
                    num = int(num_str.strip())
                    # Clean LLM artifacts
                    text = text.strip()
                    text = text.replace("<turn|>", "").replace("<|turn|>", "")
                    text = text.replace("<|end|>", "").replace("<|start|>", "")
                    # Remove any remaining angle-bracket tags
                    import re
                    text = re.sub(r'<[^>]+>', '', text).strip()
                    if text:
                        lines[num] = text
                except ValueError:
                    continue

        # Apply refined narration
        refined_count = 0
        for scene in scenes:
            num = scene["scene_number"]
            if num in lines and lines[num]:
                scene["voiceover"] = lines[num]
                refined_count += 1

        logger.info(f"Refined {refined_count}/{len(scenes)} scenes")
        return scenes


# ============================================================
# Step 2b: Write story transcript to video output directory
# ============================================================

def write_transcript(scenes: list[dict], output_dir: Path, video_title: str = ""):
    """Write the complete story and voiceover transcript to the video directory.

    Creates two files in the video output directory:
      - story.md    — full narrative with scene descriptions and voiceovers
      - transcript.txt — voiceover text only, scene by scene
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Full story document
    story_lines = [
        f"# {video_title or 'Psychological Cinema — Story Transcript'}",
        f"",
        f"Scenes: {len(scenes)}",
        f"",
    ]

    transcript_lines = [
        f"{video_title or 'Transcript'}",
        f"",
    ]

    for s in scenes:
        num = s.get("scene_number", 0)
        title = s.get("title", f"Scene {num}")
        beat = s.get("beat", "")
        vo = s.get("voiceover", "").strip()
        desc = s.get("scene_description", "").strip()
        visual = s.get("visual_cause_of_emotion", "").strip()
        effect = s.get("ken_burns_effect", "")
        chars = s.get("characters_present", [])

        # Story document
        story_lines.append(f"## Scene {num}: {title}")
        story_lines.append(f"**Beat:** {beat}")
        story_lines.append(f"**Characters:** {', '.join(chars) if chars else 'none'}")
        story_lines.append(f"**Ken Burns:** {effect}")
        story_lines.append(f"")
        story_lines.append(f"**Visual:** {desc}")
        if visual:
            story_lines.append(f"**Emotional cue:** {visual}")
        story_lines.append(f"")
        story_lines.append(f"**Voiceover:**")
        story_lines.append(f"> {vo}")
        story_lines.append(f"")
        story_lines.append(f"---")
        story_lines.append(f"")

        # Transcript (voiceover only)
        transcript_lines.append(f"[Scene {num}: {title}]")
        transcript_lines.append(vo)
        transcript_lines.append(f"")

    story_path = output_dir / "story.md"
    story_path.write_text("\n".join(story_lines))

    transcript_path = output_dir / "transcript.txt"
    transcript_path.write_text("\n".join(transcript_lines))

    logger.info(f"Story written: {story_path}")
    logger.info(f"Transcript written: {transcript_path}")
    return story_path, transcript_path


# ============================================================
# Step 3: Background Music Generation
# ============================================================

class MusicGenerator:
    """Generate 3 distinct music zones for the narrative arc.

    Act 1 (Observation): Ambient piano — sparse A-minor notes, warm but melancholic.
    Act 2 (Inner Reality): Dark drone — low rumble + occasional dissonant notes.
    Act 3 (Psychological Truth): Near-silence — single sustained note fading to nothing.
    """

    PIANO_NOTES = {
        "A2": 110.00, "C3": 130.81, "D3": 146.83, "E3": 164.81,
        "F3": 174.61, "G3": 196.00, "A3": 220.00, "C4": 261.63,
        "D4": 293.66, "E4": 329.63, "F4": 349.23, "G4": 392.00,
        "A4": 440.00, "C5": 523.25, "E5": 659.25,
        # D minor for Act 2 (darker)
        "D2": 73.42, "D3b": 69.30, "A1": 55.00, "Bb2": 116.54,
        "D3": 146.83, "F3": 174.61, "G3": 196.00,
    }

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)

    def _piano_note(self, freq: float, duration: float, volume: float, sr: int = 44100) -> 'np.ndarray':
        """Piano-like note: harmonics + exponential decay."""
        t = np.linspace(0, duration, int(sr * duration), endpoint=False)
        harmonics = [(1.0, 1.0), (2.0, 0.5), (3.0, 0.25), (4.0, 0.15), (5.0, 0.08), (6.0, 0.05)]
        tone = np.zeros_like(t)
        for mult, amp in harmonics:
            tone += amp * np.sin(2 * np.pi * freq * mult * t)
        attack = 0.01
        decay_rate = 3.0
        envelope = np.ones_like(t)
        atk_s = int(sr * attack)
        if atk_s > 0:
            envelope[:atk_s] = np.linspace(0, 1, atk_s)
        envelope *= np.exp(-decay_rate * np.maximum(t - attack, 0))
        return tone * envelope * volume

    def _drone(self, freq: float, duration: float, volume: float, sr: int = 44100) -> 'np.ndarray':
        """Low sustained drone with breathing movement."""
        t = np.linspace(0, duration, int(sr * duration), endpoint=False)
        d = np.sin(2 * np.pi * freq * t) * 0.7
        d += np.sin(2 * np.pi * freq * 1.5 * t) * 0.2
        breathing = 0.8 + 0.2 * np.sin(2 * np.pi * 0.05 * t)
        d *= breathing * volume
        fade = int(sr * 3)
        d[:fade] *= np.linspace(0, 1, fade)
        d[-fade:] *= np.linspace(1, 0, fade)
        return d

    def _dissonant_note(self, freq: float, duration: float, volume: float, sr: int = 44100) -> 'np.ndarray':
        """Dissonant note: two close frequencies that beat against each other."""
        t = np.linspace(0, duration, int(sr * duration), endpoint=False)
        tone = np.sin(2 * np.pi * freq * t) * 0.6
        tone += np.sin(2 * np.pi * freq * 1.06 * t) * 0.4
        envelope = np.ones_like(t)
        atk = min(int(sr * 0.5), len(t) - 1)  # cap attack at note length
        if atk > 0:
            envelope[:atk] = np.linspace(0, 1, atk)
        envelope *= np.exp(-1.0 * t)
        return tone * envelope * volume

    def _sustained_note(self, freq: float, duration: float, volume: float, sr: int = 44100) -> 'np.ndarray':
        """Single sustained note that fades to silence — for the climax."""
        t = np.linspace(0, duration, int(sr * duration), endpoint=False)
        tone = np.sin(2 * np.pi * freq * t)
        # Very slow attack, then long sustain, then very slow fade to nothing
        envelope = np.ones_like(t)
        atk = int(sr * 2.0)  # 2s attack
        envelope[:atk] = np.linspace(0, 1, atk)
        # Fade starts at 30% through and goes to zero
        fade_start = int(len(t) * 0.3)
        fade_len = len(t) - fade_start
        envelope[fade_start:] *= np.linspace(1, 0, fade_len) ** 1.5  # exponential fade
        return tone * envelope * volume

    def _save_wav(self, track: 'np.ndarray', path: Path, sr: int = 44100):
        """Normalize and save as 16-bit stereo WAV."""
        peak = np.max(np.abs(track))
        if peak > 0:
            track = track / peak * 0.5
        track_int16 = (track * 32767).astype(np.int16)
        stereo = np.column_stack([track_int16, track_int16])
        from scipy.io import wavfile
        wavfile.write(str(path), sr, stereo)
        logger.info(f"Music saved: {path}")

    def generate_act1(self, duration: float) -> Path:
        """Act 1 — Observation: Ambient piano, A minor, sparse and warm."""
        music_dir = self.output_dir / "music"
        music_dir.mkdir(parents=True, exist_ok=True)
        path = music_dir / "act1_piano.wav"

        logger.info(f"Generating Act 1 music — ambient piano ({duration:.0f}s)...")
        sr = 44100
        total = int(sr * duration)
        track = np.zeros(total, dtype=np.float64)

        # Sub-drone
        track += self._drone(55.0, duration, 0.08, sr)[:total]

        # Sparse A-minor piano notes
        pattern = [
            ("A2", 0.0, 8.0, 0.15), ("E3", 2.0, 6.0, 0.10), ("A3", 4.0, 5.0, 0.12),
            ("C4", 7.0, 5.0, 0.10), ("E4", 10.0, 4.0, 0.08), ("G4", 13.0, 4.0, 0.07),
            ("A3", 16.0, 5.0, 0.10), ("F3", 19.0, 5.0, 0.09), ("C4", 22.0, 4.0, 0.08),
            ("E4", 25.0, 4.0, 0.07), ("A2", 28.0, 8.0, 0.12), ("E3", 30.0, 6.0, 0.08),
            ("A3", 33.0, 5.0, 0.09), ("C4", 36.0, 5.0, 0.07), ("E4", 39.0, 4.0, 0.06),
        ]
        pattern_dur = 42.0
        for repeat in range(int(duration / pattern_dur) + 1):
            offset = repeat * pattern_dur
            if offset >= duration:
                break
            for note_name, start, note_dur, vol in pattern:
                actual = offset + start
                if actual >= duration:
                    break
                freq = self.PIANO_NOTES.get(note_name, 220.0)
                vol_adj = vol * (1.0 - repeat * 0.1)
                note = self._piano_note(freq, min(note_dur, duration - actual), vol_adj, sr)
                s = int(actual * sr)
                e = min(s + len(note), total)
                track[s:e] += note[:e - s]

        self._save_wav(track, path, sr)
        return path

    def generate_act2(self, duration: float) -> Path:
        """Act 2 — Inner Reality: Dark drone + dissonant sparse notes."""
        music_dir = self.output_dir / "music"
        music_dir.mkdir(parents=True, exist_ok=True)
        path = music_dir / "act2_dark.wav"

        logger.info(f"Generating Act 2 music — dark drone ({duration:.0f}s)...")
        sr = 44100
        total = int(sr * duration)
        track = np.zeros(total, dtype=np.float64)

        # Deep drone — D1 (36.7Hz) very low and ominous
        track += self._drone(36.7, duration, 0.12, sr)[:total]
        # Secondary drone — A1 (55Hz) for body
        track += self._drone(55.0, duration, 0.06, sr)[:total]

        # Sparse dissonant notes — tritones and minor seconds for unease
        # D vs Bb (tritone = "devil's interval") and D vs Eb (minor second = dissonance)
        dissonant_pattern = [
            (73.42, 0.0, 8.0, 0.08),     # D2
            (116.54, 6.0, 7.0, 0.06),    # Bb2 (tritone against D)
            (77.78, 14.0, 6.0, 0.05),    # Eb2 (minor second above D — dissonant)
            (73.42, 22.0, 8.0, 0.07),   # D2 return
            (116.54, 28.0, 6.0, 0.05),  # Bb2
            (146.83, 36.0, 5.0, 0.04),  # D3
            (155.56, 42.0, 5.0, 0.03),  # Eb3 (dissonant)
        ]
        for repeat in range(int(duration / 48.0) + 1):
            offset = repeat * 48.0
            if offset >= duration:
                break
            for freq, start, note_dur, vol in dissonant_pattern:
                actual = offset + start
                if actual >= duration:
                    break
                note = self._dissonant_note(freq, min(note_dur, duration - actual), vol * (1.0 - repeat * 0.15), sr)
                s = int(actual * sr)
                e = min(s + len(note), total)
                track[s:e] += note[:e - s]

        self._save_wav(track, path, sr)
        return path

    def generate_act3(self, duration: float) -> Path:
        """Act 3 — Climax: Near-silence, single sustained note fading to nothing."""
        music_dir = self.output_dir / "music"
        music_dir.mkdir(parents=True, exist_ok=True)
        path = music_dir / "act3_silence.wav"

        logger.info(f"Generating Act 3 music — near-silence ({duration:.0f}s)...")
        sr = 44100
        total = int(sr * duration)
        track = np.zeros(total, dtype=np.float64)

        # Single low sustained note — A1 (55Hz) — barely there, fading to silence
        # This is the emotional "held breath" before the final line
        sustain = self._sustained_note(55.0, duration, 0.10, sr)
        track += sustain[:total]

        # One single piano note at the very beginning — A2, very quiet
        # Like a last heartbeat before silence
        last_note = self._piano_note(110.0, 6.0, 0.06, sr)
        s = 0
        e = min(len(last_note), total)
        track[s:e] += last_note[:e - s]

        self._save_wav(track, path, sr)
        return path


# ============================================================
# Step 3.5: Dramatic Sting Generator (v5.2 — irreversible moment impact)
# ============================================================

class DramaticStingGenerator:
    """Generate a dramatic sub-bass + chord sting for the irreversible moment.

    The slow ambient alone doesn't create impact — the viewer expects drama.
    This generator produces a layered sting:

      Layer 1: Sub-bass impact (30-50Hz) — physical sensation, 2s with quick decay
      Layer 2: Sustained dissonant chord (low piano/synth) — emotional weight, 3s with reverb tail
      Layer 3: Brief silence (0.5s) before the chord settles in

    The result is a 3-4 second audio "hit" that:
      - Has physical presence (the sub-bass moves air through speakers)
      - Has emotional weight (the chord is dissonant, not pleasant)
      - Cuts cleanly so the sting doesn't bleed into the next scene
    """

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.sr = 44100

    def generate(self, duration: float = 3.5) -> Path:
        """Generate the dramatic sting.

        Args:
            duration: Total duration in seconds. Default 3.5s.

        Returns:
            Path to the generated WAV file.
        """
        music_dir = self.output_dir / "music"
        music_dir.mkdir(parents=True, exist_ok=True)
        path = music_dir / "irreversible_sting.wav"

        logger.info(f"Generating dramatic sting ({duration:.1f}s)...")
        t = np.linspace(0, duration, int(self.sr * duration), endpoint=False)
        track = np.zeros_like(t)

        # Layer 1: Sub-bass impact — 40Hz sine with very fast attack + decay
        # Creates physical presence through low-frequency speakers
        sub_freq = 40.0
        sub = np.sin(2 * np.pi * sub_freq * t) * 0.85
        # Fast attack (0.05s) + exponential decay (over 1.5s)
        attack = 0.05
        atk_s = int(self.sr * attack)
        envelope = np.ones_like(t)
        envelope[:atk_s] = np.linspace(0, 1, atk_s)
        envelope *= np.exp(-2.5 * np.maximum(t - attack, 0))
        sub *= envelope
        track += sub

        # Layer 2: Second sub at 60Hz for harmonic thickness
        sub2 = np.sin(2 * np.pi * 60.0 * t) * 0.5
        sub2 *= envelope * 0.8
        track += sub2

        # Layer 3: Sustained dissonant chord — minor 2nd interval (dissonance)
        # Starts at 0.3s, sustains for 2.5s, decays with reverb-like tail
        chord_start = 0.3
        chord_dur = duration - chord_start - 0.2  # leave 0.2s tail
        chord_start_s = int(self.sr * chord_start)
        chord_end_s = chord_start_s + int(self.sr * chord_dur)
        chord_t = t[chord_start_s:chord_end_s]

        # Two close frequencies — a minor 2nd (C and Db) — creates beating dissonance
        chord_freq_1 = 110.0  # A2
        chord_freq_2 = 116.54  # Bb2 (minor 2nd above A — dissonant)
        chord = (
            np.sin(2 * np.pi * chord_freq_1 * chord_t) * 0.35
            + np.sin(2 * np.pi * chord_freq_2 * chord_t) * 0.35
        )
        # Soft attack + long reverb-like decay
        chord_attack = 0.15
        chord_atk_s = int(self.sr * chord_attack)
        chord_env = np.ones_like(chord_t)
        chord_env[:chord_atk_s] = np.linspace(0, 1, chord_atk_s)
        # Long exponential decay (sustained, then fades)
        chord_env *= np.exp(-1.2 * np.maximum(chord_t - chord_attack, 0))
        # Add a touch of tremolo for unease
        tremolo = 0.85 + 0.15 * np.sin(2 * np.pi * 4.0 * chord_t)
        chord *= chord_env * tremolo
        track[chord_start_s:chord_end_s] += chord

        # Layer 4: Subtle high-frequency "air" for cinematic presence
        # Very quiet pink-noise-like texture, fades quickly
        air_t = t[:int(self.sr * 0.5)]
        air = np.random.randn(len(air_t)) * 0.04
        air *= np.exp(-8.0 * air_t)  # very fast decay
        track[:len(air_t)] += air

        # Normalize
        peak = np.max(np.abs(track))
        if peak > 0:
            track = track / peak * 0.85

        # Save as 16-bit stereo WAV
        track_int16 = (track * 32767).astype(np.int16)
        stereo = np.column_stack([track_int16, track_int16])
        from scipy.io import wavfile
        wavfile.write(str(path), self.sr, stereo)
        logger.info(f"Dramatic sting saved: {path}")
        return path


# ============================================================
# Step 4: Ambient SFX Generation
# ============================================================

class AmbientSFXGenerator:
    """Generate per-scene ambient SFX based on the scene's beat.

    Expert feedback Issue 4: "Sound must become the emotional nervous system.
    Need room tone, silence, breathing, texture, environmental intimacy.
    Each scene needs its own ambient bed."
    """

    # Per-beat ambient profiles — expert feedback 02: add micro-presence sounds
    # "breathing, bedsheet movement, distant traffic, chair creaks, kitchen hum, subtle rain"
    # These sounds create intimacy through proximity.
    BEAT_PROFILES = {
        "opening_hook": {
            "sounds": ["brown_noise_low", "sine_60hz", "breathing"],
            "description": "Bedroom at night — fan hum, breathing, sheets rustling",
            "volume": 0.28,
        },
        "contrast_memory": {
            "sounds": ["pink_noise_soft", "kitchen_hum"],
            "description": "Warm morning — birds distant, kitchen, life, cutlery",
            "volume": 0.22,
        },
        "outside_version": {
            "sounds": ["brown_noise_mid", "kitchen_hum"],
            "description": "Domestic routine — kitchen, traffic, dishes, ambient life",
            "volume": 0.20,
        },
        "first_fracture": {
            "sounds": ["brown_noise_low", "sine_50hz", "rain_light"],
            "description": "Parked car — engine hum, rain on windshield, silence",
            "volume": 0.25,
        },
        "internal_collapse": {
            "sounds": ["brown_noise_low", "breathing", "chair_creak"],
            "description": "Empty room — clock, breathing, chair creak, nothing else",
            "volume": 0.22,
        },
        "almost_moment": {
            "sounds": ["brown_noise_low", "sine_55hz", "breathing", "bedsheet"],
            "description": "Bedroom — silence, breathing, sheets shifting, fabric",
            "volume": 0.28,
        },
        "defensive_retreat": {
            "sounds": ["brown_noise_mid", "sine_120hz"],
            "description": "Living room — TV hum, controller, isolation, screen glow",
            "volume": 0.20,
        },
        "her_truth": {
            "sounds": ["white_noise_filtered", "breathing"],
            "description": "Bedroom — rain, uneven breathing, tears, window",
            "volume": 0.30,
        },
        "final_truth": {
            "sounds": ["brown_noise_low", "sine_60hz", "breathing"],
            "description": "Bedroom — fan, breathing, nothing left to say, silence",
            "volume": 0.32,
        },
    }

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)

    def generate_room_tone(self, duration: float) -> Path:
        """Generate generic room tone (fallback)."""
        sfx_dir = self.output_dir / "sfx"
        sfx_dir.mkdir(parents=True, exist_ok=True)
        output_path = sfx_dir / "room_tone.wav"

        logger.info(f"Generating room tone ({duration:.0f}s)...")
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i",
            f"anoisesrc=color=brown:duration={duration}:amplitude=0.3",
            "-filter_complex",
            f"[0:a]lowpass=f=400,volume=0.5,"
            f"afade=t=in:st=0:d=2,"
            f"afade=t=out:st={max(0,duration-3)}:d=3",
            "-ar", "44100", "-ac", "2",
            str(output_path),
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path

    def generate_for_beat(self, beat: str, duration: float) -> Path:
        """Generate scene-specific ambient SFX based on the scene's beat."""
        sfx_dir = self.output_dir / "sfx"
        sfx_dir.mkdir(parents=True, exist_ok=True)

        profile = self.BEAT_PROFILES.get(beat, {
            "sounds": ["brown_noise_low"],
            "description": "Generic room tone",
            "volume": 0.20,
        })

        output_path = sfx_dir / f"ambient_{beat}.wav"
        logger.info(f"Generating ambient for '{beat}' ({duration:.0f}s): {profile['description']}")

        # Build FFmpeg inputs based on sound types
        inputs = []
        filter_parts = []
        idx = 0

        for sound_type in profile["sounds"]:
            if sound_type == "brown_noise_low":
                inputs.extend(["-f", "lavfi", "-i",
                    f"anoisesrc=color=brown:duration={duration}:amplitude=0.3"])
                filter_parts.append(f"[{idx}:a]lowpass=f=300,volume=0.5[a{idx}]")
            elif sound_type == "brown_noise_mid":
                inputs.extend(["-f", "lavfi", "-i",
                    f"anoisesrc=color=brown:duration={duration}:amplitude=0.25"])
                filter_parts.append(f"[{idx}:a]lowpass=f=800,volume=0.4[a{idx}]")
            elif sound_type == "pink_noise_soft":
                inputs.extend(["-f", "lavfi", "-i",
                    f"anoisesrc=color=pink:duration={duration}:amplitude=0.15"])
                filter_parts.append(f"[{idx}:a]lowpass=f=2000,volume=0.3[a{idx}]")
            elif sound_type == "white_noise_filtered":
                # Rain-like: white noise band-passed
                inputs.extend(["-f", "lavfi", "-i",
                    f"anoisesrc=color=white:duration={duration}:amplitude=0.2"])
                filter_parts.append(f"[{idx}:a]highpass=f=800,lowpass=f=6000,volume=0.4,aecho=0.3:0.5:200:0.2[a{idx}]")
            elif sound_type == "rain_light":
                # Light rain — softer, more distant
                inputs.extend(["-f", "lavfi", "-i",
                    f"anoisesrc=color=white:duration={duration}:amplitude=0.1"])
                filter_parts.append(f"[{idx}:a]highpass=f=1000,lowpass=f=5000,volume=0.2,aecho=0.2:0.3:150:0.1[a{idx}]")
            elif sound_type == "breathing":
                # Breathing — slow sine wave modulated to simulate breath rhythm
                inputs.extend(["-f", "lavfi", "-i",
                    f"sine=frequency=0.3:duration={duration}"])
                filter_parts.append(f"[{idx}:a]volume=0.04,tremolo=f=0.15:d=0.8,lowpass=f=100[a{idx}]")
            elif sound_type == "bedsheet":
                # Bedsheet movement — very subtle pink noise bursts
                inputs.extend(["-f", "lavfi", "-i",
                    f"anoisesrc=color=pink:duration={duration}:amplitude=0.05"])
                filter_parts.append(f"[{idx}:a]highpass=f=200,lowpass=f=4000,volume=0.08,tremolo=f=0.1:d=0.9[a{idx}]")
            elif sound_type == "chair_creak":
                # Chair creak — low frequency creaking
                inputs.extend(["-f", "lavfi", "-i",
                    f"sine=frequency=80:duration={duration}"])
                filter_parts.append(f"[{idx}:a]volume=0.02,tremolo=f=0.1:d=0.95,lowpass=f=150[a{idx}]")
            elif sound_type == "kitchen_hum":
                # Kitchen hum — fridge/appliance hum
                inputs.extend(["-f", "lavfi", "-i",
                    f"sine=frequency=120:duration={duration}"])
                filter_parts.append(f"[{idx}:a]volume=0.05,lowpass=f=200[a{idx}]")
            elif sound_type.startswith("sine_"):
                freq = float(sound_type.replace("sine_", "").replace("hz", ""))
                inputs.extend(["-f", "lavfi", "-i",
                    f"sine=frequency={freq}:duration={duration}"])
                filter_parts.append(f"[{idx}:a]volume=0.08,lowpass=f=200[a{idx}]")
            idx += 1

        # Mix all sound layers
        mix_labels = "".join(f"[a{i}]" for i in range(idx))
        filter_parts.append(f"{mix_labels}amix=inputs={idx}:duration=longest:normalize=0[mix]")
        # Apply fade and volume
        vol = profile["volume"]
        filter_parts.append(
            f"[mix]volume={vol},"
            f"afade=t=in:st=0:d=2,"
            f"afade=t=out:st={max(0,duration-3)}:d=3[out]"
        )

        cmd = [
            "ffmpeg", "-y",
            *inputs,
            "-filter_complex",
            ";".join(filter_parts),
            "-map", "[out]",
            "-ar", "44100", "-ac", "2",
            str(output_path),
        ]

        subprocess.run(cmd, check=True, capture_output=True)
        return output_path

    def generate_rain(self, duration: float) -> Path:
        """Generate rain ambience (white noise filtered)."""
        sfx_dir = self.output_dir / "sfx"
        sfx_dir.mkdir(parents=True, exist_ok=True)
        output_path = sfx_dir / "rain.wav"

        logger.info(f"Generating rain ambience ({duration:.0f}s)...")

        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i",
            f"anoisesrc=color=white:duration={duration}:amplitude=0.15",
            "-filter_complex",
            f"[0:a]highpass=f=800,lowpass=f=6000,volume=0.4,"
            f"aecho=0.3:0.5:200:0.2,"
            f"afade=t=in:st=0:d=3,"
            f"afade=t=out:st={max(0,duration-5)}:d=5",
            "-ar", "44100",
            "-ac", "2",
            str(output_path),
        ]

        subprocess.run(cmd, check=True, capture_output=True)
        return output_path


# ============================================================
# Step 5: Audio Mixer
# ============================================================

class AudioMixer:
    """Mix narration, music, and ambient SFX into final audio track."""

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)

    def mix_scene_audio(
        self,
        narration_path: Path,
        music_path: Path | None = None,
        ambient_path: Path | None = None,
        music_volume: float = 0.6,
        ambient_volume: float = 0.3,
        narration_volume: float = 0.8,
        output_path: Path | None = None,
        # v5.0 — silence engine flags
        silence_before: float = 0.0,
        silence_after: float = 0.0,
        silence_instead: bool = False,
        # v5.1 — fade engine: smooth the music cutoff at scene boundaries.
        # Music tracks (act1/2/3) are longer than a single scene. When the
        # amix truncates to the narration length, the music cuts abruptly.
        # fade_out applies an exponential fade to the *final* mixed output
        # so the music tail bleeds naturally into the next scene's intro,
        # instead of stopping like a slammed door.
        fade_out: float = 1.5,
        fade_in: float = 0.3,
        # v5.1 — when this is the last scene, use a longer fade for a
        # proper ending. Set by the caller.
        is_last_scene: bool = False,
    ) -> Path:
        """Mix narration with background music and ambient SFX.

        Per playbook: "Create subconscious emotional immersion."
        Music and ambient should be clearly present underneath narration.
        Narration should be soft and intimate, not amplified.

        v5.0 — silence engine:
          - silence_before: prepend N seconds of ambient-only (no music, no voice)
          - silence_after: append N seconds of ambient-only
          - silence_instead: skip narration entirely; output is just ambient (used on
            the irreversible moment scene, where the visual carries the moment)

        v5.1 — fade engine:
          - fade_in: tiny fade at the start (avoids click, hides edit point)
          - fade_out: fade at the end so music doesn't cut abruptly
          - is_last_scene: extends the fade_out for a proper ending
        """
        if output_path is None:
            output_path = narration_path.parent / f"{narration_path.stem}_mixed.wav"

        # v5.1 — last-scene ending: longer fade for a proper emotional close.
        if is_last_scene:
            fade_out = max(fade_out, 3.0)

        # v5.1 — fade engine: probe the primary input's duration so we can
        # compute the correct fade-out start time. ffmpeg's afade requires
        # a non-negative start time, so we can't use st=-N.
        def _probe_duration(path: Path) -> float:
            try:
                r = subprocess.run(
                    ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                     "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
                    capture_output=True, text=True, timeout=10,
                )
                return float(r.stdout.strip())
            except Exception:
                return 0.0

        # v5.0 — silence_engine: silence_instead
        # If silence_instead is set, the scene has NO narration.
        # We mix ambient only (no music, no voice). Use ambient's own duration.
        if silence_instead:
            if ambient_path and ambient_path.exists():
                ambient_dur = _probe_duration(ambient_path)
                fade_out_start = max(0.0, ambient_dur - fade_out) if fade_out > 0 else 0.0
                fade_filter = f"volume={ambient_volume}"
                if fade_in > 0:
                    fade_filter += f",afade=t=in:st=0:d={fade_in}"
                if fade_out > 0 and fade_out_start > 0:
                    fade_filter += f",afade=t=out:st={fade_out_start}:d={fade_out}"
                cmd = [
                    "ffmpeg", "-y",
                    "-i", str(ambient_path),
                    "-af", fade_filter,
                    "-ar", "44100", "-ac", "2", "-b:a", "192k",
                    str(output_path),
                ]
                subprocess.run(cmd, check=True, capture_output=True)
                logger.info(f"Silence-instead mix (ambient only): {output_path.name}")
                return output_path
            else:
                # No ambient — produce silence
                cmd = [
                    "ffmpeg", "-y",
                    "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                    "-t", "8",  # default 8s for silence-instead
                    "-ar", "44100", "-ac", "2", "-b:a", "192k",
                    str(output_path),
                ]
                subprocess.run(cmd, check=True, capture_output=True)
                logger.info(f"Silence-instead mix (true silence): {output_path.name}")
                return output_path

        # v5.1 — probe narration duration to compute fade start time
        narr_dur = _probe_duration(narration_path)
        # Total output duration includes silence_before/after
        total_dur = narr_dur + silence_before + silence_after
        fade_out_start = max(0.0, total_dur - fade_out) if fade_out > 0 else 0.0

        inputs = []
        filter_parts = []

        # Narration — soft, not amplified
        inputs.extend(["-i", str(narration_path)])
        filter_parts.append(f"[0:a]volume={narration_volume}[voice]")

        idx = 1
        mix_labels = ["[voice]"]
        mix_weights = ["1"]  # narration at its set volume

        if music_path and music_path.exists() and music_volume > 0:
            inputs.extend(["-i", str(music_path)])
            filter_parts.append(f"[{idx}:a]volume={music_volume}[music]")
            mix_labels.append("[music]")
            mix_weights.append("1")  # equal weight — music should be clearly heard
            idx += 1

        if ambient_path and ambient_path.exists():
            inputs.extend(["-i", str(ambient_path)])
            filter_parts.append(f"[{idx}:a]volume={ambient_volume}[ambient]")
            mix_labels.append("[ambient]")
            mix_weights.append("0.5")
            idx += 1

        # v5.0 — silence engine: silence_before / silence_after
        # Insert ambient-only padding at the start (before) or end (after) of
        # the mixed narration. Music and voice are absent in the silence gaps.
        if silence_before > 0 and ambient_path and ambient_path.exists():
            # Use a separate ambient input for the silence gap so we can fade it
            inputs.extend(["-i", str(ambient_path)])
            silence_before_label = f"[sbefore]"
            filter_parts.append(
                f"[{idx}:a]volume={ambient_volume},atrim=0:{silence_before},asetpts=PTS-STARTPTS{silence_before_label}"
            )
            idx += 1
            # The main mix is now N seconds shorter — we'll concat after
            # Trim the main mix to the actual narration length so the silence
            # BEFORE is pure ambient (no music) and the rest follows.
            filter_parts.append(
                f"{''.join(mix_labels)}amix=inputs={len(mix_labels)}:duration=first:"
                f"normalize=0:weights={' '.join(mix_weights)}[narr_mix]"
            )
            # Concat silence_before + narr_mix
            filter_parts.append(
                f"{silence_before_label}[narr_mix]concat=n=2:v=0:a=1[out]"
            )
        elif silence_after > 0 and ambient_path and ambient_path.exists():
            # Trim main mix to narration length, then add silence_after ambient
            inputs.extend(["-i", str(ambient_path)])
            silence_after_label = f"[safter]"
            filter_parts.append(
                f"[{idx}:a]volume={ambient_volume},atrim=0:{silence_after},asetpts=PTS-STARTPTS{silence_after_label}"
            )
            idx += 1
            filter_parts.append(
                f"{''.join(mix_labels)}amix=inputs={len(mix_labels)}:duration=first:"
                f"normalize=0:weights={' '.join(mix_weights)}[narr_mix]"
            )
            filter_parts.append(
                f"[narr_mix]{silence_after_label}concat=n=2:v=0:a=1[out]"
            )
        else:
            # No silence gaps — original behavior
            filter_parts.append(
                f"{''.join(mix_labels)}amix=inputs={len(mix_labels)}:duration=first:"
                f"normalize=0:weights={' '.join(mix_weights)}[out]"
            )

        # v5.1 — fade engine: apply fade_in and fade_out to the final output.
        # We rename the last [out] label to [out_raw], then chain afade filters.
        # The fade-out start time is computed from the probed narration duration
        # (ffmpeg's afade requires a non-negative start time, so we can't use
        # a relative offset like st=-N).
        if fade_in > 0 or fade_out > 0:
            # Find and rename the existing [out] to [out_raw]
            for i, part in enumerate(filter_parts):
                if part.rstrip().endswith("[out]"):
                    filter_parts[i] = part[:-5] + "[out_raw]"
                    break
            # Build the fade chain
            cur = "[out_raw]"
            if fade_in > 0:
                nxt = "[out_fi]"
                filter_parts.append(f"{cur}afade=t=in:st=0:d={fade_in}{nxt}")
                cur = nxt
            if fade_out > 0 and fade_out_start > 0:
                nxt = "[out]"
                filter_parts.append(
                    f"{cur}afade=t=out:st={fade_out_start}:d={fade_out}{nxt}"
                )

        cmd = [
            "ffmpeg", "-y",
            *inputs,
            "-filter_complex",
            ";".join(filter_parts),
            "-map", "[out]",
            "-ar", "44100",
            "-ac", "2",
            "-b:a", "192k",
            str(output_path),
        ]

        subprocess.run(cmd, check=True, capture_output=True)
        logger.info(f"Mixed audio: {output_path.name}")
        return output_path

    def mix_irreversible_scene(
        self,
        ambient_path: Path | None,
        sting_path: Path | None,
        ambient_volume: float = 0.30,
        sting_volume: float = 0.85,
        duration: float = 12.0,
        output_path: Path | None = None,
        fade_out: float = 2.0,
    ) -> Path:
        """v5.2 — mix the irreversible moment's audio bed.

        This is the scene that carries the emotional weight of the entire
        video. The slow ambient alone is too soft — the viewer needs to
        FEEL the moment. So we layer:

          - The ambient bed (continuous through the scene, slightly lower than usual)
          - The dramatic sting (sub-bass + chord hit, played at the start of the scene)
          - A fade-out at the end so the impact doesn't bleed into the next scene

        Args:
            ambient_path: The per-beat ambient SFX track.
            sting_path: The dramatic sting track (sub-bass + chord).
            ambient_volume: Volume for the ambient bed (0.0-1.0). Default 0.30.
            sting_volume: Volume for the sting (0.0-1.0). Default 0.85.
            duration: Total scene duration in seconds.
            output_path: Where to write the mixed audio. Defaults to the
                ambient's directory with `_irreversible_mixed.wav` suffix.
            fade_out: Fade-out at the end of the scene in seconds. Default 2.0.

        Returns:
            Path to the generated mixed audio.
        """
        if output_path is None:
            base = (ambient_path or sting_path).parent
            output_path = base / "irreversible_mixed.wav"

        inputs = []
        filter_parts = []
        idx = 0

        # Sting (placed at the start of the scene, then padded with silence to duration)
        if sting_path and sting_path.exists():
            inputs.extend(["-i", str(sting_path)])
            filter_parts.append(
                f"[{idx}:a]volume={sting_volume},apad=whole_dur={duration},"
                f"atrim=0:{duration}[sting]"
            )
            idx += 1

        # Ambient (looped/padded to fill the full duration)
        if ambient_path and ambient_path.exists():
            inputs.extend(["-i", str(ambient_path)])
            # Pad the ambient to the full duration so it doesn't cut short
            filter_parts.append(
                f"[{idx}:a]volume={ambient_volume},apad=whole_dur={duration},"
                f"atrim=0:{duration}[amb]"
            )
            idx += 1

        # Mix the two layers
        if idx == 2:
            filter_parts.append(
                f"[sting][amb]amix=inputs=2:duration=longest:normalize=0[mixed]"
            )
        elif idx == 1:
            # Only one input — just rename the label
            if sting_path and sting_path.exists():
                filter_parts.append(f"[sting]anull[mixed]")
            else:
                filter_parts.append(f"[amb]anull[mixed]")
        else:
            # No inputs at all — produce silence
            cmd = [
                "ffmpeg", "-y",
                "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                "-t", str(duration),
                "-ar", "44100", "-ac", "2", "-b:a", "192k",
                str(output_path),
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            return output_path

        # Fade out at the end so the impact doesn't bleed
        fade_out_start = max(0.0, duration - fade_out)
        filter_parts.append(
            f"[mixed]afade=t=out:st={fade_out_start}:d={fade_out}[out]"
        )

        cmd = [
            "ffmpeg", "-y",
            *inputs,
            "-filter_complex", ";".join(filter_parts),
            "-map", "[out]",
            "-ar", "44100",
            "-ac", "2",
            "-b:a", "192k",
            str(output_path),
        ]

        subprocess.run(cmd, check=True, capture_output=True)
        logger.info(f"Irreversible scene mix: {output_path.name}")
        return output_path


# ============================================================
# Step 6: Full Pipeline Orchestrator
# ============================================================

class PsychologicalCinemaPipeline:
    """Full pipeline: playbook → narrative → refine → images → TTS → music → mix → video."""

    def __init__(
        self,
        playbook_path: str,
        manifest_path: str,
        topic_dir: str | None = None,
        output_dir: str = "output/videos",
        lmstudio_url: str = "http://localhost:1234",
        lmstudio_key: str = "sk-lm-TkM3NqaZ:CQdNsDjxGRm17O3Gg59W",
        use_adapter: bool = False,
        # LLM configuration — override the defaults per-territory.
        # These come from CLI args or from the manifest's `llm:` block.
        narrative_model: str = "qwen3-coder-30b-a3b-instruct-mlx",
        narrative_temperature: float = 0.7,
        narrative_max_tokens: int = 4000,
        refiner_model: str = "supergemma4-26b-uncensored-mlx-v2",
        refiner_temperature: float = 0.6,
        refiner_max_tokens: int = 2000,
    ):
        self.playbook_path = Path(playbook_path)
        self.manifest_path = Path(manifest_path)
        self.topic_dir = Path(topic_dir) if topic_dir else self.manifest_path.parent
        self.output_dir = output_dir
        self.lmstudio_url = lmstudio_url
        self.lmstudio_key = lmstudio_key
        # v1.1.4 — render abstraction layer integration.
        # When True, image generation routes through the OpenMontage adapter
        # (SceneIntent → RenderOrchestrator → RenderBackend). When False
        # (default), the pipeline calls SDXLGenerator directly (legacy mode).
        self.use_adapter = use_adapter

        # LLM configuration. CLI args are the primary override mechanism;
        # main() does the priority resolution (CLI > manifest > built-in).
        self.narrative_model = narrative_model
        self.narrative_temperature = narrative_temperature
        self.narrative_max_tokens = narrative_max_tokens
        self.refiner_model = refiner_model
        self.refiner_temperature = refiner_temperature
        self.refiner_max_tokens = refiner_max_tokens

        # Load configs
        with open(self.playbook_path) as f:
            self.playbook = yaml.safe_load(f)
        with open(self.manifest_path) as f:
            self.manifest = yaml.safe_load(f)

        # Load topic context if available
        self.topic_context = {}
        context_path = self.topic_dir / "CONTEXT.md"
        if context_path.exists():
            self.topic_context["context_file"] = str(context_path)

        # Derive pipeline ID
        self.pid = self.manifest_path.stem.lower().replace("_sdxl", "").replace("_revised", "")

    def _apply_emotional_impact_engine(self, scenes: list) -> None:
        """v5.0 — apply the emotional_impact_engine to the manifest's scenes.

        The 4 sub-engines (irreversible_moment, silence_engine,
        voice_modulation_engine, micro_tension_engine) are described in
        detail in:
          - Psychology/EmotionalWithdrawal/FORMULA.md
          - Psychology/EmotionalWithdrawal/emotional_impact_engine.md
          - psychological_cinema_standard.yaml v5.0+

        This method:
          1. Counts and validates the irreversible_moment scene
          2. Auto-marks pre_moment / post_moment on the surrounding scenes
          3. Computes per-scene TTS prosody override (from the
             voice_modulation_engine prosody table)
          4. Computes per-scene music_volume override (removed on
             the irreversible_moment scene)
          5. Applies the default silence_after=3.0 to the irreversible
             moment and silence_before=2.0 to the post_moment scene
             if not already set
          6. Validates at least 2 scenes use silence_before/silence_after
          7. Validates at least 1 scene has shows_duality: true

        Validation errors are LOUD — the pipeline refuses to run if the
        formula is violated.
        """
        print(f"\n{'='*70}")
        print("EMOTIONAL IMPACT ENGINE v5.0")
        print(f"{'='*70}")

        # ----------------------------------------------------------------
        # 1. Count irreversible_moment scenes — must be exactly 1
        # ----------------------------------------------------------------
        irreversible = [s for s in scenes if s.get("irreversible_moment")]
        if len(irreversible) == 0:
            print("  WARNING: No scene marked `irreversible_moment: true`.")
            print("  The video will be emotionally beautiful but lack a wound.")
            print("  See FORMULA.md Rule 1. To enable, mark one scene with:")
            print("    irreversible_moment: true")
            print("    silence_instead: true    # or voiceover <= 12 words")
            print("    beat: irreversible_moment")
            print()
        elif len(irreversible) > 1:
            raise ValueError(
                f"v5.0 FORMULA VIOLATION: {len(irreversible)} scenes marked "
                f"`irreversible_moment: true`. Must be EXACTLY 1 per video. "
                f"Scenes: {[s['scene_number'] for s in irreversible]}. "
                f"See FORMULA.md Rule 1."
            )
        else:
            ir = irreversible[0]
            ir_num = ir["scene_number"]
            print(f"  Irreversible moment: scene {ir_num} ({ir.get('title', '')})")
            # Validate that the irreversible moment has prosody override
            if not ir.get("tts_prosody_override"):
                ir["tts_prosody_override"] = {
                    "rate": "-30%",
                    "volume": "-20%",
                    "pitch": "-12Hz",
                }
            # Auto-mark pre_moment on the scene before
            if ir_num > 1:
                prev = next((s for s in scenes if s["scene_number"] == ir_num - 1), None)
                if prev:
                    prev["pre_moment"] = True
            # Auto-mark post_moment on the scene after
            if ir_num < len(scenes):
                nxt = next((s for s in scenes if s["scene_number"] == ir_num + 1), None)
                if nxt:
                    nxt["post_moment"] = True
                    if not nxt.get("silence_before"):
                        nxt["silence_before"] = 2.0
            # Default silence_instead on the irreversible moment if not set
            if not ir.get("silence_instead") and not ir.get("silence_after"):
                ir["silence_instead"] = True
            if not ir.get("silence_after"):
                ir["silence_after"] = 3.0
            # Force music to silence
            ir["_music_volume_override"] = 0.0
            # Force beat to irreversible_moment (so the SFX profile is applied)
            if not ir.get("beat"):
                ir["beat"] = "irreversible_moment"

        # ----------------------------------------------------------------
        # 2. Add an irreversible_moment beat profile to AmbientSFXGenerator
        # if it doesn't already exist
        # ----------------------------------------------------------------
        if "irreversible_moment" not in AmbientSFXGenerator.BEAT_PROFILES:
            # v1.1 — Rule 21: physical emotional proximity
            # The irreversible moment needs 5+ layers: breathing (louder),
            # cloth movement, distant fan/HVAC, chair creak, room hum, one
            # of: footsteps/rain reflection. The viewer should feel physically
            # inside the room.
            AmbientSFXGenerator.BEAT_PROFILES["irreversible_moment"] = {
                "sounds": [
                    "brown_noise_low",   # room hum (very low frequency presence)
                    "sine_60hz",         # distant fan / HVAC
                    "breathing",         # breathing, forward in the mix
                    "bedsheet",          # cloth movement (gentle fabric sound)
                    "chair_creak",       # floorboard settle / chair creak
                ],
                "description": "Irreversible moment — physical proximity. Breathing, cloth, chair, room hum, fan. The viewer is inside the room.",
                "volume": 0.42,  # louder than typical 0.20-0.28 — physically present
            }

        # ----------------------------------------------------------------
        # 3. Per-scene TTS prosody override (voice_modulation_engine)
        # ----------------------------------------------------------------
        PROSODY = {
            "default":                 {"rate": "-15%", "volume": "-10%", "pitch": "-5Hz"},
            "vulnerable":              {"rate": "-20%", "volume": "-12%", "pitch": "-7Hz"},
            "fractured":               {"rate": "-22%", "volume": "-15%", "pitch": "-8Hz"},
            "emotionally_exhausted":   {"rate": "-25%", "volume": "-18%", "pitch": "-10Hz"},
            "irreversible_moment":     {"rate": "-30%", "volume": "-20%", "pitch": "-12Hz"},
        }

        for scene in scenes:
            # If the scene has an explicit tts_prosody_override, use it
            if scene.get("tts_prosody_override"):
                scene["_tts_prosody_override"] = scene["tts_prosody_override"]
                continue
            # If the scene IS the irreversible moment, force the override
            if scene.get("irreversible_moment"):
                scene["_tts_prosody_override"] = PROSODY["irreversible_moment"]
                continue
            # Auto-pick the right register based on act + energy
            act = scene.get("act", "")
            energy = scene.get("energy", 5)
            if act == "act_1_observation":
                scene["_tts_prosody_override"] = PROSODY["default"]
            elif act == "act_2_inner_reality":
                if energy <= 3:
                    scene["_tts_prosody_override"] = PROSODY["vulnerable"]
                else:
                    scene["_tts_prosody_override"] = PROSODY["default"]
            elif act == "act_3_psychological_truth":
                if scene.get("phase") == "climax" and not scene.get("silence_instead"):
                    scene["_tts_prosody_override"] = PROSODY["emotionally_exhausted"]
                else:
                    scene["_tts_prosody_override"] = PROSODY["fractured"]
            else:
                scene["_tts_prosody_override"] = PROSODY["default"]

        # ----------------------------------------------------------------
        # 4. Validate silence usage
        # ----------------------------------------------------------------
        scenes_with_silence = [
            s for s in scenes
            if s.get("silence_before", 0) >= 1.5
            or s.get("silence_after", 0) >= 1.5
            or s.get("silence_instead")
        ]
        if len(scenes_with_silence) < 2:
            print(f"  WARNING: Only {len(scenes_with_silence)} scenes use silence.")
            print("  FORMULA.md Rule 4 requires at least 2 scenes to use silence.")
            print("  Consider adding silence_before or silence_after to 1+ scene.")
        else:
            print(f"  Silence usage: {len(scenes_with_silence)} scenes use silence_before/after/instead")

        # ----------------------------------------------------------------
        # 5. Validate duality
        # ----------------------------------------------------------------
        duality = [s for s in scenes if s.get("shows_duality")]
        if not duality:
            print("  WARNING: No scene marked `shows_duality: true`.")
            print("  FORMULA.md Rule 6 (Emotional Asymmetry) requires this.")
            print("  Mark the partner's grief scene with `shows_duality: true`.")
        else:
            print(f"  Duality: scene(s) {[s['scene_number'] for s in duality]} show her grief")

        # ----------------------------------------------------------------
        # Summary
        # ----------------------------------------------------------------
        print(f"\n  Prosody summary:")
        for scene in scenes:
            p = scene.get("_tts_prosody_override", {})
            tags = []
            if scene.get("irreversible_moment"): tags.append("IRREVERSIBLE")
            if scene.get("pre_moment"): tags.append("pre_moment")
            if scene.get("post_moment"): tags.append("post_moment")
            if scene.get("silence_instead"): tags.append("silence_instead")
            tag_str = f" [{', '.join(tags)}]" if tags else ""
            print(f"    Scene {scene['scene_number']:2d}: rate={p.get('rate'):>6} vol={p.get('volume'):>6} pitch={p.get('pitch'):>6}{tag_str}")
        print()

    async def run(self, skip_narrative: bool = False, skip_images: bool = False, auto_approve: bool = False, args_playbook: str = "", args_manifest: str = ""):
        """Run the full pipeline."""
        print(f"{'='*70}")
        print(f"PSYCHOLOGICAL CINEMA PIPELINE")
        print(f"{'='*70}")
        print(f"Playbook: {self.playbook_path.name}")
        print(f"Manifest: {self.manifest_path.name}")
        print(f"Pipeline: {self.pid}")
        print()

        scenes = self.manifest.get("scenes", [])

        # Step 1: Narrative generation (if not skipping)
        if not skip_narrative and scenes:
            print("[Step 1] Narrative already in manifest — skipping generation")
        elif not skip_narrative:
            print("[Step 1] Generating narrative...")
            # Load story file from manifest reference
            story_file = self.manifest.get("story_file", "")
            if story_file:
                story_path = self.topic_dir / story_file
            else:
                # Fallback: derive from manifest filename
                story_name = self.manifest_path.stem.replace("_template", "").replace("_revised", "").replace("_sdxl", "")
                story_path = self.topic_dir / f"{story_name}.md"

            if story_path.exists():
                story_md = story_path.read_text()
                gen = NarrativeGenerator(
                    self.playbook, self.topic_dir, self.manifest,
                    self.lmstudio_key, self.lmstudio_url,
                    model=self.narrative_model,
                    temperature=self.narrative_temperature,
                    max_tokens=self.narrative_max_tokens,
                )
                scenes = gen.generate_scenes(story_md)
                self.manifest["scenes"] = scenes

                # Save generated manifest
                generated_path = self.manifest_path.parent / f"{self.manifest_path.stem}_generated.yaml"
                with open(generated_path, "w") as f:
                    yaml.dump(self.manifest, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
                print(f"  Saved generated manifest: {generated_path.name}")
            else:
                print(f"  No story file found at {story_path}")
                return

        # Step 2: Emotional refinement
        if not skip_narrative and scenes:
            print("\n[Step 2] Refining narration...")
            refiner = EmotionalRefiner(
                self.lmstudio_key, self.lmstudio_url,
                model=self.refiner_model,
                temperature=self.refiner_temperature,
                max_tokens=self.refiner_max_tokens,
            )
            scenes = refiner.refine_narration(scenes, self.playbook)
            self.manifest["scenes"] = scenes

            # Save refined manifest
            refined_path = self.manifest_path.parent / f"{self.manifest_path.stem}_refined.yaml"
            with open(refined_path, "w") as f:
                yaml.dump(self.manifest, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            print(f"  Saved refined manifest: {refined_path.name}")

        # Write story transcript to video output directory
        video_outdir = Path(self.output_dir) / self.pid
        title = self.manifest.get("story_file", "").replace(".md", "").replace("_", " ").title()
        write_transcript(scenes, video_outdir, title)

        # Calculate total duration
        total_duration = 0.0
        for scene in scenes:
            vo = scene.get("voiceover", "")
            # Estimate: ~150 words per minute for slow narration
            words = len(vo.split())
            dur = max(8.0, (words / 150) * 60)
            scene["_estimated_duration"] = dur
            total_duration += dur

        print(f"\n  Total estimated duration: {total_duration:.0f}s ({total_duration/60:.1f} min)")
        print(f"  Scenes: {len(scenes)}")

        # ============================================================
        # REVIEW CHECKPOINT — pause for human approval before production
        # ============================================================
        if not skip_narrative:
            story_path, transcript_path = write_transcript(
                scenes, Path(self.output_dir) / self.pid, title
            )
            print(f"\n{'='*70}")
            print(f"REVIEW CHECKPOINT")
            print(f"{'='*70}")
            print(f"Story written:      {story_path}")
            print(f"Transcript written: {transcript_path}")
            print(f"Manifest saved:     {self.manifest_path.parent / f'{self.manifest_path.stem}_refined.yaml'}")
            print()
            print("Please review the story and transcript.")
            print("You can edit the voiceover text in story.md or the refined YAML.")
            print()
            if not auto_approve:
                response = input("Proceed to image + video production? [y/N/edit]: ").strip().lower()
                if response == "edit":
                    print("\nPausing for edits. Re-run with --skip-narrative when ready:")
                    print(f"  python scripts/psychological_pipeline.py \\")
                    print(f"    --playbook {args_playbook} \\")
                    print(f"    --manifest {self.manifest_path.parent / f'{self.manifest_path.stem}_refined.yaml'} \\")
                    print(f"    --skip-narrative")
                    return
                elif response != "y":
                    print("Aborted. Edit the story and re-run with --skip-narrative.")
                    return
            print("Proceeding to production...")

        # Step 3: Image generation
        if not skip_images:
            if self.use_adapter:
                # v1.1.4 — render abstraction layer path.
                # Routes through SceneIntent → RenderOrchestrator → RenderBackend.
                # This is the path OpenMontage uses when videoGen is its render backend.
                print(f"\n[Step 3] Generating images via render abstraction layer...")
                from openmontage_adapter import (
                    manifest_to_intents,
                    SDXLLocalBackend,
                    RenderOrchestrator,
                )
                # Convert manifest scenes to SceneIntents.
                # Territory and archetype are territory-specific — they should
                # come from the manifest, not be hardcoded. Fall back to
                # the topic dir name if not specified.
                territory = self.manifest.get("territory") or self.topic_dir.name.lower()
                archetype = self.manifest.get("archetype") or "slow_withdrawal"
                intents = manifest_to_intents(
                    manifest_path=str(self.manifest_path),
                    territory=territory,
                    archetype=archetype,
                    output_dir=self.output_dir,
                )
                # Initialize the SDXL backend (default, local, free)
                sdxl_backend = SDXLLocalBackend(
                    manifest_yaml=str(self.manifest_path),
                    output_dir=self.output_dir,
                )
                # Initialize the orchestrator
                orchestrator = RenderOrchestrator(
                    backends=[sdxl_backend],
                    primary="sdxl-local",
                )
                print(f"  Backends: {orchestrator.available_backends()}")
                print(f"  SceneIntents: {len(intents)}")
                # Render each scene
                for intent in intents:
                    try:
                        asset = orchestrator.render_scene(intent)
                        clip_score = asset.metadata.get("clip_score", 0.0)
                        used_ref = asset.metadata.get("used_character_reference", False)
                        ref_info = " [img2img]" if used_ref else " [txt2img]"
                        print(f"  Scene {intent.index}: score={clip_score:.4f}{ref_info} backend={asset.backend}")
                    except Exception as e:
                        print(f"  Scene {intent.index}: FAILED - {e}")
                # Report orchestrator decisions
                decisions = orchestrator.get_decisions()
                total_spent = orchestrator.total_spent()
                print(f"  Total render cost: ${total_spent:.4f}")
                print(f"  Decisions: {len(decisions)}")
            else:
                # Legacy path — call SDXLGenerator directly (no abstraction)
                print(f"\n[Step 3] Generating images with SDXL + CLIP verification...")
                # Import SDXLGenerator from generate_from_yaml
                gen_script = Path(__file__).parent / "generate_from_yaml.py"
                import importlib.util
                spec = importlib.util.spec_from_file_location("generate_from_yaml", gen_script)
                gen_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(gen_module)
                # Inject manifest path so generator can find character hero references
                self.manifest["__manifest_path__"] = str(self.manifest_path)
                gen = gen_module.SDXLGenerator(self.manifest, self.output_dir)
                for scene in scenes:
                    result = gen.generate_scene_image(self.pid, scene)
                    used_ref = result.get("used_character_reference", False)
                    ref_info = " [img2img]" if used_ref else " [txt2img]"
                    print(f"  Scene {scene['scene_number']}: score={result.get('clip_score', 0):.4f}{ref_info}")

                # v5.2 — generate the alt image for the irreversible_moment scene.
                # The pipeline uses a hard cut at the midpoint of this scene, so
                # we need a 2nd image. We generate it from scene_description_alt
                # (a slightly different composition) so the cut feels intentional.
                irr_scene = next((s for s in scenes if s.get("irreversible_moment")), None)
                if irr_scene and irr_scene.get("scene_description_alt"):
                    alt_path = Path(self.output_dir) / self.pid / "scene_images" / f"scene_{irr_scene['scene_number']:03d}_alt.png"
                    if not alt_path.exists():
                        print(f"\n  [v5.2] Generating alt image for irreversible_moment (scene {irr_scene['scene_number']})...")
                        # Mutate a copy of the scene to use the alt description
                        irr_alt = dict(irr_scene)
                        irr_alt["scene_description"] = irr_scene["scene_description_alt"]
                        result = gen.generate_scene_image(self.pid, irr_alt)
                        # The generator wrote to scene_{num}.png — rename to _alt
                        wrong_path = Path(self.output_dir) / self.pid / "scene_images" / f"scene_{irr_scene['scene_number']:03d}.png"
                        if wrong_path.exists() and not alt_path.exists():
                            import shutil
                            shutil.move(str(wrong_path), str(alt_path))
                            # The original scene image was just overwritten — we need to regenerate it
                            irr_orig = dict(irr_scene)
                            irr_orig["scene_description"] = irr_scene["scene_description"]
                            result = gen.generate_scene_image(self.pid, irr_orig)
                            print(f"  [v5.2] alt image: {alt_path.name}, original: scene_{irr_scene['scene_number']:03d}.png")
                    else:
                        print(f"  [v5.2] alt image already exists: {alt_path.name}")
        else:
            print("\n[Step 3] Skipping image generation")

        # Step 4: TTS + Music + Mix + Video
        print(f"\n[Step 4] Generating narration, music, and video...")
        import re as _re
        from app.services.video_service import VideoGenerationService
        from app.services.tts_service import TTSService

        video_svc = VideoGenerationService(self.output_dir)
        tts_svc = TTSService(self.output_dir)
        music_gen = MusicGenerator(f"{self.output_dir}/{self.pid}")
        sfx_gen = AmbientSFXGenerator(f"{self.output_dir}/{self.pid}")
        mixer = AudioMixer(f"{self.output_dir}/{self.pid}")

        # Clean any LLM artifacts from voiceover text before TTS
        for scene in scenes:
            vo = scene.get("voiceover", "")
            vo = _re.sub(r'<[^>]+>', '', vo).strip()
            scene["voiceover"] = vo

        # ============================================================
        # v5.0 — EMOTIONAL IMPACT ENGINE
        # Apply the 4 sub-engines: irreversible_moment, silence_engine,
        # voice_modulation_engine, micro_tension_engine.
        # ============================================================
        self._apply_emotional_impact_engine(scenes)

        # Generate 3 music zones
        # Act 1 (scenes 1-4): ambient piano
        # Act 2 (scenes 5-8): dark drone + dissonant notes
        # Act 3 (scenes 9-11): near-silence, single fading note
        act1_dur = sum(s.get("_estimated_duration", 12) for s in scenes if s.get("act") == "act_1_observation") + 5
        act2_dur = sum(s.get("_estimated_duration", 12) for s in scenes if s.get("act") == "act_2_inner_reality") + 5
        act3_dur = sum(s.get("_estimated_duration", 12) for s in scenes if s.get("act") == "act_3_psychological_truth") + 5

        music_act1 = music_gen.generate_act1(act1_dur)
        music_act2 = music_gen.generate_act2(act2_dur)
        music_act3 = music_gen.generate_act3(act3_dur)

        # v5.2 — dramatic sting for the irreversible_moment scene.
        # A sub-bass impact + dissonant chord that creates physical + emotional
        # impact. Generated once and reused if there are multiple irreversible
        # moments (rare, but possible).
        sting_gen = DramaticStingGenerator(f"{self.output_dir}/{self.pid}")
        # Find the irreversible moment's duration
        irr_scene = next((s for s in scenes if s.get("irreversible_moment")), None)
        if irr_scene:
            irr_dur = irr_scene.get("_estimated_duration", 12) + 5
            sting_path = sting_gen.generate(duration=min(irr_dur, 6.0))
            print(f"  Dramatic sting: {sting_path.name}")
        else:
            sting_path = None

        # EXPERT FIX 4: Generate per-scene ambient SFX (not generic room tone)
        # Each beat gets its own ambient bed: bedroom=fan+breathing, kitchen=ambience, car=engine+rain, etc.
        beat_ambient = {}
        beats_seen = set()
        for scene in scenes:
            beat = scene.get("beat", scene.get("phase", ""))
            if beat not in beats_seen:
                beats_seen.add(beat)
                scene_dur = scene.get("_estimated_duration", 15) + 5
                ambient_path = sfx_gen.generate_for_beat(beat, scene_dur)
                beat_ambient[beat] = ambient_path

        # Map scenes to their act's music track
        def get_music_for_scene(scene):
            act = scene.get("act", "")
            if act == "act_1_observation":
                return music_act1
            elif act == "act_2_inner_reality":
                return music_act2
            else:
                return music_act3

        for scene in scenes:
            scene_num = scene["scene_number"]
            vo = scene.get("voiceover", "").strip()
            effect = scene.get("ken_burns_effect", "ken-burns")
            act = scene.get("act", "")
            beat = scene.get("beat", scene.get("phase", ""))
            scene_music = get_music_for_scene(scene)
            scene_ambient = beat_ambient.get(beat)
            # v5.1 — fade engine: is_last_scene enables a longer final fade
            is_last_scene = scene is scenes[-1]

            # v5.0 — irreversible_moment: music is removed on that scene
            music_override = scene.get("_music_volume_override")
            if music_override is not None:
                music_vol = music_override
            elif act == "act_1_observation":
                music_vol = 0.35
            elif act == "act_2_inner_reality":
                music_vol = 0.25
            else:
                music_vol = 0.15  # Act 3 — barely there, let the silence speak

            # Ambient volume from the beat profile
            beat_profile = AmbientSFXGenerator.BEAT_PROFILES.get(beat, {})
            ambient_vol = beat_profile.get("volume", 0.20)

            # v5.0 — silence engine flags
            silence_instead = bool(scene.get("silence_instead", False))
            silence_before = float(scene.get("silence_before", 0.0))
            silence_after = float(scene.get("silence_after", 0.0))

            print(f"\n  --- Scene {scene_num}: {scene.get('title', '')} [{act}] ---")
            tags = []
            if scene.get("irreversible_moment"):
                tags.append("IRREVERSIBLE")
            if scene.get("pre_moment"):
                tags.append("pre_moment")
            if scene.get("post_moment"):
                tags.append("post_moment")
            if scene.get("shows_duality"):
                tags.append("duality")
            if silence_instead:
                tags.append("silence_instead")
            if silence_before > 0:
                tags.append(f"silence_before={silence_before}s")
            if silence_after > 0:
                tags.append(f"silence_after={silence_after}s")
            if tags:
                print(f"  [v5.0] {', '.join(tags)}")
            if scene_ambient:
                print(f"  Ambient: {beat} ({beat_profile.get('description', '')})")

            # TTS — with v5.0 per-scene prosody override
            prosody_override = scene.get("_tts_prosody_override")
            # silence_instead means no narration
            if vo and not silence_instead:
                # v1.1 — vocal_fracture on the irreversible moment
                vocal_fracture = bool(scene.get("irreversible_moment", False))
                print(f"  TTS...", end=" ", flush=True)
                if prosody_override:
                    print(f"[prosody: rate={prosody_override['rate']} vol={prosody_override['volume']} pitch={prosody_override['pitch']}]", end=" ", flush=True)
                if vocal_fracture:
                    print(f"[vocal_fracture]", end=" ", flush=True)
                r = await tts_svc.generate_speech(
                    self.pid, scene_num, vo,
                    prosody_override=prosody_override,
                    vocal_fracture=vocal_fracture,
                )
                if r["status"] != "completed":
                    print(f"FAILED: {r.get('error')}")
                    continue
                audio_dur = tts_svc.get_audio_duration(self.pid, scene_num)
                print(f"{audio_dur:.1f}s")
                if silence_after > 0 or silence_before > 0:
                    audio_dur = audio_dur + silence_after + silence_before
                    print(f"  Total scene duration w/ silence: {audio_dur:.1f}s")
            else:
                # No narration — scene duration comes from duration_hint or default
                if silence_instead:
                    # Parse duration_hint which may be "8-12s" (range string) or a number
                    dh = scene.get("duration_hint", 8.0)
                    if isinstance(dh, str):
                        # Take the first number from "8-12s" or "8.5s"
                        import re as _re_dur
                        m = _re_dur.search(r'(\d+(?:\.\d+)?)', dh)
                        audio_dur = float(m.group(1)) if m else 8.0
                    else:
                        audio_dur = float(dh)
                    print(f"  silence_instead: {audio_dur:.1f}s (ambient only)")
                else:
                    audio_dur = scene.get("_estimated_duration", 12.0)

            # Ken Burns — v5.2: hard cut to 2nd image for the irreversible moment
            img = Path(self.output_dir) / self.pid / "scene_images" / f"scene_{scene_num:03d}.png"
            if not img.exists():
                print(f"  No image found!")
                continue

            is_irreversible = bool(scene.get("irreversible_moment", False))
            img_alt = Path(self.output_dir) / self.pid / "scene_images" / f"scene_{scene_num:03d}_alt.png"

            if is_irreversible and img_alt.exists():
                # v5.2 — irreversible moment with hard cut
                print(f"  Ken Burns (CUT: {effect} → zoom-in)...", end=" ", flush=True)
                clip = video_svc.generate_ken_burns_clip_with_cut(
                    self.pid, scene_num, img, img_alt, audio_dur, effect, "zoom-in", cut_at=0.5,
                )
                print(f"{clip.name if clip else 'FAILED'}")
            else:
                print(f"  Ken Burns ({effect})...", end=" ", flush=True)
                clip = video_svc.generate_ken_burns_clip(self.pid, scene_num, img, audio_dur, effect)
                print(f"{clip.name}")

            # Mix narration with the act-appropriate music + ambient
            # v5.0 — silence engine: pass silence_before/after/instead
            # v5.1 — fade engine: pass is_last_scene for proper ending
            # v5.2 — dramatic sting: layer the sting for irreversible_moment scenes
            narration_path = tts_svc.get_audio_path(self.pid, scene_num)
            if silence_instead:
                # No narration file. Pass None and use silence_instead.
                # v5.2: if this is the irreversible_moment AND we have a sting,
                # layer the sting with the ambient. Without the sting, the
                # silence_instead path is just ambient — which is what the
                # user said doesn't have enough impact.
                if is_irreversible and sting_path and sting_path.exists():
                    # Use a separate path that mixes sting + ambient
                    mixed_path = mixer.mix_irreversible_scene(
                        ambient_path=scene_ambient,
                        sting_path=sting_path,
                        ambient_volume=ambient_vol,
                        sting_volume=0.85,
                        duration=audio_dur,
                        fade_out=2.0,
                    )
                else:
                    mixed_path = mixer.mix_scene_audio(
                        narration_path=Path(str(narration_path)) if narration_path else Path("/tmp/placeholder.wav"),
                        music_path=None,  # no music on the irreversible moment
                        ambient_path=scene_ambient,
                        music_volume=0.0,
                        ambient_volume=ambient_vol,
                        narration_volume=0.0,
                        silence_instead=True,
                        is_last_scene=is_last_scene,
                    )
            elif narration_path:
                mixed_path = mixer.mix_scene_audio(
                    narration_path,
                    music_path=scene_music,
                    ambient_path=scene_ambient,
                    narration_volume=0.7,
                    music_volume=music_vol,
                    ambient_volume=ambient_vol,
                    silence_before=silence_before,
                    silence_after=silence_after,
                    is_last_scene=is_last_scene,
                )
            else:
                print(f"  No narration file — skipping mix")
                continue

            # Merge mixed audio with video clip
            video_dir = Path(self.output_dir) / self.pid / "clips"
            final_clips_dir = Path(self.output_dir) / self.pid / "final_clips"
            final_clips_dir.mkdir(parents=True, exist_ok=True)

            video_path = video_dir / f"scene_{scene_num:03d}.mp4"
            output_clip = final_clips_dir / f"scene_{scene_num:03d}.mp4"

            subprocess.run([
                "ffmpeg", "-y",
                "-i", str(video_path),
                "-i", str(mixed_path),
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "192k",
                "-ar", "44100",
                "-shortest",
                str(output_clip),
            ], check=True, capture_output=True)
            print(f"  Merged: {output_clip.name}")

        # Assemble final video
        print(f"\n  --- Assembling final video ---")
        final_dir = Path(self.output_dir) / self.pid
        final_clips = sorted((final_dir / "final_clips").glob("scene_*.mp4"))
        concat = final_dir / "concat.txt"
        with open(concat, "w") as f:
            for c in final_clips:
                f.write(f"file '{c.resolve()}'\n")

        out = final_dir / "final.mp4"
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
             "-i", str(concat), "-c", "copy", str(out)],
            check=True, capture_output=True,
        )

        # Verify
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries",
             "stream=codec_type,codec_name,sample_rate,duration:format=duration,size",
             "-of", "default=noprint_wrappers=1", str(out)],
            capture_output=True, text=True,
        )
        print(f"\n{probe.stdout}")
        print(f"File: {out}")
        print(f"Size: {out.stat().st_size / (1024*1024):.1f} MB")
        print(f"\nPlay: open {out}")


async def main():
    parser = argparse.ArgumentParser(description="Psychological Cinema Pipeline")
    parser.add_argument("--playbook", required=True, help="Path to playbook YAML")
    parser.add_argument("--manifest", required=True, help="Path to video manifest YAML")
    parser.add_argument("--topic-dir", default=None, help="Topic directory (defaults to manifest dir)")
    parser.add_argument("--output-dir", default="output/videos", help="Output directory")
    parser.add_argument("--skip-narrative", action="store_true", help="Skip narrative generation/refinement")
    parser.add_argument("--skip-images", action="store_true", help="Skip image generation")
    parser.add_argument("--auto-approve", action="store_true", help="Skip review checkpoint — proceed to production automatically")
    parser.add_argument("--use-adapter", action="store_true", help="Route image generation through the OpenMontage render abstraction layer (SceneIntent → RenderOrchestrator → RenderBackend)")

    # LLM configuration — these can also be set in the manifest's `llm:` block.
    # CLI overrides manifest overrides built-in defaults.
    parser.add_argument("--narrative-model", default=None,
                        help="Model name for the NarrativeGenerator (scene generation). Default: qwen3-coder-30b-a3b-instruct-mlx")
    parser.add_argument("--narrative-temperature", type=float, default=None,
                        help="Sampling temperature for scene generation. Default: 0.7")
    parser.add_argument("--narrative-max-tokens", type=int, default=None,
                        help="Max tokens for scene generation. Default: 4000")
    parser.add_argument("--refiner-model", default=None,
                        help="Model name for the EmotionalRefiner (second-pass narration). Default: supergemma4-26b-uncensored-mlx-v2")
    parser.add_argument("--refiner-temperature", type=float, default=None,
                        help="Sampling temperature for the refiner. Default: 0.6")
    parser.add_argument("--refiner-max-tokens", type=int, default=None,
                        help="Max tokens for the refiner. Default: 2000")
    parser.add_argument("--lmstudio-url", default=None,
                        help="LMStudio base URL. Default: http://localhost:1234")
    parser.add_argument("--lmstudio-key", default=None,
                        help="LMStudio API key. Default: built-in dev key")

    args = parser.parse_args()

    # Read manifest's llm block (if any) so we can show defaults before constructing.
    import yaml as _yaml
    with open(args.manifest) as _f:
        _manifest = _yaml.safe_load(_f) or {}
    _llm = _manifest.get("llm", {}) if isinstance(_manifest, dict) else {}

    def _pick(cli_val, manifest_key, default):
        """CLI > manifest > built-in default."""
        if cli_val is not None:
            return cli_val
        if manifest_key in _llm:
            return _llm[manifest_key]
        return default

    pipeline = PsychologicalCinemaPipeline(
        playbook_path=args.playbook,
        manifest_path=args.manifest,
        topic_dir=args.topic_dir,
        output_dir=args.output_dir,
        use_adapter=args.use_adapter,
        lmstudio_url=_pick(args.lmstudio_url, "lmstudio_url", "http://localhost:1234"),
        lmstudio_key=_pick(args.lmstudio_key, "lmstudio_key", "sk-lm-TkM3NqaZ:CQdNsDjxGRm17O3Gg59W"),
        narrative_model=_pick(args.narrative_model, "narrative_model", "qwen3-coder-30b-a3b-instruct-mlx"),
        narrative_temperature=float(_pick(args.narrative_temperature, "narrative_temperature", 0.7)),
        narrative_max_tokens=int(_pick(args.narrative_max_tokens, "narrative_max_tokens", 4000)),
        refiner_model=_pick(args.refiner_model, "refiner_model", "supergemma4-26b-uncensored-mlx-v2"),
        refiner_temperature=float(_pick(args.refiner_temperature, "refiner_temperature", 0.6)),
        refiner_max_tokens=int(_pick(args.refiner_max_tokens, "refiner_max_tokens", 2000)),
    )
    await pipeline.run(
        skip_narrative=args.skip_narrative,
        skip_images=args.skip_images,
        auto_approve=args.auto_approve,
        args_playbook=args.playbook,
        args_manifest=args.manifest,
    )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())