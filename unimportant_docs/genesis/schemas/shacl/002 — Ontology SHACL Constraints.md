Genesis Schema Specification (GSS)
GSS-205 — Ontology SHACL Constraints

Document ID: GSS-205
Title: Ontology SHACL Constraints
Version: 1.0.0
Status: Schema Specification
Authority: Derived from GFS-000, GFS-009, GO-001

1. Purpose

This document specifies SHACL shapes that validate Genesis Ontology files
themselves — not their PKG instances. Every ontology document (GO-001 through
GO-NNN) MUST pass these shapes before it may be promoted to `Status: Approved`
by the Governance Ontology Framework.

This enforces the constitutional invariant that every ontology inherits from
GO-001 and that canonical names remain immutable across versions (GFS-000 §17,
GO-001 §24).

2. Namespaces

```turtle
@prefix go:   <urn:genesis:ontology:> .
@prefix sha:  <urn:genesis:ontology:shacl:> .
@prefix sh:   <http://www.w3.org/ns/shacl#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix dct:  <http://purl.org/dc/terms/> .
```

3. Ontology Document Shape

```turtle
sha:OntologyDocumentShape a sh:NodeShape ;
  sh:targetClass owl:Ontology ;
  sh:property [
    sh:path dct:identifier ;
    sh:pattern "^GO-\\d{3}$" ;
    sh:minCount 1 ; sh:maxCount 1 ;
    sh:message "Ontology must declare a GO-NNN identifier." ;
  ] ;
  sh:property [
    sh:path dct:title ;
    sh:datatype xsd:string ;
    sh:minCount 1 ; sh:maxCount 1 ;
  ] ;
  sh:property [
    sh:path dct:hasVersion ;
    sh:datatype xsd:string ;
    sh:pattern "^\\d+\\.\\d+\\.\\d+$" ;
    sh:minCount 1 ; sh:maxCount 1 ;
  ] ;
  sh:property [
    sh:path go:status ;
    sh:in ( "Draft" "Reviewed" "Approved" "Published" "Deprecated" "Archived" ) ;
    sh:minCount 1 ; sh:maxCount 1 ;
  ] ;
  sh:property [
    sh:path go:authority ;
    sh:datatype xsd:string ;
    sh:minCount 1 ;
  ] .
```

4. Concept Shape

Every concept declared in an ontology must conform to GO-001 §19 (Canonical
Naming).

```turtle
sha:ConceptShape a sh:NodeShape ;
  sh:targetClass go:Concept ;
  sh:property [
    sh:path go:stableIdentifier ;
    sh:nodeKind sh:IRI ;
    sh:minCount 1 ; sh:maxCount 1 ;
    sh:message "Every concept must declare a stable IRI identifier." ;
  ] ;
  sh:property [
    sh:path go:canonicalName ;
    sh:datatype xsd:string ;
    sh:minCount 1 ; sh:maxCount 1 ;
    sh:severity sh:Violation ;
    sh:message "Canonical names are immutable (GO-001 §24)." ;
  ] ;
  sh:property [
    sh:path rdfs:label ;
    sh:datatype xsd:string ;
    sh:minCount 1 ;
  ] ;
  sh:property [
    sh:path rdfs:comment ;
    sh:datatype xsd:string ;
    sh:minCount 1 ;
    sh:message "Every concept must have a human-readable definition." ;
  ] ;
  sh:property [
    sh:path go:semanticDefinition ;
    sh:datatype xsd:string ;
    sh:minCount 1 ;
  ] ;
  sh:property [
    sh:path go:examples ;
    sh:datatype xsd:string ;
  ] .
```

5. Inheritance Shape

Enforces that every non-root concept subClassOf go:Thing or a descendant.

```turtle
sha:InheritanceShape a sh:NodeShape ;
  sh:targetClass go:Concept ;
  sh:or (
    [ sh:path rdfs:subClassOf ; sh:hasValue go:Thing ]
    [ sh:path rdfs:subClassOf ;
      sh:qualifiedValueShape [ sh:class go:Concept ] ;
      sh:qualifiedMinCount 1 ]
  ) ;
  sh:message "Every concept must transitively inherit from go:Thing (GO-001 §5)." .
```

