# Domain Model

**Version:** 1.0

## Aggregate overview

```text
Niche
 └─ Domain
    └─ OntologyNode
       └─ EpisodeContract
          ├─ StoryUniverse
          │  ├─ Characters
          │  └─ ContinuityState
          ├─ EffectivePolicySnapshot
          ├─ GenesisArtifacts
          └─ PKP
             └─ ProductionRun
                ├─ Assets
                ├─ RunManifest
                └─ OracleReport
                   └─ MasterRelease
                      └─ DistributionPackage
```

## Entity definitions

### Niche
Example: `psychology`

Fields:
- id
- name
- constitution_version
- status

### Domain
Example: `relationship_emotional_psychology`

### OntologyNode
Represents:
- problem family;
- sub-series;
- mechanism family/variant.

### StoryUniverse
Example: `UNIVERSE-MARK-SARAH`

Owns recurring canon.

### Character
Owns stable identity references, not episode emotional states.

### ContinuityState
Mutable record of persistent story history.

### EpisodeContract
Approved unit of creative intent.

### EffectivePolicySnapshot
Immutable resolved rules for that episode/version.

### GenesisArtifacts
Draft/final creative artifacts:
- thesis;
- synopsis;
- beat graph;
- screenplay;
- dialogue;
- scene states;
- shot intent;
- production design.

### PKP
Frozen executable production knowledge.

### ProductionRun
One attempted execution of one PKP version.

### Asset
Generated or approved:
- image;
- video;
- voice;
- audio;
- subtitle;
- master;
- thumbnail.

### OracleReport
Independent validation evidence.

### MasterRelease
Approved master media version.

### DistributionPackage
Platform-specific derivatives and metadata.

### CoverageEntry
Tracks what content territory has been used.

---

## Stable vs mutable

### Stable/slow-changing
- constitutions;
- series canon;
- ontology structure.

### Mutable/versioned
- continuity;
- coverage;
- Episode Contracts;
- PKPs;
- runs;
- validations;
- performance.

Do not store mutable episode emotion inside the Character entity.
