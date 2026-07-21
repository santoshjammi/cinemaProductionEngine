Genesis Example (GEX)
GEX-003 — Example Scene Specification

Document ID: GEX-003
Title: Example Scene Specification — "The Kitchen at Dawn"
Version: 1.0.0
Status: Example
Authority: Derived from GSPEC-001

1. Purpose

A complete, validated example scene specification for the opening scene of
"The Night He Stopped Reaching For Her" (GEX-001). Use this as a reference for
the structure, classification tagging, and traceability expected in a finished
scene specification.

2. Example

```json
{
  "$schema": "genesis://schemas/json/scene-specification.schema.json",
  "scene_id": "SCENE-001",
  "schema_version": "1.0.0",
  "status": "Validated",
  "production_id": "BRIEF-001",
  "scene_number": 1,
  "title": "The Kitchen at Dawn",

  "narrative_function": {
    "purpose": "Establish the silence between Ethan and Lena before the story questions it.",
    "placement": "opening",
    "classification": "Explicit",
    "evidence": ["BRIEF-001 synopsis"],
    "confidence": 1.0
  },

  "location": {
    "place": "Morrison home — kitchen",
    "time_of_day": "pre-dawn, 6:14 AM",
    "season": "late autumn",
    "classification": "Explicit",
    "evidence": ["BRIEF-001 setting"]
  },

  "characters_present": [
    {"character_id": "CHAR-001", "name": "Ethan Morrison"},
    {"character_id": "CHAR-002", "name": "Lena Morrison"}
  ],

  "beats": [
    {
      "beat": 1,
      "summary": "Ethan makes coffee. The kettle is the loudest sound in the house.",
      "intent": "Show competence as a substitute for connection.",
      "classification": "Inferred",
      "evidence": ["CHAR-001 core_wound", "CHAR-001 values"],
      "confidence": 0.76
    },
    {
      "beat": 2,
      "summary": "Lena enters, pours her own cup without acknowledging his.",
      "intent": "Establish that the silence is mutual, not hostile.",
      "classification": "Inferred",
      "evidence": ["BRIEF-001 synopsis", "CHAR-002 description"],
      "confidence": 0.72
    },
    {
      "beat": 3,
      "summary": "Ethan says 'Happy anniversary.' Lena says 'Thank you.' Neither looks up.",
      "intent": "The dialogue is correct; the absence is in the eye contact.",
      "classification": "Explicit",
      "evidence": ["BRIEF-001 synopsis"],
      "confidence": 1.0
    },
    {
      "beat": 4,
      "summary": "Ethan touches his wedding band. Lena notices and looks away.",
      "intent": "Plant the gesture that will pay off in the final scene.",
      "classification": "Inferred",
      "evidence": ["CHAR-001 physicality.gesture"],
      "confidence": 0.8
    }
  ],

  "visual": {
    "shot_language": "Static mid-shots, one insert on the wedding band.",
    "camera": "Tripod only; no handheld in this scene.",
    "lighting": "Practical kitchen light, cold blue from the window, warm tungsten overhead.",
    "palette": ["muted warm tungent", "cold pre-dawn blue", "off-white countertop"],
    "classification": "Inferred",
    "evidence": ["BRIEF-001 visual_style", "BRIEF-001 setting.atmosphere"],
    "confidence": 0.78
  },

  "sound": {
    "diegetic": ["kettle", "ceramic on quartz", "a refrigerator hum"],
    "non_diegetic": ["ambient piano, single low note, no melodic movement"],
    "silence": "The pause after 'Thank you' is held for four seconds.",
    "classification": "Inferred",
    "evidence": ["BRIEF-001 music_style"],
    "confidence": 0.7
  },

  "dialogue": [
    {
      "speaker": "Ethan Morrison",
      "line": "Happy anniversary.",
      "subtext": "I am still here. Please notice.",
      "classification": "Inferred",
      "evidence": ["CHAR-001 core_desire"],
      "confidence": 0.74
    },
    {
      "speaker": "Lena Morrison",
      "line": "Thank you.",
      "subtext": "I heard you. I do not have the energy to answer what you are really asking.",
      "classification": "Inferred",
      "evidence": ["CHAR-002 core_fear (assumed)"],
      "confidence": 0.61,
      "needs_confirmation": true
    }
  ],

  "emotional_trajectory": {
    "start": "Quiet competence",
    "end": "Quiet recognition that the silence is shared",
    "shift": "From habit to awareness, without resolution.",
    "classification": "Inferred",
    "evidence": ["BRIEF-001 theme", "scene beats"],
    "confidence": 0.73
  },

  "estimated_duration_seconds": 95,
  "classification": "Inferred",
  "evidence": ["BRIEF-001 constraints.target_duration_minutes", "beat count"],
  "confidence": 0.6,

  "dependencies": {
    "characters": ["CHAR-001", "CHAR-002"],
    "props": ["wedding band", "two coffee cups", "kettle"],
    "locations": ["Morrison home — kitchen"]
  },

  "traceability": {
    "origin": "GAS-006 Scene Architect",
    "workflow": "GWS-001 stage: architecture",
    "revision": [{"version": "1.0.0", "at": "2026-07-19", "by": "GAS-006"}]
  }
}
```

3. Validation Notes

- Every beat, dialogue line, and craft section carries a classification tag.
- The Lena subtext is flagged `needs_confirmation` because confidence is below 0.65.
- Visual and sound sections derive from brief style constraints, not invented.
- No shot lists, storyboards, or render instructions; Genesis boundary respected.
- Traceability records origin agent, workflow stage, and revision history.

4. Usage

- Reference for scene specification authors.
- Fixture for GTEST-002 (schema conformance) and GTEST-003 (agent output).
- Companion to GEX-001 (brief) and GEX-002 (Ethan Morrison Character DNA).