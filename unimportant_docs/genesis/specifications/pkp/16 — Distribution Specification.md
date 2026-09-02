Genesis Foundational Standards (GFS)
PKP-16 — Distribution Specification

Document ID: PKP-16
Title: Distribution Specification
Version: 1.0.0
Status: Pre-Production Specification
Authority: Derived from GFS-000 Constitutional Charter

1. Purpose

The Distribution Specification defines the publishing strategy of the
production. It captures platforms, aspect ratios, localization, accessibility,
metadata strategy, release strategy, and packaging requirements.

This specification translates the Project (PKP-02) into a coherent
distribution program. It does not specify marketing, audience acquisition, or
commercial terms — those are out of scope for Genesis. It specifies the
*technical and editorial requirements* that the Studio Engine and downstream
publishing systems must honor.

2. Scope

This specification defines:
- Platforms (the distribution channels the production targets)
- Aspect ratios (the presentation ratios the production must deliver)
- Localization (the language and cultural adaptation the production commits to)
- Accessibility (the accessibility features the production commits to)
- Metadata strategy (the metadata the production will publish with)
- Release strategy (the release sequence and windowing)
- Packaging requirements (the deliverable formats the production must produce)

Out of scope: marketing strategy, audience acquisition, commercial terms,
promotional materials. Those belong to downstream publishing systems.

3. Contents

3.1 Platforms
The distribution channels the production targets. Each platform is declared
with its type (theatrical, streaming, broadcast, physical media, other), its
delivery format, and its constraints.

3.2 Aspect Ratios
The presentation ratios the production must deliver. Declared as a primary
ratio and any secondary ratios, with the cropping or reframe policy for each
secondary ratio.

3.3 Localization
The language and cultural adaptation the production commits to. Declared as a
list of localization targets, each with its type (subtitled, dubbed, both), its
fidelity posture, and its cultural adaptation policy.

3.4 Accessibility
The accessibility features the production commits to. Declared as a list of
features (captions, audio description, sign language interpretation, color-contrast
adaptation, sensory-reduced cut), each with its target audience and its
implementation posture.

3.5 Metadata Strategy
The metadata the production will publish with. Declared as a set of fields
(title, synopsis, content advisories, age rating, runtime, language, credits,
keywords), each with its source specification and its update policy.

3.6 Release Strategy
The release sequence and windowing. Declared as a list of release windows,
each with its platform, its opening date envelope, its exclusivity posture,
and its dependencies.

3.7 Packaging Requirements
The deliverable formats the production must produce. Declared as a list of
packages, each with its target platform, its container format, its codec
requirements (expressed as performance envelopes, not specific codecs), its
audio configuration, and its subtitle/caption configuration.

4. Inputs

- Project Specification (PKP-02)
- Vision Specification (PKP-00)
- Creative Strategy Specification (PKP-01)
- Constitutional Charter (GFS-000)

5. Outputs

- A validated Distribution record in the Production Knowledge Graph
- A materialized Distribution Specification document
- Distribution requirements propagated to PKP-17 (Quality) and to the Studio
  Engine handoff package

6. Schema

```yaml
distribution:
  document_id: PKP-16
  version: 1.0.0
  platforms:
    - id: <string>
      type: <theatrical|streaming|broadcast|physical_media|other>
      delivery_format: <string>
      constraints: [<string>]
  aspect_ratios:
    primary: <string>
    secondary:
      - ratio: <string>
        reframe_policy: <string>
  localization:
    - language: <ISO 639-1 code>
      type: <subtitled|dubbed|both>
      fidelity_posture: <string>
      cultural_adaptation_policy: <string>
  accessibility:
    - feature: <captions|audio_description|sign_language|color_contrast|sensory_reduced|other>
      target_audience: <string>
      implementation_posture: <string>
  metadata_strategy:
    - field: <string>
      source_specification: <reference>
      update_policy: <string>
  release_strategy:
    - window: <string>
      platform: <reference>
      opening_date_envelope: <string>
      exclusivity_posture: <string>
      dependencies: [<string>]
  packaging_requirements:
    - id: <string>
      target_platform: <reference>
      container_format: <string>
      codec_envelope: <string>
      audio_configuration: <string>
      subtitle_caption_configuration: <string>
  provenance:
    source_project: <reference>
    agent: <string>
    session: <string>
    confidence: <EXPLICIT|INFERRED|CONFIRMED|ASSUMED|UNKNOWN>
```

7. Required Fields

- platforms (at least one)
- aspect_ratios.primary
- localization (at least one entry matching the primary language of PKP-02)
- accessibility (at least one entry)
- metadata_strategy (at least the fields: title, synopsis, age_rating,
  runtime, language)
- release_strategy (at least one window)
- packaging_requirements (at least one per platform)
- provenance.confidence

8. Optional Fields

- aspect_ratios.secondary (required if the production targets multiple ratios)
- accessibility features beyond the minimum (recommended)
- metadata_strategy fields beyond the minimum (recommended)

9. Validation Rules

- D-001: platforms must be consistent with the platform.primary declared in
  PKP-02.
