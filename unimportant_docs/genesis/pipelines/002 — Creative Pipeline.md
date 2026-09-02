Genesis Pipeline (GPIPE)
GPIPE-002 — Creative Pipeline

Document ID: GPIPE-002
Title: Creative Pipeline
Version: 1.0.0
Status: Pipeline
Authority: Derived from GFS-000, GFS-002, GWS-001

1. Purpose

The Creative Pipeline defines the canonical sequence by which Genesis transforms the Production Brief into the Creative Knowledge Subgraph — the narrative, character, and world knowledge required to write a screenplay. Creative work is reasoning work in Genesis: every creative decision is an abductive or inductive conclusion with provenance, evidence, and confidence.

In Genesis, creativity is not magic. The Charter's Third Principle declares reasoning precedes decision. The Creative Pipeline applies the Reasoning Patterns (GP-REAS-001/002/003) to produce knowledge, not opinions.

2. Inputs

- Production Brief (from GPIPE-001).
- Research findings (from the Research Agent, if dispatched).
- Registered ontologies: GO-101 Narrative, GO-104 Character, GO-105 World, GO-106 Event.
- Reasoning Catalog rules applicable to creative design.

3. Outputs

- Narrative Subgraph — theme, central conflict, plot, acts, sequences, scenes, beats, irreversible moment, resolution.
- Character Subgraph — protagonist, antagonist, supporting cast, motivations, fears, goals, transformations, relationships.
- World Subgraph — environments, locations, rules, resources, history, time, constraints.
- Creative Decision Records — every creative decision with provenance, alternatives considered, and confidence.
- Validation Reports — structural, semantic, and completeness validations of each subgraph.

4. Stages

4.1 Creative Design Fan-Out

The Story Architect Agent, Character Manager Agent, and Environment Manager Agent run in parallel (GP-WF-002). Each takes the Production Brief as a read-only snapshot and produces its subgraph into a staging buffer. Independence is verified before fan-out — no subgraph writes to another's nodes.

4.2 Merge

The Production Orchestrator merges the three subgraphs. Cross-references (Scene references Character, Character references World) are created post-merge by the Production Orchestrator. Conflicts are detected and routed per GP-WF-002 §5.5 — semantic conflicts escalate to the Governance Agent (GP-GOV-002).

4.3 Psychology Review

The Psychology Reviewer Agent runs semantic validation (GP-VAL-002) on the Character Subgraph using the character coherence rules from the Reasoning Catalog. Findings are routed to the Character Manager Agent for revision.

4.4 Narrative Coherence Review

The Story Coherence Validator runs semantic validation on the Narrative Subgraph. The irreversible moment, central conflict, and resolution are checked for plausibility given the Character Subgraph. Findings are routed to the Story Architect.

4.5 World Rule Review

The World Rule Validator runs semantic validation on the World Subgraph. Events placed in the world are checked against the world's declared rules. Findings are routed to the Environment Manager or, if the event belongs to the narrative, to the Story Architect.

4.6 Completeness Validation

The Completeness Validator runs GP-VAL-003 across all three subgraphs. Gaps trigger Gap Detected events; the responsible agent is dispatched. The pipeline does not advance until all three dimensions are Complete.

4.7 Creative Approval

The merged Creative Knowledge Subgraph is submitted to the approval chain: Story Architect → Character Manager → Environment Manager → Governance Agent. On approval, the subgraph is committed as the canonical creative foundation for the production.

5. Exit Criteria

The Creative Pipeline is complete when:

- Narrative, Character, and World Subgraphs are committed.
- All cross-references are created.
- All three subgraphs pass structural, semantic, and completeness validation.
- All conflicts are resolved (auto-resolved or governance-resolved).
- The Creative Approval chain is complete.
- The Creative Knowledge Subgraph is the authoritative input to the Production Pipeline (GPIPE-003).

6. Hand-off

The Creative Knowledge Subgraph is the input to the Production Pipeline. No element of the Production Pipeline may re-derive creative decisions — it must reference the Creative Knowledge Subgraph. This enforces the separation between creative reasoning and production planning.

7. Anti-Patterns

- Letting the Screenplay Writer re-derive character motivations during writing.
- Skipping psychology review because the Character Subgraph "looks fine."
- Merging subgraphs with unresolved semantic conflicts.
- Treating abductive creative decisions as Confirmed — they are Inferred until validation confirms.
- Running the three design agents sequentially when they are independent — wastes throughput.
- Advancing to the Production Pipeline with Weak creative elements unaccepted by governance.

8. Worked Example

Production Brief: a devotional drama about a monk seeking his lost sister.

Fan-out:
- Story Architect: central conflict = duty to monastery vs. love for sister; irreversible moment = leaving the monastery; resolution = finding the sister and choosing to return.
- Character Manager: protagonist = monk; Core Fear = spiritual failure; Goal = reunion; Transformation = from obedience to chosen devotion.
- Environment Manager: world = medieval Himalayan monastery; rule = silence at night; constraint = no leaving without abbot's blessing.

Merge: scenes reference characters; characters reference world rules. No conflicts.

Psychology review: Core Fear vs. Goal — coherent (PASS). Transformation plausibility — coherent (PASS).

Narrative coherence: irreversible moment aligns with central conflict (PASS).

World rule consistency: the protagonist leaves the monastery — this violates the "no leaving without abbot's blessing" rule. The Environment Manager adds a node: Abbot grants blessing. Conflict resolved.

Completeness: all three dimensions Complete. Approval chain signs. Hand-off to Production Pipeline.