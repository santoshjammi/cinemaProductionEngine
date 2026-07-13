---
name: psychological-cinema
description: |
  Produce a psychological cinema video in the "Beneath The Silence" style.
  Use when the user wants to make a cinematic short (30-180s) that explores a
  single psychological territory (emotional withdrawal, imposter syndrome,
  loneliness, etc.) with photorealistic stills, slow narration, and an
  emotionally irreversible moment. Triggers: "make a psychological cinema
  video about X", "build me a Beneath The Silence short on Y", "produce a
  cinematic monologue about Z", "create an emotional documentary short on W".
---

# Psychological Cinema — Production System

> **This is the entry point for an AI coding agent. It teaches you how to use
> the videoGen system to produce a psychological cinema video.**

The videoGen system produces short cinematic videos (30-180s) that explore a
single psychological territory. The aesthetic is **cinematic photorealism
with low-light intimacy** — like a prestige short film. The narrator is a
single voice (Andrew). The emotional logic is **implication, not exposition**.

This skill teaches you the 4-stage workflow: **territory → archetype →
scene_blueprints → render**.

## How It Works

1. **Pick a psychological territory** (e.g. emotional_withdrawal).
2. **Pick an archetype** that matches the territory (e.g. slow_withdrawal).
3. **Generate 11 scene blueprints** following the 3-act, 9-phase grid.
4. **Render** using the videoGen pipeline (M1 Max SDXL, local).

The output is a `final.mp4` video (1024×576, h264+AAC) with:
- Photorealistic still images animated with Ken Burns motion
- Andrew narration with per-scene prosody
- 3-zone music (piano/drone/silence)
- Per-scene ambient SFX (breath, cloth, chair creak, room hum)
- Exactly one **irreversible moment** (the emotional wound)
- Subtitles (cinematic bold, phrase-paced, gold emphasis)

## The 4-stage workflow

### Stage 1 — Territory

A territory is a psychological niche. The current territories are:

| Territory | Core emotions | Audience response |
|-----------|--------------|-------------------|
| `EmotionalWithdrawal` | loneliness, fear, shame, exhaustion, withdrawal | "I know this feeling." |
| `ImposterSyndrome` | performance anxiety, hidden shame, defensive confidence | "I didn't realize this was underneath it." |
| `Loneliness` | isolation, distance, longing, resignation | "That truth hurts." |
| `Rejection` | silent rejection, unrequited love, being unseen | "I know this feeling." |
| `Intimacy` | fear of closeness, vulnerability, defensive love | "I didn't realize this was underneath it." |

**Files**:
- `projects/<Territory>/CONTEXT.md` — niche context
- `projects/<Territory>/FEEDBACK_DIGEST.md` — feedback rules
- `projects/<Territory>/STYLE_GUIDE.yaml` — visual style
- `projects/<Territory>/PROMPT_LIBRARY.yaml` — reusable fragments
- `projects/<Territory>/characters/` — hero images
- `projects/<Territory>/VID##_template.yaml` — video manifest template

### Stage 2 — Archetype

An archetype is a **reusable emotional logic**. It tells you:
- The pacing curve (energy vs scene)
- The core beats
- The visual motifs
- The sound motifs
- The irreversible moment seed
- The narration cadence

The 7 archetypes (in `grammar/archetypes/library.yaml`):
- `slow_withdrawal` — "He stopped reaching before she noticed."
- `emotional_shutdown` — "She stopped feeling before he asked."
- `silent_rejection` — "She never said no. She just stopped being there."
- `masked_shame` — "He's performing confidence. He believes none of it."
- `internal_collapse` — "The outside looks normal. The inside is a collapse."
- `suppressed_desire` — "He wants to say it. He doesn't."
- `fear_of_vulnerability` — "Every time he gets close, he pulls back."

### Stage 3 — Scene Blueprints

Every video has **exactly 11 scenes** following the canonical 3-act grid:

