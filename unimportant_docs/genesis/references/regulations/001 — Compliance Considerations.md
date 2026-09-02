Genesis References (GREF)
GREF-005 — Compliance Considerations

Document ID: GREF-005
Title: Compliance Considerations
Version: 1.0.0
Status: Reference
Authority: Derived from GFS-000

1. Purpose

This document identifies compliance considerations that affect Genesis productions. It is not legal advice and does not constitute a compliance program. It enumerates the categories of obligation a production team must consider when using Genesis to produce and publish creative work, and it specifies where Genesis captures the data needed to demonstrate compliance.

2. Scope

These considerations apply to:
- The synopsis and brief submitted by the creator.
- Knowledge inferred, assumed, or confirmed by Genesis.
- Materialized documents including screenplay, scene plan, and prompts.
- The packaged PKP and its distribution to downstream engines.
- The final published production.

3. Data Privacy

3.1 Personal Data in Source Material
- If the synopsis contains real personal data, Genesis must classify those nodes as Explicit and flag them for review before inference.
- The PKG must record the provenance of any personal data so that right-to-erasure requests can be honored.

3.2 Creator and Collaborator Data
- Genesis sessions record contributor identifiers. These must be retained per the configured data retention policy and purged on schedule.
- Session logs containing personal data must be stored with access controls and audit trails.

3.3 Embeddings and Derived Data
- Embeddings of personal data are considered personal data under several regimes. Genesis must treat embeddings as in-scope for erasure and retention.
- The sqlite-vec index must be purgeable by session and by contributor.

4. AI Ethics

4.1 Disclosure of AI Involvement
- Genesis productions should disclose the extent of AI involvement in pre-production. The Documentation Publisher Agent includes an AI involvement statement in every published PKP.
- Disclosure records which agents contributed to which knowledge nodes, per the traceability principle.

4.2 Bias and Representation
- The Character Manager and Psychology Reviewer agents must flag stereotypes and biased characterizations before certification.
- Evaluation agents include representation checks as part of the readiness assessment.

4.3 Harm and Safety
- The Governance Agent must reject productions that promote unlawful harm, regardless of creator intent.
- Safety checks are validation gates and cannot be waived by the creator.

5. Content Licensing

5.1 Source Material Licensing
- The creator warrants that the synopsis and source materials are usable for the intended production. Genesis records this warranty in the session metadata.
- Inferred knowledge derived from copyrighted source material inherits the licensing constraints of that source. The PKG must propagate license tags along inference edges.

5.2 Reference and Inspiration Material
- When the Research Agent retrieves external material, it must record the source, license, and usage rights. Material with unclear licensing is treated as Unknown and not used for inference without creator confirmation.

5.3 Output Licensing
- The PKP must include a license declaration. Default is the creator's chosen license; absent a choice, the PKP is unpublished until a license is set.
- Downstream engines must honor the PKP license; Genesis includes the license in the manifest so downstream systems cannot accidentally strip it.

6. Intellectual Property

6.1 Character and World Originality
- The Character Manager and Environment Manager must flag character or world elements that closely resemble existing protected works.
- Resemblance flags do not block production but must be resolved (confirmed as original or licensed) before certification.

6.2 Trademark and Brand Use
- Any use of real trademarks, brands, or recognizable properties must be reviewed by the Governance Agent.
- The PKG records the justification for each use.

7. Regulatory Considerations by Region

7.1 European Union
- GDPR: Apply to any personal data in the synopsis, inferences, or session logs.
- AI Act: Classify Genesis use according to risk tier. Pre-production tooling is typically limited-risk, but downstream media generation may carry higher obligations.
- DSA: If the PKP is published on a platform, platform obligations apply downstream.

7.2 United States
- Copyright Office guidance on AI-generated content: Genesis pre-production material may be considered human-authored where the creator exercises sufficient creative control. The traceability record supports this position.
- FTC: Disclosure of AI involvement in advertising content.

7.3 Other Jurisdictions
- Genesis is jurisdiction-aware. The Production Brief includes a territory field. The Governance Agent applies territory-specific rules at certification.
- Where a jurisdiction is not modeled, the Governance Agent escalates for human review.

8. Accessibility

- Subtitle Agent outputs must meet the configured accessibility standard (e.g., WCAG captions).
- Visual descriptions for key shots should be generated to support audio description tracks downstream.
- Accessibility compliance is a validation gate, not an optional step.

9. Provenance and Audit

- Every decision in the PKG has a provenance record (per GFS-000 principle 8 and GREF-002 PROV mapping).
- The PKP includes a full audit trail that can be exported for third-party review without exposing personal data.
- Audit exports must be redactable: personal data fields can be replaced with pseudonymous identifiers on export.

10. Children and Vulnerable Audiences

- If the production targets children or vulnerable audiences, additional safety, privacy, and content checks apply.
- The territory and audience fields in the brief trigger these checks. They cannot be bypassed by the creator.
- COPPA, GDPR-K, and equivalent regional rules apply to the published production, and Genesis captures the data needed to demonstrate compliance.

11. Limitations of This Document

- This document does not replace legal review. Productions intended for commercial release should obtain legal review of the certified PKP.
- Regulations change. This document is versioned; updates follow the governance amendment workflow.
- Genesis captures data to support compliance but does not guarantee compliance. Compliance is the responsibility of the publisher.

12. Cross-References

- GFS-007 — Governance Constitution
- GREF-002 — Standards Mapping (ODRL for rights)
- GREF-003 — Bibliography
- GWS-NNN — Governance Workflow