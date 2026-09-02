#!/usr/bin/env python3
"""Parameterized episode driver — GENESIS → frozen PKP → PROMETHEUS multishot.

Reuses the exact proven stack from EP-0001 (GENESIS2 + bridge + freeze gate +
PROMETHEUS multishot with Ken Burns) for a NEW episode. This is the
repeatability driver: it takes an episode's synopsis/constraints/contract and
runs the full pipeline to a playable MP4.

No platform refactoring — this is a thin parameterized wrapper over the
existing, validated components.
"""
from __future__ import annotations

import asyncio
import json
import logging
import shutil
import subprocess
import sys
import time

# Shared LLM config loader (single source of truth for model selection).
sys.path.insert(0, "/Users/santosh/.hermes/scripts")
from llm_config import get_model
# Shared resource governor client (LOCAL-AI-RESOURCE-GOVERNOR-001).
from local_ai_gov_py import request_lease, release_lease, take_comfyui_lease
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("run_episode")

# ---------------------------------------------------------------------------
# EP-0002 concept (distinct from EP-0001, same Mark/Sarah canon)
# ---------------------------------------------------------------------------
EPISODE = {
    "episode_id": "EP-0002",
    "working_title": "The Apology That Never Came",
    "synopsis": (
        "After a heated argument about money, Mark says something cutting to Sarah and "
        "immediately regrets it, but pride stops him from apologizing. He buries the "
        "guilt in extra work and silence, while Sarah waits for an apology that never "
        "comes. The emotional turning point arrives when Sarah admits she doesn't need "
        "an apology — she needs to know he still cares. Mark finally breaks his silence "
        "and says the words he was too proud to say."
    ),
    "constraints": {
        "runtime": "3-5 minutes",
        "platform": "youtube",
        "grammar": "psychological_cinema",
        "tone_arc": "secure → tense → guilty → distant → vulnerable → reconciled",
        "characters": (
            "MARK (38, responsible, loving, proud, emotionally contained; struggles to admit fault), "
            "SARAH (36, perceptive, patient, affectionate, increasingly hurt by his silence)"
        ),
        "style": (
            "Cinematic psychological realism. Warm domestic lighting gradually becomes colder as "
            "Mark withdraws. Minimal narration, strong facial micro-expressions, meaningful blocking "
            "and distance, restrained piano score."
        ),
    },
    "contract": {
        "episode_id": "EP-0002",
        "working_title": "The Apology That Never Came",
        "classification": {
            "niche": "Psychology",
            "domain": "Relationship & Emotional Psychology",
            "problem_family": "RP-01",
            "sub_series": "RP-01-S01",
        },
        "universe": {
            "universe_id": "UNIVERSE-MARK-SARAH",
            "primary_characters": ["Mark", "Sarah"],
        },
        "story": {
            "primary_mechanism": "pride-driven silence",
            "story_context": "A financial argument escalates into a hurtful exchange during a busy week.",
            "viewer_recognition": "Silence after a hurtful moment is often pride, not indifference",
            "responsibility_pattern": "both",
            "intended_resolution": "Meaningful progress through honest disclosure and practical rebalancing.",
        },
        "format": {
            "format_profile": "YOUTUBE_LONGFORM_16X9",
            "target_runtime": "12m",
        },
        "continuity": {"required": True},
        "status": {"contract_state": "approved"},
    },
    "ontology_selection": {
        "niche": "Psychology",
        "domain": "Relationship & Emotional Psychology",
        "problem_family": "RP-01",
        "sub_series": "RP-01-S01",
    },
}

# Ken Burns motion per shot purpose (same as EP-0001 multishot).
MOTION_BY_PURPOSE = {
    "ESTABLISHING": "pan_right",
    "SPEAKER_COVERAGE": "zoom_in",
    "LISTENER_REACTION": "zoom_out",
    "TWO_SHOT": "pan_left",
    "EMOTIONAL_HOLD": "zoom_in",
    "INSERT": "zoom_in",
}

