Genesis Policies
GPOL-001 — Security Policy

Document ID: GPOL-001
Title: Genesis Security Policy
Version: 1.0.0
Status: Binding Policy
Authority: Derived from GFS-000, GFS-005, GFS-011

1. Purpose

This policy defines the security controls that govern every Genesis
deployment: encryption at rest, access control, audit logging, and key
management. It applies to the Production Knowledge Graph, the provenance
log, the message bus, the API surface, and every persistent store that
holds production knowledge.

2. Foundational Principle

Knowledge is the most valuable asset Genesis holds.

Every other component is replaceable. The PKG, the provenance log, and the
governance records are not. Security protects the irreplaceable. A breach
of confidentiality, integrity, or availability is a constitutional breach.

3. Threat Model

Genesis assumes:

- A semi-trusted internal network with untrusted external consumers
- Authenticated but not universally trusted internal agents (an agent may
  be compromised or buggy)
- Long-lived production data that may outlive any single deployment
- Human reviewers who may act in good faith but make errors

Controls are designed against: unauthorized reads, unauthorized writes,
provenance tampering, key disclosure, audit-log deletion, and replay of
stale credentials.

4. Encryption at Rest

4.1 Scope

Encryption at rest is mandatory for:

- The PKG graph database
- The PKG JSON-LD files in object storage
- The provenance log
- The governance log
- The review log
- The audit log
- Backups and snapshots
- Session state files

4.2 Algorithm

- AES-256-GCM for block storage
- ChaCha20-Poly1305 for object storage where AES acceleration is unavailable
- Envelope encryption: data keys are AES-256, wrapped by a master key
  held in a KMS

4.3 Key Hierarchy

- Master key: held in a hardware KMS or HSM; never leaves the KMS unencrypted
- Data Encryption Keys (DEKs): generated per object or per file, wrapped by
  the master key, stored alongside the ciphertext
- Rotation: master key rotated every 90 days; DEKs are unique per write
- Revocation: a compromised DEK is disabled by re-wrapping with a new
  master key version

4.4 Backups

Backups inherit the encryption of their source. Backups shall be
encrypted with a separate DEK and shall be tested for restore at least
quarterly. A backup that cannot be restored is not a backup.

5. Encryption in Transit

- All inter-agent messages on the bus shall use TLS 1.3
- All API traffic shall use TLS 1.3; HTTP is rejected at the edge
- Internal service-to-service traffic shall use mTLS with short-lived
  certificates issued by an internal CA
- Certificate lifetime: 24 hours; rotation automated

6. Access Control

6.1 Model

Access is role-based with attribute overlays (RBAC + ABAC):

- Roles: drawn from the Constitutional Role Registry
- Attributes: production ID, ontology namespace, confidence floor, session
- Permissions: scoped per GFS-011 section 7 and GC-004 section 5

6.2 Principles

- Least privilege: every role receives the minimum permissions required
- Separation of duties: no single role may both produce and approve the
  same artifact
- Default deny: any unlisted permission is denied
- Time-bounded: production-scoped grants expire at session end or
  production close, whichever is sooner

6.3 Authentication

- Agents authenticate with mTLS plus a signed identity certificate
- Humans authenticate with OAuth 2.0 plus a second factor
- External systems authenticate with OAuth 2.0 bearer tokens, scoped per
  GC-004 section 5
- Anonymous access is permitted only on `/v1/health` and `/v1/version`

7. Audit Logging

7.1 Scope

The audit log shall record, at minimum:

- Every authentication event (success and failure)
- Every authorization decision (allow and deny)
- Every write to the PKG (with node and edge UUIDs)
- Every governance decision (approval, veto, escalation)
- Every validation outcome (PASS, FAIL, exception)
- Every key operation (creation, rotation, revocation)
- Every configuration change
- Every API request with correlation ID, scope, and response code

7.2 Properties

- Append-only: records may not be edited or deleted
- Tamper-evident: each record is chained to the previous by a hash
- Replicated: the audit log is streamed to a separate, hardened store
- Retained: per GPOL-004

7.3 Integrity

- Records are signed by the producing service
- The chain hash is verified on every read
- A gap in the chain is a CRITICAL security event and triggers immediate
  Governance notification

8. Key Management

8.1 KMS

- Master keys live in a dedicated KMS (cloud KMS or on-prem HSM)
- The KMS enforces per-key access policies
- Key access is audited independently of the application audit log
- The KMS is the only system permitted to unwrap a master key

8.2 Lifecycle

- Generation: in-KMS, never exported
- Activation: recorded in the key registry with owner and purpose
- Rotation: master every 90 days; service certificates every 24 hours
- Revocation: immediate on compromise; all wrapped DEKs re-encrypted
- Destruction: only after retention expiry per GPOL-004; destruction is
  logged and witnessed

8.3 Secrets

- API tokens, database credentials, and signing keys are secrets
- Secrets never appear in source code, logs, or error messages
- Secrets are distributed via a secrets manager with audit logging
- A secret found in logs is rotated immediately and the leak is logged as
  a CRITICAL event

9. Session Security

- Sessions are scoped to a production and a session_id
- Session tokens carry the producing agent's identity and the session
  scope
- Sessions expire on TTL (per GFS-011) or on explicit termination
- A session may not be reused after termination; replay is rejected

10. Incident Response

- Detection: automated alerts on audit-chain gaps, key-access anomalies,
  rate-limit violations, and unauthorized write attempts
- Containment: the affected credential or agent is suspended; the affected
  PKG version is quarantined
- Eradication: compromised keys are revoked; affected data is re-encrypted
- Recovery: a clean PKG version is promoted; the audit gap is reconciled
- Postmortem: a written incident report is filed within 5 business days
  and reviewed by the Governance Authority

11. Compliance

This policy is enforced by the API Provider, the Governance Agent, and the
Validation Authority. Periodic audits shall verify:

- Encryption is enabled and key rotation is current
- Access grants match the role registry
- The audit log is continuous and unbroken
- The KMS access log matches the application audit log
- No secret is present in source control or logs

Failures are escalated per GGV-001.

12. Invariants

- Knowledge is encrypted at rest and in transit.
- Access is least-privilege and time-bounded.
- Every action is audited and tamper-evident.
- Keys are rotated, never shared, and revocable.
- Incidents are detected, contained, and reported.
- No secret is ever committed to source control.