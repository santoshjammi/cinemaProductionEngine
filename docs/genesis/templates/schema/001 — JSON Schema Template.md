Genesis Template (GTMP)
GTMP-008 — JSON Schema Template

Document ID: GTMP-008
Title: JSON Schema Template
Version: 1.0.0
Status: Template
Authority: Derived from GFS-000

1. Purpose

Blank template for Genesis JSON Schema files (GSS-NNN). Use this for any
machine-readable contract that must be validated structurally. Place finished
schemas in `schemas/json/` with the GSS-NNN scheme.

2. Template

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "genesis://schemas/json/<name>.schema.json",
  "title": "<Title>",
  "description": "<One paragraph describing what this schema validates.>",
  "type": "object",
  "additionalProperties": false,
  "required": ["<field>", "<field>"],
  "properties": {
    "<field>": {
      "type": "<string|number|boolean|array|object>",
      "description": "<description>",
      "enum": ["<value>", "<value>"]
    },
    "<field>": {
      "type": "array",
      "items": { "$ref": "#/$defs/<DefName>" },
      "minItems": 0,
      "maxItems": 100
    }
  },
  "$defs": {
    "<DefName>": {
      "type": "object",
      "required": ["<field>"],
      "properties": {
        "<field>": { "type": "<type>" }
      }
    }
  },
  "allOf": [
    { "$ref": "genesis://schemas/json/<parent>.schema.json" }
  ]
}
```

3. Required Header Fields

Every Genesis JSON Schema must include:

- `$schema` — the JSON Schema draft used
- `$id` — a `genesis://` URI identifying the schema
- `title` — human-readable name
- `description` — purpose
- `type` — root type
- `additionalProperties: false` — strict by default

4. Genesis Conventions

- Use `genesis://` URIs for `$id` and `$ref`.
- Schemas are strict: `additionalProperties: false` unless explicitly relaxed.
- Every field must have a `description`.
- Enumerate closed sets of values; never leave enums open.
- Classifications (Explicit/Inferred/Confirmed/Assumed/Unknown) must be enums.

5. Validation

- Structural: validates against JSON Schema Draft 2020-12.
- Semantic: referenced `$defs` and `$ref`s resolve within the Genesis schema set.
- Versioning: schema `$id` includes version; breaking changes require a new GSS-NNN.

6. Dependencies

- Parent schema (if `allOf` extends one): GSS-NNN
- Ontology the schema materializes: GO-NNN