#!/usr/bin/env python3
"""GENESIS freeze-only driver — run GENESIS to a frozen PKP and STOP.

Reuses the canonical GENESIS chain from run_space_between_us.py (policy
snapshot -> Genesis2 -> bridge -> frozen PKP) and halts immediately after
freeze. It does NOT invoke PROMETHEUS or any expensive media generation.
"""
import asyncio, json, logging, sys, time
from pathlib import Path

from movie_os.runtime_policy import load_and_resolve_canonical_policy

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

# Shared LLM config loader (single source of truth for model selection).
sys.path.insert(0, "/Users/santosh/.hermes/scripts")
from llm_config import get_model
# Shared resource governor client (LOCAL-AI-RESOURCE-GOVERNOR-001).
from local_ai_gov_py import request_lease, release_lease

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("genesis_freeze_only")

# Reuse the canonical synopsis + constraints + scene-state helper.
from run_space_between_us import SYNOPSIS, CONSTRAINTS, ensure_scene_state_fields


async def _run_genesis():
    from movie_os.genesis2 import Genesis2Engine
    from movie_os.genesis2.llm_client import LLMClient
    from movie_os.genesis2.llm_providers import LLMConfig
    from movie_os.genesis2.bridge import Genesis2Bridge
    from movie_os.frozen_pkp import freeze_from_brief, validate_frozen_pkp
    from movie_os.runtime_paths import get_production_context

    # Step 0: Episode Contract + Effective Policy Snapshot
    contract, policy_snapshot, policy_paths = load_and_resolve_canonical_policy()
    print(f"  Contract : {contract.episode_id} / {contract.working_title}")
    print(f"  Policy   : {policy_snapshot.policy_snapshot_id}")

    # Step 1: Genesis2 (real local Ollama) — inject the frozen canonical
    # requirement manifest into the generation constraints so downstream phases
    # are guided to preserve every MUST promise (P0-03R: manifest constrains
    # generation, not merely gates it at the end).
    from movie_os.genesis2.requirement_manifest import compile_episode_requirements
    _req_manifest = compile_episode_requirements(
        episode_id=contract.episode_id,
        synopsis=SYNOPSIS,
        contract={"working_title": contract.working_title},
    )
    print(f"\n  Canonical requirements : {len(_req_manifest.requirements)} (frozen, hash={_req_manifest.content_hash[:12]}...)")
    for r in _req_manifest.requirements:
        print(f"    {r.id} {r.category:22s} {r.obligation}  — {r.statement[:70]}")
    gen_constraints = dict(CONSTRAINTS)
    gen_constraints["canonical_requirements"] = [
        {"id": r.id, "category": r.category, "statement": r.statement, "obligation": r.obligation}
        for r in _req_manifest.requirements
    ]

    preferred_models = [get_model(), "qwen3.6:latest", "ornith:lite"]

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
    for model_name in preferred_models:
        try:
            config = LLMConfig(provider="ollama", model=model_name, timeout=300, max_tokens=8192, num_ctx=_model_num_ctx(model_name))
            engine = Genesis2Engine(llm=LLMClient(config=config))
            print(f"\n  Using local model: {model_name}")
            t0 = time.time()
            pkg = await engine.run_async(synopsis=SYNOPSIS, constraints=gen_constraints)
            print(f"  GENESIS elapsed: {time.time() - t0:.0f}s")
            break
        except Exception as exc:
            last_exc = exc
            logger.warning("Genesis2 failed with %s: %s", model_name, exc)
            pkg = None
    if pkg is None:
        raise RuntimeError(f"Genesis2 failed with all local models: {last_exc}")

    completed = sum(1 for r in pkg.phase_results if r.status.value == "completed")
    failed = sum(1 for r in pkg.phase_results if r.status.value == "failed")
    print(f"  Completed: {completed}   Failed: {failed}")
    for r in pkg.phase_results:
        icon = "✓" if r.status.value == "completed" else ("✗" if r.status.value == "failed" else "-")
        print(f"    {icon} Phase {r.phase_number:02d} ({r.phase_name}): {r.status.value}  [{len(r.validation_issues)} issues]")

    # Step 2: Bridge -> brief -> frozen PKP
    production = {"episode_id": "EP-0001", "run_id": f"RUN-{time.strftime('%Y%m%d-%H%M%S')}"}
    prod_ctx = get_production_context({"production": production})
    production_root = Path(prod_ctx["production_root"])
    run_root = Path(prod_ctx["run_root"])
    for sub in ["contract", "policy", "genesis", "runs", "oracle", "releases"]:
        (production_root / sub).mkdir(parents=True, exist_ok=True)

    bridge = Genesis2Bridge(pkg)
    brief = ensure_scene_state_fields(bridge.to_brief())
    brief["production"] = production
    brief["policy_snapshot_id"] = policy_snapshot.policy_snapshot_id
    brief["production_paths"] = {"production_root": str(production_root), "run_root": str(run_root)}
    # Narrative contract: Mark & Sarah episodes are LINEAR drama with a REQUIRED
    # resolution. The freeze gate consumes this deterministically.
    brief.setdefault("narrative_contract", {
        "resolution_requirement": "REQUIRED",
        "narrative_structure": "LINEAR",
    })

    # Character preparation — resolve the characters that appear in this brief
    # (or the psychology default) and inject `brief['character_consistency']` so
    # the image stage anchors every scene to the same character identities.
    from movie_os.genesis2.character_prep import prepare_characters
    prepare_characters(brief)

    # ── P0-03R: Compile + freeze the CANONICAL requirement manifest BEFORE any
    # downstream reconciliation.  The denominator must come from the approved
    # concept (contract + synopsis), never from the artifact being evaluated.
    from movie_os.genesis2.requirement_manifest import compile_episode_requirements
    manifest = compile_episode_requirements(
        episode_id=contract.episode_id,
        synopsis=SYNOPSIS,
        contract={"working_title": contract.working_title},
    )
    brief["canonical_requirements"] = [r.to_dict() for r in manifest.requirements]
    brief["requirement_manifest"] = manifest.to_dict()
    print(f"\n  Canonical requirements : {len(manifest.requirements)} (frozen, hash={manifest.content_hash[:12]}...)")
    for r in manifest.requirements:
        print(f"    {r.id} {r.category:22s} {r.obligation}")

    print(f"\n  Title      : {brief['title']}")
    print(f"  Scenes     : {len(brief['scenes'])} scenes")
    for scene in brief['scenes']:
        print(f"    Scene {scene.get('number','?'):2d}: {scene.get('title','???'):28s} | {scene.get('act',''):6s} | beat={scene.get('narrative_beat','?'):12s} | energy={scene.get('energy',0)}")
    print(f"  Dialogues  : {len(brief.get('dialogues',[]))} scenes with dialogue")
    for d in brief.get('dialogues', []):
        print(f"    Scene {d.get('scene_number','?')}: {len(d.get('lines',[]))} spoken + {len(d.get('inner_voice',[]))} inner voice")

    # ── P0-04: Performance enrichment — fill only missing mandatory fields.
    # Authoritative lines come from the bridge (orphans already excluded).
    # Enrichment never rewrites dialogue text and never overwrites authored
    # performance; it supplies only missing subtext/delivery/emotional state.
    from movie_os.genesis2.performance_eval import (
        normalize_performance_fields,
        performance_coverage,
        voice_binding_coverage,
        _line_missing_fields,
    )
    from movie_os.genesis2.performance_enrich import build_enrichment_context, enrich_dialogue_batches
    from movie_os.genesis2.llm_client import LLMClient
    from movie_os.genesis2.llm_providers import LLMConfig

    _perf_llm = LLMClient(config=LLMConfig(provider="ollama", model=get_model(),
                                           timeout=90, max_tokens=1024, num_ctx=_model_num_ctx(get_model())))
    dialogue_batches = brief.get("dialogues", [])

    def _batch_context(batch):
        return build_enrichment_context(
            episode_mechanism=brief.get("primary_mechanism", "fear-based withdrawal"),
            character_canon=brief.get("characters", {}),
            scene=batch,
            prev_lines=batch.get("lines", [])[:2],
            next_lines=batch.get("lines", [])[2:4],
        )

    enriched_batches, enrichment_result = enrich_dialogue_batches(dialogue_batches, _batch_context, _perf_llm)
    brief["dialogues"] = enriched_batches
    _enriched_count = enrichment_result["repaired_lines"]
    if not enrichment_result["passed"]:
        # P0 (VIDEO_FIRST_POLICY): performance enrichment is a non-blocking
        # quality improvement.  The dialogue is already authored and valid; a
        # generic/blank enrichment or an enrichment LLM timeout must not crash
        # the run.  Log the blocker and continue with the original authored
        # dialogue so GENESIS can reach the freeze gate.
        brief["performance_enrichment_blocker"] = enrichment_result["blocker"]
        print(f"\n  ⚠ PERFORMANCE ENRICHMENT PARTIAL: {enrichment_result['blocker']['code']} (continuing with authored dialogue)")

    # Performance coverage evidence (authoritative denominator).
    _all_lines = [ln for d in brief.get("dialogues", []) for ln in d.get("lines", [])]
    _perf_cov = performance_coverage(_all_lines)
    _voice_cov = voice_binding_coverage(_all_lines)
    brief["performance_satisfaction_manifest"] = {
        "authoritative_dialogue_lines": len(_all_lines),
        "performance_coverage": _perf_cov,
        "voice_binding_reconciliation": _voice_cov,
        "lines_enriched": _enriched_count,
    }
    print(f"\n  Performance coverage : {_perf_cov['complete_records']}/{_perf_cov['expected']} "
          f"({_perf_cov['percentage']:.0f}%) | voice bindings {_voice_cov['resolved']}/{_voice_cov['authoritative_lines']}")

    output_dir = run_root / "genesis"
    output_dir.mkdir(parents=True, exist_ok=True)
    pkg_path = output_dir / "production_knowledge_package.json"
    pkg_path.write_text(json.dumps(pkg.model_dump(), indent=2, default=str), encoding="utf-8")

    # ── P0-03R-SER-01: persistence integrity — prove in-memory == persisted ==
    # reloaded before freeze.  The live PKG must not lose subclass semantic
    # fields through serialization.  Attach the report to the brief (BEFORE it
    # is written) so the persisted artifact carries the proof and the freeze
    # gate can block (PERSISTED_KNOWLEDGE_MISMATCH) on any loss.
    from movie_os.genesis2.serialization_reconciliation import serialize_reconcile_package
    ser_report = serialize_reconcile_package(pkg)
    brief["serialization_reconciliation"] = ser_report
    print(f"\n  Persistence integrity : {ser_report['semantic_information_loss']} phase(s) lost fields "
          f"({'PASS' if ser_report['passed'] else 'FAIL'})")

    brief_path = output_dir / "movie_os_brief.json"
    brief_path.write_text(json.dumps(brief, indent=2, default=str), encoding="utf-8")

    from movie_os.genesis2.freeze_gate import FreezeIneligibleError
    try:
        frozen_pkp = freeze_from_brief(
            episode_id=contract.episode_id,
            policy_snapshot_id=policy_snapshot.policy_snapshot_id,
            episode_contract_id=contract.episode_id,
            episode_contract_hash=policy_snapshot.snapshot_hash,
            policy_snapshot_hash=policy_snapshot.snapshot_hash,
            production=production,
            brief=brief,
            genesis_pkg=pkg,  # deterministic freeze-eligibility gate (P0-01)
        )
    except FreezeIneligibleError as exc:
        print("\n  ⛔ FREEZE ELIGIBILITY REJECTED (P0-01 fail-closed)")
        for b in exc.result.blocking_reasons:
            print(f"      - {b.get('code','?')} @ {b.get('phase','?')}: {b.get('detail','')[:100]}")
        brief_path = output_dir / "movie_os_brief.json"
        brief_path.write_text(json.dumps(brief, indent=2, default=str), encoding="utf-8")
        raise
    brief["frozen_pkp"] = frozen_pkp.model_dump()
    (output_dir / "pkp").mkdir(parents=True, exist_ok=True)
    pkp_path = output_dir / "pkp" / f"{frozen_pkp.pkp_id}.yaml"
    pkp_path.write_text(json.dumps(frozen_pkp.model_dump(), indent=2, default=str), encoding="utf-8")
    freeze_manifest = output_dir / "pkp" / "freeze_manifest.json"
    freeze_manifest.write_text(json.dumps({"pkp_id": frozen_pkp.pkp_id, "content_hash": frozen_pkp.content_hash}, indent=2), encoding="utf-8")

    # Self-verify: the frozen PKP must pass validate_frozen_pkp + hash check.
    validate_frozen_pkp(
        frozen_pkp.model_dump(),
        expected_episode_id=contract.episode_id,
        expected_policy_snapshot_id=policy_snapshot.policy_snapshot_id,
    )
    assert frozen_pkp.content_hash == frozen_pkp.compute_content_hash(), "PKP content hash mismatch"

    print(f"\n  → FROZEN PKP  : {pkp_path}")
    print(f"  → Freeze id   : {frozen_pkp.pkp_id}  hash={frozen_pkp.content_hash[:16]}...")
    print(f"  → Brief       : {brief_path}")
    print(f"  → Raw PKG     : {pkg_path}")
    print("\n  STOPPING BEFORE PROMETHEUS — no media generated.")

    return {"production": production, "pkp_id": frozen_pkp.pkp_id, "content_hash": frozen_pkp.content_hash, "run_root": str(run_root)}


