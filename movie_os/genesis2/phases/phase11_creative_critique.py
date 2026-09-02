"""Phase 11: Creative Critique — provide creative feedback and improvement suggestions."""

from __future__ import annotations

import json
from typing import Any

from ..models import ConfidenceLevel, KnowledgeObject, ValidationIssue, CritiqueFinding as ModelCritiqueFinding, CreativeCritique as CritiqueKO
from ..phase_base import PhaseBase


class CreativeCritiquePhase(PhaseBase):
    phase_number = 11
    phase_name = "Creative Critique"
    _REQUIRED: list[str] = ["findings", "overall_assessment"]

    def build_draft_prompt(self, pkg: dict[str, Any]) -> str:
        previous_keys = [f"phase_{i:02d}" for i in range(1, 11)]
        prev = self.slice_context(pkg, previous_keys)
        return (
            f"# Phase 11: Creative Critique\n\n"
            f"Provide creative feedback on the full knowledge package.\n\n"
            f"## Knowledge Package\n{json.dumps(prev, indent=2, default=str)}\n\n"
            f"## Provide\n"
            f"- findings: array of observations with severity and recommendations\n"
            f"- overall_assessment: summary of creative quality\n"
            f"- recommended_actions: prioritized list of improvements\n\n"
            f'Respond with JSON: {{ "findings": [{{ "question": "", "answer": "", "severity": "critical|major|minor", "recommendation": "" }}], "overall_assessment": "", "recommended_actions": [] }}\n'
            f"Include purpose, creative_intent, reasoning, confidence."
        )

    def parse_draft(self, response: str | dict) -> KnowledgeObject:
        from ..llm_client import _extract_json
        data = response if isinstance(response, dict) else _extract_json(response)
        findings_data = data.get("findings", [])
        findings = []
        for f in findings_data:
            if hasattr(f, 'model_dump'):
                findings.append(f)
            elif isinstance(f, dict):
                sev = f.get("severity", "minor")
                q = f.get("question", "")
                a = f.get("answer", "")
                rec = f.get("recommendation", "")
                # Drop findings with no substantive content. The local model
                # sometimes emits a severity label with empty question/answer/
                # recommendation; an empty finding must not block freeze.
                if not (str(q).strip() or str(a).strip() or str(rec).strip()):
                    continue
                from ..models import CritiqueFinding
                findings.append(CritiqueFinding(question=q, answer=a, severity=sev, recommendation=rec))
            elif hasattr(f, 'question'):  # already a finding
                findings.append(f)
        from ..models import CreativeCritique
        return CreativeCritique(
            findings=findings,
            overall_assessment=data.get("overall_assessment", ""),
            recommended_actions=data.get("recommended_actions", []),
            purpose=data.get("purpose", ""), creative_intent=data.get("creative_intent", ""),
            reasoning=data.get("reasoning", ""), confidence=data.get("confidence", "inferred"),
        )

    def draft(self, pkg: dict[str, Any]) -> KnowledgeObject:
        prompt = self.build_draft_prompt(pkg)
        cfg = getattr(self.llm, "_config", None)
        from ..models import CreativeCritique
        response_format = CreativeCritique.model_json_schema()
        # The base schema marks findings/overall_assessment optional, so the
        # model can legally omit them. Require them so the structured-output
        # path forces the critique structure to be present.
        response_format["required"] = [
            "purpose", "creative_intent", "reasoning", "confidence",
            "findings", "overall_assessment", "recommended_actions",
        ]
        bounded_tokens = 1024
        if cfg is not None and hasattr(self.llm, "_get_provider"):
            try:
                from ..llm_providers import LLMConfig
                phase_cfg = LLMConfig(**cfg.model_dump()) if hasattr(cfg, "model_dump") else cfg
                bounded_tokens = min(int(getattr(phase_cfg, "max_tokens", 0) or 0), 1024) or 1024
                original_tokens = getattr(cfg, "max_tokens", bounded_tokens)
                cfg.max_tokens = bounded_tokens
                try:
                    response_obj = getattr(self.llm, "generate_json")(prompt, "planner", self.phase_name, self.phase_name, response_format=response_format)
                except TypeError:
                    response_obj = getattr(self.llm, "generate_json")(prompt, cfg, "planner")
                finally:
                    cfg.max_tokens = original_tokens
                response = response_obj
            except Exception:
                response = self.llm.generate(prompt, phase_name=self.phase_name, task_key=self.phase_name)
        else:
            response = self.llm.generate(prompt, phase_name=self.phase_name, task_key=self.phase_name)
        return self.parse_draft(response)

    def _review_specific(self, knowledge: KnowledgeObject) -> list[str]:
        issues: list[str] = []
        findings = getattr(knowledge, "findings", [])
        if not (isinstance(findings, list) and len(findings) > 0):
            issues.append("No findings provided — at least one critique finding expected")
        assessment = getattr(knowledge, "overall_assessment", None)
        if not (isinstance(assessment, str) and assessment.strip()):
            issues.append("Missing overall_assessment — required for creative feedback")
        return issues

    def _validate_specific(self, knowledge: KnowledgeObject) -> list[ValidationIssue]:  # noqa
        from ..models import ValidationIssue  # noqa
        issues: list[ValidationIssue] = []
        findings = getattr(knowledge, "findings", [])
        if isinstance(findings, list):
            valid_severities = {"critical", "major", "minor"}
            for i, finding in enumerate(findings):
                fdata = finding.model_dump() if hasattr(finding, 'model_dump') else {}
                sev = fdata.get("severity") if isinstance(fdata, dict) else getattr(finding, "severity", "")
                if isinstance(sev, str) and sev not in valid_severities:
                    issues.append(ValidationIssue(
                        category="schema_error", severity="warning",
                        location=f"{self.phase_name}.findings[{i}].severity",
                        description=f"Severity '{sev}' is not valid (use critical/major/minor)",
                    ))
        return issues
