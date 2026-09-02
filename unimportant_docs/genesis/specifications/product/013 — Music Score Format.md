Genesis Specification (GSPEC)
GSPEC-010 — Music Score Format

Document ID: GSPEC-010
Title: Music Score Format Specification
Version: 1.0.0
Status: Specification
Authority: Derived from GO-110 Audio, Music, Sound Design & Silence Ontology

1. Purpose

This Specification defines the format for a music score — the complete specification of the musical architecture of a production.

2. Format

music_score:
  version: "1.0.0"

  architecture:
    emotional_zones:
      - zone: "act_1"
        title: "Observation"
        emotional_state: "warm_nostalgic"
        tempo_bpm: 70
        key: "C Major"
        instrumentation: ["piano", "strings", "soft pads"]
        volume: 0.4
      - zone: "act_2"
        title: "Inner Reality"
        emotional_state: "quiet_unease"
        tempo_bpm: 60
        key: "A Minor"
        instrumentation: ["cello", "bass drone", "sparse piano"]
        volume: 0.3
      - zone: "act_3"
        title: "Psychological Truth"
        emotional_state: "devastating_quiet"
        tempo_bpm: 50
        key: "F Major"
        instrumentation: ["solo piano", "silence"]
        volume: 0.35
      - zone: "sting"
        title: "Irreversible Moment"
        emotional_state: "shock_recognition"
        tempo_bpm: 40
        key: "D Minor"
        instrumentation: ["low brass", "sub bass", "silence"]
        volume: 0.5

  scene_cues:
    - scene_number: integer
      zone: "act_1 | act_2 | act_3 | sting | none"
      volume: number (0.0-1.0)
      duration_seconds: number
      mood: "string"
      silence_before: number (optional)
      silence_after: number (optional)

  motifs:
    - name: "string"
      description: "string"
      scenes: [integer]
      emotional_association: "string"

3. Validation

- Each scene must have a music cue assignment
- Volume must be between 0.0 and 1.0
- Tempo must be between 20 and 200 BPM
- The sting zone should only be used for irreversible moments
- Silence (zone: none) must be intentional, not a gap
