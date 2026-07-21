Genesis Architecture Decision Record (ADR)

ADR-003 — Why Constitutional Hierarchy

Document ID: ADR-003
Title: Genesis is Governed by a Constitutional Hierarchy with the Charter as Supreme Authority
Version: 1.0.0
Status: Accepted
Authority: Derived from GFS-000 Constitutional Charter §17

Date: 2025-01-05
Decision Maker: Chief Architect
Reviewer: Governance Agent
Supersedes: none
Superseded By: none
Related Documents: GFS-000, GFS-001 through GFS-009, GO-001, GARCH-001, ADR-001, ADR-002

1. Context

Genesis is a system that produces knowledge intended to outlive any specific implementation, model, renderer, or team. The Constitutional Charter (GFS-000) opens by declaring that "knowledge must survive changes in AI models, rendering technologies, and production workflows" (§16). This requirement creates a design problem that ordinary engineering practices do not solve.

Most engineering systems govern themselves through conventions: code review, style guides, team agreements, and ad hoc documentation. These mechanisms work when the system and the team are the only constants. They fail when the system must outlive the team. Conventions drift. Style guides rot. Team agreements evaporate when the team changes. Within a few years, a convention-governed system becomes a system with no governance at all: every new contributor reinvents the rules, and the system's invariants erode.

Genesis faces this problem in an acute form because:

- It is the authoritative source of truth for productions. Errors in Genesis propagate downstream into every media artifact produced by the Studio Engine.
- It depends on AI models that change every few months. Without governance, each new model invites a rewrite of the system's reasoning behavior.
- It must remain stable across many productions, each with its own vocabulary, genre, and constraints. Without a governing layer, productions would each introduce incompatible extensions.
- It is intended to be implemented independently by different teams. Without a supreme authority, independent implementations would diverge into incompatible systems.
- Its invariants—knowledge precedes production, inference must be distinguished from fact, every decision must be traceable—are the kind of invariants that look obvious until they are violated, after which they look irreplaceable. Conventions do not defend them; constitutions do.

The question was therefore: what governance structure can hold Genesis's invariants stable across model changes, team changes, implementation changes, and decades of evolution?

Three candidate governance models were considered:

- Conventional governance (code review, team agreements, documentation)
- Architectural governance (a set of architecture documents with no constitutional authority)
- Constitutional governance (a supreme charter, domain constitutions, and an amendment process)

2. Decision

Genesis is governed by a constitutional hierarchy. The Constitutional Charter (GFS-000) is the supreme authority. Nine domain constitutions (GFS-001 through GFS-009) derive from the Charter and govern specific domains. Every other document—ontologies, architectures, agent specifications, workflows, schemas, decisions, and implementations—derives from the constitutional layer and must conform to it. If a lower-level document conflicts with the Charter, the Charter prevails.

The decision is elaborated by the following binding rules:

- The Constitutional Charter (GFS-000) holds supreme authority. No other document may override it.
- Nine domain constitutions (GFS-001 through GFS-009) derive from the Charter and govern specific domains: Knowledge, Discovery, Validation, Agents, Governance, Workflows, Ontology, Materialization, and Quality. Each domain constitution derives its authority from the Charter and may not contradict it.
- The Core Ontology (GO-001) and all derived ontologies derive from the Charter and the Ontology Constitution (GFS-006 or equivalent).
- Architecture documents (GARCH-001+) derive from the Charter and the relevant domain constitutions.
- Agent specifications (GAS-001+) derive from the Charter and the Agent Constitution.
- Workflow specifications (GWS-001+) derive from the Charter and the Workflow Constitution.
- ADRs derive from the Charter and the Governance Constitution. An ADR may not override a constitution; an ADR may only interpret, apply, or extend within the constitutional frame.
- Implementations derive from all of the above. An implementation that conflicts with any governing document is non-conforming and may not be certified.
- Conflicts are resolved upward: implementation yields to ADR; ADR yields to architecture; architecture yields to ontology; ontology yields to domain constitution; domain constitution yields to the Charter.
- Amendments to the Charter require the constitutional amendment process defined in the Governance Constitution. Amendments to domain constitutions require the process defined in each constitution, ratified by the Governance Agent.
- Lower-level documents may be revised by their owning roles without constitutional amendment, provided the revision does not conflict with any higher-level document.

