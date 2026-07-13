"""PromptTemplate — the structured prompt format.

A prompt is not a string. It's a structured document with:

  - metadata: id, version, author, supported_models, temperature
  - variables: the placeholders that get filled with context
  - constraints: rules the LLM should follow (e.g., "max 30 words")
  - examples: few-shot examples for the LLM
  - negative_prompts: what to avoid
  - the body: the actual prompt template (with {{variable}} placeholders)

The PromptTemplate is the source of truth. The PromptBuilder injects
context, the PromptOptimizer tunes it, the PromptValidator checks it,
and the PromptRenderer produces the final string.
"""

from __future__ import annotations

from datetime import date
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PromptRole(str, Enum):
    """The role this prompt plays in the pipeline."""
    SYSTEM = "system"                  # system message
    USER = "user"                      # user message
    IMAGE = "image"                    # image generation prompt
    NEGATIVE = "negative"              # negative prompt
    METADATA = "metadata"              # metadata extraction prompt
    TRANSLATION = "translation"        # translation prompt
    STRUCTURED = "structured"          # structured output (JSON/YAML)


# ---------------------------------------------------------------------------
# Variable — a placeholder in the prompt body
# ---------------------------------------------------------------------------

class VariableType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"
    ENUM = "enum"


class Variable(BaseModel):
    """A placeholder in the prompt body, e.g., {{character_name}}."""
    name: str                                          # the placeholder name (without braces)
    type: VariableType = VariableType.STRING
    required: bool = True
    description: str = ""
    default: Any = None
    enum_values: list[str] = Field(default_factory=list)  # for ENUM type
    constraints: dict[str, Any] = Field(default_factory=dict)  # min, max, regex, etc.


# ---------------------------------------------------------------------------
# Constraint — a rule the prompt must follow
# ---------------------------------------------------------------------------

class Constraint(BaseModel):
    """A rule the LLM should follow when using this prompt."""
    rule: str                                          # "Maximum 30 words"
    severity: str = "must"                             # "must", "should", "may"
    examples_pass: list[str] = Field(default_factory=list)   # examples that satisfy
    examples_fail: list[str] = Field(default_factory=list)   # examples that violate


# ---------------------------------------------------------------------------
# Example — few-shot
# ---------------------------------------------------------------------------

class Example(BaseModel):
    """A few-shot example."""
    description: str = ""
    input: dict[str, Any] = Field(default_factory=dict)       # variable values
    output: str = ""                                          # expected output


# ---------------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------------

class PromptMetadata(BaseModel):
    """Describes the prompt — for discovery, versioning, model selection."""
    id: str                                            # unique ID, e.g., "image.cinematic.v3"
    version: str = "1.0.0"                             # semver
    author: str = ""
    created_at: date = Field(default_factory=date.today)
    description: str = ""
    role: PromptRole = PromptRole.IMAGE
    capability: str = ""                               # "image", "story", "voice", etc.
    tags: list[str] = Field(default_factory=list)

    # Model compatibility
    supported_models: list[str] = Field(default_factory=list)  # ["flux-dev", "sdxl", "sd3"]
    recommended_temperature: float = 0.7
    recommended_max_tokens: int = 1000

    # Cost
    avg_tokens: int = 0
    avg_cost_usd: float = 0.0

    # History
    changelog: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# PromptTemplate — the whole thing
# ---------------------------------------------------------------------------

class PromptTemplate(BaseModel):
    """A structured prompt — the unit of prompt engineering in the Movie OS."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    metadata: PromptMetadata
    variables: list[Variable] = Field(default_factory=list)
    constraints: list[Constraint] = Field(default_factory=list)
    examples: list[Example] = Field(default_factory=list)
    negative_prompts: list[str] = Field(default_factory=list)

    # The actual prompt body — uses {{variable}} placeholders
    body: str = ""

    @field_validator("body")
    @classmethod
    def _validate_body_has_no_undeclared_vars(cls, v: str, info) -> str:
        """Check that every {{var}} in the body is declared in variables."""
        # Find all {{...}} placeholders
        import re
        declared = {var.name for var in info.data.get("variables", [])}
        used = set(re.findall(r"\{\{(\w+)\}\}", v))
        undeclared = used - declared
        if undeclared:
            raise ValueError(
                f"Prompt body uses undeclared variables: {undeclared}. "
                f"Add them to the variables list or fix the body."
            )
        return v

    def render(self, context: dict[str, Any]) -> str:
        """Render the prompt body with the given context.

        Replaces {{variable}} placeholders with values from context.
        If a variable has a default and is not in context, the default
        is used. Missing required variables (with no default) raise an error.
        """
        import re

        # Build a resolved context: explicit values win, then defaults
        resolved = dict(context)
        for var in self.variables:
            if var.name not in resolved and var.default is not None:
                resolved[var.name] = var.default

        # Validate that all required variables are now resolved
        for var in self.variables:
            if var.required and var.name not in resolved:
                raise ValueError(f"Missing required variable: {var.name}")

        def _replace(match: re.Match) -> str:
            name = match.group(1)
            if name not in resolved:
                return match.group(0)  # leave unchanged
            value = resolved[name]
            if isinstance(value, list):
                return ", ".join(str(v) for v in value)
            if isinstance(value, dict):
                return str(value)
            return str(value)

        return re.sub(r"\{\{(\w+)\}\}", _replace, self.body)
