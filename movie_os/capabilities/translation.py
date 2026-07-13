"""TranslationCapability — translates text between languages.

For multi-language content. For Phase 0, this is a stub. Implementation
lands in later phases.
"""

from __future__ import annotations

import logging

from .base import (
    Capability,
    TranslationCapabilityError,
    TranslationIntent,
    TranslationResult,
)


logger = logging.getLogger("movie_os.capabilities.translation")


class TranslationCapability(Capability[TranslationIntent, TranslationResult]):
    """Translate text from one language to another."""

    name = "translation"
    description = "Translate text between languages while preserving tone."
    version = "0.1.0"

    def __init__(self, provider=None):
        self._provider = provider

    def can_handle(self, intent: TranslationIntent) -> bool:
        return bool(intent.text) and bool(intent.target_language)

    async def execute(self, intent: TranslationIntent) -> TranslationResult:
        if not intent.text:
            raise TranslationCapabilityError("TranslationIntent.text is required")
        if not intent.target_language:
            raise TranslationCapabilityError("TranslationIntent.target_language is required")
        if self._provider is not None and hasattr(self._provider, "render"):
            return await self._provider.render(intent)
        raise NotImplementedError(
            "TranslationCapability is a stub in Phase 0. "
            "Implementation lands in a later phase."
        )
