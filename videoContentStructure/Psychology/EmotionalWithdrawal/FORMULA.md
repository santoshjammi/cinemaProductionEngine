# Emotional Withdrawal — Production Formula v1.1

> Single source of truth for generating emotional-withdrawal videos.
> Every other file (`FEEDBACK_DIGEST.md`, `STYLE_GUIDE.yaml`, `PROMPT_LIBRARY.yaml`,
> `psychological_cinema_standard.yaml`) MUST be consistent with this document.
> When feedback changes, update THIS file first, then propagate.
>
> **v1.1 (2026-07-07)**: Added feedback 04 — micro-tension storytelling. 4 new rules.
> See "v1.1 ADDITIONS" at the bottom.

## The promise

The viewer should eventually feel:

> "I don't know why this affected me so much."

That is the real benchmark. Not views. Not likes. **Subconscious emotional
recognition.** That's what makes psychological cinema powerful.

---

## The 8 non-negotiable rules

Every video MUST satisfy these. They are the formula.

### Rule 1 — ONE emotionally irreversible moment

The video MUST contain exactly one moment that:
- Interrupts itself mid-action
- Reveals something both characters try to hide
- Cannot be unwitnessed once seen

**Visual signature:** a small, un-stageable, human action that is suddenly
withdrawn. The action itself is tiny; what it carries is enormous.

**Audio signature on this scene:**
- TTS prosody drops dramatically: rate `-30%` (default `-15%`), volume `-20%` (default `-10%`), pitch `-12Hz` (default `-5Hz`)
- The voiceover itself is short (≤12 words), often a single trailing thought
- The narration may be SILENT or near-silent — voiceover is OPTIONAL on this scene
- The scene plays out in amplified silence: room tone ONLY, no music

**Manifest flag:** `irreversible_moment: true` on exactly ONE scene.

**Visual prompt anchor (add to scene description):**
> "an interrupted action — the hand that almost reached, the sentence that
> almost began, the look that almost landed — the body catches itself and
> redirects, but the witness sees what almost happened"

**Examples of irreversible moments (for any video):**
- He almost reaches for her hand, pauses, withdraws. She notices, pretends not to.
- She starts to say something, stops, picks up her phone instead. He saw her start.
- He looks at her across the room, looks away before she can look back. She was about to look back.
- They both reach for the door handle at the same time, hands touch, both pull away.
- He almost cries, swallows it, adjusts his collar, walks out.

### Rule 2 — Behavioral realism, not sad posing

Replace emotional adjectives with **behaviors that leak the emotion**.

**Forbidden visual patterns (negative prompt additions):**
- "staring sadly at camera"
- "crying openly"
- "dramatic pose"
- "head in hands"
- "looking into the distance dramatically"
- "tear rolling down cheek in slow motion"
- "intense emotional expression"

**Required behaviors (inject into every scene):**
- Unfinished gestures (hand starts, stops, returns)
- Delayed responses (mid-action pause)
- Looking away too quickly
- Distracted routines (mechanical, automatic)
- Checking phone during vulnerability
- Fake-normal conversation
- The body doing one thing while the face does another

### Rule 3 — Environmental imperfection

Every frame MUST contain at least 2 of:
- wrinkled blankets / rumpled sheets
- dishes in sink / half-empty mug
- imperfect lighting (a flickering lamp, single bulb, dead corner)
- messy hallway / shoes kicked off
- partially open doors
- reflections in mirrors/windows
- film grain, slight blur, soft focus edge
- visible dust, fingerprints, water marks, worn surfaces

Spaces must feel **inhabited**, not staged.

### Rule 4 — Silence as storytelling

Silence is part of the soundtrack. Not supporting the video — IS the video.

**Three silence types (all configurable per scene):**

| Type | Description | Audio config |
|------|-------------|--------------|
| `silence_after` | 2s of pure room tone after this scene | no music, no narration, only beat ambient at half volume |
| `silence_before` | 2s of pure room tone before this scene | same |
| `silence_instead` | The scene has NO narration; ambient + room tone carry it | narration volume = 0, music volume = 0 |

**Manifest flags:** `silence_after: 2.0`, `silence_before: 2.0`, `silence_instead: true` (in seconds, on any scene).

**The irreversible moment scene is ALWAYS `silence_instead: true` plus `silence_after: 3.0`.**
The next scene gets `silence_before: 2.0`. The truth lands, then the next image.

