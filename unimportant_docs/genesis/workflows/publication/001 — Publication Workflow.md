Genesis Workflow Specification (GWS)
GWS-010 — Publication Workflow

Document ID: GWS-010
Title: Publication Workflow
Version: 1.0.0
Status: Workflow Specification
Authority: Derived from GFS-007, GWS-001

1. Purpose

This workflow defines how a certified production is packaged into a Production Knowledge Package (PKP) and distributed to downstream engines, archives, and publication targets. It begins after the Governance Agent issues the Production Readiness Certificate and ends when the PKP is delivered to its configured destinations.

2. Preconditions

- Production state is Certifying or Certified.
- Production Readiness Certificate (PRC) has been issued by the Governance Agent.
- All validation gates from GWS-001 have passed.
- No critical issues are unresolved.
- The PKG is internally consistent and version-locked.

3. Workflow Stages

3.1 Stage P0: Pre-Pack Verification

Agent: Production Publisher Agent
Input: PKG, PRC, evaluation reports
Output: Pre-Pack Verification Report

The Production Publisher Agent re-verifies that the PKG and PRC are coherent before packaging. It checks that the certificate references the current PKG version, that all referenced documents exist, and that no orphaned knowledge nodes remain. If verification fails, the workflow returns the production to the Governance Agent.

3.2 Stage P1: PKP Assembly

Agent: Production Publisher Agent
Input: Verified PKG, PRC, manifests
Output: PKP draft

The agent assembles the PKP from:
- The canonical PKG (JSON-LD serialization plus RDF backup).
- Materialized documents (screenplay, scene plan, shot plan, prompts, music score).
- Evaluation reports and revision history.
- The Production Readiness Certificate.
- The manifest declaring structure, version, and contents.
- The license declaration from the brief and confirmed at certification.
- The provenance and audit trail.

3.3 Stage P2: Documentation Generation

Agent: Documentation Publisher Agent
Input: PKG
Output: Human-readable documentation set

The Documentation Publisher Agent materializes documentation views from the canonical PKG:
- Production overview document.
- Character and world reference documents.
- Scene-by-scene production guide.
- AI involvement and provenance summary.
- Accessibility and compliance summary.

All documentation is a materialized view. The canonical source remains the PKG.

3.4 Stage P3: Packaging

Agent: Production Publisher Agent
Input: PKP draft, documentation set
Output: Packaged PKP artifact

The agent packages the PKP as a content-addressed artifact:
- Computes a digest for each layer (PKG, documents, certificate, manifest).
- Builds an OCI-style manifest referencing the layers.
- Signs the manifest using the configured signing key.
- Writes the artifact to the local staging area.

3.5 Stage P4: Validation of the Package

Agent: Production Publisher Agent
Input: Packaged PKP
Output: Package Validation Report

The agent validates the package before distribution:
- Verifies all digests.
- Verifies the manifest signature.
- Confirms the package opens and the PKG loads in a fresh session.
- Confirms documentation renders and links resolve.

If validation fails, packaging is re-run from Stage P3. If it fails twice, the workflow escalates to the Governance Agent.

3.6 Stage P5: Distribution

Agent: Production Publisher Agent
Input: Validated PKP
Output: Distribution Receipts

The agent distributes the PKP to configured targets:
- Pushes the OCI artifact to the configured registry.
- Writes a BagIt copy to the configured archive if archival is enabled.
- Notifies configured downstream engines via AsyncAPI events.
- Publishes a public metadata record (schema.org / Dublin Core) if public release is enabled.

Each target produces a receipt recorded in the manifest.

3.7 Stage P6: Publication Confirmation

Agent: Production Publisher Agent
Input: Distribution receipts
Output: Publication Confirmation

The agent confirms successful distribution:
- All configured targets acknowledged receipt.
- Digests at targets match source digests.
- The session state is updated to Published.
- A final publication confirmation is appended to the PKP audit trail.

4. Versioning

4.1 Initial Publication
- The first published PKP for a production is version 1.0.0.
- The version is recorded in the manifest and in the PRC.

4.2 Revisions
- A revision that changes the PKG increments the minor version (e.g., 1.0.0 → 1.1.0).
- A revision that changes the production scope or territory increments the major version.
- A re-packaging without PKG changes increments the patch version.
- Every version is immutable once published. New versions are new artifacts.

4.3 Withdrawn Versions
- A published version may be marked withdrawn. Withdrawn versions remain in the registry for audit but are no longer the active version.
- Withdrawal requires governance approval and is recorded in the audit trail.

5. Failure Handling

- Failure at Stage P0 returns the production to certification.
- Failure at Stage P3 or P4 retries once, then escalates.
- Failure at Stage P5 rolls back partial distribution: any target that received the artifact is notified of the failed publication; the artifact is tombstoned at those targets.
- Failure at Stage P6 leaves the production in Published state but flags the session for manual review.

6. Security

- Signing keys are configured at deployment time and never stored in the PKG.
- Distribution targets are authenticated with deployment-scoped credentials.
- The PKP audit trail is append-only.

7. Cross-References

- GWS-001 — Full Production Workflow (stages 0–9)
- GFS-007 — Governance Constitution
- GAS-NNN — Production Publisher Agent, Documentation Publisher Agent
- GREF-002 — Standards Mapping (OCI, BagIt, ODRL)
- GREF-005 — Compliance Considerations