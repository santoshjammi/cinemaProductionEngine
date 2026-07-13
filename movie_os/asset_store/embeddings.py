"""EmbeddingIndex — semantic search over the asset store.

Uses sqlite-vec for fast vector similarity and sentence-transformers
for text embeddings. The default model is `all-MiniLM-L6-v2`
(384-dim, fast, 80MB).

The index is opt-in: assets are embedded when you call
`EmbeddingIndex.embed(asset)`. You can also `embed_query(text)`
and search the index for the most similar assets.
"""

from __future__ import annotations

import logging
import sqlite3
import sqlite_vec
from pathlib import Path
from typing import Any, Optional

from .schema import Asset, AssetType
from .store import AssetStore


logger = logging.getLogger("movie_os.asset_store.embeddings")


# Embedding dimension for all-MiniLM-L6-v2
DEFAULT_DIM = 384


class EmbeddingIndex:
    """Semantic search index backed by sqlite-vec.

    Lazy-loads the sentence-transformer model on first embed
    call. Tests can pass `model=None` and call `set_vectors()`
    to inject pre-computed vectors.
    """

    def __init__(
        self,
        store: AssetStore,
        *,
        model_name: str = "all-MiniLM-L6-v2",
        dim: int = DEFAULT_DIM,
    ):
        self.store = store
        self.model_name = model_name
        self.dim = dim
        self._model: Any = None
        self._ensure_table()

    def _ensure_table(self) -> None:
        """Create the vec0 virtual table if it doesn't exist."""
        self.store.conn.enable_load_extension(True)
        self.store.conn.load_extension(sqlite_vec.loadable_path())
        # vec0 virtual table for vector similarity
        self.store.conn.execute(f"""
            CREATE VIRTUAL TABLE IF NOT EXISTS asset_embeddings USING vec0(
              asset_id TEXT PRIMARY KEY,
              embedding float[{self.dim}]
            )
        """)
        self.store.conn.commit()

    def _get_model(self):
        """Lazy-load the sentence-transformers model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as e:
                raise RuntimeError(
                    "sentence-transformers not installed. "
                    "Run: pip install sentence-transformers"
                ) from e
            logger.info(f"Loading embedding model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed_text(self, text: str) -> list[float]:
        """Embed a single text string. Returns a list of floats."""
        model = self._get_model()
        vec = model.encode(text, convert_to_numpy=True)
        return vec.tolist()

    def embed_query(self, text: str) -> list[float]:
        """Embed a search query. Same as embed_text for now."""
        return self.embed_text(text)

    def embed_asset(self, asset: Asset) -> None:
        """Embed an asset's prompt (or its path) and store in the index.

        If the asset has no prompt, we use the filename as a
        fallback. If there's nothing to embed, we skip.
        """
        text = asset.prompt or asset.path.name
        if not text:
            return
        vec = self.embed_text(text)
        self.set_vector(asset.id, vec)
        logger.debug(f"Embedded asset {asset.id}")

    def set_vector(self, asset_id: str, vector: list[float]) -> None:
        """Set (or replace) the embedding for an asset."""
        assert len(vector) == self.dim, f"Expected dim {self.dim}, got {len(vector)}"
        import struct
        # sqlite-vec expects raw float32 bytes
        vec_bytes = struct.pack(f"{self.dim}f", *vector)
        # Delete first to handle re-embedding
        self.store.conn.execute(
            "DELETE FROM asset_embeddings WHERE asset_id = ?",
            (asset_id,),
        )
        self.store.conn.execute(
            "INSERT INTO asset_embeddings (asset_id, embedding) VALUES (?, ?)",
            (asset_id, vec_bytes),
        )
        self.store.conn.commit()

    def remove(self, asset_id: str) -> None:
        """Remove an asset from the index."""
        self.store.conn.execute(
            "DELETE FROM asset_embeddings WHERE asset_id = ?",
            (asset_id,),
        )
        self.store.conn.commit()

    def search(self, query: str, k: int = 5) -> list[tuple[Asset, float]]:
        """Find the top-k assets most similar to the query text.

        Returns a list of (Asset, distance) tuples. Lower distance
        = more similar.
        """
        query_vec = self.embed_query(query)
        return self.search_by_vector(query_vec, k=k)

    def search_by_vector(
        self, query_vec: list[float], k: int = 5
    ) -> list[tuple[Asset, float]]:
        """Search by a pre-computed vector."""
        import struct
        assert len(query_vec) == self.dim
        vec_bytes = struct.pack(f"{self.dim}f", *query_vec)
        rows = self.store.conn.execute(
            """
            SELECT asset_id, distance
            FROM asset_embeddings
            WHERE embedding MATCH ?
            ORDER BY distance
            LIMIT ?
            """,
            (vec_bytes, k),
        ).fetchall()
        results = []
        for row in rows:
            asset = self.store.get_or_none(row["asset_id"])
            if asset is not None:
                results.append((asset, row["distance"]))
        return results

    def count(self) -> int:
        """Number of embedded assets."""
        row = self.store.conn.execute(
            "SELECT COUNT(*) as c FROM asset_embeddings"
        ).fetchone()
        return row["c"]
