"""StoryCapability — generates story content (DNA, context, scenes).

This is where the story generation LLM lives. The capability dispatches
to a StoryProvider (LMStudio, OpenAI, Anthropic, local models). The
provider chooses the model, temperature, and prompt format.

For Phase 0, this is a stub. The implementation comes in Phase 4.
"""

from __future__ import annotations

import logging

from .base import (
    Capability,
    StoryCapabilityError,
    StoryIntent,
    StoryResult,
)


logger = logging.getLogger("movie_os.capabilities.story")


class StoryCapability(Capability[StoryIntent, StoryResult]):
    """Generate story content — DNA, context, narrative, scene structure."""

    name = "story"
    description = "Generate story content via an LLM (DNA, context, narrative, scenes)."
    version = "0.1.0"

    def __init__(self, provider=None):
        self._provider = provider

    def can_handle(self, intent: StoryIntent) -> bool:
        return bool(intent.task)

    async def execute(self, intent: StoryIntent) -> StoryResult:
        if not intent.task:
            raise StoryCapabilityError("StoryIntent.task is required")
        if self._provider is not None and hasattr(self._provider, "render"):
            return await self._provider.render(intent)
        raise NotImplementedError(
            "StoryCapability is a stub in Phase 0. "
            "Implementation lands in Phase 4 (wrap existing story_factory)."
        )