async def main():
    """LOCAL-AI-RESOURCE-GOVERNOR-001 §C/§D: wrap GENESIS in a local_llm lease.

    Acquire the lease at the coherent language-generation boundary, run the
    existing GENESIS pipeline to a frozen PKP, then release the lease in a
    finally (guaranteed cleanup on success AND failure). After the package is
    frozen, the LLM lease is released so PROMETHEUS/ComfyUI is not blocked.
    """
    print("=" * 60)
    print("  GENESIS -> FROZEN PKP (no PROMETHEUS)")
    print("=" * 60)

    lease = request_lease(
        application="videogen-genesis",
        workload="genesis_language_generation",
        priority=80,
        context=131072,
        resource_class="local_llm",
    )
    if lease["status"] in ("queued", "rejected"):
        print(f"  ⛔ GOVERNOR: {lease['status']} ({lease['reason']}) — GENESIS deferred, not starting")
        return {"status": lease["status"], "reason": lease["reason"]}
    lease_id = lease["lease_id"]
    print(f"  Resource lease   : granted ({lease_id}) local_llm videogen-genesis")

    try:
        return await _run_genesis()
    finally:
        # §D: release the local_llm lease after the frozen package is produced
        # (success) OR on failure (VG-07). Guaranteed cleanup either way. The
        # governor also expires stale leases if this process is killed.
        release_lease(lease_id)
        print(f"  Resource lease   : released ({lease_id})")


if __name__ == "__main__":
    asyncio.run(main())
