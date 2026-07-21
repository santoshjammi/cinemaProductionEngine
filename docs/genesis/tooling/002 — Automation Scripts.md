Genesis Tooling (GTOOL)
GTOOL-002 — Automation Scripts

Document ID: GTOOL-002
Title: Automation Scripts
Version: 1.0.0
Status: Active
Authority: Derived from GFS-000

1. Purpose

Defines the batch and CI/CD automation scripts that wrap the Genesis CLI
(GTOOL-001). Scripts are thin wrappers; all logic lives in the CLI so that
behavior is consistent across local and automated environments.

2. Script Catalog

All scripts live in `tooling/scripts/` and are executable (`chmod +x`). Each
script writes a JSON result to stdout and human-readable progress to stderr.

### scripts/validate-all.sh

Validates every document, schema, and ontology in a Genesis repository.

```bash
bash tooling/scripts/validate-all.sh [--root <dir>] [--strict]
```

- Walks `ontology/`, `schemas/`, `specifications/`, `agents/`, `workflows/`.
- Invokes `genesis validate` for each file.
- Aggregates results into a single JSON report.
- `--strict` treats Warn-severity failures as errors.
- Exit 0 only if all files pass.

### scripts/compile-ontologies.sh

Compiles every ontology in the repository.

```bash
bash tooling/scripts/compile-ontologies.sh [--root <dir>] [--output <dir>]
```

- Invokes `genesis compile --ontology` for each domain.
- Fails fast on the first ontology validation error.
- Writes generated models to `--output` (default `dist/ontology/`).

### scripts/run-tests.sh

Runs the full Genesis test suite.

```bash
bash tooling/scripts/run-tests.sh [--suite <ontology|schema|agent|workflow|e2e|all>]
```

- Invokes `genesis test --suite <suite>` for each requested suite.
- Writes per-suite reports to `tests/reports/`.
- Aggregates a summary report at `tests/reports/summary-<timestamp>.json`.

### scripts/certify-pkg.sh

Runs full validation and certification on a PKG.

```bash
bash tooling/scripts/certify-pkg.sh --pkg <dir> [--output <cert>]
```

- Runs `genesis validate --pkg`, then `genesis certify`.
- Writes the certificate to `--output` (default `pkg/certificate.json`).
- Exit 0 only if certification succeeds.

### scripts/generate-docs.sh

Generates documentation for a PKG.

```bash
bash tooling/scripts/generate-docs.sh --pkg <dir> --output <dir>
```

- Invokes `genesis generate --kind docs --pkg <pkg> --output <dir>`.
- Used to refresh human-readable views after PKG updates.

3. CI/CD Integration

### GitHub Actions

A reference workflow lives at `.github/workflows/genesis.yml`:

```yaml
name: Genesis
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install Genesis
        run: pip install genesis-engine
      - name: Validate all
        run: bash tooling/scripts/validate-all.sh --strict
      - name: Run tests
        run: bash tooling/scripts/run-tests.sh --suite all
      - name: Upload reports
        uses: actions/upload-artifact@v4
        with:
          name: genesis-reports
          path: tests/reports/
```

### Pre-commit Hook

A reference hook for validating changed files before commit:

```bash
#!/bin/bash
changed=$(git diff --cached --name-only | grep -E '\.(yaml|json|md)$')
for f in $changed; do
  genesis validate --path "$f" || exit 1
done
```

4. Conventions

- Every script uses `set -euo pipefail`.
- Every script writes status to stderr, JSON to stdout.
- Every script accepts `--help` and prints usage.
- No script mutates the repository except via `genesis` CLI commands.
- No script embeds secrets. Secrets come from environment variables.

5. Dependencies

- Genesis CLI (GTOOL-001) installed and on PATH.
- `jq` for JSON manipulation in scripts.
- `python3` for any inline helpers.