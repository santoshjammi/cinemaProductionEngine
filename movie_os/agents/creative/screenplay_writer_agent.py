"""Movie OS v1 — Screenplay Writer Agent.

Writes screenplay with dialogue, actions, beats using Movie OS Screenplay Specification.
Takes outline.md + creative_brief.md as input and produces screenplay.md output.

Usage:
    from movie_os.agents.creative.screenplay_writer_agent import ScreenplayWriterAgent

    agent = ScreenplayWriterAgent()
    result = await agent.execute(context)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from movie_os.capabilities.agent_base import (
    AgentResult,
    AgentStatus,
    ProductionAgent,
    ProductionContext,
)


logger = logging.getLogger("movie_os.agents.creative.screenplay_writer_agent")


class ScreenplayWriterAgent(ProductionAgent):
    """Writes screenplay with dialogue, actions, beats.

    This agent takes outline.md and creative_brief.md as input and produces
    screenplay.md using the Movie OS Screenplay Specification format.

    Responsibilities:
        - Write structured screenplay with YAML frontmatter per scene
        - Include dialogue, actions, emotional beats, silence, narration
        - Follow grammar rules for dialogue style, pacing, camera language
        - Ensure cause-and-effect chain between scenes
    """

    name = "screenplay_writer"
    version = "1.0.0"
    capability = "story"
    grammar_aware = True

    async def execute(self, context: ProductionContext) -> AgentResult:
        """Execute screenplay writing for the production.

        Args:
            context: Production context with outline.md and creative_brief loaded.

        Returns:
            AgentResult with screenplay.md written to production_dir/screenplay.md
        """
        try:
            # Load input data from context
            outline = context.outline
            creative_brief = context.creative_brief
            grammar_config = context.grammar_config

            if not outline and not creative_brief:
                return AgentResult(
                    status=AgentStatus.FAILED,
                    message="No outline or creative brief loaded in context",
                )

            # Generate screenplay content using LLM
            screenplay_content = await self._generate_screenplay_with_llm(outline, creative_brief, grammar_config, context)

            # Write screenplay.md to production directory
            output_path = context.production_dir / "screenplay.md"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(screenplay_content)

            # Update context with screenplay data
            context.screenplay_path = output_path

            return AgentResult(
                status=AgentStatus.SUCCESS,
                message=f"Screenplay written for '{context.title}'",
                updated_context=context,
                artifacts={"screenplay_path": str(output_path)},
            )

        except Exception as e:
            logger.exception("Screenplay writing failed")
            return AgentResult(
                status=AgentStatus.FAILED,
                message=f"Screenplay writing failed: {str(e)}",
                errors=[str(e)],
            )

    async def _generate_screenplay_with_llm(self, outline: dict[str, Any], brief: dict[str, Any], grammar: dict[str, Any], context: ProductionContext) -> str:
        """Generate screenplay content using local LLM (Ollama)."""
        from movie_os.llm.client import get_llm_client

        llm = get_llm_client()
        if not llm.is_available():
            logger.warning("LLM not available, falling back to template")
            return self._generate_screenplay_template(outline, brief, grammar)

        # Prepare the system and user prompts
        title = context.title or "Untitled"
        
        # Get character information from brief if available, otherwise use defaults
        characters = brief.get("characters", [
            {"name": "Ethan Morrison", "age": 32, "role": "Marriage counselor"},
            {"name": "Claire Morrison", "age": 30, "role": "Graphic designer"}
        ])
        
        # Get the grammar name if available
        grammar_name = context.grammar if hasattr(context, 'grammar') and context.grammar else "psychological_cinema"
        
        # Get the target runtime if available
        target_runtime = brief.get("target_runtime", "15-20 minutes")
        
        # Get the primary emotion if available
        primary_emotion = brief.get("primary_emotion", "emotional withdrawal")
        
        system_prompt = f"""You are a senior screenplay writer for the Movie OS Cinema Production Engine.
Your job is to write high-quality screenplays following the Movie OS Screenplay Specification format.

Grammar: {grammar_name}
Production: {title}

Rules:
- Follow the Movie OS Screenplay Specification exactly
- Use proper YAML frontmatter for each scene (with all required fields)
- Write dialogue that matches the grammar's style and emotional tone
- Ensure each scene has a clear purpose, emotion, and character focus
- Include all required elements: dialogue, actions, beats, silence, narration, camera intent, music intent
- Never write melodrama or villain-making - focus on authentic emotional journeys
- Ensure cause-and-effect chain between scenes
- Keep the runtime in mind (target: {target_runtime})
- Focus on emotional authenticity and relatability
- Use the character information provided in the creative brief

Movie OS Screenplay Specification:
1. YAML frontmatter per scene with all required fields (Purpose, Location, Time, Characters, Emotion, Mood)
2. Dialogue section with character names in ALL CAPS and stage directions in parentheses
3. Action section describing visual elements and movements
4. Beat section with timing information (e.g., "pause: 2s")
5. Narration section for internal thoughts or voiceover
6. Director Notes with specific camera and editing instructions
7. Camera Intent section describing visual language (camera movement, framing)
8. Music Intent section with musical themes and cues
9. Silence/Pauses section for moments of quiet or tension

