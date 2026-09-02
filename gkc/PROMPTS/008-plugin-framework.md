# GKC-008 — Engineering Prompt

## Objective

Implement the **Plugin Framework (C14)**: plugin discovery, manifest parsing, integrity verification, capability checking, extension point registration, dispatch with failure isolation, lifecycle management, and per-plugin observability.

## Inputs

- `DESIGN/008-plugin-framework.md` (authoritative)
- `DESIGN/003-component-architecture.md` (§ C14 boundaries)
- `DECISIONS/008-plugin-framework-adr-candidates.md`

## Scope

1. **Plugin discovery** (§ 10) — scan the workspace's `plugins/` directory; parse manifests; reject malformed manifests.
2. **Integrity verification** (§ 2.4) — hash the `code/` directory; compare to manifest's `integrity_hash`; reject on mismatch.
3. **Capability checking** (§ 5) — load workspace capability policy; check plugin capabilities against policy; reject on denial.
4. **GKC version compatibility check** — verify `gkc_version_compat` against the current GKC version.
5. **Extension point registration** (§ 4) — register plugins for all 12 extension point kinds; detect conflicts; support `override: true`.
6. **Dispatch with failure isolation** (§ 8) — call plugins via the framework; catch exceptions at the boundary; mark affected artifacts `plugin-failed`; emit diagnostics.
7. **Runtime capability enforcement (level A)** — load-time check only (per ADR-Candidate-0020). Level B shims are stubbed for M5.
8. **Lifecycle** (§ 3) — implement the 6-state machine; track state per plugin.
9. **Plugin registry** (§ 7) — in-memory registry; persists to workspace metadata.
10. **CLI subcommands** (§ 7.3, § 11) — `gkc plugin list`, `info`, `install`, `uninstall`, `hash`.
11. **Observability** (§ 12) — per-plugin metrics; exposed via `gkc doctor` and `gkc stats`.
12. **Built-in extensions as plugins** (§ 9) — register built-in classifiers, parsers, providers, etc. through the same framework path.

## Out of Scope

- Runtime capability enforcement shims (level B) — stubbed for M5.
- Process isolation / WASM — post-M5 horizon.
- Central plugin registry — post-M5.
- Real plugin implementations (use stub plugins for testing).

## Done Conditions

- A stub plugin can be installed, loaded, dispatched, and unloaded.
- Integrity verification rejects a tampered plugin.
- Capability policy rejects a plugin that requires a denied capability.
- Version compatibility rejects a plugin that targets a different GKC version.
- Extension point conflicts are detected and rejected.
- A throwing plugin triggers per-artifact recovery; the affected artifact is marked; other artifacts proceed.
- Built-in extensions are registered through the same path as plugins.
- All five CLI subcommands work.
- Per-plugin metrics are emitted and queryable.

## Constraints

- Implementation language: per `DECISIONS/0010-implementation-language.md`.
- No external services.
- No reflection; plugin contracts are explicit interfaces.
- All dispatch is via the framework; no direct plugin calls from core.

## Deliverables

- `plugins/discovery` — plugin discovery
- `plugins/manifest` — manifest parsing and validation
- `plugins/integrity` — integrity verification
- `plugins/capabilities` — capability policy and checking
- `plugins/registry` — plugin registry
- `plugins/dispatch` — dispatch with failure isolation
- `plugins/lifecycle` — lifecycle state machine
- `plugins/builtins` — built-in extension registrations
- `plugins/observability` — per-plugin metrics
- `plugins/tests/*` — per-feature tests with stub plugins

## Verification

1. `gkc test plugins` — all plugin tests pass.
2. Install a stub plugin; verify it loads and dispatches.
3. Tamper the stub plugin's code; verify integrity check rejects it.
4. Declare a denied capability in a stub; verify capability check rejects it.
5. Register two plugins for the same extension point id; verify conflict is detected.
6. Dispatch a throwing stub; verify per-artifact recovery and `plugin-failed` diagnostic.
7. `gkc plugin list`, `info`, `install`, `uninstall`, `hash` all work.
8. `gkc doctor` shows plugin health and metrics.

Report pass/fail per step. Any failure blocks M0.