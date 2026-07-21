Genesis Architecture Specification (GAS)
GARCH-008 — Production Knowledge Package Specification

Document ID: GARCH-008
Title: Production Knowledge Package Specification
Version: 1.0.0
Status: Architecture Specification
Authority: Derived from GARCH-001, GARCH-002, GARCH-007, GFS-003, GFS-006, GFS-007

1. Purpose

This document is the master specification for the Production Knowledge Package (PKP). It defines every component, its schema, its dependencies, and its validation rules. The PKP is the single artifact that crosses the Genesis-to-Studio boundary.

2. What the PKP Is

The PKP is a frozen, signed, immutable projection of the Production Knowledge Graph at the moment of certification. It is the authoritative input to the Studio Engine and the auditable record of every pre-production decision.

The PKP is *not* the PKG. The PKG is live and mutable; the PKP is a snapshot. The PKG is internal; the PKP is the export.

3. PKP Components

The PKP consists of the following components, each with its own schema:

3.1 Manifest (`pkg-manifest.json`)
Top-level index. Lists every other component, its digest, its schema version, and its location within the bundle.

3.2 PKG Snapshot (`pkg-snapshot.jsonl`)
A serialized projection of every assertion in the PKG at certification time. Format: one JSON object per line, each with id, type, properties, provenance, confidence, revision.

3.3 Provenance Ledger (`provenance-ledger.jsonl`)
Append-only record of every write to the PKG up to certification. Each entry: assertion id, agent id, source, evidence, timestamp, prior revision.

3.4 Validation Report (`validation-report.json`)
Every validation finding, its severity, its target assertion, its resolution state at certification.

3.5 Governance Record (`governance-record.json`)
Approval state, approver, approval timestamp, conditions, signature.

3.6 Deliverable Index (`deliverables.json`)
The list of certified deliverables the Studio Engine may produce from this PKP: image prompts, voice prompts, score cues, subtitle tracks, etc.

3.7 Materializable Views Index (`views-index.json`)
The list of projections the Studio Engine may request from the Genesis Materialization Service: screenplay, shot list, character bibles, world bible, score plan.

3.8 Ontology Reference (`ontology-ref.json`)
The set of ontology IDs (GO-NNN) and versions the PKG conforms to. Used by the Studio Engine to interpret concepts correctly.

3.9 Signature (`pkg-signature.json`)
Cryptographic signature over the manifest and all listed digests.

4. Component Schemas

4.1 Manifest Schema
```
{
  "pkgId": string (uuid),
  "version": string (semver),
  "certifiedAt": ISO8601,
  "expiresAt": ISO8601 | null,
  "components": [
    { "name": string, "path": string, "digest": string, "schemaVersion": string }
  ],
  "ontologyRefs": [ "GO-NNN@version" ],
  "genesisVersion": string
}
```

4.2 Assertion Schema (in snapshot)
```
{
  "id": string (uri),
  "type": string (GO concept),
  "properties": object,
  "provenance": { "agent": "GAS-NNN", "source": string, "evidence": [string], "timestamp": ISO8601 },
  "confidence": "EXPLICIT" | "CONFIRMED" | "INFERRED" | "ASSUMED" | "UNKNOWN",
  "revision": integer,
  "supersededBy": string | null
}
```

4.3 Validation Finding Schema
```
{
  "id": string,
  "severity": "blocking" | "major" | "minor" | "info",
  "target": string (assertion id),
  "rule": string (validation rule id),
  "message": string,
  "state": "open" | "resolved" | "waived",
  "resolvedBy": "GAS-NNN" | null
}
```

4.4 Governance Record Schema
```
{
  "approver": "GAS-NNN",
  "approvedAt": ISO8601,
  "conditions": [string],
  "signature": string,
  "signatureAlgorithm": string
}
```

5. Dependencies

The PKP depends on:

- The Core and Domain Ontologies (GO-001 through GO-119) for concept typing.
- The Semantic Relationship Catalog (GO-002) for relationship typing.
- The Validation Engine for the validation report.
- The Governance Engine for the governance record and signature.
- The Provenance Ledger for the audit trail.

A PKP cannot be assembled if any of these dependencies are missing or inconsistent.

6. Validation Rules

A PKP is valid only if all of the following hold:

- R1 Manifest lists every required component.
- R2 Every component digest matches the manifest.
- R3 Every assertion in the snapshot conforms to a registered ontology concept.
- R4 Every assertion has complete provenance (agent, source, timestamp).
- R5 Every assertion has a confidence classification.
- R6 No blocking validation findings remain open.
- R7 Governance approval is present and signed.
- R8 Every deliverable in the deliverable index is derivable from the snapshot.
- R9 Every ontology reference resolves to a registered ontology version.
- R10 The signature verifies against the manifest and all digests.

A PKP that fails any rule is rejected at the boundary. The Studio Engine must refuse to consume it.

7. Versioning

A PKP is versioned with semver. A new version is issued whenever:

- The underlying PKG is revised after certification.
- The ontology references change.
- The governance approval is re-issued.

Old versions are retained indefinitely for audit. They are never edited in place.

8. Read-Only Guarantee

Once certified, a PKP is read-only. No component may be modified, re-signed, or re-issued in place. Corrections require a new version with a new signature and a new provenance entry explaining the correction.

9. Storage Layout

When delivered as a file handoff, the PKP uses the following layout:

```
<pkg-id>/
  pkg-manifest.json
  pkg-snapshot.jsonl
  provenance-ledger.jsonl
  validation-report.json
  governance-record.json
  deliverables.json
  views-index.json
  ontology-ref.json
  pkg-signature.json
```

10. Non-Goals

This specification does not define:

- The internal storage format of the live PKG.
- The Studio Engine's consumption logic.
- The cryptographic algorithm choices (those live in the governance constitution).
- The retention policy beyond the read-only guarantee.

11. Approval

This specification is binding for every PKP emitted by Genesis and every PKP consumed by the Studio Engine.