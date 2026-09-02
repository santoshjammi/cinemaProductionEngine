from __future__ import annotations

from movie_os.genesis2.performance_enrich import (
    enrich_line,
    enrich_dialogue_batches,
)


class FakeLLM:
    def __init__(self, responses=None, exc=None):
        self.responses = list(responses or [])
        self.exc = exc
        self.prompts = []
        self.calls = 0

    def generate(self, prompt: str, tier: str = "planner", **kwargs) -> str:
        self.prompts.append(prompt)
        self.calls += 1
        if self.exc is not None:
            raise self.exc
        if self.responses:
            return self.responses.pop(0)
        if "SC01-L001" in prompt or "SC01-L002" in prompt or "Required line ids" in prompt:
            return '{"scene_id": "1", "lines": [{"line_id": "SC01-L001", "subtext": "stay calm", "delivery_intent": "measured", "emotional_state_primary": "guarded"}, {"line_id": "SC01-L002", "subtext": "stay calm", "delivery_intent": "measured", "emotional_state_primary": "guarded"}]}'
        return '{"scene_id": "1", "lines": [{"line_id": "SC01-L001", "subtext": "stay calm", "delivery_intent": "measured", "emotional_state_primary": "guarded"}]}'



def _line(**overrides):
    base = {
        "line_id": "SC01-L001",
        "speaker": "MARK",
        "text": "I'm fine.",
        "emotional_state_primary": "guarded",
        "delivery_intent": "defensive",
        "subtext": "don't push",
        "character_voice_id": "MSVR-MARK",
        "presentation_mode": "EXTERNAL",
    }
    base.update(overrides)
    return base



def test_complete_record_skips_llm_calls():
    llm = FakeLLM()
    line = _line()
    out = enrich_line(line, {"scene": {"scene_number": 1}}, llm)
    assert out == line
    assert llm.calls == 0



def test_authoritative_line_only_enrichment_uses_missing_lines_only():
    llm = FakeLLM()
    batches = [
        {
            "scene_number": 1,
            "lines": [_line(), _line(line_id="SC01-L002", emotional_state_primary="")],
            "inner_voice": [_line(line_id="SC01-IV1")],
        }
    ]

    def build_context(batch):
        return {"scene": batch}

    updated, result = enrich_dialogue_batches(batches, build_context, llm)
    assert result["passed"] is True
    assert result["repaired_lines"] == 1
    assert llm.calls == 1
    assert updated[0]["lines"][0]["text"] == "I'm fine."
    assert updated[0]["inner_voice"] == [_line(line_id="SC01-IV1")]


def test_scene_batch_enrichment_uses_one_request_per_batch():
    llm = FakeLLM()
    batches = [
        {
            "scene_number": 1,
            "lines": [
                _line(line_id="SC01-L001", emotional_state_primary=""),
                _line(line_id="SC01-L002", emotional_state_primary=""),
            ],
            "inner_voice": [],
        }
    ]

    def build_context(batch):
        return {"scene": batch}

    updated, result = enrich_dialogue_batches(batches, build_context, llm)
    assert result["passed"] is True
    assert result["repaired_lines"] == 2
    assert llm.calls == 1
    assert len(llm.prompts) >= 1
    assert "Required line ids" in llm.prompts[0]
    assert updated[0]["lines"][0]["emotional_state_primary"] == "guarded"


def test_missing_line_id_blocks_reconciliation():
    llm = FakeLLM(responses=['{"scene_id":"1","lines":[{"line_id":"SC01-L999","subtext":"stay calm","delivery_intent":"measured","emotional_state_primary":"guarded"}]}'])
    batches = [{"scene_number": 1, "lines": [_line(line_id="SC01-L001", emotional_state_primary="")], "inner_voice": []}]

    def build_context(batch):
        return {"scene": batch}

    updated, result = enrich_dialogue_batches(batches, build_context, llm)
    assert result["passed"] is False
    assert result["blocker"]["code"] == "PERFORMANCE_ENRICHMENT_INCOMPLETE"
    assert result["aborted_remaining_batches"] is True



def test_bounded_retry_retries_once_then_returns_line():
    llm = FakeLLM(exc=RuntimeError("timeout"))
    line = _line(emotional_state_primary="")
    out = enrich_line(line, {"scene": {"scene_number": 1}}, llm)
    assert out == line
    assert llm.calls == 2



def test_abort_remaining_batches_on_final_failure():
    class PartiallyFailingLLM:
        def __init__(self):
            self.calls = 0

        def generate(self, prompt: str, tier: str = "planner", **kwargs) -> str:
            self.calls += 1
            if self.calls <= 2:
                raise RuntimeError("timeout")
            return '{"subtext": "stay calm", "delivery_intent": "measured", "emotional_state_primary": "guarded"}'

    llm = PartiallyFailingLLM()
    batches = [
        {"scene_number": 1, "lines": [_line(emotional_state_primary="")], "inner_voice": []},
        {"scene_number": 2, "lines": [_line(line_id="SC02-L001", emotional_state_primary="")], "inner_voice": []},
    ]

    def build_context(batch):
        return {"scene": batch}

    updated, result = enrich_dialogue_batches(batches, build_context, llm)
    assert result["passed"] is False
    assert result["blocker"]["code"] == "PERFORMANCE_ENRICHMENT_INCOMPLETE"
    assert result["aborted_remaining_batches"] is True
    assert result["processed_batches"] == 1
    assert len(updated) == 1
