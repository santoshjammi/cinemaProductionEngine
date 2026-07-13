"""Movie OS Asset Store — unified asset & knowledge management.

Public API:
    from movie_os.asset_store import (
        AssetStore, Asset, AssetType, AssetVersion,
        EmbeddingIndex, tag_search, semantic_search,
    )

Phase 9 replaces ad-hoc file paths and CharacterRegistry/EnvironmentRegistry
patterns with a single SQLite-backed store. Every generated artifact
(image, audio, video, music, sfx, even prompts) becomes a first-class
Asset with metadata, tags, version history, and semantic search.
"""

from .schema import Asset, AssetType, AssetVersion
from .store import AssetStore

__all__ = [
    "Asset", "AssetType", "AssetVersion", "AssetStore",
]
