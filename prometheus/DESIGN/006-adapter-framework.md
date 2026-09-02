# PROMETHEUS-006 — Adapter Framework

> The adapter framework: the capability registry, the provider abstraction, the adapter lifecycle, and the contract between PROMETHEUS and any execution backend. Adapters are the replaceable edge of the platform; the engine is unchanged when adapters are swapped.

---

## 1. Purpose

Define, at engineering precision:

- What an adapter *is* and what it *is not*.
- The adapter interface (the contract every adapter satisfies).
- The capability registry (how adapters are discovered and selected).
- The provider abstraction (how local and cloud providers sit behind the same interface).
- The adapter lifecycle (load, invoke, unload).
- How adapters classify their own failures.
- How adapters participate in determinism (seed-based and recorded-output).
- How new adapters are added without engine changes.

This document is the engineering realization of `010` §5 (Runtime Services), §10 (Runtime Extensibility), and §11 (Platform Independence).

---

## 2. What an Adapter Is

An adapter is a **plugin** that satisfies the adapter interface and executes one EIR node by invoking a provider. The adapter is the only subsystem that calls external providers (image models, TTS, FFmpeg, etc.); the engine never calls providers directly.

```
EIR node
   │
   │  Adapter Framework dispatches
   ▼
Adapter (plugin)
   │
   │  invokes provider (local or cloud) behind the capability interface
   ▼
Provider output
   │
   │  adapter validates + records provenance
   ▼
AdapterResult
```

An adapter **is**:

