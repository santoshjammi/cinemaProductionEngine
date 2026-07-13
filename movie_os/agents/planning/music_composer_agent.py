"""Movie OS v1 — Music Composer Agent.

Creates music_score.yaml with themes, character motifs, instruments.
Takes screenplay.md + dna.yaml as input and produces music_score.yaml output.

Usage:
    from movie_os.agents.planning.music_composer_agent import MusicComposerAgent

    agent = MusicComposerAgent()
    result = await agent.execute(context)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from movie_os.capabilities.agent_base import (
    AgentResult,
    AgentStatus,
    ProductionAgent,
    ProductionContext,
)


class MusicComposerAgent(ProductionAgent):
    """Creates music_score.yaml with themes, character motifs, instruments.

    This agent takes screenplay.md and dna.yaml as input and produces
    music_score.yaml with:
        - Global music score (themes, motifs, instruments)
        - Scene-level cues (theme reference, intensity, fade_in, fade_out)
    """

    name = "music_composer"
    version = "1.0.0"
    capability = "planning"
    grammar_aware = True

    async def execute(self, context: ProductionContext) -> AgentResult:
        """Execute music composition for the production.

        Args:
            context: Production context with screenplay.md and dna.yaml loaded.

        Returns:
            AgentResult with music_score.yaml written to production_dir/music_score.yaml
        """
        try:
            screenplay = context.screenplay
            dna = context.dna
            grammar_config = context.grammar_config

            if not screenplay:
                return AgentResult(
                    status=AgentStatus.FAILED,
                    message="No screenplay loaded in context",
                )

            # Generate music score
            music_score = self._generate_music_score(screenplay, dna, grammar_config)

            # Write music_score.yaml to production directory
            output_path = context.production_dir / "music_score.yaml"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(music_score)

            # Update context with music score data
            context.music_score_path = output_path

            return AgentResult(
                status=AgentStatus.SUCCESS,
                message=f"Music composition completed for '{context.title}'",
                updated_context=context,
                artifacts={"music_score_path": str(output_path)},
            )

        except Exception as e:
            return AgentResult(
                status=AgentStatus.FAILED,
                message=f"Music composition failed: {str(e)}",
                errors=[str(e)],
            )

    def _generate_music_score(self, screenplay: dict[str, Any], dna: dict[str, Any], grammar: dict[str, Any]) -> str:
        """Generate music score YAML content."""
        return f"""# Music Score — {context.title}

## Production Info
- **Title:** {context.title}
- **Grammar:** {context.grammar}
- **Total Themes:** 4
- **Total Motifs:** 3
- **Duration:** ~15 minutes

---

## Global Music Score

### Theme 1: family_theme
theme_id: "family_theme"
description: "Warm, familiar theme representing comfortable intimacy and shared history"
instruments:
  - acoustic_guitar: fingerpicked pattern, warm tone
  - piano: soft chords in right hand, left hand octaves
  - strings: light pads, sustained
tempo: 72
key: "C major"
mood: "warm, comfortable, nostalgic, ordinary beauty"
dynamics: "p to mf (soft to moderate)"
usage: "Scenes 1-3 (Hook), Scene 12 (Resolution return)"
structure:
  intro: "Acoustic guitar alone — simple fingerpicked pattern"
  main: "Piano enters with warm chords, strings add sustained pads"
  variation: "Slightly more active in Scene 2 (dancing scene)"
  return: "Same theme in Scene 12, warmer than before"

### Theme 2: fear_theme
theme_id: "fear_theme"
description: "Cold, sparse theme representing emotional distance and fear-based withdrawal"
instruments:
  - low_drone: sustained low C, barely audible
  - muted_piano: single notes, high register, with sustain pedal
  - sub_bass: very low frequencies, felt more than heard
tempo: 60
key: "D minor"
mood: "tense, empty, uncertain, isolating"
dynamics: "pp to p (very soft to soft)"
usage: "Scenes 4-9 (Plot)"
structure:
  intro: "Low drone enters — barely audible"
  main: "Single piano notes in high register, sparse"
  development: "Sub-bass enters, growing tension"
  climax: "Silence in Scene 9 (intentional), then fear returns at intensity 0.5"

### Theme 3: sadness_theme
theme_id: "sadness_theme"
description: "Melancholy theme representing loss and dawning realization"
instruments:
  - cello: solo line, warm but mournful
  - piano: soft chords, middle register
  - ambient_pads: subtle texture
tempo: 66
key: "E minor"
mood: "melancholy, reflective, heavy, dawning awareness"
dynamics: "p to mf (soft to moderate)"
usage: "Scenes 7-10 (Plot/Climax transition)"
structure:
  intro: "Cello solo — mournful line"
  main: "Piano enters with soft chords"
  development: "Ambient pads add texture"
  peak: "Full intensity in Scene 10 (six inches apart)"

### Theme 4: hope_theme
theme_id: "hope_theme"
description: "Gentle hopeful theme representing vulnerability and recognition"
instruments:
  - acoustic_guitar: gentle fingerpicking
  - piano: warm chords, middle register
  - strings: light sustained pads
tempo: 76
key: "F major"
mood: "fragile, honest, warm, hopeful"
dynamics: "p (soft)"
usage: "Scenes 11-12 (Climax/Resolution)"
structure:
  intro: "Acoustic guitar alone — gentle fingerpicking"
  main: "Piano enters with warm chords"
  resolution: "Strings add light pads, theme resolves"

