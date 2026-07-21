Genesis Pattern (GP)
GP-VAL-003 — Completeness Validation Pattern

Document ID: GP-VAL-003
Title: Completeness Validation Pattern
Version: 1.0.0
Status: Pattern
Authority: Derived from GFS-000, GFS-004, GO-001

1. Purpose

The Completeness Validation Pattern defines how Genesis verifies that a PKG contains every knowledge element required to declare production readiness. Structural validation (GP-VAL-001) checks shape; semantic validation (GP-VAL-002) checks meaning; completeness validation checks coverage. A PKG may be structurally sound and semantically coherent and still be incomplete — a missing theme, a missing antagonist, a missing world rule, a missing irreversible moment.

In Genesis, completeness is the final gate before the Production Readiness Certificate. The Charter's Tenth Principle declares production readiness is measurable. This pattern defines that measurement.

2. When to Apply

Apply this pattern when:

- A production is being considered for Production Readiness Certification.
- A workflow stage produces a deliverable and the deliverable's completeness must be confirmed.
- A revision loop completes and the affected dimension must be re-checked for completeness.
- A Production Brief is being parsed and the discovery agent must determine which required elements are present and which are gaps.
- An ontology version bump introduces new required fields and existing PKGs must be re-checked.

Do not apply this pattern for structural shape (use GP-VAL-001) or for semantic coherence (use GP-VAL-002). Completeness is about presence, not shape or meaning.

3. Completeness Dimensions

Genesis defines completeness across seven dimensions:

- Creative Intent — vision, mission, audience, message, experience.
- Narrative — theme, central conflict, irreversible moment, plot, arc, resolution.
- Character — protagonist, antagonist, supporting cast, motivations, transformations, relationships.
- World — environment, locations, rules, resources, history, time, constraints.
- Production — phases, deliverables, milestones, dependencies, specifications.
- Governance — approvals, decision records, audit trail, compliance.
- Knowledge Quality — evidence classes, confidence floors, traceability.

Each dimension declares a Required Element Set — the knowledge elements that must be present for the dimension to be complete. The set is owned by the corresponding domain ontology and the Reasoning Catalog.

4. Completeness Model

A PKG is complete when:

- Every dimension's Required Element Set is fully present.
- Every present element satisfies its evidence class floor.
- Every present element satisfies its confidence floor.
- Every gap declared in the Production Brief has been resolved (either filled or explicitly waived by governance).
- No Required Element is classified Unknown.

A PKG may be complete with optional elements missing. The Required Element Set is the floor, not the ceiling.

5. Workflow

5.1 Load Required Element Sets

For each dimension, load the Required Element Set from the corresponding ontology and the Reasoning Catalog. The set is versioned with the ontology — an ontology bump may add required elements (a MINOR bump) or remove them (a MAJOR bump with migration).

5.2 Query the PKG

For each required element, query the PKG for its presence. Classify each as:

- Present — element exists with evidence class ≥ floor and confidence ≥ floor.
- Present but weak — element exists but evidence class < floor or confidence < floor.
- Absent — element does not exist.
- Waived — element is explicitly waived by a governance decision.

5.3 Compute Dimension Scores

For each dimension, compute:

- Coverage = present / required.
- Weak fraction = (present but weak) / required.
- Waived fraction = waived / required.

A dimension is Complete when coverage + waived = required and weak fraction = 0. A dimension is Weak when weak fraction > 0. A dimension is Incomplete when coverage + waived < required.

5.4 Emit Completeness Report

Commit the Completeness Report to the PKG with: per-dimension coverage, weak fraction, waived fraction, and verdict; overall PKG completeness verdict (Complete / Weak / Incomplete); and provenance.

5.5 Route Gaps

Every Absent required element triggers a Gap Detected event (see GP-ARCH-002). The Discovery Agent or the responsible domain agent is dispatched to fill the gap. A Weak element triggers a revision request with the responsible agent named.

5.6 Production Readiness Gate

The Production Readiness Certificate may be issued only when:

- Every dimension is Complete.
- No Weak elements remain (or governance has explicitly accepted each).
- All waivers are documented with a governance decision record.
- The Completeness Report is committed.

6. Use Inside Genesis

- Discovery Agent — uses completeness validation to identify gaps in the parsed Production Brief.
- Production Orchestrator — runs completeness validation at every stage boundary to confirm the stage's deliverable.
- Governance Agent — runs completeness validation before issuing the Production Readiness Certificate.
- Revision Agent — uses the Completeness Report to target the agent responsible for each gap.

7. Worked Example

A production's Character dimension is being checked. Required Element Set:

- Protagonist (required, confidence ≥ 0.8).
- Antagonist (required, confidence ≥ 0.8).
- Supporting cast ≥ 2 (required, confidence ≥ 0.6).
- Core Fear per character (required, confidence ≥ 0.7).
- Transformation arc for protagonist (required, confidence ≥ 0.7).

PKG query results:

- Protagonist: Present, confidence 0.85. OK.
- Antagonist: Absent. GAP.
- Supporting cast: 3 characters, confidence ≥ 0.7. OK.
- Core Fear for protagonist: Present, confidence 0.6. WEAK.
- Transformation arc for protagonist: Present, confidence 0.75. OK.

Dimension verdict: Incomplete (Antagonist absent) and Weak (Core Fear below floor).

Gap Detected event emitted for Antagonist → Character Manager Agent dispatched. Revision request queued for Core Fear confidence → Character Manager Agent dispatched to re-derive with stronger evidence.

8. Anti-Patterns

- Treating "present" as "complete" without checking evidence class and confidence.
- Allowing Unknown-classified elements to count as present.
- Waiving required elements without a governance decision record.
- Running completeness validation before structural and semantic validation — completeness assumes the others.
- Issuing the Production Readiness Certificate with any Incomplete dimension.
- Skipping the Completeness Report — the certificate depends on it.

9. Exit Criteria

Completeness validation is complete when:

- Every dimension's Required Element Set has been queried.
- Per-dimension coverage, weak fraction, and waived fraction are recorded.
- Every Absent element has triggered a Gap Detected event.
- Every Weak element has triggered a revision request.
- The Completeness Report is committed.
- For the Production Readiness Certificate: every dimension is Complete and no Weak elements remain unaccepted.