# Character anchors (verbatim) for identity consistency.
ANCHORS = (
    "MARK: a tall, lean man in his late 30s with warm brown skin, short black hair "
    "with a silver streak at the left temple. "
    "SARAH: a woman of medium height in her early 30s with light tan skin and long dark wavy hair."
)
STYLE = (
    "cinematic film still, photorealistic, realistic adult drama, "
    "natural warm lighting, shallow depth of field, "
    "sharp expressive faces, subtle skin texture, "
    "professional cinematography, high production value, "
    "crisp clean image, high detail"
)
QUALITY = (
    "BOTH MARK and SARAH clearly visible in frame, sharp focused detailed faces, "
    "crystal-clear high resolution, bright vibrant well-lit, "
    "professional lighting, crisp clean image, "
    "natural skin tones, warm inviting atmosphere, "
    "glowing healthy skin, balanced exposure"
)
NEGATIVE = (
    "3D animation, cartoon, Pixar, DreamWorks, anime, illustration, "
    "stylized, cel-shaded, glossy plastic skin, "
    "blurry, out of focus, soft focus, low resolution, grainy, "
    "dark, dimly lit, underexposed, vintage, retro, hazy, foggy, noise, "
    "distorted, deformed, ugly, bad anatomy, extra limbs, watermark, text"
)


