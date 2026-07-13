"""Agent 2: Context Generator.

This agent NEVER invents the story. Its only job is to build the world
that the story will live in: characters, setting, psychological truth,
visual language, emotional atmosphere. It reads the user's synopsis and
produces a ~600-word context document.

Why it never writes the story: the Story Generator is the only creative
writing stage. Context builds the stage; Story performs on it.

Input:  synopsis (1-5 sentences)
Output: context.md (~600 words, fixed section structure)
"""

from __future__ import annotations

from pathlib import Path

from .llm_client import chat, LLMError


CONTEXT_SECTIONS = """\
# Context

## Territory
<territory_name>

## Theme
<theme_statement>

## Psychological Truth
<the_deeper_truth_under_the_story>

## Characters
<character_1_name> (<age>)
<occupation>
<personality_traits>
<one_line_role>

<character_2_name> (<age>)
<occupation>
<personality_traits>
<one_line_role>

## Relationship
<duration_and_nature_of_relationship>
<shared_context_children_history-etc>

## Setting
<where_they_live_and_work>
<time_period>
<physical_environment>

## Emotional Atmosphere
<the_feeling_that_permeates_every_scene>
<the_pace_and_pacing_of_life>

## Visual Language
<3-5_visual_anchors_that_reinforce_the_theme>
<lighting_and_color_motifs>
<spatial_relationships>

## Ending Emotion
<what_the_viewer_should_feel_in_their_chest_at_the_end>
"""


SYSTEM_PROMPT = f"""You are a Context Generator for cinematic psychological storytelling.

Your ONLY job is to build the world that a story will live in. You do NOT write the story. You do NOT narrate the plot. You describe the territory, the characters, the setting, and the emotional atmosphere.

Given a synopsis, output a Markdown document with EXACTLY these sections (in this order, with this exact heading text):

{CONTEXT_SECTIONS}

Rules:
- Each section should be 1-3 sentences. Total document: ~400-600 words.
- Characters: give them NAMES (not just roles), ages, occupations, 2-3 personality traits, and a one-line role in the story. Make them feel like real people, not archetypes.
- Psychological Truth: a single statement that captures what's really happening under the surface. Not the plot — the meaning.
- Visual Language: 3-5 concrete visual anchors (e.g., "muted interiors", "distance inside shared rooms", "night scenes", "long pauses", "hands almost touching").
- Ending Emotion: what the viewer should feel in their chest at the end. Not a plot point — an emotional state.
- Output ONLY the markdown. No commentary. No fences. No preamble.
- If the synopsis is thin, make reasonable inferences from the implied territory — do not ask for more input.
"""


def generate_context(
    synopsis: str,
    *,
    output_path: str | Path | None = None,
    temperature: float = 0.3,
    max_tokens: int = 1500,
    base_url: str = "http://localhost:1234",
    api_key: str = "sk-lm-TkM3NqaZ:CQdNsDjxGRm17O3Gg59W",
) -> str:
    """Generate the story context from a synopsis.

    Args:
        synopsis: Free-form story synopsis.
        output_path: If given, write the context markdown to this path.
        temperature: LLM sampling temperature.
        max_tokens: Maximum tokens in the response.
        base_url: LMStudio base URL. Override for non-default deployments.
        api_key: LMStudio API key.

    Returns:
        The context markdown as a string.

    Raises:
        LLMError: If the LLM call fails.
    """
    user_prompt = f"Synopsis:\n\n{synopsis}\n\nBuild the world for this story:"
    text = chat(
        system=SYSTEM_PROMPT,
        user=user_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        base_url=base_url,
        api_key=api_key,
    )

    # Strip any markdown fences
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("markdown") or text.startswith("md"):
            text = text.split("\n", 1)[1]
        text = text.strip()
        if text.endswith("```"):
            text = text[:-3].strip()

    if not text.startswith("#"):
        # LLM forgot the heading — prepend it
        text = "# Context\n\n" + text

    if output_path is not None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            f.write(text)

    return text
