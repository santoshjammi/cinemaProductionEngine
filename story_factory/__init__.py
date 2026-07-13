"""Story Factory — three specialized agents that turn a synopsis into a movie.

Public API:
    from story_factory import (
        generate_dna,
        generate_context,
        generate_story,
        structure_scenes,
        MasterTimeline,
        timeline_to_manifest,
        save_manifest,
    )

Pipeline:
    synopsis.txt
        ↓ [DNA Generator + Context Generator in parallel]
    dna.yaml  +  context.md
        ↓ [Story Generator]
    story.md
        ↓ [Scene Structurer]
    master_timeline.yaml
        ↓ [Master Timeline → Manifest adapter]
    manifest.yaml
        ↓ [existing pipeline]
    final.mp4

See docs/generateStoryContextDna.md for the design rationale.
See docs/superpowers/plans/createOncePublishAnywhere.md for the
Master Timeline and multi-platform publishing story.
"""

from .dna_generator import generate_dna
from .context_generator import generate_context
from .story_generator import generate_story
from .scene_structurer import structure_scenes
from .master_timeline import (
    MasterTimeline,
    Scene,
    Character,
    DialogueLine,
    MusicCue,
    AmbientCue,
    ShotLanguage,
    SilenceEngine,
)
# Shot and Frame were added in Phase 0 to movie_os.domain.story
from movie_os.domain.story import Shot, Frame
from .timeline_to_manifest import timeline_to_manifest, save_manifest
from .llm_client import chat, LLMError

__all__ = [
    "generate_dna",
    "generate_context",
    "generate_story",
    "structure_scenes",
    "MasterTimeline",
    "Scene",
    "Shot",
    "Frame",
    "Character",
    "DialogueLine",
    "MusicCue",
    "AmbientCue",
    "ShotLanguage",
    "SilenceEngine",
    "timeline_to_manifest",
    "save_manifest",
    "chat",
    "LLMError",
]
