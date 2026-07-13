"""ResearchCapability — gathers context from the web (DuckDuckGo, Wikipedia).

This is the entry point for the new "Research" stage of the pipeline
(per the enhancement doc). For Phase 0, this is a stub. Implementation
lands in a later phase.
"""

from __future__ import annotations

import logging

from .base import (
    Capability,
    ResearchCapabilityError,
    ResearchIntent,
    ResearchResult,
)


logger = logging.getLogger("movie_os.capabilities.research")


class ResearchCapability(Capability[ResearchIntent, ResearchResult]):
    """Research a topic from the web (DuckDuckGo, Wikipedia, etc.)."""

    name = "research"
    description = "Research a topic and return a summary with source citations."
    version = "0.1.0"

    def __init__(self, provider=None):
        self._provider = provider

    def can_handle(self, intent: ResearchIntent) -> bool:
        return bool(intent.query)

    async def execute(self, intent: ResearchIntent) -> ResearchResult:
        if not intent.query:
            raise ResearchCapabilityError("ResearchIntent.query is required")
        if self._provider is not None and hasattr(self._provider, "render"):
            return await self._provider.render(intent)
        raise NotImplementedError(
            "ResearchCapability is a stub in Phase 0. "
            "Implementation lands in a later phase."
        )
