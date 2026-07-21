Genesis Pattern (GP)
GP-DESIGN-001 — Knowledge-First Design Pattern

Document ID: GP-DESIGN-001
Title: Knowledge-First Design Pattern
Version: 1.0.0
Status: Pattern
Authority: Derived from GFS-000, GFS-001, GO-001

1. Purpose

The Knowledge-First Design Pattern defines how Genesis components are designed around knowledge before they are designed around behavior, prompts, or artifacts. Every other concern — the agent's prompt, the output document, the workflow stage, the downstream contract — follows from the structure of the knowledge the component must produce.

In Genesis, knowledge is canonical and files are materialized views (Charter, Fifth Principle). Designing a component to produce a file first inverts that order and produces brittle artifacts whose knowledge is implicit. Designing knowledge first produces artifacts whose meaning survives changes in format, model, and renderer.

2. When to Apply

Apply this pattern when:

- Designing a new agent — define the PKG subgraph it produces before writing its prompt.
- Designing a new workflow stage — define the knowledge state at entry and exit before choosing agents.
- Designing a new ontology extension — define the concepts before the SHACL shapes.
- Designing a new pipeline — define the knowledge milestones before the orchestration.
- Refactoring an agent whose output is file-shaped rather than knowledge-shaped.

Do not apply this pattern to pure infrastructure (logging, serialization) where knowledge structure is not the concern.

3. Design Order

Knowledge-First design follows a strict order:

1. Identify the decision the component must support.
2. Identify the PKG subgraph that decision requires.
3. Identify the ontology concepts that subgraph uses.
4. Identify the relationships (GO-002 predicates) the subgraph asserts.
5. Identify the evidence and confidence the subgraph requires.
6. Identify the validation rules (SHACL) the subgraph must satisfy.
7. Only then design the prompt, the workflow stage, and the output artifact.

Steps 1–6 are knowledge design. Step 7 is artifact design. Reversing the order is the defining anti-pattern of this pattern.

4. Knowledge Contract

Every component declares a Knowledge Contract with:

- Output subgraph — the typed PKG nodes and edges the component produces.
- Input subgraph — the typed PKG nodes and edges the component consumes.
- Concepts used — the ontology concept IDs (GO-NNN-CCC) referenced.
- Predicates used — the GO-002 relationship IDs referenced.
- Evidence requirements — minimum evidence class (Explicit / Inferred / Confirmed / Assumed) for each produced node.
- Confidence floor — the minimum confidence the component must achieve for each produced node.
- Validation shapes — the SHACL shapes the output must satisfy.

The Knowledge Contract is committed before the prompt. The prompt is derived from the contract, not the other way around.

5. Workflow

5.1 State the Decision

Express the decision the component must support in one sentence using only registered vocabulary. Example: "The Story Architect Agent decides the central conflict and the irreversible moment of the production."

5.2 Sketch the Subgraph

Sketch the nodes and edges the decision produces. Example: Production → has_conflict → Conflict; Conflict → has_irreversible_moment → Event.

5.3 Bind to Ontology

For every node, name the ontology concept. For every edge, name the GO-002 predicate. If a concept or predicate is missing, raise an ontology extension request — do not invent vocabulary.

5.4 Declare Evidence and Confidence

For every produced node, declare the evidence class required and the confidence floor. A node without an evidence requirement defaults to Assumed, which is rarely acceptable.

5.5 Declare Validation

For every relationship cardinality and inheritance constraint, declare the SHACL shape the output must satisfy. The component is not designed until it is machine-validatable.

5.6 Derive the Prompt

Only after the Knowledge Contract is committed, write the prompt or workflow stage that produces the subgraph. The prompt must reference the contract; it must not invent new vocabulary or new relationships.

5.7 Validate the Output

Run the component and validate the output against the SHACL shapes. If validation fails, the defect is in the prompt or the contract — not in the validator.

6. Use Inside Genesis

- Story Architect Agent — the Narrative Subgraph is designed before the Story Architect prompt.
- Character Manager Agent — the Character Subgraph is designed before the character reasoning prompt.
- Screenplay Writer Agent — the Screenplay Document's knowledge representation (Scene, Beat, Dialogue, Action) is designed before the screenplay prompt.
- Production Readiness Certificate — the certificate's knowledge structure (readiness dimensions, evidence, sign-off) is designed before the certificate template.

7. Worked Example

Designing the Story Architect Agent:

1. Decision: select central conflict and irreversible moment.
2. Subgraph: Production → has_conflict → Conflict; Conflict → has_irreversible_moment → Event; Conflict → opposes → Theme; Conflict → drives → Character.
3. Concepts: Conflict (GO-101), Event (GO-106), Theme (GO-101), Character (GO-104).
4. Predicates: has_conflict, has_irreversible_moment, opposes, drives (all from GO-002).
5. Evidence: Conflict must be Inferred with confidence ≥ 0.7; irreversible_moment must be Inferred with confidence ≥ 0.8.
6. Validation: Production → has_conflict → exactly one Conflict; Conflict → has_irreversible_moment → exactly one Event.
7. Prompt: derived to elicit the above; references the contract; uses no vocabulary outside GO-101 / GO-104 / GO-106.

8. Anti-Patterns

- Writing the prompt first and reverse-engineering the knowledge structure.
- Designing an output document before the PKG subgraph it materializes.
- Using vocabulary in the prompt that is not in any registered ontology.
- Declaring a Knowledge Contract with no validation shapes — unvalidated knowledge is not knowledge.
- Treating confidence as an afterthought — confidence is part of the contract.
- Producing a file as the canonical output — files are materialized views of knowledge.

9. Exit Criteria

Knowledge-First design is complete when:

- The Knowledge Contract is committed.
- Every node and edge references registered vocabulary.
- Every produced node has an evidence class and confidence floor.
- SHACL shapes are committed under schemas/.
- The prompt references the contract and uses no unregistered vocabulary.
- A representative output passes SHACL validation.