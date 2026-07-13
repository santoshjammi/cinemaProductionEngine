"""Search — tag and semantic search over the asset store."""

from __future__ import annotations

import json
import logging
import sqlite3
from typing import Any

from .schema import Asset, AssetType


logger = logging.getLogger("movie_os.asset_store.search")


def tag_search(
    conn: sqlite3.Connection,
    *tags: str,
    match_all: bool = False,
    type: AssetType | str | None = None,
    limit: int = 50,
) -> list[Asset]:
    """Search assets by tags.

    Args:
        conn: An open SQLite connection (must have row_factory=Row).
        tags: One or more tags to search for.
        match_all: If True, return only assets with ALL tags. If False
            (default), return assets with ANY of the tags.
        type: Optional AssetType filter.
        limit: Max results.

    Returns:
        List of matching Asset objects.
    """
    if not tags:
        return []
    if isinstance(type, str):
        type = AssetType(type)

    if match_all:
        # Use a subquery: asset must have all tags
        placeholders = ",".join("?" * len(tags))
        query = f"""
            SELECT a.* FROM assets a
            WHERE a.deleted = 0
              AND a.id IN (
                SELECT asset_id FROM asset_tags
                WHERE tag IN ({placeholders})
                GROUP BY asset_id
                HAVING COUNT(DISTINCT tag) = ?
              )
        """
        params: list = list(tags) + [len(tags)]
    else:
        # Any of the tags
        placeholders = ",".join("?" * len(tags))
        query = f"""
            SELECT a.* FROM assets a
            WHERE a.deleted = 0
              AND EXISTS (
                SELECT 1 FROM asset_tags t
                WHERE t.asset_id = a.id AND t.tag IN ({placeholders})
              )
        """
        params = list(tags)

    if type is not None:
        query += " AND a.type = ?"
        params.append(type.value)
    query += " ORDER BY a.created_at DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    return [Asset.from_db_row(dict(r)) for r in rows]


def all_tags(conn: sqlite3.Connection) -> dict[str, int]:
    """Get a count of all tags in use.

    Returns a dict of tag -> count. Tags come from the asset_tags
    table (populated by sync_tags — call that first if needed).
    """
    rows = conn.execute("""
        SELECT tag, COUNT(*) as count
        FROM asset_tags
        GROUP BY tag
        ORDER BY count DESC
    """).fetchall()
    return {row["tag"]: row["count"] for row in rows}


def sync_tags(conn: sqlite3.Connection) -> int:
    """Rebuild the asset_tags table from assets.tags JSON arrays.

    This is called lazily — the tags column on assets is the source
    of truth, asset_tags is a denormalized index for fast queries.
    Returns the number of tag-asset pairs.
    """
    conn.execute("DELETE FROM asset_tags")
    rows = conn.execute("SELECT id, tags FROM assets WHERE deleted = 0").fetchall()
    count = 0
    for row in rows:
        tags = json.loads(row["tags"]) if row["tags"] else []
        for tag in tags:
            conn.execute(
                "INSERT INTO asset_tags (asset_id, tag) VALUES (?, ?)",
                (row["id"], tag),
            )
            count += 1
    conn.commit()
    return count


def ensure_tag_index(conn: sqlite3.Connection) -> None:
    """Create the asset_tags table + indexes if they don't exist."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS asset_tags (
          asset_id TEXT NOT NULL,
          tag TEXT NOT NULL,
          FOREIGN KEY (asset_id) REFERENCES assets(id)
        );
        CREATE INDEX IF NOT EXISTS idx_asset_tags_tag ON asset_tags(tag);
        CREATE INDEX IF NOT EXISTS idx_asset_tags_asset ON asset_tags(asset_id);
    """)
    conn.commit()
