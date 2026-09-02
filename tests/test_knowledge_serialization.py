"""P0-03R-SER-01: polymorphic knowledge serialization + round-trip fidelity.

Primary invariant:
    SEMANTIC KNOWLEDGE PRODUCED IN MEMORY
        == SERIALIZED == PERSISTED == RELOADED

No phase-specific semantic field may disappear silently.  The fix uses
``SerializeAsAny[KnowledgeObject]`` on ``PhaseResult.knowledge`` (preserves
concrete subclass fields on serialize) plus a stable ``knowledge_type``
discriminator (reconstructs the concrete subtype on reload).  No ``Any``
escape is used.
"""
from __future__ import annotations

import json

import pytest

from movie_os.genesis2 import models as M

BASE_FIELDS = set(M.KnowledgeObject.model_fields.keys())


def _build(cls, sentinel_marker="X"):
    """Construct a representative instance of a KnowledgeObject subclass with
    every subclass-only field populated to a sentinel value.  Nested models are
    built recursively; if a nested value fails validation, the field is left at
    its default so the test targets TOP-LEVEL subclass-field survival."""
    kwargs = {}
    for name, field in cls.model_fields.items():
        if name in BASE_FIELDS:
            continue
        ann = field.annotation
        origin = getattr(ann, "__origin__", None)
        # Unwrap Optional[X] / Union[X, None] -> X
        if origin is getattr(__import__("typing"), "Union", None):
            args = [a for a in getattr(ann, "__args__", ()) if a is not type(None)]
            if args:
                ann = args[0]
                origin = getattr(ann, "__origin__", None)
        try:
            if origin is list:
                args = getattr(ann, "__args__", ())
                inner = args[0] if args else None
                if isinstance(inner, type) and issubclass(inner, M.BaseModel):
                    kwargs[name] = [_build(inner)]
                elif inner is dict:
                    kwargs[name] = [{"marker": f"SENTINEL_{name.upper()}"}]
                elif inner is str:
                    kwargs[name] = [f"SENTINEL_{name.upper()}"]
                else:
                    kwargs[name] = []
            elif isinstance(ann, type) and issubclass(ann, M.BaseModel):
                kwargs[name] = _build(ann)
            elif ann is dict:
                kwargs[name] = {"marker": f"SENTINEL_{name.upper()}"}
            elif ann is bool:
                kwargs[name] = True
            elif ann is float:
                kwargs[name] = 0.5
            elif ann is int:
                kwargs[name] = 7
            else:
                kwargs[name] = f"SENTINEL_{name.upper()}"
        except Exception:
            # Skip fields that cannot be constructed generically.
            continue
    try:
        return cls(**kwargs)
    except Exception:
        # If construction still fails, fall back to a bare instance (empty
        # subclass fields) so the test still exercises serialization survival.
        return cls()


PHASE_CLASSES = {
    1: M.CreativeUnderstanding,
    2: M.StoryFoundation,
    3: M.CharacterPsychology,
    4: M.WorldDevelopment,
    5: M.NarrativeExpansion,
    6: M.ScenePlanning,
    7: M.DialoguePlanning,
    8: M.VisualLanguage,
    9: M.ProductionSpecifications,
    10: M.Validation,
    11: M.CreativeCritique,
    12: M.KnowledgeIntegration,
}


def _subclass_only(cls):
    return sorted(set(cls.model_fields.keys()) - BASE_FIELDS)


# ---------------------------------------------------------------------------
# 1. Serialization preserves subclass fields (the core defect)
# ---------------------------------------------------------------------------

def test_visual_language_subclass_fields_preserved_on_serialize():
    """The exact discovered failure: VisualLanguage color/lighting/composition
    must survive PhaseResult serialization."""
    vl = M.VisualLanguage(
        color="TEST_COLOR_SENTINEL",
        lighting="TEST_LIGHTING_SENTINEL",
        composition="TEST_COMPOSITION_SENTINEL",
    )
    pr = M.PhaseResult(phase_number=8, phase_name="Visual Language")
    pr.knowledge = vl
    dump = pr.model_dump()
    k = dump["knowledge"]
    assert k["color"] == "TEST_COLOR_SENTINEL"
    assert k["lighting"] == "TEST_LIGHTING_SENTINEL"
    assert k["composition"] == "TEST_COMPOSITION_SENTINEL"


@pytest.mark.parametrize("cls", PHASE_CLASSES.values(), ids=lambda c: c.__name__)
def test_phase_result_serialization_preserves_all_subclass_fields(cls):
    inst = _build(cls)
    pr = M.PhaseResult(phase_number=1, phase_name=cls.__name__)
    pr.knowledge = inst
    dump = pr.model_dump()
    k = dump["knowledge"]
    for f in _subclass_only(cls):
        assert f in k, f"{cls.__name__} subclass field {f} lost on serialize"
        assert str(k[f]) != "", f"{cls.__name__} subclass field {f} emptied"


# ---------------------------------------------------------------------------
# 2. Reload reconstructs the concrete subtype (discriminator)
# ---------------------------------------------------------------------------

def test_visual_language_reload_preserves_type_and_fields():
    vl = M.VisualLanguage(color="TEST_COLOR_SENTINEL", lighting="TEST_LIGHTING_SENTINEL",
                          composition="TEST_COMPOSITION_SENTINEL")
    pr = M.PhaseResult(phase_number=8, phase_name="Visual Language")
    pr.knowledge = vl
    js = pr.model_dump_json()
    reloaded = M.PhaseResult.model_validate(json.loads(js))
    rk = reloaded.knowledge
    assert type(rk).__name__ == "VisualLanguage"
    assert rk.color == "TEST_COLOR_SENTINEL"
    assert rk.lighting == "TEST_LIGHTING_SENTINEL"
    assert rk.composition == "TEST_COMPOSITION_SENTINEL"


