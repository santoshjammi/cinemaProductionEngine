Genesis Asset Registry (GAREG)
GAREG-001 — Asset Registry

Document ID: GAREG-001
Title: Asset Registry
Version: 1.0.0
Status: Active
Authority: Derived from GFS-000

1. Purpose

Catalogs the canonical reusable assets shipped with the Genesis Engine. These
assets are used by tests, examples, demos, and as starting points for new
productions. They are reference material, not production output.

2. Scope

- Lists every shipped fixture, sample, and reference asset.
- Does not list generated PKG artifacts (those are outputs, not assets).
- Does not list schemas or ontologies (those are listed in their own modules).

3. Asset Categories

### Sample Briefs

| Asset ID | Path | Description |
|----------|------|-------------|
| BRIEF-001 | `assets/briefs/night-he-stopped-reaching.yaml` | A complete Production Brief for "The Night He Stopped Reaching For Her" |
| BRIEF-002 | `assets/briefs/minimal-valid.yaml` | A minimal valid brief used by unit tests |
| BRIEF-003 | `assets/briefs/missing-character.yaml` | A brief with a missing character, used by completeness tests |

### Example Character DNAs

| Asset ID | Path | Description |
|----------|------|-------------|
| CHAR-001 | `assets/characters/ethan-morrison.json` | Full Character DNA for Ethan Morrison (BRIEF-001) |
| CHAR-002 | `assets/characters/lena-morrison.json` | Full Character DNA for Lena Morrison (BRIEF-001) |
| CHAR-003 | `assets/characters/minimal-valid.json` | Minimal valid Character DNA used by unit tests |

### Reference Style Guides

| Asset ID | Path | Description |
|----------|------|-------------|
| STYLE-001 | `assets/styles/cinematic-intimate.yaml` | Visual style guide for intimate domestic drama |
| STYLE-002 | `assets/styles/cinematic-noir.yaml` | Visual style guide for noir-influenced productions |
| STYLE-003 | `assets/styles/minimal-ambient.yaml` | Music and sound style guide for ambient minimal scores |

### Reference Synopses

| Asset ID | Path | Description |
|----------|------|-------------|
| SYN-001 | `assets/synopses/night-he-stopped-reaching.md` | Source synopsis for BRIEF-001 |
| SYN-002 | `assets/synopses/short-demo.md` | A short demo synopsis for smoke tests |

### Reference Constraints

| Asset ID | Path | Description |
|----------|------|-------------|
| CON-001 | `assets/constraints/default.yaml` | Default production constraints (16:9, 1024x576, en-US) |
| CON-002 | `assets/constraints/short-form.yaml` | Short-form constraints (≤ 5 minutes) |

### Test Fixtures

| Asset ID | Path | Description |
|----------|------|-------------|
| FIX-ONTO-001 | `tests/fixtures/ontology/minimal-valid.yml` | Passes all ontology tests |
| FIX-ONTO-002 | `tests/fixtures/ontology/missing-header.yml` | Fails GTEST-001 T001 |
| FIX-SCH-001 | `tests/fixtures/schema/valid-production-brief.json` | Schema-valid brief |
| FIX-SCH-002 | `tests/fixtures/schema/invalid-unknown-field.json` | Fails GTEST-002 T010 |
| FIX-AGT-001 | `tests/fixtures/agent/sample-character-architect-input.json` | Sample agent input |
| FIX-AGT-002 | `tests/fixtures/agent/sample-character-architect-output.json` | Sample agent output |
| FIX-E2E-001 | `tests/fixtures/e2e/synopsis-night-he-stopped-reaching.md` | E2E source synopsis |

4. Asset Conventions

- Every asset file has a stable path; tests reference paths, not copies.
- Every asset is versioned alongside the repository; breaking changes require a new asset ID.
- Assets are read-only in tests; tests that need mutation copy first.
- Every asset lists the GSS-NNN schema or GO-NNN ontology it conforms to in a front-matter comment.

5. Contribution

- New assets are added via PR.
- Every new asset must declare its conforming schema or ontology.
- Assets must not contain copyrighted material; original content only.

6. Dependencies

- Schemas: GSS-NNN set
- Ontologies: GO-NNN set
- Tests: GTEST-001 through GTEST-005
- Examples: GEX-001 through GEX-003