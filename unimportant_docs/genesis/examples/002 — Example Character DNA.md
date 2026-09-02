Genesis Example (GEX)
GEX-002 — Example Character DNA

Document ID: GEX-002
Title: Example Character DNA — Ethan Morrison
Version: 1.0.0
Status: Example
Authority: Derived from GSPEC-001

1. Purpose

A complete, validated example Character DNA for Ethan Morrison, derived from
BRIEF-001 (GEX-001). Use this as a reference for the depth, structure, and
classification tagging expected in a finished Character DNA.

2. Example

```json
{
  "$schema": "genesis://schemas/json/character-dna.schema.json",
  "character_id": "CHAR-001",
  "schema_version": "1.0.0",
  "status": "Validated",
  "production_id": "BRIEF-001",

  "identity": {
    "name": "Ethan Morrison",
    "role": "protagonist",
    "age": 42,
    "occupation": "Structural engineer",
    "location": "Portland, Oregon",
    "classification": "Explicit",
    "evidence": ["BRIEF-001 characters[0]"]
  },

  "core_wound": {
    "statement": "He learned early that being needed is the safest form of love.",
    "classification": "Inferred",
    "evidence": ["BRIEF-001 synopsis", "BRIEF-001 characters[0].description"],
    "confidence": 0.78
  },

  "core_fear": {
    "statement": "That he has become invisible to the person who once saw him.",
    "classification": "Explicit",
    "evidence": ["BRIEF-001 characters[0].core_fear"],
    "confidence": 1.0
  },

  "core_desire": {
    "statement": "To be asked a question he cannot answer with competence.",
    "classification": "Inferred",
    "evidence": ["core_wound", "core_fear"],
    "confidence": 0.71
  },

  "ghost": {
    "statement": "His father left without saying why. Ethan has spent his life being the man who stays.",
    "classification": "Inferred",
    "evidence": ["core_wound"],
    "confidence": 0.62,
    "needs_confirmation": true
  },

  "values": [
    {"value": "Reliability", "classification": "Explicit", "evidence": ["BRIEF-001 characters[0].description"]},
    {"value": "Precision", "classification": "Inferred", "evidence": ["occupation"]},
    {"value": "Emotional restraint", "classification": "Inferred", "evidence": ["synopsis"], "confidence": 0.66}
  ],

  "voice": {
    "pace": "slow",
    "register": "low",
    "vocabulary": "concrete, technical metaphors",
    "avoidance": "does not use the word 'love' in dialogue",
    "classification": "Inferred",
    "evidence": ["occupation", "core_wound"],
    "confidence": 0.7
  },

  "physicality": {
    "posture": "contained, shoulders forward",
    "gesture": "touches his wedding band when anxious",
    "movement": "economical, never idle",
    "classification": "Assumed",
    "evidence": ["visual_style reference"],
    "confidence": 0.5,
    "assumption": "consistent with cinematic intimate drama convention"
  },

  "arc": {
    "start_state": "Performs love through reliability; believes presence is enough.",
    "mid_state": "Confronted by Lena's withdrawal and Maya's quiet witness.",
    "end_state": "Admits the thing he has been hiding; chooses to be asked, not needed.",
    "transformation": "From competent to vulnerable.",
    "classification": "Inferred",
    "evidence": ["synopsis", "theme", "psychological_truth"],
    "confidence": 0.74
  },

  "relationships": [
    {
      "to": "Lena Morrison",
      "type": "spouse",
      "dynamic": "He reaches; she has stopped reaching back.",
      "tension": "His need to be needed vs. her need to be known.",
      "classification": "Inferred",
      "evidence": ["synopsis", "characters[1]"],
      "confidence": 0.8
    },
    {
      "to": "Maya Chen",
      "type": "acquaintance",
      "dynamic": "He senses she sees the marriage more clearly than he does.",
      "classification": "Inferred",
      "evidence": ["characters[2].description"],
      "confidence": 0.6
    }
  ],

  "traceability": {
    "origin": "GAS-004 Character Architect",
    "workflow": "GWS-001 stage: reasoning",
    "revision": [{"version": "1.0.0", "at": "2026-07-19", "by": "GAS-004"}]
  }
}
```

3. Validation Notes

- Every field carries a classification tag.
- Inferred assertions carry evidence and confidence.
- The ghost is flagged `needs_confirmation` because confidence is below 0.65.
- Assumed assertion carries an explicit assumption statement.
- Traceability records origin agent, workflow stage, and revision history.
- No media references; Genesis boundary respected.

4. Usage

- Reference for Character DNA authors.
- Fixture for GTEST-002 (schema conformance) and GTEST-003 (agent output).
- Companion to GEX-001 (brief) and GEX-003 (scene spec).