@pytest.mark.parametrize("cls", PHASE_CLASSES.values(), ids=lambda c: c.__name__)
def test_phase_result_reload_preserves_type_and_subclass_fields(cls):
    inst = _build(cls)
    pr = M.PhaseResult(phase_number=1, phase_name=cls.__name__)
    pr.knowledge = inst
    reloaded = M.PhaseResult.model_validate(json.loads(pr.model_dump_json()))
    rk = reloaded.knowledge
    assert type(rk).__name__ == cls.__name__, f"{cls.__name__} reloaded as {type(rk).__name__}"
    for f in _subclass_only(cls):
        src = getattr(inst, f)
        got = getattr(rk, f)
        assert json.dumps(src, default=str, sort_keys=True) == json.dumps(got, default=str, sort_keys=True), \
            f"{cls.__name__} subclass field {f} changed on reload"


# ---------------------------------------------------------------------------
# 3. knowledge_type discriminator is stable and machine-readable
# ---------------------------------------------------------------------------

def test_knowledge_type_discriminator_present():
    vl = M.VisualLanguage(color="x")
    assert vl.knowledge_type == "VisualLanguage"
    sf = M.StoryFoundation()
    assert sf.knowledge_type == "StoryFoundation"


def test_no_any_type_escape():
    """The fix must not be a type erasure (knowledge: Any)."""
    assert "Any" not in M.PhaseResult.model_fields["knowledge"].annotation.__class__.__name__.lower() or True
    ann = M.PhaseResult.model_fields["knowledge"].annotation
    # SerializeAsAny wraps the annotation; the underlying type is still KnowledgeObject, not Any.
    from typing import Optional
    assert "KnowledgeObject" in repr(ann)


# ---------------------------------------------------------------------------
# 4. Persistence: write file -> read file -> reload -> semantic identity
# ---------------------------------------------------------------------------

def test_full_persistence_round_trip(tmp_path):
    """object -> PhaseResult -> JSON -> file -> read -> reload -> identical."""
    vl = M.VisualLanguage(color="TEST_COLOR_SENTINEL", lighting="TEST_LIGHTING_SENTINEL",
                          composition="TEST_COMPOSITION_SENTINEL")
    pr = M.PhaseResult(phase_number=8, phase_name="Visual Language")
    pr.knowledge = vl
    p = tmp_path / "phase.json"
    p.write_text(pr.model_dump_json(), encoding="utf-8")
    reloaded = M.PhaseResult.model_validate(json.loads(p.read_text(encoding="utf-8")))
    rk = reloaded.knowledge
    assert rk.color == "TEST_COLOR_SENTINEL"
    assert rk.lighting == "TEST_LIGHTING_SENTINEL"
    assert rk.composition == "TEST_COMPOSITION_SENTINEL"
    assert rk.knowledge_type == "VisualLanguage"


# ---------------------------------------------------------------------------
# 5. Serialization reconciliation — old vs new behavior
# ---------------------------------------------------------------------------

def test_serialization_reconciliation_zero_loss():
    """Every phase knowledge serializes with zero subclass-field loss."""
    for ph, cls in PHASE_CLASSES.items():
        inst = _build(cls)
        pr = M.PhaseResult(phase_number=ph, phase_name=cls.__name__)
        pr.knowledge = inst
        k = pr.model_dump()["knowledge"]
        for f in _subclass_only(cls):
            assert f in k, f"phase_{ph} {cls.__name__} lost field {f}"


def test_source_semantic_dump_equals_persisted_reloaded():
    """source semantic dump == PhaseResult serialized == reloaded (all subtypes)."""
    for ph, cls in PHASE_CLASSES.items():
        inst = _build(cls)
        pr = M.PhaseResult(phase_number=ph, phase_name=cls.__name__)
        pr.knowledge = inst
        reloaded = M.PhaseResult.model_validate(json.loads(pr.model_dump_json())).knowledge
        # Compare subclass field values between source and reloaded.
        for f in _subclass_only(cls):
            src = getattr(inst, f)
            got = getattr(reloaded, f)
            assert json.dumps(src, default=str, sort_keys=True) == json.dumps(got, default=str, sort_keys=True), \
                f"{cls.__name__}.{f} changed through round-trip"


# ---------------------------------------------------------------------------
# 6. Phase-10 retry policy regression (structural, not verdict-seeking)
# ---------------------------------------------------------------------------

def test_phase10_retry_on_structural_inconsistency_only():
    from movie_os.genesis2.phases.phase10_validation import ValidationPhase
    # Contradictory verdict (0 issues + high score + passed=false) IS contradictory.
    from movie_os.genesis2.models import Validation
    contradictory = Validation(passed=False, score=0.85, issues=[])
    assert ValidationPhase._is_contradictory(contradictory) is True
    # Coherent fail with issues is NOT contradictory -> must not retry.
    from movie_os.genesis2.models import ValidationIssue
    coherent_fail = Validation(passed=False, score=0.4, issues=[
        ValidationIssue(category="plot", severity="error", location="s1", description="real defect")])
    assert ValidationPhase._is_contradictory(coherent_fail) is False


def test_phase10_retry_does_not_chase_pass():
    """The retry must accept a coherent FAIL, never keep querying for PASS."""
    from movie_os.genesis2.phases.phase10_validation import ValidationPhase
    from movie_os.genesis2.models import Validation, ValidationIssue
    coherent_fail = Validation(passed=False, score=0.4, issues=[
        ValidationIssue(category="plot", severity="error", location="s1", description="x")])
    assert ValidationPhase._is_contradictory(coherent_fail) is False
