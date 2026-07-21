Genesis Manifest (GMF)
GMF-002 — Dependency Manifest

Document ID: GMF-002
Title: Dependency Manifest
Version: 1.0.0
Status: Manifest
Authority: Derived from GFS-000 §16

1. Purpose

This manifest lists every external dependency the Genesis Engine relies
on for its reference implementation. Genesis itself is
implementation-independent (GFS-000 §16); the dependencies here describe
one concrete way to build it, not the only way. Any dependency may be
replaced with a functionally equivalent alternative without violating
the constitution, provided the replacement respects the boundaries in
GFS-000 §15 (no media generation inside Genesis).

2. Dependency Categories

- D-1 Orchestration and state
- D-2 Data validation and schemas
- D-3 Storage and graph
- D-4 Embeddings and retrieval
- D-5 Media generation (downstream only)
- D-6 Audio and voice (downstream only)
- D-7 Audio post-production (downstream only)
- D-8 Packaging and serialization

3. D-1 Orchestration and State

Dependency: LangGraph
Purpose: Workflow orchestration for stateful, multi-step agent
  execution. Maps Genesis workflows (GWS-001+) to a runnable graph.
Used by: Production Orchestrator (GAS-026), Revision Agent (GAS-027),
  every workflow in L5.
Boundary: Used only inside L6 (Execution). Workflows in L5 are defined
  declaratively and are agnostic to the orchestrator runtime.
Replacement: any stateful graph executor with checkpoint and resume
  support (Temporal, Prefect with state, or a custom graph runner).
Version: pin to a MAJOR version; MINOR upgrades require a regression run.

4. D-2 Data Validation and Schemas

Dependency: Pydantic
Purpose: Runtime validation of node and edge property shapes against
  the ontology type constraints.
Used by: every agent that writes to the PKG; every validator that reads
  from the PKG.
Boundary: used to enforce GFS-010 §3 property schemas. Pydantic models
  are generated from ontology declarations, not hand-written.
Replacement: any schema validator with typed models and JSON export
  (msgspec, attrs + cattrs, dataclasses + jsonschema).
Version: pin to a MAJOR version.

5. D-3 Storage and Graph

Dependency: sqlite-vec
Purpose: Vector storage layer over SQLite for embedding-based retrieval
  of nodes and edges. Used for the discovery loop and for semantic
  queries (GKR-001 §10.2).
Used by: Research Agent (GAS-007), Story Architect (GAS-001) during
  discovery, every agent that performs semantic lookup.
Boundary: storage is an implementation detail of L3 (Knowledge). The
  PKG serialization is JSON-LD per GFS-010 §4 and is independent of the
  storage engine.
Replacement: any embedded vector index (FAISS, LanceDB, DuckDB +
  VSS). The replacement must support subgraph extraction and provenance
  queries.
Version: pin to a MINOR version; vector storage formats change often.

6. D-4 Embeddings and Retrieval

Dependency: sentence-transformers
Purpose: Compute embeddings for PKG nodes and edges to support
  semantic retrieval, similarity-based validation, and contradiction
  detection.
Used by: Research Agent (GAS-007), validators that perform similarity
  checks (GAS-019 Visual Consistency, GAS-022 Character Consistency).
Boundary: embeddings are a derived representation. The PKG is the
  source of truth; embeddings are a cache that may be rebuilt at any
  time.
Replacement: any sentence embedding model (OpenAI embeddings, Cohere,
  a local model). The replacement must be deterministic for a fixed
  model version.
Version: pin to a specific model; embedding drift is a defect.

7. D-5 Media Generation (Downstream Only)

Dependencies: ComfyUI, FLUX
Purpose: Image generation for storyboards, concept frames, and visual
  references. These are downstream of Genesis; they consume the PKP
  after Genesis certifies readiness.
Used by: Image Generator Agent (GAS-011). This agent operates at the
  boundary between Genesis and the Studio Engine. Inside Genesis, the
  agent only reads specifications and emits requests; the generation
  itself runs downstream.
Boundary: per GFS-000 §15, no media generation capability exists
  inside Genesis. The Image Generator Agent spec describes the
  contract; the runtime runs downstream.
Replacement: any image generation stack (Stable Diffusion, DALL-E,
  Midjourney via API). The replacement must accept the prompt format
  produced by the Prompt Builder (GAS-006).
Version: pin to a model checkpoint; image output is sensitive to
  model version.

8. D-6 Audio and Voice (Downstream Only)

Dependencies: EdgeTTS (and equivalent voice synthesis runtimes)
Purpose: Voice generation for dialogue scratch tracks and reference
  reads. Downstream of Genesis.
Used by: Voice Generator Agent (GAS-012). As with GAS-011, the agent
  inside Genesis only emits requests; synthesis runs downstream.
Boundary: same as D-5. No audio generation capability exists inside
  Genesis.
Replacement: any voice synthesis runtime (ElevenLabs, Coqui,
  Bark). The replacement must accept the voice profile produced by the
  Dialogue Writer (GAS-008) and the Character Manager (GAS-004).
Version: pin to a voice model version; voice identity must be stable
  across a production.

9. D-7 Audio Post-Production (Downstream Only)

Dependency: ffmpeg
Purpose: Audio mixing, format conversion, and subtitle muxing for
  downstream assembly. Downstream of Genesis.
Used by: Audio Mixing Agent (GAS-014), Video Composer Agent (GAS-015),
  Subtitle Agent (GAS-016). Inside Genesis these agents emit
  specifications; the runtime runs downstream.
Boundary: same as D-5. ffmpeg is a runtime tool, not a Genesis
  capability.
Replacement: any media processing pipeline that accepts the spec format
  produced by these agents.
Version: pin to a MAJOR version; MINOR upgrades require a regression
  run on sample productions.

10. D-8 Packaging and Serialization

Dependency: JSON-LD (and the `jsonld` library)
Purpose: Canonical serialization of the PKG (GFS-010 §4). The PKP is
  distributed as a JSON-LD document with the Genesis ontology context.
Used by: every component that serializes or deserializes the PKG.
Boundary: JSON-LD is the canonical format. Any internal
  representation (in-memory graph, SQLite rows) must round-trip
  through JSON-LD without loss.
Replacement: none. JSON-LD is constitutional for PKG distribution.
  Internal storage formats may vary.

11. Versioning Policy for Dependencies

- Every dependency is pinned to a version range.
- MAJOR version upgrades require a PR with a migration note.
- MINOR version upgrades require a regression run on the sample
  productions in `examples/`.
- PATCH upgrades are automatic if tests pass.
- Security patches are applied immediately and recorded in the
  CHANGELOG.

12. Boundary Reaffirmation

Dependencies D-5, D-6, and D-7 are downstream of Genesis. The agents
that reference them (GAS-011, GAS-012, GAS-013, GAS-014, GAS-015,
GAS-016, GAS-025) emit specifications and requests; they do not
generate media inside Genesis. This separation is absolute (GFS-000
§15). If a future runtime merges media generation into Genesis, it
violates the Charter and requires a constitutional amendment.

13. Compliance

Any replacement dependency must:

- Respect the PKG as the source of truth.
- Not require media generation inside Genesis.
- Preserve the JSON-LD canonical serialization.
- Preserve provenance and confidence on every node and edge.
- Support checkpoint and resume for long-running sessions.