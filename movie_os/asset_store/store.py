"""AssetStore — SQLite + filesystem CRUD for assets.

The store keeps two things:
  1. Metadata in SQLite (assets table, asset_versions table)
  2. Files on disk under <files_dir>/<asset_id>/v<n>/<filename.ext>

When you `create()` an asset, the source file is COPIED into
the versioned location. The `path` on the returned Asset points
to that copy. Files are never overwritten — to "update" an asset,
call `create_version()` which adds a v2, v3, etc.
"""

from __future__ import annotations

import json
import logging
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator, Optional

from .schema import Asset, AssetType, AssetVersion


logger = logging.getLogger("movie_os.asset_store")


# SQLite schema — applied on first connect
SCHEMA = """
CREATE TABLE IF NOT EXISTS assets (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL,
  current_path TEXT NOT NULL,
  tags TEXT NOT NULL DEFAULT '[]',
  prompt TEXT,
  model TEXT,
  seed INTEGER,
  metadata TEXT DEFAULT '{}',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  current_version INTEGER NOT NULL DEFAULT 1,
  version_of TEXT,
  deleted INTEGER NOT NULL DEFAULT 0,
  FOREIGN KEY (version_of) REFERENCES assets(id)
);

CREATE TABLE IF NOT EXISTS asset_versions (
  id TEXT PRIMARY KEY,
  asset_id TEXT NOT NULL,
  version INTEGER NOT NULL,
  path TEXT NOT NULL,
  created_at TEXT NOT NULL,
  notes TEXT,
  FOREIGN KEY (asset_id) REFERENCES assets(id)
);

CREATE TABLE IF NOT EXISTS asset_tags (
  asset_id TEXT NOT NULL,
  tag TEXT NOT NULL,
  FOREIGN KEY (asset_id) REFERENCES assets(id)
);

CREATE INDEX IF NOT EXISTS idx_assets_type ON assets(type);
CREATE INDEX IF NOT EXISTS idx_assets_deleted ON assets(deleted);
CREATE INDEX IF NOT EXISTS idx_assets_version_of ON assets(version_of);
CREATE INDEX IF NOT EXISTS idx_versions_asset ON asset_versions(asset_id);
CREATE INDEX IF NOT EXISTS idx_asset_tags_tag ON asset_tags(tag);
CREATE INDEX IF NOT EXISTS idx_asset_tags_asset ON asset_tags(asset_id);
"""


