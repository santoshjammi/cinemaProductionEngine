Genesis Template (GTMP)
GTMP-003 — Ontology Extension Template

Document ID: GTMP-003
Title: Ontology Extension Template
Version: 1.0.0
Status: Template
Authority: Derived from GFS-000

1. Purpose

This template is for extending an existing canonical ontology (GO-NNN) with new
classes, relationships, or rules without rewriting the parent. Extensions must
remain backward-compatible and must not contradict the parent ontology.

2. Template

```
Genesis Ontology Extension (GOX)
GOX-NNN — <Parent> Extension: <Topic>

Document ID: GOX-NNN
Title: <Parent> Extension: <Topic>
Version: 1.0.0
Status: Draft | Validated | Canonical
Authority: Derived from GO-<Parent>

1. Parent Ontology
- ID: GO-<NNN>
- Version: <x.y.z>
- Compatibility: <forward / backward / strict>

2. Purpose
<One paragraph describing why the extension is needed.>

3. New Classes
For each new class:
- Name: <ClassName>
- Parent: <existing ClassName from parent ontology>
- Description: <what it represents>
- Properties:
  - <property>: <type> — <cardinality>
- Constraints:
  - <constraint>

4. New Relationships
For each new relationship:
- Name: <relName>
- Domain: <ClassA>
- Range: <ClassB>
- Cardinality: <1:1 | 1:N | M:N>
- Inverse: <inverseRelName or None>
- Description: <semantic meaning>

5. New Rules
- <rule expression>
- <rule expression>

6. Backward Compatibility
- No parent class is removed or narrowed.
- No parent relationship is removed or reversed.
- All parent rules remain satisfied.

7. Validation
- Extension passes parent ontology validators.
- No class or relationship name collision with parent.
- All new rules are satisfiable.

8. Dependencies
- GO-<Parent>
- <other referenced ontologies>
```

3. Usage Notes

- Number with the GOX-NNN scheme.
- Place in `ontology/<domain>/extensions/`.
- Extensions cannot override parent rules; they only add.
- Promote an extension into the parent when it becomes universally required.