### Rule 5 — Implication over explanation

Never close an emotion. Never explain what the visual already shows.

**Voiceover rules:**
- No "he felt..." / "she felt..." / "they were..."
- No cause-and-effect ("so he retreated because she...")
- No therapy language ("emotional safety", "attachment", "avoidant")
- No moral or lesson
- Use trailing implication: leave a phrase unfinished, let the visual complete the meaning

**Pattern (use this exact form):**
- Bad: "He no longer felt emotionally safe."
- Good: "Eventually… even small moments started feeling dangerous."

**Voiceover length:**
- Default: ≤25 words per scene
- Irreversible moment scene: ≤12 words OR zero (use `silence_instead: true`)

### Rule 6 — Emotional asymmetry / duality

The relationship MUST be a tragedy for BOTH characters.

**Required pattern:** at least one scene must show her loneliness AS HER OWN,
not as a reflection of his. She has her own grief, her own fear, her own
retreat. They are two lonely people in the same house.

**Manifest flag:** `shows_duality: true` on exactly one scene (typically the
penultimate or second-to-last scene in Act 3). The LLM prompt demands
"parallel emotional suffering" for this scene.

### Rule 7 — Sound proximity (the physical closeness rule)

The soundscape must feel **physically close**, not atmospheric.

**Required micro-sound elements (per scene, layered into ambient SFX):**
- breathing (always)
- cloth movement (bedroom scenes)
- finger taps, chair creak (interior scenes)
- distant rain, kitchen hum, footsteps (transition scenes)
- one of: phone buzz, glass set down, drawer close, door not-quite-closed (any interior scene)

These tiny sounds create emotional intimacy through proximity. Prestige
cinema does this constantly. We do it via `BEAT_PROFILES` in
`AmbientSFXGenerator` — every beat profile includes at least 3 layers.

**Volume rule:** ambient SFX is mixed at the scene's `ambient_volume`
(typically 0.20-0.32). It must be audible against the music, not buried
under it.

### Rule 8 — Almost moments are the signature

The strongest moments are not sad moments. They are **almost moments**:
- almost touching
- almost speaking honestly
- almost reconnecting
- almost vulnerable

Every video MUST contain at least one "almost moment" as the emotional
centerpiece. This is where tension lives — not in despair, in
**interruption**. The almost is stronger than the never.

The irreversible moment (Rule 1) is the strongest of these. It is the
single almost-moment that becomes permanent because it was witnessed.

---

## The structural formula

Every Emotional Withdrawal video follows this skeleton:

```
ACT 1 — Observation            "I know this feeling."
  1. hook         (1 scene)     Tense restraint, frozen gesture
  2. warmth       (2 scenes)    Something to lose. Golden hour only.
  3. normalcy     (1 scene)     Polite. Functional. Empty.

ACT 2 — Inner Reality          "I didn't realize this was underneath it."
  4. crack        (1 scene)     First visible fracture
  5. collapse     (2 scenes)    Deepening darkness
  6. almost       (1 scene)     IRREVERSIBLE MOMENT lives here (Rule 1)

ACT 3 — Psychological Truth    "That truth hurts."
  7. retreat      (1 scene)     Self-protection
  8. duality      (1 scene)     HER grief (Rule 6, shows_duality: true)
  9. climax       (1 scene)     Final truth, devastating
```

**Total: 11 scenes.** Target duration 4-7 minutes.

---

## The audio formula

### Music zones (3 distinct emotional territories)

| Zone | Scenes | Sound |
|------|--------|-------|
| Act 1 | 1-4 | Sparse ambient piano. Major 7ths, soft attack. Hope + warmth. |
| Act 2 | 5-7 | Dark drone. Dissonant tritones, low cello-like pads. Unease. |
| Act 3 | 8-11 | Near-silence. Single sustained note, fading. Room tone dominates. |

### Per-scene TTS prosody

Default voiceover prosody: `rate=-15%, volume=-10%, pitch=-5Hz` (Andrew).

**Override for irreversible moment scene:**
`rate=-30%, volume=-20%, pitch=-12Hz` (a quarter slower, much lower, much softer).

This single prosody change is what makes the irreversible moment stand out
without the viewer knowing why. The voice "drops" into a register the rest
of the video never uses.

### Silence engineering

