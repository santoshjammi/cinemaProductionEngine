#!/usr/bin/env python3
"""Giri continuation: re-run performance enrichment + freeze on a completed
GENESIS PKP (all 12 phases done). The prior freeze was rejected on
LINE_PERFORMANCE_INCOMPLETE because the enrichment LLM timed out under
resource contention. This re-runs enrichment (bounded) then freezes.

Usage: giri_ep0002_continue.py <episode_id> <run_id>
"""
from __future__ import annotations

import asyncio
import json
import logging
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("giri_continue")

# The completed run (all 12 phases done, freeze rejected on perf).
_episode_id = sys.argv[1] if len(sys.argv) > 1 else "EP-0002"
_run_id = sys.argv[2] if len(sys.argv) > 2 else "RUN-20260829-073618"
RUN_ROOT = ROOT / "productions" / _episode_id / "runs" / _run_id
PKG_PATH = RUN_ROOT / "genesis" / "production_knowledge_package.json"
BRIEF_PATH = RUN_ROOT / "genesis" / "movie_os_brief.json"


async def main():
    from movie_os.genesis2.llm_client import LLMClient
    from movie_os.genesis2.llm_providers import LLMConfig
    from movie_os.genesis2.performance_eval import performance_coverage, voice_binding_coverage
    from movie_os.genesis2.performance_enrich import build_enrichment_context, enrich_dialogue_batches
    from movie_os.frozen_pkp import freeze_from_brief, validate_frozen_pkp
    from movie_os.genesis2.freeze_gate import FreezeIneligibleError

    print("=" * 60)
    print("  GIRI — continuation (enrich + freeze)")
    print("=" * 60)

    brief = json.loads(BRIEF_PATH.read_text(encoding="utf-8"))
    pkg = json.loads(PKG_PATH.read_text(encoding="utf-8"))
    print(f"  Run      : {RUN_ROOT.name}")
    print(f"  Scenes   : {len(brief.get('scenes', []))}")
    print(f"  Dialogues: {len(brief.get('dialogues', []))}")

    # Rebuild the brief from the PKG via the bridge so all authoritative
    # dialogue (all scenes) is carried, not just what the failed run persisted.
    from movie_os.genesis2.bridge import Genesis2Bridge
    from run_space_between_us import ensure_scene_state_fields
    from movie_os.genesis2.models import ProductionKnowledgePackage
    _pkg_obj = ProductionKnowledgePackage.model_validate(pkg)
    _bridge = Genesis2Bridge(_pkg_obj)
    brief = ensure_scene_state_fields(_bridge.to_brief())
    brief["production"] = {"episode_id": _episode_id, "run_id": RUN_ROOT.name}
    brief["policy_snapshot_id"] = brief.get("policy_snapshot_id", "")
    brief["production_paths"] = {"production_root": str(RUN_ROOT.parent), "run_root": str(RUN_ROOT)}
    print(f"  Rebuilt scenes   : {len(brief.get('scenes', []))}")
    print(f"  Rebuilt dialogues: {len(brief.get('dialogues', []))}")

    # Re-run performance enrichment (bounded, qwen3:4b).
    _perf_llm = LLMClient(config=LLMConfig(provider="ollama", model="qwen3:4b",
                                           timeout=120, max_tokens=1024, num_ctx=131072))
    dialogue_batches = brief.get("dialogues", [])

    def _batch_context(batch):
        return build_enrichment_context(
            episode_mechanism=brief.get("primary_mechanism", "pride-driven silence"),
            character_canon=brief.get("characters", {}),
            scene=batch,
            prev_lines=batch.get("lines", [])[:2],
            next_lines=batch.get("lines", [])[2:4],
        )

    enriched_batches, enrichment_result = enrich_dialogue_batches(dialogue_batches, _batch_context, _perf_llm)
    brief["dialogues"] = enriched_batches
    print(f"\n  Enrichment: passed={enrichment_result['passed']} repaired={enrichment_result['repaired_lines']}")
    if not enrichment_result["passed"]:
        print(f"  ⚠ Enrichment incomplete: {enrichment_result['blocker']['code']}")

    _all_lines = [ln for d in brief.get("dialogues", []) for ln in d.get("lines", [])]
    _perf_cov = performance_coverage(_all_lines)
    _voice_cov = voice_binding_coverage(_all_lines)
    brief["performance_satisfaction_manifest"] = {
        "authoritative_dialogue_lines": len(_all_lines),
        "performance_coverage": _perf_cov,
        "voice_binding_reconciliation": _voice_cov,
    }
    print(f"  Performance coverage : {_perf_cov['complete_records']}/{_perf_cov['expected']} "
          f"({_perf_cov['percentage']:.0f}%) | voice bindings {_voice_cov['resolved']}/{_voice_cov['authoritative_lines']}")

    # Persist updated brief.
    BRIEF_PATH.write_text(json.dumps(brief, indent=2, default=str), encoding="utf-8")

    # Freeze.
    production = brief.get("production", {"episode_id": _episode_id, "run_id": RUN_ROOT.name})
    policy_snapshot_id = brief.get("policy_snapshot_id", "")
    from movie_os.genesis2.requirement_manifest import compile_episode_requirements
    manifest = compile_episode_requirements(
        episode_id=_episode_id, synopsis=brief.get("synopsis", ""),
        contract={"working_title": brief.get("title", "")},
    )
    brief["canonical_requirements"] = [r.to_dict() for r in manifest.requirements]
    brief["requirement_manifest"] = manifest.to_dict()

    try:
        frozen_pkp = freeze_from_brief(
            episode_id=_episode_id,
            policy_snapshot_id=policy_snapshot_id,
            episode_contract_id=_episode_id,
            episode_contract_hash=policy_snapshot_id,
            policy_snapshot_hash=policy_snapshot_id,
            production=production,
            brief=brief,
            genesis_pkg=None,
        )
    except FreezeIneligibleError as exc:
        print("\n  ⛔ FREEZE ELIGIBILITY REJECTED")
        for b in exc.result.blocking_reasons:
            print(f"      - {b.get('code','?')} @ {b.get('phase','?')}: {b.get('detail','')[:100]}")
        raise

    brief["frozen_pkp"] = frozen_pkp.model_dump()
    (RUN_ROOT / "genesis" / "pkp").mkdir(parents=True, exist_ok=True)
    pkp_path = RUN_ROOT / "genesis" / "pkp" / f"{frozen_pkp.pkp_id}.yaml"
    pkp_path.write_text(json.dumps(frozen_pkp.model_dump(), indent=2, default=str), encoding="utf-8")
    (RUN_ROOT / "genesis" / "pkp" / "freeze_manifest.json").write_text(
        json.dumps({"pkp_id": frozen_pkp.pkp_id, "content_hash": frozen_pkp.content_hash}, indent=2), encoding="utf-8")

    validate_frozen_pkp(frozen_pkp.model_dump(), expected_episode_id=_episode_id, expected_policy_snapshot_id=policy_snapshot_id)
    assert frozen_pkp.content_hash == frozen_pkp.compute_content_hash(), "PKP content hash mismatch"

    print(f"\n  → FROZEN PKP  : {pkp_path}")
    print(f"  → Freeze id   : {frozen_pkp.pkp_id}  hash={frozen_pkp.content_hash[:16]}...")
    return {"pkp_id": frozen_pkp.pkp_id, "pkp_path": str(pkp_path), "run_root": str(RUN_ROOT)}


if __name__ == "__main__":
    asyncio.run(main())
