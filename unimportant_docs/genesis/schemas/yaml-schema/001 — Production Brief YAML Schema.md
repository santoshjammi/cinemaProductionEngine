Genesis Schema Specification (GSS)
GSS-101 — Production Brief YAML Schema

Document ID: GSS-101
Title: Production Brief YAML Schema
Version: 1.0.0
Status: Schema Specification
Authority: Derived from GFS-010, GSS-001

1. Purpose

This Schema defines the YAML serialization format for Production Briefs. A
Production Brief is the human-authored entry artifact that captures initial
creative intent, constraints, and target audience before discovery begins.
YAML is preferred over JSON for brief authoring due to readability and comment
support.

2. When to Use

Use this schema when:
- A creator submits an initial brief to Genesis
- A discovery agent ingests raw creative intent
- A brief is materialized from the PKG for human review

3. Top-Level Structure

```yaml
# Production Brief — top-level document
brief:
  id: "urn:genesis:brief:<uuid>"        # required, stable identifier
  version: "1.0.0"                        # required, semver
  status: draft | reviewed | approved     # required
  created_at: "2026-07-19T00:00:00Z"      # ISO-8601
  author:
    name: "Jane Creator"
    role: "creator"
  production_id: "urn:genesis:prod:<uuid>"  # link to PKG once created
```

4. Creative Intent Block

The `intent` block carries the synopsis, vision, and message. Per GFS-000,
the synopsis is the creative problem statement, not the story.

```yaml
intent:
  synopsis: |
    A retired teacher discovers her late husband left her a series of letters
    that rewrite the story of their marriage.
  logline: "One sentence elevator pitch."
  vision: "What emotional experience the audience should have."
  message: "Optional thematic message."
  themes:
    - grief
    - rediscovery
    - forgiveness
  tone: "bittersweet, contemplative"
  genre: "drama"
  format: feature | short | series | documentary | devotional
```

5. Constraints Block

Constraints bound the creative space. Genesis must respect them throughout
discovery and reasoning.

```yaml
constraints:
  duration_minutes: 95
  audience:
    primary: "adults 35-60"
    secondary: "literary drama enthusiasts"
  language: "en"
  cultural_context: "contemporary urban India"
  content_rating: "PG-13"
  budget_tier: "indie"
  hard_no:
    - "excessive violence"
    - "on-screen smoking"
  must_have:
    - "female protagonist over 60"
    - "epistolary device"
```

6. References Block

Optional references the creator supplies to seed discovery.

```yaml
references:
  inspirations:
    - title: "The Letter (2012)"
      medium: film
      note: "tone reference"
  source_material:
    - kind: book
      title: "Letters to My Husband"
      author: "Jane Creator"
  research_hints:
    - "widowhood in later life"
    - "epistolary narrative structure"
```

7. Discovery Targets Block

Tells Genesis which knowledge areas to prioritize during discovery.

```yaml
discovery_targets:
  - domain: character
    priority: high
    focus: ["protagonist arc", "antagonist as memory"]
  - domain: world
    priority: medium
    focus: ["domestic interior", "decade-spanning timeline"]
  - domain: narrative
    priority: high
    focus: ["non-linear structure", "letter as framing device"]
```

8. Validation Rules

- `brief.id` MUST be a valid URN
- `intent.synopsis` MUST NOT be empty
- `constraints.duration_minutes` MUST be a positive integer
- `discovery_targets` MUST contain at least one entry
- All enum fields MUST use values from the controlled vocabularies defined in
  the Core Ontology (GO-001) and the Production Ontology (GO-301)

9. Tooling

Validation:
```bash
genesis validate brief --schema gss-101 --input brief.yaml
```

Materialization from PKG:
```bash
genesis materialize brief --pkg <pkg-id> --output brief.yaml
```

10. Relationship to Other Schemas

- Inherits vocabulary from GSS-001 (PKG JSON Schema)
- Composed with GSS-102 (Character DNA YAML Schema) when characters are
  pre-specified
- Parsed by the Ontology Compiler (GSPEC-COMP-001) to seed the PKG

11. Revision History

- 1.0.0 — Initial draft. Derived from GSS-001 v1.0.0.