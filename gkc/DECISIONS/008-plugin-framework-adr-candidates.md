# ADR Candidates — GKC-008 Plugin Framework

> Decisions surfaced by `DESIGN/008-plugin-framework.md`.

---

## ADR-Candidate-0044 — Plugin hot-reload

**Context.** § 3 does not mention hot-reload. Should the framework support it?

**Options.**
- **A. No.** Plugins are loaded at session start and unloaded at session end. Changes require a new session.
- **B. Yes, full hot-reload.** Plugins can be unloaded and reloaded mid-session.
- **C. Yes, but only for development.** A `--dev` mode allows hot-reload; production sessions do not.

**Recommendation.** A. No hot-reload. Simplicity and determinism favor session-scoped plugins. Developers can use short sessions or the `gkc plugin install` + new-session workflow. Hot-reload introduces cache-invalidation complexity.

**Blocking impact.** Blocks M0. Must be resolved before M0.

---

## ADR-Candidate-0045 — Cryptographic plugin signatures

**Context.** § 2.4 uses content hashes for integrity. Should plugins be cryptographically signed?

**Options.**
- **A. No, hash only.** Content hash verifies integrity; no provenance.
- **B. Optional signatures.** Plugins may include a signature; the framework verifies if present.
- **C. Required signatures for non-local plugins.** Plugins installed from outside the workspace require a signature.

**Recommendation.** A. Hash only for M0–M5. Signatures add key management and PKI complexity not justified for a local-first compiler. A later horizon can add B if plugin distribution becomes a trust problem.

**Blocking impact.** Blocks M0. Must be resolved before M0.

---

## ADR-Candidate-0046 — Built-in extensions as internal plugins

**Context.** § 9 says built-ins go through the same dispatch path. Should they be packaged as "internal plugins" with the same manifest format?

**Options.**
- **A. Same format.** Built-ins ship as plugin packages in a core directory; loaded identically.
- **B. Different format.** Built-ins are registered programmatically at startup; no manifest.
- **C. Same format, different load path.** Built-ins use the same manifest but load from a core directory, not the workspace's `plugins/`.

**Recommendation.** C. Same format, different load path. Same manifest ensures consistency and lets users override built-ins. Different load path keeps built-ins out of the user's plugin directory.

**Blocking impact.** Blocks M0 built-in registration. Must be resolved before M0.

---

## ADR-Candidate-0047 — Per-plugin capability policy

**Context.** § 5.2 specifies workspace-level capability policy. Should per-plugin overrides be allowed?

**Options.**
- **A. Workspace-level only.** One policy for all plugins. Simple.
- **B. Per-plugin overrides.** Each plugin can have a specific policy; workspace policy is the default.
- **C. Workspace policy + per-plugin grants.** Workspace sets the max; plugins can be granted less.

**Recommendation.** A. Workspace-level only. Per-plugin overrides add configuration complexity and break the "workspace is self-contained" invariant. If a plugin needs more capability, the workspace policy should be updated explicitly.

**Blocking impact.** Blocks M0. Must be resolved before M0.

---

## ADR-Candidate-0048 — Plugin priority field

**Context.** § 10.2 introduces a `priority` field for order-sensitive extension points. Is this in the manifest?

**Options.**
- **A. Yes, in the manifest per extension point registration.** Each registration has a `priority` field.
- **B. Yes, in a separate config file.** Priority is configured outside the manifest.
- **C. No.** Order is alphabetical by plugin id; no priority field.

**Recommendation.** A. In the manifest per registration. Authors know their priority needs; making it explicit is cleaner than alphabetical ordering. Default 100; lower runs first.

**Blocking impact.** Blocks M0 manifest schema. Must be resolved before M0.