"""ThemeAnalyst — Extracts primary/secondary themes, symbolic motifs, psychological truth."""

from __future__ import annotations

import json
from typing import Any, TYPE_CHECKING

from movie_os.genesis.discovery.base import DiscoveryAgent
from movie_os.genesis.master_prompt import build_agent_prompt

if TYPE_CHECKING:
    from movie_os.genesis.pkg import ProductionKnowledgeGraph


class ThemeAnalyst(DiscoveryAgent):
    """Extracts the thematic structure of the story.

    Builds on the IntentAnalyst's output to surface the primary theme,
    secondary themes, recurring symbolic motifs, and the psychological
    truth the story is exploring. Themes drive both the symbolic layer
    (visual/aural motifs) and the character arcs.
    """

    name = "theme_analyst"
    analysis_key = "themes"

    def build_prompt(self, pkg: "ProductionKnowledgeGraph") -> str:
        instructions = (
            "Analyze the synopsis and extract: "
            "1) Primary theme, "
            "2) Secondary themes, "
            "3) Symbolic motifs, "
            "4) The psychological truth being explored. "
            "Respond with JSON containing: primary_theme, secondary_themes "
            "(array), motifs (array), psychological_truth, confidence."
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

        primary = str(parsed.get("primary_theme", "")).strip()
        if not primary:
            raise ValueError("ThemeAnalyst: missing required field 'primary_theme'")

        secondary = parsed.get("secondary_themes", [])
        if isinstance(secondary, str):
            secondary = [s.strip() for s in secondary.split(",") if s.strip()]
        elif not isinstance(secondary, list):
            secondary = []
        else:
            secondary = [str(s).strip() for s in secondary if str(s).strip()]

        motifs = parsed.get("motifs", [])
        if isinstance(motifs, str):
            motifs = [m.strip() for m in motifs.split(",") if m.strip()]
        elif not isinstance(motifs, list):
            motifs = []
        else:
            motifs = [str(m).strip() for m in motifs if str(m).strip()]

        normalized: dict[str, Any] = {
            "primary_theme": primary,
            "secondary_themes": secondary,
            "motifs": motifs,
            "psychological_truth": str(parsed.get("psychological_truth", "")).strip(),
            "confidence": parsed.get("confidence", "unknown"),
        }
        return normalized

    def _summarize(self, result: dict[str, Any]) -> str:
        return (
            f"primary='{result.get('primary_theme', '')[:80]}' "
            f"secondary={len(result.get('secondary_themes', []))} "
            f"motifs={len(result.get('motifs', []))}"
        )