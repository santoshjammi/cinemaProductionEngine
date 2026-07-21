Genesis Policies
GPOL-004 — Data Retention Policy

Document ID: GPOL-004
Title: Genesis Data Retention Policy
Version: 1.0.0
Status: Binding Policy
Authority: Derived from GFS-000, GFS-006, GFS-007, GPOL-001

1. Purpose

This policy defines how long each class of data is retained within Genesis,
when it may be archived, when it must be deleted, and which artifacts are
exempt from deletion. It applies to the Production Knowledge Graph, the
provenance log, the governance and review logs, the audit trail, evaluation
reports, and every persistent store named in the Security Policy
(GPOL-001).

2. Foundational Principle

Some knowledge must outlive the system that produced it.

Provenance, governance decisions, and certification records are the
institutional memory of Genesis. They shall survive model changes, software
rewrites, and deployment migrations. Operational data—sessions, caches,
intermediate reasoning artifacts—may be shorter-lived. This policy
distinguishes the two.

3. Data Classes

Genesis recognizes six classes of data, each with its own retention
schedule.

3.1 Production Knowledge Graph Versions

- Every CERTIFIED PKG version is retained indefinitely in the archive
- Every SUPERSEDED PKG version is retained for at least 10 years after
  supersession, then may be archived to cold storage
- Every DRAFT or VALIDATED PKG version that never reached CERTIFIED is
  retained for 1 year after the session ended, then deleted
- Withdrawn PKP versions are retained indefinitely for provenance

3.2 Provenance Logs

- Every provenance entry for a CERTIFIED PKG is retained indefinitely
- Provenance entries for non-certified sessions are retained for 1 year
- Provenance entries are append-only and never edited
- Deletion of provenance is permitted only after the 1-year threshold for
  non-certified work, and only by a Governance-approved job

3.3 Governance and Review Logs

- Governance approvals, vetoes, escalations, and appeals are retained
  indefinitely
- Review records are retained indefinitely
- Exception waivers are retained until their review date plus 5 years,
  then archived
- These logs are the institutional memory of Genesis; deletion is
  prohibited

3.4 Audit Trail

- The security audit log (per GPOL-001 section 7) is retained for at least
  7 years
- Audit records are append-only and tamper-evident
- After 7 years, records may be moved to cold storage but shall remain
  verifiable
- Audit records are never deleted while any production they reference
  remains in the archive

3.5 Evaluation Reports

- Evaluation reports for CERTIFIED productions are retained for 10 years
- Evaluation reports for non-certified productions are retained for 1 year
- Trend data aggregated from evaluation reports is retained indefinitely
- Raw evaluation inputs (model outputs, prompts) are retained for 90 days
  unless referenced by an appeal or incident

3.6 Session and Operational Data

- Session state files are retained for 30 days after session end, then
  deleted
- Intermediate reasoning artifacts (working memory, draft subgraphs not
  committed to the PKG) are deleted at session end
- Caches are ephemeral and may be cleared at any time
- Backups of operational data follow the backup retention schedule in
  section 5

4. Retention Schedule Summary

| Data class                     | Minimum retention      | Maximum before archive |
|--------------------------------|------------------------|------------------------|
| CERTIFIED PKG versions          | indefinite             | indefinite             |
| SUPERSEDED PKG versions         | 10 years               | 10 years to cold       |
| Non-certified PKG versions      | 1 year                 | deleted at 1 year      |
| Provenance (certified)          | indefinite             | indefinite             |
| Provenance (non-certified)      | 1 year                 | deleted at 1 year      |
| Governance and review logs     | indefinite             | indefinite             |
| Audit trail                    | 7 years                | 7 years to cold        |
| Evaluation reports (certified) | 10 years               | 10 years to cold       |
| Evaluation reports (other)      | 1 year                 | deleted at 1 year      |
| Session state                  | 30 days                | deleted at 30 days     |
| Intermediate reasoning          | session end            | deleted at session end |
| Backups                         | 90 days                | 90 days, then delete   |

5. Backup Retention

- Daily backups retained for 30 days
- Weekly backups retained for 90 days
- Monthly backups retained for 1 year
- Yearly snapshots retained for as long as any production they reference
- Backups are encrypted per GPOL-001 section 4.4
- A backup older than its retention window is deleted by an automated job
  that logs the deletion to the audit trail

6. Archival

- Archival moves data to cold storage; it does not delete data
- Archived data shall remain queryable within 24 hours of a restore request
- Archived data retains its encryption, integrity hashes, and provenance
- A restore test is run quarterly; failure is a MAJOR incident

7. Deletion

- Deletion is irreversible and is permitted only for data past its
  retention window
- Deletion is performed by a Governance-approved job that records:
  - Data class
  - Date range deleted
  - Count of records
  - Approving authority
  - Audit log reference
- Deletion of data still within its retention window is a CRITICAL breach

8. Legal Hold

- A legal hold issued by the Governance Authority suspends deletion for
  the named data class until the hold is lifted
- A legal hold shall record its reason, issuer, scope, and expected
  duration
- While a hold is active, retention windows continue to accrue but no
  deletion job runs against the held data

9. Exemptions from Deletion

The following are never deleted, regardless of age:

- The Charter and its derived constitutions
- Every ADR
- Every ontology version that was ever ACTIVE
- Every agent specification that was ever registered
- Every governance approval, veto, and appeal record
- Every Production Readiness Certificate ever issued

These are institutional memory. They survive the system.

10. Compliance

This policy is enforced by the Governance Agent and audited quarterly.
The audit verifies:

- No data was deleted before its retention window
- No data class exceeded its archive threshold without action
- Every deletion job produced an audit record
- Every legal hold is honored
- Backups were tested for restore in the last quarter

11. Invariants

- Institutional memory is never deleted.
- Operational data is bounded and purged.
- Archival preserves integrity and provenance.
- Deletion is Governance-approved and logged.
- Legal holds override retention windows.
- Backups are tested, not assumed.
- Restore is verified, not promised.