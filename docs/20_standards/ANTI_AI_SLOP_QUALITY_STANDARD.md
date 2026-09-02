# Anti-AI-Slop Quality Standard

**Document ID:** AAS-001  
**Version:** 1.0  
**Status:** BLOCKING QUALITY STANDARD

## Definition

For this studio, “AI slop” means output whose automation is more visible than its human intention.

Common symptoms:

- generic emotional writing;
- repetitive conversational rhythm;
- unstable character identity;
- static AI images under TTS;
- over-explained themes;
- unmotivated camera movement;
- synthetic performances;
- continuity drift;
- interchangeable characters;
- visually attractive but narratively irrelevant assets.

AI-generated does not automatically mean AI slop.

Uncontrolled generative inconsistency does.

---

## Gate 1 — Story

FAIL if:

- conflict does not causally escalate;
- the same realization is repeated;
- the ending happens because runtime ends;
- a multi-part story lacks a predefined destination;
- the “psychology” is a label rather than demonstrated behavior;
- the episode duplicates a prior story with superficial changes.

---

## Gate 2 — Dialogue

FAIL if:

- characters repeatedly speak like therapists or essayists;
- theme is stated instead of dramatized;
- multiple scenes repeat confession → reframe → acceptance;
- voices are interchangeable;
- dialogue does not create consequences;
- quotas produce unnatural exchanges.

---

## Gate 3 — Character

FAIL if:

- face changes enough to appear like another actor;
- apparent age/ethnicity shifts materially;
- voice identity changes;
- work/family canon changes;
- one spouse repeatedly functions as permanent moral authority;
- continuity is ignored without cause.

---

## Gate 4 — Emotional continuity

FAIL if:

- emotion jumps without cause;
- previous discoveries are forgotten;
- repair is unearned;
- a reaction contradicts the scene state;
- a later part resets the relationship.

---

## Gate 5 — Visual performance

FAIL if:

- a visible speaking close-up is functionally static;
- long conversations are mostly one still image plus zoom;
- reaction coverage is absent from major exchanges;
- generated frames look like unrelated stock/AI images;
- wardrobe/location continuity breaks without cause.

---

## Gate 6 — Motion / lip sync

FAIL if:

- readable speaker mouth does not plausibly match speech;
- lip-sync error is distracting;
- random motion changes emotional meaning;
- voiceover is introduced merely to hide failed animation.

---

## Gate 7 — Voice/audio

FAIL if:

- recurring voice identity changes;
- one character is materially less intelligible;
- TTS cadence is uniformly synthetic;
- score masks dialogue;
- every scene uses the same undifferentiated music bed.

---

## Gate 8 — Production integrity

FAIL if:

- placeholder assets remain;
- stale assets from another production are reused without provenance match;
- immutable run manifest is missing;
- PROMETHEUS makes creative choices absent from PKP;
- the final master cannot be traced back to approved inputs.

---

## Quality classifications

```yaml
quality:
  REJECTED:
    meaning: blocking failures present
  REWORK_REQUIRED:
    meaning: fixable major failures
  APPROVED_WITH_LIMITATIONS:
    meaning: no blocking issue; limitations documented
  APPROVED_MASTER:
    meaning: narrative, performance, continuity, production, and technical gates pass
```

---

## Vertical-slice bar

Before scaling the channel, one Psychology vertical slice must demonstrate:

- same Mark;
- same Sarah;
- same voices;
- true causal dialogue;
- scene-to-scene emotional continuity;
- cinematic coverage;
- correct visible-speaker lip sync;
- listener reactions;
- no static portrait dependency;
- immutable provenance;
- ORACLE approval.