- A plugin (loaded by the Plugin Framework, S26).
- A consumer of the EIR (it reads one node at a time).
- A caller of a provider (local or cloud, behind the capability interface).
- A validator of its own output (per the node's ValidationSpec).
- A recorder of its version, the seed, and the invocation params (for provenance).

An adapter **is not**:

- Creative. It never invents content (L-15). If the EIR node is missing a detail, the adapter reports a `rendering-gap`, not an invention.
- A reader of the PKP. It reads only the EIR node.
- A writer to ATLAS. The Asset Emission Service (S23) writes outputs.
- A caller of GENESIS, ORACLE, or the human.
- A modifier of the EIR. The EIR is immutable from Stage 8.

---

## 3. The Adapter Interface

Every adapter satisfies a language-neutral interface. The interface is the contract; adapters in any language can satisfy it (via the SDK, S29).

### 3.1 The core interface

```
interface Adapter {
  adapter_id        : AdapterId
  adapter_version   : SemVer
  capabilities       : List<Capability>     // which capabilities this adapter provides
  supported_eir_versions : List<SemVer>    // which EIR schema versions this adapter accepts

  invoke(node : Node, inputs : ResolvedInputs, context : InvocationContext) → AdapterResult

  classify_failure(error : AdapterError) → FailureClass

  health_check() → HealthStatus
}
```

### 3.2 AdapterResult

```
AdapterResult : Success | Failure | Gap

Success {
  output        : Output            // the produced media/artifact
  output_hash   : Hash              // deterministic hash of the output
  validation    : ValidationResult  // the ValidationSpec checks' results
  metrics       : AdapterMetrics    // duration, resource usage, provider latency
}

Failure {
  error_class   : FailureClass      // recoverable | retryable | fatal | adapter | resource | validation
  error_message : String
  error_detail  : ErrorDetail       // stack trace, provider response, etc.
  retryable     : Bool
}

Gap {
  missing_detail : MissingDetail    // what the EIR node did not specify
  rationale      : String
}
```

### 3.3 InvocationContext

```
InvocationContext {
  execution_id    : ExecutionId
  event_bus       : EventBusHandle     // for the adapter to emit events
  config          : Config             // adapter-specific config (no secrets in the EIR; secrets resolved here)
  security        : SecurityHandle      // capability checks (network, filesystem, subprocess)
  cache           : CacheHandle        // for the adapter to check/update the node cache
}
```

The `InvocationContext` is the adapter's handle to the runtime. The adapter uses it to emit events, resolve secrets, check capabilities, and access the cache. The adapter does **not** use it to call GENESIS, ORACLE, or the human.

### 3.4 ResolvedInputs

```
ResolvedInputs : Map<InputName, ResolvedValue>

ResolvedValue : {
  value      : Value | AssetRef       // literal value or asset reference
  type       : TypeRef
  source     : InputSource            // pkp-artifact | parent-output | config | constant
}
```

The adapter framework resolves the node's inputs before invoking the adapter. The adapter receives resolved values, not references (except for large assets, which are passed as `AssetRef` and resolved via ATLAS or the local cache).

---

## 4. The Capability Registry

The capability registry is the runtime's directory of adapters. It maps a **capability** (e.g., `image-generation`) to one or more adapters that provide it.

### 4.1 Capability

```
Capability : String       // e.g., "image-generation", "voice-synthesis", "audio-mixing", "video-assembly"
```

Capabilities are domain-specific. Cinema capabilities (`010` §5.1):

| Capability | Local provider (cinema) | Cloud provider (optional) |
|---|---|---|
| `image-generation` | Stable Diffusion / FLUX | cloud image API |
| `video-generation` | SVD-XT | cloud video API |
| `voice-synthesis` | edge-tts | cloud TTS API |
| `music-generation` | procedural (numpy) | MusicGen / AudioLDM |
| `audio-mixing` | FFmpeg | cloud mixing API |
| `video-assembly` | FFmpeg | cloud assembly API |
| `subtitle-generation` | text generation | cloud API |

Non-cinema domains define their own capabilities (e.g., `book-typesetting`, `game-level-baking`). The capability namespace is open; new capabilities are added by registering adapters for them.

### 4.2 Registry entry

```
RegistryEntry {
  adapter_id      : AdapterId
  adapter_version : SemVer
  capabilities    : List<Capability>
  priority        : Int               // for selecting between multiple adapters for the same capability
  locality        : Locality          // local | cloud
  constraints     : List<Constraint>   // e.g., "requires-gpu", "requires-network"
  health          : HealthStatus      // last known health
}
```

### 4.3 Resolution

The resource resolver (S5) resolves an adapter identity to a concrete adapter instance via the registry:

```
CapabilityRegistry.resolve(capability, constraints) → AdapterId
```

Resolution rules (in priority order):

1. **Locality**: prefer `local` over `cloud` (`010` §11.2, `00` §3.4).
2. **Priority**: higher-priority adapters win (PKP-declared or config-declared).
3. **Constraints**: the adapter must satisfy all declared constraints (e.g., `requires-gpu`).
4. **Health**: the adapter must be healthy (last health check passed).
5. **EIR version**: the adapter must support the EIR's schema version.

If no adapter satisfies all rules, the resolver emits `no-provider-available` and uses the fallback (if any).

### 4.4 Fallback

Each capability may declare a fallback adapter. Fallbacks are used when the primary adapter fails or is unavailable (`010` §8.2). Fallback selection is recorded in the execution report.

```
Fallback {
  primary   : AdapterId
  fallback  : AdapterId
  condition : FallbackCondition    // primary-failed | primary-unavailable | quality-below-threshold
}
```

---

## 5. Provider Abstraction

The provider abstraction is the architectural enforcement of platform independence (`010` §11). The runtime does not know whether a provider is local or cloud; it knows only the capability interface.

### 5.1 Local vs cloud

- **Local providers** run in-process or as local subprocesses (Ollama, Stable Diffusion, edge-tts, FFmpeg). They require no network access beyond loopback (for local model servers).
- **Cloud providers** run behind a network API. They require network access (non-loopback), gated by the capability policy (S25).

Both sit behind the same capability interface. The adapter hides the difference; the runtime sees only `Adapter.invoke(node, inputs, context) → AdapterResult`.

### 5.2 Provider swapping

A provider is swapped by updating the registry (registering a new adapter, or changing the priority). No engine code changes (`010` §10.1). The new adapter must satisfy the determinism requirements (§7) and the capability interface.

### 5.3 Provider versioning

Every adapter records its `adapter_version` and the provider's version (if different) in the execution report. This enables replay with the same version or regeneration with a different version (`010` §9.4).

---

## 6. Adapter Lifecycle

```
load ──► health_check ──► invoke* ──► unload
```

### 6.1 Load

The plugin framework (S26) loads the adapter plugin. Loading checks:

- The adapter manifest declares the adapter's capabilities, constraints, and required runtime capabilities.
- The adapter's required runtime capabilities (filesystem read, network, subprocess) are permitted by the security policy (S25). If not, the adapter is rejected at load time.
- The adapter's `supported_eir_versions` intersect the runtime's EIR version. If not, the adapter is rejected.

### 6.2 Health check

After load, the runtime calls `health_check()`. The adapter verifies its provider is available (e.g., the local model server is running; FFmpeg is installed). A failed health check marks the adapter `unhealthy`; the resolver skips it.

### 6.3 Invoke

The runtime calls `invoke(node, inputs, context)` for each EIR node the adapter is dispatched to execute. The adapter:

1. Reads the node's binding, parameters, seed, validation spec, provenance stub.
2. Resolves any secrets via the `context.config` (never stored in the EIR).
3. Checks the `context.security` for the capabilities it needs (network, subprocess).
4. Invokes the provider (local or cloud).
5. Runs the ValidationSpec checks on the output.
6. Emits events via `context.event_bus` (at least: invoke-start, invoke-end, validation-result).
7. Records metrics (duration, resource usage, provider latency).
8. Returns `AdapterResult`.

### 6.4 Unload

At runtime shutdown, the adapter is unloaded. The adapter releases resources (model memory, network connections, file handles).

---

## 7. Determinism

Adapters participate in the runtime's determinism (Invariant 7.1 from `DESIGN/001`). The determinism mode is declared per-node in the EIR (`DESIGN/004` §3.6):

### 7.1 Seed-based determinism

For providers that support seeding (most image, video, and music generation models), the adapter:

- Receives the seed from the EIR node.
- Passes the seed to the provider.
- The same seed + same provider version ⇒ same output.

The adapter records the seed and the provider version in the result metrics for provenance.

### 7.2 Recorded-output determinism

For providers that are irreducibly non-deterministic (some cloud APIs, some TTS systems), the adapter uses the recorded-output fallback (`010` §9.3):

- On first render, the adapter invokes the provider and records the specific output (the media file) in ATLAS, with the provider version and the invocation parameters.
- On replay, the adapter does not re-invoke the provider; it reads the recorded output from ATLAS.
- The recorded output is the deterministic result for that `(node, provider version, parameters)` tuple.

This ensures determinism even for non-deterministic providers, at the cost of storing the output. The stored output is the media itself (stored in ATLAS regardless), so the fallback adds no storage overhead.

### 7.3 Determinism requirements for new adapters

A new adapter must:

- Declare its `DeterminismMode` (seed-based or recorded-output).
- If `seed-based`, pass the determinism test (two invocations with the same seed + same version produce byte-identical outputs, within a tolerance defined by ADR).
- If `recorded-output`, implement the recorded-output protocol (record on first render, replay on subsequent renders).

An adapter that cannot satisfy either is rejected at registration.

---

## 8. Failure Classification

Adapters classify their own failures via `classify_failure(error) → FailureClass`. The failure recovery engine (S16) uses this classification to decide retry, fallback, or fatal-termination (`DESIGN/012`).

| Failure class | Meaning | Recovery |
|---|---|---|
| `recoverable` | Transient; retry may succeed. | Retry per retry strategy. |
| `retryable` | Retryable with backoff. | Retry per retry strategy. |
| `fatal` | Unrecoverable; the node cannot execute. | Mark `failed`; continue other nodes. |
| `adapter` | The adapter itself failed (bug, misconfiguration). | Retry once; if persists, fatal. |
| `resource` | Resource exhaustion (OOM, GPU unavailable). | Serialize; if persists, fatal. |
| `validation` | The output failed the ValidationSpec. | Retry with fallback; if persists, fatal. |
| `gap` | The EIR node is missing a required detail. | Mark `rendering-gap`; continue. |
| `constitutional` | The node violates a constitutional invariant. | Fatal; emit `constitutional-violation`. |

---

## 9. Adding a New Adapter

A new adapter is added by:

1. Implementing the adapter interface (§3) in any language (via the SDK).
2. Declaring the adapter's capabilities, constraints, and required runtime capabilities in a manifest.
3. Registering the adapter in the capability registry (via config or a plugin manifest).
4. Passing the determinism test (§7.3).
5. Passing the health check (§6.2).

No engine code changes. No runtime rebuild. The runtime picks up the new adapter via the registry (`010` §10.1).

---

## 10. Adding a New Media Type

A new media type (e.g., 3D models, VR scenes) is added by:

1. Defining a new capability (e.g., `model-generation`).
2. Implementing an adapter for the new capability.
3. Registering the adapter.
4. The PKP can now declare artifacts that require the new capability.

New media types require PKP and COM extensions (`010` §10.2), coordinated under the Constitution. The runtime itself does not change.

---

## 11. The Adapter Contract with the Runtime

| Aspect | Adapter's obligation | Runtime's obligation |
|---|---|---|
| **Input** | Reads the EIR node only. | Provides the EIR node + resolved inputs. |
| **Output** | Returns AdapterResult. | Records the result; handles failure classification. |
| **Determinism** | Declares and satisfies DeterminismMode. | Records seed + version; uses recorded-output fallback. |
| **Provenance** | Records version + seed + params. | Stamps provenance at emission. |
| **Events** | Emits invoke-start, invoke-end, validation-result. | Delivers events via the event bus. |
| **Capabilities** | Declares required runtime capabilities. | Rejects at load time if exceeded. |
| **Secrets** | Resolves secrets via context.config. | Never puts secrets in the EIR. |
| **Creativity** | Never invents; reports gaps. | Never asks the adapter to invent. |
| **Providers** | Calls providers (local or cloud). | Does not call providers directly. |

---

## 12. What This Document Does Not Define

- The EIR schema — that is `DESIGN/004`.
- The scheduler's dispatch algorithm — that is `DESIGN/011`.
- The failure recovery engine's full classification logic — that is `DESIGN/012`.
- The plugin framework's loading and sandboxing — that is `DESIGN/015`.
- The security policy — that is `DESIGN/015`.

This document defines the adapter interface, the capability registry, and the provider abstraction. The internals of plugin loading and security are in `DESIGN/015`.

---

## 13. ADR Candidates Surfaced

| Candidate | Decision | Blocking milestone |
|---|---|---|
| 0018 | Adapter invocation protocol (in-process / subprocess / IPC) | M2 |
| 0030 | Determinism tolerance (byte-identical / hash-identical / perceptual) | M0 |
| 0031 | Recorded-output storage policy (when to record; retention) | M2 |
| 0032 | Adapter manifest format (TOML / YAML / JSON) | M0 |
| 0033 | Capability namespace governance (open / registered) | M5 |
| 0034 | Cloud adapter authentication (per-adapter / global) | M3 |

---

## 14. Cross-References

| Reference | Relevance |
|---|---|
| `010` §5 (Runtime Services) | The capability registry; the provider abstraction. |
| `010` §10 (Runtime Extensibility) | New providers; new media types; new runtimes. |
| `010` §11 (Platform Independence) | Local-first, cloud-capable. |
| `DESIGN/004` | EIR (the adapter's input). |
| `DESIGN/012` | Failure recovery (uses adapter failure classification). |
| `DESIGN/015` | Plugin framework + security. |

---

**End of PROMETHEUS-006.**