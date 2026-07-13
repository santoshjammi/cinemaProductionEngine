"""LMStudio Story Provider — wraps the story_factory's chat() function.

This is the default story generation provider. It uses LMStudio
(local LLM server) to generate story content via the story_factory
agents: DNA, context, narrative, scenes.

The provider is a thin wrapper that:
  1. Maps the StoryIntent.task to the right story_factory function
  2. Passes the parameters
  3. Returns a StoryResult with the content
"""

from __future__ import annotations

import logging
from typing import Any

from movie_os.capabilities.base import StoryIntent, StoryResult
from movie_os.domain.asset import RenderBackend
from movie_os.providers.base import StoryProvider, run_sync


logger = logging.getLogger("movie_os.providers.story.lmstudio")


# Map task names to story_factory functions
_TASK_FUNCTIONS = {
    "dna": "_call_dna",
    "context": "_call_context",
    "narrative": "_call_narrative",
    "scenes": "_call_scenes",
}


class LMStudioStoryProvider(StoryProvider):
    """Story generation via LMStudio (local LLM)."""

    name = "lmstudio"
    backend = RenderBackend.UNKNOWN  # story isn't a model-specific asset

    def __init__(
        self,
        base_url: str = "http://localhost:1234",
        api_key: str = "sk-lm-TkM3NqaZ:CQdNsDjxGRm17O3Gg59W",
        narrative_model: str = "qwen3-coder-30b-a3b-instruct-mlx",
        narrative_temperature: float = 0.7,
        narrative_max_tokens: int = 4000,
        refiner_model: str = "supergemma4-26b-uncensored-mlx-v2",
        refiner_temperature: float = 0.6,
        refiner_max_tokens: int = 2000,
    ):
        self.base_url = base_url
        self.api_key = api_key
        self.narrative_model = narrative_model
        self.narrative_temperature = narrative_temperature
        self.narrative_max_tokens = narrative_max_tokens
        self.refiner_model = refiner_model
        self.refiner_temperature = refiner_temperature
        self.refiner_max_tokens = refiner_max_tokens

    async def render(self, intent: StoryIntent) -> StoryResult:
        """Generate story content based on the task in the intent."""
        if not intent.task:
            raise ValueError("StoryIntent.task is required")

        if intent.task not in _TASK_FUNCTIONS:
            raise ValueError(
                f"Unknown story task: {intent.task}. "
                f"Valid: {list(_TASK_FUNCTIONS.keys())}"
            )

        method_name = _TASK_FUNCTIONS[intent.task]
        method = getattr(self, method_name)
        return await run_sync(method, intent)

    def _call_dna(self, intent: StoryIntent) -> StoryResult:
        """Generate Story DNA from a synopsis."""
        from story_factory import generate_dna
        dna = generate_dna(
            intent.synopsis,
            base_url=self.base_url,
            api_key=self.api_key,
            temperature=self.narrative_temperature,
            max_tokens=2000,
        )
        return StoryResult(content=dna, task="dna")

    def _call_context(self, intent: StoryIntent) -> StoryResult:
        """Generate context from a synopsis."""
        from story_factory import generate_context
        context = generate_context(
            intent.synopsis,
            base_url=self.base_url,
            api_key=self.api_key,
            temperature=self.narrative_temperature,
            max_tokens=2000,
        )
        return StoryResult(content=context, task="context")

    def _call_narrative(self, intent: StoryIntent) -> StoryResult:
        """Generate the story narrative from DNA + context."""
        from story_factory import generate_story
        story = generate_story(
            intent.synopsis,
            intent.dna,
            intent.context,
            base_url=self.base_url,
            api_key=self.api_key,
            temperature=self.narrative_temperature,
            max_tokens=self.narrative_max_tokens,
        )
        return StoryResult(content=story, task="narrative")

    def _call_scenes(self, intent: StoryIntent) -> StoryResult:
        """Structure the story into a Master Timeline."""
        from story_factory import structure_scenes
        timeline = structure_scenes(
            intent.dna,
            intent.context,
            intent.story,
            base_url=self.base_url,
            api_key=self.api_key,
            temperature=0.3,
            max_tokens=5000,
        )
        return StoryResult(content=timeline, task="scenes")

    def can_handle(self, intent: StoryIntent) -> bool:
        return bool(intent.task) and intent.task in _TASK_FUNCTIONS


def make(settings: dict, cost_per_call_usd: float = 0.0) -> LMStudioStoryProvider:
    """Build an LMStudioStoryProvider from config settings."""
    return LMStudioStoryProvider(
        base_url=settings.get("base_url", "http://localhost:1234"),
        api_key=settings.get("api_key", "sk-lm-TkM3NqaZ:CQdNsDjxGRm17O3Gg59W"),
        narrative_model=settings.get("narrative_model", "qwen3-coder-30b-a3b-instruct-mlx"),
        narrative_temperature=settings.get("narrative_temperature", 0.7),
        narrative_max_tokens=settings.get("narrative_max_tokens", 4000),
        refiner_model=settings.get("refiner_model", "supergemma4-26b-uncensored-mlx-v2"),
        refiner_temperature=settings.get("refiner_temperature", 0.6),
        refiner_max_tokens=settings.get("refiner_max_tokens", 2000),
    )
