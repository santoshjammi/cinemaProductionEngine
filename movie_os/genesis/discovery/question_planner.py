"""QuestionPlanner — Generates targeted questions only for critical unknowns with confidence < 60%."""

from __future__ import annotations

import json
from typing import Any, TYPE_CHECKING

from movie_os.genesis.discovery.base import DiscoveryAgent
from movie_os.genesis.master_prompt import build_agent_prompt

if TYPE_CHECKING:
    from movie_os.genesis.pkg import ProductionKnowledgeGraph


class QuestionPlanner(DiscoveryAgent):
    """Generates targeted questions for the human collaborator.

    Consumes the GapAnalyst's critical_gaps and emits questions ONLY for
    critical unknowns where confidence < 60%. Each question carries the
    question text, why it matters (downstream decisions that depend on
    it), the current confidence percentage, and a suggested default.
    If no critical unknowns exist, returns an empty questions array so
    the pipeline can proceed without blocking on the human.
    """

    name = "question_planner"
    analysis_key = "questions"

    def build_prompt(self, pkg: "ProductionKnowledgeGraph") -> str:
        instructions = (
            "Based on the knowledge gaps identified, generate questions ONLY "
            "for critical unknowns where confidence < 60%. Each question must "
            "include: 1) The question text, 2) Why it matters (what decisions "
            "depend on it), 3) Current confidence percentage, 4) A suggested "
            "default value. If no critical unknowns exist, return an empty "
            "questions array. Respond with JSON containing: questions (array "
            "of {question, why_it_matters, confidence_pct, suggested_default}), "
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

        raw_questions = parsed.get("questions", [])
        if not isinstance(raw_questions, list):
            raw_questions = []

        questions: list[dict[str, Any]] = []
        for q in raw_questions:
            if not isinstance(q, dict):
                continue
            text = str(q.get("question", "")).strip()
            if not text:
                continue
            try:
                confidence_pct = float(q.get("confidence_pct", 0))
            except (TypeError, ValueError):
                confidence_pct = 0.0
            questions.append(
                {
                    "question": text,
                    "why_it_matters": str(q.get("why_it_matters", "")).strip(),
                    "confidence_pct": confidence_pct,
                    "suggested_default": str(q.get("suggested_default", "")).strip(),
                }
            )

        normalized: dict[str, Any] = {
            "questions": questions,
            "confidence": parsed.get("confidence", "unknown"),
        }
        return normalized

    def _summarize(self, result: dict[str, Any]) -> str:
        return f"questions={len(result.get('questions', []))}"