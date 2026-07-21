Genesis Runtime (GRT)
GRT-001 — Runtime Configuration

Document ID: GRT-001
Title: Runtime Configuration
Version: 1.0.0
Status: Runtime
Authority: Derived from GFS-000, GFS-005, GFS-009

1. Purpose

The Runtime Configuration defines the static configuration of a Genesis runtime instance — the engine-wide parameters, defaults, and resource declarations that govern how Genesis executes. Runtime configuration is distinct from session configuration (GRT-002): runtime config is per-instance and stable across sessions; session config is per-production and per-session.

In Genesis, runtime configuration is constitutional in spirit but operational in form. It does not change the Charter; it realizes the Charter in executable parameters.

2. Configuration Scope

Runtime configuration covers:

- Engine identity — instance ID, environment (dev / staging / prod), region.
- Model providers — the LLM, embedding, and reasoning model providers the engine may invoke.
- Ontology sources — paths to the active ontology tree, SHACL schemas, and the Reasoning Catalog.
- Registry sources — paths to the Ontology Registry, Agent Registry, Capability Registry.
- Event Bus — mode (in-process / distributed), retention, audit log path.
- Validation defaults — default confidence floors, default evidence class floors, default SLAs.
- Workflow defaults — default workflow manifest, default fan-out parallelism, default barrier timeout.
- Governance defaults — default approval chain templates, default escalation SLAs.
- Storage — PKG store path, staging buffer path, decision record store path.
- Logging — log level, log sink, audit log path.
- Limits — maximum PKG size, maximum fan-out branches, maximum revision retries.

3. Configuration File

Runtime configuration is stored as a YAML file at `runtime/runtime.yaml` (or `runtime.yaml` at the genesis root for instance-level overrides). The file is versioned with the same scheme as ontologies (MAJOR.MINOR.PATCH) and is itself registered as a knowledge artifact in the PKG.

Schema sketch:

    runtime:
      instance_id: "genesis-prod-01"
      environment: "prod"
      region: "us-east-1"
      version: "1.0.0"

    models:
      reasoning:
        provider: "..."
        model: "..."
        api_key_env: "GENESIS_REASONING_KEY"
      embedding:
        provider: "..."
        model: "..."
      governance:
        provider: "..."
        model: "..."

    ontology:
      root: "docs/genesis/ontology"
      schemas: "docs/genesis/schemas"
      reasoning_catalog: "docs/genesis/reasoning/Catalog.md"

    registries:
      ontology: "docs/genesis/registry/001 — Ontology Registry.md"
      agent: "docs/genesis/registry/002 — Agent Registry.md"
      capability: "docs/genesis/registry/003 — Capability Registry.md"

    event_bus:
      mode: "in-process"
      retention_days: 90
      audit_log: "logs/event_bus.log"

    validation:
      default_confidence_floor: 0.7
      default_evidence_floor: "Inferred"
      default_coherence_score_floor: 0.6

    workflow:
      default_manifest: "docs/genesis/workflows/GWS-001 — Full Production Workflow.md"
      default_fan_out_parallelism: 8
      default_barrier_timeout_seconds: 3600

    governance:
      default_approval_templates: "docs/genesis/governance/ApprovalTemplates.md"
      default_escalation_sla_hours: 4

    storage:
      pkg_store: "data/pkg"
      staging_buffer: "data/staging"
      decision_records: "data/decisions"

    logging:
      level: "info"
      sink: "file"
      audit_log: "logs/audit.log"

    limits:
      max_pkg_nodes: 100000
      max_fan_out_branches: 16
      max_revision_retries: 3

4. Loading Order

At startup, the runtime loads configuration in this order (later sources override earlier):

1. Built-in defaults compiled into the engine.
2. `runtime/runtime.yaml` (instance defaults).
3. Environment variables prefixed `GENESIS_` (e.g. `GENESIS_REASONING_KEY`).
4. CLI flags (one-shot overrides for a single run).

Each override is logged to the audit log with the source and the parameter changed.

5. Validation

At startup, the runtime validates the configuration:

- Every referenced registry path exists.
- Every referenced ontology root and schemas path exists.
- Every model provider is reachable (a lightweight ping).
- Every default confidence floor is in [0,1].
- Every default SLA is greater than zero.
- The environment is one of (dev / staging / prod).
- The instance ID is non-empty and unique within the deployment.

A startup validation failure is fatal — Genesis does not start with an invalid configuration.

6. Hot Reload

Runtime configuration supports hot reload for a limited parameter set:

- Logging level — may be raised or lowered at runtime.
- Default SLAs — may be tightened (loosening requires a restart).
- Fan-out parallelism — may be increased (decreasing requires a restart).
- Default confidence floors — may be raised (lowering requires a restart).

Hot reload is logged to the audit log. Parameters not in the hot-reload set require a restart.

7. Environment Profiles

Three environment profiles are predefined:

- dev — verbose logging, low SLAs, small limits, single-process event bus.
- staging — production-like config but with reduced model providers and smaller limits.
- prod — minimal logging, full SLAs, large limits, distributed event bus.

Switching profiles requires a restart. The active profile is recorded in the PKG at startup.

8. Anti-Patterns

- Storing secrets directly in the YAML. Use environment variables.
- Referencing registry paths that do not exist.
- Setting confidence floors to 0 — that disables validation.
- Setting SLAs to infinity — escalation never fires.
- Allowing prod to run with dev's small limits.
- Skipping startup validation — invalid config silently produces invalid runs.

9. Exit Criteria

Runtime configuration is complete when:

- The YAML file validates against the runtime schema.
- Every referenced path exists.
- Every referenced provider is reachable.
- Startup validation passes.
- The active profile is recorded in the PKG.
- The audit log captures the full loaded configuration (with secrets redacted).