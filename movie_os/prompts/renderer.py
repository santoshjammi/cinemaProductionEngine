"""PromptRenderer — the end of the prompt pipeline.

Pipeline: PromptTemplate → PromptBuilder → PromptOptimizer → PromptValidator → PromptRenderer

The Renderer takes a template + context and produces the final string
that's sent to the LLM. The Renderer's job is small — most of the
work is in the Template (structure), the Builder (context assembly),
the Optimizer (tuning), and the Validator (checking).
"""

from __future__ import annotations

import logging
from typing import Any

from movie_os.domain.prompt import PromptTemplate
from .builder import PromptBuilder
from .validator import PromptValidator


logger = logging.getLogger("movie_os.prompts.renderer")


class PromptRenderer:
    """Renders a PromptTemplate with a context.

    Combines the Builder + Validator in one call. The output is
    either the rendered prompt (if validation passed) or raises
    an error with details.
    """

    def __init__(self, template: PromptTemplate):
        self.template = template
        self.builder = PromptBuilder(template)
        self.validator = PromptValidator(template)

    def render(
        self,
        context: dict[str, Any],
        *,
        raise_on_fail: bool = True,
    ) -> tuple[str, Any]:
        """Render the template with the given context.

        Args:
            context: The context dict (variable values).
            raise_on_fail: If True, raise ValueError when validation fails.
                If False, return the rendered prompt with the validation
                result as the second element.

        Returns:
            A tuple of (rendered_prompt, validation_result).
        """
        rendered = self.template.render(context)
        validation = self.validator.validate(rendered, context)

        if not validation.passed and raise_on_fail:
            raise ValueError(
                f"Prompt validation failed: {validation.issues}"
            )

        return rendered, validation

    def render_from_scene(
        self,
        scene,
        characters: dict | None = None,
        extra: dict[str, Any] | None = None,
        raise_on_fail: bool = True,
    ) -> tuple[str, Any]:
        """Convenience: build context from a Scene, then render."""
        context = self.builder.build_from_scene(scene, characters, extra)
        return self.render(context, raise_on_fail=raise_on_fail)