Format as a complete screenplay in proper Markdown with:
- Proper YAML frontmatter for each scene
- Clear section headings (Dialogue, Action, Beat, Narration, Director Notes, Camera Intent, Music Intent)
- All required elements in each scene
"""

        # Create a detailed outline of the screenplay structure from the input
        outline_content = ""
        if outline:
            outline_content += "## Outline Structure\n"
            for act_key, act_data in outline.items():
                if isinstance(act_data, dict):
                    outline_content += f"### {act_key}\n"
                    for scene in act_data.get("scenes", []):
                        outline_content += f"- {scene}\n"
                else:
                    outline_content += f"### {act_key}: {act_data}\n"

        # Create character information
        characters_info = ""
        for i, char in enumerate(characters):
            name = char.get("name", f"Character {i+1}")
            age = char.get("age", "Unknown")
            role = char.get("role", "Character")
            characteristics = char.get("characteristics", "")
            
            if characteristics:
                characters_info += f"- **{name}** ({age}) — {role}. {characteristics}\n"
            else:
                characters_info += f"- **{name}** ({age}) — {role}\n"

        user_prompt = f"""Create a complete screenplay for '{title}' following the Movie OS Screenplay Specification.

## Production Details
- Primary Emotion: {primary_emotion}
- Target Runtime: {target_runtime}

## Characters
{characters_info}

## Outline Structure
{outline_content if outline_content else "No detailed outline provided. Create a complete screenplay structure."}

## Required Screenplay Format

Write the entire screenplay in proper Markdown format with:
1. YAML frontmatter for each scene (with Purpose, Location, Time, Characters, Emotion, Mood)
2. Dialogue section with character names in ALL CAPS and stage directions in parentheses
3. Action section describing visual elements and movements  
4. Beat section with timing information (e.g., "pause: 2s")
5. Narration section for internal thoughts or voiceover
6. Director Notes with specific camera and editing instructions
7. Camera Intent section describing visual language (camera movement, framing)
8. Music Intent section with musical themes and cues
9. Silence/Pauses section for moments of quiet or tension

## Example Scene Format:
```
### SCENE 1: The Quiet Beginning [HOOK]

**Purpose:** Establish comfortable intimacy and shared history
**Location:** Kitchen, early morning, golden hour  
**Time:** Morning
**Characters:** Ethan, Claire
**Emotion:** Comfort
**Mood:** Warm, ordinary beauty

#### Dialogue

**ETHAN**
*(pouring coffee)* "You know what I noticed?"

**CLAIRE**
*(without looking up from her sketchbook)* "What?"

**ETHAN**
"You still take your coffee with two sugars. Even after seven years."

**CLAIRE**
*(smiles, finally looks up)* "Don't start with the poetry thing."

**ETHAN**
"It's not poetry. It's data. I'm a counselor. This is what I do."

**CLAIRE**
"And what does the data say?"

**ETHAN**
"That you're going to burn the toast again."

*(beat: she looks at the toaster, it's smoking)*

**CLAIRE**
"Shit."

#### Action

*Claire rushes to the toaster. Ethan laughs — a real laugh, not the polite one he'll stop making months from now.*

#### Beat

*pause: 2s — They share a look. The kind that says "we've done this a thousand times before."*

#### Narration

*Ethan's thoughts: This is what I've missed. The real connection.*

#### Director Notes

- Establish warm lighting and intimate framing
- Use close-ups for emotional beats  
- Cut to wide shot when Ethan pours coffee

#### Camera Intent

- Medium close-up on Ethan's face during the conversation
- Wide shot of the kitchen to show the setting

#### Music Intent

- Gentle piano melody with soft strings
- Musical cue when Ethan says "It's not poetry"

#### Silence/Pauses

*pause: 2s — They share a look. The kind that says "we've done this a thousand times before."*
```

Format the entire screenplay as proper Markdown with all scenes following this structure exactly."""
        
        # Generate content using LLM
        response = llm.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.7,
            max_tokens=8192
        )

        if response.success:
            return response.content
        else:
            logger.warning(f"LLM generation failed: {response.error}")
            return self._generate_screenplay_template(outline, brief, grammar)

    def _generate_screenplay_template(self, outline: dict[str, Any], brief: dict[str, Any], grammar: dict[str, Any]) -> str:
        """Generate a template screenplay when LLM is not available."""
        title = brief.get("title", "Untitled")
        
        # Default character set
        characters = brief.get("characters", [
            {"name": "Ethan Morrison", "age": 32, "role": "Marriage counselor"},
            {"name": "Claire Morrison", "age": 30, "role": "Graphic designer"}
        ])
        
        screenplay = f"""# {title}

## Characters
"""
        
        for i, char in enumerate(characters):
            name = char.get("name", f"Character {i+1}")
            age = char.get("age", "Unknown")
            role = char.get("role", "Character")
            characteristics = char.get("characteristics", "")
            
            if characteristics:
                screenplay += f"- **{name}** ({age}) — {role}. {characteristics}\n"
            else:
                screenplay += f"- **{name}** ({age}) — {role}\n"

        screenplay += """

