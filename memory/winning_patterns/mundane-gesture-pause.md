# Winning Pattern: mundane-gesture-pause

> **Proven pattern from VID01 (v1.1.3). Use as template for future irreversible moments.**

## What this is

A specific type of irreversible moment where the protagonist is performing an
**ordinary domestic gesture** (making tea, setting a table, folding a shirt,
loading a dishwasher) and **freezes mid-action** for a reason they can't name.

The viewer projects their own pain onto this freeze. They recognize the
pause. They know what the protagonist is feeling without being told.

## Why it works

- **Universal recognition** — every viewer has done this. They've set a
  table, started to fold a shirt, picked up a glass — and stopped for no
  reason.
- **Discovered pain, not displayed pain** — the audience completes the
  emotional meaning themselves. They don't need narration to explain.
- **Short attention span friendly** — the gesture is small, the freeze is
  brief, life continues. The pain is felt, then the protagonist moves on.
  This is how real emotional collapse actually works.
- **No villain** — the pause is internal. There's no one to blame. The
  relationship itself is the tragedy.

## When to use

- **Slow withdrawal** archetype (primary)
- **Emotional shutdown** archetype (secondary)
- **Internal collapse** archetype (the freeze is the collapse)

## The schema (conforms to `grammar/scene_blueprint_schema.yaml`)

```yaml
- id: <territory>-08-<gesture-slug>
  index: 8
  title: "<Verb>-ing the <Noun>"   # e.g. "Setting the Table", "Folding the Shirt"
  beat: irreversible_moment
  act: act_2_inner_reality
  phase: almost
  duration_seconds: 12.0
  energy: 5

  emotional_state:
    primary: restrained
    secondary: yearning
    subtext: "<Protagonist> does not know why they stopped. The viewer recognizes this pause — it has happened to them."

  visual_symbolism:
    symbols:
      - "<the frozen object>"        # fork, shirt, glass, kettle
      - "<the domestic setting>"     # kitchen, bedroom, laundry room
      - "<an imperfection detail>"   # untouched glass, sock on floor, unwashed mug
      - "<a transition object>"      # door cracked, jacket on chair, phone face-down
    imperfection:
      - "<clothing slipping off>"
      - "<messy hair or bare feet>"
      - "<ambient sound (fridge hum, clock tick)>"
    what_is_NOT_shown: "The argument. The collapse. The whole relationship. Just the freeze."

  camera_language:
    shot_size: medium
    movement: static
    framing: rule_of_thirds
    depth_of_field: shallow
    lens_mm: 50
    lighting_key: natural

  soundtrack_zone:
    music_zone: silent
    music_volume: 0.0
    ambient_sfx_profile: irreversible_moment
    ambient_volume: 0.42
    silence_after_seconds: 3.0

  narration:
    text: "<≤12 words, present tense, the protagonist noticing the pause>"
    prosody_register: irreversible_moment
    vocal_fracture: true
    breath_pre_pad_ms: 400
    break_words: [<the loaded word — usually the verb of the gesture>]

  render_hints:
    mode: img2img_from_hero
    micro_behaviors: [unfinished_movements, hesitation, emotional_withdrawal]
    environmental_imperfections: [<3 categories from STYLE_GUIDE>]

  irreversible_moment: true
```

## Examples of gestures that work

| Gesture | Story context | Frozen object |
|---------|--------------|---------------|
| Setting the table | Couple drifting apart | The second fork |
| Folding a shirt | Long-distance relationship | The shirt that doesn't get folded |
| Watering a plant | Post-divorce grief | The watering can that doesn't pour |
| Making tea | Emotional shutdown | The kettle that doesn't get turned on |
| Loading dishwasher | Quiet resentment | The plate that gets put back instead of in |
| Pouring coffee | Resentment | The second cup that doesn't get poured |
| Setting an alarm | Depression | The clock that doesn't get set |
| Brushing teeth | Withdrawal | The brush that doesn't move |
| Tying shoes | Avoidance | The lace that doesn't get tied |
| Putting on a coat | Leaving | The door handle that doesn't get turned |

## What NOT to do

- Don't pick a gesture that requires explanation (don't show "arguing
  silently" — the audience has to see it, not infer it)
- Don't use a gesture that's already symbolic (don't freeze on a
  wedding ring or a family photo — those are "explaining")
- Don't show both characters in this scene — the moment is private. The
  other person is offscreen or in the background, out of focus
- Don't make the protagonist's face visible — this is about the
  gesture, not the facial expression

## How the pipeline renders this

1. The image is generated with `img2img_from_hero` (using the protagonist's hero image as reference)
2. The prompt is: "cinematic photorealism, 35mm film grain, [protagonist anchors], [the gesture mid-freeze], [the setting details], [the imperfection details]"
3. The narration is TTS'd with `vocal_fracture: true` (chunked TTS with silences around the loaded word)
4. The audio is mixed with 0 music, 0.42 ambient volume, 5 layers of breath-forward ambient SFX
5. The clip is rendered with Ken Burns (typically `ken-burns` with negative amplitude)
6. 3 seconds of pure ambient silence follows the clip

## Proven metrics (from VID01)

- **Scene duration**: 12.0s (the longest scene in the video)
- **CLIP score**: 0.65+ (good — the semantic directing is producing coherent results)
- **Mode**: img2img_from_hero (character consistency preserved)
- **Voiceover words**: 9-12 (within the ≤12 limit for irreversible moment)
- **Prosody register**: irreversible_moment (rate=-30% vol=-20% pitch=-12Hz)

## Reuse

This pattern has been used successfully in:
- VID01 — Scene 8 "Setting the Table" (woman, fork, kitchen)

Future videos in `emotional_withdrawal` territory should default to this
pattern for the irreversible moment scene. Adapt the specific gesture to
the story; keep the emotional logic.