6. Relationship Shape

```turtle
sha:RelationshipShape a sh:NodeShape ;
  sh:targetClass go:Relationship ;
  sh:property [
    sh:path go:predicateName ;
    sh:datatype xsd:string ;
    sh:minCount 1 ; sh:maxCount 1 ;
  ] ;
  sh:property [
    sh:path go:cardinality ;
    sh:in ( "1..1" "0..1" "1..*" "0..*" "n..m" ) ;
    sh:minCount 1 ; sh:maxCount 1 ;
  ] ;
  sh:property [
    sh:path go:directionality ;
    sh:in ( "directed" "bidirectional" "undirected" ) ;
    sh:minCount 1 ; sh:maxCount 1 ;
  ] ;
  sh:property [
    sh:path go:transitive ;
    sh:datatype xsd:boolean ;
    sh:minCount 1 ; sh:maxCount 1 ;
  ] ;
  sh:property [
    sh:path go:symmetric ;
    sh:datatype xsd:boolean ;
    sh:minCount 1 ; sh:maxCount 1 ;
  ] .
```

7. Extension Constraint

Domain ontologies MUST declare the ontology they extend.

```turtle
sha:ExtensionShape a sh:NodeShape ;
  sh:targetClass go:DomainOntology ;
  sh:property [
    sh:path go:extends ;
    sh:nodeKind sh:IRI ;
    sh:minCount 1 ;
    sh:message "Domain ontologies must declare the parent ontology (GO-001 §23)." ;
  ] ;
  sh:sparql [
    sh:message "Domain concept must not contradict parent (GO-001 §24)." ;
    sh:prefixes [ sh:declare [ sh:prefix "go" ; sh:namespace <urn:genesis:ontology:> ] ] ;
    sh:select """
      SELECT $this WHERE {
        $this go:contradicts ?parentConcept .
        FILTER NOT EXISTS { $this go:extends/go:supersedes ?parentConcept }
      }
    """ ;
  ] .
```

8. Status Transition Shape

Enforces the lifecycle in GO-001 §20.

```turtle
sha:StatusTransitionShape a sh:NodeShape ;
  sh:targetClass owl:Ontology ;
  sh:sparql [
    sh:message "Status must follow lifecycle: Proposed → Reviewed → Validated → Approved → Published → Deprecated → Archived." ;
    sh:prefixes [ sh:declare [ sh:prefix "go" ; sh:namespace <urn:genesis:ontology:> ] ] ;
    sh:select """
      SELECT $this WHERE {
        $this go:status ?new ; go:previousStatus ?old .
        FILTER NOT EXISTS {
          (?old ?new) IN (
            ("Proposed","Reviewed"), ("Reviewed","Validated"),
            ("Validated","Approved"), ("Approved","Published"),
            ("Published","Deprecated"), ("Deprecated","Archived")
          )
        }
      }
    """ ;
  ] .
```

9. Validation Procedure

1. The Ontology Compiler (GSPEC-COMP-001) parses each ontology Markdown file
   into RDF/Turtle via the GO Markdown grammar.
2. Load the resulting ontology graph with `sha:*` shapes into pySHACL.
3. Any `sh:Violation` blocks promotion of the ontology to `Approved`.
4. Validation report is attached to the ontology's Decision Record.

```bash
genesis validate ontology --ontology go-104 --shapes gss-205
```

10. Severity Policy

- Lifecycle and inheritance violations: `sh:Violation` (blocking).
- Missing examples: `sh:Warning` (advisory).
- Missing synonyms: `sh:Info`.

11. Relationship to Other Schemas

- Pairs with GSS-201 (PKG SHACL Constraints) which validates PKG instances.
- Consumed by GSPEC-COMP-001 (Ontology Compiler) and GWS-VALID-001 (Ontology
  Validation Workflow).
- References GSS-401 (Genesis Core OWL Ontology) for the OWL representation.

12. Revision History

- 1.0.0 — Initial draft. Derived from GO-001 v1.0.0.