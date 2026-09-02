Genesis Architecture Decision Record (ADR)

ADR-004 — Why Five Confidence Levels

Document ID: ADR-004
Title: Knowledge is Classified into Five Confidence Levels: EXPLICIT, INFERRED, CONFIRMED, ASSUMED, UNKNOWN
Version: 1.0.0
Status: Accepted
Authority: Derived from GFS-000 Constitutional Charter §10 and GFS-009 Quality Constitution

Date: 2025-01-07
Decision Maker: Chief Architect
Reviewer: Governance Agent
Supersedes: none
Superseded By: none
Related Documents: GFS-000, GFS-009, GO-001, GARCH-001, GARCH-003, ADR-002

1. Context

Genesis is an AI-driven system. Unlike traditional databases, where every row is assumed to be true, a knowledge system that uses AI must distinguish between facts the creator asserted, conclusions an AI inferred, assumptions adopted for forward progress, and gaps that have not yet been filled. Without this distinction, the Production Knowledge Graph becomes a flat bag of assertions that no downstream consumer can trust at a calibrated level.

The Constitutional Charter requires that "inference must be distinguished from fact" (GFS-000 §10) and that "every decision must be traceable" (§12). These two requirements create a strong constraint: the system must tag every assertion with a confidence classification, and the classification must travel with the assertion through every projection, every subgraph, and every materialized view.

The question was therefore: how many confidence levels does the system need, what are they, and what are the rules for assigning and propagating them?

Several candidate schemes were considered:

- Two levels (fact / inferred) — too coarse to support the workflows Genesis requires
- Three levels (fact / inferred / unknown) — better, but loses the distinction between inferred-and-validated and inferred-and-unvalidated
- Four levels (explicit / inferred / assumed / unknown) — closer, but loses the distinction between inferred and subsequently confirmed, which is critical for certification
- Five levels (explicit / inferred / confirmed / assumed / unknown) — the scheme this ADR adopts
- Seven levels (a continuous confidence score bucketed) — too granular and too fragile; AI confidence scores are not calibrated enough to support seven meaningful buckets

The Charter itself names five classifications in §10: Explicit, Inferred, Confirmed, Assumed, Unknown. This ADR operationalizes the Charter's enumeration.

2. Decision

Genesis classifies every node and every edge in the Production Knowledge Graph with one of five confidence levels. The five levels are mutually exclusive and collectively exhaustive: every assertion must carry exactly one. The levels are:

EXPLICIT
The assertion was directly stated by the creator in source material (the synopsis, the brief, an interview, a clarifying answer). It is the highest-confidence level. It is not inferred; it is given. EXPLICIT assertions may still be wrong (creators make mistakes), but they are authoritative for the purpose of the production.

INFERRED
The assertion was produced by an agent from existing knowledge using reasoning, pattern matching, or AI generation. It has not yet been validated against external evidence or creator confirmation. INFERRED is the default confidence for agent-generated assertions until they are promoted.

CONFIRMED
The assertion was INFERRED and has subsequently been validated. Validation may take several forms: cross-checked against another source, approved by the creator, corroborated by a second independent agent, or satisfied by an evidence-backed validation rule. CONFIRMED is the highest confidence an inferred assertion can reach.

ASSUMED
The assertion was adopted without evidence for the purpose of forward progress. It is a placeholder that the system treats as true until it is either confirmed or replaced. ASSUMED assertions are flagged for discovery; they must never silently persist into a certified Production Knowledge Package.

UNKNOWN
The assertion has not been made. It marks a gap. UNKNOWN is not a value on an existing node; it is the presence of an absence—a declared gap that the system has acknowledged and intends to resolve through discovery.

The decision is elaborated by the following binding rules:

- Every node and every edge in the PKG carries a `confidence` attribute with exactly one of these five values.
- Confidence is immutable per revision. A change in confidence creates a new revision, not an in-place update.
- Confidence travels with the assertion through every subgraph, every materialized view, and every export. No projection may strip confidence.
- Confidence is queryable. The Semantic Layer (GARCH-003) supports filtering by confidence level and computing confidence-aware subgraphs.
- Confidence propagates. A derived node's confidence is a function of its supporters' confidence, per the propagation rules in GARCH-003 §10.
- Confidence thresholds are production-configurable but bounded. A production may set its certification threshold no lower than CONFIRMED for all certification-blocking assertions and no lower than EXPLICIT for creator-authored creative intent.
- ASSUMED assertions must be resolved before certification. A PKP may not be issued while ASSUMED assertions remain in certification-blocking subgraphs.
- UNKNOWN gaps must be either resolved or explicitly waived by governance before certification.

3. Status

Accepted on 2025-01-07 by the Chief Architect, reviewed and approved by the Governance Agent.

No supersession is anticipated. The five-level scheme is derived directly from the Charter (GFS-000 §10), which would require constitutional amendment to change.

4. Consequences

4.1 Positive Consequences

