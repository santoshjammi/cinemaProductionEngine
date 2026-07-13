"""Phase 9.1 tests — AssetStore schema, CRUD, versioning."""

from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture
def store(tmp_path):
    from movie_os.asset_store import AssetStore
    return AssetStore(db_path=tmp_path / "test.db", files_dir=tmp_path / "files")


@pytest.fixture
def sample_image(tmp_path):
    p = tmp_path / "image.png"
    p.write_bytes(b"\x89PNG\r\n\x1a\n" + b"x" * 200)
    return p


class TestAssetSchema:
    def test_asset_to_db_row_roundtrip(self):
        from movie_os.asset_store import Asset, AssetType
        a = Asset(
            type=AssetType.IMAGE,
            path=Path("/tmp/x.png"),
            tags=["dark", "cinematic"],
            prompt="A man in a dark room",
        )
        row = a.to_db_row()
        a2 = Asset.from_db_row(row)
        assert a.id == a2.id
        assert a.type == a2.type
        assert a.tags == a2.tags
        assert a.prompt == a2.prompt


class TestAssetStoreCreate:
    def test_create_copies_file(self, store, sample_image, tmp_path):
        from movie_os.asset_store import AssetType
        a = store.create(AssetType.IMAGE, sample_image, prompt="test", tags=["dark"])
        assert a.path.exists()
        assert a.path != sample_image  # it's a copy
        assert a.path.read_bytes() == sample_image.read_bytes()
        assert a.type == AssetType.IMAGE
        assert a.tags == ["dark"]
        assert a.prompt == "test"
        assert a.current_version == 1

    def test_create_missing_file_raises(self, store):
        from movie_os.asset_store import AssetType
        with pytest.raises(FileNotFoundError):
            store.create(AssetType.IMAGE, "/no/such/file.png")

    def test_create_accepts_string_type(self, store, sample_image):
        from movie_os.asset_store import AssetType
        a = store.create("image", sample_image)
        assert a.type == AssetType.IMAGE


class TestAssetStoreRead:
    def test_get_returns_asset(self, store, sample_image):
        from movie_os.asset_store import AssetType
        a = store.create(AssetType.IMAGE, sample_image)
        b = store.get(a.id)
        assert b.id == a.id
        assert b.path == a.path

    def test_get_missing_raises(self, store):
        with pytest.raises(KeyError):
            store.get("not-a-real-id")

    def test_list_returns_assets(self, store, sample_image):
        from movie_os.asset_store import AssetType
        store.create(AssetType.IMAGE, sample_image, tags=["a"])
        store.create(AssetType.IMAGE, sample_image, tags=["b"])
        all_assets = store.list()
        assert len(all_assets) == 2

    def test_list_filtered_by_type(self, store, sample_image, tmp_path):
        from movie_os.asset_store import AssetType
        store.create(AssetType.IMAGE, sample_image)
        audio_path = tmp_path / "voice.wav"
        audio_path.write_bytes(b"RIFF" + b"x" * 100)
        store.create(AssetType.AUDIO, audio_path)
        images = store.list(type=AssetType.IMAGE)
        audios = store.list(type=AssetType.AUDIO)
        assert len(images) == 1
        assert len(audios) == 1

    def test_list_excludes_deleted_by_default(self, store, sample_image):
        from movie_os.asset_store import AssetType
        a = store.create(AssetType.IMAGE, sample_image)
        store.soft_delete(a.id)
        assert store.list() == []
        assert len(store.list(include_deleted=True)) == 1


class TestAssetStoreUpdate:
    def test_tag_adds_tags(self, store, sample_image):
        from movie_os.asset_store import AssetType
        a = store.create(AssetType.IMAGE, sample_image, tags=["x"])
        a = store.tag(a.id, "y", "z")
        assert set(a.tags) == {"x", "y", "z"}

    def test_untag_removes_tags(self, store, sample_image):
        from movie_os.asset_store import AssetType
        a = store.create(AssetType.IMAGE, sample_image, tags=["x", "y", "z"])
        a = store.untag(a.id, "y")
        assert set(a.tags) == {"x", "z"}

    def test_soft_delete(self, store, sample_image):
        from movie_os.asset_store import AssetType
        a = store.create(AssetType.IMAGE, sample_image)
        store.soft_delete(a.id)
        assert store.get_or_none(a.id) is None
        # The file is still on disk
        assert a.path.exists()


class TestAssetStoreVersions:
    def test_create_version_bumps_version(self, store, sample_image, tmp_path):
        from movie_os.asset_store import AssetType
        a = store.create(AssetType.IMAGE, sample_image)
        new_file = tmp_path / "image_v2.png"
        new_file.write_bytes(b"v2-content")
        a2 = store.create_version(a.id, new_file, notes="better contrast")
        assert a2.current_version == 2
        assert a2.path.read_bytes() == b"v2-content"
        # Original v1 file still exists
        assert a.path.exists()
        assert a.path.read_bytes() == sample_image.read_bytes()

    def test_versions_returns_history(self, store, sample_image, tmp_path):
        from movie_os.asset_store import AssetType
        a = store.create(AssetType.IMAGE, sample_image)
        for i in range(2, 4):
            f = tmp_path / f"v{i}.png"
            f.write_bytes(f"v{i}".encode())
            store.create_version(a.id, f)
        versions = store.versions(a.id)
        assert [v.version for v in versions] == [1, 2, 3]

    def test_rollback_restores_prior_version(self, store, sample_image, tmp_path):
        from movie_os.asset_store import AssetType
        a = store.create(AssetType.IMAGE, sample_image)
        v2 = tmp_path / "v2.png"
        v2.write_bytes(b"v2-content")
        a = store.create_version(a.id, v2)
        assert a.current_version == 2
        rolled = store.rollback(a.id, target_version=1)
        assert rolled.current_version == 1
        # v1 is the v1 file (still on disk)
        assert rolled.path.read_bytes() == sample_image.read_bytes()
        # v2 still on disk
        assert a.path.exists()
        assert a.path.read_bytes() == b"v2-content"

    def test_rollback_to_missing_version_raises(self, store, sample_image):
        from movie_os.asset_store import AssetType
        a = store.create(AssetType.IMAGE, sample_image)
        with pytest.raises(KeyError):
            store.rollback(a.id, target_version=99)


class TestInMemory:
    def test_in_memory_store_works(self, tmp_path):
        """The store works with :memory: SQLite (for tests/embedded use)."""
        from movie_os.asset_store import AssetStore, AssetType
        store = AssetStore(db_path=":memory:", files_dir=tmp_path / "files")
        img = tmp_path / "x.png"
        img.write_bytes(b"x" * 100)
        a = store.create(AssetType.IMAGE, img)
        assert store.get(a.id).id == a.id
        store.close()