# ---------------------------------------------------------------------------
# GENESIS → frozen PKP (parameterized)
# ---------------------------------------------------------------------------
async def run_genesis(episode: dict) -> dict:
    from movie_os.genesis2 import Genesis2Engine
    from movie_os.genesis2.llm_client import LLMClient
    from movie_os.genesis2.llm_providers import LLMConfig
    from movie_os.genesis2.bridge import Genesis2Bridge
    from movie_os.genesis2.requirement_manifest import compile_episode_requirements
    from movie_os.frozen_pkp import freeze_from_brief, validate_frozen_pkp
    from movie_os.runtime_paths import get_production_context
    from movie_os.runtime_policy import (
        validate_episode_contract, resolve_policy, persist_production_policy,
    )
    from run_space_between_us import ensure_scene_state_fields

    episode_id = episode["episode_id"]
    synopsis = episode["synopsis"]
    constraints = dict(episode["constraints"])
    contract_data = episode["contract"]
    ontology_selection = episode["ontology_selection"]

    print("=" * 60)
    print(f"  GENESIS → FROZEN PKP — {episode_id}")
    print("=" * 60)

    # Step 0: Episode Contract + Effective Policy Snapshot (parameterized).
    contract = validate_episode_contract(contract_data)
    from movie_os.runtime_policy import _read_yaml, _sha256, DOCS
    format_profile = _read_yaml(DOCS / "40_contracts" / "FORMAT_PROFILE.schema.yaml")
    source_versions = {
        "docs/00_governance/01_CINEMA_MASTER_CONSTITUTION.md": "2026-08-10",
        "docs/10_psychology/00_PSYCHOLOGY_SUB_CONSTITUTION.md": "2026-08-10",
        "docs/10_psychology/10_mark_sarah/00_MARK_SARAH_SERIES_CONSTITUTION.md": "2026-08-10",
        "docs/20_standards/DIALOGUE_AND_PERFORMANCE_STANDARD.md": "2026-08-10",
        "docs/20_standards/EMOTIONAL_CONTINUITY_STANDARD.md": "2026-08-10",
        "docs/20_standards/VISUAL_CHARACTER_CONTINUITY_STANDARD.md": "2026-08-10",
        "docs/20_standards/VOICE_AUDIO_STANDARD.md": "2026-08-10",
        "docs/20_standards/MOTION_AND_LIPSYNC_STANDARD.md": "2026-08-10",
        "docs/20_standards/CINEMATIC_SHOT_LANGUAGE_STANDARD.md": "2026-08-10",
        "docs/20_standards/ANTI_AI_SLOP_QUALITY_STANDARD.md": "2026-08-10",
        "docs/40_contracts/FORMAT_PROFILE.schema.yaml": _sha256(format_profile),
    }
    policy_snapshot = resolve_policy(contract, ontology_selection, format_profile=format_profile, source_versions=source_versions)
    persist_production_policy(contract, policy_snapshot)
    print(f"  Contract : {contract.episode_id} / {contract.working_title}")
    print(f"  Policy   : {policy_snapshot.policy_snapshot_id}")

    # Step 1: Genesis2 (real local Ollama) with canonical requirement manifest.
    _req_manifest = compile_episode_requirements(
        episode_id=episode_id, synopsis=synopsis, contract={"working_title": contract.working_title},
    )
    print(f"\n  Canonical requirements : {len(_req_manifest.requirements)} (frozen, hash={_req_manifest.content_hash[:12]}...)")
    gen_constraints = dict(constraints)
    gen_constraints["canonical_requirements"] = [
        {"id": r.id, "category": r.category, "statement": r.statement, "obligation": r.obligation}
        for r in _req_manifest.requirements
    ]

    preferred_models = ["qwen3:4b", "qwen3.6:latest", "ornith:lite"]

    def _model_num_ctx(model_name: str) -> int:
        if model_name == "qwen3:4b":
            # 32768 ctx loads at ~7.6GB — the evidence-backed sweet spot on the
            # 32GB M1 Max. It produced 5 rich scenes, 30/30 performance, and
            # completed cleanly with zero stuck states. 131072 loads at 22-23GB
            # and thrashes near the 32GB limit (stuck "Stopping..." states).
            # 8192 loads at 3.9GB but under-produces sparse scenes. 32768 is
            # the verified working value. DO NOT CHANGE without new evidence.
            return 32768
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
            pkg = await engine.run_async(synopsis=synopsis, constraints=gen_constraints)
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

    # Step 2: Bridge → brief → frozen PKP.
    production = {"episode_id": episode_id, "run_id": f"RUN-{time.strftime('%Y%m%d-%H%M%S')}"}
    prod_ctx = get_production_context({"production": production})
    production_root = Path(prod_ctx["production_root"])
    run_root = Path(prod_ctx["run_root"])
    for sub in ["contract", "policy", "genesis", "runs", "oracle", "releases"]:
        (production_root / sub).mkdir(parents=True, exist_ok=True)
    for sub in ["images", "voice", "music", "motion", "render", "manifest"]:
        (run_root / sub).mkdir(parents=True, exist_ok=True)

    bridge = Genesis2Bridge(pkg)
    brief = ensure_scene_state_fields(bridge.to_brief())
    brief["production"] = production
    brief["policy_snapshot_id"] = policy_snapshot.policy_snapshot_id
    brief["production_paths"] = {"production_root": str(production_root), "run_root": str(run_root)}
    brief.setdefault("narrative_contract", {
        "resolution_requirement": "REQUIRED",
        "narrative_structure": "LINEAR",
    })

    # Character preparation — resolve the characters that appear in this brief
    # (or the psychology default) and inject `brief['character_consistency']` so
    # the image stage anchors every scene to the same character identities.
    from movie_os.genesis2.character_prep import prepare_characters
    prepare_characters(brief)

    manifest = compile_episode_requirements(
        episode_id=episode_id, synopsis=synopsis, contract={"working_title": contract.working_title},
    )
    brief["canonical_requirements"] = [r.to_dict() for r in manifest.requirements]
    brief["requirement_manifest"] = manifest.to_dict()

    print(f"\n  Title      : {brief['title']}")
    print(f"  Scenes     : {len(brief['scenes'])} scenes")
    for scene in brief['scenes']:
        print(f"    Scene {scene.get('number','?'):2d}: {scene.get('title','???'):28s} | {scene.get('act',''):6s} | beat={scene.get('narrative_beat','?'):12s} | energy={scene.get('energy',0)}")
    print(f"  Dialogues  : {len(brief.get('dialogues',[]))} scenes with dialogue")
    for d in brief.get('dialogues', []):
        print(f"    Scene {d.get('scene_number','?')}: {len(d.get('lines',[]))} spoken + {len(d.get('inner_voice',[]))} inner voice")

    # Performance enrichment (non-blocking).
    from movie_os.genesis2.performance_eval import (
        normalize_performance_fields, performance_coverage, voice_binding_coverage,
    )
    from movie_os.genesis2.performance_enrich import build_enrichment_context, enrich_dialogue_batches
    _perf_llm = LLMClient(config=LLMConfig(provider="ollama", model=get_model(), timeout=90, max_tokens=1024, num_ctx=_model_num_ctx(get_model())))
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
    if not enrichment_result["passed"]:
        brief["performance_enrichment_blocker"] = enrichment_result["blocker"]
        print(f"\n  ⚠ PERFORMANCE ENRICHMENT PARTIAL: {enrichment_result['blocker']['code']} (continuing with authored dialogue)")

    _all_lines = [ln for d in brief.get("dialogues", []) for ln in d.get("lines", [])]
    _perf_cov = performance_coverage(_all_lines)
    _voice_cov = voice_binding_coverage(_all_lines)
    brief["performance_satisfaction_manifest"] = {
        "authoritative_dialogue_lines": len(_all_lines),
        "performance_coverage": _perf_cov,
        "voice_binding_reconciliation": _voice_cov,
    }
    print(f"\n  Performance coverage : {_perf_cov['complete_records']}/{_perf_cov['expected']} "
          f"({_perf_cov['percentage']:.0f}%) | voice bindings {_voice_cov['resolved']}/{_voice_cov['authoritative_lines']}")

    output_dir = run_root / "genesis"
    output_dir.mkdir(parents=True, exist_ok=True)
    pkg_path = output_dir / "production_knowledge_package.json"
    pkg_path.write_text(json.dumps(pkg.model_dump(), indent=2, default=str), encoding="utf-8")

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
            episode_id=episode_id,
            policy_snapshot_id=policy_snapshot.policy_snapshot_id,
            episode_contract_id=episode_id,
            episode_contract_hash=policy_snapshot.snapshot_hash,
            policy_snapshot_hash=policy_snapshot.snapshot_hash,
            production=production,
            brief=brief,
            genesis_pkg=pkg,
        )
    except FreezeIneligibleError as exc:
        print("\n  ⛔ FREEZE ELIGIBILITY REJECTED (P0-01 fail-closed)")
        for b in exc.result.blocking_reasons:
            print(f"      - {b.get('code','?')} @ {b.get('phase','?')}: {b.get('detail','')[:100]}")
        raise

    brief["frozen_pkp"] = frozen_pkp.model_dump()
    (output_dir / "pkp").mkdir(parents=True, exist_ok=True)
    pkp_path = output_dir / "pkp" / f"{frozen_pkp.pkp_id}.yaml"
    pkp_path.write_text(json.dumps(frozen_pkp.model_dump(), indent=2, default=str), encoding="utf-8")
    freeze_manifest = output_dir / "pkp" / "freeze_manifest.json"
    freeze_manifest.write_text(json.dumps({"pkp_id": frozen_pkp.pkp_id, "content_hash": frozen_pkp.content_hash}, indent=2), encoding="utf-8")

    validate_frozen_pkp(frozen_pkp.model_dump(), expected_episode_id=episode_id, expected_policy_snapshot_id=policy_snapshot.policy_snapshot_id)
    assert frozen_pkp.content_hash == frozen_pkp.compute_content_hash(), "PKP content hash mismatch"

    print(f"\n  → FROZEN PKP  : {pkp_path}")
    print(f"  → Freeze id   : {frozen_pkp.pkp_id}  hash={frozen_pkp.content_hash[:16]}...")
    return {
        "production": production,
        "pkp_id": frozen_pkp.pkp_id,
        "content_hash": frozen_pkp.content_hash,
        "run_root": str(run_root),
        "pkp_path": str(pkp_path),
        "brief_path": str(brief_path),
        "scenes": len(brief["scenes"]),
        "dialogue_lines": len(_all_lines),
        "shots": len(frozen_pkp.model_dump().get("shots", {}).get("shots", [])),
    }