- Auditable reasoning. Every assertion carries its epistemic status. A reviewer can ask "show me everything that is INFERRED but not yet CONFIRMED" and get a precise answer. This is impossible in a system with a single "confidence score."
- Quality gates become meaningful. Certification can require CONFIRMED for blocking assertions. Without five levels, certification would have to choose between "everything must be fact" (impossible) and "everything is fine" (irresponsible).
- Discovery is targetable. UNKNOWN and ASSUMED assertions are explicit targets for discovery agents. The system can prioritize its work by the number and severity of gaps.
- Confidence propagation is well-defined. Because there are exactly five levels with a fixed ordering, propagation rules are simple and deterministic. A continuous score would require ad hoc propagation functions.
- Consumer trust is calibrated. A downstream consumer (the Studio Engine, a human reviewer) can choose its trust level: "treat CONFIRMED as true, INFERRED as a hypothesis, ASSUMED as a warning, UNKNOWN as missing."
- Creator intent is preserved. EXPLICIT is a distinct level, so creator-stated assertions are never silently merged with agent-inferred assertions. The distinction between "the creator said this" and "the agent thinks this" is preserved end to end.
- Contradictions are detectable. A contradiction between two EXPLICIT assertions is a creator-level conflict; a contradiction between two INFERRED assertions is a reasoning failure; a contradiction between an EXPLICIT and an ASSUMED assertion is a gap-closing event. Each requires a different response, and the five-level scheme makes the type of contradiction legible.

4.2 Negative Consequences

- Five levels impose a discipline. Every agent that writes to the PKG must classify its output. Agents that cannot justify their classification produce validation findings. This is friction, deliberately.
- The levels are discrete, not continuous. A reviewer who wants to know "how confident is this INFERRED assertion?" cannot get a finer answer from the confidence tag alone. The mitigation is that provenance carries the supporting evidence and the agent's reasoning, which is a richer signal than a number.
- Promotion from INFERRED to CONFIRMED requires a validation step. This adds a workflow hop. The mitigation is that validation can be batched and automated for many assertion types.
- The five-level vocabulary must be taught to every contributor. A new agent author who confuses ASSUMED with INFERRED will produce incorrect provenance. The mitigation is the Validation Engine, which flags confidence misclassifications, and the agent specifications, which define each level precisely.
- Cross-production comparability is imperfect. What one production considers CONFIRMED (e.g., cross-checked against a reference) another might consider EXPLICIT (if the creator directly approved the inference). The mitigation is the production's confidence profile, which declares its validation rules in writing.

4.3 Neutral Consequences

- The five-level vocabulary enters the project's working language. Future ADRs, agent specs, and workflow definitions must use the five terms consistently.
- Confidence becomes a first-class query dimension. Tools that ignore confidence are non-conforming.
- The PKG schema includes a confidence field on every node and every edge, which shapes every downstream data structure.

5. Alternatives

5.1 Alternative 1: Two Levels (Fact / Inferred)

Description: Every assertion is either a fact (creator-stated) or inferred (agent-produced). No further distinction.

Advantages:
- Simplest possible scheme.
- Easy to teach and enforce.
- No propagation rules needed beyond "fact outranks inferred."

Disadvantages:
- Loses the distinction between inferred-and-validated and inferred-and-unvalidated. This is the single most important distinction for certification.
- Loses the distinction between assumed-for-progress and properly inferred. ASSUMED assertions are dangerous if they silently inherit the trust of INFERRED.
- No way to mark gaps. Without UNKNOWN, gaps are invisible in the PKG.
- Cannot support quality gates. Certification needs at least three levels to distinguish "ready," "almost ready," and "not ready."

Rejection Rationale: Two levels are too coarse to support the Charter's requirement that inference be distinguished from fact and that production readiness be measurable.

5.2 Alternative 2: Three Levels (Explicit / Inferred / Unknown)

Description: Assertions are explicit, inferred, or unknown. No confirmed and no assumed.

Advantages:
- Cleaner than two levels.
- Captures the most important distinction (explicit vs. inferred) and the gap marker (unknown).
- Easy to teach.

Disadvantages:
- No way to represent "inferred and then validated." Every inferred assertion stays INFERRED forever, which makes certification impossible (you cannot certify what has not been validated) or trivial (you certify INFERRED, which defeats the purpose).
- No way to represent "assumed for forward progress." Assumptions are a real and necessary category in pre-production; without it, agents either refuse to proceed or silently promote assumptions to INFERRED, which is worse.

Rejection Rationale: Three levels lose the validated-inference and assumed-for-progress distinctions, both of which are essential to the workflow layer.

5.3 Alternative 3: Continuous Confidence Score (0.0 to 1.0)

Description: Every assertion carries a numeric confidence score produced by the agent or model. Consumers filter by threshold.

Advantages:
- Maximum granularity.
- No discrete taxonomy to enforce.
- Aligns with how some AI models already emit confidence.

