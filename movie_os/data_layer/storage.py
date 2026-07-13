"""Filesystem storage for character and environment data.

Each character/environment is stored in its own directory:

    data/characters/jane_doe/
        character.yaml       # the CharacterDNA serialized
        hero.png             # primary reference image
        side.png             # secondary reference (optional)
        three_quarter.png    # etc.

    data/environments/bedroom/
        environment.yaml    # the EnvironmentDNA serialized
        hero.png            # primary reference image
        night.png           # variant
        golden_hour.png     # etc.

This module provides the file I/O — the registries (CharacterRegistry,
EnvironmentRegistry) build on top of this.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Optional
import yaml


logger = logging.getLogger("movie_os.data_layer.storage")


class EntityStorage:
    """Filesystem storage for a collection of entities (characters or environments).

    Each entity lives in its own directory under `root`. The directory
    contains a manifest YAML file plus any associated files
    (reference images, etc.).
    """

    def __init__(self, root: str | Path, manifest_filename: str = "entity.yaml"):
        """Initialize storage at `root`.

        Args:
            root: The directory under which entities are stored
                (e.g., `movie_os/data/characters`).
            manifest_filename: The name of the YAML file that holds
                the entity data (default: "entity.yaml").
        """
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.manifest_filename = manifest_filename

    def list_keys(self) -> list[str]:
        """List all entity keys (directory names under root)."""
        if not self.root.exists():
            return []
        return sorted(
            d.name for d in self.root.iterdir()
            if d.is_dir() and (d / self.manifest_filename).exists()
        )

    def has(self, key: str) -> bool:
        """Check if an entity with this key exists."""
        return (self.root / key / self.manifest_filename).exists()

    def path_for(self, key: str) -> Path:
        """Get the directory path for an entity (creates it if missing)."""
        path = self.root / key
        path.mkdir(parents=True, exist_ok=True)
        return path

    def manifest_path_for(self, key: str) -> Path:
        """Get the manifest file path for an entity."""
        return self.root / key / self.manifest_filename

    def file_path_for(self, key: str, filename: str) -> Path:
        """Get a file path inside the entity's directory."""
        return self.root / key / filename

    def load(self, key: str) -> Optional[dict[str, Any]]:
        """Load an entity's manifest as a dict. Returns None if not found."""
        path = self.manifest_path_for(key)
        if not path.exists():
            return None
        with open(path) as f:
            return yaml.safe_load(f)

    def save(self, key: str, data: dict[str, Any]) -> Path:
        """Save an entity's manifest. Returns the manifest path."""
        self.path_for(key)  # ensures the directory exists
        path = self.manifest_path_for(key)
        with open(path, "w") as f:
            yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        logger.info(f"Saved entity: {path}")
        return path

    def delete(self, key: str) -> bool:
        """Delete an entity. Returns True if it existed, False otherwise."""
        import shutil
        path = self.root / key
        if not path.exists():
            return False
        shutil.rmtree(path)
        logger.info(f"Deleted entity: {key}")
        return True

    def list_files(self, key: str) -> list[Path]:
        """List all files inside an entity's directory (excluding the manifest)."""
        entity_dir = self.root / key
        if not entity_dir.exists():
            return []
        return sorted(
            f for f in entity_dir.iterdir()
            if f.is_file() and f.name != self.manifest_filename
        )

    def copy_file_in(self, key: str, source: str | Path, filename: str | None = None) -> Path:
        """Copy a file into the entity's directory.

        Args:
            key: Entity key
            source: Path to the source file
            filename: Name to save as (default: source's filename)

        Returns the destination path.
        """
        import shutil
        source = Path(source)
        if filename is None:
            filename = source.name
        self.path_for(key)  # ensures the directory exists
        dest = self.file_path_for(key, filename)
        shutil.copy2(source, dest)
        logger.info(f"Copied file to entity: {dest}")
        return dest


__all__ = ["EntityStorage"]
