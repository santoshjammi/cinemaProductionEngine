# Scene Blueprint: `slow_withdrawal-08-setting-the-table` (irreversible_moment)

> **This is the canonical irreversible moment for the slow_withdrawal archetype.**
>
> Use it as a template for any slow_withdrawal video. Adapt the specific
> gesture to your story, but keep the emotional logic.

---

## The scene

**Emotional logic**: A small domestic gesture (a routine task) becomes frozen
mid-action. The protagonist is interrupted by an emotion they can't name.
The viewer sees the pause. They project the pain themselves.

**What the audience sees**: A woman in a kitchen, about to set the table. She
stops at the second fork. She picks it up, sets it down, picks it up again.
She does not finish setting the table. She leans on the counter with both
hands and doesn't move.

**What the audience feels**: "I have done this. I have been this person. I
know this pause."

**What is NOT shown**: The argument. The collapse. The whole relationship.
Just the freeze.

---

## The schema (conforms to `grammar/scene_blueprint_schema.yaml`)

```yaml
- id: <territory>-08-<slug>
  index: 8
  title: "Setting the Table"
  beat: irreversible_moment
  act: act_2_inner_reality
  phase: almost
  duration_seconds: 12.0
  energy: 5

  emotional_state:
    primary: restrained
    secondary: yearning
    subtext: "She does not know why she stopped. The viewer recognizes this pause — it has happened to them."

  visual_symbolism:
    symbols: ["second fork", "half-set table", "untouched glass of water", "cardigan half-off shoulder"]
    imperfection: ["messy hair", "cardigan slipping", "fridge hum"]
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
    silence_before_seconds: 0.0
    silence_after_seconds: 3.0
    silence_instead: false

  narration:
    text: "She stopped. The second fork... she didn't know why."
    prosody_register: irreversible_moment
    vocal_fracture: true
    breath_pre_pad_ms: 400
    break_words: [stopped]
    emphasis_words: [stopped, second, fork]
    # Pipeline applies rate=-30% vol=-20% pitch=-12Hz automatically

  subtitle_emphasis:
    emphasis_words: [stopped, second, fork]
    pause_after_words: [stopped]
    phrase_pacing: true
    max_words_per_caption: 5

  transition_type:
    in_transition: fade_black
    out_transition: cut
    silence_gap_seconds: 0.0

  render_hints:
    mode: img2img_from_hero
    hero_reference: characters/wife_hero.png
    negative_prompts: [candlelit_dinner, finished_meal, romantic_framing]
    micro_behaviors: [unfinished_movements, hesitation, emotional_withdrawal]
    environmental_imperfections: [kitchen_mess, fabric_wear, signs_of_life]

  irreversible_moment: true
  pre_moment: false
  post_moment: false
  shows_duality: false
```

---

## Why this works (the emotional logic)

The pause is **ordinary**. The viewer has done this exact gesture. They have
set a table, stopped mid-action, picked up a fork, set it down, picked it up
again. They have leaned on a counter and not moved.

The viewer projects their own pain onto this gesture. They don't need
narration to tell them what the woman is feeling. They feel it themselves.

That is **implication, not exposition**. The audience completes the
emotional meaning internally.

The pause is also **brief** (12 seconds). The video doesn't dwell. The next
scene moves on. The pain is felt, then life continues. That is how real
emotional collapse works — you pause, then you keep going.

---

## Variations on this scene

For different slow_withdrawal stories, adapt the gesture:

| Story | The pause | The frozen gesture |
|-------|----------|-------------------|
| Couple drifting apart | She is setting the table. | The second fork. |
| Long-distance relationship | She is folding his shirts. | The shirt that doesn't get folded. |
| Post-divorce grief | He is watering a plant. | The watering can that doesn't pour. |
| One partner sick | She is making his favorite meal. | The spice she can't remember. |
| Affair discovered | He is shaving. | The razor that stops mid-stroke. |

The **structure is constant**: a small domestic task, frozen mid-action. The
specifics adapt to the story.

---

## Pipeline requirements (asserted)

- This scene has `irreversible_moment: true`
- This scene has `prosody_register: irreversible_moment`
- This scene has `vocal_fracture: true` (if voiceover exists)
- The previous scene has `pre_moment: true`
- The next scene has `post_moment: true`
- This scene has `silence_after_seconds ≥ 2.0`
- The voiceover is ≤12 words (or `silence_instead: true`)
- The next scene has `silence_before_seconds ≥ 1.5`

If any of these is violated, the pipeline refuses to render.

---

## File path

This blueprint lives at:

```
projects/EmotionalWithdrawal/scene_blueprints/slow_withdrawal-08-setting-the-table.yaml
```

(Currently as inline YAML; can be extracted to a separate YAML file if reused.)
