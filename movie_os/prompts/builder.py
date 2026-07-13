"""PromptBuilder — assembles context for a prompt from the domain model.

Given a domain object (Scene, CharacterDNA, etc.), produces the
context dict that the PromptTemplate's variables expect.

The builder is the bridge between the domain layer and the prompt
layer. It knows how to extract the right information from a Scene
or a CharacterDNA to fill a prompt's variables.
"""

from __future__ import annotations

import logging
from typing import Any

from movie_os.domain.prompt import PromptTemplate
from movie_os.domain.story import Scene, Story
from movie_os.domain.character import CharacterDNA


logger = logging.getLogger("movie_os.prompts.builder")


class PromptBuilder:
    """Assembles context from domain objects for a prompt template."""

    def __init__(self, template: PromptTemplate):
        self.template = template

    def build_from_scene(
        self,
        scene: Scene,
        characters: dict[str, CharacterDNA] | None = None,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a context dict from a Scene + characters."""
        ctx: dict[str, Any] = {}

        # Direct scene fields
        if "subject" in self._declared_vars():
            ctx["subject"] = scene.scene_description or scene.title
        if "scene_description" in self._declared_vars():
            ctx["scene_description"] = scene.scene_description
        if "mood" in self._declared_vars():
            ctx["mood"] = scene.emotional_state
        if "energy" in self._declared_vars():
            ctx["energy"] = scene.energy
        if "voiceover" in self._declared_vars():
            ctx["voiceover"] = scene.voiceover
        if "phase" in self._declared_vars():
            ctx["phase"] = scene.phase
        if "beat" in self._declared_vars():
            ctx["beat"] = scene.beat
        if "shot_size" in self._declared_vars():
            ctx["shot_size"] = scene.shot_language.get("shot_size", "medium")
        if "lens_mm" in self._declared_vars():
            ctx["lens_mm"] = scene.shot_language.get("lens_mm", 50)
        if "lighting_key" in self._declared_vars():
            ctx["lighting_key"] = scene.shot_language.get("lighting_key", "natural_shadows")

        # Character-derived
        if "characters" in self._declared_vars() and characters:
            ctx["characters"] = self._summarize_characters(scene, characters)
        if "character_names" in self._declared_vars() and characters:
            ctx["character_names"] = [
                characters[c].name for c in scene.characters_present if c in characters
            ]
        if "character_anchors" in self._declared_vars() and characters:
            ctx["character_anchors"] = self._character_anchors(scene, characters)

        # Apply defaults for missing variables
        for var in self.template.variables:
            if var.name not in ctx and var.default is not None:
                ctx[var.name] = var.default

        # User-provided extra context wins
        if extra:
            ctx.update(extra)

        return ctx

    def build_from_story(
        self,
        story: Story,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a context dict from a Story."""
        ctx: dict[str, Any] = {
            "title": story.title,
            "logline": story.logline,
            "synopsis": story.synopsis,
            "territory": story.territory,
            "ending": story.ending,
        }
        if extra:
            ctx.update(extra)
        return ctx

    def _declared_vars(self) -> set[str]:
        return {v.name for v in self.template.variables}

    def _summarize_characters(
        self, scene: Scene, characters: dict[str, CharacterDNA]
    ) -> list[dict[str, str]]:
        result = []
        for char_key in scene.characters_present:
            if char_key in characters:
                char = characters[char_key]
                result.append({
                    "key": char.key,
                    "name": char.name,
                    "visual_anchor": char.physical.visual_anchor,
                })
        return result

    def _character_anchors(
        self, scene: Scene, characters: dict[str, CharacterDNA]
    ) -> list[str]:
        result = []
        for char_key in scene.characters_present:
            if char_key in characters:
                char = characters[char_key]
                if char.physical.visual_anchor:
                    result.append(char.physical.visual_anchor)
        return result