# ---------------------------------------------------------------------------
# PROMETHEUS multishot (parameterized, dynamic shot selection)
# ---------------------------------------------------------------------------
def _probe_duration(path: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, timeout=10)
    try:
        return float(r.stdout.strip())
    except Exception:
        return 0.0


def _select_representative_shots(shots: list[dict], max_per_scene: int = 3) -> dict[int, list[str]]:
    """Dynamically select 2-3 representative shots per scene, maximizing
    composition/emotion/visibility difference. Prefers establishing, speaker
    coverage, listener reaction, two-shot, insert, emotional hold."""
    from collections import defaultdict
    by_scene = defaultdict(list)
    for s in shots:
        by_scene[s["scene_id"]].append(s)
    selection: dict[int, list[str]] = {}
    for scene_id in sorted(by_scene):
        scene_shots = by_scene[scene_id]
        # Prefer a diverse purpose set.
        purpose_order = ["ESTABLISHING", "SPEAKER_COVERAGE", "LISTENER_REACTION", "TWO_SHOT", "INSERT", "EMOTIONAL_HOLD"]
        picked: list[dict] = []
        for purpose in purpose_order:
            if len(picked) >= max_per_scene:
                break
            for s in scene_shots:
                if s.get("purpose") == purpose and s not in picked:
                    picked.append(s)
                    break
        # Fill remaining slots with the first shots not yet picked.
        for s in scene_shots:
            if len(picked) >= max_per_scene:
                break
            if s not in picked:
                picked.append(s)
        selection[scene_id] = [s["shot_id"] for s in picked[:max_per_scene]]
    return selection