3. Status

Accepted on 2025-01-05 by the Chief Architect, reviewed and approved by the Governance Agent.

No supersession is anticipated. Replacing the constitutional hierarchy would require dissolving the Charter itself, which the Charter's own amendment process is designed to make difficult.

4. Consequences

4.1 Positive Consequences

- Stability across change. The Charter's invariants—knowledge precedes production, inference must be distinguished from fact, every decision must be traceable—are now defended at the highest layer. They survive team changes, model changes, and implementation rewrites.
- Traceability of authority. Every document carries an `Authority` field naming the document it derives from. A reader can trace any rule from an implementation up through architecture, ontology, domain constitution, and Charter to the supreme authority.
- Explicit amendment process. Changes to invariants require the constitutional amendment process. This forces deliberation where convention would allow drift.
- Independent implementation. Different teams can implement Genesis independently and remain conforming, because conformance is measured against the constitutional layer, not against any specific implementation.
- Conflict resolution. When two documents disagree, the hierarchy determines which prevails. There is no need for ad hoc negotiation; the rule is fixed.
- Auditability. Auditors can verify conformance by walking the hierarchy. A non-conforming implementation is detectable by inspection.
- Domain separation. The nine domain constitutions partition governance into coherent areas, each with its own amendments, owners, and review process. The Charter does not need to address every detail; it delegates.
- Longevity. Constitutions are designed to last. A constitutional system is the only governance model that explicitly anticipates decades of evolution.

4.2 Negative Consequences

- Change is slower. Constitutional amendments are deliberately harder than ordinary revisions. This is a feature for invariants and a friction for everything else. The mitigation is precise scope: only true invariants live in the Charter; everything else lives in lower documents with lighter amendment processes.
- The learning curve is steeper. New contributors must understand the hierarchy before they can contribute safely. The mitigation is the AGENTS.md guide and the document header convention that names each document's authority explicitly.
- Over-governance risk. A system with a constitution, nine domain constitutions, ontologies, architectures, ADRs, and specifications can become a bureaucracy. The mitigation is the amendment process itself: constitutions that become obstacles can be amended; documents that prove unnecessary can be retired.
- Rigidity in unexpected places. Sometimes a rule that seemed invariant turns out to be an implementation choice that should be flexible. If it is encoded in a constitution, unwinding it requires amendment. The mitigation is the discipline of placing only true invariants in constitutions and leaving implementation choices to lower documents.

4.3 Neutral Consequences

- The vocabulary of "charter," "constitution," "amendment," and "ratification" enters the engineering vocabulary of the project. Future ADRs must use these terms consistently.
- The document hierarchy becomes a navigable structure. Tools that index the hierarchy (e.g., a conformance checker) become valuable.
- Governance becomes an engineering discipline within the project, not a separate organizational function.

5. Alternatives

5.1 Alternative 1: Conventional Governance

Description: Genesis would be governed by code review, style guides, team agreements, and documentation. No supreme authority would exist. Decisions would be made by the current team.

Advantages:
- Lowest overhead. No formal governance machinery.
- Fast change. Anything can be changed at any time by the current team.
- Familiar to most engineering teams.

Disadvantages:
- Drift is inevitable. Conventions rot when the team changes.
- Invariants are undefended. "Knowledge precedes production" becomes a guideline that the next contributor can ignore.
- Independent implementations diverge. With no supreme authority, two implementations of Genesis become two different systems.
- Auditability is lost. There is no fixed standard to audit against.
- Longevity is not designed for. The system survives only as long as the team that understands its conventions.

Rejection Rationale: Conventional governance is incompatible with the Charter's own mandate that knowledge survive changes in models, technologies, and workflows. A convention-governed system cannot make that guarantee.

5.2 Alternative 2: Architectural Governance Without a Constitution

Description: Genesis would be governed by a set of architecture documents (GARCH-001+) that define invariants, but no document would hold supreme authority. Conflicts would be resolved by reference to the most relevant architecture document.

Advantages:
- More structured than conventional governance.
- Easier to amend than a constitution.
- Familiar to engineering organizations.

