Genesis Governance
GGV-003 — Review Policy

Document ID: GGV-003
Title: Genesis Review Policy
Version: 1.0.0
Status: Governance Standard
Authority: Derived from GFS-006, GFS-007, GGV-001

1. Purpose

This policy defines how reviews are conducted within the Genesis Engine:
who reviews what, against which criteria, how often, how the results are
recorded, and how a reviewer's decision may be appealed. It applies to
every review performed by any constitutional role, agent, or human
reviewer.

2. Foundational Principle

Review is the disciplined act of refusing to trust unverified knowledge.

Genesis does not ship on the strength of a single agent. Every significant
artifact is reviewed by at least one party that did not produce it. The
cost of a review is always less than the cost of a downstream defect.

3. Review Types

3.1 Self Review

- Performed by: the producing role
- Purpose: catch obvious defects before peer review
- Required before: any artifact is submitted for peer review
- Output: a self-review note attached to the artifact

3.2 Peer Review

- Performed by: a different role in the same domain
- Purpose: validate domain correctness
- Required before: domain approval
- Output: a peer review record (see section 6)

3.3 Cross-Domain Review

- Performed by: a role from a different domain
- Purpose: detect cross-domain inconsistencies
- Required before: validation approval of any cross-domain artifact
- Output: a cross-domain review record

3.4 Constitutional Review

- Performed by: the Validation Authority
- Purpose: verify compliance with the Charter and derived constitutions
- Required before: governance approval
- Output: a constitutional compliance certificate

3.5 Governance Review

- Performed by: the Governance Agent
- Purpose: authorize publication, certification, or lifecycle transitions
- Required before: publication
- Output: a governance decision record

3.6 Human Review

- Performed by: a human reviewer in a constitutional role
- Purpose: confirm intent, resolve ambiguity, evaluate creative direction
- Required for: any creative-impact change and any CRITICAL change
- Output: a human review record with signature

4. Reviewer Eligibility

A reviewer shall:

- Hold a registered constitutional role or be a designated human reviewer
- Not be the producer of the artifact under review
- Not share accountability scope with the producer for the artifact under
  review, except in cross-domain review where overlap is the point
- Disclose any conflict of interest in the review record

A reviewer who is ineligible shall recuse themselves and the review is
reassigned. A review performed by an ineligible reviewer is void.

5. Review Criteria

Every review shall evaluate the artifact against, at minimum:

- Constitutional compliance (Charter and derived constitutions)
- Internal consistency (no contradictions within the artifact)
- Cross-domain consistency (no contradictions with related artifacts)
- Completeness (all required fields, sections, subgraphs, or evidence)
- Traceability (every significant conclusion is supported)
- Confidence validity (confidence labels are justified by evidence)
- Provenance integrity (origin, dependencies, and revisions are recorded)
- Backward compatibility (where applicable)
- Risk (impact and likelihood of defects)

Each criterion shall receive one of: PASS | PASS_WITH_NOTES | FAIL. A FAIL
on constitutional compliance or internal consistency blocks the artifact.
Other FAILs block unless explicitly waived by the appropriate authority per
GGV-001 section 5.

6. Review Log

Every review shall produce a record written to the review log containing:

- Review ID (UUID)
- Artifact under review (file, node set, subgraph, decision)
- Reviewer (role, agent, or human identifier)
- Review type
- Date
- Criteria evaluated (with PASS / PASS_WITH_NOTES / FAIL per criterion)
- Findings (numbered, each with severity and location)
- Recommendation (APPROVE | REJECT | REVISE)
- Conditions (if APPROVE with conditions)
- Conflict of interest disclosure
- Provenance (session, references)

The review log is append-only. Reviews may not be edited after submission;
corrections require a new review record that supersedes the prior one.

7. Review Frequency

- Per artifact: every published version is reviewed at least once before
  publication
- Per session: the Production Orchestrator triggers a session-level review
  at every checkpoint and at session end
- Per ontology: reviewed at every MAJOR or MINOR version change
- Per agent: reviewed at registration and at every behavior change that
  affects canonical knowledge
- Per PKG: reviewed at every version bump and at certification
- Periodic: the Governance Agent schedules a full review of every ACTIVE
  ontology and agent every 12 months, regardless of change

8. Severity Classification

- BLOCKER: constitutional violation, contradiction, or untraceable
  conclusion; artifact may not proceed
- MAJOR: missing required content, failed cross-domain check, confidence
  unjustified; artifact returns for revision
- MINOR: formatting, documentation, or non-blocking inconsistency; artifact
  proceeds with a recorded note
- INFO: observation; no action required

9. Appeal Process

A producer may appeal a review decision once. The appeal shall:

- Cite the review record being appealed
- Provide new evidence, a corrected artifact, or a rebuttal referencing the
  constitutional standard
- Be submitted within 5 business days of the review decision
- Be reviewed by the next authority in the escalation path (GGV-001
  section 8)

The appeal outcome is one of:

- UPHELD: the original decision stands; the artifact is rejected
- OVERTURNED: the original decision is reversed; the artifact proceeds
- REVISE: the producer must address the appeal reviewer's notes and
  resubmit

A second rejection is final for the current production cycle. Further
appeals require a charter-level amendment.

10. Reviewer Accountability

Reviewers are accountable for their decisions. A review that approves a
BLOCKER defect is itself a MAJOR breach and is logged to the governance
audit trail. Repeated reviewer failures trigger a Governance review of the
reviewer's eligibility.

11. Compliance

This policy is binding on every constitutional role, agent, and human
reviewer. Reviews performed outside this policy are void and shall be
repeated by an eligible reviewer. The Governance Agent audits the review
log at the end of every session.

12. Invariants

- Every significant artifact is reviewed.
- No reviewer reviews their own work.
- Every review is recorded.
- Every record is immutable.
- Every rejection is appealable once.
- Every reviewer is accountable.
- Review frequency is scheduled, not opportunistic.