| # | Beat | Act | Energy | Purpose |
|---|------|-----|--------|---------|
| 1 | `opening_hook` | 1 | 3 | Frozen moment of withdrawal |
| 2 | `contrast_memory` | 1 | 7 | Warmth / memory / something to lose |
| 3 | `contrast_memory` | 1 | 7 | Warmth / memory / something to lose |
| 4 | `outside_version` | 1 | 4 | The polite, functional outside |
| 5 | `first_fracture` | 2 | 3 | The first visible crack |
| 6 | `internal_collapse` | 2 | 2 | The psychological truth |
| 7 | `internal_collapse` | 2 | 2 | The psychological truth (deep) |
| **8** | **`irreversible_moment`** | 2 | **5** | **THE WOUND** |
| 9 | `defensive_retreat` | 3 | 2 | Self-protection |
| 10 | `her_truth` | 3 | 3 | Her grief, her own |
| 11 | `final_truth` | 3 | 1 | The devastating final line |

Each scene has a **schema** (see `grammar/scene_blueprint_schema.yaml`):
`id`, `index`, `title`, `beat`, `act`, `phase`, `duration_seconds`, `energy`,
`emotional_state`, `visual_symbolism`, `camera_language`, `soundtrack_zone`,
`narration`, `subtitle_emphasis`, `transition_type`, `render_hints`.

### Stage 4 — Render

Run the pipeline:

```bash
python scripts/psychological_pipeline.py \
  --playbook projects/<Territory>/psychological_cinema_standard.yaml \
  --manifest projects/<Territory>/VID##_template.yaml \
  --topic-dir projects/<Territory> \
  --output-dir output/videos \
  --auto-approve
```

The pipeline will:
1. **Apply the emotional_impact_engine** (irreversible_moment + silence + voice_modulation + micro_tension)
2. **Validate** the manifest (exactly 1 irreversible_moment, etc.)
3. **Generate images** with SDXL (1024×576, photorealism anchor preserved)
4. **Generate TTS** with Andrew voice + per-scene prosody + vocal_fracture on the irreversible moment
5. **Generate music** (3 zones: piano/drone/silence)
6. **Generate ambient SFX** (per-beat profiles, 5 layers on irreversible_moment)
7. **Mix audio** (narration + music + ambient with silence gaps)
8. **Animate** with Ken Burns
9. **Assemble** the final video

Output: `output/videos/<pipeline_id>/final.mp4`

## How to use this skill

### Create a new video in an existing territory

1. **Copy a template**:
   ```bash
   cp projects/EmotionalWithdrawal/VID01_template.yaml \
      projects/EmotionalWithdrawal/VID02_template.yaml
   ```

2. **Edit**:
   - `story_file`: point to your new story
   - `scenes[]`: write 11 scenes following the schema
   - Mark exactly 1 scene as `irreversible_moment: true`
   - Mark exactly 1 scene as `shows_duality: true`

3. **Add heroes** to `projects/<Territory>/characters/` (one per character)

4. **Run**:
   ```bash
   python scripts/psychological_pipeline.py \
     --playbook projects/EmotionalWithdrawal/psychological_cinema_standard.yaml \
     --manifest projects/EmotionalWithdrawal/VID02_template.yaml \
     --auto-approve
   ```

5. **Review** the output video. Iterate on the scene descriptions or voiceover.

### Create a new territory

1. **Create the folder**:
   ```bash
   mkdir projects/<NewTerritory>
   ```

2. **Add context files**:
   - `CONTEXT.md` — niche context, audience
   - `FEEDBACK_DIGEST.md` — rules (use the EmotionalWithdrawal one as a template)
   - `STYLE_GUIDE.yaml` — visual system
   - `PROMPT_LIBRARY.yaml` — reusable fragments
   - `psychological_cinema_standard.yaml` — production standard

3. **Add character heroes** to `characters/<char>_hero.png`

4. **Add your first video** following the template

5. **Run the pipeline**

## Production grammar (the rules)

These rules are **non-negotiable**. The pipeline enforces them.

### From the canonical video spec (`grammar/canonical_video_spec.yaml`)

