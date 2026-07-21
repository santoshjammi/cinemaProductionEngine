"""Movie OS v1 — Cinema Production Engine Agent Architecture.

This module defines the base interface for ALL production agents in the
Cinema Production Engine. Every agent implements this protocol.

Agents are organized by category:
  - creative/     (ResearchAgent, StoryArchitectAgent, etc.)
  - planning/     (ScenePlannerAgent, ShotPlannerAgent, etc.)
  - generation/   (CharacterManagerAgent, ImageGeneratorAgent, etc.)
  - post_production/ (AudioMixingAgent, VideoComposerAgent, etc.)
  - evaluation/   (StoryQualityAgent, DialogueQualityAgent, etc.)
  - orchestration/ (ProductionOrchestratorAgent, RevisionAgent)

Usage:
    from movie_os.capabilities.agent_base import ProductionAgent, ProductionContext

    class ScreenplayWriterAgent(ProductionAgent):
        name = "screenplay_writer"
        version = "1.0.0"
        capability = "story"
        grammar_aware = True

        async def execute(self, context: ProductionContext) -> AgentResult:
            ...
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class AgentStatus(str, Enum):
    """Agent execution status."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    REVISED = "revised"
    SKIPPED = "skipped"


class EvaluationCategory(str, Enum):
    """Evaluation score categories."""
    STORY_QUALITY = "story_quality"
    DIALOGUE_AUTHENTICITY = "dialogue_authenticity"
    VISUAL_CONSISTENCY = "visual_consistency"
    AUDIO_BALANCE = "audio_balance"
    EMOTIONAL_IMPACT = "emotional_impact"
    CHARACTER_CONSISTENCY = "character_consistency"
    TIMING_PACING = "timing_pacing"
    YOUTUBE_READINESS = "youtube_readiness"


# ---------------------------------------------------------------------------
# Production Context — shared state passed between agents
# ---------------------------------------------------------------------------

@dataclass
class ProductionContext:
    """Shared context passed between all production agents.

    This is the single source of truth for production state during execution.
    Agents read from and write to this context — never directly to files.
    File I/O is handled by the orchestrator.
    """

    # --- Production identity ---
    production_id: str = ""
    title: str = ""
    grammar: str = ""  # e.g., "psychological_cinema"
    content_type: str = ""  # e.g., "psychological_story"
    series: Optional[str] = None
    season: Optional[int] = None
    episode: Optional[int] = None

    # --- File paths (resolved by orchestrator) ---
    production_dir: Path = field(default_factory=Path)
    dna_path: Path = field(default_factory=lambda: Path("dna.yaml"))
    research_path: Path = field(default_factory=lambda: Path("research.md"))
    creative_brief_path: Path = field(default_factory=lambda: Path("creative_brief.md"))
    director_notes_path: Path = field(default_factory=lambda: Path("director_notes.md"))
    outline_path: Path = field(default_factory=lambda: Path("outline.md"))
    screenplay_path: Path = field(default_factory=lambda: Path("screenplay.md"))
    timeline_path: Path = field(default_factory=lambda: Path("master_timeline.yaml"))
    manifest_path: Path = field(default_factory=lambda: Path("manifest.yaml"))
    production_rules_path: Path = field(default_factory=lambda: Path("production_rules.yaml"))
    music_score_path: Path = field(default_factory=lambda: Path("music_score.yaml"))
    prompts_dir: Path = field(default_factory=lambda: Path("prompts"))
    characters_dir: Path = field(default_factory=lambda: Path("characters"))
    environments_dir: Path = field(default_factory=lambda: Path("environments"))
    assets_dir: Path = field(default_factory=lambda: Path("assets"))
    renders_dir: Path = field(default_factory=lambda: Path("renders"))
    metadata_dir: Path = field(default_factory=lambda: Path("metadata"))

    # --- Loaded data (populated by orchestrator) ---
    dna: dict[str, Any] = field(default_factory=dict)
    creative_brief: dict[str, Any] = field(default_factory=dict)
    director_notes: dict[str, Any] = field(default_factory=dict)
    outline: dict[str, Any] = field(default_factory=dict)
    screenplay: dict[str, Any] = field(default_factory=dict)
    timeline: dict[str, Any] = field(default_factory=dict)
    production_rules: dict[str, Any] = field(default_factory=dict)
    music_score: dict[str, Any] = field(default_factory=dict)

    # --- Grammar (loaded from movie_os/grammars/) ---
    grammar_config: dict[str, Any] = field(default_factory=dict)

    # --- Character & Environment data ---
    characters: dict[str, Any] = field(default_factory=dict)
    environments: dict[str, Any] = field(default_factory=dict)

    # --- Generated assets (paths to generated content) ---
    images: list[Path] = field(default_factory=list)
    voices: list[Path] = field(default_factory=list)
    music_tracks: list[Path] = field(default_factory=list)
    audio_mixes: list[Path] = field(default_factory=list)
    final_video: Optional[Path] = None
    subtitles: Optional[Path] = None
    
    # --- Dynamic asset paths (set by agents during execution) ---
    image_paths: list[str] = field(default_factory=list)
    voice_paths: list[str] = field(default_factory=list)
    music_paths: list[str] = field(default_factory=list)
    audio_mix_path: Optional[str] = None
    video_path: Optional[str] = None
    images_dir: Optional[Path] = None
    voices_dir: Optional[Path] = None
    music_dir: Optional[Path] = None
    audio_dir: Optional[Path] = None
    video_dir: Optional[Path] = None

    # --- Evaluation results ---
    evaluation_scores: dict[str, float] = field(default_factory=dict)
    evaluation_feedback: dict[str, str] = field(default_factory=dict)

    # --- Execution state ---
    status: AgentStatus = AgentStatus.PENDING
    revision_count: int = 0
    max_revisions: int = 3
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    # --- Helper methods ---
    def add_error(self, error: str):
        self.errors.append(error)

    def add_warning(self, warning: str):
        self.warnings.append(warning)

    def add_evaluation_score(self, category: EvaluationCategory, score: float):
        self.evaluation_scores[category.value] = score

    def add_evaluation_feedback(self, category: EvaluationCategory, feedback: str):
        self.evaluation_feedback[category.value] = feedback

    def should_revise(self) -> bool:
        """Check if production should be revised based on evaluation scores."""
        thresholds = {
            EvaluationCategory.STORY_QUALITY: 0.6,
            EvaluationCategory.DIALOGUE_AUTHENTICITY: 0.7,
            EvaluationCategory.VISUAL_CONSISTENCY: 0.7,
            EvaluationCategory.AUDIO_BALANCE: 0.6,
            EvaluationCategory.EMOTIONAL_IMPACT: 0.5,
            EvaluationCategory.CHARACTER_CONSISTENCY: 0.7,
        }

        for category, threshold in thresholds.items():
            score = self.evaluation_scores.get(category.value, 0.0)
            if score < threshold:
                return True

        return False

    def get_failed_categories(self) -> list[str]:
        """Get categories that failed evaluation."""
        thresholds = {
            EvaluationCategory.STORY_QUALITY: 0.6,
            EvaluationCategory.DIALOGUE_AUTHENTICITY: 0.7,
            EvaluationCategory.VISUAL_CONSISTENCY: 0.7,
            EvaluationCategory.AUDIO_BALANCE: 0.6,
            EvaluationCategory.EMOTIONAL_IMPACT: 0.5,
            EvaluationCategory.CHARACTER_CONSISTENCY: 0.7,
        }

        failed = []
        for category, threshold in thresholds.items():
            score = self.evaluation_scores.get(category.value, 0.0)
            if score < threshold:
                failed.append(category.value)
        return failed


