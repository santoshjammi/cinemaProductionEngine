# Imposter Syndrome — Territory

> **This is the canonical reference for the imposter_syndrome territory.**

## What this territory is

Cinematic psychological storytelling about **the gap between performed confidence and felt capability**.

The core theme:
> He's performing confidence. He believes none of it.

The strongest moments are not the public performances. They are the private cracks:
- the bathroom mirror rehearsal that doesn't work
- the parking lot pause before walking in
- the hand tremor no one sees
- the missed word in the middle of a confident sentence
- the collapse when nobody is watching

The audience response:
- **Act 1**: "I know this feeling." (the public self)
- **Act 2**: "I didn't realize this was underneath it." (the private self)
- **Act 3**: "That truth hurts." (the recognition)

## Core emotions

- performance anxiety
- hidden shame
- defensive confidence
- self-doubt
- fear of being seen
- the mask
- the cost of performing
- the relief when the mask slips

## Files in this territory

| File | Purpose |
|------|---------|
| `README.md` | This file |
| `CONTEXT.md` | Shared creative universe, audience definition, what this IS / IS NOT |
| `FEEDBACK_DIGEST.md` | Synthesized expert feedback rules |
| `STYLE_GUIDE.yaml` | Visual system |
| `PROMPT_LIBRARY.yaml` | Reusable prompt fragments |
| `FORMULA.md` | Production philosophy |
| `characters/` | Hero images |
| `VID##_story.md` | Source story |
| `VID##_template.yaml` | Video manifest |

## Recommended archetypes

- `masked_shame` (primary)
- `internal_collapse`
- `emotional_shutdown`
- `fear_of_vulnerability`

## Production notes

- **Voice**: en-US-AndrewMultilingualNeural (can be the same voice as EmotionalWithdrawal — the audience bonds with voice continuity)
- **Music**: 3-zone (piano/drone/silence) — same as EmotionalWithdrawal
- **Visual**: cinematic photorealism, 35mm film grain, but the **lighting key** shifts to mirror/public/private contrast:
  - Act 1 (public): bright, professional, suit-and-tie, conference room lighting
  - Act 2 (private): low light, parking garage, bathroom mirror, stairwell
  - Act 3 (recognition): single source, harsh, the moment of being seen
- **Duration**: 4-7 minutes target

## Visual motifs

- A suit that fits perfectly and a face that doesn't
- A reflection in a window that contradicts the public pose
- Hands that grip too hard
- A smile that doesn't reach the eyes
- Empty rooms after the performance
- The bathroom mirror
- The parking garage
- The stairwell
- The phone, dark, face-down
- A breath held too long

## Sound motifs

- Loud public noise, then sudden quiet
- A single heartbeat sound
- Echo in a stairwell
- The hum of a fluorescent light
- A breath released
- A door closing behind

## Voiceover cadence

Confident at first, then cracking. Pace slows. Pitch drops. The voice eventually trails off.

## Reference videos

(none yet — this territory is a new opportunity)

## How to start

1. Copy `projects/EmotionalWithdrawal/VID01_template.yaml` → `projects/ImposterSyndrome/VID01_template.yaml`
2. Change `story_file` to your new story
3. Update characters in `characters/` (the protagonist, not a couple)
4. Adjust the archetype to `masked_shame` in the manifest
5. Run the pipeline

The canonical video spec (`grammar/canonical_video_spec.yaml`) and the scene
blueprint schema (`grammar/scene_blueprint_schema.yaml`) apply unchanged.
Only the story, characters, and archetype change.

## Sample scene (the irreversible moment for masked_shame)

```yaml
- id: imposter-syndrome-08-the-pause
  index: 8
  title: "The Pause"
  beat: irreversible_moment
  emotional_state:
    primary: shame
    secondary: defensive
  visual_symbolism: [imperfection, downward_eye_contact, unfinished_gesture]
  camera_language:
    shot_size: close_up
    movement: static
    framing: rule_of_thirds
    lighting_key: dramatic_side_light
  narration:
    text: "He forgot the word. For one second, everyone knew."
    prosody_register: irreversible_moment
    vocal_fracture: true
  soundtrack_zone:
    music_zone: silent
    ambient_sfx_profile: irreversible_moment
    silence_instead: false
    silence_after_seconds: 3.0
  irreversible_moment: true
```
