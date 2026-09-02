Genesis Standard (GSTD)
GSTD-002 — Coding Standards

Document ID: GSTD-002
Title: Coding Standards
Version: 1.0.0
Status: Standard
Authority: Derived from GFS-000, GFS-010, GSTD-001

1. Purpose

This Standard defines the coding standards for all source code in the Genesis
Engine — runtime, agents, tooling, tests, and build scripts. It ensures code
is safe to compile, safe to run, safe to extend, and consistent with the
constitutional principles of traceability and explainability.

2. Language Versions

- Python: 3.11+
- TypeScript: 5.x
- Rust (if used): 1.75+
- Shell scripts: bash, `set -euo pipefail`

3. Style

### Python
- Lint and format: `ruff` with line length 100.
- Type checking: `mypy --strict` with zero errors.
- Imports: absolute, ordered stdlib / third-party / local, no wildcard imports.
- Docstrings: Google style on every public module, class, and function.
- Comments: only where the code cannot speak for itself. No dead-code
  comments. No commented-out code.

### TypeScript
- Lint and format: `eslint` + `prettier`.
- Type checking: `tsc --strict`.
- Imports: ESM, ordered, no barrel imports inside the same package.
- JSDoc on every exported symbol.

4. Error Handling

- Raise typed exceptions from a defined error catalog (GFS-006 / GSPEC runtime
  error catalog). Never raise bare `Exception` or `Error`.
- Every exception carries a stable `code`, human `message`, `trace_id`, and
  `retriable` flag.
- Never swallow exceptions silently. At minimum, log with trace_id.
- Public APIs convert internal exceptions to typed API errors at the boundary.

5. Logging

- Structured JSON logging via `structlog` (Python) or `pino` (TypeScript).
- Required fields on every log line: `timestamp`, `level`, `trace_id`,
  `session_id`, `production_id` (when applicable), `agent_id` (when
  applicable).
- Secrets MUST NEVER appear in logs. A redaction filter is mandatory.
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL. Production defaults to
  INFO.

6. Async and Concurrency

- Python: `asyncio` only. No threads for I/O. CPU-bound work uses
  `anyio.to_thread.run_sync`.
- TypeScript: `async`/`await`. No floating promises — `no-floating-promises`
  lint rule enforced.
- Cancellation must be honored at every await point.
- Deadlocks are prevented by strict lock ordering documented per module.

7. Testing

- Test names: `test_{unit}_{condition}_{expected}`.
- One assertion focus per test; multiple asserts allowed only on the same
  subject.
- Test data uses builders or factories, never inline magic values.
- No network calls in unit tests. Use fixture clients.
- Coverage gate: 90% line, 80% branch. Below the gate, CI fails.
- Mutation testing is recommended quarterly for the `validation/` and
  `pkg/` modules.

8. Security

- Secrets from environment or platform secrets manager only. Never in code,
  never in config, never in tests.
- User input is validated at every trust boundary using Pydantic or zod.
- SQL/Cypher queries use parameterized forms only. No string concatenation.
- Dependencies are pinned and scanned weekly (`pip-audit`, `npm audit`).
- No `eval`, no `exec`, no `new Function` in runtime code.

9. Provenance Discipline

Every mutation of PKG state MUST record provenance via the injected recorder.
Direct writes bypassing the recorder are forbidden and will fail review.

10. Immutability

- PKG nodes and edges are versioned. Updates create a new version; the old
  version remains queryable for audit.
- Configuration objects are frozen after load.
- Avoid global mutable state. Singletons are limited to the runtime
  bootstrap.

11. Comments and Documentation

- Code comments explain *why*, not *what*.
- Public APIs are documented in docstrings/JSDoc and reflected in generated
  reference docs.
- ADRs (`decisions/`) record every non-trivial design choice.

12. Review Criteria

A pull request is approvable only when:
- Lint and type checks pass.
- Tests pass and coverage gate is met.
- Provenance is recorded for any PKG mutation.
- No secrets introduced.
- Public API changes are documented and reflected in the CHANGELOG.
- ADR exists or is updated for any architectural change.

13. Cross-References

- Naming Conventions: GSTD-001
- Documentation Standards: GSTD-003
- Python Implementation: GSPEC-071
- Graph DB Implementation: GSPEC-072
- Error Catalog: GSPEC runtime/002