"""Phase 9.3 tests — EmbeddingIndex with sqlite-vec."""

from __future__ import annotations

import struct
from pathlib import Path

import pytest


@pytest.fixture
def store_with_assets(tmp_path):
    from movie_os.asset_store import AssetStore, AssetType
    store = AssetStore(db_path=tmp_path / "test.db", files_dir=tmp_path / "files")
    prompts = [
        "A lonely man sitting in a dark room, contemplative",
        "Bright sunny day, two lovers walking in a park",
        "A thunderstorm at night, lightning strikes a tree",
        "An old man in a dark basement, fear in his eyes",
    ]
    for i, prompt in enumerate(prompts):
        img = tmp_path / f"img_{i}.png"
        img.write_bytes(b"x" * 100)
        store.create(AssetType.IMAGE, img, tags=[f"scene_{i}"], prompt=prompt)
    return store


def _fake_vector(seed: int, dim: int = 384) -> list[float]:
    """Generate a deterministic test vector. Not semantically meaningful
    but lets us test the search mechanics."""
    import math
    return [
        math.sin((i + seed) * 0.1) for i in range(dim)
    ]


class TestEmbeddingIndexSetup:
    def test_index_creates_table(self, store_with_assets):
        from movie_os.asset_store.embeddings import EmbeddingIndex
        idx = EmbeddingIndex(store_with_assets)
        # The asset_embeddings table should exist
        row = store_with_assets.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='asset_embeddings'"
        ).fetchone()
        assert row is not None

    def test_index_starts_empty(self, store_with_assets):
        from movie_os.asset_store.embeddings import EmbeddingIndex
        idx = EmbeddingIndex(store_with_assets)
        assert idx.count() == 0


class TestSetVector:
    def test_set_vector_stores_embedding(self, store_with_assets):
        from movie_os.asset_store.embeddings import EmbeddingIndex
        idx = EmbeddingIndex(store_with_assets)
        assets = store_with_assets.list()
        idx.set_vector(assets[0].id, _fake_vector(1))
        assert idx.count() == 1

    def test_set_vector_replaces(self, store_with_assets):
        from movie_os.asset_store.embeddings import EmbeddingIndex
        idx = EmbeddingIndex(store_with_assets)
        assets = store_with_assets.list()
        idx.set_vector(assets[0].id, _fake_vector(1))
        idx.set_vector(assets[0].id, _fake_vector(2))
        assert idx.count() == 1

    def test_remove_clears_embedding(self, store_with_assets):
        from movie_os.asset_store.embeddings import EmbeddingIndex
        idx = EmbeddingIndex(store_with_assets)
        assets = store_with_assets.list()
        idx.set_vector(assets[0].id, _fake_vector(1))
        idx.remove(assets[0].id)
        assert idx.count() == 0

    def test_wrong_dim_raises(self, store_with_assets):
        from movie_os.asset_store.embeddings import EmbeddingIndex
        idx = EmbeddingIndex(store_with_assets)
        with pytest.raises(AssertionError):
            idx.set_vector("any-id", [1.0, 2.0, 3.0])


class TestSearchByVector:
    def test_search_returns_closest(self, store_with_assets):
        from movie_os.asset_store.embeddings import EmbeddingIndex
        idx = EmbeddingIndex(store_with_assets)
        assets = store_with_assets.list()
        # Embed 4 assets with seeds 1, 2, 3, 4
        for i, a in enumerate(assets):
            idx.set_vector(a.id, _fake_vector(i + 1))
        # Search for the vector with seed=3 — should be closest to asset 3
        results = idx.search_by_vector(_fake_vector(3), k=4)
        assert len(results) == 4
        # The closest should be the one with seed=3 (index 2)
        assert results[0][0].id == assets[2].id
        # Distance should be 0 for the exact match
        assert results[0][1] < 0.01

    def test_search_respects_k(self, store_with_assets):
        from movie_os.asset_store.embeddings import EmbeddingIndex
        idx = EmbeddingIndex(store_with_assets)
        assets = store_with_assets.list()
        for a in assets:
            idx.set_vector(a.id, _fake_vector(1))
        results = idx.search_by_vector(_fake_vector(1), k=2)
        assert len(results) == 2

    def test_search_skips_missing_assets(self, store_with_assets):
        from movie_os.asset_store.embeddings import EmbeddingIndex
        idx = EmbeddingIndex(store_with_assets)
        assets = store_with_assets.list()
        idx.set_vector(assets[0].id, _fake_vector(1))
        idx.set_vector("nonexistent-id", _fake_vector(2))  # orphan vector
        # search should skip the orphan
        results = idx.search_by_vector(_fake_vector(1), k=5)
        assert len(results) == 1
        assert results[0][0].id == assets[0].id


class TestEmbedAsset:
    def test_embed_asset_uses_prompt(self, store_with_assets):
        from movie_os.asset_store.embeddings import EmbeddingIndex
        idx = EmbeddingIndex(store_with_assets)
        a = store_with_assets.list()[0]
        # Stub out embed_text to avoid loading the model
        idx.embed_text = lambda text: _fake_vector(1) if "lonely" in text else _fake_vector(2)
        idx.embed_asset(a)
        assert idx.count() == 1

    def test_embed_asset_falls_back_to_filename(self, store_with_assets):
        from movie_os.asset_store.embeddings import EmbeddingIndex
        idx = EmbeddingIndex(store_with_assets)
        a = store_with_assets.list()[0]
        a.prompt = None  # clear the prompt
        idx.embed_text = lambda text: _fake_vector(1)
        idx.embed_asset(a)
        assert idx.count() == 1
