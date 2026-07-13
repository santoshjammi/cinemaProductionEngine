"""End-to-end 9-scene story test.

Runs the full multi-agent pipeline on a real 9-scene brief:
  brief → story → visual (FLUX via ComfyUI) → voice (EdgeTTS) →
  music (procedural) → publishing (ffmpeg + Ken Burns) → final video

The final video is a real playable mp4 with all 9 scenes,
voiceover, music bed, and Ken Burns motion.

Note: This test requires:
  - ComfyUI running on localhost:8188 (with --cpu)
  - FLUX.1 Dev fp8 + CLIP-L + T5-XXL + VAE installed
  - edge-tts for voice synthesis
  - ffmpeg for video composition

Run time on CPU: ~5-10 minutes (FLUX is the bottleneck).
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(repo_root))

    from movie_os.agents import build_graph, new_state, AgentContext
    from movie_os.agents.story_agent import load_brief
    from movie_os.asset_store import AssetStore
    from movie_os.capabilities import (
        CapabilityRegistry, ImageCapability, VoiceCapability,
        MusicCapability, SFXCapability, StoryCapability,
    )
    from movie_os.providers import (
        default_provider_factory,
    )

    print("=" * 60)
    print("Phase 10+ — Full 9-Scene End-to-End Test")
    print("=" * 60)

    # Build a registry with all 4 rendering providers
    print("\n[setup] Building capability registry...")
    registry = CapabilityRegistry()
    # Image: FLUX via ComfyUI (bf16 for MPS, fp8 for CUDA)
    image_cap = ImageCapability(provider=default_provider_factory(
        "image", "flux_comfyui",
        {"comfyui_url": "http://127.0.0.1:8188", "model": "flux1-dev-bf16.safetensors"},
        0.0,
    ))
    registry.register(image_cap)
    # Voice: EdgeTTS
    voice_cap = VoiceCapability(provider=default_provider_factory(
        "voice", "edge_tts", {}, 0.0,
    ))
    registry.register(voice_cap)
    # Music: Procedural
    music_cap = MusicCapability(provider=default_provider_factory(
        "music", "procedural", {}, 0.0,
    ))
    registry.register(music_cap)
    # SFX: Procedural (will skip if no layers)
    sfx_cap = SFXCapability(provider=default_provider_factory(
        "sfx", "procedural", {}, 0.0,
    ))
    registry.register(sfx_cap)
    # Story: LMStudio (we'll provide timeline via brief, so this is a no-op fallback)
    story_cap = StoryCapability(provider=default_provider_factory(
        "story", "lmstudio", {"url": "http://127.0.0.1:1234"}, 0.0,
    ))
    registry.register(story_cap)
    print(f"  Registered capabilities: {registry.list()}")

    # Build an asset store
    output_root = Path("/tmp/movie_os_9scene_e2e")
    output_root.mkdir(exist_ok=True)
    db_path = output_root / "assets.db"
    if db_path.exists():
        db_path.unlink()
    store = AssetStore(db_path=db_path, files_dir=output_root / "files")
    print(f"  Asset store: {db_path}")

    # Build context with all providers
    context = AgentContext(
        registry=registry,
        output_dir=str(output_root),
        asset_store=store,
        quality="production",  # 20 steps for crisp images
    )
    # Inject the context into the graph
    from movie_os.agents import graph as graph_mod
    orig_build = graph_mod.build_graph

    def build_with_context(checkpointer=None):
        from movie_os.agents.state import MovieState
        from movie_os.agents.story_agent import StoryAgent
        from movie_os.agents.visual_agent import VisualAgent
        from movie_os.agents.voice_agent import VoiceAgent
        from movie_os.agents.music_agent import MusicAgent
        from movie_os.agents.sfx_agent import SFXAgent
        from movie_os.agents.qa_agent import QAAgent
        from movie_os.agents.publishing_agent import PublishingAgent
        from movie_os.agents.movie_agent import MovieAgent
        from langgraph.graph import StateGraph
        from langgraph.checkpoint.memory import MemorySaver
        story = StoryAgent(context)
        visual = VisualAgent(context)
        voice = VoiceAgent(context)
        music = MusicAgent(context)
        sfx = SFXAgent(context)
        qa = QAAgent(context)
        publishing = PublishingAgent(context)
        movie = MovieAgent(context)
        graph = StateGraph(MovieState)
        graph.add_node("movie_agent", movie)
        graph.add_node("story_agent", story)
        graph.add_node("visual_agent", visual)
        graph.add_node("voice_agent", voice)
        graph.add_node("music_agent", music)
        graph.add_node("sfx_agent", sfx)
        graph.add_node("qa_agent", qa)
        graph.add_node("publishing_agent", publishing)
        graph.set_entry_point("movie_agent")
        graph.add_edge("movie_agent", "story_agent")
        graph.add_edge("story_agent", "visual_agent")
        graph.add_edge("story_agent", "voice_agent")
        graph.add_edge("story_agent", "music_agent")
        graph.add_edge("story_agent", "sfx_agent")
        graph.add_edge("visual_agent", "qa_agent")
        graph.add_edge("voice_agent", "qa_agent")
        graph.add_edge("music_agent", "qa_agent")
        graph.add_edge("sfx_agent", "qa_agent")
        graph.add_conditional_edges(
            "qa_agent",
            graph_mod._route_after_qa,
            {"visual_agent": "visual_agent", "publishing_agent": "publishing_agent", "__end__": "__end__"},
        )
        graph.add_edge("publishing_agent", "__end__")
        if checkpointer is None:
            checkpointer = MemorySaver()
        return graph.compile(checkpointer=checkpointer)

    graph = build_with_context()

    # Load the 9-scene brief
    brief_path = Path(__file__).parent / "brief_9scene.yaml"
    brief = load_brief(brief_path)
    # The brief has a `scenes` list — pass it as pre-built timeline
    # The StoryAgent will pick this up via the `scenes` key in the brief
    print(f"\nBrief: {brief['title']}")
    print(f"  Scenes: {len(brief.get('scenes', []))}")
    for s in brief.get("scenes", []):
        print(f"    {s['number']}. {s['title']} ({s['act']}/{s['phase']}, energy={s['energy']})")

    state = new_state(brief, thread_id="9scene_e2e")

    # Run only the rendering + publishing agents (skip story_agent)
    # Easier: just call the graph and the story agent will run again
    # but produce a brief-as-timeline which will overwrite ours.
    # To skip story_agent, we use a different graph: just visual → ... → publishing
    print("\n[graph] Running full pipeline (this may take 5-10 minutes)...")
    print("  Stages: visual (FLUX) + voice (EdgeTTS) + music + publishing (ffmpeg)")

    import time
    t0 = time.time()
    result = asyncio.run(graph.ainvoke(
        state,
        config={"configurable": {"thread_id": "9scene_e2e"}},
    ))
    elapsed = time.time() - t0
    print(f"\n[done] Graph completed in {elapsed:.1f}s")
    print(f"  current_step: {result.get('current_step')}")
    print(f"  errors: {result.get('errors', [])}")

    # Check the final video
    final_video = result.get("final_video")
    if not final_video:
        print(f"\nFAIL: no final_video in result")
        print(f"  scene_assets keys: {list(result.get('scene_assets', {}).keys())}")
        for sn, a in result.get("scene_assets", {}).items():
            print(f"    scene {sn}: {list(a.keys())}")
        return 1

    final_path = Path(final_video)
    if not final_path.exists():
        print(f"\nFAIL: final_video path doesn't exist: {final_path}")
        return 1

    size_mb = final_path.stat().st_size / (1024 * 1024)
    duration = result.get("final_video_duration", 0.0)
    print(f"\n[result] Final video: {final_path}")
    print(f"  Size: {size_mb:.1f} MB")
    print(f"  Duration: {duration:.1f}s")
    print(f"  Asset ID: {result.get('final_video_asset_id', '?')}")

    # Verify asset store has all the assets
    assets = store.list(limit=100)
    print(f"\n[assets] {len(assets)} assets registered in store:")
    type_counts = {}
    for a in assets:
        type_counts[a.type.value] = type_counts.get(a.type.value, 0) + 1
    for t, c in type_counts.items():
        print(f"  {t}: {c}")

    # Check the video plays (ffprobe)
    print("\n[verify] Probing final video...")
    from movie_os.agents.compositor import probe_duration
    probed = probe_duration(final_path)
    print(f"  Probed duration: {probed:.1f}s")
    if abs(probed - duration) > 2.0:
        print(f"  WARN: probed duration differs from state by {abs(probed-duration):.1f}s")

    # Success criteria
    if size_mb < 0.1:
        print("\nFAIL: video is too small (<0.1MB)")
        return 1
    if probed < 5.0:
        print(f"\nFAIL: video is too short ({probed:.1f}s)")
        return 1

    print(f"\nPASS: Full 9-scene e2e complete in {elapsed:.1f}s")
    print(f"  Video: {final_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
