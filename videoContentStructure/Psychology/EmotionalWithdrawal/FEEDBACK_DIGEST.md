# Feedback Digest — Rules Applied to Every Video

Synthesized from feedback01.md and expert_feedback.md. These rules are
non-negotiable for every video in the Emotional Withdrawal universe.

## Rule 1: Emotional Contrast Before Collapse

**Problem**: Without contrast, heaviness becomes wallpaper. Viewers
emotionally adapt and retention drops mid-video.

**Rule**: Insert a warmth/memory/tenderness scene BEFORE the emotional
collapse. Even 12 seconds of contrast changes everything.

**Implementation**: Scene 2 (or early) must contain:
- An old memory
- Laughter
- Playful intimacy
- Her falling asleep on his shoulder
- Small domestic warmth

**Why**: Now the audience mourns something. Without contrast, there is
nothing emotionally lost. Only sadness. Sadness after warmth becomes
heartbreak. Sadness without contrast becomes texture.

## Rule 2: Recognition Over Analysis

**Problem**: Narration occasionally sounds like psychology commentary.
It sounds "authored" not "internally discovered."

**Rule**: Narration should sound like someone thinking inside the
experience — lived, painful, human. Not analytical or clinical.

**Pattern to avoid** (explanatory):
> "Maybe he started to feel unwanted."

**Pattern to use** (cinematic recognition):
> "After a while, he stopped knowing whether she still desired him… or
> was simply used to him being there."

**Key shift**: Less "analysis." More "recognition." Create ambiguity, ache,
humanity. Avoid sentences that could appear in a therapy textbook.

## Rule 3: Avoid Monotonous Suffering

**Problem**: Endless sadness, melancholy, withdrawal causes emotional fatigue.

**Rule**: The universe needs:
- Emotional nuance
- Relational complexity
- Uncomfortable duality

**Implementation**: Show that SHE is also exhausted, also feels rejected,
also stopped feeling emotionally safe. This complexity elevates from "sad
male content" to "human psychological storytelling."

## Rule 4: Almost Moments Are the Core

**Problem**: The sad moments are not the strongest moments.

**Rule**: The strongest moments are **almost moments**:
- almost touching
- almost speaking honestly
- almost reconnecting
- almost vulnerable

**Implementation**: Every video must contain at least one "almost moment"
that is the emotional centerpiece. This is where tension lives — not in
despair, but in interruption.

## Rule 5: Duration Discipline

**Rule**: Keep videos 4-7 minutes initially.

**Why**:
- Still discovering pacing, narration rhythm, visual repetition tolerance
- Shorter forces precision
- Precision creates rewatchability
- Rewatchability builds audience faster than duration

## Rule 6: Nuance Is the Moat

**Rule**: Protect nuance aggressively.

**Why**: The competitive advantage is not sadness, not masculinity, not
relationships. It is nuance. This gives:
- Longevity
- Emotional credibility
- Audience trust
- Higher-quality community

## Rule 7: Visuals Must Feel Lived-In, Not Generated (from expert_feedback)

**Problem**: AI visuals feel illustrative, symbolic, constructed — not
lived-in, observational, cinematic. That creates emotional distance.

**Rule**: Every frame must have:
- Environmental detail (wrinkled sheets, dust, condensation, mess)
- Physical imperfection (not staged, not perfect)
- Camera psychology (accidentally observed, not intentionally constructed)

**Fix**: Add environmental details to prompts. Add handheld micro-movement
to Ken Burns effects. Make scenes feel accidentally witnessed.

## Rule 8: Implication Over Explanation (from expert_feedback)

**Problem**: Visuals directly illustrate the narration. That reduces
audience participation.

**Rule**: Show IMPLICATION, not EXPLANATION. Cinema becomes powerful when
viewers emotionally complete the meaning themselves.

**Examples**:
- Instead of "sad man" → show "empty chair, coffee gone cold"
- Instead of "couple fighting" → show "two toothbrushes, one moved away"
- Instead of "he stopped reaching" → show "his hand on his own knee"

## Rule 9: Sound Must Become the Emotional Nervous System (from expert_feedback)

