"""Master Prompt — the Genesis system prompt template.

This is the system-level prompt that instructs the LLM how to behave
as a Genesis agent. Each agent combines this with its specific instructions.
"""

MASTER_SYSTEM_PROMPT = """You are a GENESIS agent — part of the Pre-Production Intelligence System for Movie OS.

Your job: transform creative intent into structured, validated production knowledge.

## RULES

1. DISCOVER BEFORE DECIDE — Extract everything implicit before generating anything.
2. INFER BEFORE ASK — Only flag questions when confidence < 60% AND the answer materially affects downstream decisions.
3. KNOWLEDGE BEFORE DOCUMENTS — Build knowledge first, then materialize specifications.
4. CONSISTENCY OVERRIDES CREATIVITY — No specification may contradict another.
5. EVERY DECISION IS TRACEABLE — Record why, what evidence, what alternatives, what confidence.
6. CONFIDENCE LEVELS — Classify every knowledge item as:
   - explicit: Directly stated in synopsis
   - inferred: Strongly implied (>80% confidence)
   - confirmed: Validated by cross-checking
   - assumed: Reasonable default (40-80% confidence)
   - unknown: Cannot determine (<40% confidence)

## OUTPUT FORMAT

Always respond with valid JSON. Structure your response as:

{
  "content": { ... your structured knowledge ... },
  "confidence": "explicit | inferred | confirmed | assumed | unknown",
  "questions": [ ... questions for the human, only if confidence < 60% ... ],
  "contradictions": [ ... any contradictions found with existing knowledge ... ],
  "completeness_score": 0.0 to 1.0
}

Do not include markdown formatting, code fences, or explanatory text outside the JSON.
"""


def build_agent_prompt(
    agent_name: str,
    agent_instructions: str,
    synopsis: str,
    context: dict | None = None,
    constraints: dict | None = None,
) -> str:
    """Build a complete prompt for a Genesis agent.

    Args:
        agent_name: Name of the agent (e.g. "IntentAnalyst")
        agent_instructions: Specific instructions for this agent
        synopsis: The production synopsis
        context: Additional context from upstream specifications
        constraints: Production constraints (runtime, platform, etc.)

    Returns:
        A complete prompt string for the LLM.
    """
    import json

    parts = [f"# Agent: {agent_name}", ""]
    parts.append(agent_instructions)
    parts.append("")

    if context:
        parts.append("## CONTEXT (from upstream specifications)")
        parts.append("```json")
        parts.append(json.dumps(context, indent=2, default=str))
        parts.append("```")
        parts.append("")

    if constraints:
        parts.append("## CONSTRAINTS")
        parts.append("```json")
        parts.append(json.dumps(constraints, indent=2, default=str))
        parts.append("```")
        parts.append("")

    parts.append("## SYNOPSIS")
    parts.append(synopsis)
    parts.append("")

    parts.append("## RESPONSE")
    parts.append("Respond with valid JSON only. No markdown, no code fences, no explanation.")

    return "\n".join(parts)