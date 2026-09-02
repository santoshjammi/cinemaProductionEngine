from __future__ import annotations

import asyncio
import json

from movie_os.frozen_pkp import freeze_from_brief
from movie_os.genesis2 import Genesis2Engine, MockLLMClient
from movie_os.genesis2.bridge import Genesis2Bridge
from movie_os.prometheus.models import CertificationStatus, Director, ProductionCertificate
from movie_os.prometheus.mock_provider import MockFluxComfyUIProvider
from movie_os.prometheus.pipeline import PipelineConfig, PrometheusPipeline


def _fixture_responses() -> dict[str, str]:
    return {
        "Phase 06": json.dumps({
            "purpose": "scene plan", "creative_intent": "complete scene arc", "reasoning": "fixture", "confidence": "confirmed",
            "scenes": [
                {"scene_number": 1, "title": "The Silence", "purpose": "open fear", "conflict": "silence", "emotion": "fear", "visual_goal": "domestic tension", "audio_goal": "quiet room", "character_goal": "Mark hesitates", "transition": "to truth", "duration": "30", "narrative_beat": "hook"},
                {"scene_number": 2, "title": "The Pressure", "purpose": "turning point", "conflict": "job instability", "emotion": "vulnerability", "visual_goal": "closer framing", "audio_goal": "softening", "character_goal": "Sarah understands", "transition": "to repair", "duration": "45", "narrative_beat": "plot"},
                {"scene_number": 3, "title": "The Truth", "purpose": "repair", "conflict": "aftermath", "emotion": "hopeful", "visual_goal": "warm light", "audio_goal": "calm", "character_goal": "shared plan", "transition": "to resolution", "duration": "30", "narrative_beat": "climax"},
            ],
        }),
        "Phase 07": json.dumps({
            "purpose": "dialogue plan", "creative_intent": "real conversation", "reasoning": "fixture", "confidence": "confirmed",
            "dialogues": [
                {"scene_number": 1, "conversation_intent": "hide fear", "subtext": "Mark is scared", "emotional_state": "uneasy", "silence_opportunities": ["pause"], "dialogue_rhythm": "staccato", "speech_patterns": "short", "voice_direction": "restrained", "lines": [
                    {"speaker": "MARK", "text": "I have been quiet because I am scared.", "emotion": "fearful"},
                    {"speaker": "SARAH", "text": "Scared of what?", "emotion": "concerned"},
                    {"speaker": "MARK", "text": "Of disappointing you.", "emotion": "ashamed"},
                    {"speaker": "SARAH", "text": "Then tell me the truth.", "emotion": "steady"},
                    {"speaker": "MARK", "text": "The job situation got worse.", "emotion": "vulnerable"},
                    {"speaker": "SARAH", "text": "We will face it together.", "emotion": "warm"},
                ], "inner_voice": [{"speaker": "MARK_INNER", "text": "She will think less of me.", "emotion": "whisper"}]},
                {"scene_number": 2, "conversation_intent": "repair", "subtext": "They move forward together", "emotional_state": "hopeful", "silence_opportunities": [], "dialogue_rhythm": "gentle", "speech_patterns": "open", "voice_direction": "warm", "lines": [
                    {"speaker": "SARAH", "text": "We can adjust the budget tonight.", "emotion": "practical"},
                    {"speaker": "MARK", "text": "I should not have hidden it.", "emotion": "remorseful"},
                    {"speaker": "SARAH", "text": "Now we know what we are dealing with.", "emotion": "reassuring"},
                    {"speaker": "MARK", "text": "I feel lighter already.", "emotion": "relieved"},
                    {"speaker": "SARAH", "text": "That is what honesty does.", "emotion": "warm"},
                    {"speaker": "MARK", "text": "Thank you for staying with me.", "emotion": "grateful"},
                ], "inner_voice": []},
                {"scene_number": 3, "conversation_intent": "resolution", "subtext": "shared plan", "emotional_state": "hopeful", "silence_opportunities": [], "dialogue_rhythm": "gentle", "speech_patterns": "open", "voice_direction": "warm", "lines": [
                    {"speaker": "MARK", "text": "I can call the recruiter after dinner.", "emotion": "determined"},
                    {"speaker": "SARAH", "text": "And I will help you update the budget.", "emotion": "supportive"},
                    {"speaker": "MARK", "text": "I am glad I told you.", "emotion": "relieved"},
                    {"speaker": "SARAH", "text": "That was the right first step.", "emotion": "steady"},
                    {"speaker": "MARK", "text": "We are still us.", "emotion": "hopeful"},
                    {"speaker": "SARAH", "text": "Always.", "emotion": "warm"},
                ], "inner_voice": []},
            ],
        }),
        "Phase 12": json.dumps({
            "purpose": "integrate", "creative_intent": "package all", "reasoning": "fixture", "confidence": "confirmed",
            "package": {"summary": "complete"},
            "knowledge_graph": {"nodes": [{"id": "n1"}], "edges": []},
            "asset_registry": [{"asset_id": "a1"}],
            "dependencies": [{"from": "phase_06", "to": "phase_07"}],
            "cross_references": [{"source": "scene_1", "target": "dialogue_1"}],
            "version_history": [{"version": "1"}],
        }),
        "Phase 10": json.dumps({
            "purpose": "validate", "creative_intent": "check consistency", "reasoning": "fixture", "confidence": "confirmed",
            "issues": [], "passed": True, "score": 1.0,
        }),
    }


