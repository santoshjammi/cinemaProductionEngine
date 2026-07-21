"""AudienceAnalyst — Determines target audience, emotional state, transformation, objections."""

from __future__ import annotations

import json
from typing import Any, TYPE_CHECKING

from movie_os.genesis.discovery.base import DiscoveryAgent
from movie_os.genesis.master_prompt import build_agent_prompt

if TYPE_CHECKING:
    from movie_os.genesis.pkg import ProductionKnowledgeGraph


class AudienceAnalyst(DiscoveryAgent):
    """Determines the target audience and their journey.

    Identifies the target audience (demographics and psychographics),
    the emotional state they are in when watching, the transformation
    they should experience, and the objections or resistance the story
    must overcome. Audience insight shapes tone, pacing, and content
    warnings in the PKP.
    """

    name = "audience_analyst"
    analysis_key = "audience"

    def build_prompt(self, pkg: "ProductionKnowledgeGraph") -> str:
        instructions = (
            "Analyze the synopsis and determine: "
            "1) Target audience (demographics, psychographics), "
            "2) Their emotional state when watching, "
            "3) The transformation they should experience, "
            "4) Potential objections or resistance. "
            "Respond with JSON containing: target_audience, emotional_state, "
            "desired_transformation, objections (array), confidence."
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

        target = str(parsed.get("target_audience", "")).strip()
        if not target:
            raise ValueError("AudienceAnalyst: missing required field 'target_audience'")

        objections = parsed.get("objections", [])
        if isinstance(objections, str):
            objections = [o.strip() for o in objections.split(";") if o.strip()]
        elif not isinstance(objections, list):
            objections = []
        else:
            objections = [str(o).strip() for o in objections if str(o).strip()]

        normalized: dict[str, Any] = {
            "target_audience": target,
            "emotional_state": str(parsed.get("emotional_state", "")).strip(),
            "desired_transformation": str(parsed.get("desired_transformation", "")).strip(),
            "objections": objections,
            "confidence": parsed.get("confidence", "unknown"),
        }
        return normalized

    def _summarize(self, result: dict[str, Any]) -> str:
        return (
            f"audience='{result.get('target_audience', '')[:60]}' "
            f"objections={len(result.get('objections', []))}"
        )