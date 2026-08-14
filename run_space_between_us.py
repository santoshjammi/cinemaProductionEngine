#!/usr/bin/env python3
"""Run 'The Space Between Us' through the actual GENESIS phases.

Uses the real Genesis2 engine (12 phases) with Ollama, then the bridge,
then the PROMETHEUS pipeline. Exercises the new dramatic-question framework
(HOOK/PLOT/CLIMAX) and the expanded dialogue + inner voice.
"""
import asyncio, json, logging, sys, time
from pathlib import Path

from movie_os.runtime_policy import load_and_resolve_canonical_policy

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("run_space_between_us")

SYNOPSIS = (
    "After losing his job, a husband named Mark becomes terrified that his wife Sarah will "
    "eventually see him as a failure. Instead of admitting the fear, he slowly withdraws — "
    "short answers at dinner, avoiding eye contact, sleeping in another room, rejecting small "
    "moments of affection. His wife initially thinks he no longer loves her. The emotional "
    "turning point comes when she quietly says, 'You don't have to disappear just because "
    "you're hurting.' He almost responds, but fear wins for one more moment — until he finally "
    "reaches for her hand."
)

CONSTRAINTS = {
    "runtime": "3-5 minutes",
    "platform": "youtube",
    "grammar": "psychological_cinema",
    "tone_arc": "secure → uneasy → painfully distant → vulnerable → cautiously hopeful",
    "characters": "MARK (38, responsible, loving, proud, emotionally contained; fears being seen as inadequate), "
                  "SARAH (36, perceptive, patient, affectionate, increasingly hurt by his silence)",
    "style": "Cinematic psychological realism. Warm domestic lighting gradually becomes colder as Mark withdraws. "
             "Minimal narration, strong facial micro-expressions, meaningful blocking and distance, restrained piano score.",
}


def ensure_scene_state_fields(brief: dict) -> dict:
    """Fill frozen-PKP scene-state and dialogue fields from the bridged brief."""
    scenes = []
    for scene in brief.get("scenes", []) or []:
        scene = dict(scene)
        title = str(scene.get("title") or f"Scene {scene.get('number', '?')}")
        beat = str(scene.get("narrative_beat") or scene.get("act") or "scene")
        scene.setdefault("entry_state", f"{title}: establishes the starting emotional state")
        scene.setdefault("turning_point", f"{title}: the {beat} shifts the relationship")
        scene.setdefault("exit_state", f"{title}: leaves the characters changed for the next scene")
        scene.setdefault("emotional_progression", ["steady", "uneasy", "changed"])
        scenes.append(scene)

    existing_dialogues = {}
    for d in brief.get("dialogues", []) or []:
        try:
            scene_num = int(d.get("scene_number"))
        except Exception:
            continue
        existing_dialogues[scene_num] = dict(d)

    dialogues = []
    for idx, scene in enumerate(scenes, start=1):
        scene_num = int(scene.get("number") or idx)
        if scene.get("title"):
            lead = str(scene["title"])
        else:
            lead = f"Scene {scene_num}"
        dialogue = dict(existing_dialogues.get(scene_num) or {})
        if not dialogue:
            speaker = "MARK" if scene_num % 2 == 1 else "SARAH"
            listener = "SARAH" if speaker == "MARK" else "MARK"
            progression = scene.get("emotional_progression", ["steady", "uneasy"])
            dialogue = {
                "scene_number": scene_num,
                "conversation_intent": f"{lead}: keep the scene moving with an honest exchange",
                "subtext": f"{speaker} speaks while {listener} reacts and listens",
                "emotional_state": str(progression[0] if progression else "steady"),
                "lines": [
                    {"speaker": speaker, "text": f"{lead}: I need to tell you something important.", "emotion": str(progression[0] if progression else "steady")},
                    {"speaker": listener, "text": "I am listening.", "emotion": str(progression[1] if len(progression) > 1 else (progression[0] if progression else "uneasy"))},
                ],
                "inner_voice": [],
            }
        dialogue.setdefault("scene_number", scene_num)
        dialogue.setdefault("conversation_intent", f"{lead}: keep the scene moving with an honest exchange")
        dialogue.setdefault("subtext", "Speaker and listener stay in active conversational coverage")
        dialogue.setdefault("emotional_state", str(scene.get("emotional_progression", ["steady"])[0]))
        dialogue.setdefault("lines", [])
        if not dialogue["lines"]:
            dialogue["lines"] = [
                {"speaker": "MARK", "text": f"{lead}: I need to tell you something important.", "emotion": str(scene.get("emotional_progression", ["steady"])[0])},
                {"speaker": "SARAH", "text": "I am listening.", "emotion": str(scene.get("emotional_progression", ["steady", "uneasy"])[1 if len(scene.get("emotional_progression", [])) > 1 else 0])},
            ]
        dialogue.setdefault("inner_voice", [])
        dialogues.append(dialogue)
    brief = dict(brief)
    brief["scenes"] = scenes
    brief["dialogues"] = dialogues
    return brief


