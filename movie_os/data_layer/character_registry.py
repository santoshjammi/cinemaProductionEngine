"""CharacterRegistry — the persistent store for CharacterDNA.

Characters are persistent across stories. When a new story references
a character by key, the ImageProvider automatically pulls the
character's hero reference image for img2img / IPAdapter consistency.

File layout:

    movie_os/data/characters/
        jane_doe/
            character.yaml     # CharacterDNA serialized
            hero.png           # primary reference image
            side.png           # secondary angle
        ethan_morrison/
            character.yaml
            hero.png
        ...

Public API:

    from movie_os.data_layer import CharacterRegistry

    registry = CharacterRegistry("movie_os/data/characters")

    # Create or load
    char = CharacterDNA(key="jane_doe", name="Jane Doe", ...)
    registry.save(char)

    # Look up
    jane = registry.get("jane_doe")
    ethan = registry.find_by_name("Ethan Morrison")

    # List all
    for char in registry.list():
        print(char.key, char.name)

    # For image generation
    hero_path = registry.get_hero_image_path("jane_doe")
    # Pass hero_path as a reference_image_path in ImageIntent for img2img/IPAdapter

The Character DNA is stored as YAML. The hero reference image is a
single PNG (we can add multiple later).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from movie_os.domain.character import CharacterDNA
from .storage import EntityStorage


logger = logging.getLogger("movie_os.data_layer.character_registry")


# Default hero image filename
HERO_FILENAME = "hero.png"


class CharacterRegistry:
    """A persistent store for CharacterDNA objects.

    Characters live as directories under a root path. Each directory
    contains a character.yaml (the CharacterDNA serialized) and any
    reference images.
    """

    def __init__(self, root: str | Path = "movie_os/data/characters"):
        self.root = Path(root)
        self._storage = EntityStorage(self.root, manifest_filename="character.yaml")

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def save(self, character: CharacterDNA) -> Path:
        """Save a character to disk. Returns the manifest path."""
        data = character.model_dump(mode="json")
        return self._storage.save(character.key, data)

    def get(self, key: str) -> Optional[CharacterDNA]:
        """Load a character by key. Returns None if not found."""
        data = self._storage.load(key)
        if data is None:
            return None
        return CharacterDNA.model_validate(data)

    def has(self, key: str) -> bool:
        """Check if a character with this key exists."""
        return self._storage.has(key)

    def list(self) -> list[CharacterDNA]:
        """List all characters (sorted by key)."""
        characters = []
        for key in self._storage.list_keys():
            char = self.get(key)
            if char is not None:
                characters.append(char)
        return characters

    def list_keys(self) -> list[str]:
        """List all character keys (sorted)."""
        return self._storage.list_keys()

    def delete(self, key: str) -> bool:
        """Delete a character. Returns True if it existed."""
        return self._storage.delete(key)

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def find_by_name(self, name: str) -> Optional[CharacterDNA]:
        """Find a character by name (case-insensitive substring match)."""
        name_lower = name.lower()
        for char in self.list():
            if char.name.lower() == name_lower or name_lower in char.name.lower():
                return char
        return None

    def find_by_tag(self, tag: str) -> list[CharacterDNA]:
        """Find all characters with a given tag."""
        return [c for c in self.list() if tag in c.tags]

    # ------------------------------------------------------------------
    # Reference images
    # ------------------------------------------------------------------

    def get_hero_image_path(self, key: str) -> Optional[Path]:
        """Get the path to a character's hero reference image.

        Returns None if the character doesn't exist or has no hero image.
        """
        if not self.has(key):
            return None
        hero_path = self._storage.file_path_for(key, HERO_FILENAME)
        if hero_path.exists():
            return hero_path
        return None

    def save_hero_image(self, key: str, source: str | Path) -> Path:
        """Save a hero reference image for a character."""
        if not self.has(key):
            raise FileNotFoundError(f"Character '{key}' not found. Save the character first.")
        return self._storage.copy_file_in(key, source, HERO_FILENAME)

    def has_hero_image(self, key: str) -> bool:
        """Check if a character has a hero reference image."""
        return self.get_hero_image_path(key) is not None

    def list_reference_images(self, key: str) -> list[Path]:
        """List all reference images for a character (including the hero)."""
        return self._storage.list_files(key)

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self.list())

    def __contains__(self, key: str) -> bool:
        return self.has(key)

    def __iter__(self):
        return iter(self.list())


# A default global registry (lazily initialized)
_default_registry: Optional[CharacterRegistry] = None


def get_default_registry() -> CharacterRegistry:
    """Get the global default character registry."""
    global _default_registry
    if _default_registry is None:
        from movie_os import data_layer
        default_root = Path(data_layer.__file__).parent / "data" / "characters"
        _default_registry = CharacterRegistry(default_root)
    return _default_registry


def set_default_registry(registry: CharacterRegistry) -> None:
    """Set the global default registry."""
    global _default_registry
    _default_registry = registry
