# Movie OS Screenplay Specification v1.0

## Overview

The Movie OS Screenplay is the **canonical creative artifact** for every production. It answers one question:

> **"What happens?"**

It is NOT a traditional Hollywood screenplay format. It is NOT free-form prose. It is a **structured Markdown specification optimized for AI agents and production**.

Everything else in the pipeline derives from the screenplay:
- The timeline references the screenplay (not duplicating creative content)
- Agents read the screenplay to generate assets
- Evaluation agents score the screenplay before rendering

## File Format

Each scene uses **YAML frontmatter** for metadata + **structured sections** for content.

### Scene Structure

```markdown
# [Production Title]

## Characters
- **[Character Name]** (age) — brief description, speech style
- **[Character Name]** (age) — brief description, speech style

---

## ACT 1 — [Act Title]

### SCENE [N]: [Scene Title] [PHASE: hook|plot|climax|resolution]

**Purpose:** [Narrative purpose of this scene]
**Location:** [Where this happens]
**Time:** [Time of day / temporal context]
**Characters:** [Who is present]
**Emotion:** [Primary emotional state]
**Mood:** [Atmospheric quality]

#### Dialogue

**[CHARACTER_NAME]**
*[delivery]* "[dialogue line]"
*(subtext: what they really mean)*

**[CHARACTER_NAME]**
"[response line]"

#### Action

*[description of physical action, movement, gesture]*

#### Beat

*[beat_type]: [duration] — [description]*

#### Silence

*[silence_description]*

#### Narration (optional)

*[narrator voiceover text]*

#### Director Notes

- *[camera intent: e.g., "Close-up. Warm practical lighting. Shallow depth of field."]*
- *[music intent: e.g., "fear_theme, intensity 0.4, fade_in 3s"]*
- *[lighting intent]*
- *[any other directorial guidance]*

---
```

### YAML Frontmatter (Per Scene)

Each scene MAY include YAML frontmatter for machine-readable metadata:

```yaml
---
scene_number: 1
title: Morning Ritual
phase: hook
purpose: Establish comfortable silence and shared history
location: Apartment Kitchen
time: morning
characters: [ethan, claire]
emotion: comfort
mood: warm_intimate
duration_seconds: 45
dialogue_density: high
music_intent: family_theme
camera_intent: close-up, shallow DOF, warm practical lighting
---
```

### Key Conventions

1. **Character names in ALL CAPS** before dialogue — easy for AI parsing
2. **Delivery in italics** before dialogue line — indicates tone/manner
3. **Subtext in parentheses** after dialogue — what the character really means
4. **Actions in italics** as separate paragraphs — physical movement/gesture
5. **Beats labeled explicitly** — `*[pause]: 2s — Ethan looks at his coffee]*`
6. **Silence described** — `*[3 seconds of silence. The refrigerator hums.]*`
7. **Narration in blockquotes** — separates narrator from character voice
8. **Director notes as bullet list** — camera, music, lighting guidance

### Emotional Beats Types

| Type | Duration | Purpose |
|------|----------|---------|
| `pause` | 1-3s | Natural speech pause |
| `silence` | 3-10s | Meaningful quiet — audience sits with emotion |
| `action_beat` | 2-5s | Physical action that carries emotional weight |
| `beat` | 1-2s | Brief moment of realization or shift |
| `long_silence` | 10-30s | The "unforgettable scene" — no dialogue, just presence |

### Dialogue Delivery Types

| Delivery | Use Case |
|----------|----------|
| *whispered* | Intimate, vulnerable moments |
| *hesitant* | Fear-based withdrawal, uncertainty |
| *laughing* | Warmth, shared history |
| *deflected* | Avoidance, changing subject |
| *quietly* | Suppressed emotion |
| *without looking up* | Distraction, emotional distance |
| *after a pause* | Hesitation before vulnerability |
| *automatically* | Habitual responses, emotional numbness |

## Example Scene (Complete)

```markdown
### SCENE 1: Morning Ritual [HOOK]

**Purpose:** Establish comfortable silence and shared history between Ethan and Claire
**Location:** Apartment Kitchen
**Time:** Early morning, golden hour
**Characters:** Ethan, Claire
**Emotion:** Comfort
**Mood:** Warm, intimate, ordinary

#### Dialogue

**ETHAN**
*(pouring coffee)* "You know what I noticed?"

**CLAIRE**
*(without looking up from her sketchbook)* "What?"

**ETHAN**
"You still take your coffee with two sugars. Even after seven years."

**CLAIRE**
*(smiles, finally looks up)* "Don't start with the poetry thing."

**ETHAN**
"It's not poetry. It's data. I'm a counselor. This is what I do."

**CLAIRE**
"And what does the data say?"

**ETHAN**
"That you're going to burn the toast again."

*(beat: she looks at the toaster, it's smoking)*

**CLAIRE**
"Shit."

#### Action

*Claire rushes to the toaster. Ethan laughs — a real laugh, not the polite one he'll stop making months from now.*

#### Beat

*pause: 2s — They share a look. The kind that says "we've done this a thousand times before."*

#### Narration

> He was the kind of man who made love feel like conversation. Gentle. Exploratory. Full of questions he didn't know how to answer.
>
> For seven years, that's what he'd done.

#### Director Notes

- Close-up on Ethan's hands pouring coffee — warm practical lighting from kitchen window
- Shallow depth of field — Claire slightly out of focus in background
- Music: family_theme, intensity 0.3, fade_in 3s
- Ken Burns: very slow pan left to right, following Ethan's gaze toward Claire

---
```

## Screenplay vs Timeline Separation

| Document | Answers | Contains |
|----------|---------|----------|
| **Screenplay** | "What happens?" | Dialogue, narration, actions, emotional beats, pauses, silence, director notes |
| **Timeline** | "How do we produce it?" | Scene durations, shot language, music cues (theme reference only), voiceover references, visual generation params |

The timeline references the screenplay:
```yaml
scenes:
  - scene_number: 1
    title: Morning Ritual
    screenplay_reference: "#scene-1-morning-ritual"   # links to screenplay section
    duration_seconds: 45
    music:
      theme: family_theme
      intensity: 0.3
      fade_in: 3
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-07-09 | Initial specification — structured Markdown for AI production |