def _build_shot_prompt(shot: dict, scene: dict) -> str:
    purpose = shot.get("purpose", "")
    framing = shot.get("framing", {}).get("type", "")
    subject = shot.get("visual_subject", {}).get("primary", "")
    action = shot.get("visual_action", "")
    emotional = shot.get("emotional_intent", "")
    composition = shot.get("composition", {}).get("relationship", "")

    parts = []
    if purpose == "ESTABLISHING":
        parts.append("wide establishing shot of the home interior, both characters small in frame, spatial context")
    elif purpose == "INSERT":
        parts.append("extreme close-up insert of a meaningful object on a table, shallow depth of field")
    elif purpose == "TWO_SHOT":
        parts.append("two-shot medium close-up of MARK and SARAH facing each other, natural dialogue exchange")
    elif purpose == "LISTENER_REACTION":
        parts.append(f"reaction close-up of {subject or 'the listener'}, isolated, processing emotion")
    elif purpose == "EMOTIONAL_HOLD":
        parts.append(f"emotional hold close-up of {subject or 'the character'}, lingering, after-effect")
    else:  # SPEAKER_COVERAGE
        parts.append(f"over-the-shoulder two-shot, {subject or 'the speaker'} delivering a line")

    if framing:
        parts.append(f"{framing.lower()} framing")
    if composition:
        parts.append(composition)
    if action:
        parts.append(action)
    if emotional:
        parts.append(f"emotional intent: {emotional}")
    parts.append(STYLE)
    parts.append(QUALITY)
    parts.append(ANCHORS)
    parts.append("cinematic, photorealistic, high quality, natural color grade, bright vivid colors, high-definition, sharp detail")
    return ", ".join(p for p in parts if p)


async def generate_shot_images(shots_by_id: dict, scenes: dict, selection: dict, img_dir: Path, run_id: str) -> dict[str, Path]:
    from movie_os.capabilities.base import ImageIntent
    from movie_os.providers.image.flux_comfyui import FluxComfyUIProvider
    # Port 8189 is the FLUX-capable ComfyUI (v0.33.1, ComfyUI-Installs) which
    # exposes UNETLoader/VAELoader/DualCLIPLoader and sees the FLUX models.
    # Port 8188 (Comfy Desktop v0.24.0) lacks those loader nodes and returns
    # prompt_outputs_failed_validation on every FLUX render.
    provider = FluxComfyUIProvider(comfyui_url="http://127.0.0.1:8189", model="flux1-dev-fp8.safetensors")
    shot_images: dict[str, Path] = {}
    for scene_id, shot_ids in selection.items():
        first_shot = shot_ids[0]
        existing = img_dir / f"scene_{scene_id:03d}.png"
        if existing.exists() and existing.stat().st_size > 10000:
            shot_images[first_shot] = existing
            logger.info(f"  [img] {first_shot} reuses existing scene_{scene_id:03d}.png")
        else:
            shot_images[first_shot] = existing
        for shot_id in shot_ids[1:]:
            shot = shots_by_id[shot_id]
            scene = scenes.get(scene_id, {})
            prompt = _build_shot_prompt(shot, scene)
            out_path = img_dir / f"shot_{shot_id}.png"
            if out_path.exists() and out_path.stat().st_size > 10000:
                shot_images[shot_id] = out_path
                logger.info(f"  [img] {shot_id} reuses existing {out_path.name}")
                continue
            intent = ImageIntent(
                prompt=prompt, negative_prompt=NEGATIVE, width=1024, height=576,
                quality="production", seed=2000 + scene_id * 10 + len(shot_ids),
                metadata={"scene_number": scene_id, "output_dir": str(img_dir), "pipeline_id": run_id},
            )
            try:
                asset = await provider.render(intent)
                p = Path(asset.path)
                if p != out_path:
                    shutil.copy2(p, out_path)
                shot_images[shot_id] = out_path
                logger.info(f"  [img] generated {shot_id} -> {out_path.name}")
            except Exception as e:
                logger.warning(f"  [img] {shot_id} generation failed: {e}")
                shot_images[shot_id] = existing
    return shot_images


