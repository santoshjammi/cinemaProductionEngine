Genesis Template (GTMP)
GTMP-012 — ADR Template

Document ID: GTMP-012
Title: ADR Template
Version: 1.0.0
Status: Template
Authority: Derived from GFS-000

1. Purpose

Blank template for Genesis Architecture Decision Records. Use this for any
non-obvious decision that future maintainers need to understand. Place finished
ADRs in `decisions/` with the ADR-NNN scheme. ADRs are immutable once Accepted;
supersession happens via a new ADR.

2. Template

```
Genesis Decision Record (ADR)
ADR-NNN — <Title>

Document ID: ADR-NNN
Title: <Title>
Version: 1.0.0
Status: Proposed | Accepted | Rejected | Deprecated | Superseded by ADR-NNN
Authority: Derived from GFS-000

1. Date
<YYYY-MM-DD>

2. Deciders
- <role / person>
- <role / person>

3. Context
<2-4 paragraphs describing the problem, constraints, and forces at play.
Include any relevant constitutional references (GFS-NNN).>

4. Decision
<One paragraph stating the decision clearly and unambiguously.>

5. Alternatives Considered
For each alternative:
- Alternative A: <description>
  - Pros: <list>
  - Cons: <list>
  - Rejected because: <reason>
- Alternative B: <description>
  - Pros: <list>
  - Cons: <list>
  - Rejected because: <reason>

6. Consequences
- Positive: <list>
- Negative: <list>
- Neutral: <list>

7. Compliance
- This decision conforms to: <GFS-NNN, GARCH-NNN>
- This decision affects: <GAS-NNN, GO-NNN, GWS-NNN>

8. Traceability
- Origin: <trigger for this decision>
- Evidence: <links to specs, metrics, research>
- Confidence: <High | Medium | Low>
- Revision history:
  - v1.0.0 — <date> — initial

9. Supersession
<Leave empty. If superseded, fill with "Superseded by ADR-NNN on YYYY-MM-DD.">
```

3. Usage Notes

- ADRs record *why*, not *what*. The *what* lives in specifications.
- Once Accepted, an ADR is immutable. Correct mistakes with a new ADR.
- Rejecting an alternative requires a reason, not just a preference.
- Every ADR must list its constitutional compliance.