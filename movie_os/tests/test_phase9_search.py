"""Phase 9.2 tests — tag search."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def store_with_assets(tmp_path):
    from movie_os.asset_store import AssetStore, AssetType
    store = AssetStore(db_path=tmp_path / "test.db", files_dir=tmp_path / "files")
    # Create 3 images with different tag combos
    for i, tags in enumerate([
        ["dark", "cinematic"],
        ["dark", "irreversible_moment"],
        ["bright", "happy"],
    ]):
        img = tmp_path / f"img_{i}.png"
        img.write_bytes(b"x" * 100)
        store.create(AssetType.IMAGE, img, tags=tags, prompt=f"scene {i}")
    return store


class TestTagSearch:
    def test_search_by_single_tag(self, store_with_assets):
        from movie_os.asset_store.search import tag_search
        results = tag_search(store_with_assets.conn, "dark")
        assert len(results) == 2

    def test_search_by_any_tag_default(self, store_with_assets):
        from movie_os.asset_store.search import tag_search
        results = tag_search(store_with_assets.conn, "dark", "bright")
        assert len(results) == 3

    def test_search_by_all_tags(self, store_with_assets):
        from movie_os.asset_store.search import tag_search
        results = tag_search(store_with_assets.conn, "dark", "irreversible_moment", match_all=True)
        assert len(results) == 1
        assert "irreversible_moment" in results[0].tags
        assert "dark" in results[0].tags

    def test_search_by_all_tags_no_match(self, store_with_assets):
        from movie_os.asset_store.search import tag_search
        results = tag_search(store_with_assets.conn, "dark", "bright", match_all=True)
        assert len(results) == 0

    def test_search_with_type_filter(self, store_with_assets):
        from movie_os.asset_store.search import tag_search
        from movie_os.asset_store import AssetType
        # No AUDIO assets, so this should return empty
        results = tag_search(store_with_assets.conn, "dark", type=AssetType.AUDIO)
        assert len(results) == 0
        # But with IMAGE filter, it should return 2
        results = tag_search(store_with_assets.conn, "dark", type=AssetType.IMAGE)
        assert len(results) == 2

    def test_search_no_tags_returns_empty(self, store_with_assets):
        from movie_os.asset_store.search import tag_search
        assert tag_search(store_with_assets.conn) == []

    def test_search_limit(self, store_with_assets):
        from movie_os.asset_store.search import tag_search
        results = tag_search(store_with_assets.conn, "dark", limit=1)
        assert len(results) == 1

    def test_tag_index_updates_on_tag_change(self, store_with_assets):
        from movie_os.asset_store.search import tag_search
        a = store_with_assets.list()[0]
        store_with_assets.tag(a.id, "favorite")
        results = tag_search(store_with_assets.conn, "favorite")
        assert len(results) == 1
        assert results[0].id == a.id

    def test_tag_index_updates_on_untag(self, store_with_assets):
        from movie_os.asset_store.search import tag_search
        a = store_with_assets.list()[0]
        store_with_assets.tag(a.id, "favorite")
        store_with_assets.untag(a.id, "favorite")
        results = tag_search(store_with_assets.conn, "favorite")
        assert len(results) == 0


class TestAllTags:
    def test_all_tags_counts(self, store_with_assets):
        from movie_os.asset_store.search import all_tags
        counts = all_tags(store_with_assets.conn)
        assert counts["dark"] == 2
        assert counts["bright"] == 1
        assert counts["cinematic"] == 1
        assert counts["irreversible_moment"] == 1