Disadvantages:
- No supreme authority. When two architecture documents conflict, there is no rule for which prevails.
- Invariants are not distinguished from implementation choices. Everything lives at the same level, so everything is equally easy to change, including the things that should not change.
- No explicit amendment process. Architecture documents are revised like any other documentation, which means invariants drift as easily as conventions.
- The hierarchy is flat. There is no way to say "this rule is more fundamental than that rule." Everything is equal, which means nothing is supreme.

Rejection Rationale: A flat architecture document set cannot defend invariants. Without a supreme authority, every architecture decision is one revision away from being overturned. This is incompatible with the Charter's longevity requirement.

5.3 Alternative 3: Single Supreme Document, No Domain Constitutions

Description: The Charter would be the only governing document. All other documents would derive directly from it. There would be no domain constitutions.

Advantages:
- Simplest hierarchy. One supreme document, everything else beneath.
- No delegation ambiguity. Everything traces to one source.
- Easier to learn.

Disadvantages:
- The Charter becomes enormous. To govern nine domains in detail, it must contain all domain-specific rules, which makes it unreadable.
- Amendment becomes all-or-nothing. Any change to any domain requires amending the Charter, which is the heaviest process.
- Domain expertise is not localized. Domain experts must understand the entire Charter to participate in governance of their domain.

Rejection Rationale: A single-document constitution cannot scale to nine domains without becoming unreadable and unamendable. The domain constitution layer exists to partition governance so that each domain can be amended independently within its scope, while the Charter remains short, stable, and supreme.

6. Compliance

6.1 Validation Rules

The Validation Engine (S3 per GARCH-002) enforces the following invariants:

- Every document in the Genesis repository must declare a Document ID, Version, Status, and Authority in its header.
- Every document's Authority field must reference an existing higher-level document ID, terminating at GFS-000.
- No document may declare an Authority higher than GFS-000. GFS-000's Authority is "Supreme."
- No document may contradict any document in its authority chain. Contradictions are flagged as validation findings.
- ADRs must reference the constitution or charter from which they derive.
- Implementations must declare conformance to the constitutional hierarchy in their build manifest.

6.2 Governance Gates

- The Constitution Amendment gate must approve any change to GFS-000 or any domain constitution (GFS-001..009). The gate requires ratification by the Governance Agent and a recorded amendment record in the Provenance Ledger.
- The Document Authority gate must approve any new top-level document, verifying that its declared Authority is valid and that it does not conflict with any higher-level document.
- The Conformance gate must approve any implementation before it may be certified as a Genesis-conforming system.

6.3 Audit Checks

- Query for any document missing a valid Authority field. Such documents are ungoverned and must be retired or assigned an authority.
- Query for any document whose Authority chain does not terminate at GFS-000. Such documents indicate a parallel governance structure, which is forbidden.
- Query for any contradiction between a document and its authority chain. Such contradictions indicate constitutional drift.
- Query for any implementation that declares conformance but fails the conformance checklist. Such implementations are non-conforming.

6.4 Amendment Process

This ADR may be amended by supersession. A superseding ADR that proposes to dissolve the constitutional hierarchy must demonstrate how the Charter's longevity, traceability, and stability requirements would be met without a supreme authority. The bar for such a supersession is intentionally high.

7. References

- GFS-000 Constitutional Charter, §§15, 16, 17
- GFS-001 through GFS-009 Domain Constitutions (referenced)
- GO-001 Genesis Core Ontology, §24 (Constitutional Invariants)
- GARCH-001 Enterprise Architecture, §2 (Architectural Principles)
- ADR-001 Why Genesis is Pre-Production Only
- ADR-002 Why Knowledge Graph Not Relational

8. Notes

The constitutional hierarchy is the governance counterpart to the architectural decisions in ADR-001 and ADR-002. ADR-001 fixes the boundary; ADR-002 fixes the data structure; ADR-003 fixes the rules under which the boundary and the data structure can be changed. Together, the three ADRs form the founding architecture of Genesis.

9. Sign-off

| Role | Name | Date | Signature |
|------|------|------|----------|
| Decision Maker | Chief Architect | 2025-01-05 | (signed) |
| Reviewer | Governance Agent | 2025-01-06 | (signed) |
| Governance Agent | Governance Agent | 2025-01-06 | (signed) |