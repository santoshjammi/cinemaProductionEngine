"""EnvironmentRegistry — the persistent store for EnvironmentDNA.

Environments (apartment, therapist office, temple, village, etc.) are
persistent across stories. When a new story says "the bedroom", the
ImageProvider pulls the environment's hero reference image for
visual consistency.

File layout:

    movie_os/data/environments/
        bedroom_jane/
            environment.yaml   # EnvironmentDNA serialized
            hero.png           # primary reference image
            night.png          # variant (night lighting)
            golden_hour.png    # variant (golden hour lighting)
        therapist_office/
            environment.yaml
            hero.png
        ...

The same pattern as CharacterRegistry. The EnvironmentDNA can have
multiple variants (time_of_day, weather) — each variant can have
its own reference image.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from movie_os.domain.environment import EnvironmentDNA
from .storage import EntityStorage


logger = logging.getLogger("movie_os.data_layer.environment_registry")


HERO_FILENAME = "hero.png"


class EnvironmentRegistry:
    """A persistent store for EnvironmentDNA objects."""

    def __init__(self, root: str | Path = "movie_os/data/environments"):
        self.root = Path(root)
        self._storage = EntityStorage(self.root, manifest_filename="environment.yaml")

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def save(self, environment: EnvironmentDNA) -> Path:
        """Save an environment to disk."""
        data = environment.model_dump(mode="json")
        return self._storage.save(environment.key, data)

    def get(self, key: str) -> Optional[EnvironmentDNA]:
        """Load an environment by key."""
        data = self._storage.load(key)
        if data is None:
            return None
        return EnvironmentDNA.model_validate(data)

    def has(self, key: str) -> bool:
        return self._storage.has(key)

    def list(self) -> list[EnvironmentDNA]:
        envs = []
        for key in self._storage.list_keys():
            env = self.get(key)
            if env is not None:
                envs.append(env)
        return envs

    def list_keys(self) -> list[str]:
        return self._storage.list_keys()

    def delete(self, key: str) -> bool:
        return self._storage.delete(key)

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def find_by_name(self, name: str) -> Optional[EnvironmentDNA]:
        """Find an environment by name (case-insensitive substring)."""
        name_lower = name.lower()
        for env in self.list():
            if env.name.lower() == name_lower or name_lower in env.name.lower():
                return env
        return None

    # ------------------------------------------------------------------
    # Reference images
    # ------------------------------------------------------------------

    def get_hero_image_path(self, key: str) -> Optional[Path]:
        """Get the path to the environment's hero reference image."""
        if not self.has(key):
            return None
        hero_path = self._storage.file_path_for(key, HERO_FILENAME)
        if hero_path.exists():
            return hero_path
        return None

    def get_variant_image_path(
        self, key: str, variant_label: str
    ) -> Optional[Path]:
        """Get the path to a specific variant's reference image.

        variant_label: e.g., "night", "golden_hour", "rain"
        """
        if not self.has(key):
            return None
        path = self._storage.file_path_for(key, f"{variant_label}.png")
        if path.exists():
            return path
        return None

    def save_hero_image(self, key: str, source: str | Path) -> Path:
        if not self.has(key):
            raise FileNotFoundError(f"Environment '{key}' not found. Save it first.")
        return self._storage.copy_file_in(key, source, HERO_FILENAME)

    def save_variant_image(
        self, key: str, variant_label: str, source: str | Path
    ) -> Path:
        """Save a variant image (e.g., 'night.png', 'rain.png')."""
        if not self.has(key):
            raise FileNotFoundError(f"Environment '{key}' not found. Save it first.")
        return self._storage.copy_file_in(key, source, f"{variant_label}.png")

    def has_hero_image(self, key: str) -> bool:
        return self.get_hero_image_path(key) is not None

    def list_reference_images(self, key: str) -> list[Path]:
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


# Default global registry
_default_registry: Optional[EnvironmentRegistry] = None


def get_default_registry() -> EnvironmentRegistry:
    global _default_registry
    if _default_registry is None:
        from movie_os import data_layer
        default_root = Path(data_layer.__file__).parent / "data" / "environments"
        _default_registry = EnvironmentRegistry(default_root)
    return _default_registry


def set_default_registry(registry: EnvironmentRegistry) -> None:
    global _default_registry
    _default_registry = registry
