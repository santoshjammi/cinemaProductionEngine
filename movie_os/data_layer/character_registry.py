"""CharacterRegistry — the persistent store for CharacterDNA.

Characters are persistent across stories. When a new story references
a character by key, the ImageProvider automatically pulls the
character's hero reference image for img2img / IPAdapter consistency.

SQLite vector search (Phase 8) adds similarity-based lookups
via `search_similar(query_text, k=5)` backed by sqlite-vec.

Public API:
    from movie_os.data_layer import CharacterRegistry

    registry = CharacterRegistry("movie_os/data/characters")

    # Create or load
    char = CharacterDNA(key="jane_doe", name="Jane Doe", ...)
    registry.save(char)
    # Automatically builds vector index on first save() if not present

    # Look up
    jane = registry.get("jane_doe")
    ethan = registry.find_by_name("Ethan Morrison")

    # Vector similarity search (Phase 8)
    similar = registry.search_similar("brave young woman", k=3)

    # List all
    for char in registry.list():
        print(char.key, char.name)

The Character DNA is stored as YAML. The hero reference image is a
single PNG (we can add multiple later).
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Any, Optional

from movie_os.domain.character import CharacterDNA
from .storage import EntityStorage


logger = logging.getLogger("movie_os.data_layer.character_registry")


# ---------------------------------------------------------------------------
# Helpers: char-ngram vector feature extraction (no heavy deps)
# ---------------------------------------------------------------------------

def _text_to_f32_vector(text: str, dim: int = 768) -> list[float]:
    """Deterministic TF-like feature vector for short text.

    Uses character 4-gram hashing into `dim` buckets, L2-normalised.
    This is a minimal embedding that works without any embedding model.
    """
    vec: list[float] = [0.0] * dim
    if len(text) < 4:
        grams = [text.lower()]
    else:
        grams = [text[i:i + 4].lower() for i in range(len(text) - 3)]
    for gram in grams:
        h = int(hashlib.md5(gram.encode()).hexdigest(), 16) % dim
        vec[h] += 1.0
    norm = sum(v ** 2 for v in vec) ** 0.5 or 1.0
    return [v / norm for v in vec]


def _character_to_vector(dna: CharacterDNA, dim: int = 768) -> list[float]:
    """Vectorise a character's defining text fields and average."""
    texts = [
        dna.name,
        dna.role,
        " ".join(dna.tags),
        dna.physical.visual_anchor,
        " ".join(dna.psychological.personality_traits or []),
        dna.psychological.core_fear,
        dna.psychological.core_desire,
        dna.speech.speaking_style,
    ]
    combined = " | ".join(t for t in texts if t)
    return _text_to_f32_vector(combined, dim)


# ---------------------------------------------------------------------------
# Character Registry
# ---------------------------------------------------------------------------

HERO_FILENAME = "hero.png"


