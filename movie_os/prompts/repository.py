"""PromptRepository — the central index of all prompt templates.

The Repository loads prompt YAML files from a directory tree and
indexes them by:
  - id (e.g., "image.cinematic.v1") — primary key
  - capability (e.g., "image", "story") — for finding all prompts
    that serve a capability
  - supported_models (e.g., ["flux-dev", "sdxl"]) — for model-specific
    selection (the most capable prompt for a given model)

The Repository is the discovery layer. It doesn't render prompts
(that's the Renderer's job) — it just finds them.

Usage:

    from movie_os.prompts import PromptRepository

    repo = PromptRepository("movie_os/prompts")
    prompt = repo.get("image.cinematic.v1")
    print(prompt.body)

    # All image prompts
    for p in repo.by_capability("image"):
        print(p.metadata.id, p.metadata.version)

    # All prompts that support flux-dev
    for p in repo.by_model("flux-dev"):
        print(p.metadata.id)

    # The latest version of an image prompt
    latest = repo.latest("image", "cinematic")
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Iterator, Optional

from movie_os.domain.prompt import PromptTemplate
from .loader import load_prompt_template


logger = logging.getLogger("movie_os.prompts.repository")


class PromptNotFoundError(KeyError):
    """Raised when a prompt ID is not in the repository."""
    def __init__(self, prompt_id: str):
        super().__init__(prompt_id)
        self.prompt_id = prompt_id


class PromptRepository:
    """The central index of prompt templates.

    Loads from a directory of YAML files. Indexes by id, capability, and
    supported model. Supports queries for the latest version of a prompt.
    """

    def __init__(self, root: str | Path | None = None):
        self.root = Path(root) if root else None
        self._templates: dict[str, PromptTemplate] = {}

        if self.root is not None:
            self.load(self.root)

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def load(self, root: str | Path) -> int:
        """Load all YAML prompt files from `root` (recursively).

        Returns the number of templates loaded. Existing templates with
        the same ID are overwritten.
        """
        root = Path(root)
        if not root.exists():
            logger.warning(f"Prompt root does not exist: {root}")
            return 0

        count = 0
        for yaml_file in root.rglob("*.yaml"):
            try:
                template = load_prompt_template(yaml_file)
                self._templates[template.metadata.id] = template
                count += 1
            except Exception as e:
                logger.warning(f"Failed to load prompt {yaml_file}: {e}")

        logger.info(f"Loaded {count} prompt templates from {root}")
        return count

    def add(self, template: PromptTemplate) -> None:
        """Add a template directly (useful for tests)."""
        self._templates[template.metadata.id] = template

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get(self, prompt_id: str) -> PromptTemplate:
        """Get a prompt by its exact ID. Raises PromptNotFoundError if missing."""
        if prompt_id not in self._templates:
            raise PromptNotFoundError(prompt_id)
        return self._templates[prompt_id]

    def try_get(self, prompt_id: str) -> Optional[PromptTemplate]:
        """Get a prompt by ID, or None if not found."""
        return self._templates.get(prompt_id)

    def has(self, prompt_id: str) -> bool:
        """Check if a prompt ID is in the repository."""
        return prompt_id in self._templates

    def __contains__(self, prompt_id: str) -> bool:
        return self.has(prompt_id)

    def __len__(self) -> int:
        return len(self._templates)

    def __iter__(self) -> Iterator[PromptTemplate]:
        return iter(self._templates.values())

    # ------------------------------------------------------------------
    # Querying
    # ------------------------------------------------------------------

    def by_capability(self, capability: str) -> list[PromptTemplate]:
        """Get all prompts that serve a capability (e.g., 'image')."""
        return [
            t for t in self._templates.values()
            if t.metadata.capability == capability
        ]

    def by_model(self, model: str) -> list[PromptTemplate]:
        """Get all prompts that support a given model."""
        return [
            t for t in self._templates.values()
            if model in t.metadata.supported_models
        ]

    def by_role(self, role: str) -> list[PromptTemplate]:
        """Get all prompts with a given role (e.g., 'system', 'image')."""
        from movie_os.domain.prompt import PromptRole
        try:
            role_enum = PromptRole(role)
        except ValueError:
            return []
        return [
            t for t in self._templates.values()
            if t.metadata.role == role_enum
        ]

    def by_tag(self, tag: str) -> list[PromptTemplate]:
        """Get all prompts with a given tag."""
        return [
            t for t in self._templates.values()
            if tag in t.metadata.tags
        ]

    def latest(
        self,
        capability: str,
        name: str,
        model: str | None = None,
    ) -> Optional[PromptTemplate]:
        """Get the latest version of a prompt.

        Args:
            capability: e.g., "image"
            name: e.g., "cinematic" — matches the id prefix
                "image.cinematic" (any version)
            model: optional — if given, prefer prompts that support this model

        Returns the prompt with the highest semver version, or None.
        """
        prefix = f"{capability}.{name}"
        candidates = [
            (tid, t) for tid, t in self._templates.items()
            if tid.startswith(prefix + ".") or tid == prefix
        ]
        if not candidates:
            return None

        # If a model is specified, prefer prompts that support it
        if model:
            model_match = [
                (tid, t) for tid, t in candidates
                if model in t.metadata.supported_models
            ]
            if model_match:
                candidates = model_match

        # Sort by semver version (descending) — pick the highest
        def _version_key(item):
            tid, t = item
            v = t.metadata.version
            parts = v.split(".")
            try:
                return tuple(int(p) for p in parts)
            except ValueError:
                return (0,)

        candidates.sort(key=_version_key, reverse=True)
        return candidates[0][1]

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def list_ids(self) -> list[str]:
        """List all prompt IDs (sorted)."""
        return sorted(self._templates.keys())

    def info(self) -> list[dict[str, Any]]:
        """Get info about all loaded prompts (for CLI / debugging)."""
        return [
            {
                "id": t.metadata.id,
                "version": t.metadata.version,
                "capability": t.metadata.capability,
                "role": t.metadata.role.value if hasattr(t.metadata.role, "value") else t.metadata.role,
                "models": t.metadata.supported_models,
                "tags": t.metadata.tags,
                "variables": len(t.variables),
            }
            for t in self._templates.values()
        ]


# Global default repository
_default_repository: PromptRepository | None = None


def get_default_repository() -> PromptRepository:
    """Get the global default repository, creating it on first call.

    The default repository loads from `movie_os/prompts` (the bundled
    prompts that ship with the package).
    """
    global _default_repository
    if _default_repository is None:
        from movie_os import prompts
        prompts_dir = Path(prompts.__file__).parent
        _default_repository = PromptRepository(prompts_dir)
    return _default_repository


def set_default_repository(repo: PromptRepository) -> None:
    """Set the global default repository (useful for testing)."""
    global _default_repository
    _default_repository = repo