class AssetStore:
    """The asset store. Backed by SQLite + filesystem.

    For tests, pass a `:memory:` db_path. For production, use a
    real .db file.
    """

    def __init__(self, db_path: str | Path, files_dir: str | Path | None = None):
        self.db_path = str(db_path)
        self.files_dir = Path(files_dir) if files_dir else Path(db_path).parent / "files"
        self.files_dir.mkdir(parents=True, exist_ok=True)
        self._conn: Optional[sqlite3.Connection] = None

    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
            self._conn.executescript(SCHEMA)
            self._conn.commit()
        return self._conn

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    def create(
        self,
        type: AssetType | str,
        source_path: str | Path,
        *,
        tags: list[str] | None = None,
        prompt: str | None = None,
        model: str | None = None,
        seed: int | None = None,
        metadata: dict | None = None,
    ) -> Asset:
        """Create a new asset by copying source_path into the store."""
        type = AssetType(type) if isinstance(type, str) else type
        source_path = Path(source_path)
        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")

        asset = Asset(
            type=type,
            path=Path(),  # placeholder, set after copy
            tags=tags or [],
            prompt=prompt,
            model=model,
            seed=seed,
            metadata=metadata or {},
        )
        version_dir = self.files_dir / asset.id / "v1"
        version_dir.mkdir(parents=True, exist_ok=True)
        new_path = version_dir / source_path.name
        shutil.copy2(source_path, new_path)
        asset.path = new_path

        version = AssetVersion(
            asset_id=asset.id,
            version=1,
            path=new_path,
        )
        self._insert(asset, version)
        logger.info(f"AssetStore: created {asset.id} ({type.value}) → {new_path}")
        return asset

    def _insert(self, asset: Asset, version: AssetVersion) -> None:
        row = asset.to_db_row()
        self.conn.execute(
            """INSERT INTO assets
               (id, type, current_path, tags, prompt, model, seed,
                metadata, created_at, updated_at, current_version,
                version_of, deleted)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                row["id"], row["type"], row["current_path"], row["tags"],
                row["prompt"], row["model"], row["seed"], row["metadata"],
                row["created_at"], row["updated_at"], row["current_version"],
                row["version_of"], row["deleted"],
            ),
        )
        vrow = version.to_db_row()
        self.conn.execute(
            """INSERT INTO asset_versions
               (id, asset_id, version, path, created_at, notes)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (vrow["id"], vrow["asset_id"], vrow["version"],
             vrow["path"], vrow["created_at"], vrow["notes"]),
        )
        for tag in asset.tags:
            self.conn.execute(
                "INSERT INTO asset_tags (asset_id, tag) VALUES (?, ?)",
                (asset.id, tag),
            )
        self.conn.commit()

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get(self, asset_id: str) -> Asset:
        """Get an asset by ID. Raises KeyError if not found."""
        row = self.conn.execute(
            "SELECT * FROM assets WHERE id = ? AND deleted = 0",
            (asset_id,),
        ).fetchone()
        if row is None:
            raise KeyError(f"Asset not found: {asset_id}")
        return Asset.from_db_row(dict(row))

    def get_or_none(self, asset_id: str) -> Optional[Asset]:
        try:
            return self.get(asset_id)
        except KeyError:
            return None

    def list(
        self,
        *,
        type: AssetType | str | None = None,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[Asset]:
        """List assets, optionally filtered by type."""
        if isinstance(type, str):
            type = AssetType(type)
        query = "SELECT * FROM assets"
        params: list = []
        if not include_deleted:
            query += " WHERE deleted = 0"
            if type is not None:
                query += " AND type = ?"
                params.append(type.value)
        elif type is not None:
            query += " WHERE type = ?"
            params.append(type.value)
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        rows = self.conn.execute(query, params).fetchall()
        return [Asset.from_db_row(dict(r)) for r in rows]

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def tag(self, asset_id: str, *tags_to_add: str) -> Asset:
        """Add tags to an asset."""
        asset = self.get(asset_id)
        new_tags = sorted(set(asset.tags) | set(tags_to_add))
        self.conn.execute(
            "UPDATE assets SET tags = ?, updated_at = ? WHERE id = ?",
            (json.dumps(new_tags), datetime.utcnow().isoformat(), asset_id),
        )
        for tag in tags_to_add:
            self.conn.execute(
                "INSERT OR IGNORE INTO asset_tags (asset_id, tag) VALUES (?, ?)",
                (asset_id, tag),
            )
        self.conn.commit()
        return self.get(asset_id)

    def untag(self, asset_id: str, *tags_to_remove: str) -> Asset:
        """Remove tags from an asset."""
        asset = self.get(asset_id)
        new_tags = [t for t in asset.tags if t not in tags_to_remove]
        self.conn.execute(
            "UPDATE assets SET tags = ?, updated_at = ? WHERE id = ?",
            (json.dumps(new_tags), datetime.utcnow().isoformat(), asset_id),
        )
        for tag in tags_to_remove:
            self.conn.execute(
                "DELETE FROM asset_tags WHERE asset_id = ? AND tag = ?",
                (asset_id, tag),
            )
        self.conn.commit()
        return self.get(asset_id)

    def soft_delete(self, asset_id: str) -> None:
        """Mark an asset as deleted (doesn't remove the file)."""
        self.conn.execute(
            "UPDATE assets SET deleted = 1, updated_at = ? WHERE id = ?",
            (datetime.utcnow().isoformat(), asset_id),
        )
        self.conn.commit()

    # ------------------------------------------------------------------
    # Versions
    # ------------------------------------------------------------------

    def versions(self, asset_id: str) -> list[AssetVersion]:
        """Get all versions of an asset, oldest first."""
        rows = self.conn.execute(
            "SELECT * FROM asset_versions WHERE asset_id = ? ORDER BY version ASC",
            (asset_id,),
        ).fetchall()
        return [AssetVersion.from_db_row(dict(r)) for r in rows]

    def create_version(
        self,
        asset_id: str,
        source_path: str | Path,
        *,
        notes: str | None = None,
    ) -> Asset:
        """Add a new version to an existing asset.

        The current_version is bumped, and a new immutable v<n> dir
        is created with the new file. The Asset.path is updated.
        """
        asset = self.get(asset_id)
        source_path = Path(source_path)
        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")

        new_version = asset.current_version + 1
        version_dir = self.files_dir / asset_id / f"v{new_version}"
        version_dir.mkdir(parents=True, exist_ok=True)
        new_path = version_dir / source_path.name
        shutil.copy2(source_path, new_path)

        now = datetime.utcnow().isoformat()
        version = AssetVersion(
            asset_id=asset_id,
            version=new_version,
            path=new_path,
            notes=notes,
        )
        self.conn.execute(
            """INSERT INTO asset_versions
               (id, asset_id, version, path, created_at, notes)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (version.id, version.asset_id, version.version,
             str(version.path), version.created_at, version.notes),
        )
        self.conn.execute(
            """UPDATE assets SET current_path = ?, current_version = ?,
                                  updated_at = ? WHERE id = ?""",
            (str(new_path), new_version, now, asset_id),
        )
        self.conn.commit()
        return self.get(asset_id)

    def rollback(self, asset_id: str, target_version: int) -> Asset:
        """Roll back the current pointer to a prior version.

        The prior version file is NOT moved or copied. We just
        update the asset's current_path / current_version to point
        at the prior version's file. The "newer" version remains
        on disk and in the version history.
        """
        versions = self.versions(asset_id)
        target = next((v for v in versions if v.version == target_version), None)
        if target is None:
            raise KeyError(f"Version {target_version} not found for {asset_id}")

        now = datetime.utcnow().isoformat()
        self.conn.execute(
            """UPDATE assets SET current_path = ?, current_version = ?,
                                  updated_at = ? WHERE id = ?""",
            (str(target.path), target.version, now, asset_id),
        )
        self.conn.commit()
        return self.get(asset_id)
