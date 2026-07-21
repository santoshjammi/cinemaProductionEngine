"""AudioIntentAgent — generates PKP-12 Audio Intent Specification."""

from __future__ import annotations
from typing import Any, TYPE_CHECKING
from movie_os.genesis.pkp_agents.base import PKPAgent
from movie_os.genesis.master_prompt import build_agent_prompt

if TYPE_CHECKING:
    from movie_os.genesis.pkg import ProductionKnowledgeGraph


class AudioIntentAgent(PKPAgent):
    name = "audio_intent_agent"
    spec_id = "PKP-12"
    spec_name = "Audio Intent Specification"
    phase = "E"
    expected_keys: list[str] = ["sonic_palette", "music_philosophy", "score_motifs", "diegetic_sound", "dialogue_treatment", "audio_arc"]
    dependencies = ["PKP-09"]

    def build_prompt(self, pkg: "ProductionKnowledgeGraph") -> str:
        return build_agent_prompt(
            agent_name=self.name,
            agent_instructions=(
                "Generate the Audio Intent Specification. Define: sonic palette, music "
                "philosophy, score themes and motifs, diegetic sound design, ambient sound "
                "layers, dialogue treatment intent, silence strategy, and emotional audio "
                "arc. Express narrative intent as sound, not yet as finalized cues. "
                "Respond with JSON containing these fields plus a confidence field."
            ),
            synopsis=pkg.synopsis,
            context=self.get_dependency_content(pkg),
            constraints=pkg.constraints,
        )

    def parse_response(self, response: str, pkg: "ProductionKnowledgeGraph") -> dict[str, Any]:
        from movie_os.genesis.llm_client import LLMClient
        return LLMClient._extract_json(response)

    def validate(self, content: dict[str, Any], pkg: "ProductionKnowledgeGraph") -> list[str]:
        errors = super().validate(content, pkg)
        required = ["sonic_palette", "music_philosophy", "score_motifs",
                    "diegetic_sound", "dialogue_treatment", "audio_arc"]
        for field in required:
            if field not in content:
                errors.append(f"Missing required field: {field}")
        return errors