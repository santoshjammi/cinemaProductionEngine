"""Tests for the Movie OS Phase 6 deliverables (Character & Environment Memory).

These tests verify:
- EntityStorage CRUD operations
- CharacterRegistry CRUD, search, hero images
- EnvironmentRegistry CRUD, search, hero + variant images
- File-based persistence
- CLI commands (character list, show, delete; environment list, show, delete)
- Backward compat: existing tests still pass

Run with:
    cd /Users/santosh/Desktop/projects/videoGen
    ./venv/bin/python -m pytest movie_os/tests/test_phase6.py -v --override-ini="addopts="
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pytest


# ---------------------------------------------------------------------------
# EntityStorage tests
# ---------------------------------------------------------------------------

class TestEntityStorage:
    """The filesystem storage layer."""

    def test_create_storage(self, tmp_path):
        from movie_os.data_layer import EntityStorage
        storage = EntityStorage(tmp_path / "chars", "character.yaml")
        assert storage.root.exists()

    def test_save_and_load(self, tmp_path):
        from movie_os.data_layer import EntityStorage
        storage = EntityStorage(tmp_path / "chars", "character.yaml")
        data = {"name": "Jane", "age": 30}
        path = storage.save("jane", data)
        assert path.exists()
        loaded = storage.load("jane")
        assert loaded["name"] == "Jane"
        assert loaded["age"] == 30

    def test_list_keys(self, tmp_path):
        from movie_os.data_layer import EntityStorage
        storage = EntityStorage(tmp_path / "chars", "character.yaml")
        storage.save("jane", {"name": "Jane"})
        storage.save("bob", {"name": "Bob"})
        storage.save("alice", {"name": "Alice"})
        assert storage.list_keys() == ["alice", "bob", "jane"]

    def test_has(self, tmp_path):
        from movie_os.data_layer import EntityStorage
        storage = EntityStorage(tmp_path / "chars", "character.yaml")
        storage.save("jane", {"name": "Jane"})
        assert storage.has("jane")
        assert not storage.has("bob")

    def test_delete(self, tmp_path):
        from movie_os.data_layer import EntityStorage
        storage = EntityStorage(tmp_path / "chars", "character.yaml")
        storage.save("jane", {"name": "Jane"})
        assert storage.delete("jane") is True
        assert not storage.has("jane")
        assert storage.delete("jane") is False  # already gone

    def test_load_missing_returns_none(self, tmp_path):
        from movie_os.data_layer import EntityStorage
        storage = EntityStorage(tmp_path / "chars", "character.yaml")
        assert storage.load("nonexistent") is None

    def test_list_files(self, tmp_path):
        from movie_os.data_layer import EntityStorage
        storage = EntityStorage(tmp_path / "chars", "character.yaml")
        storage.save("jane", {"name": "Jane"})
        # Manually create some image files
        (tmp_path / "chars" / "jane" / "hero.png").write_bytes(b"\x89PNG")
        (tmp_path / "chars" / "jane" / "side.png").write_bytes(b"\x89PNG")
        files = storage.list_files("jane")
        assert len(files) == 2
        names = {f.name for f in files}
        assert names == {"hero.png", "side.png"}


# ---------------------------------------------------------------------------
# CharacterRegistry tests
# ---------------------------------------------------------------------------

class TestCharacterRegistry:
    """The character registry."""

    def _make_char(self, key="jane_doe", name="Jane Doe", age=30, gender="female"):
        from movie_os.domain import CharacterDNA, PhysicalAppearance, Gender
        return CharacterDNA(
            key=key, name=name, role="protagonist",
            physical=PhysicalAppearance(age=age, gender=Gender(gender), visual_anchor="woman, 30s"),
        )

    def test_save_and_get(self, tmp_path):
        from movie_os.data_layer import CharacterRegistry
        reg = CharacterRegistry(tmp_path / "chars")
        char = self._make_char()
        reg.save(char)
        loaded = reg.get("jane_doe")
        assert loaded is not None
        assert loaded.name == "Jane Doe"
        assert loaded.physical.age == 30

    def test_has_and_contains(self, tmp_path):
        from movie_os.data_layer import CharacterRegistry
        reg = CharacterRegistry(tmp_path / "chars")
        reg.save(self._make_char())
        assert reg.has("jane_doe")
        assert "jane_doe" in reg
        assert not reg.has("bob")
        assert "bob" not in reg

    def test_list(self, tmp_path):
        from movie_os.data_layer import CharacterRegistry
        reg = CharacterRegistry(tmp_path / "chars")
        reg.save(self._make_char("jane_doe", "Jane Doe", 30, "female"))
        reg.save(self._make_char("ethan_morrison", "Ethan Morrison", 32, "male"))
        reg.save(self._make_char("bob_smith", "Bob Smith", 25, "male"))
        chars = reg.list()
        assert len(chars) == 3
        keys = {c.key for c in chars}
        assert keys == {"jane_doe", "ethan_morrison", "bob_smith"}

    def test_find_by_name(self, tmp_path):
        from movie_os.data_layer import CharacterRegistry
        reg = CharacterRegistry(tmp_path / "chars")
        reg.save(self._make_char("jane_doe", "Jane Doe"))
        reg.save(self._make_char("ethan_morrison", "Ethan Morrison"))
        # Exact match
        found = reg.find_by_name("Jane Doe")
        assert found is not None
        assert found.key == "jane_doe"
        # Case-insensitive partial
        found = reg.find_by_name("ethan")
        assert found.key == "ethan_morrison"
        # Not found
        assert reg.find_by_name("nonexistent") is None

    def test_hero_image(self, tmp_path):
        from movie_os.data_layer import CharacterRegistry
        reg = CharacterRegistry(tmp_path / "chars")
        reg.save(self._make_char())
        # No hero yet
        assert reg.get_hero_image_path("jane_doe") is None
        assert not reg.has_hero_image("jane_doe")
        # Save a hero (use a fake PNG file)
        hero_source = tmp_path / "source.png"
        hero_source.write_bytes(b"\x89PNG\r\n\x1a\n")
        path = reg.save_hero_image("jane_doe", hero_source)
        assert path.exists()
        assert reg.has_hero_image("jane_doe")
        # Read it back
        loaded = reg.get_hero_image_path("jane_doe")
        assert loaded.exists()

    def test_save_hero_for_missing_character_raises(self, tmp_path):
        from movie_os.data_layer import CharacterRegistry
        reg = CharacterRegistry(tmp_path / "chars")
        with pytest.raises(FileNotFoundError):
            reg.save_hero_image("nonexistent", tmp_path / "x.png")

    def test_delete(self, tmp_path):
        from movie_os.data_layer import CharacterRegistry
        reg = CharacterRegistry(tmp_path / "chars")
        reg.save(self._make_char())
        assert reg.delete("jane_doe") is True
        assert not reg.has("jane_doe")

    def test_len_and_iter(self, tmp_path):
        from movie_os.data_layer import CharacterRegistry
        reg = CharacterRegistry(tmp_path / "chars")
        reg.save(self._make_char("a", "A"))
        reg.save(self._make_char("b", "B"))
        reg.save(self._make_char("c", "C"))
        assert len(reg) == 3
        keys = [c.key for c in reg]
        assert keys == ["a", "b", "c"]


# ---------------------------------------------------------------------------
# EnvironmentRegistry tests
# ---------------------------------------------------------------------------

class TestEnvironmentRegistry:
    """The environment registry."""

    def _make_env(self, key="bedroom", name="Bedroom"):
        from movie_os.domain import EnvironmentDNA, LightingProfile, ArchitecturalStyle
        return EnvironmentDNA(
            key=key, name=name,
            location_type="interior",
            architectural_style=ArchitecturalStyle.MODERN,
            lighting=LightingProfile(primary_source="lamp"),
            description="A modest bedroom",
        )

    def test_save_and_get(self, tmp_path):
        from movie_os.data_layer import EnvironmentRegistry
        reg = EnvironmentRegistry(tmp_path / "envs")
        env = self._make_env()
        reg.save(env)
        loaded = reg.get("bedroom")
        assert loaded is not None
        assert loaded.name == "Bedroom"
        assert loaded.architectural_style == "modern"

    def test_hero_image(self, tmp_path):
        from movie_os.data_layer import EnvironmentRegistry
        reg = EnvironmentRegistry(tmp_path / "envs")
        reg.save(self._make_env())
        hero_source = tmp_path / "src.png"
        hero_source.write_bytes(b"\x89PNG")
        reg.save_hero_image("bedroom", hero_source)
        assert reg.has_hero_image("bedroom")

    def test_variant_images(self, tmp_path):
        from movie_os.data_layer import EnvironmentRegistry
        reg = EnvironmentRegistry(tmp_path / "envs")
        reg.save(self._make_env())
        # Save variants
        for variant in ["night", "golden_hour", "rain"]:
            src = tmp_path / f"{variant}_src.png"
            src.write_bytes(b"\x89PNG")
            reg.save_variant_image("bedroom", variant, src)
        # Look them up
        assert reg.get_variant_image_path("bedroom", "night") is not None
        assert reg.get_variant_image_path("bedroom", "golden_hour") is not None
        assert reg.get_variant_image_path("bedroom", "rain") is not None
        # Missing variant
        assert reg.get_variant_image_path("bedroom", "storm") is None

    def test_find_by_name(self, tmp_path):
        from movie_os.data_layer import EnvironmentRegistry
        reg = EnvironmentRegistry(tmp_path / "envs")
        reg.save(self._make_env("bedroom", "James's Bedroom"))
        reg.save(self._make_env("office", "Therapist Office"))
        found = reg.find_by_name("therapist")
        assert found.key == "office"

    def test_delete(self, tmp_path):
        from movie_os.data_layer import EnvironmentRegistry
        reg = EnvironmentRegistry(tmp_path / "envs")
        reg.save(self._make_env())
        assert reg.delete("bedroom") is True
        assert not reg.has("bedroom")


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

class TestCLI:
    """The character and environment CLI commands."""

    def test_character_list_empty(self, capsys, tmp_path):
        from movie_os.data_layer import CharacterRegistry
        from movie_os.data_layer.character_registry import set_default_registry

        reg = CharacterRegistry(tmp_path / "chars")
        set_default_registry(reg)

        from movie_os import cli
        rc = cli.main(["character", "list"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "No characters" in out

    def test_character_list_with_data(self, capsys, tmp_path):
        from movie_os.data_layer import CharacterRegistry
        from movie_os.data_layer.character_registry import set_default_registry
        from movie_os.cli import main
        from movie_os.domain import CharacterDNA, PhysicalAppearance, Gender

        reg = CharacterRegistry(tmp_path / "chars")
        reg.save(CharacterDNA(
            key="jane_doe", name="Jane Doe", role="protagonist",
            physical=PhysicalAppearance(age=30, gender=Gender.FEMALE, visual_anchor="woman"),
        ))
        set_default_registry(reg)

        rc = main(["character", "list"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "jane_doe" in out
        assert "Jane Doe" in out

    def test_character_show(self, capsys, tmp_path):
        from movie_os.data_layer import CharacterRegistry
        from movie_os.data_layer.character_registry import set_default_registry
        from movie_os.cli import main
        from movie_os.domain import CharacterDNA, PhysicalAppearance, Gender

        reg = CharacterRegistry(tmp_path / "chars")
        reg.save(CharacterDNA(
            key="jane_doe", name="Jane Doe", role="protagonist",
            physical=PhysicalAppearance(age=30, gender=Gender.FEMALE, visual_anchor="woman"),
        ))
        set_default_registry(reg)

        rc = main(["character", "show", "jane_doe"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "Key:        jane_doe" in out
        assert "Name:       Jane Doe" in out
        assert "Age:        30" in out

    def test_character_show_missing(self, capsys, tmp_path):
        from movie_os.data_layer import CharacterRegistry
        from movie_os.data_layer.character_registry import set_default_registry
        from movie_os.cli import main

        reg = CharacterRegistry(tmp_path / "chars")
        set_default_registry(reg)

        rc = main(["character", "show", "nonexistent"])
        assert rc == 1
        err = capsys.readouterr().err
        assert "not found" in err

    def test_character_delete(self, capsys, tmp_path):
        from movie_os.data_layer import CharacterRegistry
        from movie_os.data_layer.character_registry import set_default_registry
        from movie_os.cli import main
        from movie_os.domain import CharacterDNA, PhysicalAppearance, Gender

        reg = CharacterRegistry(tmp_path / "chars")
        reg.save(CharacterDNA(
            key="jane_doe", name="Jane Doe",
            physical=PhysicalAppearance(age=30, gender=Gender.FEMALE, visual_anchor="w"),
        ))
        set_default_registry(reg)

        rc = main(["character", "delete", "jane_doe"])
        assert rc == 0
        assert not reg.has("jane_doe")

    def test_environment_list_empty(self, capsys, tmp_path):
        from movie_os.data_layer import EnvironmentRegistry
        from movie_os.data_layer.environment_registry import set_default_registry
        from movie_os.cli import main
        reg = EnvironmentRegistry(tmp_path / "envs")
        set_default_registry(reg)

        rc = main(["environment", "list"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "No environments" in out

    def test_environment_list_with_data(self, capsys, tmp_path):
        from movie_os.data_layer import EnvironmentRegistry
        from movie_os.data_layer.environment_registry import set_default_registry
        from movie_os.cli import main
        from movie_os.domain import EnvironmentDNA, LightingProfile, ArchitecturalStyle

        reg = EnvironmentRegistry(tmp_path / "envs")
        reg.save(EnvironmentDNA(
            key="bedroom", name="James's Bedroom",
            location_type="interior",
            architectural_style=ArchitecturalStyle.MODERN,
            lighting=LightingProfile(primary_source="lamp"),
        ))
        set_default_registry(reg)

        rc = main(["environment", "list"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "bedroom" in out
        assert "James's Bedroom" in out

    def test_environment_show(self, capsys, tmp_path):
        from movie_os.data_layer import EnvironmentRegistry
        from movie_os.data_layer.environment_registry import set_default_registry
        from movie_os.cli import main
        from movie_os.domain import EnvironmentDNA, LightingProfile, ArchitecturalStyle

        reg = EnvironmentRegistry(tmp_path / "envs")
        reg.save(EnvironmentDNA(
            key="bedroom", name="Bedroom",
            location_type="interior",
            architectural_style=ArchitecturalStyle.MODERN,
            lighting=LightingProfile(primary_source="lamp"),
        ))
        set_default_registry(reg)

        rc = main(["environment", "show", "bedroom"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "Key:        bedroom" in out
        assert "Name:       Bedroom" in out


# ---------------------------------------------------------------------------
# Backward compat
# ---------------------------------------------------------------------------

class TestBackwardCompat:
    """The existing code (story_factory, pipeline, etc.) still works."""

    def test_story_factory_still_works(self):
        from story_factory import generate_dna, generate_context
        import inspect
        assert "synopsis" in inspect.signature(generate_dna).parameters

    def test_providers_still_work(self):
        from movie_os.providers import (
            SDXLLocalProvider, FluxComfyUIProvider, EdgeTTSProvider,
        )
        from movie_os.providers import registry
        assert isinstance(registry.make("image", "sdxl_local", {}, 0.0), SDXLLocalProvider)
        assert isinstance(registry.make("image", "flux_comfyui", {}, 0.0), FluxComfyUIProvider)
        assert isinstance(registry.make("voice", "edge_tts", {}, 0.0), EdgeTTSProvider)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
