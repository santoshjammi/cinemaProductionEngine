"""EnvironmentRegistry — the persistent store for EnvironmentDNA.

Environments (apartment, therapist office, temple, village, etc.) are
persistent across stories. When a new story says "the bedroom", the
ImageProvider pulls the environment's hero reference image for
visual consistency.

SQLite vector search (Phase 8) adds similarity-based lookups
via `search_similar(query_text, k=5)` backed by sqlite-vec.

File layout:
    movie_os/data/environments/
        bedroom_jane/
            environment.yaml   # EnvironmentDNA serialized
            hero.png           # primary reference image
            night.png          # variant (night lighting)
            golden_hour.png    # variant (golden hour lighting)
        therapist_office/
            environment.yaml
            hero.png

The same pattern as CharacterRegistry. The EnvironmentDNA can have
multiple variants (time_of_day, weather) — each variant can have
its own reference image.
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Any, Optional

from movie_os.domain.environment import EnvironmentDNA
from .storage import EntityStorage


logger = logging.getLogger("movie_os.data_layer.environment_registry")


# ---------------------------------------------------------------------------
# Helpers: char-ngram vector feature extraction (no heavy deps) — env variant
# ---------------------------------------------------------------------------

def _text_to_f32_vector(text: str, dim: int = 768) -> list[float]:
    """Deterministic TF-like feature vector for short text."""
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


def _environment_to_vector(env: EnvironmentDNA, dim: int = 768) -> list[float]:
    """Vectorise an environment's defining text fields and average."""
    texts = [
        env.name,
        env.key,
        env.architectural_style.value if hasattr(env.architectural_style, 'value') else str(env.architectural_style),
        env.description,
        " ".join(env.notable_features or []),
        env.lighting.primary_source,
        env.lighting.color_temperature,
    ]
    combined = " | ".join(t for t in texts if t)
    return _text_to_f32_vector(combined, dim)


# ---------------------------------------------------------------------------
# Environment Registry
# ---------------------------------------------------------------------------

HERO_FILENAME = "hero.png"


