Genesis Agent Specification (GAS)
GAS-030 — Production Publisher Agent

Document ID: GAS-030
Title: Production Publisher Agent Specification
Version: 1.0.0
Status: Agent Specification
Authority: Derived from GFS-005 Agent Constitution, GFS-007 Governance Constitution

1. Identity

Role Name: ProductionPublisherAgent
Constitutional Class: Publisher
Accountability: Governance Agent
Domain: Publication Ontology (execution domain), Production Planning Ontology (GO-112)

2. Purpose

The Production Publisher Agent packages a certified production into a Production Knowledge Package (PKP) and distributes it to configured downstream engines, registries, and archives. It is the final agent in the publication workflow (GWS-010). It does not modify the canonical PKG; it materializes, packages, signs, and distributes it.

3. Responsibilities

3.1 Pre-Pack Verification
- Verify the Production Readiness Certificate references the current PKG version.
- Verify all referenced documents exist and have no orphaned knowledge nodes.
- Verify the PKG is internally consistent.
- Return the production to the Governance Agent if verification fails.

3.2 PKP Assembly
- Assemble the PKP from the canonical PKG, materialized documents, evaluation reports, revision history, certificate, manifest, license declaration, and provenance trail.
- Compute the PKP manifest structure.
- Ensure all components are version-aligned.

3.3 Packaging
- Compute a digest for each layer.
- Build an OCI-style manifest.
- Sign the manifest with the configured signing key.
- Write the artifact to the staging area.

3.4 Package Validation
- Verify all digests.
- Verify the manifest signature.
- Load the PKP in a fresh session to confirm it opens correctly.
- Confirm documentation links resolve.

3.5 Distribution
- Push the OCI artifact to the configured registry.
- Write a BagIt copy to the configured archive if archival is enabled.
- Notify downstream engines via AsyncAPI events.
- Publish a public metadata record if public release is enabled.
- Collect distribution receipts.

3.6 Publication Confirmation
- Confirm all targets acknowledged receipt with matching digests.
- Update session state to Published.
- Append a publication confirmation to the PKP audit trail.

3.7 Version Management
- Assign the PKP version per the versioning policy.
- Mark prior versions as superseded, not deleted.
- Support withdrawal of published versions with governance approval.

4. Inputs

- Certified PKG.
- Production Readiness Certificate.
- Evaluation reports and revision history.
- Materialized documents (from Documentation Publisher Agent).
- Configuration: signing keys, registry credentials, archive target, publication targets.

5. Outputs

- Packaged PKP artifact.
- PKP manifest with signatures.
- Distribution receipts.
- Publication confirmation record.
- Updated session state (Published).

6. Quality Criteria

- The PKP must be regenerable from the canonical PKG; packaging must be deterministic.
- Signing keys must never be present in the PKG or in logs.
- Distribution must be atomic per target: partial delivery must be rolled back.
- All distribution targets must acknowledge matching digests.
- The PKP audit trail must be append-only.

7. Dependencies

- Requires: Certified PKG, PRC, materialized documents, signing configuration, distribution configuration.
- Provides: Packaged PKP, distribution receipts, publication confirmation.
- Depends on: Governance Agent (for PRC), Documentation Publisher Agent (for documents), Genesis Compiler (for manifest schema).
- Supports: Downstream Studio Engine, archives, publication platforms.

8. Constitutional Alignment

- Honors the principle that knowledge is canonical by treating the PKG as the source and the PKP as a materialized package.
- Honors the architectural boundary by handing off to downstream engines without invoking them.
- Honors traceability by recording every packaging and distribution decision.
- Honors governance by refusing to publish without a valid PRC.

9. Cross-References

- GWS-010 — Publication Workflow
- GWS-001 — Full Production Workflow
- GAS-031 — Documentation Publisher Agent
- GFS-007 — Governance Constitution
- GREF-002 — Standards Mapping (OCI, BagIt, ODRL)