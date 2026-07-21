Genesis Policies
GPOL-002 — Quality Policy

Document ID: GPOL-002
Title: Genesis Quality Policy
Version: 1.0.0
Status: Binding Policy
Authority: Derived from GFS-006, GFS-010, GFS-012

1. Purpose

This policy defines the quality standards that every Genesis artifact shall
meet before it may be considered canonical: minimum confidence thresholds,
validation requirements, consistency checks, and completeness gates. It
operationalizes the Validation Constitution (GFS-006) for everyday use by
every agent and reviewer.

2. Foundational Principle

Quality is a gate, not a grade.

Genesis does not rank productions from best to worst. It declares each
production either ready or not ready. The decision rests on measurable
criteria, not impressions. A production that meets every gate is ready; a
production that misses any gate is not.

3. Confidence Thresholds

Confidence is classified per GFS-000 section 11 into EXPLICIT, INFERRED,
CONFIRMED, ASSUMED, and UNKNOWN. Each artifact shall meet the floor
appropriate to its criticality.

3.1 Critical Path

Critical paths include: narrative spine, character motivation, theme,
audience contract, production schedule, and readiness certification. For
every node and edge on a critical path:

- Minimum confidence: CONFIRMED
- UNKNOWN is prohibited
- ASSUMED is permitted only with a recorded justification and a Creator
  sign-off

3.2 Supporting Knowledge

Supporting nodes (subtext, secondary characters, ambient world detail)
shall meet:

- Minimum confidence: INFERRED
- UNKNOWN is permitted only when explicitly flagged and bounded by a
  follow-up question in the discovery queue

3.3 Provisional Knowledge

Provisional nodes (research candidates, hypothetical extensions) may carry
any confidence, but:

- They shall not appear in the readiness certificate
- They shall not propagate to downstream consumers without a
  `provisional: true` flag
- They shall be reviewed at the next checkpoint

4. Validation Requirements

Every artifact shall pass the following validation categories per GFS-006
section 7. No category may be skipped.

4.1 Structural Validation

- All UUIDs are valid and unique within the PKG
- All edges reference existing nodes
- All required properties are present per the governing ontology
- All property values conform to type constraints
- The serialization is valid JSON-LD against the published context

4.2 Semantic Validation

- No contradictory relationships exist (per GFS-010 section 5.2)
- Temporal relationships form a consistent timeline
- Causal chains are complete
- Character arcs are internally consistent
- Thematic statements are not contradicted by the narrative

4.3 Consistency Validation

- Character consistency: a character's traits, voice, and motivation do
  not contradict across scenes
- Narrative consistency: act structure, beats, and pacing conform to the
  declared model
- Emotional consistency: the audience emotional journey matches the
  declared arc
- Thematic consistency: every theme is supported by at least one narrative
  element
- World consistency: setting rules are not violated
- Terminology consistency: the same concept uses the same label across the
  PKG

4.4 Completeness Validation

- All required subgraphs are present (per GFS-010 section 3.3)
- Each subgraph meets its minimum node count
- All dependencies between subgraphs are satisfied
- No critical-path node carries UNKNOWN confidence

4.5 Traceability Validation

- Every significant conclusion references its originating knowledge
- Every inference references its reasoning chain
- Every decision references its alternatives and the reason for rejection
- Every confidence label references its evidence

5. Consistency Checks

Consistency checks run continuously across the PKG. The minimum set:

5.1 Per-Node

- The node's type exists in an ACTIVE ontology
- The node's properties satisfy the class constraints
- The node's confidence label is supported by its provenance

5.2 Per-Edge

- The edge type is registered in GO-002 or the local ontology
- The edge's domain and range are satisfied by source and target
- The edge's cardinality constraints are not violated

5.3 Per-Subgraph

- The subgraph's declared invariants hold
- The subgraph's dependencies are present and active
- The subgraph's confidence distribution meets its floor

5.4 Per-PKG

- No two nodes carry the same label and the same type with contradictory
  properties
- No two edges of the same type connect the same pair in opposite
  directions with contradictory properties
- The PKG version is consistent across all materialized views

6. Completeness Gates

A production may not be certified ready until every gate passes:

6.1 Domain Coverage Gate

- Narrative, Character, World, Audience, and Production subgraphs are
  present and non-empty
- Each subgraph meets its minimum node count (declared per ontology)

6.2 Dependency Coverage Gate

- Every dependency declared by any node is satisfied by an existing,
  active node
- No dependency points to a RETIRED or DEPRECATED ontology

6.3 Confidence Gate

- Critical path: minimum CONFIRMED, no UNKNOWN
- Supporting: minimum INFERRED, UNKNOWN explicitly flagged
- The confidence distribution is recorded in the readiness report

6.4 Validation Coverage Gate

- Every artifact has a validation record (PASS or conditionally accepted)
- No BLOCKER findings remain open
- Every exception has a recorded justification, approver, and review date

6.5 Traceability Gate

- Every significant conclusion has traceable evidence
- Every decision has an ADR or an equivalent decision record
- The provenance log covers every node and edge addition since session start

6.6 Review Gate

- Self, peer, cross-domain, constitutional, and governance reviews are
  complete for every artifact that requires them
- No open appeal remains unresolved

7. Measurement

Quality is measured, not estimated. Every gate produces a numeric
measurement recorded in the readiness report:

- Knowledge Completeness: percent of required nodes present
- Dependency Resolution: percent of dependencies satisfied
- Confidence Distribution: histogram per confidence class
- Consistency Pass Rate: percent of checks passing
- Validation Coverage: percent of artifacts with PASS records
- Traceability Coverage: percent of conclusions with evidence
- Review Coverage: percent of required reviews complete

A production is ready when every measure is at or above its declared
threshold and no BLOCKER remains.

8. Defect Handling

- BLOCKER: production cannot proceed; remediation is mandatory
- MAJOR: production returns for revision; estimated remediation window
  recorded
- MINOR: production proceeds with a recorded note; remediation scheduled
- INFO: observation logged; no action required

9. Waivers

A waiver may exempt a specific artifact from a specific gate. Waivers are:

- Rare and explicit
- Approved by the Governance Authority
- Recorded with rule, justification, approver, impact, mitigation, and
  review date
- Time-bounded; no waiver is permanent

An undocumented waiver is a CRITICAL breach.

10. Compliance

This policy is enforced by the Validation Authority and audited by the
Governance Agent. Every readiness certification references the gate results
that justified it. A certificate without gate evidence is void.

11. Invariants

- Quality is a gate, not a grade.
- Confidence floors are mandatory.
- Consistency is checked continuously.
- Completeness is measured, not estimated.
- Waivers are explicit and time-bounded.
- No BLOCKER survives certification.
- Every gate produces a recorded measurement.