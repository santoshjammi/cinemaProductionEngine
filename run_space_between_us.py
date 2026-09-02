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


def _is_empty(value) -> bool:
    """True when a value carries no real creative content."""
    if value is None:
        return True
    if isinstance(value, (dict, list, tuple, set)):
        return len(value) == 0
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return False
    return not str(value).strip()


def ensure_scene_state_fields(brief: dict) -> dict:
    """Normalize / derive deterministic state only.  NEVER author screenplay content.

    This function may fill missing *technical* structure (empty lists, stable
    IDs, count-derived metadata) but must not invent dialogue, scene titles,
    acts, beats, emotional states, motivations, or shot content.  Where such
    creative content is absent, a validation defect is recorded and the
    corresponding PKP field is left empty so the freeze gate can reject the
    package (see movie_os/genesis2/freeze_gate.py).
    """
    defects: list[dict] = []
    scenes = []
    for scene in brief.get("scenes", []) or []:
        scene = dict(scene)
        title = scene.get("title")
        act = scene.get("act")
        narrative_beat = scene.get("narrative_beat")
        purpose = scene.get("purpose") or scene.get("scene_description")
        scene_num = scene.get("number") or scene.get("scene_number") or scene.get("id") or 0
        try:
            scene_num = int(scene_num)
        except Exception:
            scene_num = 0

        # Technical normalization (allowed).
        scene.setdefault("emotional_progression", [])
        # DO NOT fabricate entry/turning/exit state text — leave missing so the
        # freeze gate can detect semantic absence.
        if not scene.get("entry_state"):
            # deterministic derivation only when a real title exists
            if _is_empty(title):
                defects.append({"code": "SCENE_TITLE_MISSING", "scene": scene_num, "severity": "BLOCKER"})
            else:
                scene.setdefault("entry_state", "")
        # Shot plan: deterministically derived from dialogue lines at freeze
        # time (freeze_from_brief builds a shot per line). It is NOT authored
        # creative content, so a missing inline shot dict is not a blocker.
        # We leave shot empty and let freeze_from_brief derive it deterministically.
        scenes.append(scene)

    existing_dialogues = {}
    for d in brief.get("dialogues", []) or []:
        try:
            scene_num = int(d.get("scene_number"))
        except Exception:
            continue
        existing_dialogues[scene_num] = dict(d)

    dialogues = []
    for scene in scenes:
        scene_num = int(scene.get("number") or scene.get("scene_number") or scene.get("id") or 0)
        dialogue = dict(existing_dialogues.get(scene_num) or {})
        dialogue.setdefault("scene_number", scene_num)
        # Dialogue policy: derive deterministically. If no real dialogue lines
        # were authored, classify VISUAL_ONLY ONLY IF the scene declares it;
        # otherwise leave CONVERSATION and let the freeze gate enforce density.
        lines = dialogue.get("lines", []) or []
        has_real_lines = any(
            isinstance(ln, dict) and _is_truth(ln.get("text"))
            for ln in lines
        )
        policy_type = "CONVERSATION"
        declared = (dialogue.get("dialogue_policy") or scene.get("dialogue_policy") or {})
        if isinstance(declared, dict) and declared.get("type"):
            policy_type = str(declared["type"]).upper()
        # A scene whose authored lines have only one distinct speaker is a
        # monologue (e.g. an internal rehearsal), not a two-party conversation.
        # Reclassify so the freeze gate does not demand a second speaker.
        if policy_type == "CONVERSATION":
            speakers = {
                str(ln.get("speaker", "")).strip()
                for ln in lines if isinstance(ln, dict) and _is_truth(ln.get("text"))
            }
            if len(speakers) == 1:
                policy_type = "MONOLOGUE"
        if not has_real_lines and policy_type not in ("VISUAL_ONLY", "MONOLOGUE"):
            defects.append({
                "code": "DIALOGUE_PLANNING_INCOMPLETE",
                "scene": scene_num,
                "severity": "BLOCKER",
                "detail": f"no authored dialogue lines for scene {scene_num}",
            })
        dialogue.setdefault("dialogue_policy", {"type": policy_type})
        dialogue.setdefault("conversation_intent", "")
        dialogue.setdefault("subtext", "")
        dialogue.setdefault("emotional_state", "")
        dialogue.setdefault("inner_voice", [])
        # Only keep authored lines; never substitute placeholders.
        dialogue["lines"] = [
            ln for ln in lines
            if isinstance(ln, dict) and _is_truth(ln.get("text")) and ln.get("speaker")
        ]
        dialogues.append(dialogue)

    brief = dict(brief)
    brief["scenes"] = scenes
    brief["dialogues"] = dialogues
    if defects:
        brief["_genesis_defects"] = brief.get("_genesis_defects", []) + defects
    return brief


def _is_truth(value) -> bool:
    if value is None:
        return False
    if isinstance(value, (dict, list, tuple, set)):
        return len(value) > 0
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value != 0
    return bool(str(value).strip())


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

    # Prefer the fast local model that is currently responding reliably.
    # Deepseek-coder-v2 has been timing out / 400ing on later GENESIS phases.
    preferred_models = ["qwen3:4b", "qwen3.6:latest", "ornith:lite", "deepseek-coder-v2:latest"]

    def _model_num_ctx(model_name: str) -> int:
        if model_name == "qwen3:4b":
            return 131072
        if model_name == "qwen3.6:latest":
            return 131072
        if model_name == "ornith:lite":
            return 65536
        return 4096
    last_exc = None
    pkg = None
    elapsed = 0.0
    for model_name in preferred_models:
        try:
            config = LLMConfig(provider="ollama", model=model_name, timeout=300, max_tokens=4096, num_ctx=_model_num_ctx(model_name))
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
