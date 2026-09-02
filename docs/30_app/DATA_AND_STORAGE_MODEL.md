# Data & Storage Model

**Version:** 1.0

## Principle

Separate authoritative source documents from runtime data.

## Suggested logical stores

### Governance store
- constitutions
- standards
- versions
- change requests

### Content-intelligence store
- ontology
- coverage
- content performance

### Canon store
- universes
- characters
- visual refs
- voice refs
- continuity

### Production store
- Episode Contracts
- Policy Snapshots
- GENESIS artifacts
- PKPs
- runs
- assets
- ORACLE reports

### Distribution store
- master releases
- derivatives
- metadata
- publish records

---

## Immutable IDs

Never rely only on filenames.

Suggested prefixes:

```text
NICHE-
DOMAIN-
PF-       problem family
SS-       sub-series
MV-       mechanism variant
UNIVERSE-
CHAR-
EP-
ARC-
POLICY-
PKP-
RUN-
ASSET-
ORACLE-
RELEASE-
```

## Asset provenance

Every generated media asset should include:

```yaml
asset:
  asset_id:
  type:
  production_id:
  pkp_version:
  run_id:
  source_asset_ids:
  model:
  model_version:
  workflow_version:
  seed:
  settings_hash:
  file_path:
  sha256:
  status:
```

## No shared mutable “latest” as truth

Convenience symlinks/folders may exist.

Release authority must reference immutable IDs/hashes.