def _render_shot_video(image: Path, audio: Path, duration_s: float, out_path: Path, motion: str) -> Path | None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists() and out_path.stat().st_size > 10000:
        return out_path
    dur = max(duration_s, 1.0)
    fps = 24
    frames = int(dur * fps)
    if motion == "zoom_in":
        z, x, y = f"1+0.08*on/{frames}", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif motion == "zoom_out":
        z, x, y = f"1.08-0.08*on/{frames}", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif motion == "pan_left":
        z, x, y = "1.15", f"(iw-iw/zoom)*(1-on/{frames})", "ih/2-(ih/zoom/2)"
    elif motion == "pan_right":
        z, x, y = "1.15", f"(iw-iw/zoom)*(on/{frames})", "ih/2-(ih/zoom/2)"
    elif motion == "pan_up":
        z, x, y = "1.15", "iw/2-(iw/zoom/2)", f"(ih-ih/zoom)*(1-on/{frames})"
    else:
        z, x, y = "1.15", "iw/2-(iw/zoom/2)", f"(ih-ih/zoom)*(on/{frames})"
    vf = (f"scale=1920:1080:force_original_aspect_ratio=decrease,"
          f"pad=1920:1080:(ow-iw)/2:(oh-ih)/2,"
          f"zoompan=z='{z}':x='{x}':y='{y}':d=1:s=1920x1080:fps={fps}")
    cmd = (f'ffmpeg -y -loop 1 -i "{image}" -i "{audio}" '
           f'-vf "{vf}" '
           f'-c:v libx264 -pix_fmt yuv420p -preset medium -crf 20 -r {fps} '
           f'-c:a aac -b:a 192k -ar 48000 '
           f'-map 0:v -map 1:a -t {duration_s} "{out_path}"')
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
    if not out_path.exists() or out_path.stat().st_size < 10000:
        logger.error(f"  [video] shot render failed: {r.stderr[-500:]}")
        return None
    return out_path


def _compute_scene_duration(voice_paths: list[Path], min_duration_s: float = 8.0, pause_s: float = 0.7, tail_s: float = 2.0) -> float:
    total = 0.0
    for p in voice_paths:
        if p and p.exists():
            total += _probe_duration(p) + pause_s
    if total <= 0:
        return min_duration_s
    return max(min_duration_s, total + tail_s)


def _mix_scene_audio(music: Path | None, voice_paths: list[Path], out_path: Path) -> Path | None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists() and out_path.stat().st_size > 1000:
        return out_path
    inputs, filters, idx = [], [], 0
    if music is not None and music.exists():
        inputs += ["-i", str(music)]
        filters.append(f"[{idx}:a]volume=-6dB,aresample=48000[m]")
        idx += 1
    cursor_ms = 0
    pause_ms = 700
    for vp in voice_paths:
        if not vp or not vp.exists():
            continue
        inputs += ["-i", str(vp)]
        filters.append(f"[{idx}:a]aformat=sample_rates=48000:channel_layouts=stereo,"
                       f"adelay={cursor_ms}|{cursor_ms},volume=2.2[v{idx}]")
        idx += 1
        cursor_ms += int((_probe_duration(vp) + pause_ms / 1000.0) * 1000)
    if idx == 0:
        return None
    if music is not None and music.exists():
        mix_inputs = "".join(f"[v{i}]" for i in range(1, idx))
        filters.append(f"{mix_inputs}amix=inputs={idx-1}:duration=first:dropout_transition=3[vout]")
        filters.append("[m][vout]amix=inputs=2:duration=first:dropout_transition=3[out]")
    else:
        mix_inputs = "".join(f"[v{i}]" for i in range(1, idx))
        filters.append(f"{mix_inputs}amix=inputs={idx-1}:duration=first:dropout_transition=3[out]")
    cmd = (["ffmpeg", "-y"] + inputs + ["-filter_complex", ";".join(filters), "-map", "[out]", "-c:a", "aac", "-b:a", "192k", str(out_path)])
    subprocess.run(cmd, capture_output=True, timeout=180)
    if not out_path.exists() or out_path.stat().st_size < 1000:
        return None
    norm_path = out_path.with_suffix(".norm.m4a")
    subprocess.run(f'ffmpeg -y -i "{out_path}" -af "loudnorm=I=-16:TP=-1.5:LRA=11" -c:a aac -b:a 192k "{norm_path}"',
                   shell=True, capture_output=True, text=True, timeout=120)
    if norm_path.exists() and norm_path.stat().st_size > 0:
        shutil.move(str(norm_path), str(out_path))
    return out_path if out_path.exists() else None


