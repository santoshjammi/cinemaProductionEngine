"""GapAnalyst — Classifies all knowledge as EXPLICIT/INFERRED/CONFIRMED/ASSUMED/UNKNOWN."""

from __future__ import annotations

import json
from typing import Any, TYPE_CHECKING

from movie_os.genesis.discovery.base import DiscoveryAgent
from movie_os.genesis.master_prompt import build_agent_prompt

if TYPE_CHECKING:
    from movie_os.genesis.pkg import ProductionKnowledgeGraph


class GapAnalyst(DiscoveryAgent):
    """Classifies knowledge gaps to drive the question phase.

    Reviews everything discovered so far and classifies ALL knowledge
    into explicit, inferred, confirmed, assumed, and unknown buckets.
    Flags critical_gaps — items that are both unknown AND critical to
    downstream decisions. The QuestionPlanner consumes critical_gaps
    to decide what to ask the human.
    """

    name = "gap_analyst"
    analysis_key = "knowledge_gaps"

    def build_prompt(self, pkg: "ProductionKnowledgeGraph") -> str:
        instructions = (
            "Analyze the synopsis and classify ALL knowledge into: "
            "1) Explicit (directly stated), "
            "2) Inferred (strongly implied >80%), "
            "3) Confirmed (validated), "
            "4) Assumed (reasonable default 40-80%), "
            "5) Unknown (cannot determine <40%). "
            "List what is known and what is missing. "
            "Respond with JSON containing: explicit (array), inferred "
            "(array), confirmed (array), assumed (array), unknown (array), "
            "critical_gaps (array of items that are unknown AND critical), "
            "confidence."
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

        normalized: dict[str, Any] = {
            "explicit": _as_list(parsed.get("explicit", [])),
            "inferred": _as_list(parsed.get("inferred", [])),
            "confirmed": _as_list(parsed.get("confirmed", [])),
            "assumed": _as_list(parsed.get("assumed", [])),
            "unknown": _as_list(parsed.get("unknown", [])),
            "critical_gaps": _as_list(parsed.get("critical_gaps", [])),
            "confidence": parsed.get("confidence", "unknown"),
        }

        total = sum(
            len(normalized[k]) for k in ("explicit", "inferred", "confirmed", "assumed", "unknown")
        )
        if total == 0:
            raise ValueError("GapAnalyst: all classification buckets are empty")
        return normalized

    def _summarize(self, result: dict[str, Any]) -> str:
        return (
            f"explicit={len(result.get('explicit', []))} "
            f"inferred={len(result.get('inferred', []))} "
            f"unknown={len(result.get('unknown', []))} "
            f"critical={len(result.get('critical_gaps', []))}"
        )