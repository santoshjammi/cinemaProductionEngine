# Emotional Impact Engine — Operational Specification

> 4 sub-engines that drive all emotional-withdrawal videos. Loaded by
> `psychological_cinema_standard.yaml` v5.0+ and consumed by
> `psychological_pipeline.py`. Every other file in this directory must
> be consistent with this spec.

## Overview

```
emotional_impact_engine
├── irreversible_moment      # Rule 1: the wound
├── silence_engine           # Rule 4: the pause
├── voice_modulation_engine  # Rule 5 + audio: the drop
└── micro_tension_engine     # Rule 2 + Rule 8: the behavior
```

These four sub-engines are NOT independent. They lock together at one
specific moment in every video: the **trigger moment**. That is where
all four fire simultaneously — visual interruption, audio drop, voice
softening, behavior arrest — to create the irreversible moment.

---

## 1. irreversible_moment

**Mandatory: exactly one per video.** No more, no less. The pipeline
rejects manifests that mark zero or more than one scene with
`irreversible_moment: true`.

### Objective

- `emotional_memory_creation` — viewer remembers the moment days later
- `sensory_immersion` — viewer feels physically present in the room
- `psychological_shift` — viewer's emotional state is permanently altered by the moment

### Structure: 3-phase temporal model

The irreversible moment is NOT a single beat. It is a 3-phase sequence
spanning the moment scene and its immediate neighbors.

#### pre_moment (the scene immediately before the trigger scene)

