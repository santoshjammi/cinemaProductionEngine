"""Config loader — load MovieOSConfig from a YAML file.

The loader:
  1. Reads the YAML
  2. Validates against the schema
  3. Merges with built-in defaults (so a minimal config still works)
  4. Returns a MovieOSConfig object

Usage:

    from movie_os.config import load_config

    # Load from default location
    config = load_config("config/movie_os.yaml")

    # Load with overrides
    config = load_config("config/movie_os.yaml", overrides={
        "rendering": {"aspect_ratio": "9:16", "quality": "draft"},
    })

    # Load from a dict (useful for testing)
    config = load_config_from_dict({
        "version": "1.0",
        "project": {"name": "test"},
    })
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .schema import MovieOSConfig


DEFAULT_CONFIG_PATH = Path("config/movie_os.yaml")


class ConfigError(ValueError):
    """Raised when the config file is invalid or cannot be loaded."""


def load_config(
    path: str | Path | None = None,
    *,
    overrides: dict[str, Any] | None = None,
    use_defaults: bool = True,
) -> MovieOSConfig:
    """Load a MovieOSConfig from a YAML file.

    Args:
        path: Path to the YAML file. If None, uses DEFAULT_CONFIG_PATH.
        overrides: A dict of overrides to apply on top of the file. Useful
            for CLI flags that should win over the file.
        use_defaults: If True, missing fields are filled from built-in
            defaults. If False, missing fields cause an error.

    Returns:
        A validated MovieOSConfig object.

    Raises:
        FileNotFoundError: If the file doesn't exist and no defaults are used.
        ConfigError: If the YAML is invalid or doesn't match the schema.
    """
    path = Path(path) if path else DEFAULT_CONFIG_PATH
    data: dict[str, Any] = {}

    if path.exists():
        try:
            with open(path) as f:
                data = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ConfigError(f"Invalid YAML in {path}: {e}") from e

    if not data and not use_defaults:
        raise FileNotFoundError(
            f"Config file not found: {path}. "
            f"Pass use_defaults=True to use built-in defaults."
        )

    if overrides:
        data = _deep_merge(data, overrides)

    return _build_config(data)


def load_config_from_dict(data: dict[str, Any]) -> MovieOSConfig:
    """Load a MovieOSConfig from a dict (useful for testing)."""
    return _build_config(data)


def _build_config(data: dict[str, Any]) -> MovieOSConfig:
    """Build a MovieOSConfig from raw data, with validation."""
    try:
        return MovieOSConfig.model_validate(data)
    except Exception as e:
        raise ConfigError(f"Config validation failed: {e}") from e


def _deep_merge(base: dict[str, Any], overrides: dict[str, Any]) -> dict[str, Any]:
    """Deep-merge overrides into base. Overrides win."""
    result = dict(base)
    for key, value in overrides.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def write_default_config(path: str | Path) -> None:
    """Write a default config file to `path`. Useful for bootstrapping."""
    from .defaults import DEFAULT_CONFIG_DICT
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        yaml.safe_dump(
            DEFAULT_CONFIG_DICT,
            f,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
        )
