# 011 — ORACLE Validation Architecture

**Status:** Architectural Specification — Phase II
**Version:** 1.0.0
**Date:** 2026-07-21
**Derives Authority From:** `006` (Constitution, Tier 0); `001` §2.1 (ORACLE pillar definition, Tier 2); `007` (CIR, validated by ORACLE for provenance and explainability, Tier 2); `009` (PKP, validated by ORACLE for structural and creative compliance, Tier 2); `010` (PROMETHEUS, whose output ORACLE validates, Tier 2); `002` Part 11 (Creative Metrics, which ORACLE measures, Tier 2); `004` Part 5 (Semantic Invariants, which ORACLE enforces, Tier 2).
**Precedence:** Below the Constitution. This specification is the full architectural realization of the ORACLE pillar introduced in `001` §2.1 and constitutionalized by `006` (L-16, L-17, and Part 9 compliance).
**Scope:** ORACLE's philosophy, validation layers, constitution validation, semantic validation, creative validation, runtime validation, compliance, metrics, certification, audit, risk, violation reporting, and governance.

---

## Table of Contents

1. [Validation Philosophy](#1-validation-philosophy)
2. [Validation Layers](#2-validation-layers)
3. [Constitution Validation](#3-constitution-validation)
4. [Semantic Validation](#4-semantic-validation)
5. [Creative Validation](#5-creative-validation)
6. [Runtime Validation](#6-runtime-validation)
7. [Compliance](#7-compliance)
8. [Metrics](#8-metrics)
9. [Certification](#9-certification)
10. [Audit](#10-audit)
11. [Risk](#11-risk)
12. [Violation Reporting](#12-violation-reporting)
13. [Governance](#13-governance)

---

# 1. Validation Philosophy

## 1.1 Validation Is Independent

ORACLE is the ACI Platform's **independent validation authority**. It is independent in three respects:

1. **Independent from creation.** ORACLE did not author the CIS, the CIR, or the PKP, and did not render the media. It has no stake in the output being "good"; its only stake is the output being **faithful to intent and decisions**.
2. **Independent from execution.** ORACLE did not render the media and does not alter it. It reads the media and compares it to the specifications.
3. **Independent from creative judgment.** ORACLE does not assess whether the work is "creative" by its own taste; it assesses whether the work matches the creative decisions the Board made and the creative intent the human expressed (`006` L-17).

This independence is the architectural realization of the separation of validation from creation and execution (`00` §3.3, `006` Part 4). Without it, validation would be self-assessment — the executor or the Board judging its own work — and the platform's quality assurance would be unaccountable.

## 1.2 Validation Never Mutates

ORACLE is constitutionally prohibited from mutating any artifact (`006` L-16). It may not:

- Modify the CIS, the CIR, or the PKP.
- Modify the media.
- Modify the compilation or execution reports.

ORACLE **writes only validation reports**. A validation report is a Creative Artifact (`004` §2.3.53) of type `validation_report`, persisted in ATLAS (`012`), referencing the artifacts it validates by identity. The report is advisory: it describes what is correct, what is drift, and what is violation; it does not fix anything.

This is the architectural enforcement of the principle that validation is advisory, not authoritative (`001` §2.1, `006` Part 4.3). The human and the Board decide what to do with a validation report; ORACLE does not decide for them.

## 1.3 Validation Is Against Intent and Decisions

ORACLE validates against the **CIS** (intent), the **CIR** (decisions), and the **PKP** (executable specification) — not against its own creative judgment (`006` L-17). This means:

- ORACLE does not assess "is this a good film?" by its own taste.
- ORACLE assesses "does this media match the creative decisions in the CIR?" and "does this media fulfill the creative intent in the CIS?"
- If ORACLE's taste differs from the Board's decisions, ORACLE's taste is irrelevant; the Board's decisions are the standard.

This is what makes the platform's validation principled rather than opinionated: the standard is the human's intent and the Board's decisions, not the validator's preferences.

## 1.4 Constitutional Derivation

| Law | How it governs ORACLE |
|-----|----------------------|
| L-16 (Validation Never Mutates Artifacts) | ORACLE writes only validation reports. |
| L-17 (Validation Is Against Intent and Decisions) | ORACLE validates against CIS, CIR, PKP. |
| L-9 (Every Decision Has Provenance) | ORACLE audits provenance completeness. |
| L-10 (Every Decision Is Explainable) | ORACLE audits explainability. |
| L-12 (Compilation Never Invents Creativity) | ORACLE detects compile-time drift. |
| L-14 (Execution Never Changes Intent) | ORACLE detects render-time drift. |
| L-15 (Execution Never Invents Creativity) | ORACLE detects render-time invention. |

---

# 2. Validation Layers

## 2.1 The Layered Validation Model

ORACLE's validation is organized in five layers, each addressing a distinct concern:

| Layer | What it validates | Source of truth | Constitutional grounding |
|-------|------------------|-----------------|--------------------------|
| **Constitution Validation** | Constitutional law compliance across all artifacts. | The Constitution (`006`). | L-1..L-25. |
| **Semantic Validation** | COM invariants and graph integrity. | The COM (`004` Part 5). | L-4, L-5. |
| **Creative Validation** | Media vs. CIR decisions (drift detection) and CIS intent. | The CIR (`007`), the CIS (`003`). | L-9, L-10, L-12, L-14, L-15. |
| **Runtime Validation** | Media vs. PKP specifications (structural, visual, audio, continuity). | The PKP (`009`). | L-13, L-14. |
| **Compliance** | Constitutional certification of the production. | The Constitution (`006` Part 9). | L-22. |

## 2.2 Layer Ordering

The layers are ordered from most fundamental to most specific:

1. **Constitution Validation** (is the production constitutionally compliant?).
2. **Semantic Validation** (are the COM objects and graphs valid?).
3. **Creative Validation** (does the media match the creative decisions?).
4. **Runtime Validation** (does the media match the executable specifications?).
5. **Compliance** (is the production certified?).

A failure at a higher layer may invalidate lower-layer validation (e.g., a constitutional violation may make creative validation moot). The layers are not independent; they are cumulative.

## 2.3 Validation Inputs

ORACLE reads, from ATLAS (`012`):

- The pinned CIS (`003`) — for intent validation.
- The frozen CIR (`007`) — for decision validation and provenance audit.
- The frozen PKP (`009`) — for specification validation.
- The rendered media (from `010`) — for media validation.
- The compilation report (`008` Part 10.3) — for compile-time audit.
- The execution report (`010` Part 2.4) — for render-time audit.
- Prior validation reports (for trend analysis and learning).

ORACLE writes, to ATLAS:

- Validation reports (one per validation pass, referencing the validated artifacts by identity).

---

# 3. Constitution Validation

## 3.1 What Constitution Validation Checks

Constitution Validation verifies that the production's artifacts comply with the constitutional laws (`006` Part 3):

| Law | What ORACLE checks | How |
|-----|-------------------|-----|
| L-1 (Intent Precedes Cognition) | The CIR Root references a pinned CIS. | `lookup(cir-root).cis_version` is pinned. |
| L-2 (Intent Is Human-Authored) | No CIR node's provenance shows engine-authored intent. | Audit CIR provenance for `authored_by: engine` in CIS domains. |
| L-6 (Cognition Precedes Decision) | Every CIR node references faculty enrichments. | Audit CIR provenance for `faculty_enrichments` completeness. |
| L-8 (Decision Authority Is Defined) | Every CIR node names a home director. | Audit CIR nodes for `home_director`. |
| L-9 (Every Decision Has Provenance) | Every CIR node is provenance-complete (`007` Part 5.2). | Provenance completeness check. |
| L-10 (Every Decision Is Explainable) | The `explain` query returns a valid answer for every CIR node. | Explainability audit. |
| L-11 (Decision Precedes Compilation) | Every PKP artifact carries `cir_origin` referencing a frozen CIR node. | `cir_origin` audit on PKP artifacts. |
| L-12 (Compilation Never Invents Creativity) | No PKP artifact has content not traceable to a CIR node. | Compile-time drift detection (Part 5.3). |
| L-13 (Production Knowledge Is Compiled) | The PKP hash matches the compiler's recorded hash. | Hash verification. |
| L-14 (Execution Never Changes Intent) | No media has content not traceable to a PKP artifact. | Render-time drift detection (Part 5.4). |
| L-15 (Execution Never Invents Creativity) | (Same as L-14; render-time invention is drift.) | Render-time drift detection. |
| L-19 (History Is Immutable) | No frozen artifact has been mutated. | Version integrity audit. |

## 3.2 Constitutional Violation Classification

Constitutional violations are classified per `006` Part 9.4:

| Severity | Definition | ORACLE's action |
|----------|-----------|-----------------|
| **Critical** | A violation of an inviolable law (L-25, L-19). | The production is not certifiable; the violation is reported to the human and the Board. |
| **Major** | A violation of a non-inviolable law that compromises invariants. | The production is not certifiable until remediated; the violation is reported. |
| **Minor** | A violation that does not compromise invariants but violates process. | The violation is recorded; the production is certifiable with a note. |

---

# 4. Semantic Validation

## 4.1 COM Invariant Enforcement

Semantic Validation verifies that all COM objects (in the CIR and the PKP) satisfy the COM's semantic invariants (`004` Part 5):

| Invariant | What ORACLE checks |
|-----------|-------------------|
| I-SI-1 (Every Scene has a Purpose) | Every Scene object in the PKP has a `purpose` field. |
| I-SI-3 (Every Character has a Motivation) | Every Character object has a Goal or Need. |
| I-SI-5 (Every Payoff references a prior Setup) | Every Payoff object's `references` edge points to a Setup that `precedes` it. |
| I-SI-7 (Every Emotion Transition has a source and target) | Every Emotion Transition object has both. |
| I-SI-8 (Every Dialogue has a speaker) | Every Dialogue object has a `speaker` field. |
| I-SI-9 (Every Shot belongs to exactly one Scene) | Every Shot object's `belongs_to` edge points to exactly one Scene. |
| I-SI-14 (Every Creative Decision has provenance) | Every CIR node has provenance. |
| I-SI-15 (depends_on is acyclic) | The CIR's and PKP's dependency graphs are acyclic. |
| I-SI-21 (Every Creative Artifact carries cir_origin) | Every PKP artifact has `cir_origin`. |
| ... (all 40 invariants from `004` Part 5) | ... |

## 4.2 Graph Integrity

Semantic Validation also verifies graph integrity:

- **Identity integrity**: every object's identity is unique and well-formed.
- **Reference integrity**: every `references`, `depends_on`, `belongs_to`, `authorizes` edge points to an existing object.
- **Version integrity**: every version's `amends` edge points to a prior version; no version is mutated.
- **Provenance integrity**: every provenance chain is complete and traversable.

---

# 5. Creative Validation

## 5.1 Media vs. CIR Decisions (Drift Detection)

Creative Validation's primary function is **drift detection**: verifying that the rendered media matches the creative decisions in the CIR. Drift is detected by:

1. For each PKP artifact, ORACLE traverses `cir_origin` to the authorizing CIR node.
2. ORACLE reads the CIR node's decision (the selected alternative).
3. ORACLE compares the media rendered from the PKP artifact to the CIR node's decision.
4. If the media diverges from the decision beyond a tolerance, ORACLE flags a drift.

Drift is classified:

| Drift type | Cause | Severity |
|------------|-------|----------|
| **Compile-time drift** | The compiler produced a PKP artifact with content not in the CIR (L-12 violation). | Major. |
| **Render-time drift** | PROMETHEUS produced media with content not in the PKP (L-14/L-15 violation). | Major. |
| **Tolerance drift** | The media is within the tolerance but deviates slightly (e.g., a character's expression is sadder than the CIR specified). | Minor (recorded; not blocking). |

## 5.2 Media vs. CIS Intent

Creative Validation also verifies that the media fulfills the CIS's intent:

- **Emotional journey**: does the rendered video's emotional trajectory match the CIS's Emotional Journey (D-4) and Emotion Transition Graph (D-5)?
- **Ending intent**: does the ending match the CIS's Ending Intent (D-20)?
- **Theme and message**: does the work convey the CIS's Theme (D-2) and Message (D-3)?
- **Audience**: is the work receivable by the CIS's Audience (D-6)?

These checks are subjective-proxy checks: ORACLE uses models (e.g., emotion detection, theme classification) to estimate whether the media conveys the intended meaning. The estimates are recorded with confidence; low-confidence estimates are flagged for human review.

## 5.3 The Drift Report

A drift report is a validation report artifact containing:

| Field | Definition |
|-------|-----------|
| `pkp_artifact` | The PKP artifact that drift was detected on. |
| `cir_origin` | The CIR node that authorized the artifact (traversed for the decision). |
| `cis_source` | The CIS domain that the CIR node reasons from (traversed for the intent). |
| `drift_type` | `compile_time / render_time / tolerance`. |
| `drift_description` | What the divergence is. |
| `severity` | `critical / major / minor`. |
| `recommendation` | ORACLE's recommendation (e.g., "re-enter CIR at node X for revision"). |

The drift report is persisted in ATLAS. The Board reads drift reports and re-enters the CIR at the named nodes for surgical revision (`007` Part 10.5). The human may override a drift report (accept the drift), but the override is recorded and does not alter the report (L-16).

---

# 6. Runtime Validation

## 6.1 Structural Validation

Runtime Validation verifies that the media matches the PKP structurally:

| Check | What it verifies |
|-------|-----------------|
| Scene count | The media contains the number of scenes the PKP specifies. |
| Durations | Each scene's duration matches the PKP's Timeline artifact. |
| Total runtime | The total runtime is within the production profile's envelope. |
| Character presence | All characters specified in the PKP appear in the media. |
| Audio tracks | All audio tracks (voice, music, SFX) are present and synchronized. |

## 6.2 Visual Consistency

Visual consistency validation verifies that characters look the same across scenes (CLIP-based verification, extended from the existing `backend/app/services/image_verifier.py` per `001` §2.1):

- For each character, ORACLE compares the character's appearance across all scenes.
- A consistency score below threshold is flagged as drift.

## 6.3 Continuity Enforcement

Continuity validation verifies cross-scene consistency:

| Check | What it verifies |
|-------|-----------------|
| Wardrobe continuity | A character's wardrobe is consistent across scenes (unless the PKP specifies a change). |
| Prop continuity | Props are consistent across scenes. |
| Lighting continuity | Lighting is consistent across scenes within a sequence (unless the PKP specifies a change). |
| Blocking continuity | Character blocking is consistent across cuts within a scene. |
| Time-of-day continuity | Time of day is consistent across scenes within a sequence. |

## 6.4 Audio Quality

Audio quality validation verifies:

- Voice synthesis quality (clarity, emotional prosody matching the Voice artifacts).
- Music quality (matching the Music artifacts' intent).
- Mix quality (voice is audible over music; SFX are balanced).
- Silence is present where the PKP specifies silence (I-SI-19).

---

# 7. Compliance

## 7.1 Constitutional Compliance Certification

ORACLE performs constitutional compliance certification per `006` Part 9.3. A production is **constitutionally certified** when:

| Criterion | How ORACLE verifies |
|-----------|---------------------|
| The CIS was validated and approved (L-1). | The CIR Root references a pinned, approved CIS. |
| The CIR was frozen with full provenance (L-9). | Provenance completeness audit (Part 3). |
| The PKP was compiled from the frozen CIR (L-11). | `cir_origin` audit; CIR hash matches. |
| The media was rendered from the PKP without drift (L-14, L-15). | Drift detection (Part 5). |
| The validation report references CIR nodes and CIS domains (L-17). | Validation report self-audit. |
| All artifacts are archived in ATLAS with provenance (L-18). | ATLAS archive audit. |

Certification is issued as a validation report of type `certification`. A production without certification is not considered complete and may not be distributed.

## 7.2 Certification and the Human

The human may override a certification failure (accept a production that ORACLE did not certify). The override is recorded with the human's identity and rationale; the production is marked `certified_with_overrides`. The override does not alter ORACLE's report (L-16); it adds a human-decision record to the production's archive.

---

# 8. Metrics

## 8.1 The Creative Metrics

ORACLE measures the Creative Metrics defined in `002` Part 11:

| Metric | How ORACLE measures it |
|--------|----------------------|
| Emotional effectiveness | Detected emotion per scene (audio-visual model) compared to the CIR's emotional trajectory. |
| Narrative coherence | Scene-level summary (model) checked against the CIR's narrative purpose. |
| Character depth | Character consistency across scenes (CLIP-extended). |
| Psychological realism | Behavior plausibility (model) given the CIR's character bible. |
| Dialogue quality | Dialogue quality (model) plus silence detection. |
| Pacing | Pacing measured from the rendered cut compared to the CIR's pacing curve. |
| Symbolism | Detected metaphors (model) compared to the CIR's metaphor list. |
| Audience engagement | Retention prediction (model) per scene. |
| Replay value | (Pre-freeze metric; not measured post-render.) |
| Retention prediction | Per-scene retention model. |
| Continuity | ORACLE Continuity Enforcement (Part 6.3). |
| Cinematic realism | Cinematic coherence model. |
| Platform readiness | Platform-specific validation (duration, aspect, content policy). |

## 8.2 Metric Scoring

Each metric produces:

- A **per-scene score** (where applicable).
- A **production-level aggregate**.
- A **confidence level** in the score (model confidence).

Metric scores are recorded in the validation report. Scores below threshold are flagged for the Board's attention; they do not block certification unless they indicate drift (Part 5).

## 8.3 Metrics and the Constitution

The Creative Metrics are not constitutional laws; they are quality measurements. ORACLE measures them and reports them; the Board and the human decide whether the scores are acceptable. This preserves the principle that validation is advisory (L-16): ORACLE reports quality; it does not enforce taste.

---

# 9. Certification

(Covered in Part 7. Constitutional compliance certification is the certification model. No separate certification body exists; ORACLE is the certifier.)

---

# 10. Audit

## 10.1 Constitutional Auditing

ORACLE performs constitutional auditing per `006` Part 9.2. Audits are periodic reviews of the platform's artifacts and operations against the Constitution:

| Audit type | What it covers |
|------------|---------------|
| Artifact audit | Provenance completeness, immutability, `cir_origin` chain integrity. |
| Decision audit | Decision traceability to enrichments, override recording, alternative preservation. |
| Execution audit | PROMETHEUS's drift record, provider version recording. |
| Learning audit | Pattern-update governance, no retroactive re-reasoning. |

Audit results are recorded as validation reports of type `audit`. Audits do not block productions; they inform governance and the Constitutional Review Board (`006` Part 7.5).

## 10.2 Audit Frequency

Audits are performed:

- **Per production**: artifact and decision audits run as part of certification (Part 7).
- **Periodically**: platform-wide audits (execution, learning) run on a schedule governed by the Constitutional Review Board.
- **On demand**: the human or the Board may request an audit at any time.

---

# 11. Risk

## 11.1 Risk Classification

ORACLE classifies validation findings by risk:

| Risk level | Definition | Action |
|------------|-----------|--------|
| **Blocking** | The finding prevents certification (a major or critical violation). | The production is not certified until remediated. |
| **Warning** | The finding is a concern but does not prevent certification. | The finding is recorded; the Board may address it. |
| **Advisory** | The finding is informational (e.g., a low metric score within tolerance). | The finding is recorded; no action required. |

## 11.2 Risk and the Human

The human may accept a blocking finding (overriding ORACLE's recommendation). The override is recorded; the production is marked `certified_with_overrides`. The human's authority is supreme (`006` L-25); ORACLE's is advisory (L-16).

---

# 12. Violation Reporting

## 12.1 The Violation Report

A violation report is a validation report of type `violation`, containing:

| Field | Definition |
|-------|-----------|
| `law` | The constitutional law violated (e.g., L-12). |
| `severity` | `critical / major / minor`. |
| `artifact` | The artifact the violation was detected on. |
| `description` | What the violation is. |
| `evidence` | The evidence (e.g., a PKP artifact without `cir_origin`). |
| `recommendation` | ORACLE's recommended remediation. |

## 12.2 Remediation

Remediation follows `006` Part 9.5:

1. The offending action is suspended (for critical and major violations).
2. The violation is recorded.
3. The offending component is corrected.
4. Affected artifacts are re-validated.
5. The violation is reviewed by the Constitutional Review Board (`006` Part 7.5).

ORACLE reports violations; it does not remediate them (L-16). Remediation is performed by the component that caused the violation (the compiler for compile-time violations, PROMETHEUS for render-time violations, the Board for decision violations) and re-validated by ORACLE.

## 12.3 The Violation Loop

```
ORACLE detects violation
   │
   ▼
ORACLE writes violation report to ATLAS
   │
   ▼
Responsible component (Board / Compiler / PROMETHEUS) reads the report
   │
   ▼
Responsible component remediates (CIR amendment / PKP recompilation / media re-render)
   │
   ▼
ORACLE re-validates
   │
   ▼
Violation resolved OR escalated to the human
```

The loop is mediated by ATLAS; no direct calls between ORACLE and the responsible components (`001` §2.3).

---

# 13. Governance

## 13.1 ORACLE Evolution

ORACLE's architecture evolves under the Constitution:

| Change type | Authority |
|--------------|-----------|
| **New validation layer** | Architectural amendment to this specification. |
| **New metric** | Architectural amendment to this specification and to `002` Part 11. |
| **New audit type** | Architectural amendment to this specification. |
| **Certification criteria change** | Constitutional amendment (affects `006` Part 9.3). |

## 13.2 Compatibility

| Concern | Rule |
|---------|------|
| **Backward compatibility** | A new ORACLE version must be able to validate archived productions (producing the same validation results, given the same artifacts). |
| **Forward compatibility** | ORACLE leaves extension points (new layers, new metrics) for future validation needs. |
| **Cross-runtime compatibility** | ORACLE's architecture (layers, drift detection, certification, audit) is runtime-independent; the specific metrics and continuity checks are cinema-specific. A future runtime defines its own validation specifics using the architecture. |

## 13.3 Constitutional Compliance

| Law | Compliance |
|-----|------------|
| L-16 (Validation Never Mutates) | Part 1.2 (ORACLE writes only reports). |
| L-17 (Validation Against Intent and Decisions) | Part 1.3, Part 5. |
| L-9, L-10, L-12, L-14, L-15 | Part 3 (Constitution Validation). |
| L-22 (Constitutional Amendments Require Process) | Part 7 (certification enforces constitutional compliance). |

---

## Architectural Rules (Restated)

This specification produced no implementation code. It architecturalizes ORACLE as the independent validation authority, governed by L-16 (never mutates) and L-17 (validates against intent and decisions). ORACLE's five-layer validation model (constitution, semantic, creative, runtime, compliance) enforces the constitutional laws and the COM invariants, detects drift, certifies productions, and audits the platform — all without mutating any artifact.

---

## Cross-References

| Reference | Relevance |
|-----------|-----------|
| `006` (Constitution) | L-16, L-17, Part 9 (compliance) govern ORACLE. |
| `001` §2.1 | The ORACLE pillar definition; architecturalized here. |
| `007` (CIR) | Validated for provenance, explainability, drift. |
| `009` (PKP) | Validated for structural and creative compliance. |
| `010` (PROMETHEUS) | ORACLE validates PROMETHEUS's output. |
| `003` (CIS) | The intent ORACLE validates against. |
| `002` Part 11 | The Creative Metrics ORACLE measures. |
| `004` Part 5 | The Semantic Invariants ORACLE enforces. |
| `008` Part 10 | The compilation report ORACLE audits. |
| `010` Part 2.4 | The execution report ORACLE audits. |
| `012` (ATLAS) | The persistence layer ORACLE reads from and writes reports to. |

---

**End of Specification.**