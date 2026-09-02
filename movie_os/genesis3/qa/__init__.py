"""Story QA Department — module-level registry for all 9 constitutions."""

from __future__ import annotations

from movie_os.genesis3.qa.base import BaseConstitution, ConstitutionReview, QADepartmentReport
from movie_os.genesis3.qa.department import QADepartment
from movie_os.genesis3.qa.story_constitution import StoryConstitution
from movie_os.genesis3.qa.character_constitution import CharacterConstitution
from movie_os.genesis3.qa.psychology_constitution import PsychologyConstitution
from movie_os.genesis3.qa.dialogue_constitution import DialogueConstitution
from movie_os.genesis3.qa.visual_constitution import VisualConstitution
from movie_os.genesis3.qa.emotion_constitution import EmotionConstitution
from movie_os.genesis3.qa.cinema_constitution import CinemaConstitution
from movie_os.genesis3.qa.continuity_constitution import ContinuityConstitution
from movie_os.genesis3.qa.production_constitution import ProductionConstitution

__all__ = [
    "BaseConstitution",
    "ConstitutionReview",
    "StandardCheck",
    "QADepartmentReport",
    "QADepartment",
    "CONSTITUTIONS",
    "get_constitution",
    "list_constitutions",
    "register_all",
]

# Lazy import support — const_instance_cache keyed by name
_CONSTITUTION_CLASSES = {
    "story": StoryConstitution,
    "character": CharacterConstitution,
    "psychology": PsychologyConstitution,
    "dialogue": DialogueConstitution,
    "visual": VisualConstitution,
    "emotion": EmotionConstitution,
    "cinema": CinemaConstitution,
    "continuity": ContinuityConstitution,
    "production": ProductionConstitution,
}

# Module-level registry dict (populated on first contact)
_constitutions_cache: dict[str, BaseConstitution] | None = None


def _ensure_init() -> dict[str, BaseConstitution]:
    global _constitutions_cache
    if _constitutions_cache is None:
        _constitutions_cache = {}
        for name_cls in _CONSTITUTION_CLASSES.items():
            n = name_cls[0]
            inst = name_cls[1]()
            QADepartment.register(n, inst)
            _constitutions_cache[n] = inst
    return _constitutions_cache


def register_all() -> dict[str, BaseConstitution]:
    """Register every constitution class into QADepartment. Returns the registry."""
    return _ensure_init()


CONSTITUTIONS: dict[str, BaseConstitution] = {}  # populated lazily via get_constitution


def get_constitution(name: str) -> BaseConstitution:
    """Return a constitution instance by name; registers it if not yet loaded.

    Raises:
        KeyError: if no such constitution exists.
    """
    _ensure_init()
    inst = QADepartment.get_constitution(name)
    cache = _constitutions_cache
    if inst is None:
        if cache is not None and name in cache:
            return cache[name]
        raise KeyError(name + " not found among: " + ", ".join(sorted(_CONSTITUTION_CLASSES)))
    return inst


def list_constitutions() -> list[str]:
    """Return sorted list of available constitution names."""
    _ensure_init()
    result = QADepartment.list_constitutions()
    return result
