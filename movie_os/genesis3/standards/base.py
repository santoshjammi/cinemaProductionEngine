"""Base models for the GENESIS Standards Framework."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Literal
from pydantic import BaseModel, Field


class QualityCriterion(BaseModel):
    name: str
    description: str
    weight: float = Field(ge=0.0, le=1.0, default=0.25)
    evaluator_type: str = "heuristic"


class ValidationRule(BaseModel):
    rule_id: str
    description: str
    evaluator: str
    severity: Literal["critical", "major", "minor"] = "major"


class StandardResult(BaseModel):
    standard_name: str
    passed: bool
    score: float = Field(ge=0.0, le=1.0)
    evidence: list[str] = Field(default_factory=list)
    failures: list[str] = Field(default_factory=list)
    details: str = ""


class Standard(ABC):
    name: str
    purpose: str
    principles: list[str]
    criteria: list[QualityCriterion]
    validation_rules: list[ValidationRule]
    failure_conditions: list[str]
    required_evidence: list[str]
    certification_threshold: float = 0.7

    @abstractmethod
    def evaluate(self, evidence: dict[str, Any]) -> StandardResult:
        pass

    def _score_from_bool(self, value: bool) -> float:
        return 1.0 if value else 0.0

    def _weighted_score(self, scores: list[tuple[float, float]]) -> float:
        total = sum(s * w for s, w in scores)
        weight_sum = sum(w for _, w in scores)
        return total / weight_sum if weight_sum > 0 else 0.0
