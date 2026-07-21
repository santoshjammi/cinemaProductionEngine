Genesis Pattern (GP)
GP-VAL-001 — Structural Validation Pattern

Document ID: GP-VAL-001
Title: Structural Validation Pattern
Version: 1.0.0
Status: Pattern
Authority: Derived from GFS-000, GFS-004, GO-001

1. Purpose

The Structural Validation Pattern defines how Genesis verifies that a PKG subgraph conforms to the shape constraints declared by the ontologies it references. Structural validation is the first and strictest validation layer: a subgraph that fails structural validation may not be merged into the live PKG, may not be read by downstream agents, and may not be materialized into any artifact.

In Genesis, structural validation is deductive (see GP-REAS-001). It applies ontology cardinalities, inheritance constraints, and relationship directionality as hard rules. A structural failure is never a warning — it is a hard defect that triggers the Revision Agent.

2. When to Apply

Apply this pattern when:

- An agent emits a new PKG subgraph and the merge step must decide whether to accept.
- A workflow stage boundary requires a validation gate.
- An ontology version bump requires re-validation of existing PKG instances.
- A revision loop completes and the revised subgraph must be re-checked.
- A Production Knowledge Package is being assembled and each member subgraph must be structurally sound.

Do not apply this pattern for semantic plausibility (use GP-VAL-002 Semantic Validation) or for completeness against the production brief (use GP-VAL-003 Completeness Validation).

3. Validation Scope

Structural validation checks:

- Concept typing — every node is an instance of a registered ontology concept.
- Inheritance — every node satisfies the constraints of its concept's ancestors.
- Cardinality — every relationship satisfies the declared cardinality (1:1, 1:N, N:M, minimum, maximum).
- Directionality — every relationship points in the declared subject → object direction.
- Predicate registration — every edge uses a predicate from GO-002.
- Required fields — every concept's mandatory attributes are present.
- Uniqueness — identifiers declared unique are unique within the subgraph.
- Reference integrity — every edge target resolves to a node that exists or is declared in the same merge set.

Structural validation does NOT check semantic plausibility, narrative coherence, or completeness against intent.

4. Validation Engine

The Structural Validation Agent runs SHACL shapes compiled from the registered ontologies. Each ontology produces a SHACL shape file under schemas/ at publication time. The agent loads the shapes for every concept referenced in the subgraph and runs a single validation pass.

Validation output is a Validation Report — a typed PKG artifact with:

- Subject — the subgraph validated.
- Shapes evaluated — list of SHACL shape IDs.
- Results — per shape: passed / failed / not applicable.
- Failures — per failure: the shape, the violating node, the violating edge, and the expected constraint.
- Verdict — PASS or FAIL.
- Provenance — link to the Decision Record that caused the subgraph to be produced.

5. Workflow

5.1 Identify Shapes

For every concept referenced in the subgraph, load the corresponding SHACL shape from schemas/. If a referenced concept has no SHACL shape, the subgraph is invalid by default — the ontology is incomplete.

5.2 Run Validation

Execute SHACL validation against the subgraph. Capture every violation with its shape, node, and edge.

5.3 Classify Failures

Each failure is classified:

- Cardinality violation — a relationship count is out of range.
- Type violation — a node is not an instance of its declared concept.
- Direction violation — an edge points the wrong way.
- Predicate violation — an edge uses an unregistered predicate.
- Reference violation — an edge target does not resolve.
- Field violation — a required field is missing or ill-typed.

5.4 Emit Validation Report

Commit the Validation Report to the PKG. If verdict is PASS, the merge proceeds. If verdict is FAIL, the merge is blocked and the Revision Agent is dispatched.

5.5 Route to Revision

For each failure, the Revision Agent maps the failing shape to the responsible upstream agent using the workflow manifest. The revision request names the agent, the failing shape, and the violating node.

6. Use Inside Genesis

- Stage 2 → Stage 3 boundary: each Creative Design subgraph (Narrative, Character, World) is structurally validated before merge.
- Stage 3 → Stage 4 boundary: the Screenplay Document is structurally validated before Production Planning.
- Ontology version bump: every existing PKG instance is re-validated against the new SHACL shapes; failures trigger a Migration Record (see GP-ONT-002).
- Production Knowledge Package assembly: every member subgraph is structurally validated before packaging.

7. Worked Example

The Character Manager Agent emits a Character Subgraph containing:

- Character: Arjuna (typed GO-104-Character).
- Character: Arjuna → has_core_fear → Core Fear: Loss of mentor.
- Character: Arjuna → has_goal → Goal: Win the war.

SHACL shapes evaluated:

- Character → has_core_fear → exactly one Core Fear: PASS (one edge present).
- Character → has_goal → at least one Goal: PASS.
- Character → has_persona → at least one Persona: FAIL (no Persona edge).

Verdict: FAIL. Revision Agent dispatched to Character Manager Agent with the failing shape and the violating node.

8. Anti-Patterns

- Treating a structural failure as a warning and merging anyway.
- Validating only the changed nodes without re-checking inherited constraints.
- Letting the validator fix the defect — validators emit reports, not patches.
- Running structural validation before the ontology is registered — unregistered ontologies have no SHACL.
- Accepting a subgraph whose referenced concepts have no SHACL shapes — the ontology is incomplete.
- Using semantic plausibility as a substitute for structural validation — they are different layers.

9. Exit Criteria

Structural validation is complete when:

- Every referenced concept has a loaded SHACL shape.
- Validation has run against the full subgraph.
- Every failure is classified and recorded.
- The Validation Report is committed to the PKG.
- For PASS, the merge proceeds.
- For FAIL, the Revision Agent has been dispatched with the failing shapes and responsible agents named.