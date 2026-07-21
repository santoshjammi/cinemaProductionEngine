Genesis Architecture Specification (GAS)
GARCH-007 — Studio Handoff Specification

Document ID: GARCH-007
Title: Studio Handoff Specification
Version: 1.0.0
Status: Architecture Specification
Authority: Derived from GARCH-001 §6, GFS-000, GFS-007

1. Purpose

This document defines the exact interface and deliverables passed from Genesis to the Studio Engine. It specifies what the Studio Engine receives, how it consumes the handoff, and what it may never do.

The handoff is the only legal channel between Genesis and the Studio Engine. All other communication is forbidden.

2. The Handoff Boundary

Genesis terminates at the issuance of a certified Production Knowledge Package (PKP). The Studio Engine begins at the receipt of that PKP. The boundary is absolute:

- Genesis does not call into the Studio Engine.
- The Studio Engine does not write back into the live PKG.
- The Studio Engine may not query the live PKG.
- The Studio Engine may request a revision only by returning the PKP to Genesis.

3. Handoff Artifact

The handoff artifact is the certified PKP, as specified in GARCH-008. It is a single immutable, signed bundle containing:

- A frozen snapshot of the PKG at certification time.
- The full provenance ledger up to certification.
- The validation and governance approval records.
- The list of certified deliverables.
- The signature of the Governance Engine.
- The manifest of materializable views the Studio Engine may request.

4. Transport

The PKP is delivered through one of three transport modes:

4.1 File Handoff
The PKP is serialized to a versioned directory layout on shared storage. The Studio Engine reads the manifest file (`pkg-manifest.json`) and resolves referenced artifacts.

4.2 API Handoff
The PKP is published to the Genesis REST/GraphQL API under a stable, immutable URL. The Studio Engine fetches it with a single authenticated request.

4.3 Event Handoff
The PKP is announced on the message bus with a `pkg.certified` event. Subscribers receive a reference and fetch the full bundle via API or file.

All three modes deliver identical content. The mode is a deployment choice, not a semantic one.

5. What the Studio Engine Receives

The Studio Engine receives, at minimum:

- The complete narrative structure (themes, arcs, scenes, beats).
- The complete character registry with profiles, voices, and arcs.
- The complete world/environment registry.
- The complete shot plan with composition, blocking, and camera intent.
- The complete dialogue and subtitle manifests.
- The complete score and SFX plans.
- The complete style and visual language references.
- The prompt manifests for every generable asset.
- The validation findings (resolved) and governance approval.
- The provenance ledger.

6. How the Studio Engine Consumes It

The Studio Engine:

6.1 Reads the manifest first to discover available projections.
6.2 Requests materialized views through the Genesis Materialization Service (read-only).
6.3 Uses prompt manifests as inputs to provider calls.
6.4 Reports asset references back to its own asset registry (not to the PKG).
6.5 Emits production telemetry to its own logs (not to the PKG).

7. What the Studio Engine May Not Do

- Write to the PKG.
- Modify the PKP.
- Bypass the manifest to read raw PKG internals.
- Cache the PKP beyond its declared validity window without re-validation.
- Re-certify or self-approve any change to Genesis knowledge.
- Reach into Genesis agents, workflows, or runtime internals.

8. Revision Protocol

When the Studio Engine requires a change to certified knowledge:

8.1 It returns the PKP to Genesis with a revision request.
8.2 The Revision Agent (GAS-027) opens a new workflow against the returned PKP.
8.3 Genesis re-validates, re-approves, and emits a new PKP version.
8.4 The old PKP is marked superseded but retained for audit.

The Studio Engine never edits Genesis knowledge directly. It only ever consumes a new PKP version.

9. Validity and Expiry

A PKP is valid from its certification timestamp until either:

- It is superseded by a newer version.
- Its declared expiry elapses (production-specific).
- The Governance Engine revokes its approval.

Expired PKPs remain readable for audit but may not be used for new production work.

10. Signatures and Integrity

Every PKP carries:

- A content digest of every included artifact.
- A signature from the Governance Engine.
- A chain of provenance back to the original creative intent.

The Studio Engine must verify the signature before consuming the PKP. Verification failure is a hard error.

11. Non-Goals

This specification does not define:

- The internal storage format of the Studio Engine.
- The provider selection logic used by the Studio Engine.
- The rendering or publishing pipelines of the Studio Engine.
- Any aspect of media generation.

Those concerns belong to the Studio Engine specifications, not to Genesis.

12. Approval

This specification is binding for every implementation of the Genesis-to-Studio boundary. Any deviation requires a constitutional amendment.