"""Agent 3: Story Generator.

This is the ONLY agent that writes the story. Input: the synopsis plus
the DNA and Context produced by Agents 1 and 2. Output: ~1200 words of
narrative prose structured in 3 acts with a fixed template:

    1. Opening state
    2. Inciting incident
    3. Escalation
    4. Midpoint shift
    5. Emotional collapse
    6. Climax
    7. Resolution

Why fixed template: the LLM is filling in the unique content, not
inventing the structure. This dramatically reduces token usage and
improves consistency.

The story contains NO camera directions, NO image prompts, NO production
notes. Those go in the Scene Structurer (Agent 4). Story is pure
narrative.

Input:  synopsis + dna.yaml + context.md
Output: story.md (~1200 words)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .llm_client import chat, LLMError


STORY_TEMPLATE = """\
# Story

<one_paragraph_logline_that_captures_the_entire_arc>

## Act 1 — The World Before

### Opening State
<2-3_paragraphs_describing_the_protagonist_in_their_normal_life>
<the_relationship_at_its_baseline>
<the_small_habits_that_will_become_meaningful_later>

### Inciting Incident
<the_specific_moment_that_starts_the_withdrawal>
<one_paragraph_that_lands_like_a_stone>

## Act 2 — The Slow Collapse

### Escalation
<2-3_paragraphs_of_the_distance_growing>
<the_small_withdrawals_that_accumulate>
<the_political_corrections_they_both_make>

### Midpoint Shift
<the_moment_she_notices_something_is_wrong>
<or_the_moment_he_realizes_he_is_avoiding>
<one_paragraph>

### Emotional Collapse
<the_internal_truth_revealed>
<not_what_happens_what_it_MEANS>
<2-3_paragraphs>

## Act 3 — The Quiet Truth

### Climax
<the_almost_moment>
<the_interruption_that_breaks_them>
<or_the_question_that_finally_lands>

### Resolution
<the_final_truth_that_drops_like_a_stone>
<not_advice_not_a_lesson>
<a_recognition_the_viewer_carries_home>
<1-2_paragraphs>
"""


SYSTEM_PROMPT = f"""You are a Story Generator for cinematic psychological storytelling. You are the ONLY agent that writes the narrative.

Input you receive:
- A synopsis (1-5 sentences from the user)
- A Story DNA (decisions about territory, mechanism, theme, ending)
- A Context document (the world, characters, setting, atmosphere)

Your ONLY job: write the story. ~1200 words. Pure narrative. No camera. No prompts. No production notes. No image descriptions.

Follow this EXACT template (section headings, order, structure):

{STORY_TEMPLATE}

Rules:
- Total length: ~1000-1400 words. Not shorter. The depth is the value.
- Each section is 1-3 paragraphs. Use the headings as emotional pacing, not as a checklist.
- Show, don't tell. "He stopped reaching for her" is better than "He felt unwanted."
- Include the "almost moment" in the Climax — the almost-touching, almost-speaking, almost-vulnerable moment that is interrupted.
- The final line of Resolution must be a quiet truth that lands in the chest. Not advice. Not a lesson. A recognition.
- Characters speak in short, grounded dialogue if they speak at all. Internal monologue is fine. Avoid therapy-speak.
- The DNA's `ending` field tells you what the Resolution should feel like:
  * quiet_realization: a quiet understanding that changes nothing and everything
  * devastating_truth: a hard truth that lands like a stone
  * bittersweet_hope: grief mixed with a thin ray of hope
  * open_question: an unanswered question that haunts
- Do NOT include any production directions (no "cut to", no "close-up", no "music swells"). That is the Scene Structurer's job.
- Output ONLY the markdown. No commentary. No fences.
"""


def generate_story(
    synopsis: str,
    dna: dict[str, Any],
    context: str,
    *,
    output_path: str | Path | None = None,
    temperature: float = 0.5,
    max_tokens: int = 3000,
    base_url: str = "http://localhost:1234",
    api_key: str = "sk-lm-TkM3NqaZ:CQdNsDjxGRm17O3Gg59W",
) -> str:
    """Generate the story narrative from synopsis + DNA + context.

    Args:
        synopsis: The original user synopsis.
        dna: The Story DNA dict (from dna_generator).
        context: The context markdown (from context_generator).
        output_path: If given, write the story markdown to this path.
        temperature: LLM sampling temperature. Slightly higher than DNA
            (0.5) to allow more narrative variation.
        max_tokens: Maximum tokens in the response.
        base_url: LMStudio base URL. Override for non-default deployments.
        api_key: LMStudio API key.

    Returns:
        The story markdown as a string.

    Raises:
        LLMError: If the LLM call fails.
    """
    user_prompt = f"""Synopsis:
{synopsis}

Story DNA:
{yaml.dump(dna, default_flow_style=False, sort_keys=False).strip()}

Context:
{context}

Now write the story. Follow the template exactly. ~1200 words. Pure narrative."""

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
        text = "# Story\n\n" + text

    if output_path is not None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            f.write(text)

    return text
