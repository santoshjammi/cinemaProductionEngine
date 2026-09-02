# GKC-008 — Plugin Framework

> How GKC is extended without forking. Every extension point, the plugin contract, the sandboxing model, capability declarations, and the plugin lifecycle.

---

## 1. Purpose

Define the Plugin Framework (C14) as the **single, uniform extension mechanism** for GKC. After this document, a plugin author can add a new artifact kind, a new graph edge type, a new context provider, a new query kind, a new validator, or a new storage backend without touching GKC core.

This document defines:

- the **plugin package format**,
- the **manifest** (capabilities, extension points, integrity),
- the **extension point contracts** (one per extension point from `DESIGN/003` § 6),
- the **sandboxing model** (load-time, runtime, future horizons),
- the **lifecycle** (discover → load → activate → unload),
- the **failure isolation** boundary,
- the **plugin registry** (per-workspace).

---

## 2. Plugin Package Format

### 2.1 Directory layout

A plugin is a directory with a manifest and the plugin's implementation files:

```
<plugin-id>/
├── manifest.json       (required)
├── code/               (required; implementation; layout is language-specific)
│   └── ...
├── schemas/            (optional; schemas the plugin registers)
│   └── ...
└── README.md           (optional; human-readable docs)
```

### 2.2 Manifest schema

```json
{
  "id": "com.acme.gkc/vector-search",
  "version": "1.0.0",
  "gkc_version_compat": ">=0.1.0 <1.0.0",
  "integrity_hash": "sha256:...",
  "capabilities": ["filesystem-read", "network-loopback"],
  "extension_points": [
    {
      "kind": "indexer",
      "id": "vector",
      "schema": "schemas/vector-index.json"
    },
    {
      "kind": "query",
      "id": "vector:similar",
      "params_schema": "schemas/vector-similar-params.json",
      "result_schema": "schemas/vector-similar-result.json",
      "required_indexes": ["vector"]
    }
  ],
  "declared_invariants": ["determinism", "no-ir-mutation"],
  "author": "Acme",
  "license": "MIT"
}
```

### 2.3 Manifest fields

| Field | Required | Purpose |
|---|---|---|
| `id` | Yes | Reverse-DNS identifier; namespaced |
| `version` | Yes | Semver |
| `gkc_version_compat` | Yes | GKC version compatibility range |
| `integrity_hash` | Yes | SHA-256 of the code directory's content hash |
| `capabilities` | Yes | List of declared capabilities (per § 5) |
| `extension_points` | Yes | List of extension point registrations (per § 4) |
| `declared_invariants` | Yes | Invariants the plugin claims to respect |
| `author`, `license` | No | Metadata |

### 2.4 Integrity verification

At load time, the framework:

1. Hashes the `code/` directory (canonical serialization, sorted file order).
2. Compares the hash to `integrity_hash`.
3. Rejects on mismatch with `plugin-integrity-failed`.

Integrity verification is **always** enforced; there is no "trust mode" that skips it.

---

## 3. Plugin Lifecycle

```
discovered → integrity-checked → capability-checked → loaded → active → unloaded
```

- **discovered**: framework finds the plugin directory in the workspace's `plugins/` subdir.
- **integrity-checked**: `integrity_hash` verified.
- **capability-checked**: declared capabilities verified against workspace policy.
- **loaded**: plugin code is loaded into the host process (per § 6 sandboxing).
- **active**: plugin is registered for its extension points and can be dispatched.
- **unloaded**: at session end; plugin code is unloaded; no further dispatch.

### 3.1 Load failures

| Failure | Stage | Behavior |
|---|---|---|
| Integrity mismatch | integrity-checked | Reject; `plugin-integrity-failed` diagnostic |
| Capability not allowed by workspace policy | capability-checked | Reject; `plugin-capability-denied` diagnostic |
| GKC version incompatible | capability-checked | Reject; `plugin-gkc-version-incompatible` diagnostic |
| Extension point conflict (id already registered) | loaded | Reject; `plugin-extension-conflict` diagnostic |
| Code load error (syntax, missing export) | loaded | Reject; `plugin-load-error` diagnostic |

