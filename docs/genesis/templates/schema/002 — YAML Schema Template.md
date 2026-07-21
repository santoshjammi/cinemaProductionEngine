Genesis Template (GTMP)
GTMP-009 — YAML Schema Template

Document ID: GTMP-009
Title: YAML Schema Template
Version: 1.0.0
Status: Template
Authority: Derived from GFS-000

1. Purpose

Blank template for Genesis YAML Schema files. Use YAML schemas for
human-authored configuration (production briefs, workflow configs, agent
configs) where readability matters more than machine-parse strictness. Place
finished schemas in `schemas/yaml/` with the GSS-NNN scheme.

2. Template

```yaml
# Genesis YAML Schema (GSS-NNN)
# Validates: <Title>
# Description: <One paragraph>

$schema: "https://json-schema.org/draft/2020-12/schema"
$id: "genesis://schemas/yaml/<name>.schema.yaml"
title: "<Title>"
description: "<One paragraph describing what this schema validates.>"
type: object
additionalProperties: false
required:
  - <field>
  - <field>

properties:
  <field>:
    type: string
    description: "<description>"
    minLength: 1
    maxLength: 200
  <field>:
    type: object
    description: "<description>"
    required:
      - <subfield>
    properties:
      <subfield>:
        type: string
        enum: [Explicit, Inferred, Confirmed, Assumed, Unknown]
  <field>:
    type: array
    description: "<description>"
    items:
      $ref: "#/$defs/<DefName>"
    minItems: 0
    maxItems: 100

$defs:
  <DefName>:
    type: object
    required:
      - <field>
    properties:
      <field>:
        type: string

allOf:
  - $ref: "genesis://schemas/yaml/<parent>.schema.yaml"
```

3. Required Header Fields

Every Genesis YAML Schema must include:

- `$schema` — JSON Schema draft used (YAML is a syntax, not a separate spec)
- `$id` — a `genesis://` URI
- `title` — human-readable name
- `description` — purpose
- `type` — root type
- `additionalProperties: false` — strict by default

4. Genesis Conventions

- YAML is used for human authoring; the underlying schema language is JSON Schema.
- Use `genesis://` URIs for `$id` and `$ref`.
- Keep field names snake_case in YAML.
- Every field must carry a `description`.
- Classification enums must use the canonical five-tier set.

5. Validation

- Structural: parses as YAML and validates against JSON Schema Draft 2020-12.
- Semantic: referenced `$defs` and `$ref`s resolve within the Genesis schema set.
- Versioning: schema `$id` includes version; breaking changes require a new GSS-NNN.

6. Dependencies

- Parent schema (if `allOf` extends one): GSS-NNN
- Ontology the schema materializes: GO-NNN