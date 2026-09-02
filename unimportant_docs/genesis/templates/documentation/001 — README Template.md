Genesis Template (GTMP)
GTMP-010 — README Template

Document ID: GTMP-010
Title: README Template
Version: 1.0.0
Status: Template
Authority: Derived from GFS-000

1. Purpose

Blank template for module READMEs inside Genesis. Every top-level directory and
every shipped module should have a README that explains what lives there, why,
and how to work with it. READMEs are navigation aids, not specifications.

2. Template

```
# <ModuleName>

<One paragraph describing what this module contains and its role in Genesis.>

## What Lives Here

| Subdirectory / File | Purpose |
|---------------------|---------|
| <path> | <one-line purpose> |
| <path> | <one-line purpose> |

## What Does NOT Live Here

- <thing that does NOT belong here, and where it goes instead>
- <thing>

## Numbering Scheme

- Documents in this module use the <PREFIX>-NNN scheme.
- Numbering is unique within the module, not globally.

## Dependencies

- Depends on: <module list>
- Consumed by: <module list>

## Validation

- Documents here are validated by: <GVAL-NNN list>
- Schemas here are validated by: <GVAL-NNN list>

## Related

- Constitution: <GFS-NNN>
- Architecture: <GARCH-NNN>
- Workflow: <GWS-NNN>

## See Also

- <link to related module README>
- <link to guide GDE-NNN>
```

3. Usage Notes

- Keep READMEs under 120 lines. Detailed material belongs in a spec or guide.
- Do not duplicate content from specifications; link to them.
- A README answers "where am I and where do I go next?", not "how does it work?".