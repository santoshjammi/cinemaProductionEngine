Genesis Pattern (GP)
GP-REAS-001 — Deductive Reasoning Pattern

Document ID: GP-REAS-001
Title: Deductive Reasoning Pattern
Version: 1.0.0
Status: Pattern
Authority: Derived from GFS-002 Reasoning Constitution, GO-001

1. Purpose

The Deductive Reasoning Pattern defines how Genesis agents reason from general rules to specific conclusions. Deduction is the strictest form of reasoning available inside Genesis: when the premises are valid and the inference rule is sound, the conclusion is guaranteed to hold.

In Genesis, deduction is used for constitutional compliance, ontology enforcement, structural validation, and any situation where a conclusion must follow with certainty. It is the reasoning mode of validators, governance agents, and the structural consistency engine. It is never the mode of creative discovery.

2. When to Apply

Apply this pattern when:

- A constitutional rule must be enforced (e.g. every Character must have a Core Fear).
- An ontology cardinality constraint must be checked (e.g. every Scene has at least one Beat).
- A structural invariant must be verified (e.g. every narrative must contain exactly one irreversible moment).
- A decision must be reproducible and defensible without probabilistic hedging.

Do not apply deduction to creative or interpretive tasks. Deduction cannot discover latent knowledge; it can only apply what is already asserted.

3. Structure of a Deductive Step

A deductive step in Genesis is recorded as a four-tuple:

- Premise 1 — a general rule drawn from the Charter, an ontology, a policy, or a prior validated conclusion.
- Premise 2 — a fact drawn from the Production Knowledge Graph or an upstream agent's output.
- Inference Rule — the named rule applied (e.g. Modus Ponens, Universal Instantiation, Cardinality Enforcement).
- Conclusion — the specific assertion derived.

Each step is stored as a Decision Record with provenance links to the premises and the rule. Without provenance, the conclusion is treated as an assertion, not as a deduction.

4. Example Inference Rules

- Modus Ponens — if P implies Q, and P holds, then Q holds.
- Universal Instantiation — for all x, P(x); therefore P(a) for a specific a.
- Cardinality Enforcement — every Scene has at least one Beat; this Scene has zero Beats; therefore this PKG is invalid.
- Inheritance Resolution — Character inherits from Narrative Thing; therefore every Character instance satisfies the constraints of Narrative Thing.
- Transitive Closure — A depends on B; B depends on C; therefore A depends on C (when depends_on is declared transitive in GO-002).

5. Workflow

5.1 Collect Premises

The agent gathers the rule (from Charter / ontology / policy / registry) and the fact (from the PKG). Both must be current. Stale premises invalidate the deduction.

5.2 Verify Inference Rule

The rule must be one of the registered inference rules. Agents may not invent rules at runtime.

5.3 Apply Rule

The agent emits the conclusion as a typed Knowledge Object in the PKG, classified per the Sixth Principle: Explicit, Inferred, Confirmed, Assumed, or Unknown. A deductive conclusion is always Inferred unless it duplicates an Explicit fact.

5.4 Attach Confidence

Deductive conclusions carry confidence 1.0 when both premises are Explicit and the rule is sound. Confidence degrades when a premise is Assumed or Inferred; in those cases, the conclusion's confidence is the minimum of its premises' confidences.

5.5 Emit Decision Record

The conclusion is recorded with:

- Source premises (with identifiers).
- Rule name.
- Resulting assertion.
- Confidence.
- Agent that performed the inference.
- Timestamp.

Without a Decision Record, the conclusion may not be referenced by downstream agents.

6. Use Inside Genesis

- Structural Validation Agent — uses deduction to enforce ontology cardinalities.
- Governance Agent — uses deduction to enforce constitutional rules before certifying production readiness.
- Revision Agent — uses deduction to determine which upstream agent must be re-invoked when a downstream constraint fails.
- Production Orchestrator Agent — uses deduction to compute the next workflow stage from the workflow specification.

7. Worked Example

Premise 1 (rule, from GO-104): Every Character has exactly one Core Fear.
Premise 2 (fact, from PKG): Arjuna is a Character.
Premise 2 (fact, from PKG): Arjuna has zero declared Core Fears.
Rule: Cardinality Enforcement (exactly one).
Conclusion: PKG is invalid for Character "Arjuna" — missing Core Fear.

The Structural Validation Agent emits a Decision Record, the Revision Agent deductively maps the failure to the Character Manager Agent, and a revision request is dispatched.

8. Anti-Patterns

- Treating a probabilistic LLM guess as a deduction. Deductions are rule-bound, not model-bound.
- Using deduction for narrative design — design requires abduction or induction, not deduction.
- Citing a premise without an identifier. Premises must be resolvable.
- Omitting the Decision Record. Unprovenanced conclusions are not deductions.
- Allowing an inference rule not registered in the Reasoning Catalog.

9. Exit Criteria

A deduction is complete when:

- Both premises are identified and resolvable.
- The inference rule is registered.
- The conclusion is classified (Explicit / Inferred / Confirmed / Assumed / Unknown).
- The confidence is computed.
- A Decision Record is committed to the PKG.