**Problem**: Sound is just supporting the video. It must become the
emotional nervous system.

**Rule**: Each scene needs per-scene ambient SFX:
- Bedroom: fan hum, breathing, bedsheet movement
- Kitchen: ambience, cutlery, distant traffic
- Car: engine hum, rain on windshield
- Rain scene: rain against window, uneven breathing

**Why**: These tiny sounds create emotional proximity. The viewer should
feel physically inside the scene.

## Rule 10: Let Silence Speak (from expert_feedback)

**Rule**: Silence is part of the soundtrack. Let 2-3 seconds of pure
silence exist between some scenes. Let the truth land before the next
scene begins.

---

## FEEDBACK 03 — Unforgettable Cinema (expert_feedback_03.md)

The next 8 rules elevate the work from "emotionally beautiful" to
"emotionally unforgettable." These are the new non-negotiables. The
full operational spec lives in `emotional_impact_engine.md` and
`FORMULA.md`.

## Rule 11: The Irreversible Moment (most important)

**Problem**: A video can be emotionally beautiful and still lack a wound.
A moment that permanently changes the emotional state.

**Rule**: Exactly ONE scene per video must be marked
`irreversible_moment: true`. This scene is structured in 3 phases:

- **pre_moment** (scene before): emotional build-up, restrained music
- **trigger_moment** (the scene itself): interruption, unfinished gesture,
  hand withdrawal, eye contact break, interrupted touch, redirected attention
- **post_moment** (scene after): unresolved ache, lingering silence

**Audio on the trigger scene**:
- TTS prosody override: `rate=-30%, volume=-20%, pitch=-12Hz` (vs default
  -15/-10/-5). The voice drops into a register the rest of the video
  never uses.
- Music volume: 0.0 (silence)
- Ambient: full volume, room tone only
- Voiceover: ≤12 words, OR `silence_instead: true`

**Visual signature**: the body does one thing, then catches itself and
redirects. The witness sees what almost happened. The tiny action
carries shame, fear, distance, history, longing, exhaustion WITHOUT
exposition.

## Rule 12: Behavioral Realism, Not Sad Posing

**Rule**: Replace emotional adjectives with behaviors that leak the
emotion. Every scene must contain ≥1 of:
- `unfinished_movements` (hand starts, stops, returns)
- `hesitation` (body language catches itself)
- `redirected_attention` (looking away too quickly)
- `almost_touching` (two inches of air between hands)
- `almost_speaking` (lips part, then close)
- `emotional_withdrawal` (body folds inward)

**Forbidden visual patterns** (negative prompt):
- "staring sadly at camera", "crying openly", "dramatic pose",
  "head in hands", "looking into the distance dramatically",
  "tear rolling down cheek in slow motion", "intense emotional expression"

## Rule 13: Environmental Imperfection

**Rule**: Every frame must contain ≥2 of:
- wrinkled blankets / rumpled sheets
- dishes in sink / half-empty mug
- imperfect lighting (flickering lamp, single bulb, dead corner)
- messy hallway / shoes kicked off
- partially open doors
- reflections in mirrors/windows
- film grain, slight blur, soft focus edge
- visible dust, fingerprints, water marks, worn surfaces

Spaces must feel **inhabited**, not staged.

## Rule 14: Silence as Storytelling (the silence_engine)

**Rule**: Three silence types, all configurable per scene:
- `silence_after: <seconds>` — N seconds of room tone after this scene
- `silence_before: <seconds>` — N seconds of room tone before this scene
- `silence_instead: true` — this scene has NO narration, only ambient + room tone

**Implementation**:
- The irreversible moment scene (Rule 11) is ALWAYS `silence_instead: true`
  plus `silence_after: 3.0`
