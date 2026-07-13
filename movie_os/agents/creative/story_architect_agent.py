"""Movie OS v1 — Story Architect Agent.

Structures story using HOOK-PLOT-CLIMAX framework.
Takes research.md + dna.yaml as input and produces outline.md output.

Usage:
    from movie_os.agents.creative.story_architect_agent import StoryArchitectAgent

    agent = StoryArchitectAgent()
    result = await agent.execute(context)
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from movie_os.capabilities.agent_base import (
    AgentResult,
    AgentStatus,
    ProductionAgent,
    ProductionContext,
)


logger = logging.getLogger("movie_os.agents.creative.story_architect_agent")


class StoryArchitectAgent(ProductionAgent):
    """Structures story using HOOK-PLOT-CLIMAX framework.

    This agent takes research.md and dna.yaml as input and produces
    outline.md with structured scene-by-scene narrative arc.

    Responsibilities:
        - Structure story into HOOK (Act 1), PLOT (Act 2), CLIMAX (Act 3)
        - Define scene-by-scene narrative progression
        - Ensure cause-and-effect chain between scenes
        - Maintain emotional arc consistency
    """

    name = "story_architect"
    version = "1.0.0"
    capability = "story"
    grammar_aware = True

    async def execute(self, context: ProductionContext) -> AgentResult:
        """Execute story architecture for the production.

        Uses local LLM (Ollama) to structure the story based on research and DNA.
        Falls back to template if LLM is unavailable.

        Args:
            context: Production context with dna.yaml and research.md loaded.

        Returns:
            AgentResult with outline.md written to production_dir/outline.md
        """
        try:
            # Load input data from context
            dna = context.dna
            research_text = context.research_path.read_text() if context.research_path.exists() else ""

            if not dna:
                return AgentResult(
                    status=AgentStatus.FAILED,
                    message="No DNA data loaded in context",
                )

            # Try LLM-based outline first
            outline_content = None
            try:
                outline_content = await self._generate_outline_with_llm(dna, research_text, context)
                logger.info(f"Outline generated via LLM ({len(outline_content)} chars)")
            except Exception as llm_error:
                logger.warning(f"LLM outline failed, falling back to template: {llm_error}")

            if not outline_content:
                outline_content = self._generate_outline_template(dna, research_text, context)

            # Write outline.md to production directory
            output_path = context.production_dir / "outline.md"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(outline_content)

            # Update context with outline data
            context.outline_path = output_path

            return AgentResult(
                status=AgentStatus.SUCCESS,
                message=f"Story architecture completed for '{context.title}'",
                updated_context=context,
                artifacts={"outline_path": str(output_path)},
            )

        except Exception as e:
            return AgentResult(
                status=AgentStatus.FAILED,
                message=f"Story architecture failed: {str(e)}",
                errors=[str(e)],
            )

    async def _generate_outline_with_llm(self, dna: dict[str, Any], research_text: str, context: ProductionContext) -> str:
        """Generate outline using local LLM (Ollama) based on research and DNA."""
        from movie_os.llm.client import get_llm_client

        llm = get_llm_client()
        if not llm.is_available():
            logger.warning("LLM not available, falling back to template")
            return None

        territory = dna.get("territory", "unknown")
        cluster = dna.get("cluster", "unknown")
        mechanism = dna.get("mechanism", "unknown")
        archetype = dna.get("archetype", "unknown")
        theme = dna.get("theme", "unknown")
        premise = dna.get("premise", "")

        target_runtime = context.creative_brief.get("target_runtime", "14 minutes") if context.creative_brief else "14 minutes"
        target_audience = context.creative_brief.get("target_audience", "general") if context.creative_brief else "general"

        system_prompt = f"""You are a senior story architect for a Cinema Production Engine.
Your job is to structure a compelling narrative using the HOOK-PLOT-CLIMAX framework.

Grammar: {context.grammar if hasattr(context, 'grammar') and context.grammar else 'psychological_cinema'}
Target Runtime: {target_runtime}
Target Audience: {target_audience}