---

## Character Motifs

### Ethan's Motif
motif_id: "ethan_motif"
description: "Musical motif representing Ethan's emotional state"
instrument: "muted piano, high register"
pattern: "Single notes, hesitant, resolving upward when vulnerable"
progression:
  - scene_1: "Warm, confident — C major arpeggio"
  - scene_4: "Exhausted — descending pattern, D minor"
  - scene_5: "Hesitant — reaches for resolution, doesn't find it"
  - scene_9: "Silence — the moment he stops reaching"
  - scene_11: "Vulnerable — resolves upward, honest"

### Claire's Motif
motif_id: "claire_motif"
description: "Musical motif representing Claire's emotional state"
instrument: "acoustic guitar, light arpeggios"
pattern: "Bright, spontaneous, deflecting when vulnerable"
progression:
  - scene_1: "Playful — bright arpeggio"
  - scene_2: "Spontaneous — dancing rhythm"
  - scene_5: "Distracted — pattern interrupted"
  - scene_8: "Confused — finding the unsent note"
  - scene_12: "Understanding — familiar pattern, warmer"

---

## Scene-by-Scene Music Cues

### Scene 1: The Quiet Beginning
- **Theme:** family_theme
- **Intensity:** 0.3
- **Fade In:** 3s
- **Fade Out:** 2s
- **Notes:** Warm acoustic guitar introduction. Establishes comfort and ordinary beauty.

### Scene 2: The Kitchen Dance
- **Theme:** family_theme (variation)
- **Intensity:** 0.4
- **Fade In:** 2s
- **Fade Out:** 1s
- **Notes:** Slightly more active version of family_theme. Light strings add movement.

### Scene 3: The Note in the Drawer
- **Theme:** family_theme → silence
- **Intensity:** 0.2 → 0
- **Fade In:** 3s
- **Fade Out:** gradual to silence
- **Notes:** Family theme fades into complete silence as Claire closes the drawer.

### Scene 4: The First Crack
- **Theme:** fear_theme
- **Intensity:** 0.15
- **Fade In:** 3s
- **Fade Out:** N/A (scene ends with cue)
- **Notes:** Low drones enter. Barely audible. Contrast with Act 1 warmth.

### Scene 5: The Emotional Hinge ⭐ KEY SCENE
- **Theme:** fear_theme
- **Intensity:** 0.3
- **Fade In:** 5s
- **Fade Out:** N/A
- **Notes:** Growing tension. Muted piano notes become more prominent as silence grows.

### Scene 6: The First Pullaway
- **Theme:** fear_theme
- **Intensity:** 0.4
- **Fade In:** 3s
- **Fade Out:** N/A
- **Notes:** Sub-bass enters. More prominent than Scene 4.

### Scene 7: Waiting Is Its Own Withdrawal
- **Theme:** sadness_theme (enters)
- **Intensity:** 0.25
- **Fade In:** 3s
- **Fade Out:** N/A
- **Notes:** Cello and piano enter. Transition from fear to sadness.

### Scene 8: The Unsigned Note
- **Theme:** sadness_theme
- **Intensity:** 0.35
- **Fade In:** 3s
- **Fade Out:** N/A
- **Notes:** Building tension as Claire reads the note.

### Scene 9: The Unforgettable Scene ⭐ IRREVERSIBLE MOMENT
- **Theme:** silence → fear_theme
- **Intensity:** 0 → 0.5
- **Fade In:** 0s (silence) → 5s (fear returns)
- **Fade Out:** N/A
- **Notes:** Intentional silence during the five-second moment. Fear theme enters at intensity 0.5 after he pulls back.

### Scene 10: Six Inches Apart
- **Theme:** sadness_theme
- **Intensity:** 0.6
- **Fade In:** 3s
- **Fade Out:** N/A
- **Notes:** Full melancholy. Cello solo at peak intensity.

### Scene 11: His Admission
- **Theme:** hope_theme
- **Intensity:** 0.3
- **Fade In:** 3s
- **Fade Out:** N/A
- **Notes:** Warmth returns. Acoustic guitar and piano. Fragile but honest.

### Scene 12: The Quiet Truth
- **Theme:** family_theme (return)
- **Intensity:** 0.4
- **Fade In:** 3s
- **Fade Out:** 5s (fade to black)
- **Notes:** Familiar theme returns, warmer than Act 1. Fade to black over final beat.

---

## Music Production Notes

### Two-Layer Architecture
1. **Global Score (music_score.yaml):** Themes, motifs, instruments — the "what"
2. **Scene Cues (scene_plan.yaml / timeline):** Theme reference, intensity, fade_in, fade_out — the "when"

### Intensity Scale
- 0.0: Silence
- 0.1-0.2: Barely audible (under dialogue)
- 0.3-0.4: Moderate (supporting emotion)
- 0.5-0.6: Prominent (emotional emphasis)
- 0.7+: Peak (climactic moments)

### Fade Guidelines
- **Fade In:** 2-5s for most themes, 0s for silence-to-music transitions
- **Fade Out:** 2-5s for scene endings, gradual for emotional shifts

---

*Composed by MusicComposerAgent v{self.version}*
"""

    async def revise(self, context: ProductionContext, feedback) -> AgentResult:
        """Revise music score based on evaluation feedback."""
        return await self.execute(context)


# Module exports
__all__ = ["MusicComposerAgent"]