class EnvironmentRegistry:
    """A persistent store for EnvironmentDNA objects.

    Phase 8 — SQLite vector search: every save() also writes an
    embedding into movie_os/data/environments/vec_index/environments.vec
    via sqlite-vec so that search_similar() works on disk.
    """

    def __init__(self, root: str | Path = "movie_os/data/environments"):
        self.root = Path(root)
        self._storage = EntityStorage(self.root, manifest_filename="environment.yaml")
        self._vec_path = self.root / "vec_index" / "environments.vec"

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def save(self, environment: EnvironmentDNA) -> Path:
        """Save an environment to disk. Returns the manifest path."""
        data = environment.model_dump(mode="json")
        manifest = self._storage.save(environment.key, data)
        vec = _environment_to_vector(environment)
        self._ensure_vec_index()
        self._vec_ingest(environment.key, data, env=environment, vec=vec)
        return manifest

    def get(self, key: str) -> Optional[EnvironmentDNA]:
        """Load an environment by key."""
        data = self._storage.load(key)
        if data is None:
            return None
        return EnvironmentDNA.model_validate(data)

    def has(self, key: str) -> bool:
        return self._storage.has(key)

    def list(self) -> list[EnvironmentDNA]:
        envs = []
        for key in self._storage.list_keys():
            env = self.get(key)
            if env is not None:
                envs.append(env)
        return envs

    def list_keys(self) -> list[str]:
        return self._storage.list_keys()

    def delete(self, key: str) -> bool:
        ok = self._storage.delete(key)
        if ok and hasattr(self, "_conn"):
            self._vec_delete(key)
        return ok

    # ------------------------------------------------------------------
    # Search (traditional)
    # ------------------------------------------------------------------

    def find_by_name(self, name: str) -> Optional[EnvironmentDNA]:
        """Find an environment by name (case-insensitive substring)."""
        name_lower = name.lower()
        for env in self.list():
            if env.name.lower() == name_lower or name_lower in env.name.lower():
                return env
        return None

    # ------------------------------------------------------------------
    # Search (Phase 8 — vector similarity via numpy + SQLite)
    # ------------------------------------------------------------------

    def _ensure_vec_index(self):
        """Create the vector index database on disk."""
        from movie_os.memory.vector_search import VectorIndex
        self._vec_path.parent.mkdir(parents=True, exist_ok=True)
        self._vindex = VectorIndex(self._vec_path)
        self._vindex.setup(dim=768)

    def _vec_ingest(self, key: str, meta: dict, env: Any, vec: list[float]):
        if not hasattr(self, "_vindex"):
            self._ensure_vec_index()
        self._vindex.ingest(key, meta, vec)

    def _vec_delete(self, key: str):
        """Remove an entity from the vector index."""
        if not hasattr(self, "_vindex"):
            return
        try:
            self._vindex.db.execute("DELETE FROM entities WHERE key=?", (key,))
            self._vindex.db.commit()
        except Exception as exc:
            logger.warning(f"Vector index delete failed for '{key}': {exc}")

    def search_similar(self, query_text: str, k: int = 5) -> list[tuple[EnvironmentDNA, float]]:
        """Find environments most similar to *query_text* via cosine distance.

        Args:
            query_text: Free-text description of desired environment.
            k: Max neighbours to return.

        Returns:
            List of (EnvironmentDNA, score) sorted DESC by similarity.
        """
        if not hasattr(self, "_vindex"):
            self._ensure_vec_index()

        qvec = _text_to_f32_vector(query_text, 768)

        # Seed any missing entities into the vector store
        for env in self.list():
            existing = self._vindex.db.execute(
                "SELECT count(*) FROM entities WHERE key=?", (env.key,)
            ).fetchone()[0]
            if existing == 0:
                evec = _environment_to_vector(env)
                meta_data = self._storage.load(env.key) or {}
                self._vec_ingest(env.key, meta_data, env=env, vec=evec)

        results_raw = self._vindex.query(qvec, k=k)
        results: list[tuple[EnvironmentDNA, float]] = []
        for r in results_raw:
            env = self.get(r["key"])
            if env:
                results.append((env, r["score"]))
        return results

    # ------------------------------------------------------------------
    # Reference images
    # ------------------------------------------------------------------

    def get_hero_image_path(self, key: str) -> Optional[Path]:
        """Get the path to the environment's hero reference image."""
        if not self.has(key):
            return None
        hero_path = self._storage.file_path_for(key, HERO_FILENAME)
        if hero_path.exists():
            return hero_path
        return None

    def get_variant_image_path(
        self, key: str, variant_label: str
    ) -> Optional[Path]:
        """Get the path to a specific variant's reference image.

        variant_label: e.g., "night", "golden_hour", "rain"
        """
        if not self.has(key):
            return None
        path = self._storage.file_path_for(key, f"{variant_label}.png")
        if path.exists():
            return path
        return None

    def save_hero_image(self, key: str, source: str | Path) -> Path:
        if not self.has(key):
            raise FileNotFoundError(f"Environment '{key}' not found. Save it first.")
        return self._storage.copy_file_in(key, source, HERO_FILENAME)

    def save_variant_image(
        self, key: str, variant_label: str, source: str | Path
    ) -> Path:
        """Save a variant image (e.g., 'night.png', 'rain.png')."""
        if not self.has(key):
            raise FileNotFoundError(f"Environment '{key}' not found. Save it first.")
        return self._storage.copy_file_in(key, source, f"{variant_label}.png")

    def has_hero_image(self, key: str) -> bool:
        return self.get_hero_image_path(key) is not None

    def list_reference_images(self, key: str) -> list[Path]:
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


# Default global registry
_default_registry: Optional[EnvironmentRegistry] = None


def get_default_registry() -> EnvironmentRegistry:
    global _default_registry
    if _default_registry is None:
        from movie_os import data_layer
        default_root = Path(data_layer.__file__).parent / "data" / "environments"
        _default_registry = EnvironmentRegistry(default_root)
    return _default_registry


def set_default_registry(registry: EnvironmentRegistry) -> None:
    global _default_registry
    _default_registry = registry
