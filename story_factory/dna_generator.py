"""Agent 1: Story DNA Generator.

This is the ONLY agent that reads the user's synopsis. Its job is to make
decisions, not to write a story. Output is a tiny YAML (~100 tokens) that
captures the story's identity: territory, cluster, mechanism, archetype,
theme, premise, ending.

Why this is cheap: the LLM is only classifying and deciding, not creating.
The output is small and structured. Downstream agents use this to know
what kind of story they're building.

Input:  free-form synopsis (1-5 sentences)
Output: dna.yaml (~100 tokens)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .llm_client import chat, LLMError


DNA_SCHEMA = """\
id: EW-XXX
territory: <territory_name>           # e.g., "emotional_withdrawal"
cluster: <cluster_name>                # e.g., "fear_based_withdrawal"
mechanism: <psychological_mechanism>   # e.g., "anticipated_rejection"
archetype: <protagonist_archetype>     # e.g., "married_husband"
theme: <one_line_thematic_statement>   # e.g., "love_becomes_dangerous"
premise: <one_sentence_story_premise>  # the core dramatic question
ending: <ending_type>                  # "quiet_realization" | "devastating_truth" | "bittersweet_hope" | "open_question"
"""


SYSTEM_PROMPT = f"""You are a Story DNA Generator. Your only job is to classify a story synopsis into a fixed schema.

Given a synopsis, output ONLY a YAML document with these fields:

{DNA_SCHEMA}

Rules:
- Output ONLY the YAML. No commentary. No markdown fences. No explanation.
- The `id` should be derived from the territory prefix (e.g., "EW-001" for emotional_withdrawal) — use a placeholder like "EW-001" if you can't determine the number.
- The `theme` is a short phrase, not a sentence. Examples: "love_becomes_dangerous", "safety_replaces_desire", "grief_masks_as_anger".
- The `premise` is ONE sentence — the dramatic core.
- The `ending` must be one of: quiet_realization, devastating_truth, bittersweet_hope, open_question.

You are NOT writing a story. You are NOT creating characters. You are making decisions.
"""


def generate_dna(
    synopsis: str,
    *,
    output_path: str | Path | None = None,
    temperature: float = 0.3,
    max_tokens: int = 300,
    base_url: str = "http://localhost:1234",
    api_key: str = "sk-lm-TkM3NqaZ:CQdNsDjxGRm17O3Gg59W",
) -> dict[str, Any]:
    """Generate Story DNA from a synopsis.

    Args:
        synopsis: Free-form story synopsis (1-5 sentences).
        output_path: If given, write the DNA YAML to this path.
        temperature: LLM sampling temperature. Low for consistency.
        max_tokens: Maximum tokens in the response.
        base_url: LMStudio base URL. Override for non-default deployments.
        api_key: LMStudio API key.

    Returns:
        A dict representing the DNA YAML.

    Raises:
        LLMError: If the LLM call fails or returns unparseable YAML.
    """
    user_prompt = f"Synopsis:\n\n{synopsis}\n\nOutput the Story DNA YAML:"
    raw = chat(
        system=SYSTEM_PROMPT,
        user=user_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        base_url=base_url,
        api_key=api_key,
    )

    # Strip any markdown fences the LLM might add
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("yaml"):
            text = text[4:]
        text = text.strip()
        if text.endswith("```"):
            text = text[:-3].strip()

    try:
        dna = yaml.safe_load(text)
    except yaml.YAMLError as e:
        raise LLMError(f"DNA generator returned invalid YAML:\n{text}\n\nError: {e}") from e

    if not isinstance(dna, dict):
        raise LLMError(f"DNA generator returned non-dict YAML: {dna!r}")

    # Validate required fields
    required = {"id", "territory", "cluster", "mechanism", "archetype", "theme", "premise", "ending"}
    missing = required - dna.keys()
    if missing:
        raise LLMError(f"DNA missing required fields {missing}. Got: {dna!r}")

    if output_path is not None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            yaml.dump(dna, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    return dna
