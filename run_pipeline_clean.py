#!/usr/bin/env python3
"""Clean pipeline runner — runs Genesis2 → Bridge → movie_os graph."""
import asyncio, json, logging, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("run_pipeline_clean")

SYNOPSIS = (
    "In a near-future Tokyo, a retired clockmaker named Kenzo discovers that one of his "
    "grandfather's most intricate timepieces contains a hidden message — coordinates pointing to "
    "a buried vault beneath the city. As he follows the trail, he uncovers a family secret dating "
    "back to World War II: a collection of art looted by his grandfather that could change historical "
    "memory. Torn between personal redemption and public justice, Kenzo must decide whether to expose "
    "the truth or protect his family's name — all while a rival collector races against him."
)

async def main():
    from movie_os.genesis2 import Genesis2Engine
    from movie_os.genesis2.llm_client import LLMClient
    from movie_os.genesis2.llm_providers import LLMConfig

    print("=" * 60)
    print("  Genesis2 → movie_os Pipeline (Clean Runner)")
    print("=" * 60)
    print(f"  Synopsis: {SYNOPSIS[:80]}...")
    print(f"  Model: deepseek-coder-v2:latest")
    print()

    # Step 1: Genesis2
    print("=" * 60)
    print("  Step 1: Running Genesis2 Creative Intelligence Engine")
    print("=" * 60)

    config = LLMConfig(provider="ollama", model="deepseek-coder-v2:latest", timeout=600, max_tokens=8192)
    client = LLMClient(config=config)
    engine = Genesis2Engine(llm=client)

    t0 = time.time()
    pkg = await engine.run_async(synopsis=SYNOPSIS)
    elapsed = time.time() - t0

    print(f"\n  PKP version : {pkg.version}")
    print(f"  Time        : {elapsed:.0f}s")
    print(f"  Phase results : {len(pkg.phase_results)} phases executed")

    completed = sum(1 for r in pkg.phase_results if r.status.value == "completed")
    failed = sum(1 for r in pkg.phase_results if r.status.value == "failed")
    print(f"   ✓ Completed: {completed}    ✗ Failed: {failed}")

    for r in pkg.phase_results:
        icon = "✓" if r.status.value == "completed" else ("✗" if r.status.value == "failed" else "-")
        print(f"   {icon} Phase {r.phase_number:02d} ({r.phase_name}): {r.status.value}  [{len(r.validation_issues)} issues]")

    # Save PKP
    output_dir = ROOT / "output" / "videos" / "final"
    output_dir.mkdir(parents=True, exist_ok=True)
    pkg_path = output_dir / "production_knowledge_package.json"
    pkg_path.write_text(json.dumps(pkg.model_dump(), indent=2, default=str), encoding="utf-8")
    print(f"\n  → Saved PKP to {pkg_path}")

    # Step 2: Bridge → movie_os brief
    print("\n" + "=" * 60)
    print("  Step 2: Converting PKP → movie_os Brief")
    print("=" * 60)

    from movie_os.genesis2.bridge import Genesis2Bridge
    bridge = Genesis2Bridge(pkg)
    brief = bridge.to_brief()

    print(f"  Title         : {brief['title']}")
    print(f"  Logline       : {brief['logline'][:100]}...")
    print(f"  Scenes        : {len(brief['scenes'])} scenes generated")
    for scene in brief['scenes']:
        print(f"    Scene {scene.get('number', '?'):2d}: {scene.get('title', '???'):30s} | {scene.get('act', ''):6s} | energy={scene.get('energy', 0)}")

    brief_path = output_dir / "movie_os_brief.json"
    brief_path.write_text(json.dumps(brief, indent=2, default=str), encoding="utf-8")
    print(f"  → Saved brief to {brief_path}")

    # Step 3: movie_os Graph (full pipeline: story → visual → voice → music → qa → publishing)
    print("\n" + "=" * 60)
    print("  Step 3: Running movie_os Agent Graph (full pipeline)")
    print("=" * 60)

    from movie_os.agents import build_graph, new_state
    from movie_os.capabilities import get_default_registry, ImageCapability
    from movie_os.providers.registry import register_builtin_providers

    # Register built-in providers (FluxComfyUI, EdgeTTS, etc.)
    register_builtin_providers()

    # Register image capability with FluxComfyUI provider
    registry = get_default_registry()
    from movie_os.providers.registry import make as make_provider
    flux = make_provider("image", "flux_comfyui", {"comfyui_url": "http://localhost:8188"})
    if flux:
        registry.register(ImageCapability(provider=flux), label="flux_comfyui")
        registry.set_default("image", "flux_comfyui")
        print("  ✅ Registered FluxComfyUI image provider")
    else:
        print("  ⚠️  FluxComfyUI provider not available — visual stage will be skipped")

    thread_id = f"genesis2-{pkg.created_at[:10]}"
    state = new_state(brief=brief, thread_id=thread_id)

    graph = build_graph(
        checkpointer=None,
        use_new_architecture=False,
    )

    cfg = {"configurable": {"thread_id": thread_id}, "recursion_limit": 50}
    result = await graph.ainvoke(state, config=cfg)

    errors = result.get("errors", [])
    current_step = result.get("current_step", "unknown")
    print(f"  Final step    : {current_step}")
    if errors:
        print(f"  ⚠ {len(errors)} error(s):")
        for e in errors[:5]:
            print(f"    • {e}")

    # Summary
    summary = {
        "synopsis": SYNOPSIS[:120],
        "pkp_version": pkg.version,
        "title": brief["title"],
        "scenes_count": len(brief["scenes"]),
        "phases_completed": completed,
        "phases_total": len(pkg.phase_results),
        "errors": errors,
        "graph_status": current_step,
        "elapsed_seconds": elapsed,
    }
    summary_path = output_dir / "pipeline_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")

    print(f"\n{'=' * 60}")
    print(f"  ✅ Pipeline Complete!")
    print(f"  Output: {output_dir}")
    print(f"{'=' * 60}")
    return summary

if __name__ == "__main__":
    summary = asyncio.run(main())
    print(f"\nFinal: {summary['phases_completed']}/{summary['phases_total']} phases completed in {summary['elapsed_seconds']:.0f}s")