async def run_prometheus(genesis_result: dict, episode: dict) -> dict:
    episode_id = episode["episode_id"]
    run_root = Path(genesis_result["run_root"])
    pkp_path = Path(genesis_result["pkp_path"])
    img_dir = run_root / "images" / genesis_result["production"]["run_id"] / "scene_images"
    render_dir = run_root / "render"
    voice_dir = run_root / "voice"
    music_dir = run_root / "music"
    img_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 60)
    print(f"  PROMETHEUS — {episode_id} multishot")
    print("=" * 60)

    pkp = json.loads(pkp_path.read_text(encoding="utf-8"))
    shots = pkp["shots"]["shots"]
    shots_by_id = {s["shot_id"]: s for s in shots}
    sp = pkp.get("screenplay", {})
    scenes = {sc.get("scene_id"): sc for sc in sp.get("scenes", [])}

    selection = _select_representative_shots(shots)
    print(f"  PKP      : {pkp.get('pkp_id')}")
    print(f"  Shots    : {len(shots)} (selecting {sum(len(v) for v in selection.values())})")

    # 1. Generate per-shot images.
    print("\n[1/3] Generating per-shot images...")
    shot_images = await generate_shot_images(shots_by_id, scenes, selection, img_dir, genesis_result["production"]["run_id"])
    print(f"  shot images: {len(shot_images)}")

    # 2. Build multi-shot timeline.
    print("\n[2/3] Building multi-shot timeline...")
    voice_by_scene: dict[int, list[Path]] = {}
    for f in sorted(voice_dir.glob("scene_*.mp3")):
        try:
            sid = int(f.name.split("_")[1])
        except (ValueError, IndexError):
            continue
        voice_by_scene.setdefault(sid, []).append(f)
    music_by_scene: dict[int, Path] = {}
    for f in sorted(music_dir.glob("scene_*.mp3")):
        try:
            sid = int(f.name.split("_")[1])
        except (ValueError, IndexError):
            continue
        music_by_scene[sid] = f

    scene_videos: list[Path] = []
    for scene_id, shot_ids in selection.items():
        voice_paths = voice_by_scene.get(scene_id, [])
        if not voice_paths:
            logger.warning(f"  [timeline] scene {scene_id} has no voice clips")
            continue
        music = music_by_scene.get(scene_id)
        mixed = _mix_scene_audio(music, voice_paths, render_dir / f"scene_{scene_id:03d}_mixed.m4a")
        if not mixed:
            logger.warning(f"  [timeline] scene {scene_id} mix failed")
            continue
        scene_dur = _compute_scene_duration(voice_paths)
        n_shots = len(shot_ids)
        shot_dur = scene_dur / n_shots
        for shot_id in shot_ids:
            image = shot_images.get(shot_id)
            if not image or not image.exists():
                logger.warning(f"  [timeline] {shot_id} has no image, skipping")
                continue
            motion = MOTION_BY_PURPOSE.get(shots_by_id[shot_id].get("purpose", ""), "zoom_in")
            out_mp4 = render_dir / f"shot_{shot_id}.mp4"
            sv = _render_shot_video(image, mixed, shot_dur, out_mp4, motion)
            if sv:
                scene_videos.append(sv)
                logger.info(f"  [timeline] {shot_id} rendered ({shot_dur:.1f}s, {motion})")

    # 3. Concatenate into final MP4.
    print("\n[3/3] Assembling final MP4...")
    clean_title = "".join(c for c in episode["working_title"] if c.isalnum() or c in "_- ")[:40].strip(" -_")
    final_path = render_dir / f"{clean_title}_multishot.mp4"
    final_path.parent.mkdir(parents=True, exist_ok=True)
    if scene_videos:
        concat = render_dir / "concat_multishot.txt"
        concat.write_text("\n".join(f"file '{v.resolve()}'" for v in scene_videos))
        subprocess.run(f'ffmpeg -y -f concat -safe 0 -i "{concat}" -c copy "{final_path}"', shell=True, capture_output=True, timeout=120)
        if not final_path.exists() or final_path.stat().st_size < 10000:
            subprocess.run(f'ffmpeg -y -f concat -safe 0 -i "{concat}" -c:v libx264 -pix_fmt yuv420p -crf 20 -r 24 -c:a aac -b:a 192k "{final_path}"',
                           shell=True, capture_output=True, timeout=300)

    if final_path.exists() and final_path.stat().st_size > 10000:
        graded = final_path.with_suffix(".graded.mp4")
        subprocess.run(f'ffmpeg -y -i "{final_path}" -vf "eq=contrast=1.18:brightness=0.05:saturation=1.9,unsharp=5:5:0.8:5:5:0.0" '
                       f'-c:v libx264 -pix_fmt yuv420p -preset medium -crf 20 -c:a copy "{graded}"',
                       shell=True, capture_output=True, timeout=300)
        if graded.exists() and graded.stat().st_size > 10000:
            shutil.move(str(graded), str(final_path))

    ok = final_path.exists() and final_path.stat().st_size > 10000
    print(f"\n  FINAL: {final_path} ({final_path.stat().st_size//1024}KB) ok={ok}")
    print(f"  Visual assets: {len(shot_images)} | Scene videos: {len(scene_videos)}")
    return {"ok": ok, "path": str(final_path), "assets": len(shot_images), "videos": len(scene_videos)}


