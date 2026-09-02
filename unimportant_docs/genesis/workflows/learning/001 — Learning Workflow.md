Genesis Workflow Specification (GWS)
GWS-013 — Learning Workflow

Document ID: GWS-013
Title: Learning Workflow
Version: 1.0.0
Status: Workflow Specification
Authority: Derived from GFS-000, GFS-007

1. Purpose

This workflow defines how Genesis learns from completed productions. Learning is the mechanism by which the engine refines its ontologies, sharpens its agents, and accumulates reusable patterns without violating the constitutional principle that knowledge precedes production and consistency overrides creativity.

2. Scope

Learning applies to:
- Evaluation feedback from completed productions.
- Patterns extracted from certified PKPs.
- Ontology refinements derived from observed defects or gaps.
- Agent behavior refinements derived from evaluation outcomes.

Learning does NOT modify:
- The Constitutional Charter or any GFS document. Those change only via the governance workflow (GWS-012).
- Existing certified PKPs. Those are immutable.
- A live production session.

3. Preconditions

- The source production is in Archived state.
- The PKP is available in the registry.
- All evaluation reports and revision history are intact.
- The production has been closed for at least the configured cooldown period to avoid reactive learning from incomplete feedback.

4. Workflow Stages

4.1 Stage L0: Selection

Actor: Feedback Learning Agent
Input: Registry of archived productions
Output: Learning candidate set

The Feedback Learning Agent selects productions eligible for learning:
- Exclude productions that failed without certification.
- Include productions that completed at least one revision loop.
- Include productions with rich evaluation reports.
- Sample across genres, territories, and production scales.

4.2 Stage L1: Feedback Extraction

Actor: Feedback Learning Agent
Input: Selected PKPs
Output: Feedback record set

For each production, the agent extracts:
- Evaluation scores per dimension.
- Critical issues raised and how they were resolved.
- Revision loop count and outcomes.
- Creator overrides and their justification.
- Knowledge gaps discovered late (after they should have been caught).

Each feedback record is tagged with provenance: which production, which agent, which stage.

4.3 Stage L2: Pattern Extraction

Actor: Pattern Extraction Agent
Input: PKPs, feedback records
Output: Candidate patterns

The Pattern Extraction Agent identifies reusable structures:
- Narrative structures that consistently produce high story quality scores.
- Character configurations that consistently pass psychology review.
- Scene and shot configurations that produce high visual consistency scores.
- Knowledge gap patterns that recur across productions.

Each candidate pattern includes:
- Pattern description.
- Supporting productions (with provenance).
- Confidence derived from recurrence and evaluation outcomes.
- Applicability conditions (genre, territory, scale).

4.4 Stage L3: Ontology Gap Analysis

Actor: Feedback Learning Agent
Input: Feedback records, current GO-NNN ontologies
Output: Ontology gap report

The agent identifies where the ontology failed to capture necessary knowledge:
- Concepts referenced in evaluation reports but missing from the ontology.
- Relationships that agents inferred but that the ontology did not allow.
- Constraints that, if present, would have prevented a critical issue.

The gap report becomes input to a governance proposal (GWS-012) if it recommends an ontology change.

4.5 Stage L4: Pattern Validation

Actor: Validation agents (Story Quality, Visual Consistency, etc.)
Input: Candidate patterns
Output: Validated pattern set

Patterns are validated before being added to the pattern library:
- The pattern must be consistent with the constitutional hierarchy.
- The pattern must not encode bias or unsafe content.
- The pattern must produce measurable improvement when applied to a held-out production.
- Patterns that fail validation are recorded but not added.

4.6 Stage L5: Library Update

Actor: Pattern Extraction Agent
Input: Validated patterns
Output: Updated pattern library

Validated patterns are added to the pattern library with:
- Pattern ID and version.
- Provenance (which productions informed it).
- Confidence level.
- Applicability conditions.
- Usage counter (initialized to zero).

The pattern library is itself versioned. Updates follow the patch or minor version policy depending on scope.

4.7 Stage L6: Ontology Refinement Proposal

Actor: Feedback Learning Agent
Input: Ontology gap report
Output: Governance proposal

Where the gap analysis recommends an ontology change, the agent submits a proposal via GWS-012. The learning workflow does not amend ontologies directly. It only proposes amendments.

4.8 Stage L7: Agent Behavior Update

Actor: Deployment operator
Input: Pattern library updates
Output: Updated agent bindings

Agent implementations may consume the pattern library. Updating an agent to use new patterns is a deployment-scoped change handled via GWS-011. The learning workflow only updates the library; it does not modify running agents.

4.9 Stage L8: Closure

Actor: Feedback Learning Agent
Input: Library update confirmation, proposal submission record
Output: Learning cycle record

The learning cycle is recorded with:
- Productions analyzed.
- Patterns added or updated.
- Proposals submitted.
- Audit trail entries.

The cycle is closed and the next cycle starts from Stage L0 with a refreshed candidate set.

5. Feedback Loop Discipline

- Learning never shortcuts the validation gates of a live production. Patterns are advisory, not mandatory.
- A pattern with low confidence is surfaced to agents as a hint, not as a constraint.
- A pattern with high confidence may be promoted to a constraint only via a governance proposal.

6. Bias and Safety

- Patterns derived from a narrow set of productions are flagged as low-confidence.
- The Pattern Extraction Agent must check candidate patterns for biased characterizations, stereotyping, and harmful tropes before validation.
- Safety checks cannot be learned away. A pattern that would weaken a safety check is rejected.

7. Provenance and Audit

Every pattern and every ontology gap report carries full provenance. Any consumer of the pattern library can trace each pattern back to the productions that informed it. The learning audit trail is part of the engine's deployment record and is available for governance review.

8. Cross-References

- GFS-000 — Constitutional Charter
- GFS-007 — Governance Constitution
- GWS-001 — Full Production Workflow
- GWS-012 — Governance Workflow
- GAS-NNN — Feedback Learning Agent, Pattern Extraction Agent