### 3.2 Runtime failures

| Failure | Behavior |
|---|---|
| Plugin throws during dispatch | Per-artifact recovery (per ADR-Candidate-0003); `plugin-failed` diagnostic |
| Plugin exceeds declared capability at runtime | Plugin terminated; `plugin-capability-violation` diagnostic; affected artifact marked `plugin-failed` |
| Plugin hangs (timeout) | Configurable timeout (default 30s); on timeout, plugin terminated; `plugin-timeout` diagnostic |

---

## 4. Extension Point Contracts

Each extension point has a typed contract. A plugin registers against one or more extension points by declaring them in the manifest and providing the implementation.

### 4.1 Classifier (Scanner extension)

- **Extends**: C1 Scanner, stage 1.
- **Contract**: `classify(artifact_path, content_hash, first_bytes) → { kind: ArtifactKind, confidence: float } | null`
- **Registration**: `extension_points[].kind = "classifier"`.
- **Notes**: Multiple classifiers form a chain; first non-null wins. Built-in classifiers run first; plugin classifiers run after, in registration order.
- **Determinism**: Classifier output must be deterministic for a given input.

### 4.2 Parser (Parser extension)

- **Extends**: C2 Parser, stage 2.
- **Contract**: `parse(artifact, content_bytes) → { raw_metadata: RawMetadata, diagnostics: [Diagnostic] }`
- **Registration**: `kind = "parser"`, with `for_kinds: [ArtifactKind]`.
- **Notes**: One parser per kind (built-in or plugin). Plugin parsers override built-in parsers for the same kind only if explicitly registered as `override: true`.
- **Determinism**: Parser output is deterministic.

### 4.3 Inference rule (Normalizer extension)

- **Extends**: C3 Normalizer, stage 3.
- **Contract**: `infer(raw_metadata, artifact) → { inferred_fields: map<string, value>, provenance: string } | null`
- **Registration**: `kind = "inference"`.
- **Notes**: Multiple inference rules run in registration order; later rules may override earlier ones (with provenance).

### 4.4 Resolver strategy (Resolver extension)

- **Extends**: C4 Resolver, stage 4.
- **Contract**: `resolve(reference_descriptor, registry_snapshot) → { target_id: ArtifactId } | unresolved`
- **Registration**: `kind = "resolver"`, with `for_reference_kinds: [ReferenceKind]`.
- **Notes**: Multiple resolvers run in order; first successful wins.

### 4.5 Authority edge kind (Authority Builder extension)

- **Extends**: C6, stage 6.
- **Contract**: `declare_edges(registry_entry, registry_snapshot) → [AuthorityEdge]`
- **Registration**: `kind = "authority-edge"`, with `edge_kind: string`.
- **Notes**: New edge kinds must respect the stratification invariant (per ADR-Candidate-0011). The framework rejects edges that violate stratification at runtime.

### 4.6 Dependency edge kind (Dependency Builder extension)

- **Extends**: C7, stage 7.
- **Contract**: `declare_edges(registry_entry, registry_snapshot) → [DependencyEdge]`
- **Registration**: `kind = "dependency-edge"`, with `edge_kind: string` and `default_strength: hard | soft`.

### 4.7 Ontology edge kind (Ontology Compiler extension)

- **Extends**: C8, stage 8.
- **Contract**: `declare_edges(ontology_node, registry_snapshot) → [OntologyEdge]`
- **Registration**: `kind = "ontology-edge"`, with `edge_kind: string`.

### 4.8 Invariant (Validator extension)

- **Extends**: C9, stage 9.
- **Contract**: `check(ir) → [Diagnostic]`
- **Registration**: `kind = "invariant"`, with `invariant_id: string` and `severity_on_violation: Severity`.
- **Notes**: Invariant ids must be namespaced (e.g., `acme:no-circular-runtimes`). The framework rejects duplicates.

### 4.9 Index kind (Indexer extension)

- **Extends**: C10, stage 10.
- **Contract**: `build(ir) → Index`
- **Registration**: `kind = "indexer"`, with `index_id: string` and `schema: json-schema`.
- **Notes**: The index is persisted in the snapshot; the framework handles serialization via the schema.

