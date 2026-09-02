# Policy Resolution & Versioning

**Version:** 1.0

## Problem

Different AIs become inconsistent when each independently reads hundreds of documents and decides which rules matter.

The application must compile policy before creative execution.

## Resolution inputs

For a Mark & Sarah Psychology episode:

```text
Cinema Master Constitution
+
Psychology Sub-Constitution
+
Mark & Sarah Series Constitution
+
Commercial & Distribution Constitution (applicable rules)
+
Applicable Production Standards
+
Format Profile
+
Episode Contract
+
Explicit approved exceptions
```

Output:

`Effective Policy Snapshot`

## Snapshot properties

It must be:

- immutable;
- versioned;
- hashable;
- traceable to source versions;
- attached to the Episode Contract and PKP.

## Conflict detection

The resolver should classify:

- no conflict;
- lower-level specialization;
- blocking contradiction;
- missing required decision.

Example:

```yaml
conflict:
  code: SERIES_CANON_CONFLICT
  source_a: MSSC-001@1.0
  source_b: EP-004@2
  rule_a: permanent_separation_prohibited
  value_b: permanent_separation
  status: BLOCK
```

## Version behavior

Changing any of these should invalidate the snapshot:

- constitution version;
- series canon version;
- relevant standard version;
- Episode Contract version;
- Format Profile version.

Changing only a renderer patch version does not alter policy, but does alter the run manifest.

## Staleness

When an upstream artifact changes:

1. mark dependent policy snapshots stale;
2. mark unfrozen downstream artifacts stale;
3. if PKP already frozen, require a new PKP version;
4. never silently mutate history.
