Genesis Tooling (GTOOL)
GTOOL-001 — CLI Tools

Document ID: GTOOL-001
Title: CLI Tools
Version: 1.0.0
Status: Active
Authority: Derived from GFS-000

1. Purpose

Defines the canonical command-line interface for the Genesis Engine. The CLI is
the primary human and automation entry point for initializing, validating,
compiling, generating, and certifying productions.

2. Command Surface

The Genesis CLI exposes five top-level commands: `init`, `validate`, `compile`,
`generate`, `certify`. Every command writes machine-readable output to stdout
(JSON) and human-readable status to stderr.

3. Commands

### genesis init

Creates a new Genesis production scaffold.

```
genesis init --title "<title>" --synopsis <file> [--constraints <file>] [--output <dir>]
```

- Creates the production directory structure.
- Ingests the synopsis and constraints into a Production Brief (GSPEC-001).
- Writes `brief.yaml`, `pkg/` skeleton, and `manifest.yaml`.
- Exit 0 on success; non-zero on validation failure.

### genesis validate

Validates documents, schemas, ontologies, or a full PKG.

```
genesis validate --path <path> [--schema <GSS-NNN>] [--ontology <GO-NNN>]
genesis validate --pkg <pkg-dir>
```

- Without `--schema`: auto-detects the schema from the document's declared schema_id.
- With `--pkg`: runs the PKG Validator (GVAL-001), Ontology Validator (GVAL-002), and Quality Gates (GVAL-003).
- Emits a JSON report with errors, warnings, and per-rule results.
- Exit 0 only if all Block-severity rules pass.

### genesis compile

Runs the Ontology Compiler (GCMP-001) over the ontology set and a PKG.

```
genesis compile --ontology <dir> [--output <dir>]
genesis compile --pkg <pkg-dir> --output <dir>
```

- Compiles ontologies into Pydantic models, JSON Schemas, or code stubs.
- Compiles a PKG into the canonical representation declared by the manifest.
- Fails on any ontology validation error (delegates to GVAL-002).

### genesis generate

Invokes code or documentation generators (GGEN-001).

```
genesis generate --kind <pydantic|schema|docs> --from <ontology|spec|pkg> --output <dir>
genesis generate --kind docs --pkg <pkg-dir> --output docs/
```

- `--kind pydantic`: produces Pydantic models from ontology files.
- `--kind schema`: produces JSON Schema from specifications.
- `--kind docs`: produces human-readable docs from a PKG.
- Every generated file is marked as derived; the PKG remains canonical.

### genesis certify

Runs the certification workflow and issues a Production Readiness Certificate.

```
genesis certify --pkg <pkg-dir> [--output <cert-file>]
```

- Runs all quality gates (GVAL-003).
- Requires zero unresolved contradictions.
- Requires every required decision to meet its confidence threshold.
- On success, writes a signed certificate (JSON) and updates the PKG manifest.
- On failure, lists the failing gates and the decisions blocking certification.

4. Common Flags

- `--json`: forces stdout to be valid JSON only (for CI).
- `--quiet`: suppresses stderr status messages.
- `--verbose`: emits per-step trace to stderr.
- `--config <file>`: overrides default config path.
- `--dry-run`: evaluates without writing.

5. Exit Codes

- 0: success
- 1: validation failure (Block-severity rule failed)
- 2: configuration error
- 3: dependency missing (Neo4j, LLM provider)
- 4: internal error (file a bug)

6. Configuration

The CLI reads `genesis.yaml` from the current directory or `--config`. Keys:

```yaml
pkg_dir: ./pkg
ontology_dir: ./ontology
schemas_dir: ./schemas
llm:
  provider: lmstudio | openai
  model: <name>
  endpoint: <url>
graph:
  provider: neo4j
  uri: bolt://localhost:7687
```

7. Dependencies

- Validators: GVAL-001, GVAL-002, GVAL-003
- Compiler: GCMP-001
- Generators: GGEN-001
- Integrations: GINT-001, GINT-002