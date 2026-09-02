Genesis References (GREF)
GREF-004 — External References

Document ID: GREF-004
Title: External References
Version: 1.0.0
Status: Reference
Authority: Derived from GFS-000

1. Purpose

This document catalogs external tools, libraries, and resources that Genesis may integrate with or recommend for downstream engines. Genesis itself is implementation-independent (per GFS-000 section 16), so these references are illustrative of capability classes, not mandatory dependencies. Any equivalent tool may be substituted provided it satisfies the relevant Genesis specification.

2. Knowledge and Reasoning

2.1 sqlite-vec
- Purpose: Vector storage and similarity search inside SQLite.
- Role in Genesis: Powers semantic retrieval over PKG nodes and embeddings of synopsis, character, and world knowledge.
- Why referenced: Lightweight, file-based, no external services; suitable for local-first deployment.

2.2 sentence-transformers
- Purpose: Produces sentence and paragraph embeddings.
- Role in Genesis: Generates embeddings for semantic search, clustering, and similarity checks between knowledge nodes.
- Why referenced: Standard open-source embedding library with consistent model interfaces.

2.3 Pydantic
- Purpose: Python data validation and settings management.
- Role in Genesis: Defines typed models for PKG payloads, agent I/O, and configuration.
- Why referenced: Pairs well with JSON Schema export for the GSS family.

2.4 LangGraph
- Purpose: Graph-based agent orchestration framework.
- Role in Genesis: Optional implementation substrate for the Production Orchestrator Agent and workflow execution (GWS-NNN).
- Why referenced: Aligns with Genesis' graph-first mental model; supports stateful, cyclic agent flows.

3. Media Generation (Downstream, Not Genesis)

These tools are referenced because Genesis builds the prompts and references that drive them, but the tools themselves run in the Studio Engine, not Genesis.

3.1 ComfyUI
- Purpose: Node-based image generation workflow engine.
- Role in Genesis: Consumes shot prompts and character references built by the Prompt Builder Agent.
- Why referenced: Industry standard for reproducible, node-graph image pipelines.

3.2 FLUX
- Purpose: Family of text-to-image diffusion models.
- Role in Genesis: A candidate renderer for the image generation stage downstream.
- Why referenced: High-quality open-weight image generation compatible with ComfyUI.

3.3 EdgeTTS
- Purpose: Text-to-speech synthesis.
- Role in Genesis: Consumes dialogue and narration scripts to produce voice audio downstream.
- Why referenced: Lightweight, free TTS suitable for prototype and production pipelines.

3.4 ffmpeg
- Purpose: Audio/video transcoding, muxing, and assembly.
- Role in Genesis: Used downstream for video composition, subtitle muxing, and format normalization.
- Why referenced: Universal media processing tool; effectively the lingua franca of media pipelines.

3.5 Whisper
- Purpose: Speech-to-text transcription.
- Role in Genesis: Generates subtitle tracks from synthesized voice audio downstream.
- Why referenced: Reliable open-source ASR with broad language support.

3.6 demucs / spleeter
- Purpose: Audio source separation.
- Role in Genesis: Optional downstream tool for isolating vocals and music for mixing.
- Why referenced: Useful for separating voice and score tracks before final mix.

4. Serialization and Validation

4.1 jsonschema
- Purpose: JSON Schema validator.
- Role in Genesis: Validates PKG payloads and API messages against GSS-NNN schemas.
- Why referenced: Reference implementation of the JSON Schema standard.

4.2 pySHACL
- Purpose: Python SHACL validator.
- Role in Genesis: Validates PKG nodes against shapes derived from Genesis ontologies.
- Why referenced: Bridges the GO ontology family and the GSS schema family with a standard validator.

4.3 rdflib
- Purpose: RDF graph library.
- Role in Genesis: Provides the in-memory graph model when SPARQL or OWL reasoning is required.
- Why referenced: Standard Python RDF toolkit; interoperates with JSON-LD and OWL serializations.

5. Packaging and Distribution

5.1 OCI registries (e.g., distribution/distribution)
- Purpose: Content-addressed artifact storage.
- Role in Genesis: Stores and versions PKP artifacts.
- Why referenced: Reuses container registry infrastructure for non-container artifacts.

5.2 BagIt (Library of Congress)
- Purpose: Archival packaging format.
- Role in Genesis: Optional archival packaging for certified PKPs.
- Why referenced: Standard for long-term digital preservation.

6. Documentation and Diagramming

6.1 Mermaid
- Purpose: Declarative diagram generation from text.
- Role in Genesis: Renders workflow, ontology, and agent interaction diagrams in documentation.
- Why referenced: Documentation as code; diagrams survive model and tool changes.

6.2 PlantUML
- Purpose: UML and component diagrams from text.
- Role in Genesis: Optional alternative to Mermaid for more formal UML views.
- Why referenced: Better fit for formal software architecture diagrams.

7. Orchestration and Compute

7.1 Prefect / Dagster / Airflow
- Purpose: Workflow orchestration engines.
- Role in Genesis: Optional execution backend for the Genesis workflow family (GWS-NNN).
- Why referenced: Demonstrate industry patterns Genesis aligns with rather than reinvents.

7.2 Celery / RQ
- Purpose: Distributed task queues.
- Role in Genesis: Optional backend for parallel agent dispatch in Stage 2 and Stage 5 of the Full Production Workflow.
- Why referenced: Decouples dispatch from execution; aligns with implementation-independence.

8. Evaluation and Measurement

8.1 prometheus-client
- Purpose: Metrics collection.
- Role in Genesis: Emits runtime metrics for agent execution, validation gates, and revision loops.
- Why referenced: Standard observability surface for production deployments.

8.2 OpenTelemetry
- Purpose: Distributed tracing.
- Role in Genesis: Traces agent invocations across the orchestrator and downstream services.
- Why referenced: Vendor-neutral trace standard.

9. Non-Recommendation Policy

Genesis specifications must never mandate a specific tool. They mandate capabilities. When a document references a tool by name, it does so as an example of a capability class. Any substitution must be documented in an ADR and verified against the relevant GSS schema and GWS workflow.

10. Cross-References

- GREF-002 — Standards Mapping
- GSS-NNN — Schema specifications
- GWS-NNN — Workflow specifications
- GDEC-NNN — Architecture Decision Records