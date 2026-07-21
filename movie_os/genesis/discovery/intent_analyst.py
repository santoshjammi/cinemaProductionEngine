"""IntentAnalyst — Extracts creative intent, emotional transformation, territory, theme from the synopsis."""

from __future__ import annotations

import json
from typing import Any, TYPE_CHECKING

from movie_os.genesis.discovery.base import DiscoveryAgent
from movie_os.genesis.master_prompt import build_agent_prompt

if TYPE_CHECKING:
    from movie_os.genesis.pkg import ProductionKnowledgeGraph


class IntentAnalyst(DiscoveryAgent):
    """Extracts the core creative intent from a synopsis.

    This agent is the first discovery pass. It identifies what the story is
    actually trying to say, how the audience should be transformed, the
    emotional territory the story occupies, and the central theme. Downstream
    agents (theme, emotion, conflict) build on the intent this agent extracts.
    """

    name = "intent_analyst"
    analysis_key = "intent"

    def build_prompt(self, pkg: "ProductionKnowledgeGraph") -> str:
        instructions = (
            "Analyze the synopsis and extract: "
            "1) The core creative intent (what is the story trying to say?), "
            "2) The intended emotional transformation (how should the audience "
            "feel different after watching?), "
            "3) The territory (the emotional domain, e.g. 'The Quiet Marriage'), "
            "4) The central theme (the emotional question). "
            "Respond with JSON containing: intent, emotional_transformation, "
            "territory, theme, confidence."
        )
        return build_agent_prompt(
            agent_name=self.name,
            agent_instructions=instructions,
            synopsis=pkg.synopsis,
            context=pkg.get_all_discovery_results(),
            constraints=pkg.constraints,
        )

    def parse_response(self, response: str, pkg: "ProductionKnowledgeGraph") -> dict[str, Any]:
        from movie_os.genesis.llm_client import LLMClient

        parsed = LLMClient._extract_json(response)

        normalized: dict[str, Any] = {
            "intent": str(parsed.get("intent", "")).strip(),
            "emotional_transformation": str(parsed.get("emotional_transformation", "")).strip(),
            "territory": str(parsed.get("territory", "")).strip(),
            "theme": str(parsed.get("theme", "")).strip(),
            "confidence": parsed.get("confidence", "unknown"),
        }

        if not normalized["intent"]:
            raise ValueError("IntentAnalyst: missing required field 'intent'")
        if not normalized["theme"]:
            raise ValueError("IntentAnalyst: missing required field 'theme'")

        return normalized

    def _summarize(self, result: dict[str, Any]) -> str:
        return (
            f"intent='{result.get('intent', '')[:80]}' "
            f"territory='{result.get('territory', '')}' "
            f"theme='{result.get('theme', '')[:80]}'"
        )