### 4.10 Context provider (Context Compiler extension)

- **Extends**: C11, stage 11.
- **Contract**: `render(slice, model_profile) → RenderedSlice`
- **Registration**: `kind = "context-provider"`, with `provider_id: string`.
- **Notes**: Provider ids must be namespaced. Built-in providers (`markdown`, `anthropic-xml`, `openai-json`, `local-llm`) are pre-registered.

### 4.11 Query kind (Query Engine extension)

- **Extends**: C12.
- **Contract**: `execute(query_request, snapshot, indexes) → QueryResult`
- **Registration**: `kind = "query"`, with `query_kind_id: string`, `params_schema`, `result_schema`, `required_indexes`.
- **Notes**: Query kind ids must be namespaced; conflicts are rejected (per `DESIGN/006` § 9.3).

### 4.12 Storage backend (Storage extension)

- **Extends**: C13.
- **Contract**: implements the Storage interface (per `DESIGN/010`).
- **Registration**: `kind = "storage"`, with `backend_id: string`.
- **Notes**: Storage backends are mutually exclusive (only one active per workspace). The default is `filesystem`; a plugin can replace it.

---

## 5. Capabilities

### 5.1 Capability enum

| Capability | Description |
|---|---|
| `filesystem-read` | Read files within the workspace |
| `filesystem-write` | Write files within the workspace's plugin scratch dir |
| `network-loopback` | Loopback network access (127.0.0.1, ::1) |
| `network-external` | External network access |
| `subprocess` | Spawn subprocesses |
| `env-read` | Read environment variables |
| `env-write` | Set environment variables for spawned subprocesses |

### 5.2 Capability policy

Each workspace has a capability policy:

```json
{
  "allow": ["filesystem-read", "network-loopback"],
  "deny": ["network-external", "subprocess"],
  "require_explicit": ["filesystem-write", "env-read"]
}
```

- `allow`: granted at load time.
- `deny`: rejected at load time.
- `require_explicit`: the plugin must declare the capability; if declared, granted.

### 5.3 Runtime enforcement (per ADR-Candidate-0020)

- **M0–M3 (level A)**: load-time check only. Plugins are trusted after load.
- **M4–M5 (level B)**: runtime enforcement via framework-provided shims. Filesystem, network, and subprocess calls go through the framework.
- **Post-M5 (level C/D)**: process or WASM isolation.

The level is recorded in the workspace config; the framework refuses to load plugins that require capabilities above the current level.

---

## 6. Sandboxing

### 6.1 Load-time sandboxing (always on)

- Integrity hash verified.
- Capabilities checked against policy.
- GKC version compatibility checked.
- Extension point conflicts checked.

### 6.2 Runtime sandboxing (level B, M4+)

- Filesystem access goes through `framework.fs.*` shims that enforce workspace boundaries.
- Network access goes through `framework.net.*` shims that enforce loopback-only when `network-external` is not declared.
- Subprocess spawning goes through `framework.proc.*` shims that enforce declared `subprocess` capability.
- Environment access goes through `framework.env.*` shims.

A plugin that bypasses the shims (e.g., direct syscall) is in violation; the framework's capability enforcer terminates the plugin on detection. Detection is best-effort at M4; stronger via process isolation at later horizons.

### 6.3 Future horizons (post-M5)

- **Process isolation (C)**: plugins run in separate processes; IPC via the framework. Strong isolation; higher latency.
- **WASM isolation (D)**: plugins compile to WASM; run in a sandboxed runtime. Strong isolation; language constraints.

---

## 7. Plugin Registry

### 7.1 Per-workspace (per ADR-Candidate-0015)

Each workspace has its own `plugins/` directory. Plugins are not shared across workspaces.

### 7.2 Registry contents

The registry (in-memory at session start; persisted in the workspace) records:

- `plugin_id`, `version`, `integrity_hash`.
- `extension_point_registrations` (per § 4).
- `capabilities`, `policy_decision` (allow/deny).
- `load_state` (discovered/loaded/active/unloaded).

