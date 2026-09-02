Genesis References (GREF)
GREF-002 — Standards Mapping

Document ID: GREF-002
Title: Standards Mapping
Version: 1.0.0
Status: Reference
Authority: Derived from GFS-000

1. Purpose

This document maps Genesis Engine concepts, artifacts, and operations to external standards. The goal is to make Genesis knowledge portable, interoperable, and verifiable using industry-standard formats and tooling. Genesis does not depend on any single standard, but it aligns with standards where alignment increases clarity without sacrificing the constitutional principles.

2. Mapping Principles

- Genesis knowledge is canonical in the PKG; external standards are materialized views.
- A standard is adopted only when it increases portability or verifiability.
- No standard may override the Constitutional Charter.
- Where standards conflict, the Genesis internal specification prevails for internal use.
- Materialized views in external standards must always be regenerable from the PKG.

3. Knowledge Representation Standards

3.1 JSON-LD

- Used for: Serializing the PKG as a linked-data graph.
- Mapping: PKG nodes → JSON-LD nodes; PKG edges → JSON-LD properties with URIs.
- Context: A Genesis-specific @context document defines the vocabulary.
- Benefit: Enables web-scale linking of production knowledge without changing the canonical graph.

3.2 RDF / RDFS

- Used for: The semantic substrate beneath JSON-LD serialization.
- Mapping: Genesis classes → rdfs:Class; Genesis relationships → rdf:Property.
- Benefit: Allows standard SPARQL queries over the PKG.

3.3 OWL (Web Ontology Language)

- Used for: Expressing ontology axioms for the GO-NNN ontology family.
- Mapping: Genesis ontologies → OWL ontologies; constraints → OWL restrictions.
- Benefit: Enables reasoners to detect inconsistency and infer missing knowledge.

3.4 SHACL (Shapes Constraint Language)

- Used for: Validating PKG nodes against Genesis schemas (GSS-NNN).
- Mapping: GSS schemas → SHACL shapes; validation gates → SHACL validation reports.
- Benefit: Provides a standard, machine-checkable validation layer independent of custom code.

4. Interface Standards

4.1 OpenAPI

- Used for: Defining the Genesis Engine REST API surface.
- Mapping: Agent invocations → OpenAPI operations; PKG inputs/outputs → OpenAPI schemas.
- Benefit: Enables client generation, interactive docs, and contract testing.

4.2 GraphQL

- Used for: Read-only querying of the PKG by downstream engines and tooling.
- Mapping: Ontology domains → GraphQL types; relationships → GraphQL fields.
- Benefit: Allows downstream consumers to request exactly the slice of knowledge they need.

4.3 AsyncAPI

- Used for: Defining event streams for agent dispatch, progress, and completion.
- Mapping: Workflow stages → AsyncAPI channels; agent events → message schemas.
- Benefit: Standardizes event-driven integration with orchestration tooling.

5. Provenance and Trust Standards

5.1 W3C PROV

- Used for: Representing the provenance of every knowledge node and decision.
- Mapping: Genesis traceability records → PROV entities, activities, and agents.
- Benefit: Standard provenance model that survives changes in tooling.

5.2 ODRL (Open Digital Rights Language)

- Used for: Expressing rights and constraints on production knowledge and derived media.
- Mapping: Production constraints → ODRL policies; licensing terms → ODRL permissions.
- Benefit: Allows rights expressions to travel with the PKP.

6. Metadata Standards

6.1 Dublin Core

- Used for: Basic descriptive metadata on documents and materialized views.
- Mapping: Document title, creator, date, identifier → Dublin Core elements.
- Benefit: Universal discoverability in catalog systems.

6.2 schema.org

- Used for: Public-facing metadata on published productions.
- Mapping: Production → schema.org CreativeWork; episodes → schema.org Episode.
- Benefit: Search engine and platform discoverability.

7. Validation and Quality Standards

7.1 JSON Schema

- Used for: Structural validation of PKG payloads and API messages.
- Mapping: GSS schemas → JSON Schema definitions.
- Benefit: Ubiquitous tooling support and language-agnostic validation.

7.2 SOTDL / RuleML (optional)

- Used for: Expressing complex business rules that cannot be captured in SHACL alone.
- Mapping: Governance rules → rule language expressions.
- Benefit: Enables rule sharing and reasoning across engines.

8. Packaging and Distribution Standards

8.1 OCI Artifacts

- Used for: Packaging the PKP as a content-addressed artifact.
- Mapping: PKP → OCI artifact; layers → PKG, documents, certificate, manifests.
- Benefit: Reuse of registry infrastructure for distribution and versioning.

8.2 BagIt

- Used for: Archival packaging of certified PKPs.
- Mapping: PKP directory → BagIt bag; manifest → BagIt manifest.
- Benefit: Standard archival interchange with libraries and studios.

9. Workflow Standards

9.1 BPMN

- Used for: Visualizing Genesis workflows (GWS-NNN) for human review.
- Mapping: Workflow stages → BPMN tasks; revision loops → BPMN gateways.
- Benefit: Stakeholder-readable workflow diagrams.

9.2 W3C Workflow Standards

- Used for: Interop with external workflow engines where required.
- Mapping: Genesis workflow definitions → portable workflow descriptions.
- Benefit: Optional integration with enterprise scheduling tools.

10. Non-Adopted Standards (Intentional)

- Genesis does NOT adopt standards that conflict with knowledge-canonical principle:
  - File-first formats (e.g., plain DOCX as canonical) — files are materialized views.
  - Rendering-specific standards (e.g., USD as canonical) — rendering is downstream.
  - Prompt-first standards — prompts are derived artifacts, not canonical.

11. Versioning of Mappings

Each mapping is versioned alongside the Genesis specification it relates to. When an external standard releases a breaking change, the Genesis specification that depends on it must be amended through the governance workflow before the new version is adopted.

12. Cross-References

- GREF-001 — Genesis Glossary
- GSS-NNN — Schema specifications
- GO-NNN — Ontology specifications
- GSPEC-NNN — Format and protocol specifications