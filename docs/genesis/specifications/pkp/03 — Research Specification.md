Genesis Foundational Standards (GFS)
PKP-03 — Research Specification

Document ID: PKP-03
Title: Research Specification
Version: 1.0.0
Status: Pre-Production Specification
Authority: Derived from GFS-000 Constitutional Charter

1. Purpose

The Research Specification captures the factual knowledge required to make the
production credible, coherent, and defensible. It is the evidentiary foundation
on which the Story, World, and Character specifications rest.

Per the Constitutional Charter (GFS-000, Sixth Principle), inference must be
distinguished from fact. This specification enforces that distinction by
classifying every research item by source credibility, evidence strength, and
confidence level before it may be referenced by any downstream specification.

2. Scope

This specification defines:
- Domains of factual knowledge required by the production
- Specific research items within each domain
- Source credibility and evidence strength classifications
- Identified research gaps and their resolution plans
- Reference works the production depends on
- The line between established fact, expert consensus, and creative assumption

Out of scope: how the research is dramatized (that lives in the Story
Specification, PKP-04), and how the world is constructed from research (that
lives in the World Specification, PKP-05).

3. Contents

3.1 Research Domains
The factual fields the production depends on — psychology, history, science,
culture, architecture, geography, technology, law, medicine, or other. Each
domain is declared with the depth of knowledge required.

3.2 Research Items
Specific claims, facts, or bodies of knowledge the production relies on. Each
item is classified by source credibility, evidence strength, and confidence.

3.3 Source Credibility
A four-tier classification: PRIMARY (peer-reviewed, official records, original
documents), SECONDARY (reputable synthesis, expert commentary), TERTIARY
(encyclopedic, journalistic), CLAIM (unverified, anecdotal, contested).

3.4 Evidence Strength
A three-tier classification: ESTABLISHED (consensus), SUPPORTED (majority
evidence), CONTESTED (active disagreement), UNVERIFIED (single source).

3.5 Research Gaps
Knowledge the production requires but does not yet possess. Each gap is
declared with a resolution plan (research task, expert consultation, or
creative assumption with documented risk).

3.6 Reference Works
The specific works the production cites or depends on. Each reference is
declared with a citation and a relevance note.