Disadvantages:
- AI confidence scores are not calibrated across models, providers, or even prompts. A score of 0.8 from one model is not comparable to 0.8 from another.
- Propagation is undefined. How do you combine 0.7 and 0.6? Weighted average? Min? Max? Every choice is arbitrary.
- Quality gates become arbitrary. "Certify if score > 0.85" is a number with no semantic meaning. It does not say "validated" or "creator-approved."
- Audits become hard. A reviewer cannot easily ask "show me everything the creator directly stated" because that distinction is lost in the score.
- The score drifts. Models change, scores change, and old assertions become incomparable with new ones. Discrete levels are stable across model changes.

Rejection Rationale: Continuous scores look precise but are not. They lack calibration, lack propagation semantics, and lack auditability. The five-level scheme trades false precision for true semantics.

5.4 Alternative 4: Seven or More Levels

Description: A finer taxonomy with levels like "creator-stated," "creator-approved," "cross-validated," "single-agent-inferred," "multi-agent-inferred," "assumed," "unknown," "disputed."

Advantages:
- Maximum semantic distinction.
- Captures every epistemic nuance.

Disadvantages:
- The taxonomy becomes hard to teach. Seven levels require a manual to apply correctly.
- Validation rules explode. Each level needs its own rules; with seven levels, the rule set becomes unmanageable.
- The marginal levels do not carry enough operational value. The difference between "single-agent-inferred" and "multi-agent-inferred" is interesting but rarely changes a downstream decision.
- Drift toward continuous scoring. Seven levels tend to be treated as a seven-point scale, reintroducing the problems of the continuous alternative.

Rejection Rationale: Seven levels cross the threshold where the taxonomy costs more to maintain than it returns in expressive power. Five levels capture every operationally meaningful distinction.

6. Compliance

6.1 Validation Rules

The Validation Engine (S3 per GARCH-002) enforces the following invariants:

- Every node and every edge in the PKG must carry a `confidence` attribute with exactly one of the five values. Missing or invalid values produce BLOCK findings.
- EXPLICIT assertions must reference a creator-authored source in their provenance. An EXPLICIT assertion without creator provenance is reclassified as INFERRED and a warning is raised.
- CONFIRMED assertions must reference a validation event in the Provenance Ledger. A CONFIRMED assertion without validation provenance is reclassified as INFERRED and a warning is raised.
- ASSUMED assertions must reference a forward-progress rationale. Assumed assertions without rationale are rejected.
- UNKNOWN gaps must be declared as gap nodes, not as missing data. Missing data is a validation failure; declared gaps are valid.
- Certification-blocking subgraphs must contain no ASSUMED or unresolved UNKNOWN assertions at certification time. This invariant is checked at the Certification gate.

6.2 Governance Gates

- The Confidence Profile gate (per the Quality Constitution, GFS-009) must approve each production's confidence thresholds before the production may begin. Thresholds may be stricter than the Charter's defaults but not looser.
- The Certification gate must refuse to issue a PKP if any certification-blocking assertion is below CONFIRMED or if any ASSUMED or unresolved UNKNOWN assertion remains in the certification subgraph.

6.3 Audit Checks

- Query for any assertion with a confidence value outside the five-level enumeration. Such assertions indicate a writer that bypassed the schema.
- Query for any EXPLICIT assertion lacking creator provenance. Such assertions indicate a misclassification.
- Query for any CONFIRMED assertion lacking validation provenance. Such assertions indicate a misclassification.
- Query for any certification-blocking subgraph containing ASSUMED or UNKNOWN assertions. Such subgraphs indicate a premature certification attempt.
- Query for confidence propagation correctness per GARCH-003 §10. Any derived node whose confidence exceeds the propagation-rule-computed value is flagged.

6.4 Amendment Process

This ADR may be amended by supersession. Because the five-level scheme is derived from GFS-000 §10, a change to the scheme itself would require constitutional amendment. A superseding ADR may clarify the operational rules (assignment, propagation, promotion) without changing the five levels.

7. References

- GFS-000 Constitutional Charter, §§10, 12
- GFS-009 Quality Constitution (referenced)
- GO-001 Genesis Core Ontology, §7 (Knowledge Domain, Confidence)
- GARCH-001 Enterprise Architecture, §2 (Architectural Principles)
- GARCH-003 Semantic Layer Architecture, §§4.3, 8.2, 10
- ADR-002 Why Knowledge Graph Not Relational

8. Notes

The five-level scheme is the third architectural cornerstone, alongside the pre-production boundary (ADR-001), the graph data structure (ADR-002), and the constitutional hierarchy (ADR-003). Together, the four ADRs define the shape, the storage, the governance, and the epistemics of Genesis. Every subsequent decision operates within the frame they establish.

9. Sign-off

| Role | Name | Date | Signature |
|------|------|------|----------|
| Decision Maker | Chief Architect | 2025-01-07 | (signed) |
| Reviewer | Governance Agent | 2025-01-08 | (signed) |
| Governance Agent | Governance Agent | 2025-01-08 | (signed) |