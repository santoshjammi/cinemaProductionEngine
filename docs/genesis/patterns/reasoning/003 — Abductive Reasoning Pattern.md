Genesis Pattern (GP)
GP-REAS-003 — Abductive Reasoning Pattern

Document ID: GP-REAS-003
Title: Abductive Reasoning Pattern
Version: 1.0.0
Status: Pattern
Authority: Derived from GFS-002 Reasoning Constitution, GO-001

1. Purpose

The Abductive Reasoning Pattern defines how Genesis agents infer the best explanation for a set of observations. Abduction is the reasoning mode of discovery: when the synopsis is incomplete, when the PKG contains gaps, and when an agent must choose between multiple candidate hypotheses, abduction is the only sound approach.

In Genesis, abduction never produces certainty. It produces the best currently available explanation, ranked against alternatives, with explicit confidence and explicit fallback if the chosen hypothesis is later invalidated. Abduction is the dominant reasoning mode for the Story Architect, Character Manager, Environment Manager, and Research Agents during discovery.

2. When to Apply

Apply this pattern when:

- The Production Brief contains a gap that must be filled (missing theme, missing motivation, missing world rule).
- Multiple plausible interpretations of a scene compete and the agent must choose one.
- The Research Agent must explain an observation by selecting between competing domain hypotheses.
- The Psychology Reviewer Agent must infer the psychological truth behind a character's behavior.

Do not apply abduction when the conclusion is rule-guaranteed (use deduction) or when the goal is a generalization across many observations (use induction).

3. Structure of an Abductive Step

An abductive step is recorded as a five-tuple:

- Observations — the facts that require explanation.
- Candidate Hypotheses — at least two competing explanations.
- Explanation Score — for each candidate, how well it accounts for the observations.
- Simplicity Penalty — for each candidate, the complexity cost of adopting it.
- Selected Hypothesis — the candidate with the best net score, plus the runner-up.

Every abductive step is stored as a Decision Record tagged Abductive.

4. Explanation Score

The explanation score is computed as:

score = coverage × coherence × (1 − simplicity_penalty)

Where:

- coverage — fraction of observations the hypothesis explains.
- coherence — alignment of the hypothesis with existing PKG facts and ontology constraints, in [0,1].
- simplicity_penalty — penalty in [0, 0.5] for the number of new concepts, relationships, or assumptions the hypothesis introduces. Parsimony matters: a hypothesis that requires fewer new assumptions is preferred.

A hypothesis that contradicts a constitutional invariant is automatically scored 0. A hypothesis that requires unregistered ontology vocabulary is automatically scored 0. A hypothesis that contradicts an Explicit PKG fact is automatically scored 0.

5. Workflow

5.1 Enumerate Observations

Collect the facts requiring explanation. Each observation must be classified Explicit or Confirmed. Assumed and Unknown observations may inform candidate generation but do not contribute to coverage.

5.2 Generate Candidate Hypotheses

Produce at least two distinct candidate explanations. The agent must not collapse to a single hypothesis without explicit governance approval; abduction requires an alternative.

5.3 Score Each Candidate

Compute coverage, coherence, and simplicity for each. Record the scoring in the Decision Record so it can be audited.

5.4 Select and Rank

Select the highest-scoring candidate. Tag it as the Selected Hypothesis. Keep the runner-up as the Fallback Hypothesis in the Decision Record.

5.5 Classify and Assign Confidence

The selected hypothesis is classified Inferred. Confidence is the selected candidate's normalized score relative to the runner-up; if the margin is small (below a threshold defined by the Reasoning Constitution, typically 0.1), the agent must request clarification rather than commit.

5.6 Emit Decision Record

Commit the record with: observations, candidates, scores, selected hypothesis, fallback, confidence, and the agent that performed the inference.

5.7 Plan Validation

Abductive conclusions are not self-validating. The agent must propose a validation action — typically a downstream agent invocation, a Research Agent query, or a Governance Agent review — to confirm or refute the hypothesis. The validation action is recorded as a pending task in the PKG.

6. Use Inside Genesis

- Story Architect Agent — abduces the central conflict and the irreversible moment from the synopsis.
- Character Manager Agent — abduces a character's Core Fear from their observed behavior.
- Environment Manager Agent — abduces the world's governing rule from the production brief.
- Research Agent — abduces the most plausible domain explanation from gathered findings.
- Psychology Reviewer Agent — abduces the psychological truth from the narrative.

7. Worked Example

Observations (from a synopsis):
- The protagonist avoids intimate conversations.
- The protagonist cries when hearing a particular song.
- The protagonist rejects an otherwise perfect partner.

Candidate Hypotheses:
- H1: The protagonist lost a previous partner and is grieving.
- H2: The protagonist has attachment avoidance rooted in childhood.
- H3: The protagonist is hiding a secret identity.

Scores:
- H1: coverage 0.67, coherence 0.90, simplicity_penalty 0.10 → 0.54
- H2: coverage 1.00, coherence 0.80, simplicity_penalty 0.20 → 0.64
- H3: coverage 0.67, coherence 0.40, simplicity_penalty 0.50 → 0.13

Selected: H2 (attachment avoidance). Fallback: H1 (grief).
Confidence margin: 0.64 − 0.54 = 0.10 — at threshold. The Character Manager Agent holds the conclusion and requests a Research Agent query to disambiguate.

8. Anti-Patterns

- Selecting a hypothesis without scoring alternatives.
- Adopting a hypothesis that contradicts a constitutional invariant or an Explicit fact.
- Allowing a hypothesis that introduces unregistered vocabulary.
- Treating an abductive conclusion as Confirmed. Abductive conclusions are Inferred until validation confirms them.
- Skipping the fallback hypothesis. Abduction always requires a named alternative.
- Forgetting to schedule validation — unvalidated abductive conclusions silently drift into assumptions.

9. Exit Criteria

An abduction is complete when:

- Observations are enumerated and classified.
- At least two candidate hypotheses are scored.
- Selected and fallback hypotheses are named.
- The Decision Record is committed with the Abductive tag.
- A validation action is scheduled.
- The conclusion is classified Inferred with a stated confidence.