"""Movie OS v1 — Grammar loader.

Loads production grammars from movie_os/grammars/{grammar_name}/grammar.yaml.
Grammars define creative rules that control how productions are made.

Usage:
    from movie_os.production.grammar import load_grammar

    grammar = load_grammar("psychological_cinema")
    # grammar.config contains all creative rules for this grammar
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from movie_os.production.schema import GrammarSchema


GRAMMARS_DIR = Path(__file__).parent.parent / "grammars"


class GrammarError(ValueError):
    """Raised when a grammar cannot be loaded or is invalid."""


def load_grammar(grammar_name: str) -> GrammarSchema:
    """Load a production grammar by name.

    Args:
        grammar_name: Name of the grammar (e.g., "psychological_cinema").

    Returns:
        Validated GrammarSchema.

    Raises:
        GrammarError: If the grammar file doesn't exist or is invalid.
    """
    grammar_path = GRAMMARS_DIR / grammar_name / "grammar.yaml"

    if not grammar_path.exists():
        raise GrammarError(
            f"Grammar '{grammar_name}' not found at {grammar_path}. "
            f"Available grammars: {list_grammars()}"
        )

    try:
        with open(grammar_path) as f:
            data = yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        raise GrammarError(f"Invalid YAML in grammar '{grammar_name}': {e}") from e

    return GrammarSchema.model_validate(data)


def list_grammars() -> list[str]:
    """List all available grammars."""
    if not GRAMMARS_DIR.exists():
        return []
    return [d.name for d in GRAMMARS_DIR.iterdir() if d.is_dir()]


def get_grammar_path(grammar_name: str, file: str = "grammar.yaml") -> Path:
    """Get the full path to a grammar file.

    Args:
        grammar_name: Name of the grammar.
        file: Filename within the grammar directory (default: "grammar.yaml").

    Returns:
        Full path to the grammar file.
    """
    return GRAMMARS_DIR / grammar_name / file


# ---------------------------------------------------------------------------
# Module exports
# ---------------------------------------------------------------------------

__all__ = [
    "load_grammar",
    "list_grammars",
    "get_grammar_path",
    "GrammarError",
]
