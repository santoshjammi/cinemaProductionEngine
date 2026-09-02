Genesis Documentation (GDOC)
GDOC-001 — Generated Documentation Guide

Document ID: GDOC-001
Title: Generated Documentation Guide
Version: 1.0.0
Status: Active
Authority: Derived from GFS-000

1. Purpose

Explains how generated documentation works inside Genesis: what gets
generated, from what source, in what format, and how it stays in sync with the
canonical Production Knowledge Graph (PKG).

2. Principle

Files are not canonical. The PKG is canonical. Every generated document is a
materialized view of the PKG at a point in time. Generated docs carry a
header marking them as derived and recording the PKG version and generation
timestamp.

3. What Gets Generated

### From a PKG

| Output | Source | Format | Generator |
|--------|--------|--------|-----------|
| Production Brief (rendered) | PKG brief node | Markdown | GGEN-001 docs |
| Character Sheet | Character DNA nodes | Markdown per character | GGEN-001 docs |
| Scene Breakdown | Scene specification nodes | Markdown per scene | GGEN-001 docs |
| World Bible | World knowledge nodes | Markdown | GGEN-001 docs |
| Narrative Outline | Narrative nodes | Markdown | GGEN-001 docs |
| Handoff Manifest | PKG manifest | JSON | GGEN-001 docs |
| Production Readiness Certificate | Certificate node | JSON + Markdown | GGEN-001 docs |

### From an Ontology

| Output | Source | Format | Generator |
|--------|--------|--------|-----------|
| Ontology Reference Doc | GO-NNN ontology | Markdown | GGEN-001 docs |
| Class Diagram | GO-NNN ontology | Mermaid | GGEN-001 docs |
| Pydantic Models | GO-NNN ontology | Python | GGEN-001 pydantic |
| JSON Schema | GO-NNN ontology | JSON | GGEN-001 schema |

### From a Specification

| Output | Source | Format | Generator |
|--------|--------|--------|-----------|
| Spec Reference Doc | GSPEC-NNN | Markdown | GGEN-001 docs |
| Spec JSON Schema | GSPEC-NNN | JSON | GGEN-001 schema |

4. Header Convention

Every generated file begins with:

```
<!-- GENERATED. DO NOT EDIT BY HAND. -->
<!-- Source: <PKG id or ontology id> -->
<!-- Generator: GGEN-001 <version> -->
<!-- Generated at: <ISO 8601> -->
<!-- Source hash: <sha256> -->
```

For JSON files, the same fields appear in a `$comment` block.

5. Format Rules

- Markdown: GitHub-flavored, max 120 chars per line, one H1 per file.
- JSON: 2-space indent, sorted keys, UTF-8.
- Mermaid: class diagrams for ontologies, flowcharts for workflows.
- Python: Black-formatted, type-annotated, with a module docstring pointing to the source ontology.

6. Synchronization

- Generated docs are never edited by hand.
- A pre-commit hook (`tooling/scripts/validate-all.sh`) flags generated docs whose source hash no longer matches.
- Regeneration is triggered by `genesis generate --kind docs`.
- The PKG manifest records the generator version and source hash for every generated artifact.

7. Storage

- Generated docs live in `dist/docs/` by default, never in `docs/` (which is for hand-authored guides).
- The `--output <dir>` flag controls destination.
- Generated docs are not committed to the repository except for tagged releases.

8. Drift Detection

- The compiler (GCMP-001) writes a manifest of source hashes.
- The docs generator (GGEN-001) writes a manifest of generated hashes.
- Drift = source hash changed but generated hash unchanged.
- Drift is reported as a Warn-severity validation result.

9. Dependencies

- Compiler: GCMP-001
- Generators: GGEN-001
- Validator: GVAL-001 (drift detection)
- CLI: GTOOL-001 (`genesis generate --kind docs`)