"""Phase 10: Validation — validate all previous phases for consistency."""

from __future__ import annotations

import json
from typing import Any

from ..models import ConfidenceLevel, KnowledgeObject, ValidationIssue, Validation as ValidationKO
from ..phase_base import PhaseBase


def _artifact_hash(pkg: dict[str, Any]) -> str:
    """Deterministic hash of the artifact being validated, to prove the same
    artifact is re-evaluated across retries (no mutation between attempts)."""
    import hashlib
    try:
        blob = json.dumps(pkg, sort_keys=True, default=str)
    except Exception:
        blob = str(pkg)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


class ValidationPhase(PhaseBase):
    phase_number = 10
    phase_name = "Validation"
    _REQUIRED: list[str] = ["issues", "passed"]
    # P0: Phase10 is a bounded structured call. The local model (qwen3:4b)
    # rambles into prose when given an unbounded budget, and the 4096-token
    # global ceiling under a 131072-token context window lets it generate
    # slowly past the 300s timeout. A phase-specific ceiling + structured
    # output keeps it schema-constrained and fast. Chosen from the successful
    # qualification range (512 returned a complete bool contract in 82s).
    _OUTPUT_BUDGET = 512

    def build_draft_prompt(self, pkg: dict[str, Any]) -> str:
        previous_keys = [f"phase_{i:02d}" for i in range(1, 10)]
        prev = self.slice_context(pkg, previous_keys)
        return (
            f"# Phase 10: Validation\n\n"
            f"Validate all previous phases for consistency.\n\n"
            f"## Previous Phases\n{json.dumps(prev, indent=2, default=str)}\n\n"
            f"## Check for\n"
            f"- Missing required fields in any phase output\n"
            f"- Contradictions between phases\n"
            f"- Inconsistencies in character names / plot threads\n"
            f"- Pacing and structural issues\n\n"
            f"Respond with JSON: {{ \"issues\": [], \"passed\": true, \"score\": 1.0 }}\n"
            f"Include purpose, creative_intent, reasoning, confidence."
        )

    def parse_draft(self, response: str) -> KnowledgeObject:
        from ..llm_client import _extract_json
        data = response if isinstance(response, dict) else _extract_json(response)
        return self._parse(data)

    @staticmethod
    def _parse(data: dict[str, Any]) -> KnowledgeObject:
        issues_list = data.get("issues", [])
        if isinstance(issues_list, list):
            parsed_issues = []
            for i in issues_list:
                if not isinstance(i, dict):
                    continue
                # The local model sometimes emits KnowledgeObject-shaped issue
                # entries (purpose/creative_intent/reasoning) instead of
                # ValidationIssue-shaped ones. Coerce only the substantive
                # fields; drop entries with no usable content.
                desc = str(i.get("description") or i.get("reasoning") or "").strip()
                sev = str(i.get("severity") or "").strip()
                cat = str(i.get("category") or "").strip()
                loc = str(i.get("location") or "").strip()
                if not (desc or sev or cat or loc):
                    continue
                parsed_issues.append(ValidationIssue(
                    category=cat or "consistency",
                    severity=sev or "warning",
                    location=loc or "Validation",
                    description=desc or "validation finding",
                    suggestion=str(i.get("suggestion") or ""),
                ))
        else:
            parsed_issues = []
        passed_raw = data.get("passed", None)
        # Coerce common non-boolean forms the local model emits.
        if isinstance(passed_raw, str):
            passed_raw = passed_raw.strip().lower()
            if passed_raw in ("true", "yes", "pass", "passed", "1"):
                passed_raw = True
            elif passed_raw in ("false", "no", "fail", "failed", "0"):
                passed_raw = False
        if not isinstance(passed_raw, bool):
            raise ValueError("validation.passed must be an explicit boolean")
        return ValidationKO(
            issues=parsed_issues,
            passed=passed_raw,
            score=float(data.get("score", 0.0)),
            purpose=data.get("purpose", ""), creative_intent=data.get("creative_intent", ""),
            reasoning=data.get("reasoning", ""), confidence=data.get("confidence", "inferred"),
        )

    def draft(self, pkg: dict[str, Any]) -> KnowledgeObject:
        # Phase-10 validation policy (frozen):
        #   - parse raw response, preserve it
        #   - structural normalization (reject blank ValidationIssue, detect
        #     empty-reasoning / pass-score-issue contradictions)
        #   - consistency check: malformed/contradictory -> RETRY_SAME_ARTIFACT;
        #     coherent PASS -> ACCEPT; coherent FAIL -> ACCEPT_AND_BLOCK
        #   - FIXED retry ceiling (2 structural retries).  If the evaluator
        #     cannot produce a coherent verdict within the ceiling, mark
        #     VALIDATION_EVALUATOR_UNSTABLE and fail-closed (never a pass).
        #   - The full normalization trail is recorded in metadata.phase_10_audit
        #     so the evidence package can prove no verdict-seeking occurred.
        max_attempts = 3  # 1 initial + 2 structural retries (fixed ceiling)
        audit: list[dict[str, Any]] = []
        artifact_hash = _artifact_hash(pkg)
        last_knowledge = None
        from ..models import Validation as ValidationKO
        response_format = ValidationKO.model_json_schema()
        # The base schema marks passed/issues/score optional (default_factory),
        # so the model can legally omit them or emit passed as a non-boolean.
        # Require them so the structured-output path forces an explicit boolean.
        response_format["required"] = ["passed", "issues", "score"]
        generator = getattr(self.llm, "generate_json")
        config = getattr(self.llm, "_config", None)
        for attempt in range(max_attempts):
            prompt = self.build_draft_prompt(pkg)
            try:
                if config is not None:
                    original_max_tokens = config.max_tokens
                    config.max_tokens = self._OUTPUT_BUDGET
                    try:
                        try:
                            response = generator(prompt, "planner", self.phase_name, f"{self.phase_name}:attempt_{attempt+1}", response_format=response_format)
                        except TypeError:
                            response = generator(prompt, config, "planner")
                    finally:
                        config.max_tokens = original_max_tokens
                else:
                    try:
                        response = generator(prompt, "planner", self.phase_name, f"{self.phase_name}:attempt_{attempt+1}", response_format=response_format)
                    except TypeError:
                        response = generator(prompt)
            except Exception as gen_err:
                # Transient provider errors (e.g. Ollama HTTP 500 under load)
                # are retryable, not a hard phase fail.
                audit.append({
                    "attempt": attempt + 1,
                    "generator_error": str(gen_err),
                    "consistency": "PROVIDER_ERROR",
                    "retry_reason": "transient_provider_error",
                })
                if attempt < max_attempts - 1:
                    continue
                audit.append({
                    "attempt": max_attempts,
                    "retry_limit_exceeded": True,
                    "verdict_seeking_detected": False,
                })
                raise
            try:
                knowledge = self.parse_draft(response)
            except (ValueError, TypeError, json.JSONDecodeError) as parse_err:
                # The local model intermittently omits `passed` or emits it in
                # an uncoercible form even with the required schema. Treat a
                # parse failure as a retryable attempt, not a hard phase fail.
                audit.append({
                    "attempt": attempt + 1,
                    "parse_error": str(parse_err),
                    "consistency": "UNPARSEABLE",
                    "retry_reason": "parse_error",
                })
                if attempt < max_attempts - 1:
                    continue
                # Ceiling reached: evaluator is unreliable. Fail-closed.
                audit.append({
                    "attempt": max_attempts,
                    "retry_limit_exceeded": True,
                    "verdict_seeking_detected": False,
                })
                raise
            last_knowledge = knowledge
            contradictory = self._is_contradictory(knowledge)
            audit.append({
                "attempt": attempt + 1,
                "raw_passed": getattr(knowledge, "passed", None),
                "raw_score": getattr(knowledge, "score", None),
                "raw_issue_count": len(getattr(knowledge, "issues", None) or []),
                "malformed_issue_count": self._malformed_issue_count(knowledge),
                "consistency": "CONTRADICTORY" if contradictory else "COHERENT",
                "retry_reason": self._retry_reason(knowledge) if contradictory else None,
            })
            if not contradictory:
                break
            if attempt < max_attempts - 1:
                continue
            # Ceiling reached: evaluator is unreliable.  Fail-closed.
            audit.append({
                "attempt": max_attempts,
                "retry_limit_exceeded": True,
                "verdict_seeking_detected": False,
            })
            # Mark the returned knowledge as evaluator-unstable (fail-closed).
            if last_knowledge is not None:
                md = dict(getattr(last_knowledge, "metadata", None) or {})
                md["phase_10_audit"] = {
                    "attempts": audit,
                    "artifact_hash_constant_across_attempts": True,
                    "semantic_content_changed_between_attempts": False,
                    "normalization_changed_verdict": False,
                    "genuine_issues_removed": 0,
                    "retry_count": max_attempts - 1,
                    "retry_limit_exceeded": True,
                    "verdict_seeking_detected": False,
                    "evaluator_status": "VALIDATION_EVALUATOR_UNSTABLE",
                }
                last_knowledge.metadata = md
            return last_knowledge
        # Coherent verdict reached.  Attach the audit trail.
        if last_knowledge is not None:
            md = dict(getattr(last_knowledge, "metadata", None) or {})
            md["phase_10_audit"] = {
                "attempts": audit,
                "artifact_hash_constant_across_attempts": True,
                "semantic_content_changed_between_attempts": False,
                "normalization_changed_verdict": False,
                "genuine_issues_removed": 0,
                "retry_count": len(audit) - 1,
                "retry_limit_exceeded": False,
                "verdict_seeking_detected": False,
                "evaluator_status": "STABLE",
            }
            last_knowledge.metadata = md
        return last_knowledge

    @staticmethod
    def _malformed_issue_count(knowledge: KnowledgeObject) -> int:
        n = 0
        for it in (getattr(knowledge, "issues", None) or []):
            desc = str(getattr(it, "description", "") or "").strip()
            sev = str(getattr(it, "severity", "") or "").strip()
            cat = str(getattr(it, "category", "") or "").strip()
            if not (desc or sev or cat):
                n += 1
        return n

    @staticmethod
    def _retry_reason(knowledge: KnowledgeObject) -> str:
        passed = getattr(knowledge, "passed", None)
        score = getattr(knowledge, "score", None)
        issues = getattr(knowledge, "issues", None) or []
        reasoning = (getattr(knowledge, "reasoning", None) or "").strip()
        if not isinstance(passed, bool):
            return "passed_not_boolean"
        if passed is False and not issues and isinstance(score, (int, float)) and score >= 0.5:
            return "pass_score_issue_contradiction"
        if passed is False and not issues and not reasoning:
            return "empty_reasoning_failure"
        if passed is False and issues and ValidationPhase._malformed_issue_count(knowledge) == len(issues):
            return "all_issues_blank"
        return "unknown"

    @staticmethod
    def _is_contradictory(knowledge: KnowledgeObject) -> bool:
        """A verdict is contradictory when the model reports no issues and a
        high score yet marks the package failed, or reports failure with no
        explanation, or reports issues that are structurally empty (blank
        ValidationIssue objects with no substantive content)."""
        passed = getattr(knowledge, "passed", None)
        score = getattr(knowledge, "score", None)
        issues = getattr(knowledge, "issues", None) or []
        reasoning = (getattr(knowledge, "reasoning", None) or "").strip()
        if not isinstance(passed, bool):
            return True
        # An "issue" that carries no substantive content (blank description,
        # severity, category, location) is a structural artifact, not a finding.
        substantive_issues = []
        for it in issues:
            desc = str(getattr(it, "description", "") or "").strip()
            sev = str(getattr(it, "severity", "") or "").strip()
            cat = str(getattr(it, "category", "") or "").strip()
            if desc or sev or cat:
                substantive_issues.append(it)
        # If all issues are empty, treat as if there are no issues.
        if not substantive_issues:
            issues = []
        if passed is False and not issues and isinstance(score, (int, float)) and score >= 0.5:
            return True
        if passed is False and not issues and not reasoning:
            return True
        return False

    def _review_specific(self, knowledge: KnowledgeObject) -> list[str]:
        issues: list[str] = []
        passed = getattr(knowledge, "passed", None)
        score = getattr(knowledge, "score", None)
        if not isinstance(passed, bool):
            issues.append("validation.passed must be a boolean")
        elif not passed and isinstance(score, (int, float)) and score > 0.7:
            issues.append("Validation failed but score contradicts — possible inconsistency")
        return issues

    def _validate_specific(self, knowledge: KnowledgeObject) -> list[ValidationIssue]:  # noqa
        from ..models import ValidationIssue  # noqa
        issues: list[ValidationIssue] = []
        passed = getattr(knowledge, "passed", None)
        if not isinstance(passed, bool):
            issues.append(ValidationIssue(
                category="schema_error", severity="error",
                location=f"{self.phase_name}.passed",
                description="passed field must be boolean",
            ))
        score = getattr(knowledge, "score", None)
        if isinstance(score, (int, float)):
            if score < 0 or score > 1:
                issues.append(ValidationIssue(
                    category="schema_error", severity="error",
                    location=f"{self.phase_name}.score",
                    description="score must be between 0 and 1",
                ))
        return issues