| Layer | Spec |
|-------|------|
| `emotional_state` | `emotional_build_up`, `tension_accumulation`, `restrained_distance` |
| `audio` | `low_ambient_support` (the beat's ambient SFX at full volume), `subtle_room_tone`, `restrained_music` (act music at 0.6× normal) |
| `narration.style` | `observational`, `reflective`, `emotionally_restrained` |
| `scene_flag` | (none — the scene before the irreversible moment is just an ordinary scene building tension) |

#### trigger_moment (the scene marked `irreversible_moment: true`)

| Layer | Spec |
|-------|------|
| `emotional_state` | `interruption`, `hesitation`, `emotional_risk`, `internal_conflict` |
| `visual_behavior` | `unfinished_gesture`, `hand_withdrawal`, `eye_contact_break`, `interrupted_touch`, `redirected_attention` |
| `audio_transition` | **remove**: music, emotional padding. **amplify**: breathing, cloth_movement, room_tone, silence |
| `narration_transition` | `softer_delivery`, `breath_fragility`, `longer_pauses`, `emotional_fracture` |
| `tts_prosody_override` | `rate=-30% volume=-20% pitch=-12Hz` (vs default -15/-10/-5) |
| `music_volume` | 0.0 (silence, no music) |
| `ambient_volume` | 1.0 of beat profile (full volume, was the only sound) |
| `silence_after` | 3.0s (room tone only, no music) |
| `voiceover_max_words` | 12 (or `silence_instead: true` for pure silence) |
| `shot_preset` | `irreversible_moment` (extreme close-up, dramatic side-light) |
| `ken_burns` | `ken-burns` with negative amplitude (slow drift backward) |

#### post_moment (the scene immediately after the trigger scene)

| Layer | Spec |
|-------|------|
| `emotional_state` | `unresolved_ache`, `quiet_devastation`, `emotional_aftershock` |
| `audio` | `delayed_ambient_return` (the next scene's ambient enters at 50% then rises to 100% over 2s), `fragile_soundscape`, `lingering_silence` |
| `narration.style` | `minimal`, `emotionally_exhausted`, `unresolved` |
| `silence_before` | 2.0s (the lingering silence from the trigger moment continues into this scene before any narration) |
| `music_volume` | 0.5× normal (music re-enters, but quieter than before) |

### Validation (pipeline enforces all of these)

- Exactly 1 scene with `irreversible_moment: true`
- That scene's voiceover ≤12 words OR `silence_instead: true`
- That scene's `music_volume` overrides to 0.0
- That scene's TTS uses the dramatic prosody override
- The previous scene is `pre_moment: true` (or unflagged; pipeline auto-marks it)
- The next scene is `post_moment: true` (or unflagged; pipeline auto-marks it)
- The next scene has `silence_before` ≥1.5s

---

## 2. silence_engine

**Philosophy:** silence is storytelling. Emotional weight requires space.
Silence creates anticipation.

### Rules

1. **Use silence before emotional truths.** Mark `silence_before: 2.0` on
   any scene that begins with an emotional truth statement.
2. **Use silence after emotional interruption.** Mark `silence_after: 3.0`
   on the irreversible moment scene (this is mandatory, see trigger_moment).
3. **Never continuously fill emotional space.** At least 2 scenes per video
   must have either `silence_before` OR `silence_after` ≥1.5s.
4. **Silence should feel intentional.** Silence is room tone at the beat's
   ambient profile, no music, no narration. Not literal silence — the room
   is still heard. The viewer feels the absence of meaning-making.

### Implementation (pipeline behavior)

```yaml
# In scene manifest:
silence_before: 2.0    # seconds of room tone before narration starts
silence_after: 3.0     # seconds of room tone after narration ends
silence_instead: true  # this scene has NO narration, only ambient
```

When `silence_instead: true`:
- The scene plays only with ambient SFX at full profile volume
- No music
- No TTS
- The Ken Burns clip length is determined by the scene's `duration_hint`
  in the manifest (default 8s if unset)

When `silence_before` or `silence_after` is set:
- That many seconds of room tone are prepended or appended to the scene's audio
- The video clip is extended by the same amount
- Music in those silence gaps is muted
- Narration in those gaps is absent

### Audio mix for silence gaps

```
[silence_gap] =
  ambient_track.volume * 1.0
  + room_tone.volume * 0.5
  + music.volume = 0.0
  + narration.volume = 0.0
```

---

## 3. voice_modulation_engine

**Progression (default through the video):**
`observational` → `vulnerable` → `fractured` → `emotionally_exhausted`

The voice should follow the energy arc, but the **irreversible moment
scene breaks the progression** with an instant drop into a softer, more
breath-led register.

### Modulation rules

1. **Voice should soften during emotional exposure.** Pitch drops, volume
   drops, rate slows as the scene approaches emotional truth.
2. **Breathing should remain audible during fragile moments.** The
   `breathing` layer in the beat's ambient SFX is at full volume on
   fragile scenes (mark `voice_fragile: true` in scene manifest).
3. **Pauses should emotionally land before narration continues.** The TTS
   `<break time="500ms"/>` SSML tag is inserted at emotional pivot points
   in the voiceover.

### Prosody table (default + overrides)

| Scene type | rate | volume | pitch | breathing layer |
|------------|------|--------|-------|-----------------|
| Default (Act 1, Act 2 first half) | -15% | -10% | -5Hz | -6dB |
| Vulnerable (Act 2 second half) | -20% | -12% | -7Hz | -3dB |
| Fractured (Act 3) | -22% | -15% | -8Hz | 0dB (audible) |
| **Irreversible moment** | **-30%** | **-20%** | **-12Hz** | **+3dB (breath-forward)** |

### Voice transition into the irreversible moment

The scene BEFORE the irreversible moment uses the default prosody.
The irreversible moment scene uses the dramatic override.
The scene AFTER returns to the act-appropriate prosody (`fractured` for Act 3,
`vulnerable` for Act 2).

This sudden prosody drop on a single scene is what makes the moment stand
out without the viewer knowing why.

---

## 4. micro_tension_engine

**Philosophy:** emotion is interrupted, not displayed. The strongest
emotions leak through behaviors that the character doesn't intend.

### Required behaviors (rotate through scenes)

- `unfinished_movements` — hand starts, stops, returns
- `hesitation` — body language catches itself
- `redirected_attention` — looking away too quickly
- `almost_touching` — two inches of air between hands
- `almost_speaking` — lips part, then close
- `emotional_withdrawal` — body folds inward, makes itself smaller

### Avoid

- `direct_emotional_display` — tears, dramatic expressions
- `melodrama` — heightened, performed emotion
- `emotional_overacting` — faces doing the work the moment should

### Implementation in scene descriptions

Every `scene_description` field MUST include at least one of the required
behaviors, expressed as a concrete physical action. Not as an adjective.

**Bad:** "She looks sad."
**Good:** "She reaches across the table, stops, pulls her hand back, and
stares at the mug as if it just said something."

**Bad:** "He is exhausted."
**Good:** "He picks up his phone, sets it down, picks it up again, then
leans his head against the wall and doesn't move for a long time."

The LLM prompt explicitly forbids direct emotional adjectives and requires
physical-behavioral descriptions. The pipeline's `extract_micro_behavior`
function in the prompt builder parses the scene_description and asserts
that at least one of the 6 required behaviors is present. If none is
detected, the scene is regenerated.

---

## How the 4 sub-engines lock together

```
                    NORMAL SCENE                      IRREVERSIBLE SCENE                  NORMAL SCENE
                    ────────────                      ──────────────────                  ────────────
silence_engine      silence_after=0                   silence_after=3.0                   silence_before=2.0
voice_modulation    default (-15/-10/-5)              OVERRIDE (-30/-20/-12)              post-progression (-22/-15/-8)
micro_tension       1 micro-behavior                  THE interruption itself              2+ micro-behaviors (aftershock)
irreversible_moment (none)                            TRIGGER FIRES                       (none)
```

All four engines change at the same scene boundary. That synchronization
is what makes the moment feel "different" without the viewer being able
to name why.

---

## Pipeline integration contract

The `psychological_pipeline.py` reads these flags from each scene in the
manifest:

```yaml
- scene_number: 7
  title: "Unspoken Truth"
  beat: internal_collapse
  irreversible_moment: true           # Rule 1, irreversible_moment
  pre_moment: false                   # pipeline auto-marks scene before
  post_moment: false                  # pipeline auto-marks scene after
  silence_after: 3.0                  # silence_engine
  silence_before: 0.0
  silence_instead: true               # silence_engine (this scene has no VO)
  voice_fragile: true                 # voice_modulation_engine
  tts_prosody_override:               # voice_modulation_engine
    rate: "-30%"
    volume: "-20%"
    pitch: "-12Hz"
  music_volume_override: 0.0          # audio: no music on this scene
  shot_language:
    preset: irreversible_moment       # STYLE_GUIDE.yaml
  scene_description: >                # micro_tension_engine (parsed)
    He starts to say something, catches himself, picks up his phone instead.
    She noticed him start. She picks up her coffee with both hands and
    doesn't look up. The unwashed mug he left by the sink is still there.
    A sock on the hallway floor neither of them picked up. Quiet.
```

The pipeline asserts:
1. Exactly one `irreversible_moment: true` scene exists
2. `pre_moment` and `post_moment` flags are set on the surrounding scenes
3. The scene before is in Act 2 (the almost phase)
4. The voiceover is ≤12 words OR `silence_instead: true`
5. `tts_prosody_override` is set with all 3 fields
6. `music_volume_override: 0.0` is set

If any assertion fails, the pipeline refuses to run and prints the exact violation.