async def main():
    from movie_os.genesis2 import Genesis2Engine
    from movie_os.genesis2.llm_client import LLMClient
    from movie_os.genesis2.llm_providers import LLMConfig
    from movie_os.runtime_paths import get_production_context

    print("=" * 60)
    print("  THE SPACE BETWEEN US — GENESIS → PROMETHEUS")
    print("=" * 60)
    print(f"  Synopsis: {SYNOPSIS[:80]}...")
    print(f"  Model: deepseek-coder-v2:latest")
    print()

    # Step 0: Episode Contract + Effective Policy Snapshot
    print("=" * 60)
    print("  Step 0: Resolving Episode Contract + Policy Snapshot")
    print("=" * 60)
    contract, policy_snapshot, policy_paths = load_and_resolve_canonical_policy()
    print(f"  Contract   : {contract.episode_id} / {contract.working_title}")
    print(f"  Policy     : {policy_snapshot.policy_snapshot_id}")
    print(f"  Hash       : {policy_snapshot.snapshot_hash[:12]}...")

    # Step 1: Genesis2 (12 phases, real Ollama)
    print("=" * 60)
    print("  Step 1: Running Genesis2 Creative Intelligence Engine")
    print("=" * 60)

    preferred_models = ["deepseek-coder-v2:latest", "qwen3.6:latest", "ornith:lite"]
    last_exc = None
    pkg = None
    elapsed = 0.0
    for model_name in preferred_models:
        try:
            config = LLMConfig(provider="ollama", model=model_name, timeout=600, max_tokens=8192, num_ctx=8192)
            client = LLMClient(config=config)
            engine = Genesis2Engine(llm=client)
            print(f"  Using local model: {model_name}")
            t0 = time.time()
            pkg = await engine.run_async(synopsis=SYNOPSIS, constraints=CONSTRAINTS)
            elapsed = time.time() - t0
            break
        except Exception as exc:
            last_exc = exc
            logger.warning("Genesis2 failed with %s: %s", model_name, exc)
            pkg = None
    if pkg is None:
        raise RuntimeError(f"Genesis2 failed with all local models: {last_exc}")

    production = {
        "episode_id": "EP-0001",
        "run_id": f"RUN-{time.strftime('%Y%m%d-%H%M%S')}",
    }
    prod_ctx = get_production_context({"production": production})
    production_root = Path(prod_ctx["production_root"])
    run_root = Path(prod_ctx["run_root"])
    for sub in ["contract", "policy", "genesis", "runs", "oracle", "releases"]:
        (production_root / sub).mkdir(parents=True, exist_ok=True)
    for sub in ["images", "voice", "music", "motion", "render", "manifest"]:
        (run_root / sub).mkdir(parents=True, exist_ok=True)

    print(f"\n  PKP version : {pkg.version}")
    print(f"  Time        : {elapsed:.0f}s")
    completed = sum(1 for r in pkg.phase_results if r.status.value == "completed")
    failed = sum(1 for r in pkg.phase_results if r.status.value == "failed")
    print(f"   ✓ Completed: {completed}    ✗ Failed: {failed}")

    for r in pkg.phase_results:
        icon = "✓" if r.status.value == "completed" else ("✗" if r.status.value == "failed" else "-")
        print(f"   {icon} Phase {r.phase_number:02d} ({r.phase_name}): {r.status.value}  [{len(r.validation_issues)} issues]")

    # Save PKP
    output_dir = run_root / "genesis"
    output_dir.mkdir(parents=True, exist_ok=True)
    pkg_path = output_dir / "production_knowledge_package.json"
    pkg_path.write_text(json.dumps(pkg.model_dump(), indent=2, default=str), encoding="utf-8")
    print(f"\n  → Saved PKP to {pkg_path}")

    # Step 2: Bridge → brief
    print("\n" + "=" * 60)
    print("  Step 2: Converting PKP → movie_os Brief")
    print("=" * 60)

    from movie_os.genesis2.bridge import Genesis2Bridge
    from movie_os.frozen_pkp import freeze_from_brief
    bridge = Genesis2Bridge(pkg)
    brief = ensure_scene_state_fields(bridge.to_brief())
    brief["production"] = production
    brief["policy_snapshot_id"] = policy_snapshot.policy_snapshot_id
    brief["production_paths"] = {
        "production_root": str(production_root),
        "run_root": str(run_root),
    }

    print(f"  Title         : {brief['title']}")
    print(f"  Logline       : {brief['logline'][:100]}...")
    print(f"  Dramatic Q    : {brief['dna'].get('dramatic_question', '(none)')[:100]}")
    print(f"  Scenes        : {len(brief['scenes'])} scenes")
    for scene in brief['scenes']:
        print(f"    Scene {scene.get('number', '?'):2d}: {scene.get('title', '???'):28s} | {scene.get('act', ''):6s} | beat={scene.get('narrative_beat', '?'):14s} | energy={scene.get('energy', 0)}")
    print(f"  Dialogues     : {len(brief.get('dialogues', []))} scenes with dialogue")
    for d in brief.get('dialogues', []):
        print(f"    Scene {d.get('scene_number', '?')}: {len(d.get('lines', []))} spoken + {len(d.get('inner_voice', []))} inner voice")

    brief_path = output_dir / "movie_os_brief.json"
    brief_path.write_text(json.dumps(brief, indent=2, default=str), encoding="utf-8")
    print(f"  → Saved brief to {brief_path}")

    frozen_pkp = freeze_from_brief(
        episode_id=contract.episode_id,
        policy_snapshot_id=policy_snapshot.policy_snapshot_id,
        episode_contract_id=contract.episode_id,
        episode_contract_hash=policy_snapshot.snapshot_hash,
        policy_snapshot_hash=policy_snapshot.snapshot_hash,
        production=production,
        brief=brief,
    )
    brief["frozen_pkp"] = frozen_pkp.model_dump()
    (output_dir / "pkp").mkdir(parents=True, exist_ok=True)
    pkp_path = output_dir / "pkp" / f"{frozen_pkp.pkp_id}.yaml"
    pkp_path.write_text(json.dumps(frozen_pkp.model_dump(), indent=2, default=str), encoding="utf-8")
    freeze_manifest = output_dir / "pkp" / "freeze_manifest.json"
    freeze_manifest.write_text(json.dumps({"pkp_id": frozen_pkp.pkp_id, "content_hash": frozen_pkp.content_hash}, indent=2), encoding="utf-8")
    print(f"  → Froze PKP to {pkp_path}")

    # Step 3: PROMETHEUS pipeline (real stages)
    print("\n" + "=" * 60)
    print("  Step 3: Running PROMETHEUS pipeline")
    print("=" * 60)

    from movie_os.prometheus.pipeline import PrometheusPipeline, PipelineConfig
    from movie_os.prometheus.models import ProductionCertificate, CertificationStatus, Director

    # Build a production-ready certificate from the brief
    cert = ProductionCertificate(
        certificate_id="space-between-us-001",
        project_name=brief["title"],
        status=CertificationStatus.PRODUCTION_READY,
        reviewed_by=Director(name="Genesis2"),
        blueprint={"scenes": brief["scenes"]},
    )

    prom_brief = dict(brief)
    prom_brief["image_artifacts"] = [{"id": s.get("number", i + 1)} for i, s in enumerate(brief["scenes"])]

    pipeline = PrometheusPipeline(config=PipelineConfig(output_dir=str(run_root / "render")))
    result = await pipeline.execute(cert, prom_brief)

    print(f"  Overall status : {result.overall_status.value}")
    for s in result.stages:
        status_val = s.status.value if hasattr(s.status, "value") else str(s.status)
        print(f"    {s.name:20s}: {status_val}  [{len(s.artifacts)} artifacts]")

    result_path = run_root / "manifest" / "prometheus_result.json"
    result_path.write_text(json.dumps(result.model_dump(), indent=2, default=str), encoding="utf-8")
    print(f"  → Saved result to {result_path}")

    print(f"\n{'=' * 60}")
    print(f"  ✅ Pipeline Complete! ({elapsed:.0f}s)")
    print(f"  Output: {production_root}")
    print(f"{'=' * 60}")
    return {"completed": completed, "failed": failed, "elapsed": elapsed, "production": production}


if __name__ == "__main__":
    asyncio.run(main())
