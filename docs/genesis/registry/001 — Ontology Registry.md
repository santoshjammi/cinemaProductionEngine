Genesis Registry (GREG)
GREG-001 — Ontology Registry

Document ID: GREG-001
Title: Ontology Registry
Version: 1.0.0
Status: Registry
Authority: Derived from GFS-000, GFS-009, GO-001

1. Purpose

The Ontology Registry is the authoritative catalog of every registered ontology in Genesis. An ontology that is not registered here does not exist constitutionally. Agents may not reference unregistered ontologies; validators may not load SHACL from unregistered ontologies; the PKG may not contain instances of unregistered concepts.

The registry is the single source of truth for ontology IDs, versions, owners, statuses, parents, and SHACL artifact paths. It is updated only through the Ontology Derivation Pattern (GP-ONT-001) and the Ontology Versioning Pattern (GP-ONT-002).

2. Registry Schema

Each entry contains:

- Ontology ID — GO-NNN, permanent.
- Title — human-readable name.
- Version — current Semantic Version (see GP-ONT-002).
- Owner — agent role accountable for the ontology.
- Status — Proposed / Reviewed / Validated / Approved / Published / Deprecated / Sunset / Archived.
- Parent — the ontology this one extends (GO-001 for first-tier domain ontologies; a domain ontology for vertical extensions).
- Derivation Date — when the ontology was first registered.
- SHACL Path — path under schemas/ to the SHACL shapes.
- Migration Record — for MAJOR bumps, path to the ADR under decisions/.

3. Registry Update Rules

- An entry may be added only by the Ontology Derivation Pattern's registration step.
- A version may be bumped only by the Ontology Versioning Pattern.
- A status may transition only along the lifecycle defined in GO-001 §20.
- An Ontology ID is permanent. Reuse of an archived ID is forbidden.
- Every Published ontology must have a SHACL path. An ontology without SHACL is not Published.

4. Core Ontologies

| ID | Title | Version | Status | Parent | Owner |
|----|-------|---------|--------|--------|-------|
| GO-001 | Genesis Core Ontology | 1.0.0 | Published | — | Chief Architect |
| GO-002 | Genesis Semantic Relationship Catalog | 1.0.0 | Published | GO-001 | Chief Architect |
| GO-003 | Knowledge Classification Ontology | 1.0.0 | Published | GO-001 | Governance Agent |
| GO-004 | Evidence & Provenance Ontology | 1.0.0 | Published | GO-001 | Governance Agent |
| GO-005 | Confidence & Uncertainty Ontology | 1.0.0 | Published | GO-001 | Reasoning Engine |
| GO-006 | Lifecycle & State Ontology | 1.0.0 | Published | GO-001 | Governance Agent |

5. Domain Ontologies — Identity & Knowledge

| ID | Title | Version | Status | Parent | Owner |
|----|-------|---------|--------|--------|-------|
| GO-101 | Narrative Ontology | 1.3.0 | Published | GO-001 | Story Architect |
| GO-102 | Plot & Structure Ontology | 1.1.0 | Published | GO-101 | Story Architect |
| GO-103 | Human Psychology & Behavior Ontology | 1.2.0 | Published | GO-001 | Psychology Reviewer |
| GO-104 | Character Ontology | 1.3.0 | Published | GO-001 | Character Manager |
| GO-105 | World & Environment Ontology | 1.2.0 | Published | GO-001 | Environment Manager |
| GO-106 | Event, Action & Causality Ontology | 1.1.0 | Published | GO-001 | Story Architect |
| GO-107 | Knowledge, Information & Revelation Ontology | 1.0.0 | Published | GO-001 | Discovery Agent |
| GO-108 | Theme & Motif Ontology | 1.0.0 | Published | GO-101 | Story Architect |
| GO-109 | Emotional Arc Ontology | 1.0.0 | Published | GO-101 | Psychology Reviewer |
| GO-110 | Conflict Ontology | 1.0.0 | Published | GO-101 | Story Architect |

6. Domain Ontologies — Experience & Execution

| ID | Title | Version | Status | Parent | Owner |
|----|-------|---------|--------|--------|-------|
| GO-111 | Audience Experience Ontology | 1.0.0 | Published | GO-001 | Discovery Agent |
| GO-112 | Tone & Style Ontology | 1.0.0 | Published | GO-001 | Story Architect |
| GO-113 | Pacing & Rhythm Ontology | 1.0.0 | Published | GO-101 | Story Architect |
| GO-114 | Symbolism & Metaphor Ontology | 1.0.0 | Published | GO-101 | Story Architect |
| GO-115 | Staging & Blocking Ontology | 1.0.0 | Published | GO-105 | Scene Planner |
| GO-116 | Shot & Camera Intent Ontology | 1.0.0 | Published | GO-115 | Shot Planner |
| GO-117 | Sound & Music Intent Ontology | 1.0.0 | Published | GO-101 | Music Composer |
| GO-118 | Asset Specification Ontology | 1.0.0 | Published | GO-001 | Production Orchestrator |
| GO-119 | Production Knowledge Package Ontology | 1.0.0 | Published | GO-001 | Publisher |

7. Vertical Extensions

| ID | Title | Version | Status | Parent | Owner |
|----|-------|---------|--------|--------|-------|
| GO-201 | Psychological Cinema Ontology | 0.9.0 | Validated | GO-101 | Story Architect |
| GO-202 | Devotional Storytelling Ontology | 1.0.0 | Published | GO-101 | Devotional Coherence Validator |
| GO-203 | Documentary Ontology | 1.0.0 | Published | GO-101 | Archival Research Agent |
| GO-204 | Educational Narrative Ontology | 0.8.0 | Reviewed | GO-101 | Story Architect |
| GO-205 | Children's Storytelling Ontology | 1.0.0 | Published | GO-101 | Story Architect |
| GO-206 | Interactive Narrative Ontology | 0.7.0 | Proposed | GO-101 | Story Architect |

8. Deprecated and Archived

| ID | Title | Last Version | Status | Replacement | Sunset Date |
|----|-------|--------------|--------|-------------|--------------|
| (none currently) | — | — | — | — | — |

9. Audit

The registry is auditable: every add, version bump, and status transition is recorded with a timestamp, the acting agent, and the approving Governance Agent. The audit log is part of the PKG.

10. Anti-Patterns

- Referencing an ontology ID not in this registry.
- Consuming an ontology with status below Published (without governance approval for Candidate use).
- Reusing an archived ID.
- Bumping a version without updating this registry.
- Publishing an ontology without a SHACL path.

11. Exit Criteria

The registry is complete when:

- Every ontology in the genesis/ontology/ tree has a registry entry.
- Every Published ontology has a SHACL path.
- Every MAJOR bump has a Migration Record reference.
- Every Deprecated ontology has a replacement and a sunset date.