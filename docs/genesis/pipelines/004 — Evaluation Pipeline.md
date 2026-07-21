Genesis Pipeline (GPIPE)
GPIPE-004 — Evaluation Pipeline

Document ID: GPIPE-004
Title: Evaluation Pipeline
Version: 1.0.0
Status: Pipeline
Authority: Derived from GFS-000, GFS-008, GWS-001

1. Purpose

The Evaluation Pipeline defines the canonical sequence by which Genesis assesses a Production Knowledge Package against seven quality dimensions before certifying it for downstream hand-off. Evaluation is the final gate: no package leaves Genesis without a complete Evaluation Report and a signed Production Readiness Certificate.

In Genesis, evaluation is constitutional. The Charter's Ninth Principle declares consistency overrides creativity, and the Tenth Principle declares production readiness is measurable. This pipeline operationalizes both: every dimension is measured, every finding is typed, every certificate is traceable to the evaluation that produced it.

2. Inputs

- Production Knowledge Package (from GPIPE-003).
- Registered ontologies, SHACL shapes, and Reasoning Catalog rules.
- Validation Patterns: GP-VAL-001 (Structural), GP-VAL-002 (Semantic), GP-VAL-003 (Completeness).
- Evaluation rubric per dimension (see §4).

3. Outputs

- Evaluation Report — per-dimension findings, scores, and overall verdict.
- Defect List — every detected defect with severity, responsible agent, and revision target.
- Production Readiness Certificate — issued only when all dimensions pass.
- Learning Corpus Entry — the evaluated production is added to the learning corpus for future induction.

4. Evaluation Dimensions

Genesis evaluates seven dimensions in parallel (GP-WF-002):

- Structural Integrity — every subgraph passes SHACL validation (GP-VAL-001).
- Semantic Coherence — every applicable coherence rule passes (GP-VAL-002).
- Completeness — every Required Element is present, evidence-class-compliant, and confidence-floor-compliant (GP-VAL-003).
- Narrative Integrity — the narrative's central conflict, irreversible moment, and resolution are mutually consistent and align with the Brief.
- Character Integrity — every character's motivations, fears, goals, and transformation are internally consistent and align with the narrative.
- World Integrity — every world rule is internally consistent and is not violated by any event in the narrative.
- Production Integrity — the Production Plan, Asset Specifications, and Prompt Library are internally consistent and complete relative to the Screenplay Document.

Each dimension is owned by a registered evaluator agent. Evaluators run independently against the same package snapshot; their findings merge into a single Evaluation Report.

5. Stages

5.1 Snapshot

The Production Orchestrator takes a read-only snapshot of the Production Knowledge Package. All evaluators consume the snapshot, never the live PKG.

5.2 Fan-Out Evaluation

The seven evaluators run in parallel. Each emits a Dimension Evaluation Report with: dimension, rubric items evaluated, findings (pass / warn / fail), score, and provenance.

5.3 Merge

The Production Orchestrator merges the seven Dimension Evaluation Reports into the consolidated Evaluation Report. Cross-dimension conflicts (e.g. Narrative Integrity pass but Character Integrity fail) are flagged for revision routing.

5.4 Defect Routing

Every Warn and Fail finding is routed to the responsible agent via the Revision Agent. The revision target is identified by walking the finding's provenance to the originating agent. Revisions are dispatched; the pipeline does not advance until all Fails are resolved. Warns may be accepted by governance with a decision record.

5.5 Re-Evaluation

After revisions complete, the affected dimensions re-evaluate against the updated snapshot. Re-evaluation is scoped to the revised subgraphs to control cost.

5.6 Certification

When all seven dimensions pass (or Warns are governance-accepted), the Governance Agent runs the Production Readiness approval chain (GP-GOV-001). On approval, the Production Readiness Certificate is issued and attached to the package.

5.7 Learning Capture

The Learning Agent ingests the evaluated production into the learning corpus. Every Decision Record, Validation Report, and Evaluation finding becomes training material for future inductive rule promotion (GP-REAS-002).

6. Exit Criteria

The Evaluation Pipeline is complete when:

- All seven Dimension Evaluation Reports are committed.
- The consolidated Evaluation Report is committed.
- Every Fail is resolved; every Warn is governance-accepted.
- The Production Readiness approval chain is complete.
- The Production Readiness Certificate is issued.
- The Learning Corpus Entry is committed.

7. Hand-off

The certified Production Knowledge Package is handed to downstream engines. The Evaluation Report and Certificate travel with the package as the authoritative evidence that the package is ready. Downstream engines may not consume an uncertified package.

8. Anti-Patterns

- Treating Warns as silent passes — they require governance acceptance.
- Running evaluators sequentially when they are independent — wastes throughput.
- Re-evaluating the entire package when only one subgraph changed — scope the re-evaluation.
- Issuing the certificate with unresolved Fails.
- Letting an evaluator fix defects — evaluators report; responsible agents revise.
- Skipping Learning Capture — future inductions depend on the corpus.
- Allowing downstream engines to consume the package before the certificate is issued.

9. Worked Example

Devotional drama package evaluation:

- Structural Integrity: PASS (all SHACL shapes satisfied).
- Semantic Coherence: PASS (coherence score 0.91).
- Completeness: PASS (all dimensions complete).
- Narrative Integrity: PASS (conflict, irreversible moment, resolution aligned).
- Character Integrity: WARN (protagonist's final choice has confidence 0.72, below 0.8 floor for transformation confidence). Governance accepts with a decision record citing the abductive reasoning trail.
- World Integrity: PASS (abbot's blessing node resolves the leaving-violation).
- Production Integrity: PASS (38 Shot Plans align with 12 Scene Plans; Prompt Library covers all specs).

Consolidated Evaluation Report: 6 Pass, 1 Warn (accepted). Certificate issued. Learning corpus entry committed. Package handed to Studio Engine.