Genesis Runtime (GRT)
GRT-002 — Session Configuration

Document ID: GRT-002
Title: Session Configuration
Version: 1.0.0
Status: Runtime
Authority: Derived from GFS-000, GFS-005, GFS-009

1. Purpose

The Session Configuration defines the per-production, per-session parameters that govern a single execution of a Genesis pipeline. Where runtime configuration (GRT-001) is stable across sessions, session configuration is scoped: it names the production, the workflow, the active agents, the active ontologies, and the per-session limits.

In Genesis, a session is one execution of a pipeline against one production. Multiple sessions may run concurrently on the same runtime, each with its own session configuration. Sessions are isolated: they do not share staging buffers, do not share trace IDs, and do not read each other's in-flight writes.

2. Configuration Scope

Session configuration covers:

- Session identity — session ID, production ID, trace ID, parent session (for revisions).
- Production reference — the Production Brief or the resumed PKG snapshot.
- Pipeline selection — which pipeline (Discovery / Creative / Production / Evaluation) this session runs.
- Workflow manifest — the workflow spec this session follows.
- Active ontologies — the ontology versions this session pins.
- Active agents — the agent versions this session pins.
- Active rules — the Reasoning Catalog rules this session applies.
- Per-session overrides — confidence floors, SLAs, fan-out parallelism, barrier timeout.
- Checkpoint policy — checkpoint interval (time-based or stage-based).
- Resume policy — whether this session resumes from a checkpoint or starts fresh.
- Audit scope — whether the audit log captures full provenance or summary only.

3. Configuration File

Session configuration is stored as a YAML file at `runtime/sessions/<session_id>.yaml` and is committed to the PKG at session start. The file is versioned with the session (a session restart may bump the version if the resume policy changes).

Schema sketch:

    session:
      session_id: "sess-2026-07-19-0001"
      production_id: "prod-0421"
      trace_id: "trace-0421-001"
      parent_session: null
      version: "1.0.0"

    production:
      brief_ref: "pkg://prod-0421/brief"
      resume_from: "pkg://prod-0421/checkpoint-12"
      resume_policy: "from_checkpoint"

    pipeline:
      type: "creative"
      manifest: "docs/genesis/pipelines/002 — Creative Pipeline.md"
      workflow: "docs/genesis/workflows/GWS-001 — Full Production Workflow.md"

    ontologies:
      pins:
        GO-001: "1.0.0"
        GO-101: "1.3.0"
        GO-104: "1.3.0"
        GO-105: "1.2.0"

    agents:
      pins:
        GAS-004: "1.0.0"
        GAS-005: "1.0.0"
        GAS-006: "1.0.0"

    rules:
      catalog_version: "1.2.0"
      apply_candidate_rules: false

    overrides:
      confidence_floor: 0.75
      coherence_score_floor: 0.65
      fan_out_parallelism: 4
      barrier_timeout_seconds: 1800

    checkpoint:
      mode: "stage_boundary"
      interval_minutes: 30

    audit:
      provenance: "full"

4. Pinning

Session configuration pins ontology versions, agent versions, and rule catalog versions so that a session's results are reproducible. A session that starts against GO-104 v1.3.0 must complete against GO-104 v1.3.0 — a mid-session ontology bump is forbidden. If an ontology bumps mid-session, the session must checkpoint, retire, and a new session starts against the new version.

Pinning applies to:

- Ontologies — exact version.
- Agents — exact prompt version.
- Reasoning Catalog — exact catalog version.
- Workflow manifest — exact manifest version.

Unpinned sessions default to the runtime's current version of each resource. Production sessions must pin; dev sessions may leave defaults.

5. Resume Policy

A session may resume from a checkpoint or start fresh.

- Fresh — the session starts at the pipeline's first stage with the referenced Production Brief.
- From checkpoint — the session loads the referenced checkpoint and resumes at the next stage. The checkpoint's PKG snapshot is the starting state; the session's staging buffer is empty.
- From revision — the session is a revision session. The parent session is named, the revised subgraph is the starting state, and the session runs only the affected stages.

Resume policy is validated at session start: a from-checkpoint session whose checkpoint does not exist is fatal; a from-revision session whose parent session is not complete is fatal.

6. Checkpoint Policy

Checkpoints are committed per the Operational Memory System:

- Stage boundary — checkpoint after every stage completion.
- Time-based — checkpoint every N minutes (default 30).
- Size-based — checkpoint when the staging buffer exceeds a threshold.

Checkpoint contents:

- PKG snapshot (immutable).
- Staging buffer state.
- Decision Records committed so far.
- Session configuration version.
- Trace ID.

Checkpoints are named `checkpoint-<stage>-<sequence>` and stored under `data/sessions/<session_id>/checkpoints/`.

7. Isolation

Concurrent sessions are isolated:

- Each session has its own staging buffer under `data/sessions/<session_id>/staging/`.
- Each session has its own trace ID; events do not cross sessions.
- Each session reads a snapshot of the PKG at session start; it does not see other sessions' in-flight writes.
- Merge to the live PKG happens only at session completion, under the merge protocol (GP-WF-002 §5).

A session that attempts to read another session's staging buffer is a fatal error.

8. Lifecycle

A session moves through:

    Initialized → Running → Checkpointing → Running → ... → Completed | Failed | Cancelled

- Initialized — session config validated, pinned versions loaded.
- Running — pipeline executing.
- Checkpointing — a checkpoint is committed; the session briefly pauses.
- Completed — pipeline finished; PKG merge committed.
- Failed — a fatal error occurred; the session is retired with a Failure Record.
- Cancelled — a human or governance cancelled the session; the session is retired with a Cancellation Record.

9. Anti-Patterns

- Running a production session without pinning ontology versions.
- Resuming from a checkpoint that belongs to a different production.
- Letting two sessions share a staging buffer.
- Bumping an ontology mid-session without retiring the session.
- Setting the checkpoint interval too long — long intervals lose work on failure.
- Setting the audit scope to summary for a production session — production sessions require full provenance.

10. Exit Criteria

Session configuration is complete when:

- The session YAML validates against the session schema.
- Every pinned version exists in the corresponding registry.
- The resume policy is valid against the referenced checkpoint or parent session.
- The pipeline and workflow manifest exist and are compatible.
- The session is committed to the PKG with its trace ID.