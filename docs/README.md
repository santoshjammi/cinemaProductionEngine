# videoGen Authoritative Documentation

**Version:** 1.0  
**Status:** AUTHORITATIVE  
**Effective date:** 2026-08-10

This directory is the current source of truth for the `videoGen` application and its cinematic-production operating model.

The previous documentation tree has been renamed to:

`/Users/santosh/Desktop/projects/videoGen/unimportant_docs`

That directory is **legacy evidence only**. It has zero current authority unless a rule is explicitly re-adopted into this documentation tree through the re-adoption protocol in `90_migration/LEGACY_RE_ADOPTION_PROTOCOL.md`.

---

## 1. Why this reset exists

The earlier project accumulated several generations of architecture, prompts, agents, constitutions, PKP definitions, screenplay rules, and production assumptions. Many ideas were valuable, but authority overlapped.

The new system therefore separates:

1. **Constitutional law** — what must not drift.
2. **Niche law** — how a specific content domain must behave.
3. **Series canon** — what is true inside a recurring story universe.
4. **Ontology** — what content territory exists.
5. **Standards** — measurable craft and production requirements.
6. **Contracts** — what exact episode or production is being made.
7. **GENESIS** — creative reasoning and deterministic compilation.
8. **PROMETHEUS** — media execution only.
9. **ORACLE** — independent validation.
10. **ATLAS** — persistence, provenance, memory, and version history.
11. **Commercial distribution** — truthful packaging and derivative distribution.

---

## 2. Authority order

When two artifacts conflict, the higher item wins:

1. `00_governance/01_CINEMA_MASTER_CONSTITUTION.md`
2. Applicable niche constitution
3. Applicable series constitution
4. Approved Episode Contract
5. Applicable production standards
6. Effective Policy Snapshot
7. Frozen PKP
8. Provider configuration
9. Runtime implementation
10. Generated asset

The Commercial & Distribution Constitution is cross-cutting but may never override ethical, narrative, factual, niche, or series law.

---

## 3. Directory map

```text
docs/
├── README.md
├── 00_governance/
│   ├── 00_AUTHORITY_AND_PRECEDENCE.md
│   ├── 01_CINEMA_MASTER_CONSTITUTION.md
│   ├── 02_COMMERCIAL_DISTRIBUTION_CONSTITUTION.md
│   └── 03_DOCUMENT_CLASSIFICATION_STANDARD.md
├── 10_psychology/
│   ├── 00_PSYCHOLOGY_SUB_CONSTITUTION.md
│   ├── 01_RELATIONSHIP_PSYCHOLOGY_CONTENT_ONTOLOGY.yaml
│   ├── 02_RELATIONSHIP_PSYCHOLOGY_CONTENT_ONTOLOGY.md
│   ├── 10_mark_sarah/
│   │   ├── 00_MARK_SARAH_SERIES_CONSTITUTION.md
│   │   ├── 01_MARK_SARAH_CHARACTER_BIBLE_v2.yaml
│   │   ├── 02_MARK_SARAH_VOICE_REGISTRY.yaml
│   │   ├── 03_MARK_SARAH_VISUAL_IDENTITY_REGISTRY.yaml
│   │   └── 04_MARK_SARAH_CONTINUITY_REGISTRY.yaml
│   └── 20_coverage/
│       └── PSYCHOLOGY_CONTENT_COVERAGE_REGISTRY.yaml
├── 20_standards/
│   ├── DIALOGUE_AND_PERFORMANCE_STANDARD.md
│   ├── EMOTIONAL_CONTINUITY_STANDARD.md
│   ├── VISUAL_CHARACTER_CONTINUITY_STANDARD.md
│   ├── VOICE_AUDIO_STANDARD.md
│   ├── MOTION_AND_LIPSYNC_STANDARD.md
│   ├── CINEMATIC_SHOT_LANGUAGE_STANDARD.md
│   ├── MULTIPART_STORY_STANDARD.md
│   └── ANTI_AI_SLOP_QUALITY_STANDARD.md
├── 30_app/
│   ├── APP_PRODUCT_ARCHITECTURE.md
│   ├── DOMAIN_MODEL.md
│   ├── POLICY_RESOLUTION_AND_VERSIONING.md
│   ├── WORKFLOW_STATE_MACHINE.md
│   ├── UI_INFORMATION_ARCHITECTURE.md
│   ├── AI_AGENT_BOUNDARIES.md
│   └── DATA_AND_STORAGE_MODEL.md
├── 40_contracts/
│   ├── EFFECTIVE_POLICY_SNAPSHOT.schema.yaml
│   ├── EPISODE_CONTRACT.schema.yaml
│   ├── FORMAT_PROFILE.schema.yaml
│   ├── PKP.schema.yaml
│   ├── ORACLE_VALIDATION_REPORT.schema.yaml
│   └── IMMUTABLE_RUN_MANIFEST.schema.yaml
├── 50_execution/
│   ├── HERMES_OPERATING_DIRECTIVE.md
│   ├── GENESIS_EXECUTION_CONTRACT.md
│   ├── PROMETHEUS_EXECUTION_CONTRACT.md
│   └── ORACLE_EXECUTION_CONTRACT.md
└── 90_migration/
    ├── README.md
    ├── LEGACY_RE_ADOPTION_PROTOCOL.md
    └── VIDEOGEN_CONSISTENCY_AUDIT_AND_STANDARDIZATION_DIRECTION_v1.0.md
```

---

## 4. Core operating sentence

> **Constitutions define what may never drift. GENESIS decides and compiles what the production means. PROMETHEUS realizes only the frozen production package. ORACLE independently judges the result. ATLAS remembers every approved truth and immutable version.**

---

## 5. What Hermes must load

Hermes should **not** recursively ingest the full repository for every task.

For a Psychology / Mark & Sarah episode, resolve only:

- Cinema Master Constitution
- Commercial & Distribution Constitution where relevant
- Psychology Sub-Constitution
- Mark & Sarah Series Constitution
- selected RPCO nodes
- current continuity state
- applicable standards
- Episode Contract
- current Effective Policy Snapshot

PROMETHEUS should receive the frozen PKP and production configuration, not the entire constitutional corpus.

---

## 6. First production objective

Do not optimize the whole platform before proving one real vertical slice.

The initial production target is:

**Psychology → Relationship & Emotional Psychology → Emotional Withdrawal → Fear-Based Withdrawal → Mark & Sarah**

The slice must prove:

- stable Mark visual identity;
- stable Sarah visual identity;
- stable Mark voice;
- stable Sarah voice;
- natural causal dialogue;
- emotional-state continuity;
- cinematic reaction coverage;
- speaker lip-sync where the mouth is readable;
- no static-portrait conversation dependency;
- immutable PKP and run manifest;
- ORACLE anti-slop pass.

A technically valid MP4 is not enough.
