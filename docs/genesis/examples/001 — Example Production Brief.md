Genesis Example (GEX)
GEX-001 — Example Production Brief

Document ID: GEX-001
Title: Example Production Brief — "The Night He Stopped Reaching For Her"
Version: 1.0.0
Status: Example
Authority: Derived from GSPEC-001

1. Purpose

A complete, validated example Production Brief for the short film "The Night He
Stopped Reaching For Her". Use this as a reference for what a finished brief
looks like. It is the source for BRIEF-001 in the Asset Registry (GAREG-001)
and the input for the end-to-end tests (GTEST-005).

2. Example

```yaml
# Production Brief — conforms to GSPEC-001 / GSS-NNN
schema_id: genesis://schemas/yaml/production-brief.schema.yaml
brief_id: BRIEF-001
title: "The Night He Stopped Reaching For Her"
version: 1.0.0
status: Validated

synopsis: |
  Ethan and Lena Morrison have been married for eleven years. They share a
  house in Portland, a quiet routine, and a silence that has grown louder than
  any argument. On the night of their anniversary, Ethan reaches for Lena in
  bed — a gesture she once answered without thinking. Tonight she turns away.
  The film follows the next fourteen hours: a kitchen at dawn, a drive to the
  office, a phone call that is almost honest, and a return home where Ethan
  finally says the thing he has been hiding for years.

  The story is not about infidelity. It is about the slow disappearance of a
  person who once felt known, and the moment a marriage admits that it has
  become a performance. By morning, both characters understand that intimacy
  is not a habit to be maintained but a question to be asked again.

territory: "The Quiet Marriage"
theme: "When intimacy becomes a performance, the heart learns to hide."
psychological_truth: "The fear of rejection transforms affection into anxiety."

characters:
  - name: "Ethan Morrison"
    role: protagonist
    description: >
      A 42-year-old structural engineer who has spent a decade confusing
      reliability with love. He is calm, precise, and emotionally elsewhere.
    core_fear: "That he has become invisible to the person who once saw him."
  - name: "Lena Morrison"
    role: protagonist
    description: >
      A 39-year-old freelance editor who edits other people's words because
      she no longer trusts her own. She is warm in public, absent in private.
    core_fear: "That she stopped being knowable long before Ethan stopped asking."
  - name: "Maya Chen"
    role: supporting
    description: >
      Lena's closest friend and the only person who notices the silence.
      A family therapist who refuses to therapize her friends.
    core_fear: "That she sees the ending before they do."

setting:
  time_period: "Contemporary"
  location: "Portland, Oregon"
  atmosphere: >
    Intimate domestic spaces, muted warm tones, late-autumn light. Rain on
    windows. The house is clean and tired.

constraints:
  target_duration_minutes: 12
  resolution: "1024x576"
  aspect_ratio: "16:9"
  visual_style: >
    Cinematic, shallow depth of field, naturalistic lighting, handheld only
    in moments of emotional rupture.
  narration_voice: "en-US-GuyNeural"
  music_style: >
    Ambient piano, minimal, with long silences. No melodic resolution until
    the final scene.

references:
  - "In the Bedroom (2001) — tonal reference"
  - "Paris, Texas (1984) — silence as dialogue"
  - "Marriage Story (2019) — domestic specificity"
```

3. Validation Notes

- All required GSPEC-001 fields populated.
- Both protagonists have explicit core fears.
- Setting atmosphere is concrete, not abstract.
- Constraints match the default constraints (CON-001) with duration set to 12.
- No media assets referenced; Genesis boundary respected.

4. Usage

- Input for the end-to-end test suite (GTEST-005).
- Source for BRIEF-001 (GAREG-001).
- Companion to GEX-002 (Ethan Morrison Character DNA) and GEX-003 (Scene Spec).