The pipeline inserts silence gaps between scenes based on scene flags.
Silence = room tone (the beat's ambient SFX) at half volume, no music, no
narration. The viewer's nervous system fills the gap.

---

## The visual formula

### Three consistent anchors (always present)

1. **Cool blue undertones** — never warm overall, only warm from practical lights
2. **Shallow depth of field** with bokeh — never deep focus for intimate scenes
3. **35mm film grain** — never clean digital

### Shot presets (use these names in scene manifests)

- `intimate_close` — close-up, practical phone light, bokeh
- `quiet_medium` — medium, warm tungsten, moderate depth
- `isolation_portrait` — medium close, low-key, telephoto
- `numbness_wide` — medium, screen-lit, shallow
- `final_truth` — close-up, moonlight, devastating
- `warmth_memory` — medium, golden hour (ONLY for Act 1 contrast scenes)
- `almost_moment` — extreme close-up, moonlight (the almost-touching shot)
- **`irreversible_moment`** — NEW. Extreme close-up, dramatic side-light. The interrupted gesture.

### Negative prompt (extended, append to every scene)

```
cartoon, anime, illustration, painting, 3d render, cgi, video game,
blurry, low quality, distorted, deformed, disfigured, bad anatomy,
extra limbs, extra fingers, watermark, signature, text,
oversaturated, hdr, plastic skin, duplicate, cloned,
overlapping subjects, messy composition, chaotic,
multiple scenes, collage, split screen, bright daylight,
cheerful, stock photo, commercial photography,
staring sadly at camera, dramatic pose, head in hands,
crying openly, tear rolling down cheek in slow motion,
looking into the distance dramatically,
clean modern interior, staged photo, perfect lighting,
empty sterile room
```

### Ken Burns

Use only: `ken-burns`, `zoom-in`, `zoom-out`, `pan-right`, `pan-left`.

**For irreversible moment scene:** use `ken-burns` with **negative
amplitude** (slow drift backward, not forward) so the moment feels like
it's already receding.

---

## The character formula

### Two-character default (protagonist + partner)

Each character has 3-5 visual anchors used verbatim in every scene they
appear in. Hero images (`characters/<name>_hero.png`) are used for
img2img character consistency at strength 0.45.

### Emotional range (per character, repeatable)

The character's emotional state is shown by **which micro-behavior is
active**, not by facial expression. Same face, different hands, different
posture, different relationship to the space.

Examples for `protagonist`:
- `restraint`: hand frozen mid-reach, jaw clenched, held breath
- `shame`: head bowed, hunched, avoiding eye contact
- `numbness`: blank stare, slack jaw, mechanical movements
- `grief`: motionless, eyes open but unfocused
- `interrupted`: about to do X, catches self, does Y — THIS IS THE IRREVERSIBLE ONE

### Duality handling

The LLM is required to give the partner her own scenes (Rule 6). The
partner's emotional range is independent: her retreat, her exhaustion, her
grief, her almost-moment (different from his, equally weighted).

---

## The check before shipping

Before any video goes to production, verify:

- [ ] Exactly ONE scene has `irreversible_moment: true`
- [ ] That scene has TTS prosody override applied (rate=-30, volume=-20, pitch=-12)
- [ ] That scene is `silence_instead: true` OR has ≤12-word voiceover
- [ ] At least 1 scene has `silence_after` (≥2s)
- [ ] The 8th scene has `shows_duality: true`
- [ ] All scenes have ≥2 environmental imperfection elements in the description
- [ ] All scenes have ≥1 micro-behavior (unfinished gesture, delayed response, etc.)
- [ ] Voiceovers use trailing implication, no "he/she felt..."
- [ ] 3 music zones active (piano/drone/silence) across acts
- [ ] Per-scene ambient SFX applied (not generic room tone)
- [ ] Hero images used for character consistency (img2img)
- [ ] Total duration 4-7 minutes

---

## Versioning

| Version | Date | Change |
|---------|------|--------|
| 1.0 | Initial | First complete formula. 8 rules. Irreversible moment, silence, duality, behavioral realism, environmental imperfection, sound proximity, almost moments, implication. |
| 1.1 | 2026-07-07 | FEEDBACK 04: 4 refinements. Characters must be imperfect (tiredness, awkwardness, asymmetry). Emotional devastation must hide in ordinary gestures. Sound must be physically close (more micro-audio layers). Voice must fracture (unfinished cadence, breath hesitation, longer pauses). |

When you change this file, bump the version and update all dependent files
in the same commit. The order of update: this file → FEEDBACK_DIGEST.md →
STYLE_GUIDE.yaml → PROMPT_LIBRARY.yaml → standard YAML → pipeline code.

---

# v1.1 ADDITIONS — FEEDBACK 04: MICRO-TENSION STORYTELLING

> The expert confirmed v5.0 is on the right track. The remaining ceilings
> are subtle, not structural. The next level is **micro-tension storytelling**
> — interrupted vulnerability, almost connection, emotional hesitation,
> restrained devastation.

## Rule 9 — Characters must be imperfect, not composed

**Problem:** Characters still feel "aesthetically composed, emotionally
symbolic, visually curated." Perfection creates distance. Imperfection
creates humanity.

**Implementation:** Every character anchor must include at least 1 of:
- **tiredness** — slightly heavy eyes, mouth not quite smiling, posture
  not quite straight
- **awkwardness** — slightly off-center, slightly uncomfortable
- **distraction** — looking away, mid-thought elsewhere
- **behavioral inconsistency** — one gesture contradicts another
- **asymmetry** — hair not quite in place, one collar folded, sleeve half
  rolled up

**Forbidden visual patterns (negative prompt additions):**
- "perfectly styled hair", "flawless skin", "magazine cover pose"
- "idealized portrait", "studio lighting", "beauty shot"
- "attractive couple", "romantic framing", "candlelit dinner"
- "flawless composition"

## Rule 10 — Emotional devastation hides in ordinary gestures

**Problem:** Some shots still "announce" the emotional moment. The
audience needs to discover the pain themselves.

**Stronger approach:** Hide emotional weight in:
- making tea silently
- almost speaking, then stopping
- changing the subject mid-sentence
- interrupted routine (starting to load the dishwasher, then stopping)
- a small practical task (folding a shirt, putting down a glass)
- a delayed response (5 seconds too long)

The audience should feel "this is just life" while unconsciously
registering devastation.

## Rule 11 — Sound must create physical emotional proximity

**Problem:** Sound supports mood but doesn't yet create physical
intimacy. The irreversible moment needs MORE micro-audio layers.

**Implementation:** The `irreversible_moment` beat profile (in
`AmbientSFXGenerator.BEAT_PROFILES`) must include ALL of:
- breathing (louder, +3dB on this beat)
- cloth movement (gentle fabric sound)
- distant fan or HVAC hum
- chair creak or floorboard settle
- room hum (very low frequency presence)
- one of: soft footsteps, rain reflection, water dripping

**Volume:** this scene's ambient is mixed at the beat's `volume` (0.35
for irreversible_moment) — louder than the typical 0.20-0.28. The viewer
should feel physically inside the room, not listening from outside.

## Rule 12 — Voice must fracture on emotional moments

**Problem:** Voiceover sounds emotionally controlled. On the irreversible
moment, it should feel **emotionally unstable** — not dramatic, just
fragile.

**Implementation:** When the scene is marked `irreversible_moment: true`
AND has a non-empty voiceover (i.e. NOT `silence_instead`), the TTS
service applies:

1. **Breath pre-pad:** Prepend a `<break time="400ms"/>` SSML tag so
   the voice enters from silence, not from a clean word.
2. **SSML break tags:** Insert `<break time="300ms"/>` before any
   emotionally loaded word (a pre-curated list: "still", "almost",
   "dangerous", "tired", "grief", "afraid", "love", "lost", "alone").
3. **TTS prosody override:** rate=-30%, volume=-20%, pitch=-12Hz.
4. **Pre-pad audio:** A 200ms breath audio layer is mixed in before the
   TTS so the voice begins on an inhale, not on a word.

When the scene uses `silence_instead: true`, no TTS is generated —
the visual carries the moment. The above applies only when there IS
a voiceover.

## The "one unforgettable moment" focus

The expert's strategic advice:

> Stop thinking: "How do I make the whole video better?"
> Instead think: "How do I make ONE emotional moment unforgettable?"

When iterating on a video, the irreversible moment scene should get
**disproportionate attention** — the most refined description, the
deepest SFX, the most specific voice fracture. The other 10 scenes
can be good. The irreversible moment must be **unforgettable**.
