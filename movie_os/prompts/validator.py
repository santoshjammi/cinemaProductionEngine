"""PromptValidator — checks that a rendered prompt satisfies constraints.

For Phase 0, the validator does basic checks:
  - all required variables are present
  - the rendered text respects constraints (e.g., "max 50 words")
  - the negative_prompts are applied (warn if the prompt body contains them)

Future: semantic validation, model-specific checks, history-aware validation.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any

from movie_os.domain.prompt import PromptTemplate


logger = logging.getLogger("movie_os.prompts.validator")


@dataclass
class ValidationResult:
    """The result of validating a rendered prompt."""
    passed: bool
    issues: list[str]
    warnings: list[str]

    def __bool__(self) -> bool:
        return self.passed


class PromptValidator:
    """Validates a rendered prompt against the template's constraints."""

    def __init__(self, template: PromptTemplate):
        self.template = template

    def validate(self, rendered: str, context: dict[str, Any] | None = None) -> ValidationResult:
        """Validate the rendered prompt.

        Args:
            rendered: The final prompt string.
            context: The context that was used to render (for variable checks).

        Returns:
            A ValidationResult with passed/issues/warnings.
        """
        issues: list[str] = []
        warnings: list[str] = []

        # Check that all required variables were provided
        if context is not None:
            for var in self.template.variables:
                if var.required and var.name not in context:
                    issues.append(f"Missing required variable: {var.name}")

        # Check constraints
        for constraint in self.template.constraints:
            if self._check_constraint(constraint, rendered):
                continue
            if constraint.severity == "must":
                issues.append(f"Failed MUST constraint: {constraint.rule}")
            elif constraint.severity == "should":
                warnings.append(f"Failed SHOULD constraint: {constraint.rule}")
            # "may" failures are just info, not a warning

        # Check that the prompt doesn't contain the negative prompts
        rendered_lower = rendered.lower()
        for neg in self.template.negative_prompts:
            # Check for whole-word matches (avoid false positives like "no" in "not")
            pattern = r"\b" + re.escape(neg.lower()) + r"\b"
            if re.search(pattern, rendered_lower):
                warnings.append(f"Prompt contains negative term: '{neg}'")

        return ValidationResult(
            passed=len(issues) == 0,
            issues=issues,
            warnings=warnings,
        )

    def _check_constraint(self, constraint, rendered: str) -> bool:
        """Check a single constraint against the rendered prompt.

        Supports a few built-in constraint patterns:
          - "Maximum N words" / "Minimum N words"
          - "Maximum N characters"
        """
        rule = constraint.rule.lower()
        if rule.startswith("maximum ") and "word" in rule:
            n = self._extract_number(rule)
            if n is not None and len(rendered.split()) > n:
                return False
        elif rule.startswith("minimum ") and "word" in rule:
            n = self._extract_number(rule)
            if n is not None and len(rendered.split()) < n:
                return False
        elif rule.startswith("maximum ") and "char" in rule:
            n = self._extract_number(rule)
            if n is not None and len(rendered) > n:
                return False
        # Unknown constraint — assume pass
        return True

    def _extract_number(self, text: str) -> int | None:
        import re
        m = re.search(r"\d+", text)
        return int(m.group(0)) if m else None
