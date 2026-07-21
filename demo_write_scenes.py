#!/usr/bin/env python3
"""
demo_write_scenes.py — writes rich cinematic scene pages to scenes.json using mock data.

Run this to see exactly what the structured output looks like:
    python3 demo_write_scenes.py
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Project root on PATH
sys.path.insert(0, str(Path(__file__).resolve().parent))

from pipeline.scene_file_writer import SceneFileWriter

# ── mock pipeline data (what the LLM stages would produce) ───────────────────

MOCK_STORY = {
    "title": "The Quiet Room",
    "logline": "A man slowly withdraws from his marriage after repeated small rejections.",
    "synopsis": "Over the course of one week, Aryan notices his wife Sia growing increasingly distant. Each attempt at connection is met with a polite deflection. The film follows his quiet internal unraveling as love transforms into fear — fear of needing someone who no longer needs him back.",
}

MOCK_SCENES = [
    {
        "id": 1,
        "title": "Morning Routine",
        "description": "Aryan pours two cups of coffee. Sia doesn't look up from her phone.",
        "location": "Kitchen — Dawn",
        "time": "Dawn",
        "duration_estimate": "2 Mins",
        "characters": ["ARYAN", "SIA"],
    },
    {
        "id": 2,
        "title": "The Mirror",
        "description": "Aryan stands before the bathroom mirror. He studies his own tired eyes.",
        "location": "Bathroom — Midnight",
        "time": "Midnight",
        "duration_estimate": "3 Mins",
        "characters": ["ARYAN"],
    },
    {
        "id": 3,
        "title": "Dinner Silence",
        "description": "Clink of forks against plates. Neither speaks. The TV murmurs in the background.",
        "location": "Dining Room — Evening",
        "time": "Evening",
        "duration_estimate": "2.5 Mins",
        "characters": ["ARYAN", "SIA"],
    },
]

MOCK_DIALOGUES = [
    {"id": 1, "sceneNumber": 1, "speaker": "ARYAN", "emotion": "Hopeful but tentative", "delivery": "Quietly", "text": "Did you sleep?"},
    {"id": 2, "sceneNumber": 1, "speaker": "SIA", "emotion": "Distracted / polite deflection", "delivery": "Without looking up", "text": "Mhm."},
    {"id": 3, "sceneNumber": 1, "speaker": "ARYAN", "emotion": "Quietly hopeful", "delivery": "Almost a whisper", "text": "I made coffee. Your usual."},
    {"id": 4, "sceneNumber": 2, "speaker": "ARYAN", "emotion": "Narration / voiceover", "delivery": "Flat, exhausted", "text": "I think I've stopped wanting to be wanted because trying hurts less when you stop."},
    {"id": 5, "sceneNumber": 3, "speaker": "ARYAN", "emotion": "Narration / voiceover", "delivery": "Hollow", "text": "Love wasn't what died. It was just… forgotten. Like a room we used to share."},
]

MOCK_PROMPTS = [
    {"id": 1, "sceneNumber": 1, "cinematicPrompt": "Wide shot of a dimly lit kitchen at dawn. Cold blue lighting, shallow depth of field.", "cameraAngle": "Wide Shot", "lighting": "Cold blue ambient", "colorPalette": ["#1a2b4c", "#4a6fa5", "#8fa8c4"], "visualStyle": "Neo-noir minimalism"},
    {"id": 2, "sceneNumber": 2, "cinematicPrompt": "Close-up on Aryan's face reflected in a foggy bathroom mirror. Steam rising. Harsh single light source.", "cameraAngle": "Extreme Close-Up", "lighting": "Harsh overhead fluorescent", "colorPalette": ["#c4a882", "#3e2723", "#f5f0eb"], "visualStyle": "Psychological realism"},
    {"id": 3, "sceneNumber": 3, "cinematicPrompt": "Medium two-shot of a couple sitting at a dining table. Warm amber light from a single lamp, deep shadows between them.", "cameraAngle": "Medium Two-Shot", "lighting": "Warm amber practical / deep shadows", "colorPalette": ["#b8860b", "#2c1810", "#f4e4c1"], "visualStyle": "Dutch-angle tension"},
]

MOCK_AUDIO = [
    {"id": 1, "sceneNumber": 1, "sfx": "Clock ticking. Fridge hum. Coffee pouring.", "musicCue": "None — diegetic sound only", "voiceoverScript": ""},
    {"id": 2, "sceneNumber": 2, "sfx": "Water dripping. Distant city sounds.", "musicCue": "Low cello drone, slow tempo", "voiceoverScript": "I think I've stopped wanting to be wanted because trying hurts less when you stop."},
    {"id": 3, "sceneNumber": 3, "sfx": "Clink of forks. TV murmur.", "musicCue": "Silence — then a single piano note every 8 seconds", "voiceoverScript": "Love wasn't what died. It was just… forgotten. Like a room we used to share."},
]


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    base = Path("pipeline/output/ew001")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = base / f"gen_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    writer = SceneFileWriter(run_dir)
    out_path = writer.write(
        story=MOCK_STORY,
        scenes=MOCK_SCENES,
        dialogues=MOCK_DIALOGUES,
        prompts=MOCK_PROMPTS,
        audio=MOCK_AUDIO,
    )

    print(f"\n✅  Scene file written to: {out_path}")
    print(f"   Total scene pages: {len(MOCK_SCENES)}")
    print("\n── Preview (first scene) ──\n")
    with open(out_path) as fh:
        data = json.load(fh)
        print(json.dumps(data["scenes"][0], indent=2))


if __name__ == "__main__":
    main()
