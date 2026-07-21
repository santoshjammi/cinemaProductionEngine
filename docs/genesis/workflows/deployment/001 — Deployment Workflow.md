Genesis Workflow Specification (GWS)
GWS-011 — Deployment Workflow

Document ID: GWS-011
Title: Deployment Workflow
Version: 1.0.0
Status: Workflow Specification
Authority: Derived from GFS-000, GFS-005

1. Purpose

This workflow defines how the Genesis Engine itself is deployed. It covers local setup for individual creators, cloud deployment for teams, configuration management, and the boundaries between Genesis and the downstream Studio Engine. This workflow is about deploying the engine, not about running a production.

2. Deployment Models

2.1 Local-First
- Target: Single creator workstation.
- Storage: SQLite database for the PKG, sqlite-vec for embeddings, local filesystem for artifacts.
- Compute: In-process agents, optional local task queue.
- Network: Optional; only required for research agent and registry push.
- Rationale: Honors the implementation-independence and creator-control principles.

2.2 Team
- Target: Small studio shared environment.
- Storage: Shared Postgres with pgvector, shared filesystem or S3-compatible object store.
- Compute: Shared worker pool (Celery/RQ or equivalent), shared orchestrator instance.
- Network: Internal network; egress for research and publishing.
- Rationale: Multiple contributors collaborating on a PKG with shared state.

2.3 Cloud
- Target: Scalable multi-tenant or large studio deployment.
- Storage: Managed Postgres, managed object store, managed vector store.
- Compute: Containerized agents with autoscaling; managed queue.
- Network: VPC-isolated core, public-facing publication endpoints only.
- Rationale: Production-scale throughput and high availability.

3. Deployment Stages

3.1 Stage D0: Prerequisites Check

Operator: Deployer (human or automation)
Input: Deployment configuration
Output: Prerequisites Report

Verify:
- Runtime version matches the Genesis specification version.
- Required external tools (ffmpeg, sqlite-vec, embedding model) are available or reachable.
- Signing keys and registry credentials are configured.
- The constitutional documents are present and unmodified relative to their recorded digests.

3.2 Stage D1: Configuration Load

Operator: Deployer
Input: Configuration file
Output: Loaded configuration

Load:
- Storage backends (PKG store, vector store, artifact store).
- Agent registry mapping role names to implementations.
- Workflow definitions (GWS-NNN).
- Schema set (GSS-NNN) and ontology set (GO-NNN) to activate.
- Territory rules and compliance configuration.
- Signing and publication configuration.

3.3 Stage D2: Schema and Ontology Compilation

Operator: Genesis Compiler
Input: GSS schemas, GO ontologies
Output: Compiled validators, SHACL shapes, JSON Schema artifacts

The compiler turns declarative Genesis specifications into executable validators:
- GSS → JSON Schema and SHACL shapes.
- GO → OWL ontologies and Pydantic models.
- GWS → executable workflow definitions.

Compilation failures halt deployment. No partial deployment is permitted.

3.4 Stage D3: Registry Seeding

Operator: Genesis Compiler
Input: Compiled artifacts, agent registry
Output: Populated registry

The compiled schemas, ontologies, workflows, and agent bindings are written to the registry. The registry is the source of truth for what the deployment can do.

3.5 Stage D4: Service Start

Operator: Deployer
Input: Populated registry
Output: Running services

Start:
- Orchestrator service.
- Agent workers.
- Validation service.
- Publication service (if enabled).
- API surface (OpenAPI-defined endpoints).
- Event surface (AsyncAPI-defined channels).

3.6 Stage D5: Smoke Test

Operator: Deployer
Input: Running services
Output: Smoke Test Report

Run a synthetic brief through a minimal workflow:
- Brief accepted.
- Discovery produces a stub PKG.
- Validation runs.
- A stub PKP is packaged.
- Publication is exercised against a throwaway target.

Failures halt the deployment and roll back services started in Stage D4.

3.6 Stage D6: Declaration of Readiness

Operator: Deployer
Input: Smoke Test Report
Output: Deployment Record

The deployment is recorded with:
- Genesis specification version.
- Compiled schema and ontology digests.
- Agent bindings and versions.
- Deployment timestamp and operator identity.

The engine is now ready to accept production briefs.

4. Configuration Management

4.1 Configuration Sources
- Base configuration shipped with the engine.
- Site configuration supplied by the operator.
- Environment variables for secrets.
- No secrets in files. No secrets in the registry.

4.2 Configuration Validation
- Configuration is itself validated against a GSS schema.
- Unknown fields fail validation. Genesis does not silently ignore configuration.

4.3 Configuration Reload
- Non-destructive configuration changes (agent bindings, workflow tuning) may be reloaded without restart.
- Destructive changes (storage backend change, schema set change) require a clean redeployment.

5. Boundary with Studio Engine

- Genesis and the Studio Engine are deployed independently.
- The only contract between them is the PKP delivered through the publication workflow (GWS-010).
- Genesis never invokes Studio Engine components.
- Studio Engine components read the PKP via the configured registry or archive.

6. Upgrades

- Upgrades follow the governance amendment workflow for constitutional documents.
- Schema and ontology upgrades are versioned. Existing PKGs must be migratable or marked read-only.
- Engine upgrades are tested against the smoke test before being declared ready.
- A failed upgrade rolls back to the prior deployment record.

7. Failure Handling

- Prerequisites failure: halt, report, do not deploy.
- Compilation failure: halt, report, do not partial-deploy.
- Service start failure: roll back started services, report.
- Smoke test failure: roll back the full deployment, preserve logs for diagnosis.

8. Cross-References

- GFS-000 — Constitutional Charter (sections 15, 16)
- GFS-005 — Agent Constitution
- GWS-010 — Publication Workflow
- GREF-004 — External References