"""EmotionAnalyst — Maps emotional arc, modulation points, irreversible moment, almost moment."""

from __future__ import annotations

import json
from typing import Any, TYPE_CHECKING

from movie_os.genesis.discovery.base import DiscoveryAgent
from movie_os.genesis.master_prompt import build_agent_prompt

if TYPE_CHECKING:
    from movie_os.genesis.pkg import ProductionKnowledgeGraph


class EmotionAnalyst(DiscoveryAgent):
    """Maps the emotional journey of the story.

    Identifies the beginning, middle, and end emotional states, the
    modulation points where emotion shifts, the irreversible moment
    (point of no return), and the almost moment (near-reconnection).
    This emotional map drives scene pacing and tonal contrast in the PKP.
    """

    name = "emotion_analyst"
    analysis_key = "emotional_arc"

    def build_prompt(self, pkg: "ProductionKnowledgeGraph") -> str:
        instructions = (
            "Analyze the synopsis and map the emotional journey: "
            "1) Beginning emotional state, "
            "2) Middle emotional state, "
            "3) End emotional state, "
            "4) Modulation points (where emotion shifts), "
            "5) The irreversible moment (the point of no return), "
            "6) The almost moment (near-reconnection). "
            "Respond with JSON containing: beginning_emotion, middle_emotion, "
            "end_emotion, modulation_points (array), irreversible_moment, "
            "almost_moment, confidence."
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

        modulation = parsed.get("modulation_points", [])
        if isinstance(modulation, str):
            modulation = [m.strip() for m in modulation.split(";") if m.strip()]
        elif not isinstance(modulation, list):
            modulation = []
        else:
            modulation = [str(m).strip() for m in modulation if str(m).strip()]

        normalized: dict[str, Any] = {
            "beginning_emotion": str(parsed.get("beginning_emotion", "")).strip(),
            "middle_emotion": str(parsed.get("middle_emotion", "")).strip(),
            "end_emotion": str(parsed.get("end_emotion", "")).strip(),
            "modulation_points": modulation,
            "irreversible_moment": str(parsed.get("irreversible_moment", "")).strip(),
            "almost_moment": str(parsed.get("almost_moment", "")).strip(),
            "confidence": parsed.get("confidence", "unknown"),
        }

        if not normalized["beginning_emotion"] or not normalized["end_emotion"]:
            raise ValueError(
                "EmotionAnalyst: 'beginning_emotion' and 'end_emotion' are required"
            )
        return normalized

    def _summarize(self, result: dict[str, Any]) -> str:
        return (
            f"begin='{result.get('beginning_emotion', '')[:40]}' "
            f"end='{result.get('end_emotion', '')[:40]}' "
            f"modulations={len(result.get('modulation_points', []))}"
        )