### 7.3 Registry queries

- `gkc doctor` lists all registered plugins and their states.
- `gkc plugin list` lists plugins.
- `gkc plugin info <id>` shows details.
- `gkc plugin install <path>` installs a plugin to the workspace.
- `gkc plugin uninstall <id>` removes a plugin.

---

## 8. Failure Isolation

### 8.1 Per-artifact recovery

When a plugin throws during dispatch (per `DESIGN/003` § C14 and `DESIGN/005` § 5.2):

1. The framework catches the exception at the dispatch boundary.
2. The affected artifact is marked `plugin-failed` (in the relevant stage's output).
3. A `plugin-failed` diagnostic is emitted with plugin id, exception details, and provenance.
4. Other artifacts and other plugins continue.

### 8.2 Per-package recovery (context provider)

If a context provider throws (per `DESIGN/007` § 9.5):

1. The framework catches the exception.
2. The compiler falls back to the built-in `markdown` provider.
3. A `provider-fallback` marker is added to the package metadata.

### 8.3 Per-invariant recovery (validator)

If an invariant plugin throws (per `DESIGN/005` § 5.1):

1. The framework catches the exception.
2. The invariant is marked `not-checked` in the validation report.
3. An `invariant-check-failed` error diagnostic is emitted.

### 8.4 No recovery for load-time failures

Load-time failures (integrity, capability, version, conflict) are fatal for the plugin; the plugin is not loaded. Other plugins continue.

---

## 9. Built-in Plugins

Built-in extensions (classifiers, parsers, providers, query kinds, etc.) are registered at startup exactly like plugin-provided ones. The framework has no special-case code for built-ins; they go through the same dispatch path.

This means: a plugin can override a built-in by registering the same extension point id with `override: true`. The framework logs the override and proceeds.

---

## 10. Plugin Discovery

### 10.1 Discovery path

The framework discovers plugins in `<workspace>/plugins/*/manifest.json`.

### 10.2 Discovery order

Plugins are discovered in sorted order (by plugin id) for deterministic load order. Load order matters only for extension points where order is significant (e.g., classifier chain); for those, the framework uses the manifest's declared `priority` field (default 100; lower runs first).

### 10.3 Conflicts

Two plugins registering the same extension point id (and not `override: true`) produce a `plugin-extension-conflict` diagnostic; the second plugin is not loaded for that extension point.

---

## 11. Plugin Development Workflow

### 11.1 Author

1. Create a plugin directory with `manifest.json`.
2. Implement the extension point contracts in `code/`.
3. Compute `integrity_hash` (via `gkc plugin hash <dir>`).
4. Test locally via `gkc plugin install <dir>`.

### 11.2 Distribute

Plugins are distributed as directories (or archives). There is no central plugin registry in M0–M5; distribution is the author's responsibility (git, tarball, etc.). A central registry is a post-M5 horizon.

### 11.3 Install

`gkc plugin install <path>` copies the plugin into the workspace's `plugins/` directory and verifies integrity.

### 11.4 Uninstall

`gkc plugin uninstall <id>` removes the plugin directory. Active sessions are unaffected (the plugin remains loaded until session end); new sessions will not load it.

---

## 12. Observability

### 12.1 Per-plugin metrics

The framework emits per-plugin metrics:

- `dispatches` (count per extension point).
- `failures` (count, by failure type).
- `duration_ms` (per dispatch).
- `capabilities_used` (which declared capabilities were exercised).

### 12.2 CLI surface

- `gkc doctor` shows plugin health.
- `gkc plugin list` shows registered plugins.
- `gkc stats --plugins` shows per-plugin metrics.

---

## 13. Open Questions for ADR

Surfaced in `DECISIONS/008-plugin-framework-adr-candidates.md`:

1. Should plugins support hot-reload (unload + reload without session restart)?
2. Should the framework support plugin signatures (cryptographic, not just hash)?
3. Should the framework support plugin dependencies (per ADR-Candidate-0022)?
4. Should built-in extensions be implementable as "internal plugins" (same contract, different load path)?
5. Should the capability policy be workspace-level or also configurable per-plugin?