# ---------------------------------------------------------------------------
# Agent Result — output from each agent execution
# ---------------------------------------------------------------------------

@dataclass
class AgentResult:
    """Result returned by an agent's execute() or revise() method."""

    status: AgentStatus = AgentStatus.PENDING
    message: str = ""
    updated_context: Optional[ProductionContext] = None
    artifacts: dict[str, Any] = field(default_factory=dict)  # files written, data produced
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def is_success(self) -> bool:
        return self.status == AgentStatus.SUCCESS

    @property
    def is_failure(self) -> bool:
        return self.status == AgentStatus.FAILED


# ---------------------------------------------------------------------------
# Evaluation Feedback — passed from evaluation agents to revision agent
# ---------------------------------------------------------------------------

@dataclass
class EvaluationFeedback:
    """Structured feedback from evaluation agents for revision."""

    category: EvaluationCategory
    score: float
    threshold: float
    feedback: str
    requires_revision: bool = True

    @property
    def passed(self) -> bool:
        return self.score >= self.threshold


# ---------------------------------------------------------------------------
# ProductionAgent — base class for all agents
# ---------------------------------------------------------------------------

class ProductionAgent(ABC):
    """Base class for all production agents in the Cinema Production Engine.

    Every agent must implement:
      - name: Unique identifier (e.g., "screenplay_writer")
      - version: Semantic version (e.g., "1.0.0")
      - capability: Capability this agent serves (e.g., "story", "image", "voice")
      - grammar_aware: Whether this agent respects grammar rules

    Agents may optionally implement:
      - revise(): Revise output based on evaluation feedback
    """

    name: str = ""
    version: str = "1.0.0"
    capability: str = ""
    grammar_aware: bool = False

    @abstractmethod
    async def execute(self, context: ProductionContext) -> AgentResult:
        """Execute the agent's core responsibility.

        Args:
            context: Shared production context with all loaded data.

        Returns:
            AgentResult with status, message, updated context, and artifacts.
        """
        ...

    async def revise(self, context: ProductionContext, feedback: EvaluationFeedback) -> AgentResult:
        """Revise output based on evaluation feedback (optional override).

        Default implementation returns a failure result indicating revision not supported.

        Args:
            context: Shared production context.
            feedback: Evaluation feedback for the specific category.

        Returns:
            AgentResult with revision status and updated artifacts.
        """
        return AgentResult(
            status=AgentStatus.FAILED,
            message=f"Revision not supported for agent '{self.name}'",
        )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name} version={self.version} capability={self.capability}>"


# ---------------------------------------------------------------------------
# Provider — interface for AI model providers
# ---------------------------------------------------------------------------

class Provider(ABC):
    """Base class for AI capability providers.

    Providers implement specific AI capabilities (image, voice, music, etc.)
    and are interchangeable — replacing one provider never requires architectural changes.

    Example:
        class ComfyUIProvider(ImageProvider):
            async def generate(self, prompt: str, **kwargs) -> Path:
                ...

        class FLUXProvider(ImageProvider):
            async def generate(self, prompt: str, **kwargs) -> Path:
                ...
    """

    name: str = ""
    provider_type: str = ""  # e.g., "image", "voice", "music"
    enabled: bool = True
    config: dict[str, Any] = field(default_factory=dict)

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the provider (e.g., connect to ComfyUI, load model)."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider is available and healthy."""
        ...


# ---------------------------------------------------------------------------
# Module exports
# ---------------------------------------------------------------------------

__all__ = [
    "ProductionAgent",
    "Provider",
    "ProductionContext",
    "AgentResult",
    "EvaluationFeedback",
    "AgentStatus",
    "EvaluationCategory",
]