- D-002: aspect_ratios.primary must be consistent with the format in PKP-02.
  A theatrical feature requires a theatrical ratio; a streaming short may
  declare a streaming-native ratio.
- D-003: localization must include the primary language of PKP-02 as a
  minimum.
- D-004: accessibility must include at minimum captions for the primary
  language.
- D-005: metadata_strategy fields must reference source specifications that
  exist in the PKP.
- D-006: release_strategy dependencies must form a directed acyclic graph.
- D-007: packaging_requirements.codec_envelope must be expressed as a
  performance envelope (resolution, bitrate band, frame rate), not as a
  specific codec. Codec selection belongs to the Studio Engine.
- D-008: No distribution requirement may violate a non-negotiable principle
  from PKP-00.
- D-009: For each packaging requirement, the audio_configuration must be
  consistent with the audio_intent in PKP-12.

10. Dependencies

- PKP-02 — Project Specification (hard)
- PKP-00 — Vision Specification (soft)
- PKP-01 — Creative Strategy Specification (soft)

11. Versioning

- MAJOR: Removal of a platform, change to aspect_ratios.primary, or change to
  release_strategy windowing.
- MINOR: Addition of localization targets, accessibility features, or
  packaging requirements.
- PATCH: Wording refinements that do not alter distribution strategy.

A MAJOR change to Distribution triggers revalidation of PKP-17.

12. Examples

```yaml
distribution:
  document_id: PKP-16
  version: 1.0.0
  platforms:
    - id: "PLAT-001"
      type: "theatrical"
      delivery_format: "DCP"
      constraints: ["24fps", "5.1 audio minimum"]
    - id: "PLAT-002"
      type: "streaming"
      delivery_format: "ProRes master, streaming encode derived."
      constraints: ["HDR10 optional", "2.0 and 5.1 audio"]
  aspect_ratios:
    primary: "1.85:1"
    secondary:
      - ratio: "16:9"
        reframe_policy: "Protect for 16:9 from the start; no hard matte."
  localization:
    - language: "en"
      type: "subtitled"
      fidelity_posture: "Original dialogue preserved; captions verbatim."
      cultural_adaptation_policy: "No cultural adaptation for primary language."
    - language: "fr"
      type: "both"
      fidelity_posture: "Dubbed with original ambience preserved."
      cultural_adaptation_policy: "Clinical terminology localized; no plot changes."
  accessibility:
    - feature: "captions"
      target_audience: "Deaf and hard-of-hearing viewers."
      implementation_posture: "Verbatim captions for all dialogue; ambient sound described."
    - feature: "audio_description"
      target_audience: "Blind and low-vision viewers."
      implementation_posture: "Described track for all scenes; description written during pre-production."
  metadata_strategy:
    - field: "title"
      source_specification: "PKP-02"
      update_policy: "Immutable post-release."
    - field: "synopsis"
      source_specification: "PKP-04"
      update_policy: "Immutable post-release."
    - field: "age_rating"
      source_specification: "PKP-02"
      update_policy: "Immutable post-release."
    - field: "runtime"
      source_specification: "PKP-02"
      update_policy: "Updated on final cut certification."
  release_strategy:
    - window: "Festival window"
      platform: "PLAT-001"
      opening_date_envelope: "Week 1-2 of release year."
      exclusivity_posture: "Non-exclusive; festival circuit only."
      dependencies: []
    - window: "Theatrical window"
      platform: "PLAT-001"
      opening_date_envelope: "Week 3-8."
      exclusivity_posture: "Exclusive theatrical for 8 weeks."
      dependencies: ["Festival window"]
    - window: "Streaming window"
      platform: "PLAT-002"
      opening_date_envelope: "Week 9 onward."
      exclusivity_posture: "Non-exclusive streaming."
      dependencies: ["Theatrical window"]
  packaging_requirements:
    - id: "PKG-001"
      target_platform: "PLAT-001"
      container_format: "DCP"
      codec_envelope: "2K, 24fps, 150-200 Mbps video band."
      audio_configuration: "5.1 surround, dialogue-centric mix per PKP-12."
      subtitle_caption_configuration: "Open captions on screen; no separate track."
    - id: "PKG-002"
      target_platform: "PLAT-002"
      container_format: "ProRes 4444 master"
      codec_envelope: "1080p and 4K, 24fps, 80-120 Mbps streaming band."
      audio_configuration: "2.0 and 5.1, dialogue-centric mix per PKP-12."
      subtitle_caption_configuration: "Closed captions; separate described-video track."
  provenance:
    source_project: "PKP-02 v1.0.0"
    agent: "DistributionArchitectAgent"
    session: "sess-015"
    confidence: "CONFIRMED"
```

13. Future Extensibility

- A field for interactive distribution (branching narratives, viewer choice)
  may be added in a MINOR version when interactive productions are supported.
- A field for spatial audio distribution (Dolby Atmos, Ambisonics) may be added
  when the Studio Engine introduces a spatial audio layer.
- A field for cross-platform release coordination (shared metadata, synchronized
  release) may be added when multi-platform releases become a first-class
  workflow.