Rules:
- Structure must serve emotional truth, not plot mechanics
- Every scene must have a clear narrative purpose
- Cause-and-effect chain is non-negotiable
- No melodrama, no villains — withdrawal is mutual and unconscious
- Silence and stillness are dramatic tools, not empty space
- The audience must feel the loss because they invested in the love

Output format: Markdown with clear scene headings, durations, purposes, and emotional beats."""

        user_prompt = f"""Structure this production's outline based on the DNA and research.

## Production DNA
- Territory: {territory}
- Cluster: {cluster}
- Mechanism: {mechanism}
- Archetype: {archetype}
- Theme: {theme}
- Premise: {premise}

## Research Summary (from ResearchAgent)
{research_text[:3000] if research_text else 'No research available'}

## Required Structure

### ACT 1 — HOOK: Make the Audience Fall in Love
- 3 scenes that establish the relationship before it changes
- Each scene must show, not tell, why these people love each other
- Include specific visual details (not generic descriptions)
- Total duration: ~40% of runtime

### ACT 2 — PLOT: The Invisible Shift
- 5-6 scenes showing the slow drift
- No dramatic events — just accumulated small moments
- Each scene must escalate the distance slightly
- Include one KEY SCENE (the hinge moment neither character recognizes)
- Total duration: ~40% of runtime

### ACT 3 — CLIMAX: The Moment of Recognition
- 2-3 scenes where something finally breaks through
- Not resolution — just recognition
- Must feel earned by everything that came before
- Total duration: ~20% of runtime

