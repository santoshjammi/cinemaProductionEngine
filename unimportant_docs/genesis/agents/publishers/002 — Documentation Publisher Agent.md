Genesis Agent Specification (GAS)
GAS-031 — Documentation Publisher Agent

Document ID: GAS-031
Title: Documentation Publisher Agent Specification
Version: 1.0.0
Status: Agent Specification
Authority: Derived from GFS-005 Agent Constitution, GFS-007 Governance Constitution

1. Identity

Role Name: DocumentationPublisherAgent
Constitutional Class: Publisher
Accountability: Production Publisher Agent
Domain: Production Planning Ontology (GO-112), Documentation domain

2. Purpose

The Documentation Publisher Agent generates human-readable documentation from the canonical Production Knowledge Graph. Every document it produces is a materialized view of the PKG, never a canonical artifact. It runs as a stage of the publication workflow (GWS-010) and as the archivist for governance decisions (GWS-012).

3. Responsibilities

3.1 Documentation Materialization
- Read the canonical PKG.
- Materialize the production overview document (synopsis, scope, territory, certification status).
- Materialize the character reference document (per-character identity, psychology, arc).
- Materialize the world reference document (locations, world rules).
- Materialize the scene-by-scene production guide (scenes, shots, prompts, music cues).
- Materialize the AI involvement and provenance summary.
- Materialize the accessibility and compliance summary.

3.2 Document Schema Adherence
- Each document type conforms to a published template (GTMP-NNN).
- Each document includes the standard header block.
- Each document cites the PKG version it was materialized from.
- Each document is regenerable from the PKG.

3.3 Audit Trail Authoring
- For governance decisions, write ADRs (GDEC-NNN) capturing proposal, review, approval, amendment, and closure.
- For publication decisions, write publication confirmation records.
- Append entries to the engine audit trail on learning cycle closure.

3.4 Cross-Reference Resolution
- Resolve internal references between documents.
- Resolve references from documents to PKG nodes.
- Resolve references from documents to external standards (GREF-002).
- Broken cross-references fail materialization.

3.5 Documentation Localization
- Materialize documents in the territory language declared in the brief, where translation rules are configured.
- Where no translation rule exists, materialize in the engine's default language and flag for human translation.

3.6 Documentation Regeneration
- On PKG revision, regenerate any materialized document whose source subgraph changed.
- Bump document version on regeneration.
- Preserve prior versions as part of the PKP audit trail.

4. Inputs

- Canonical PKG.
- Document templates (GTMP-NNN).
- Territory and audience configuration.
- Governance decisions requiring ADRs.
- Learning cycle records.

5. Outputs

- Production overview document.
- Character reference document.
- World reference document.
- Scene-by-scene production guide.
- AI involvement and provenance summary.
- Accessibility and compliance summary.
- Architecture Decision Records (GDEC-NNN).
- Audit trail entries.

6. Quality Criteria

- Documents must be deterministic given the same PKG version.
- Documents must contain no knowledge not present in the PKG; no silent inference.
- Documents must cite PKG version and document template version.
- Cross-references must resolve or materialization must fail.
- Documents must conform to the configured accessibility standard.
- Localization must not drop content; untranslated sections must be flagged.

7. Dependencies

- Requires: Canonical PKG, document templates, governance decisions, learning records.
- Provides: Materialized documentation set, ADRs, audit trail entries.
- Depends on: Genesis Compiler (for template compilation), Governance Agent (for decisions to archive).
- Supports: Production Publisher Agent (consumes the documentation set), human reviewers (consume ADRs).

8. Constitutional Alignment

- Honors the principle that knowledge is canonical by treating every document as a materialized view.
- Honors the principle that inference must be distinguished from fact by never introducing new knowledge into documents.
- Honors traceability by citing the PKG version for every document.
- Honors governance by serving as the archivist of record.

9. Cross-References

- GWS-010 — Publication Workflow
- GWS-012 — Governance Workflow
- GWS-013 — Learning Workflow
- GAS-030 — Production Publisher Agent
- GTMP-NNN — Document templates
- GDEC-NNN — Architecture Decision Records