# Emotional Withdrawal — Shared Universe Context

This directory produces cinematic psychological storytelling videos about
emotional withdrawal in intimate relationships. All videos share the same
visual universe, narrative philosophy, and technical pipeline.

## Files in this directory

| File | Purpose |
|------|---------|
| `CONTEXT.md` | This file. Shared creative universe, rules, constraints |
| `STYLE_GUIDE.yaml` | Visual system, color palette, shot language, character anchors |
| `PROMPT_LIBRARY.yaml` | Reusable prompt fragments, lighting setups, composition patterns |
| `FEEDBACK_DIGEST.md` | Synthesized expert feedback rules applied to every video |
| `VID01.md` | Original story script for VID01 |
| `VID01_sdxl.yaml` | Generation manifest for VID01 (SDXL + CLIP verification) |
| `VID01_revised.yaml` | Revised generation manifest incorporating feedback01 |
| `feedback01.md` | Raw expert feedback for VID01 |

## The Universe

### What this IS
- Cinematic psychological storytelling
- Emotionally interrupted relationships — not broken ones
- Human nuance, not gendered blame
- Prestige emotional storytelling, not "sad male content"

### What this is NOT
- YouTube commentary
- Advice content
- Villainization of either partner
- Monotonous suffering
- Viral outrage bait

### Core theme
> Your niche is not broken relationships. It is emotionally interrupted
> relationships. That's much deeper.

The strongest moments are not the sad moments. They are **almost moments**:
- almost touching
- almost speaking honestly
- almost reconnecting
- almost vulnerable

Emotional tension lives in **interruption**, not in despair.

## Narrative Philosophy

1. **Emotional contrast is mandatory.** Without warmth before the collapse,
   there is nothing lost. Insert memory, laughter, tenderness, hope before
   the withdrawal. Even 12 seconds of contrast changes everything.

2. **Recognition over analysis.** Narration should sound like internal truth
   discovery, not psychology explanation. Less "he felt unwanted" and more
   "he stopped knowing whether she still desired him or was simply used to
   him being there."

3. **Emotional modulation, not flatline.** Cinema needs modulation. If every
   scene is sad, dark, reflective — the audience stops feeling sadness.
   Need brief warmth, memory, contrast to make the collapse hurt.

4. **Uncomfortable duality.** She is exhausted too. She also feels rejected.
   She also stopped feeling emotionally safe. This elevates from "sad male
   content" to "human psychological storytelling."

5. **Nuance is the moat.** Not sadness, not masculinity, not relationships.
   Nuance. Protect it aggressively.

## Technical Pipeline

- **Model**: Stable Diffusion XL (local, M1 Max 64GB, MPS, float16)
- **Resolution**: 1024x576 (16:9 cinematic)
- **Verification**: CLIP ViT-B/32, 4 candidates per scene, min score 0.30
- **TTS**: Microsoft Edge TTS (en-US-GuyNeural), 44.1kHz, clear English
- **Video**: Ken Burns effects (zoom/pan), FFmpeg assembly, h264 + AAC
- **Duration**: 4-7 minutes (shorter forces precision, precision creates
  rewatchability)

## How to create a new video in this universe

1. Create a `VID##_story.md` file with the narrative structure
2. Create a `VID##_sdxl.yaml` manifest referencing the shared style guide
3. Run: `python scripts/generate_from_yaml.py <manifest.yaml>`
4. Review the output against the feedback digest rules
5. Iterate

## Video Structure Template (from expert feedback)

Every video should include:

```
1. Opening hook (emotional tension, not statistics)
2. Contrast moment (warmth, memory — something to lose)
3. The outside version (how it looks from outside)
4. The internal collapse (psychological truth)
5. The almost moment (interruption — almost touching/speaking/reconnecting)
6. The defensive retreat (self-protection)
7. The final truth (emotional resolution, not advice)
```

The "almost moment" (step 5) is where emotional tension lives.
The "contrast moment" (step 2) is what makes the audience mourn.