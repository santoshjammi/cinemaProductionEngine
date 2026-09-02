Genesis Schema Specification (GSS)
GSS-001 — Production Knowledge Graph JSON Schema

Document ID: GSS-001
Title: Production Knowledge Graph JSON Schema
Version: 1.0.0
Status: Schema Specification
Authority: Derived from GFS-010

1. Purpose

This Schema defines the JSON Schema for the Production Knowledge Graph serialization format. It provides structural validation rules for PKG documents.

2. Schema

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://genesis.movieos.dev/schemas/pkg/v1.json",
  "title": "Production Knowledge Graph",
  "type": "object",
  "required": ["id", "production", "version", "nodes", "edges"],
  "properties": {
    "@context": { "type": "string", "format": "uri" },
    "id": { "type": "string", "format": "uuid" },
    "production": { "type": "string" },
    "version": { "type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$" },
    "created_at": { "type": "string", "format": "date-time" },
    "provenance": {
      "type": "object",
      "required": ["agent", "session"],
      "properties": {
        "agent": { "type": "string" },
        "session": { "type": "string" }
      }
    },
    "nodes": {
      "type": "array",
      "items": { "$ref": "#/$defs/Node" }
    },
    "edges": {
      "type": "array",
      "items": { "$ref": "#/$defs/Edge" }
    },
    "subgraphs": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "required": ["name", "node_ids", "edge_ids"],
        "properties": {
          "name": { "type": "string" },
          "node_ids": { "type": "array", "items": { "type": "string", "format": "uuid" } },
          "edge_ids": { "type": "array", "items": { "type": "string", "format": "uuid" } }
        }
      }
    },
    "validation": {
      "type": "object",
      "properties": {
        "status": { "type": "string", "enum": ["PASS", "FAIL", "PENDING"] },
        "errors": { "type": "array", "items": { "type": "string" } },
        "warnings": { "type": "array", "items": { "type": "string" } }
      }
    }
  },
  "$defs": {
    "Node": {
      "type": "object",
      "required": ["id", "type", "label", "confidence"],
      "properties": {
        "id": { "type": "string", "format": "uuid" },
        "type": { "type": "string" },
        "label": { "type": "string" },
        "properties": { "type": "object" },
        "confidence": { "type": "string", "enum": ["EXPLICIT", "INFERRED", "CONFIRMED", "ASSUMED", "UNKNOWN"] },
        "created_at": { "type": "string", "format": "date-time" },
        "provenance": {
          "type": "object",
          "properties": {
            "agent": { "type": "string" },
            "session": { "type": "string" }
          }
        }
      }
    },
    "Edge": {
      "type": "object",
      "required": ["id", "type", "source_id", "target_id", "confidence"],
      "properties": {
        "id": { "type": "string", "format": "uuid" },
        "type": { "type": "string" },
        "source_id": { "type": "string", "format": "uuid" },
        "target_id": { "type": "string", "format": "uuid" },
        "properties": { "type": "object" },
        "confidence": { "type": "string", "enum": ["EXPLICIT", "INFERRED", "CONFIRMED", "ASSUMED", "UNKNOWN"] },
        "created_at": { "type": "string", "format": "date-time" },
        "provenance": {
          "type": "object",
          "properties": {
            "agent": { "type": "string" },
            "session": { "type": "string" }
          }
        }
      }
    }
  }
}

3. Validation Rules

- All node IDs must be valid UUIDs
- All edge source/target IDs must reference existing node IDs
- Confidence must be one of the five defined levels
- Version must follow semantic versioning
- Subgraph node_ids and edge_ids must reference existing nodes/edges
- Provenance agent and session are required for all nodes and edges

4. Usage

This schema is used to validate PKG documents before they are committed to the graph database. Validation is performed by the Validation Agent (GFS-006).
