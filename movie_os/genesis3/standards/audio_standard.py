"""Audio Standards."""
from __future__ import annotations
from typing import Any
from .base import Standard, QualityCriterion, ValidationRule, StandardResult


class AudioStandard(Standard):
    name = "audio"
    purpose = "Sound design, ambient audio, Foley quality."
    principles = ["Objective quality criteria for audio dimension."]
    criteria = [
        QualityCriterion(name="sound_design", description="Quality check for sound_design", weight=0.25),
        QualityCriterion(name="ambient_audio", description="Quality check for ambient_audio", weight=0.25),
        QualityCriterion(name="foley_quality", description="Quality check for foley_quality", weight=0.25),
        QualityCriterion(name="audio_clarity", description="Quality check for audio_clarity", weight=0.25),
    ]
    validation_rules = [
        ValidationRule(rule_id="audio-001", description="Validate audio quality", evaluator="heuristic"),
    ]
    failure_conditions = ["sound_design fails to meet minimum threshold", "ambient_audio fails to meet minimum threshold", "foley_quality fails to meet minimum threshold", "audio_clarity fails to meet minimum threshold"]
    required_evidence = ["sound_design_evidence", "ambient_audio_evidence", "foley_quality_evidence", "audio_clarity_evidence"]
    certification_threshold = 0.7

    def evaluate(self, evidence: dict[str, Any]) -> StandardResult:
        data = evidence.get("audio", {})
        checks = []
        for cn in self.criteria:
            key = cn.name
            val = data.get(key, data.get(key + "_score", 0.5))
            if isinstance(val, bool):
                checks.append((self._score_from_bool(val), cn.weight))
            elif isinstance(val, (int, float)):
                checks.append((min(val, 1.0), cn.weight))
            else:
                checks.append((0.5, cn.weight))
        score = self._weighted_score(checks)
        failures = [c.name for c, (s, _) in zip(self.criteria, checks) if s < 0.5]
        return StandardResult(
            standard_name=self.name,
            passed=score >= self.certification_threshold,
            score=round(score, 4),
            evidence=[f"score={score:.2f}"],
            failures=failures,
            details=f"{{len(failures)}} failure(s) out of {len(self.criteria)} criteria",
        )
