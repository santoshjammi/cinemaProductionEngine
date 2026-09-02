"""GENESIS Standards Framework."""
from .base import Standard, QualityCriterion, ValidationRule, StandardResult
from .story_standard import StoryStandard
from .cinema_standard import CinemaStandard
from .emotional_standard import EmotionalStandard
from .psychological_standard import PsychologicalStandard
from .narrative_standard import NarrativeStandard
from .character_standard import CharacterStandard
from .dialogue_standard import DialogueStandard
from .scene_standard import SceneStandard
from .shot_standard import ShotStandard
from .visual_standard import VisualStandard
from .audio_standard import AudioStandard
from .music_standard import MusicStandard
from .editing_standard import EditingStandard
from .production_standard import ProductionStandard

STANDARDS: dict[str, Standard] = {}

def get_standard(name: str) -> Standard:
    if name not in STANDARDS:
        _init_registry()
    if name not in STANDARDS:
        raise KeyError(f"Unknown standard: {name}")
    return STANDARDS[name]

def list_standards() -> list[str]:
    _init_registry()
    return sorted(STANDARDS.keys())

def evaluate_all(evidence: dict) -> dict[str, StandardResult]:
    _init_registry()
    return {name: std.evaluate(evidence) for name, std in STANDARDS.items()}

def _init_registry():
    if STANDARDS:
        return
    for cls in [StoryStandard, CinemaStandard, EmotionalStandard, PsychologicalStandard,
                NarrativeStandard, CharacterStandard, DialogueStandard, SceneStandard,
                ShotStandard, VisualStandard, AudioStandard, MusicStandard,
                EditingStandard, ProductionStandard]:
        inst = cls()
        STANDARDS[inst.name] = inst
