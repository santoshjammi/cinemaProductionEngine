Genesis Specification (GSPEC)
GSPEC-001 — Production Brief Format

Document ID: GSPEC-001
Title: Production Brief Format Specification
Version: 1.0.0
Status: Specification
Authority: Derived from GFS-000, GFS-010

1. Purpose

This Specification defines the format and required fields for a Production Brief — the initial input to the Genesis Engine. The brief is the human creator's expression of creative intent.

2. Format

The Production Brief is a YAML document with the following structure:

2.1 Required Fields

title: "string"
synopsis: "string (1-3 paragraphs describing the story)"
territory: "string (the emotional domain, e.g. 'The Quiet Marriage')"
theme: "string (the central emotional question)"

2.2 Optional Fields

psychological_truth: "string (the core insight the story reveals)"
characters:
  - name: "string"
    role: "protagonist | antagonist | supporting | tertiary"
    description: "string"
    core_fear: "string (optional)"

setting:
  time_period: "string"
  location: "string"
  atmosphere: "string"

constraints:
  target_duration_minutes: number
  target_resolution: "string"
  target_aspect_ratio: "string"
  visual_style: "string"
  music_style: "string"
  narration_voice: "string"

references:
  - type: "image | video | text"
    url: "string"
    description: "string"

3. Example

title: "The Night He Stopped Reaching For Her"
synopsis: "A married couple's slow drift told through accumulated micro-moments..."
territory: "The Quiet Marriage"
theme: "When intimacy becomes a performance, the heart learns to hide."
psychological_truth: "The fear of rejection transforms affection into anxiety."
characters:
  - name: "Ethan Morrison"
    role: "protagonist"
    description: "Marriage counselor, cautious, emotionally reserved"
    core_fear: "Fear of rejection"
  - name: "Claire Morrison"
    role: "supporting"
    description: "Graphic designer, creative, deeply intuitive"
    core_fear: "Fear of abandonment"
setting:
  time_period: "Contemporary"
  location: "Portland, Oregon"
  atmosphere: "Intimate domestic spaces, muted warm tones"
constraints:
  target_duration_minutes: 8
  target_resolution: "1024x576"
  target_aspect_ratio: "16:9"
  visual_style: "Cinematic, shallow depth of field, film grain"
  narration_voice: "en-US-GuyNeural"

4. Validation

- Title must be non-empty
- Synopsis must be at least 100 characters
- Territory must be non-empty
- Theme must be non-empty
- At least one character must be defined
- Target duration must be between 1 and 60 minutes
