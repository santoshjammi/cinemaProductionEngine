"""Movie OS Agents — multi-agent orchestration.

Public API:
    from movie_os.agents import (
        MovieState, AgentBase, AgentContext,
        StoryAgent, VisualAgent, VoiceAgent, MusicAgent,
        SFXAgent, QAAgent, PublishingAgent, MovieAgent,
        build_graph, run_graph,
        
        # New Cinema Production Engine agents
        ResearchAgent, StoryArchitectAgent, ScreenplayWriterAgent,
        ProductionOrchestratorAgent, RevisionAgent,
    )

Two architecture paths:
1. Legacy (backward compatible): MovieAgent → Story → Visual → Voice → Music → QA → Publishing
2. New (Cinema Production Engine): ProductionOrchestratorAgent → all 26 agents → Evaluation → Revision

Auto-detection: If production_dir/screenplay.md exists, uses new architecture.
"""

from .state import MovieState, MovieStateModel, new_state, validate_state
from .base import AgentBase, AgentContext, make_state_updater
from .movie_agent import MovieAgent
from .story_agent import StoryAgent
from .visual_agent import VisualAgent
from .voice_agent import VoiceAgent
from .music_agent import MusicAgent
from .sfx_agent import SFXAgent
from .qa_agent import QAAgent
from .publishing_agent import PublishingAgent

# New Cinema Production Engine agents (all 26)
from .creative.research_agent import ResearchAgent
from .creative.story_architect_agent import StoryArchitectAgent
from .creative.psychology_reviewer_agent import PsychologyReviewerAgent
from .creative.screenplay_writer_agent import ScreenplayWriterAgent
from .creative.dialogue_writer_agent import DialogueWriterAgent

from .planning.scene_planner_agent import ScenePlannerAgent
from .planning.shot_planner_agent import ShotPlannerAgent
from .planning.prompt_builder_agent import PromptBuilderAgent
from .planning.music_composer_agent import MusicComposerAgent

from .generation.character_manager_agent import CharacterManagerAgent
from .generation.environment_manager_agent import EnvironmentManagerAgent
from .generation.image_generator_agent import ImageGeneratorAgent
from .generation.voice_generator_agent import VoiceGeneratorAgent
from .generation.music_generator_agent import MusicGeneratorAgent

from .post_production.audio_mixing_agent import AudioMixingAgent
from .post_production.video_composer_agent import VideoComposerAgent
from .post_production.subtitle_agent import SubtitleAgent

from .evaluation.story_quality_agent import StoryQualityAgent
from .evaluation.dialogue_quality_agent import DialogueQualityAgent
from .evaluation.visual_consistency_agent import VisualConsistencyAgent
from .evaluation.audio_mix_agent import AudioMixAgent
from .evaluation.emotion_score_agent import EmotionScoreAgent
from .evaluation.character_consistency_agent import CharacterConsistencyAgent
from .evaluation.youtube_readiness_agent import YouTubeReadinessAgent

from .orchestration.production_orchestrator_agent import ProductionOrchestratorAgent
from .orchestration.revision_agent import RevisionAgent

# Migration adapter (imported from movie_os.migration, not agents)
try:
    from movie_os.migration.adapter import MigrationAdapter, MigrationResult
except ImportError:
    MigrationAdapter = None
    MigrationResult = None


def build_graph(checkpointer=None, config=None, skip_stages=None, only_stage=None, use_new_architecture=None, production_dir=None):
    """Build the LangGraph state machine (re-exported from graph.py)."""
    from .graph import build_graph as _build_graph
    return _build_graph(
        checkpointer=checkpointer,
        config=config,
        skip_stages=skip_stages,
        only_stage=only_stage,
        use_new_architecture=use_new_architecture,
        production_dir=production_dir,
    )


def run_graph(initial_state, *, thread_id, checkpointer=None, config=None):
    """Run the graph (re-exported from graph.py)."""
    from .graph import run_graph as _run_graph
    return _run_graph(initial_state, thread_id=thread_id, checkpointer=checkpointer, config=config)


__all__ = [
    # Legacy agents (backward compatible)
    "MovieState", "MovieStateModel", "new_state", "validate_state",
    "AgentBase", "AgentContext", "make_state_updater",
    "MovieAgent", "StoryAgent", "VisualAgent", "VoiceAgent",
    "MusicAgent", "SFXAgent", "QAAgent", "PublishingAgent",
    "build_graph", "run_graph",
    # New Cinema Production Engine agents (26 total)
    "ResearchAgent", "StoryArchitectAgent", "PsychologyReviewerAgent",
    "ScreenplayWriterAgent", "DialogueWriterAgent",
    "ScenePlannerAgent", "ShotPlannerAgent", "PromptBuilderAgent",
    "MusicComposerAgent",
    "CharacterManagerAgent", "EnvironmentManagerAgent", "ImageGeneratorAgent",
    "VoiceGeneratorAgent", "MusicGeneratorAgent",
    "AudioMixingAgent", "VideoComposerAgent", "SubtitleAgent",
    "StoryQualityAgent", "DialogueQualityAgent", "VisualConsistencyAgent",
    "AudioMixAgent", "EmotionScoreAgent", "CharacterConsistencyAgent",
    "YouTubeReadinessAgent",
    "ProductionOrchestratorAgent", "RevisionAgent",
]

# Import migration adapter from correct path (movie_os.migration, not agents)
try:
    from movie_os.migration.adapter import MigrationAdapter, MigrationResult as _MigrationResult
except ImportError:
    _MigrationResult = None
    MigrationAdapter = None


def build_graph(checkpointer=None, config=None, skip_stages=None, only_stage=None, use_new_architecture=None, production_dir=None):
    """Build the LangGraph state machine (re-exported from graph.py)."""
    from .graph import build_graph as _build_graph
    return _build_graph(
        checkpointer=checkpointer,
        config=config,
        skip_stages=skip_stages,
        only_stage=only_stage,
        use_new_architecture=use_new_architecture,
        production_dir=production_dir,
    )


def run_graph(initial_state, *, thread_id, checkpointer=None, config=None):
    """Run the graph (re-exported from graph.py)."""
    from .graph import run_graph as _run_graph
    return _run_graph(initial_state, thread_id=thread_id, checkpointer=checkpointer, config=config)


__all__ = [
    "MovieState", "MovieStateModel", "new_state", "validate_state",
    "AgentBase", "AgentContext", "make_state_updater",
    "MovieAgent", "StoryAgent", "VisualAgent", "VoiceAgent",
    "MusicAgent", "SFXAgent", "QAAgent", "PublishingAgent",
    "build_graph", "run_graph",
]