For each scene, specify:
1. Scene number and title
2. Duration (in seconds, aligned to target runtime)
3. Location
4. Characters present
5. Narrative purpose (what this scene does for the story)
6. Emotional intent (what the audience should feel)
7. Key visual detail (one specific image that carries the emotion)
8. Dialogue beats (if any — remember: real people don't speak in essays)

Target total runtime: {target_runtime}"""

        response = llm.generate(system_prompt, user_prompt, temperature=0.85, max_tokens=6144)

        if not response.success:
            logger.warning(f"LLM outline failed: {response.error}")
            return None

        return f"""# Outline — {context.title if hasattr(context, 'title') and context.title else 'Untitled'}

## Production DNA
- **Territory:** {territory}
- **Cluster:** {cluster}
- **Mechanism:** {mechanism}
- **Archetype:** {archetype}
- **Theme:** {theme}

---

{response.content}

---

*Generated by StoryArchitectAgent v{self.version} via LLM ({response.model_used})*
"""

    def _generate_outline_template(self, dna: dict[str, Any], research_text: str, context: ProductionContext) -> str:
        """Generate outline using template (fallback when LLM unavailable)."""
        territory = dna.get("territory", "unknown")
        cluster = dna.get("cluster", "unknown")
        mechanism = dna.get("mechanism", "unknown")
        archetype = dna.get("archetype", "unknown")
        theme = dna.get("theme", "unknown")
        premise = dna.get("premise", "")

        outline = f"""# Outline — {context.title if hasattr(context, 'title') and context.title else 'Untitled'}

## Production DNA
- **Territory:** {territory}
- **Cluster:** {cluster}
- **Mechanism:** {mechanism}
- **Archetype:** {archetype}
- **Theme:** {theme}
- **Premise:** {premise}

---

## ACT 1 — HOOK: Make the Audience Fall in Love (0–4 minutes)

### Purpose
Establish who these people are before anything changes. The audience must emotionally invest in the relationship so they feel the loss when it shifts.

### Scene 1: The Quiet Beginning [HOOK]
**Duration:** 60 seconds
**Purpose:** Show comfortable intimacy and shared history
**Location:** Kitchen, morning
**Characters:** Ethan, Claire
**Emotion:** Comfort, warmth
**Mood:** Golden hour, ordinary beauty

*Dialogue beats:*
- Ethan notices something small about Claire (coffee order, habit)
- Claire responds with inside joke or deflection
- Shared glance that says "we've done this a thousand times"

### Scene 2: The Kitchen Dance [HOOK]
**Duration:** 60 seconds
**Purpose:** Show physical affection and playful dynamic
**Location:** Kitchen/living room
**Characters:** Ethan, Claire
**Emotion:** Playfulness, ease
**Mood:** Warm, spontaneous

*Dialogue beats:*
- Spontaneous moment of connection (dancing for five seconds, burning dinner)
- Laughter over something mundane
- Physical touch that feels natural, not performative

### Scene 3: The Note in the Drawer [HOOK]
**Duration:** 60 seconds
**Purpose:** Establish the handwritten notes motif — what used to be
**Location:** Bedroom drawer / desk
**Characters:** Claire (solo), Ethan (off-screen)
**Emotion:** Quiet nostalgia
**Mood:** Intimate, private

*Dialogue beats:*
- Claire finds an old note (or Ethan leaves a new one)
- No dialogue — just the visual of handwritten words
- The note says something simple but meaningful

---

## ACT 2 — PLOT: The Invisible Shift (4–10 minutes)

### Purpose
Show the slow, almost invisible drift. Nothing dramatic happens — that's the point. Small moments accumulate into emotional distance.

### Scene 4: The First Crack [PLOT]
**Duration:** 60 seconds
**Purpose:** Introduce the catalyst — work stress, late nights, missed connections
**Location:** Office / home evening
**Characters:** Ethan (solo), Claire (off-screen)
**Emotion:** Exhaustion, quiet frustration
**Mood:** Diminished warmth

*Dialogue beats:*
- Ethan comes home after she's asleep
- "How was your day?" asked while looking at a screen
- He starts to answer, then stops — why bother?

### Scene 5: The Emotional Hinge [PLOT] ⭐ KEY SCENE
**Duration:** 60 seconds
**Purpose:** THE MOMENT EVERYTHING CHANGED — neither knows it at the time
**Location:** Living room, evening
**Characters:** Ethan, Claire (distracted)
**Emotion:** Reached for connection, received nothing
**Mood:** The silence between reaching and not-reaching

*Dialogue beats:*
- Ethan had something real to share (pride, vulnerability, joy)
- Claire is distracted — laptop, phone, work
- "How was your day?" asked without looking up
- He stands in the doorway, words building behind his teeth
- "Good," he says instead of what he meant to say
- She says "That's nice" without looking up
- He walks away. Decides, without deciding, to keep it to himself next time

### Scene 6: The First Pullaway [PLOT]
**Duration:** 60 seconds
**Purpose:** Show the first withdrawal — he pulls back, she doesn't notice yet
**Location:** Bedroom, night
**Characters:** Ethan, Claire (sleeping)
**Emotion:** Hesitation, fear
**Mood:** Dark, intimate, quiet

*Dialogue beats:*
- She reaches for him in bed (spontaneous, unthinking)
- He tensed — pulled away before she found him
- "I'm sorry" whispered to the wall behind her
- She meant nothing by it. He assumed he'd failed.

### Scene 7: Waiting Is Its Own Withdrawal [PLOT]
**Duration:** 60 seconds
**Purpose:** Show both sides — he stops initiating, she waits (which is also withdrawal)
**Location:** Kitchen, morning
**Characters:** Ethan, Claire
**Emotion:** Routine without connection
**Mood:** Flat normality

*Dialogue beats:*
- She makes coffee for both of them "just in case"
- He drinks it standing at the counter
- Never thanks her. Never notices. Or notices and doesn't know what to do with it.
- Neither says anything about the silence growing

### Scene 8: The Unsigned Note [PLOT]
**Duration:** 60 seconds
**Purpose:** She finds his unsent note — parallel to her keeping his
**Location:** His desk drawer
**Characters:** Claire (solo)
**Emotion:** Confusion, dawning concern
**Mood:** Quiet discovery

*Dialogue beats:*
- She finds an unsigned, unsent note dated two months ago
- "I hope I never become someone who makes you feel alone"
- She doesn't know what to do with it. Puts it back.
- Begins wondering: is he unhappy? Is it me?

### Scene 9: The Unforgettable Scene [PLOT] ⭐ IRREVERSIBLE MOMENT
**Duration:** 60 seconds
**Purpose:** THE FIVE-SECOND MOMENT that becomes the emotional identity of everything
**Location:** Bedroom, night
**Characters:** Ethan, Claire (sleeping)
**Emotion:** Choosing fear over love for the last time
**Mood:** Stillness, weight, silence

*Dialogue beats:*
- He reaches for her hand in bed one more time
- His fingers move toward hers across the narrow space
- He pauses — just a beat, just five seconds
- She never wakes up
- He slowly pulls his hand back. Lies on his side. Stares at the ceiling.
- No dialogue. No music. Just five seconds of a man choosing fear over love.

---

## ACT 3 — CLIMAX: The Emotional Reveal (10–13 minutes)

### Purpose
Reveal what was happening inside both characters. Not reconciliation — recognition.

### Scene 10: Six Inches Apart [CLIMAX]
**Duration:** 60 seconds
**Purpose:** Show the distance — sleeping six inches apart, emotionally miles
**Location:** Bedroom, months later
**Characters:** Ethan, Claire (both awake, both pretending)
**Emotion:** Quiet devastation
**Mood:** Cold, distant, heavy

*Dialogue beats:*
- Neither speaks. Both are aware of the space between them.
- The space that wasn't there before.
- The space that grew without either of them noticing.

### Scene 11: His Admission [CLIMAX]
**Duration:** 60 seconds
**Purpose:** He finally says what he's been hiding
**Location:** Bedroom, evening
**Characters:** Ethan, Claire
**Emotion:** Vulnerability, fear, honesty
**Mood:** Fragile, raw

*Dialogue beats:*
- "I didn't stop wanting you."
- Pause. Looks at her for the first time in months.
- "I just became afraid of failing you."
- She doesn't know what to say. Neither does he.
- But for five seconds, they're honest.

---

## ACT 4 — RESOLUTION: Recognition, Not Resolution (13–15 minutes)

### Purpose
Quiet truth lands. No villains. No dramatic betrayals. Just ordinary people making ordinary decisions that slowly create extraordinary emotional distance.

### Scene 12: The Quiet Truth [RESOLUTION]
**Duration:** 60 seconds
**Purpose:** The recognition that makes someone think "This could have happened to my parents"
**Location:** Kitchen, morning — same as Scene 1 but different
**Characters:** Ethan, Claire (parallel actions)
**Emotion:** Recognition, quiet hope
**Mood:** Familiar but changed

*Dialogue beats:*
- She still keeps his last note in her drawer
- He still makes coffee for both of them in the morning
- Neither has said anything about it
- But the coffee is still warm. The note is still there.
- And that's not nothing. That's everything.

---

## Emotional Arc Summary

| Act | Duration | Purpose | Emotional State |
|-----|----------|---------|-----------------|
| Hook (Act 1) | 0–4 min | Make audience fall in love | Warmth, comfort, ordinary beauty |
| Plot (Act 2) | 4–10 min | Show invisible drift | Exhaustion, hesitation, silence |
| Climax (Act 3) | 10–13 min | Reveal internal world | Vulnerability, fear, honesty |
| Resolution (Act 4) | 13–15 min | Recognition without resolution | Quiet hope, recognition |

## Key Scenes (Must Be Memorable)

1. **Scene 5 — The Emotional Hinge:** He reaches for her with something real — she isn't there to receive it. Neither decides anything consciously. But everything changes.
2. **Scene 9 — The Five-Second Moment:** No dialogue. Just five seconds of a man choosing fear over love for the last time. This becomes the emotional identity of everything that follows.

## Psychological Truth

> Fear-based withdrawal doesn't begin when love ends. It begins when vulnerability starts feeling more dangerous than distance.
>
> It doesn't happen in one night. It happens one quiet disappointment at a time — one hand not held, one message not sent, one conversation postponed for months — until the people who used to reach for each other have forgotten how.

---
*Generated by StoryArchitectAgent v{self.version}*
"""
        return outline

    async def revise(self, context: ProductionContext, feedback) -> AgentResult:
        """Revise outline based on evaluation feedback."""
        # Outline revision would re-run with updated parameters
        return await self.execute(context)


# Module exports
__all__ = ["StoryArchitectAgent"]