- 11 scenes, 3 acts, 4-7 minutes target duration
- Energy descends from 7 (warmth) to 1 (climax)
- Exactly 1 `irreversible_moment` scene (typically scene 8)
- Exactly 1 `shows_duality` scene (typically scene 10)
- At least 2 scenes use `silence_before` or `silence_after` ≥ 1.5s
- Voiceover ≤25 words per scene, ≤12 for the irreversible moment
- The irreversible moment scene has `silence_instead: true` OR voiceover ≤12 words
- The irreversible moment scene has `prosody_register: irreversible_moment`
- The irreversible moment scene has `vocal_fracture: true`

### From feedback 01 (lived-in, not staged)

- Every scene has ≥2 environmental imperfections in the description
- Every scene has ≥1 micro-behavior (unfinished gesture, hesitation, etc.)
- Visual implication, not exposition
- No "staring sadly at camera" or "crying openly"

### From feedback 02 (micro-tension)

- Replace emotional adjectives with behaviors that leak the emotion
- Hide devastation in ordinary gestures (making tea silently, almost speaking)
- Sound must feel physically close (breathing, cloth, chair creak)
- Voice must fracture on the irreversible moment

### From feedback 03 (one unforgettable moment)

- ONE emotionally irreversible moment per video
- The voice drops into a register the rest of the video never uses
- The pre_moment scene is in Act 2, builds tension
- The post_moment scene continues in Act 2 or 3
- 3 seconds of silence after the irreversible moment

## The 4-sub-engine emotional_impact_engine

This is the secret sauce. Every video goes through it:

1. **irreversible_moment** — exactly 1 scene, 3-phase structure (pre/trigger/post)
2. **silence_engine** — silence_before/after/instead per scene
3. **voice_modulation_engine** — prosody progression: default → vulnerable → fractured → emotionally_exhausted → irreversible_moment
4. **micro_tension_engine** — 6 required behaviors, no direct emotional display

The pipeline applies all 4 automatically when you mark the right flags in your
scene blueprints.

## Render architecture

The videoGen system uses an **abstraction layer** (`grammar/render_abstraction.md`):

- `SceneIntent` — semantic description of a scene
- `SceneAsset` — rendered output
- `RenderBackend` — interface every provider must implement
- `RenderOrchestrator` — picks the best backend, falls back if needed

The current default is `SDXLLocalBackend` (free, M1 Max). Future backends
(Flux, OpenAI, StockFootage) plug in by implementing the same interface.

## Files to read first

If you want to deeply understand the system, read in this order:

1. `grammar/canonical_video_spec.yaml` — the contract
2. `grammar/scene_blueprint_schema.yaml` — the scene structure
3. `grammar/archetypes/library.yaml` — the 7 emotional logics
4. `grammar/visual_grammar.yaml` — semantic directing, not prompting
5. `grammar/render_abstraction.md` — provider-agnostic rendering
6. `projects/EmotionalWithdrawal/FORMULA.md` — production philosophy
7. `projects/EmotionalWithdrawal/FEEDBACK_DIGEST.md` — feedback rules

## Quick start

```bash
# 1. Make sure you have the model + LMStudio
ls ~/.cache/huggingface/hub/models--stabilityai--stable-diffusion-xl-base-1.0/
open -a "LM Studio"

# 2. Use an existing template
python scripts/psychological_pipeline.py \
  --playbook videoContentStructure/Psychology/psychological_cinema_standard.yaml \
  --manifest videoContentStructure/Psychology/EmotionalWithdrawal/VID01_template_refined.yaml \
  --topic-dir videoContentStructure/Psychology/EmotionalWithdrawal \
  --output-dir output/videos \
  --auto-approve --skip-narrative

# 3. Watch the output
open output/videos/vid01_template_refined/final.mp4
```

## OpenMontage integration

videoGen is the **render backend** for OpenMontage's cinematic pipeline. The
adapter in `openmontage_adapter/` translates OpenMontage scene descriptions
to videoGen SceneIntents.

If you're using OpenMontage as the orchestrator, your scenes are described in
OpenMontage's format. The adapter handles the translation.

## Versioning

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-07 | Initial skill. Documents the canonical video spec, 7 archetypes, render abstraction. |