def test_deterministic_compiler_can_build_freeze_and_pass_prometheus():
    async def run():
        engine = Genesis2Engine(llm=MockLLMClient(responses=_fixture_responses()), max_revision_attempts=0)
        pkg = await engine.run_async("Mark is afraid of disappointing Sarah after unstable work news, so he withdraws instead of speaking.", {"runtime": "3-5 minutes", "mode": "QUALIFICATION_FIXTURE"})
        bridge = Genesis2Bridge(pkg)
        brief = bridge.to_brief()
        production = {"episode_id": "EP-0001", "run_id": "RUN-DET-001"}
        brief["production"] = production
        brief["policy_snapshot_id"] = "POLICY-DET-001"
        brief["dialogues"] = json.loads(_fixture_responses()["Phase 07"]) ["dialogues"]
        frozen = freeze_from_brief(
            episode_id="EP-0001",
            policy_snapshot_id="POLICY-DET-001",
            episode_contract_id="EP-0001",
            episode_contract_hash="contract-hash",
            policy_snapshot_hash="policy-hash",
            production=production,
            brief=brief,
        )
        cert = ProductionCertificate(certificate_id="cert-1", project_name=brief["title"], status=CertificationStatus.PRODUCTION_READY, reviewed_by=Director(name="Smoke"), blueprint={"episode_id": "EP-0001"})
        pipeline = PrometheusPipeline(config=PipelineConfig(output_dir="/tmp/videoGen-det", image_provider=MockFluxComfyUIProvider()))
        result = await pipeline.execute(cert, {**brief, "frozen_pkp": frozen.model_dump()})
        return pkg, brief, frozen, result

    pkg, brief, frozen, result = asyncio.run(run())
    assert all(r.status.value == "completed" for r in pkg.phase_results)
    assert len(brief.get("scenes", [])) == 3
    assert len(brief.get("dialogues", [])) == 3
    assert frozen.status == "FROZEN"
    assert result.overall_status.value == "completed"


def test_scene_plan_titles_survive_bridge():
    async def run():
        engine = Genesis2Engine(llm=MockLLMClient(responses=_fixture_responses()), max_revision_attempts=0)
        pkg = await engine.run_async("Mark is afraid of disappointing Sarah after unstable work news, so he withdraws instead of speaking.", {"runtime": "3-5 minutes", "mode": "QUALIFICATION_FIXTURE"})
        brief = Genesis2Bridge(pkg).to_brief()
        return [scene.get("title", "") for scene in brief.get("scenes", [])]

    titles = asyncio.run(run())
    assert all(isinstance(t, str) and t.strip() for t in titles)


def test_validation_boolean_is_explicit():
    from movie_os.genesis2.phases.phase10_validation import ValidationPhase
    from movie_os.genesis2.llm_client import MockLLMClient as _Mock

    phase = ValidationPhase(_Mock({"Phase 10": json.dumps({"issues": [], "passed": True, "score": 1.0, "reasoning": "ok", "purpose": "p", "creative_intent": "c", "confidence": "confirmed"})}))
    out = asyncio.run(phase.run({"phase_01": {}, "phase_02": {}, "phase_03": {}, "phase_04": {}, "phase_05": {}, "phase_06": {}, "phase_07": {}, "phase_08": {}, "phase_09": {}}))
    assert out.knowledge is not None
    assert getattr(out.knowledge, "passed", None) is True
