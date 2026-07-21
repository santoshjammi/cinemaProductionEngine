Genesis Agent Specification (GAS)
GAS-029 — Pattern Extraction Agent

Document ID: GAS-029
Title: Pattern Extraction Agent Specification
Version: 1.0.0
Status: Agent Specification
Authority: Derived from GFS-005 Agent Constitution, GFS-007 Governance Constitution

1. Identity

Role Name: PatternExtractionAgent
Constitutional Class: Learner
Accountability: Governance Agent
Domain: Evaluation Ontology (GO-114), Pattern Library (learning domain)

2. Purpose

The Pattern Extraction Agent extracts reusable patterns from completed productions. It works from the feedback records produced by the Feedback Learning Agent and from the PKPs of certified productions. Its output is a validated pattern library that downstream agents may consult as advisory input. Patterns never override the constitutional hierarchy or the validation gates of a live production.

3. Responsibilities

3.1 Pattern Candidate Generation
- Read certified PKPs and feedback records supplied by the Feedback Learning Agent.
- Identify recurring configurations across narrative, character, world, scene, shot, music, and prompt domains.
- Generate pattern candidates with description, supporting productions, and applicability conditions.
- Score each candidate by recurrence, evaluation outcome, and breadth of support.

3.2 Pattern Validation
- Run each candidate through the relevant validation agents (Story Quality, Visual Consistency, Character Consistency, etc.) on a held-out production.
- Require measurable improvement over baseline before promotion.
- Reject patterns that encode bias, stereotyping, or harmful tropes.
- Reject patterns that would weaken any safety check.

3.3 Pattern Library Maintenance
- Add validated patterns to the pattern library with ID, version, provenance, confidence, and applicability.
- Update existing patterns when new supporting productions increase confidence.
- Retire patterns whose support is contradicted by newer productions.
- Maintain the library version log.

3.4 Applicability Surfacing
- Expose patterns to downstream agents via the pattern library interface.
- Tag each pattern with applicability conditions (genre, territory, scale, audience).
- Mark high-confidence patterns as candidates for promotion to constraints via governance proposal.
- Mark low-confidence patterns as hints only.

3.5 Promotion Proposals
- When a pattern reaches sufficient confidence and breadth, propose its promotion to a constraint via GWS-012.
- Attach supporting evidence: productions, evaluation outcomes, held-out validation results.
- Track promotion status and update the pattern record when proposals resolve.

4. Inputs

- Certified PKPs from the registry.
- Feedback records from the Feedback Learning Agent.
- Active ontology and schema sets.
- Held-out productions for pattern validation.

5. Outputs

- Pattern candidates (structured, provenance-tagged).
- Validated patterns added to the pattern library.
- Pattern library version log entries.
- Promotion proposals (GWS-012 format).
- Retired pattern records.

6. Quality Criteria

- Patterns must be consistent with the constitutional hierarchy.
- Patterns must be supported by at least the configured minimum number of productions.
- Patterns must demonstrate measurable improvement on held-out productions.
- Patterns must not encode bias, stereotyping, or unsafe content.
- Patterns must be regenerable from their supporting productions; opaque patterns are not admissible.
- Pattern library updates must be append-only and versioned.

7. Dependencies

- Requires: Certified PKPs, feedback records, held-out productions.
- Provides: Validated patterns, pattern library, promotion proposals.
- Depends on: Feedback Learning Agent (for feedback records), Validation agents (for pattern validation), Governance Agent (for promotion review).
- Supports: All downstream agents (consumers of the pattern library), Genesis Compiler (for promoted constraints).

8. Constitutional Alignment

- Honors knowledge precedence by extracting patterns only from completed, certified productions.
- Honors consistency override by rejecting patterns that conflict with the constitutional hierarchy.
- Honors traceability by recording provenance for every pattern.
- Honors governance by proposing promotions rather than declaring constraints.

9. Cross-References

- GWS-013 — Learning Workflow
- GWS-012 — Governance Workflow
- GAS-028 — Feedback Learning Agent
- GFS-005 — Agent Constitution
- GFS-007 — Governance Constitution