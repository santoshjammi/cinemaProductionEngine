# Authority and Precedence

**Classification:** Governance  
**Status:** AUTHORITATIVE

## 1. Purpose

This document eliminates competing sources of truth.

No AI model, agent, application component, script, prompt, provider, or generated artifact may invent its own authority order.

## 2. Authority hierarchy

### Tier 1 — Universal constitutional law
`01_CINEMA_MASTER_CONSTITUTION.md`

Applies to every video niche and production type.

### Tier 2 — Niche constitutional law
Example: `10_psychology/00_PSYCHOLOGY_SUB_CONSTITUTION.md`

Applies only when the selected niche/domain matches.

### Tier 3 — Series constitutional law
Example: `10_psychology/10_mark_sarah/00_MARK_SARAH_SERIES_CONSTITUTION.md`

Defines recurring-universe invariants.

### Tier 4 — Approved production intent
The approved `EPISODE_CONTRACT`.

It may specialize lower-level choices but may not contradict Tiers 1–3.

### Tier 5 — Production standards
Dialogue, continuity, voice, visual, lip-sync, shot-language, multi-part, and anti-slop standards.

### Tier 6 — Resolved policy
The `EFFECTIVE_POLICY_SNAPSHOT`.

This is a deterministic compilation of applicable rules, versions, IDs, exceptions, and unresolved blocking issues.

### Tier 7 — Frozen executable knowledge
The PKP.

GENESIS freezes this. PROMETHEUS executes it.

### Tier 8 — Provider/runtime configuration
Model IDs, ComfyUI workflows, TTS engines, image-to-video engines, encoders, FFmpeg options, retry rules, hardware constraints.

### Tier 9 — Generated media
Images, audio, video, subtitles, thumbnails, renders.

Generated media never becomes law merely because it exists.

---

## 3. Cross-cutting commercial law

`02_COMMERCIAL_DISTRIBUTION_CONSTITUTION.md` applies to packaging, reuse, publishing, and monetization.

It can demand stronger hooks, better retention structure, or additional derivative assets.

It cannot:

- falsify the story;
- introduce a prohibited theme;
- change the psychological mechanism;
- invent scandal;
- change character canon;
- require misleading titles/thumbnails;
- override a niche safety boundary.

---

## 4. Conflict rule

If two artifacts conflict:

1. identify both artifact IDs and versions;
2. apply the higher authority;
3. mark the lower artifact stale;
4. do not silently merge incompatible instructions;
5. record a change request if the lower rule is desired.

---

## 5. No reverse authority

The following are prohibited:

- changing canon because a model generated a prettier face;
- changing dialogue because TTS pronounces a sentence poorly;
- changing a story because lip-sync is difficult;
- changing a constitution because one episode performs well;
- adopting a legacy rule because it is mentioned in `unimportant_docs`;
- allowing ORACLE to rewrite creative content while validating it.

Validation may request revision. It may not silently perform the revision.

---

## 6. Example

Suppose the Episode Contract says:

> Mark and Sarah separate permanently at the end.

The Mark & Sarah Series Constitution says:

> Their marriage is protected from permanent separation.

Result:

```yaml
status: BLOCKED
reason: SERIES_CONSTITUTION_CONFLICT
required_action: revise_episode_contract
```

The application must block PKP freeze.

---

## 7. Legacy authority

`/Users/santosh/Desktop/projects/videoGen/unimportant_docs`

has:

```yaml
authority: NONE
use: historical_research_only
automatic_ingestion: prohibited
```

See `90_migration/LEGACY_RE_ADOPTION_PROTOCOL.md`.