async def main():
    import sys as _sys
    # Episode concept comes from a JSON file (argv[1]) or defaults to EP-0002.
    concept_path = _sys.argv[1] if len(_sys.argv) > 1 else None
    if concept_path:
        episode = json.loads(Path(concept_path).read_text(encoding="utf-8"))
    else:
        episode = EPISODE
    print("=" * 60)
    print(f"  VIDEO-FIRST — {episode['episode_id']} repeatability run")
    print("=" * 60)
    print(f"  Title   : {episode['working_title']}")
    print(f"  Synopsis: {episode['synopsis'][:100]}...")

    # ── LOCAL-AI-RESOURCE-GOVERNOR-001: Phase A (GENESIS, local_llm) ──────────
    # Acquire a local_llm lease at the coherent GENESIS language-generation
    # boundary. Release only after the package is frozen.
    genesis_lease = request_lease(
        application="videogen-genesis",
        workload="genesis_language_generation",
        priority=80,
        context=131072,
        resource_class="local_llm",
    )
    if genesis_lease["status"] in ("queued", "rejected"):
        print(f"  ⛔ GOVERNOR: GENESIS deferred ({genesis_lease['status']}: {genesis_lease['reason']})")
        return {"status": genesis_lease["status"], "reason": genesis_lease["reason"]}
    print(f"  [gov] local_llm lease granted: {genesis_lease['lease_id']}")

    try:
        genesis_result = await run_genesis(episode)
    except BaseException:
        release_lease(genesis_lease["lease_id"])
        raise
    finally:
        # §D: LLM work is complete once the package is frozen -> release the
        # local_llm lease before PROMETHEUS. Do NOT hold it during rendering.
        release_lease(genesis_lease["lease_id"])
        print(f"  [gov] local_llm lease released: {genesis_lease['lease_id']}")

    # ── LOCAL-AI-RESOURCE-GOVERNOR-001: Phase B (PROMETHEUS, gpu_heavy) ───────
    # Acquire an EXCLUSIVE gpu_heavy lease before heavyweight ComfyUI rendering.
    # While held, no new heavyweight local-LLM job may start.
    prom_lease = take_comfyui_lease(
        application="videogen-prometheus", workload="heavy_render"
    )
    if prom_lease["status"] in ("queued", "rejected"):
        print(f"  ⛔ GOVERNOR: PROMETHEUS deferred ({prom_lease['status']}: {prom_lease.get('reason')})")
        logger.warning("PROMETHEUS could not obtain exclusive gpu_heavy lease; skipping render")
        return {"genesis": genesis_result, "prometheus": {"ok": False, "reason": "gpu_heavy_lease_unavailable"}}
    print(f"  [gov] gpu_heavy exclusive lease granted: {prom_lease['lease_id']}")

    try:
        prometheus_result = await run_prometheus(genesis_result, episode)
    finally:
        release_lease(prom_lease["lease_id"])
        print(f"  [gov] gpu_heavy exclusive lease released: {prom_lease['lease_id']}")

    print("\n" + "=" * 60)
    print(f"  {episode['episode_id']} COMPLETE")
    print("=" * 60)
    print(f"  GENESIS  : {genesis_result['pkp_id']} (frozen)")
    print(f"  PROMETHEUS: {prometheus_result['path']}")
    print(f"  Playable : {prometheus_result['ok']}")
    return {"genesis": genesis_result, "prometheus": prometheus_result}


if __name__ == "__main__":
    asyncio.run(main())
