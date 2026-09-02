Genesis Template (GTMP)
GTMP-011 — Guide Template

Document ID: GTMP-011
Title: Guide Template
Version: 1.0.0
Status: Template
Authority: Derived from GFS-000

1. Purpose

Blank template for Genesis guides. Guides are procedural how-to documents that
walk a user or agent through a multi-step task. Place finished guides in
`guides/` or `docs/` with the GDE-NNN scheme.

2. Template

```
Genesis Guide (GDE)
GDE-NNN — <Title>

Document ID: GDE-NNN
Title: <Title>
Version: 1.0.0
Status: Draft | Reviewed | Published
Authority: Derived from GFS-000

1. Audience
<Who this guide is for — human creator, agent developer, validator operator.>

2. Goal
<One sentence describing what the reader will be able to do after reading.>

3. Prerequisites
- <prerequisite>
- <prerequisite>

4. Steps

Step 1: <action>
- What to do: <instruction>
- Expected result: <observable outcome>
- On failure: <what to check>

Step 2: <action>
- What to do: <instruction>
- Expected result: <observable outcome>
- On failure: <what to check>

Step 3: <action>
- What to do: <instruction>
- Expected result: <observable outcome>
- On failure: <what to check>

5. Verification
<How the reader confirms success. Include a concrete command or check.>

6. Common Mistakes
- <mistake> — fix: <action>
- <mistake> — fix: <action>

7. Next Steps
- <link to next guide>
- <link to related spec>

8. References
- <GFS-NNN, GARCH-NNN, GWS-NNN>
```

3. Usage Notes

- Guides are procedural; specifications are declarative. Do not mix them.
- Each step must have an observable expected result.
- If a step cannot be verified, it is not a step — it is a prerequisite.