"""ConflictAnalyst — Identifies central conflict, internal/external, power dynamics, triggers."""

from __future__ import annotations

import json
from typing import Any, TYPE_CHECKING

from movie_os.genesis.discovery.base import DiscoveryAgent
from movie_os.genesis.master_prompt import build_agent_prompt

if TYPE_CHECKING:
    from movie_os.genesis.pkg import ProductionKnowledgeGraph


class ConflictAnalyst(DiscoveryAgent):
    """Identifies the conflict structure of the story.

    Surfaces the central conflict, internal (character vs self) and
    external (character vs other/environment) conflicts, the power
    dynamics at play, and the trigger that initiates change or
    withdrawal. Conflict structure is the backbone of the scene graph.
    """

    name = "conflict_analyst"
    analysis_key = "conflicts"

    def build_prompt(self, pkg: "ProductionKnowledgeGraph") -> str:
        instructions = (
            "Analyze the synopsis and identify: "
            "1) The central conflict, "
            "2) Internal conflicts (character vs self), "
            "3) External conflicts (character vs other/environment), "
            "4) Power dynamics, "
            "5) What triggers the change/withdrawal. "
            "Respond with JSON containing: central_conflict, "
            "internal_conflicts (array), external_conflicts (array), "
            "power_dynamics, trigger, confidence."
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

        def _as_list(value: Any) -> list[str]:
            if isinstance(value, str):
                return [v.strip() for v in value.split(";") if v.strip()]
            if isinstance(value, list):
                return [str(v).strip() for v in value if str(v).strip()]
            return []

        central = str(parsed.get("central_conflict", "")).strip()
        if not central:
            raise ValueError("ConflictAnalyst: missing required field 'central_conflict'")

        normalized: dict[str, Any] = {
            "central_conflict": central,
            "internal_conflicts": _as_list(parsed.get("internal_conflicts", [])),
            "external_conflicts": _as_list(parsed.get("external_conflicts", [])),
            "power_dynamics": str(parsed.get("power_dynamics", "")).strip(),
            "trigger": str(parsed.get("trigger", "")).strip(),
            "confidence": parsed.get("confidence", "unknown"),
        }
        return normalized

    def _summarize(self, result: dict[str, Any]) -> str:
        return (
            f"central='{result.get('central_conflict', '')[:80]}' "
            f"internal={len(result.get('internal_conflicts', []))} "
            f"external={len(result.get('external_conflicts', []))}"
        )