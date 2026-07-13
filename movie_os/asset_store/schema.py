"""Asset schema — the Pydantic models for the asset store."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field


class AssetType(str, Enum):
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    MUSIC = "music"
    SFX = "sfx"
    PROMPT = "prompt"
    TIMELINE = "timeline"
    CHARACTER = "character"
    ENVIRONMENT = "environment"
    OTHER = "other"


class Asset(BaseModel):
    """A single asset in the store.

    The `path` is the current version's location. Prior versions
    are immutable and live under the same asset_id's `v<n>/` dirs.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: AssetType
    path: Path
    tags: list[str] = Field(default_factory=list)
    prompt: Optional[str] = None
    model: Optional[str] = None
    seed: Optional[int] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    current_version: int = 1
    version_of: Optional[str] = None  # If this is v2 of another asset
    deleted: bool = False

    def to_db_row(self) -> dict[str, Any]:
        """Convert to a SQLite row dict."""
        import json
        return {
            "id": self.id,
            "type": self.type.value,
            "current_path": str(self.path),
            "tags": json.dumps(self.tags),
            "prompt": self.prompt,
            "model": self.model,
            "seed": self.seed,
            "metadata": json.dumps(self.metadata),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "current_version": self.current_version,
            "version_of": self.version_of,
            "deleted": int(self.deleted),
        }

    @classmethod
    def from_db_row(cls, row: dict) -> "Asset":
        """Construct from a SQLite row dict."""
        import json
        return cls(
            id=row["id"],
            type=AssetType(row["type"]),
            path=Path(row["current_path"]),
            tags=json.loads(row["tags"]) if row["tags"] else [],
            prompt=row["prompt"],
            model=row["model"],
            seed=row["seed"],
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            current_version=row["current_version"],
            version_of=row["version_of"],
            deleted=bool(row.get("deleted", 0)),
        )


class AssetVersion(BaseModel):
    """An immutable version of an asset."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    asset_id: str
    version: int
    path: Path
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    notes: Optional[str] = None

    def to_db_row(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "asset_id": self.asset_id,
            "version": self.version,
            "path": str(self.path),
            "created_at": self.created_at,
            "notes": self.notes,
        }

    @classmethod
    def from_db_row(cls, row: dict) -> "AssetVersion":
        return cls(
            id=row["id"],
            asset_id=row["asset_id"],
            version=row["version"],
            path=Path(row["path"]),
            created_at=row["created_at"],
            notes=row["notes"],
        )
