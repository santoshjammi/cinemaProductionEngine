Genesis Pattern (GP)
GP-REAS-002 — Inductive Reasoning Pattern

Document ID: GP-REAS-002
Title: Inductive Reasoning Pattern
Version: 1.0.0
Status: Pattern
Authority: Derived from GFS-002 Reasoning Constitution, GO-001

1. Purpose

The Inductive Reasoning Pattern defines how Genesis agents generalize from specific observations to broader rules. Induction is the engine of pattern learning: it lets Genesis infer regularities across productions, across scenes within a production, and across character behaviors so that downstream agents can operate on rules instead of re-deriving them every time.

In Genesis, induction is never certain. Every inductive conclusion carries a confidence value derived from sample size, sample diversity, and absence of counter-examples. An inductive rule may be promoted to a Candidate Rule and, after enough validation, to a Published Rule in the Reasoning Catalog — but it never attains the certainty of a deductive rule.

2. When to Apply

Apply this pattern when:

- The Research Agent observes repeated patterns across reference productions and must formulate a domain rule (e.g. "Romantic dramas modulate tension every 90 seconds").
- The Character Manager Agent infers speech patterns from observed dialogue across scenes.
- The Story Architect Agent infers pacing regularities from prior productions in the same territory.
- The Psychology Reviewer Agent infers a behavioral pattern from a character's repeated choices.

Do not apply induction when certainty is required (use deduction) or when the goal is best-explanation (use abduction).

3. Structure of an Inductive Step

An inductive step is recorded as a five-tuple:

- Observations — a set of PKG instances or facts drawn from validated productions.
- Sample Size — the count of observations.
- Diversity — the spread across productions, territories, characters, or scenes.
- Proposed Rule — the generalized assertion.
- Confidence — a value in [0,1] computed from sample size, diversity, and absence of counter-examples.

Each inductive step is stored as a Decision Record tagged Inductive.

4. Confidence Model

Confidence is computed as:

confidence = base × size_factor × diversity_factor × (1 − counter_example_penalty)

Where:

- base is 0.5 — induction is never certain by default.
- size_factor grows logarithmically with sample size, capped at 1.0.
- diversity_factor is the fraction of distinct production contexts represented, capped at 1.0.
- counter_example_penalty subtracts weight per observed counter-example, scaled by the counter-example's confidence.

A Proposed Rule with confidence below 0.6 must not be referenced by downstream agents without explicit human governance approval. A Proposed Rule above 0.85 may be promoted to a Candidate Rule. A Candidate Rule that survives three independent validation runs is promoted to a Published Rule in the Reasoning Catalog.

5. Workflow

5.1 Gather Observations

The agent collects a candidate observation set from the PKG. Observations must be classified Explicit or Confirmed; Assumed and Unknown observations may not seed induction.

5.2 Compute Sample Metrics

Compute sample size and diversity. Refuse to emit a rule if sample size is below the threshold defined by the Reasoning Constitution (typically n ≥ 5).

5.3 Propose Rule

Formulate the candidate rule. The rule must use predicates from GO-002 and concepts from registered ontologies. A rule that uses unregistered vocabulary is invalid.

5.4 Search for Counter-Examples

Query the PKG and the Reasoning Catalog for any observation that contradicts the proposed rule. Each counter-example reduces confidence. If a single high-confidence counter-example exists, the rule is rejected.

5.5 Emit Decision Record

Store the proposed rule, observation set identifiers, sample metrics, counter-example report, and confidence. Tag the record Inductive.

5.6 Promote or Reject

If confidence ≥ 0.85, promote to Candidate Rule. If confidence < 0.6, reject. Between 0.6 and 0.85, hold the rule for additional observation; request clarification from the Research Agent.

6. Use Inside Genesis

- Research Agent — induces territory rules from external productions.
- Character Manager Agent — induces speech patterns from dialogue.
- Story Architect Agent — induces pacing rules from prior productions.
- Learning Agents — induct training patterns across many productions.

7. Worked Example

Observations (n = 12 productions in the "intimate romantic drama" territory):
- 11 of 12 productions place the irreversible moment between 60% and 70% of runtime.
- 1 production places it at 82% (counter-example, confidence 0.7).

Proposed Rule: In intimate romantic drama, the irreversible moment occurs between 60% and 70% of runtime.

Confidence:
- base = 0.5
- size_factor = 0.92 (12 samples)
- diversity_factor = 0.83 (10 distinct directors)
- counter_example_penalty = 0.05 (one counter-example at confidence 0.7)

confidence = 0.5 × 0.92 × 0.83 × (1 − 0.05) ≈ 0.36

The rule is held for additional observation; the Research Agent is dispatched to widen the sample.

8. Anti-Patterns

- Treating an inductive rule as a deductive certainty.
- Inducing from Assumed or Unknown observations.
- Inducing from a sample of one production.
- Skipping the counter-example search.
- Emitting a rule that uses predicates not in GO-002.
- Promoting a Candidate Rule without three independent validations.

9. Exit Criteria

An induction is complete when:

- Observations are identified, classified, and resolvable.
- Sample metrics are recorded.
- The proposed rule uses only registered vocabulary.
- Counter-examples are enumerated and their effect on confidence is recorded.
- The Decision Record is committed with the Inductive tag.
- The rule is promoted, held, or rejected with a stated reason.