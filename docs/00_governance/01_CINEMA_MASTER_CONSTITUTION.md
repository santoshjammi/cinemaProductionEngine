# Cinema Master Constitution

**Document ID:** CMC-001  
**Version:** 1.0  
**Status:** CONSTITUTIONAL  
**Scope:** Every video produced by videoGen

## Preamble

videoGen exists to create purposeful cinematic productions across multiple niches while allowing production technology to change without corrupting creative truth.

This constitution governs all niches, including Psychology, Kids Stories, Devotional Stories, History, and future categories.

A niche may add stricter rules. It may not weaken this constitution.

---

## Article 1 — Production is the primary object

The system creates a **Production**, not merely a video file.

A Production includes:

- intent;
- audience;
- story;
- canon;
- screenplay/dialogue;
- visual/performance design;
- executable production knowledge;
- generated assets;
- validations;
- distribution derivatives;
- provenance;
- learning.

A final MP4 is one output of a Production.

---

## Article 2 — Story before spectacle

Visual quality, music, voice quality, animation, camera movement, and generative novelty may enhance a strong production.

They may not compensate for:

- a weak premise;
- incoherent causality;
- repetitive dialogue;
- unearned emotion;
- inconsistent character behavior;
- a missing ending;
- a false audience promise.

Narrative quality must be judged before expensive rendering.

---

## Article 3 — Separation of constitutional and production layers

Constitutional and creative decisions change slowly.

Production technology changes frequently.

The following are replaceable implementation details:

- LLM provider;
- image model;
- TTS provider;
- lip-sync engine;
- image-to-video model;
- ComfyUI workflow;
- renderer;
- encoder;
- orchestration framework.

They may not become the source of creative truth.

---

## Article 4 — Pillar responsibilities

### GENESIS — know, decide, compile

GENESIS may:

- interpret an approved Episode Contract;
- design the causal story;
- write the screenplay;
- write the exact dialogue;
- define performance intent;
- define scene emotional states;
- define visual intent;
- define shot intent;
- define voice direction;
- define music/sound intent;
- compile the PKP.

GENESIS produces **no final production media**.

### PROMETHEUS — make

PROMETHEUS may:

- generate images;
- animate images;
- synthesize speech;
- create lip sync;
- generate/assemble music and SFX;
- mix audio;
- composite shots;
- render masters;
- create technical derivatives.

PROMETHEUS may not:

- rewrite dialogue;
- change story meaning;
- change character identity;
- invent a new psychological mechanism;
- alter the ending;
- change canonical continuity;
- silently substitute a materially different creative choice.

### ORACLE — judge

ORACLE validates:

- policy compliance;
- narrative coherence;
- dialogue quality;
- emotional continuity;
- character consistency;
- technical quality;
- production integrity;
- anti-slop standards;
- distribution truthfulness where applicable.

ORACLE returns decisions and evidence. It does not silently rewrite the work.

### ATLAS — remember

ATLAS persists:

- constitutions and versions;
- canon;
- ontology versions;
- Episode Contracts;
- Effective Policy Snapshots;
- PKPs;
- reference identities;
- voice identities;
- continuity state;
- run manifests;
- approved assets;
- ORACLE reports;
- distribution records;
- learnings.

---

## Article 5 — One creative authority per decision

Every decision type must have one owner.

Examples:

| Decision | Owner |
|---|---|
| Story premise | GENESIS |
| Exact spoken dialogue | GENESIS |
| Character canon | Series Constitution / ATLAS |
| Episode emotional state | GENESIS |
| Voice identity | Series Canon / ATLAS |
| TTS waveform | PROMETHEUS |
| Shot lip-sync execution | PROMETHEUS |
| Final validation | ORACLE |

Duplicate creative ownership is prohibited.

---

## Article 6 — Causal storytelling

Every meaningful story change must have a cause.

A scene must alter one or more of:

- knowledge;
- interpretation;
- emotion;
- relationship state;
- goal;
- decision;
- commitment;
- physical situation.

A scene that changes nothing requires explicit justification or removal.

---

## Article 7 — Performance is part of storytelling

Dialogue is not merely text attached to images.

Each important line must be understood as an action by a character.

A production may encode:

- surface intention;
- hidden need;
- subtext;
- emotional state;
- delivery;
- physical behavior;
- expected effect on the other character;
- next-story consequence.

---

## Article 8 — Continuity is state, not memory-by-hope

Recurring characters and worlds require explicit continuity records.

The system must not depend on an LLM “remembering” prior episodes.

Continuity includes:

- identity;
- relationship history;
- locations;
- family facts;
- voice;
- appearance;
- emotional consequences;
- unresolved promises;
- known events.

---

## Article 9 — Frozen handoff

PROMETHEUS may execute only an approved, versioned PKP.

The PKP freeze requires:

- Episode Contract approval;
- applicable policy resolution;
- screenplay approval;
- dialogue approval;
- continuity validation;
- production feasibility;
- required asset references.

After freeze, any creative change creates a new PKP version.

---

## Article 10 — Immutable production provenance

Every production run must record:

- PKP version;
- policy snapshot;
- provider/model versions;
- seeds where relevant;
- input asset hashes;
- voice IDs;
- generation settings;
- outputs;
- validation results.

A shared mutable output directory is not a release record.

---

## Article 11 — No false completion

The system must distinguish:

- file generated;
- technically valid;
- creatively valid;
- production approved;
- release approved.

A placeholder-based render cannot be called production-ready.

A valid MP4 cannot be called successful cinema merely because it plays.

---

## Article 12 — Human meaning over AI mannerism

The studio rejects output that feels mass-produced, emotionally generic, visually inconsistent, mechanically repetitive, or synthetically over-explained.

See `20_standards/ANTI_AI_SLOP_QUALITY_STANDARD.md`.

---

## Article 13 — Niche extensibility

Psychology-specific rules must never become universal cinema law.

Kids, Devotional, History, and future niches receive their own Sub-Constitutions.

The production engine should remain shared.

---

## Article 14 — Amendment

A constitutional change requires:

```yaml
change:
  document_id:
  from_version:
  proposed_version:
  reason:
  affected_niches:
  affected_series:
  affected_productions:
  migration_required:
  approved_by:
```

No prompt or agent may amend constitutional law implicitly.

---

## Constitutional test

A rule belongs in this constitution only if it should still make sense after replacing “Psychology” with an entirely different niche.