class CharacterRegistry:
    """A persistent store for CharacterDNA objects.

    Characters live as directories under a root path. Each directory
    contains a character.yaml (the CharacterDNA serialized) and any
    reference images.

    Phase 8 — SQLite vector search: every save() also writes an
    embedding into movie_os/data/characters/vec_index/characters.vec
    via sqlite-vec so that search_similar() works on disk.
    """

    def __init__(self, root: str | Path = "movie_os/data/characters"):
        self.root = Path(root)
        self._storage = EntityStorage(self.root, manifest_filename="character.yaml")
        self._vec_path = self.root / "vec_index" / "characters.vec"

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def save(self, character: CharacterDNA) -> Path:
        """Save a character to disk. Returns the manifest path."""
        data = character.model_dump(mode="json")
        manifest = self._storage.save(character.key, data)
        # Phase 8 — write vector index entry too
        vec = _character_to_vector(character)
        self._ensure_vec_index()
        self._vec_ingest(character.key, data, vec)
        return manifest

    def get(self, key: str) -> Optional[CharacterDNA]:
        """Load a character by key. Returns None if not found."""
        data = self._storage.load(key)
        if data is None:
            return None
        return CharacterDNA.model_validate(data)

    def has(self, key: str) -> bool:
        """Check if a character with this key exists."""
        return self._storage.has(key)

    def list(self) -> list[CharacterDNA]:
        """List all characters (sorted by key)."""
        characters = []
        for key in self._storage.list_keys():
            char = self.get(key)
            if char is not None:
                characters.append(char)
        return characters

    def list_keys(self) -> list[str]:
        """List all character keys (sorted)."""
        return self._storage.list_keys()

    def delete(self, key: str) -> bool:
        """Delete a character. Returns True if it existed."""
        ok = self._storage.delete(key)
        # Phase 8 — remove from vector index too
        if ok and self._vec_path.exists():
            self._vec_delete(key)
        return ok

    # ------------------------------------------------------------------
    # Search (traditional)
    # ------------------------------------------------------------------

    def find_by_name(self, name: str) -> Optional[CharacterDNA]:
        """Find a character by name (case-insensitive substring match)."""
        name_lower = name.lower()
        for char in self.list():
            if char.name.lower() == name_lower or name_lower in char.name.lower():
                return char
        return None

    def find_by_tag(self, tag: str) -> list[CharacterDNA]:
        """Find all characters with a given tag."""
        return [c for c in self.list() if tag in c.tags]

    # ------------------------------------------------------------------
    # Search (Phase 8 — vector similarity via numpy + SQLite)
    # ------------------------------------------------------------------

    def _ensure_vec_index(self):
        """Create the vector index database on disk."""
        from movie_os.memory.vector_search import VectorIndex
        self._vec_path.parent.mkdir(parents=True, exist_ok=True)
        self._vindex = VectorIndex(self._vec_path)
        self._vindex.setup(dim=768)

    def _vec_ingest(self, key: str, meta: dict, vec: list[float]):
        if not hasattr(self, "_vindex"):
            self._ensure_vec_index()
        self._vindex.ingest(key, meta, vec)

    def _vec_delete(self, key: str):
        """Remove an entity from the vector index."""
        if not hasattr(self, "_vindex"):
            return
        try:
            cur = self._vindex.db.execute("DELETE FROM entities WHERE key=?", (key,))
            self._vindex.db.commit()
        except Exception as exc:
            logger.warning(f"Vector index delete failed for '{key}': {exc}")

    def search_similar(self, query_text: str, k: int = 5) -> list[tuple[CharacterDNA, float]]:
        """Find characters most similar to *query_text* via cosine distance.

        If the vector index doesn't exist yet, builds it by scanning all
        entities (only on first search).

        Args:
            query_text: Free-text description of desired character.
            k: Max number of neighbours to return.

        Returns:
            List of ``(CharacterDNA, similarity_score)`` sorted by score DESC.
        """
        # Lazy-init index if needed
        if not hasattr(self, "_vindex"):
            self._ensure_vec_index()

        qvec = _text_to_f32_vector(query_text, 768)

        # First run: seed all existing entities
        for char in self.list():
            existing = self._vindex.db.execute(
                "SELECT count(*) FROM entities WHERE key=?", (char.key,)
            ).fetchone()[0]
            if existing == 0:
                cvec = _character_to_vector(char)
                self._vec_ingest(char.key, CharacterDNA.model_validate(
                    self._storage.load(char.key) or {}
                ).model_dump(mode="json"), cvec)

        # Query
        results_raw = self._vindex.query(qvec, k=k)
        results: list[tuple[CharacterDNA, float]] = []
        for r in results_raw:
            char = self.get(r["key"])
            if char:
                results.append((char, r["score"]))
        return results

    # ------------------------------------------------------------------
    # Reference images
    # ------------------------------------------------------------------

    def get_hero_image_path(self, key: str) -> Optional[Path]:
        """Get the path to a character's hero reference image."""
        if not self.has(key):
            return None
        hero_path = self._storage.file_path_for(key, HERO_FILENAME)
        if hero_path.exists():
            return hero_path
        return None

    def save_hero_image(self, key: str, source: str | Path) -> Path:
        """Save a hero reference image for a character."""
        if not self.has(key):
            raise FileNotFoundError(f"Character '{key}' not found. Save the character first.")
        return self._storage.copy_file_in(key, source, HERO_FILENAME)

    def has_hero_image(self, key: str) -> bool:
        """Check if a character has a hero reference image."""
        return self.get_hero_image_path(key) is not None

    def list_reference_images(self, key: str) -> list[Path]:
        """List all reference images for a character (including the hero)."""
        return self._storage.list_files(key)

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self.list())

    def __contains__(self, key: str) -> bool:
        return self.has(key)

    def __iter__(self):
        return iter(self.list())

    def close(self):
        """Close the vector index connection (best-effort)."""
        if hasattr(self, "_vindex"):
            try:
                self._vindex.close()
            except Exception:
                pass


# A default global registry (lazily initialized)
_default_registry: Optional[CharacterRegistry] = None


def get_default_registry() -> CharacterRegistry:
    """Get the global default character registry."""
    global _default_registry
    if _default_registry is None:
        from movie_os import data_layer
        default_root = Path(data_layer.__file__).parent / "data" / "characters"
        _default_registry = CharacterRegistry(default_root)
    return _default_registry


def set_default_registry(registry: CharacterRegistry) -> None:
    """Set the global default registry."""
    global _default_registry
    _default_registry = registry
