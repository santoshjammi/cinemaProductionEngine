# Workflow State Machine

**Version:** 1.0

## Primary states

```text
IDEA
  ↓
EPISODE_CONTRACT_DRAFT
  ↓
EPISODE_CONTRACT_APPROVED
  ↓
POLICY_RESOLVED
  ↓
GENESIS_IN_PROGRESS
  ↓
GENESIS_REVIEW
  ↓
GENESIS_APPROVED
  ↓
PKP_FROZEN
  ↓
PROMETHEUS_IN_PROGRESS
  ↓
MEDIA_READY_FOR_ORACLE
  ↓
ORACLE_REVIEW
  ├─→ REWORK_REQUIRED ─→ appropriate upstream state
  └─→ MASTER_APPROVED
        ↓
DISTRIBUTION_READY
        ↓
PUBLISHED
        ↓
LEARNING_RECORDED
```

## Blocking states

- POLICY_CONFLICT
- CANON_MISSING
- VOICE_REFERENCE_MISSING
- VISUAL_REFERENCE_MISSING
- GENESIS_REJECTED
- PRODUCTION_FAILED
- ORACLE_REJECTED

## Important transition rules

### Cannot enter GENESIS
unless:
- Episode Contract approved;
- ontology classification valid;
- universe selected;
- applicable policy resolved.

### Cannot freeze PKP
unless:
- screenplay/dialogue approved;
- continuity passes;
- production plan is feasible;
- required identities are bound.

### Cannot approve master
unless:
- ORACLE blocking gates pass;
- no placeholder assets;
- run manifest complete.

## Rework routing

A defect must route to its owner.

Examples:

- bad dialogue → GENESIS;
- wrong face → PROMETHEUS or reference-binding workflow;
- unconstitutional premise → Episode Contract;
- lip-sync failure → PROMETHEUS;
- missing canon → Series Canon;
- misleading title → Distribution Package.
