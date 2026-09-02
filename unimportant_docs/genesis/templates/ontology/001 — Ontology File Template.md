Genesis Template (GTMP)
GTMP-002 — Ontology File Template

Document ID: GTMP-002
Title: Ontology File Template
Version: 1.0.0
Status: Template
Authority: Derived from GFS-000

1. Purpose

This is a blank template for creating a new ontology file within Genesis. Copy
this file into `ontology/<domain>/` and fill in the sections. Every ontology
must derive from the Core Ontology (GO-001) and conform to the Constitutional
Charter (GFS-000).

2. Template

```
Genesis Ontology (GO)
GO-NNN — <Domain> Ontology

Document ID: GO-NNN
Title: <Domain> Ontology
Version: 1.0.0
Status: Draft | Validated | Canonical
Authority: Derived from GO-001

1. Purpose
<One paragraph describing what this ontology defines and why it exists.>

2. Domain
<The knowledge domain this ontology governs — e.g. Character, Narrative, Visual.>

3. Classes
For each class:
- Name: <ClassName>
- Parent: <ParentClass or None>
- Description: <what instances of this class represent>
- Properties:
  - <property>: <type> — <cardinality> — <description>
  - <property>: <type> — <cardinality> — <description>
- Constraints:
  - <constraint expression>

4. Relationships
For each relationship:
- Name: <relName>
- Domain: <ClassA>
- Range: <ClassB>
- Cardinality: <1:1 | 1:N | M:N>
- Inverse: <inverseRelName or None>
- Description: <semantic meaning>

5. Rules
- <If A then B>
- <Cardinality rule>
- <Co-occurrence rule>

6. Classification Tiers
Each assertion derived from this ontology must classify as:
- Explicit
- Inferred
- Confirmed
- Assumed
- Unknown

7. Traceability
Every class, relationship, and rule must record:
- Origin (which constitution or ontology it derives from)
- Evidence required for instantiation
- Confidence threshold for promotion to Confirmed

8. Validation
- Structural: conforms to GO-001 metamodel
- Semantic: no contradictions with parent ontologies
- Completeness: all required properties populated
- Confidence: assertions meet tier thresholds

9. Dependencies
- GO-001 Core Ontology
- <other GO-NNN ontologies referenced>
```

3. Usage Notes

- Number with the GO-NNN scheme (see AGENTS.md).
- Place in `ontology/<domain>/`.
- All class and relationship names use PascalCase.
- All property names use camelCase.
- Do not duplicate concepts already defined in parent ontologies; extend them.