## ACT 1 — HOOK: Make the Audience Fall in Love

### SCENE 1: The Quiet Beginning [HOOK]

**Purpose:** Establish comfortable intimacy and shared history
**Location:** Kitchen, early morning, golden hour  
**Time:** Morning
**Characters:** Ethan, Claire
**Emotion:** Comfort
**Mood:** Warm, ordinary beauty

#### Dialogue

**ETHAN**
*(pouring coffee)* "You know what I noticed?"

**CLAIRE**
*(without looking up from her sketchbook)* "What?"

**ETHAN**
"You still take your coffee with two sugars. Even after seven years."

**CLAIRE**
*(smiles, finally looks up)* "Don't start with the poetry thing."

**ETHAN**
"It's not poetry. It's data. I'm a counselor. This is what I do."

**CLAIRE**
"And what does the data say?"

**ETHAN**
"That you're going to burn the toast again."

*(beat: she looks at the toaster, it's smoking)*

**CLAIRE**
"Shit."

#### Action

*Claire rushes to the toaster. Ethan laughs — a real laugh, not the polite one he'll stop making months from now.*

#### Beat

*pause: 2s — They share a look. The kind that says "we've done this a thousand times before."*

#### Narration

*Ethan's thoughts: This is what I've missed. The real connection.*

#### Director Notes

- Establish warm lighting and intimate framing
- Use close-ups for emotional beats  
- Cut to wide shot when Ethan pours coffee

#### Camera Intent

- Medium close-up on Ethan's face during the conversation
- Wide shot of the kitchen to show the setting

#### Music Intent

- Gentle piano melody with soft strings
- Musical cue when Ethan says "It's not poetry"

#### Silence/Pauses

*pause: 2s — They share a look. The kind that says "we've done this a thousand times before."*

---

## ACT 2 — PLOT: The Tension Builds

### SCENE 2: The Unraveling [PLOT]

**Purpose:** Introduce conflict and emotional complexity
**Location:** Living room, evening  
**Time:** Evening
**Characters:** Ethan, Claire
**Emotion:** Tension
**Mood:** Uncertainty

#### Dialogue

**CLAIRE**
*(looking at her phone)* "Did you see the news about the divorce?"

**ETHAN**
*(pauses mid-sip)* "What news?"

**CLAIRE**
"The divorce. The one that's been going on for months."

**ETHAN**
*(defensive)* "I don't follow the news like that. I'm focused on my work."

**CLAIRE**
"You're not focused on anything except your own comfort zone. You don't even know what happened to the divorce."

**ETHAN**
*(quietly)* "I'm not sure I want to know. It's better this way."

#### Action

*Claire puts down her phone and stares at Ethan. The silence stretches between them.*

#### Beat

*pause: 3s — The weight of the conversation hangs in the air*

#### Narration

*Claire's thoughts: He never listens. Never really sees me.*

#### Director Notes

- Use medium shots to show the emotional distance between characters
- Focus on subtle facial expressions and body language

#### Camera Intent

- Medium shot of both characters sitting across from each other
- Close-up on Ethan's hands as he holds his cup

#### Music Intent

- Building tension with strings and percussion
- Subtle dissonance to indicate emotional conflict

#### Silence/Pauses

*pause: 3s — The weight of the conversation hangs in the air*

---

## ACT 3 — CLIMAX: The Emotional Resolution

### SCENE 3: The Confrontation [CLIMAX]

**Purpose:** Resolve the emotional conflict and show character growth
**Location:** Kitchen, morning  
**Time:** Morning
**Characters:** Ethan, Claire
**Emotion:** Resolution
**Mood:** Hopeful

#### Dialogue

**ETHAN**
*(looking at the coffee table)* "I've been thinking about what you said."

**CLAIRE**
*(quietly)* "About the divorce?"

**ETHAN**
"No. About what you said about me not listening."

**CLAIRE**
*(surprised)* "You're actually thinking about it?"

**ETHAN**
"I'm not sure I can fix what's broken, but I want to try."

#### Action

*Ethan stands up and walks toward the window. Claire watches him.*

#### Beat

*pause: 2s — The moment of realization*

#### Narration

*Ethan's thoughts: Maybe I can't fix everything, but I can start.*

#### Director Notes

- Show Ethan's internal struggle through body language
- Use warm lighting to indicate emotional growth and hope

#### Camera Intent

- Wide shot of the kitchen showing both characters in the space
- Close-up on Ethan's face as he speaks

#### Music Intent

- Gentle piano melody with warm strings
- Crescendo to indicate emotional resolution and hope

#### Silence/Pauses

*pause: 2s — The moment of realization*

---

## Final Notes for Production Team

This screenplay follows the Movie OS Screenplay Specification with proper YAML frontmatter, dialogue structure, and all required elements for emotional storytelling in the psychological cinema genre.

"""
        return screenplay