3.7 In-World vs. Real-World Distinction
Each research item is tagged as REAL_WORLD (governs credibility), IN_WORLD
(governs the fictional world's internal consistency), or BOTH.

4. Inputs

- Project Specification (PKP-02)
- Vision Specification (PKP-00)
- Creative Strategy Specification (PKP-01)
- Original synopsis

5. Outputs

- A validated Research record in the Production Knowledge Graph
- A materialized Research Specification document
- A library of research items, each with provenance, that downstream
  specifications may cite

6. Schema

```yaml
research:
  document_id: PKP-03
  version: 1.0.0
  domains:
    - name: <string>
      depth: <shallow|working|expert>
      justification: <string>
  items:
    - id: <string>
      domain: <string>
      claim: <string>
      source_credibility: <PRIMARY|SECONDARY|TERTIARY|CLAIM>
      evidence_strength: <ESTABLISHED|SUPPORTED|CONTESTED|UNVERIFIED>
      confidence: <EXPLICIT|INFERRED|CONFIRMED|ASSUMED|UNKNOWN>
      scope: <REAL_WORLD|IN_WORLD|BOTH>
      references: [<reference id>]
      notes: <string>
  gaps:
    - id: <string>
      description: <string>
      domain: <string>
      resolution_plan: <string>
      risk_if_unresolved: <string>
      owner: <string>
  references:
    - id: <string>
      citation: <string>
      type: <book|paper|archive|interview|document|other>
      relevance: <string>
  provenance:
    source_project: <reference>
    agent: <string>
    session: <string>
    confidence: <EXPLICIT|INFERRED|CONFIRMED|ASSUMED|UNKNOWN>
```

7. Required Fields

- domains (at least one entry)
- items (at least one entry per declared domain)
- For each item: id, domain, claim, source_credibility, evidence_strength,
  confidence, scope
- gaps (the field is required; may be empty if no gaps remain)
- references (at least one entry per item that references one)
- provenance.confidence

8. Optional Fields

- references.relevance (recommended, not required)
- gaps.owner
- notes on individual items

9. Validation Rules

- R-001: Every domain declared in `domains` must have at least one item in
  `items`.
- R-002: No item may have source_credibility CLAIM and evidence_strength
  ESTABLISHED simultaneously — these are mutually exclusive.
- R-003: Every item referenced by a downstream specification must exist in
  `items` with matching id.
- R-004: A gap with risk_if_unresolved set to "blocking" must have a
  resolution_plan; the production cannot be certified ready while blocking
  gaps remain unresolved.
- R-005: scope=BOTH items must declare how the real-world claim informs the
  in-world construction in the notes field.
- R-006: An item may not be cited by PKP-04, PKP-05, or PKP-06 unless its
  confidence is at least INFERRED.
- R-007: References must use a recognizable citation style (Chicago, APA, or
  inline URI).

10. Dependencies

- PKP-02 — Project Specification (hard)
- PKP-00 — Vision Specification (soft; informs which domains are required)
- PKP-01 — Creative Strategy Specification (soft; informs depth requirements)

11. Versioning

- MAJOR: Removal of a domain, removal of an item cited downstream, or
  downgrade of an item's confidence below INFERRED.
- MINOR: Addition of a domain, addition of items, or upgrade of confidence.
- PATCH: Wording or citation corrections that do not alter claims.

A MAJOR change to Research triggers revalidation of PKP-04, PKP-05, and
PKP-06, which cite research items.

12. Examples

```yaml
research:
  document_id: PKP-03
  version: 1.0.0
  domains:
    - name: "Clinical psychology"
      depth: "working"
      justification: "Protagonist is a physician; credibility requires working knowledge of diagnostic reasoning."
    - name: "Urban geography"
      depth: "shallow"
      justification: "Single-city setting; requires verifiable district references."
  items:
    - id: "RES-001"
      domain: "Clinical psychology"
      claim: "Diagnostic uncertainty is a recognized source of clinician distress."
      source_credibility: "PRIMARY"
      evidence_strength: "SUPPORTED"
      confidence: "CONFIRMED"
      scope: "BOTH"
      references: ["REF-001"]
      notes: "Real-world finding informs protagonist's internal arc and in-world dialogue."
    - id: "RES-002"
      domain: "Urban geography"
      claim: "The hospital district is served by a single night-route tram line."
      source_credibility: "TERTIARY"
      evidence_strength: "SUPPORTED"
      confidence: "CONFIRMED"
      scope: "IN_WORLD"
      references: ["REF-002"]
      notes: "Fictionalized from real transit map; in-world only."
  gaps:
    - id: "GAP-001"
      description: "Specific procedure for the protagonist's diagnostic method."
      domain: "Clinical psychology"
      resolution_plan: "Consultation with retired diagnostician; fallback to documented case study."
      risk_if_unresolved: "blocking"
      owner: "ResearchAgent"
  references:
    - id: "REF-001"
      citation: "Croskerry, P. (2003). The importance of cognitive errors in diagnosis."
      type: "paper"
      relevance: "Establishes diagnostic uncertainty as a documented phenomenon."
    - id: "REF-002"
      citation: "Municipal Transit Authority map, 2024 edition."
      type: "document"
      relevance: "Source for in-world transit logic."
  provenance:
    source_project: "PKP-02 v1.0.0"
    agent: "ResearchAgent"
    session: "sess-002"
    confidence: "CONFIRMED"
```

13. Future Extensibility

- A field for expert consultation records (interview transcripts, signed
  reviews) may be added when expert review becomes a first-class workflow.
- A field for evidence URL archiving (to prevent link rot) may be added in a
  MINOR version.
- A field for cross-production research lineage (shared research libraries
  across a series) will be modeled as Knowledge Graph edges.