"""Pure-Python vector search using numpy cosine similarity.

No external extension required. Uses numpy for fast cosine distance
computation and SQLite for persistent metadata storage.

Usage::

    idx = VectorIndex("movie_os/memory/char_vectors.db")
    idx.setup(dim=768)
    idx.ingest("jane", {"key":"jane","text":"brave woman"}, vec=[0.1,...]*768)
    results = idx.query(vec=[0.12,...]*768, k=3)
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Optional

import numpy as np

logger = logging.getLogger("movie_os.memory.vector_search")


class VectorIndex:
    """SQLite + numpy vector index."""

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._dim: Optional[int] = None
        import sqlite3
        self.db = sqlite3.connect(str(self.db_path))

    def setup(self, dim: int = 768) -> None:
        """Create the index tables on disk if they don't exist."""
        self._dim = dim
        cur = self.db.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE,
                metadata TEXT,
                vector BLOB
            )
        """)
        self.db.commit()

    def ingest(self, key: str, data: dict[str, Any], vector: list[float]) -> int:
        """Ingest a keyed entity with its vector embedding."""
        vec_blob = np.array(vector, dtype=np.float32).tobytes()
        cur = self.db.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO entities (key, metadata, vector) VALUES (?, ?, ?)",
            (key, json.dumps(data), vec_blob),
        )
        self.db.commit()
        return cur.lastrowid

    def query(self, vector: list[float], k: int = 5) -> list[dict]:
        """Return nearest neighbors sorted by cosine distance ascending."""
        query_vec = np.array(vector, dtype=np.float32)
        cur = self.db.cursor()
        cur.execute("SELECT id, key, metadata, vector FROM entities")
        scored = []
        for rowid, key, meta_json, vec_blob in cur.fetchall():
            stored_vec = np.frombuffer(vec_blob, dtype=np.float32)
            dot = np.dot(query_vec, stored_vec)
            norm = np.linalg.norm(query_vec) * np.linalg.norm(stored_vec)
            score = 1.0 - (dot / norm) if norm > 0 else 1.0
            try:
                meta = json.loads(meta_json) if meta_json else {}
            except json.JSONDecodeError:
                meta = {}
            scored.append((score, {"key": key, "score": float(score), "metadata": meta}))
        scored.sort(key=lambda x: x[0])
        return [item for _, item in scored[:k]]

    def close(self):
        self.db.close()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()


__all__ = ["VectorIndex"]
