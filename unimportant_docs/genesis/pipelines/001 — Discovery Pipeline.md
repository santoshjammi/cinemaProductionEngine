Genesis Pipeline (GPIPE)
GPIPE-001 — Discovery Pipeline

Document ID: GPIPE-001
Title: Discovery Pipeline
Version: 1.0.0
Status: Pipeline
Authority: Derived from GFS-000, GFS-001, GWS-001

1. Purpose

The Discovery Pipeline defines the canonical sequence by which Genesis transforms a raw creative input — a synopsis, a brief, an oral description — into a structured Production Brief with identified gaps. Discovery is the first pipeline of Genesis; every other pipeline assumes its output.

In Genesis, discovery is constitutional. The Charter's Second Principle declares discovery precedes specification. This pipeline operationalizes that principle: nothing is specified until it has been discovered, and nothing that has not been discovered may be referenced downstream.

2. Inputs

- Raw creative input — a synopsis, a brief, a recorded conversation, or a structured-but-incomplete statement of intent.
- Creator constraints — stated must-haves and must-not-haves (genre, audience, tone, length, territory, taboo topics).
- Reference set — optional corpus of reference productions the creator has named.
- Existing PKG state — empty for a new production; non-empty for a resumed session.

3. Outputs

- Production Brief — the structured statement of creative intent, parsed into PKG nodes typed against GO-001 Creative Intent Domain and the relevant domain ontologies.
- Gap List — the discovered missing elements that downstream pipelines must fill.
- Discovery Decision Records — every inference made during discovery, with provenance.
- Initial Confidence Map — per discovered element, the confidence assigned at discovery time.

4. Stages

4.1 Intake

The Production Brief Intake Agent receives the raw input and commits it verbatim to the PKG as an Explicit Knowledge Object. No interpretation happens at this stage; the raw text is preserved.

4.2 Parsing

The Brief Parser Agent parses the raw input against GO-001 Creative Intent Domain and the registered domain ontologies. Every parsed element is committed as an Explicit Knowledge Object with provenance to the source span in the raw input.

4.3 Gap Detection

The Discovery Agent runs completeness validation (GP-VAL-003) against the parsed Brief using the Required Element Sets from each dimension. Every Absent element is recorded as a Gap; every Weak element is flagged.

4.4 Clarification Planning

For every Gap, the Discovery Agent determines whether the answer can be inferred (abduction, GP-REAS-003), researched (Research Agent), or must be asked of the creator (Clarification Agent). Only gaps that materially affect downstream decisions are escalated to the creator; trivial gaps are inferred and flagged.

4.5 Clarification Loop

Clarification questions are dispatched to the creator. Answers are committed as Explicit Knowledge Objects. The loop runs until every material gap is resolved (filled, waived by governance, or marked Unknown with a governance decision record).

4.6 Brief Validation

The parsed Brief is structurally validated (GP-VAL-001), semantically validated (GP-VAL-002), and completeness-validated (GP-VAL-003). A Brief that fails any layer is returned to Parsing or Clarification.

4.7 Brief Approval

The Production Brief is submitted to the Ontology Publication-style approval chain: Brief Parser → Discovery Agent → Governance Agent. On approval, the Brief is committed as the canonical statement of intent for the production.

5. Exit Criteria

The Discovery Pipeline is complete when:

- Every parsed element is committed as an Explicit Knowledge Object with provenance.
- Every Gap is resolved (filled, waived, or explicitly Unknown with governance record).
- The Brief passes structural, semantic, and completeness validation.
- The Brief Approval chain is complete.
- The Production Brief is committed to the PKG as the authoritative input to the Creative Pipeline (GPIPE-002).

6. Hand-off

The Production Brief is the input to the Creative Pipeline. No element of the Creative Pipeline may reference the raw synopsis directly — it must reference the Brief. This enforces the Charter's Fifth Principle: knowledge is canonical, files are not.

7. Anti-Patterns

- Letting downstream pipelines read the raw synopsis instead of the Brief.
- Skipping clarification because the creator is unavailable — Unknown elements must be governance-waived, not silently inferred.
- Treating Inferred elements as Explicit — discovery classifies honestly.
- Filling gaps with creator-flavored assertions without provenance.
- Advancing to the Creative Pipeline with unresolved material gaps.

8. Worked Example

Input: "A story about a monk who leaves his monastery to find his lost sister."

Parsing: Protagonist = monk (Character, Explicit); Action = leaves monastery (Event, Explicit); Goal = find lost sister (Goal, Explicit); Relationship = sibling (Relationship, Explicit).

Gaps: Theme (Absent), Central Conflict (Absent), Antagonist (Absent), World (Absent), Audience (Absent), Tone (Absent), Territory (Absent).

Clarification: theme, conflict, antagonist, and audience are material — asked of creator. World and tone are inferrable — inferred by Discovery Agent with confidence 0.7, flagged Inferred.

Brief validated and approved. Hand-off to Creative Pipeline.