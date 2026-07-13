"""Movie OS — Local AI Movie Operating System.

A reusable, capability-centric production pipeline for cinematic
psychological storytelling. Every AI capability is a plug-in.

The architecture is layered:

    Domain Model          (Pydantic schemas — the vocabulary)
        ↓
    Capability Registry   (the abstraction — "what can I ask for?")
        ↓
    Provider              (the impl — "how is it done?")
        ↓
    Workflow              (ComfyUI / programmatic — "what's the recipe?")
        ↓
    Model                 (FLUX, SDXL, EdgeTTS, etc. — "what runs it?")
        ↓
    Multi-Agent Layer     (Phase 8 — LangGraph orchestration)
        ↓
    Asset Store           (Phase 9 — SQLite + embeddings + versioning)

See docs/enhancementFluxComfyUI.md for the full design rationale.

Public API:

    # Domain (Phases 0-7)
    from movie_os.domain import (
        Story, Act, Sequence, Scene, Shot, Frame,
        CharacterDNA, EnvironmentDNA, Asset, Render, Reference,
        PromptTemplate, PromptContext,
    )

    # Capabilities (Phase 0-5)
    from movie_os.capabilities import (
        Capability, CapabilityRegistry,
        ImageCapability, VideoCapability, VoiceCapability,
        MusicCapability, SFXCapability, StoryCapability,
        TranslationCapability, ResearchCapability,
    )

    # Prompts (Phase 2)
    from movie_os.prompts import (
        PromptTemplate, PromptBuilder, PromptRenderer,
    )

    # Multi-agent (Phase 8)
    from movie_os.agents import (
        MovieState, AgentBase, AgentContext,
        StoryAgent, VisualAgent, VoiceAgent, MusicAgent,
        SFXAgent, QAAgent, PublishingAgent, MovieAgent,
        build_graph, run_graph,
    )

    # Asset store (Phase 9)
    from movie_os.asset_store import (
        AssetStore, Asset, AssetType, AssetVersion,
    )
    from movie_os.asset_store.search import tag_search
    from movie_os.asset_store.embeddings import EmbeddingIndex
"""

from . import domain, capabilities, prompts, agents, asset_store

__all__ = ["domain", "capabilities", "prompts", "agents", "asset_store"]

__version__ = "0.8.0"