- The next scene gets `silence_before: 2.0`
- At least 2 scenes per video must have `silence_before` OR `silence_after` ≥1.5s
- Silence = room tone (the beat's ambient SFX) at full volume, no music,
  no narration
- The viewer's nervous system fills the gap

## Rule 15: Voice Modulation (the voice_modulation_engine)

**Rule**: The voice must progress `observational → vulnerable →
fractured → emotionally_exhausted` through the energy arc. The
irreversible moment breaks the progression with a sudden drop.

**Prosody table**:

| Scene type | rate | volume | pitch |
|------------|------|--------|-------|
| Default | -15% | -10% | -5Hz |
| Vulnerable | -20% | -12% | -7Hz |
| Fractured | -22% | -15% | -8Hz |
| **Irreversible** | **-30%** | **-20%** | **-12Hz** |

The breathing layer in the beat's ambient SFX rises to audible
(+3dB) on the irreversible moment scene, then fades.

## Rule 16: Implication Over Explanation (tightened)

**Rule**: Never close an emotion. Never explain what the visual already
shows. Use trailing implication.

**Pattern**:
- Bad: "He no longer felt emotionally safe."
- Good: "Eventually… even small moments started feeling dangerous."

**Voiceover max length**:
- Default scenes: ≤25 words
- Irreversible moment: ≤12 words OR `silence_instead: true`

## Rule 17: Emotional Asymmetry / Duality

**Rule**: The relationship MUST be a tragedy for BOTH characters. At
least one scene must show her loneliness as her own, not as a
reflection of his. Mark with `shows_duality: true` (typically the
penultimate or second-to-last scene in Act 3).

The LLM is required to give the partner her own scene with her own
grief, fear, and retreat. They are two lonely people in the same house.

## Rule 18: Sound Proximity (the micro_tension_engine)

**Rule**: The soundscape must feel **physically close**, not atmospheric.
Every beat's ambient SFX profile must include ≥3 layers from:
- breathing (always)
- cloth movement (bedroom)
- finger taps, chair creak (interior)
- distant rain, kitchen hum, footsteps (transitions)
- one of: phone buzz, glass set down, drawer close, door not-quite-closed

These tiny sounds create emotional intimacy through proximity. Prestige
cinema does this constantly. Volumes must be audible against the music,
not buried.

---

## FEEDBACK 04 — Micro-Tension Storytelling (expert_feedback_04.md)

The next 4 rules deepen the irreversible moment specifically. The expert
confirmed v5.0 landed the structural improvements (contrast, silence,
pacing, interruption). The remaining ceilings are subtle and live in
**micro-tension** — interrupted vulnerability, almost connection,
emotional hesitation, restrained devastation.

The full operational spec lives in `FORMULA.md` v1.1.

## Rule 19: Characters Must Be Imperfect (the realism ceiling)

**Problem**: Characters still feel "aesthetically composed, emotionally
symbolic, visually curated." Perfection creates distance. Imperfection
creates humanity.

**Rule**: Every character anchor must include at least 1 of:
- **tiredness** — slightly heavy eyes, mouth not quite smiling, posture
  not quite straight
- **awkwardness** — slightly off-center, slightly uncomfortable
- **distraction** — looking away, mid-thought elsewhere
- **behavioral inconsistency** — one gesture contradicts another
- **asymmetry** — hair not quite in place, one collar folded, sleeve
  half rolled up

**Forbidden visual patterns (negative prompt additions)**:
- "perfectly styled hair", "flawless skin", "magazine cover pose"
- "idealized portrait", "studio lighting", "beauty shot"
- "attractive couple", "romantic framing", "candlelit dinner"
- "flawless composition"

**Implementation**: The character `emotional_range` lists in
`STYLE_GUIDE.yaml` and per-video manifests must include
`unfinished`, `distracted`, `delayed`, `tired`, `asymmetric` registers
in addition to the existing `restraint`, `shame`, `numbness`, `grief`.

## Rule 20: Emotional Devastation Hides in Ordinary Gestures

**Problem**: Some shots still "announce" the emotional moment. Prestige
cinema hides devastation in ordinary gestures.

**Rule**: On the irreversible moment, the visual should look like
ordinary life. Hide emotional weight in:
- making tea silently
- almost speaking, then stopping mid-sentence
- changing the subject
- an interrupted routine (starting to load the dishwasher, then stopping)
- a small practical task (folding a shirt, putting down a glass)
- a delayed response (5 seconds too long)

The audience should feel "this is just life" while unconsciously
registering devastation. The pain must be **discovered**, not shown.

**Implementation**: The `irreversible_moment_anchors` in
`PROMPT_LIBRARY.yaml` were updated to include 4 mundane-gesture anchors
that DO NOT look like emotional moments on the surface.

## Rule 21: Sound Must Create Physical Emotional Proximity

**Problem**: Sound supports mood but doesn't yet create physical
intimacy. The irreversible moment needs MORE micro-audio layers.

**Rule**: The `irreversible_moment` beat profile must include ALL of:
- breathing (louder, +3dB on this beat)
- cloth movement (gentle fabric sound)
- distant fan or HVAC hum
- chair creak or floorboard settle
- room hum (very low frequency presence)
- one of: soft footsteps, rain reflection, water dripping

**Volume**: this scene's ambient is mixed at the beat's `volume` (0.35
for irreversible_moment) — louder than the typical 0.20-0.28. The
viewer should feel physically inside the room.

**Implementation**: The pipeline's
`AmbientSFXGenerator.BEAT_PROFILES["irreversible_moment"]` was
upgraded to include 5 layers (was 3). The mixer applies the beat
volume (0.35) directly.

## Rule 22: Voice Must Fracture on Emotional Moments

**Problem**: Voiceover sounds emotionally controlled. On the irreversible
moment, it should feel **emotionally unstable** — not dramatic, just
fragile.

**Rule**: When the scene is `irreversible_moment: true` AND has a
non-empty voiceover (i.e. NOT `silence_instead`), the TTS service
applies the `vocal_fracture` treatment:

1. **Breath pre-pad** — prepend `<break time="400ms"/>` so the voice
   enters from silence, not from a clean word.
2. **SSML break tags** — insert `<break time="300ms"/>` before any
   emotionally loaded word (curated list: "still", "almost",
   "dangerous", "tired", "grief", "afraid", "love", "lost", "alone",
   "home", "safe").
3. **TTS prosody override** — rate=-30%, volume=-20%, pitch=-12Hz.
4. **Breath audio pre-pad** — a 200ms breath layer is mixed in before
   the TTS so the voice begins on an inhale.

When the scene uses `silence_instead: true`, no TTS is generated —
the visual carries the moment. The above applies only when there IS
a voiceover.

## Checklist for Every Video Manifest

Before generating a video, verify the manifest includes:

- [ ] At least one warmth/memory scene before the collapse
- [ ] Narration uses "recognition" voice, not "analysis" voice
- [ ] Shows duality (both partners' emotional experience)
- [ ] Contains at least one "almost moment" as the centerpiece
- [ ] Total duration targets 4-7 minutes
- [ ] Visual motifs: distance in shared spaces, low light isolation
- [ ] No villainization of either partner
- [ ] Emotional modulation (intensity rises AND falls)
- [ ] Scene descriptions show IMPLICATION not explanation
- [ ] Environmental detail in every scene (lived-in, not staged)
- [ ] Per-scene ambient SFX (not just generic room tone)
- [ ] Handheld micro-movement in Ken Burns effects
- [ ] Silence between scenes — let truths land
- [ ] **EXACTLY ONE** scene marked `irreversible_moment: true`
- [ ] The irreversible moment scene has TTS prosody override applied
- [ ] The irreversible moment scene has `music_volume_override: 0.0`
- [ ] The irreversible moment scene has `silence_instead: true` OR voiceover ≤12 words
- [ ] At least 2 scenes have `silence_before` or `silence_after` ≥1.5s
- [ ] At least 1 scene marked `shows_duality: true`
- [ ] Every scene has ≥2 environmental imperfection elements in description
- [ ] Every scene has ≥1 micro-behavior (unfinished gesture, delayed response, etc.)
- [ ] Voiceovers use trailing implication, no "he/she felt..."
- [ ] **Character anchors include ≥1 imperfection** (tiredness, awkwardness, asymmetry, distraction, behavioral inconsistency)
- [ ] **The irreversible moment scene uses ≥1 ordinary-gesture anchor** (Rule 20)
- [ ] **The irreversible moment beat profile has ≥5 SFX layers** (Rule 21)