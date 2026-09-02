Genesis Pattern (GP)
GP-VAL-002 — Semantic Validation Pattern

Document ID: GP-VAL-002
Title: Semantic Validation Pattern
Version: 1.0.0
Status: Pattern
Authority: Derived from GFS-000, GFS-004, GO-001

1. Purpose

The Semantic Validation Pattern defines how Genesis verifies that a structurally valid PKG subgraph is also semantically coherent. Structural validation (GP-VAL-001) checks shape; semantic validation checks meaning. A subgraph may pass every SHACL shape and still be semantically incoherent — a character whose Core Fear contradicts their Goal, a scene whose stated emotion contradicts the dialogue, a world whose governing rule contradicts a character's transformation.

In Genesis, semantic validation is abductive or inductive (see GP-REAS-002 and GP-REAS-003). It applies learned coherence rules from the Reasoning Catalog and produces a Semantic Coherence Report. A semantic failure is a soft defect — it does not block merge by default but triggers a revision request with a stated confidence and a stated severity.

2. When to Apply

Apply this pattern when:

- A structurally valid subgraph must be checked for cross-node consistency (character fear vs. goal, scene emotion vs. dialogue).
- A learned rule from the Reasoning Catalog must be applied to a new production.
- A narrative coherence check must run before the screenplay is committed.
- A character's transformation arc must be checked for psychological plausibility.
- A world's rules must be checked against the events the narrative places inside it.

Do not apply this pattern before structural validation passes — semantic validation assumes structural validity. Do not apply it for completeness against the brief (use GP-VAL-003).

3. Validation Scope

Semantic validation checks:

- Cross-node consistency — pairs of nodes that the Reasoning Catalog declares as consistency pairs.
- Rule application — every Published Rule in the Reasoning Catalog that applies to the subgraph's concept types.
- Contradiction detection — pairs of facts that assert contradictory predicates about the same subject.
- Arc plausibility — character transformation arcs that the Psychology Reviewer must sanity-check.
- World-rule consistency — events placed in a world must not violate the world's declared rules.
- Emotional coherence — scene-level emotion must align with the beats and dialogue present.

Semantic validation does NOT check structural shape (use GP-VAL-001) or completeness against the brief (use GP-VAL-003).

4. Coherence Rules

A Coherence Rule is a registered rule in the Reasoning Catalog with:

- Rule ID — stable identifier.
- Applies to — concept type pair (e.g. Character ↔ Character, Scene ↔ Dialogue).
- Predicate — the consistency relation (e.g. must_not_contradict, must_align_with, must_support).
- Confidence — the rule's own confidence, inherited from its inductive origin.
- Severity — Info, Warning, or Error. Errors block merge; Warnings trigger revision but do not block; Info is logged only.
- Validation query — the PKG query that detects a violation.

Only Published Rules may be applied in default validation. Candidate Rules may be applied only with explicit Governance Agent approval and produce Info-level findings only.

5. Workflow

5.1 Load Applicable Rules

For each concept type present in the subgraph, load every Published Rule whose "applies to" field matches. If no rule applies, semantic validation is skipped for that subgraph — not failed.

5.2 Run Validation Queries

Execute each rule's validation query against the subgraph. Capture every violation with the rule ID, the violating nodes, and the violating predicate.

5.3 Classify Findings

Each finding is classified by the rule's severity:

- Error — merge is blocked. Revision Agent is dispatched.
- Warning — merge proceeds but a revision request is queued.
- Info — finding is logged; no action required.

5.4 Compute Coherence Score

The Semantic Coherence Score is the weighted fraction of rules that passed, weighted by rule confidence. The score is recorded in the Semantic Coherence Report. A subgraph with score below 0.6 triggers a Governance Agent review regardless of individual severities.

5.5 Emit Semantic Coherence Report

Commit the report to the PKG with: subject, rules evaluated, findings, severity counts, coherence score, and provenance.

5.6 Route Findings

Errors and Warnings are routed to the Revision Agent with the responsible agent named per the workflow manifest. The revision request carries the rule ID, the violating nodes, and the rule's expected behavior.

6. Use Inside Genesis

- Psychology Reviewer Agent — applies character coherence rules to the Character Subgraph.
- Story Coherence Validator — applies narrative coherence rules to the Narrative Subgraph.
- World Rule Validator — applies world-rule consistency rules to the World Subgraph.
- Screenplay Coherence Validator — applies scene-level coherence rules to the Screenplay Document.

7. Worked Example

The Character Subgraph for Arjuna contains:

- Core Fear: Loss of mentor.
- Goal: Avoid the war.
- Transformation: From hesitation to decisive action.

Applicable Published Rules:

- CR-014 (Character): Core Fear must not contradict Goal. Severity: Error.
- CR-022 (Character): Transformation must be plausible given Core Fear and Goal. Severity: Warning.

Validation:

- CR-014: "Loss of mentor" does not contradict "Avoid the war". PASS.
- CR-022: Transformation from hesitation to decisive action is plausible given fear of loss and goal of avoidance — the war forces the conflict. PASS.

Coherence Score: 1.0. No findings. Report committed; merge proceeds.

If the Goal had been "Embrace battle eagerly" while Core Fear was "Loss of mentor" and no in-world justification existed, CR-014 would FAIL with severity Error, blocking merge.

8. Anti-Patterns

- Applying Candidate Rules without governance approval.
- Treating Warnings as Errors — severity is rule-declared, not validator-chosen.
- Running semantic validation before structural validation passes.
- Auto-fixing semantic defects — the validator reports; the responsible agent revises.
- Using an LLM's "feeling" of coherence as a finding — every finding must reference a registered rule.
- Skipping the coherence score — even passing validation must record the score.

9. Exit Criteria

Semantic validation is complete when:

- Every applicable Published Rule has been evaluated.
- Every finding is classified by severity.
- The Semantic Coherence Report is committed.
- Errors have triggered Revision Agent dispatch.
- Warnings have queued revision requests.
- The coherence score is recorded.