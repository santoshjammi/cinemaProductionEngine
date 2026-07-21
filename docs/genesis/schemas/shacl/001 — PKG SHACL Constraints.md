Genesis Schema Specification (GSS)
GSS-201 — PKG SHACL Constraints

Document ID: GSS-201
Title: PKG SHACL Constraints
Version: 1.0.0
Status: Schema Specification
Authority: Derived from GFS-010, GSS-001, GSS-205

1. Purpose

This document specifies SHACL (Shapes Constraint Language) shapes that validate
the Production Knowledge Graph (PKG) when serialized as RDF. SHACL provides
declarative, graph-native validation that complements the JSON Schema
validation in GSS-001.

Use these shapes to ensure every PKG node and edge conforms to the Genesis
Core Ontology (GO-001) and its derived domain ontologies before a Production
Knowledge Package is sealed.

2. Namespaces

```turtle
@prefix ex:        <urn:genesis:> .
@prefix pkg:       <urn:genesis:pkg:> .
@prefix go:        <urn:genesis:ontology:> .
@prefix sh:        <http://www.w3.org/ns/shacl#> .
@prefix xsd:       <http://www.w3.org/2001/XMLSchema#> .
@prefix rdf:       <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:      <http://www.w3.org/2000/01/rdf-schema#> .
@prefix prov:      <urn:genesis:provenance:> .
```

3. PKG Graph Shape

Validates the root PKG resource.

```turtle
pkg:GraphShape a sh:NodeShape ;
  sh:targetClass pkg:ProductionKnowledgeGraph ;
  sh:property [
    sh:path pkg:hasNode ;
    sh:minCount 1 ;
    sh:node pkg:NodeShape ;
    sh:message "PKG must contain at least one node." ;
  ] ;
  sh:property [
    sh:path pkg:hasEdge ;
    sh:node pkg:EdgeShape ;
  ] ;
  sh:property [
    sh:path pkg:version ;
    sh:datatype xsd:string ;
    sh:pattern "^\\d+\\.\\d+\\.\\d+$" ;
    sh:minCount 1 ; sh:maxCount 1 ;
  ] ;
  sh:property [
    sh:path pkg:productionId ;
    sh:datatype xsd:string ;
    sh:minCount 1 ; sh:maxCount 1 ;
  ] .
```

4. Node Shape

Every PKG node MUST have a stable identifier, a type derived from a Genesis
ontology concept, a confidence value in [0,1], and a provenance link.

```turtle
pkg:NodeShape a sh:NodeShape ;
  sh:targetClass pkg:Node ;
  sh:property [
    sh:path pkg:nodeId ;
    sh:datatype xsd:string ;
    sh:pattern "^urn:genesis:[a-z]+:[0-9a-fA-F-]+$" ;
    sh:minCount 1 ; sh:maxCount 1 ;
    sh:name "stable URN identifier" ;
  ] ;
  sh:property [
    sh:path rdf:type ;
    sh:minCount 1 ;
    sh:message "Every node must declare an rdf:type derived from a GO concept." ;
  ] ;
  sh:property [
    sh:path pkg:conceptType ;
    sh:nodeKind sh:IRI ;
    sh:minCount 1 ; sh:maxCount 1 ;
    sh:class go:Thing ;
    sh:message "conceptType must be a subclass of go:Thing." ;
  ] ;
  sh:property [
    sh:path pkg:confidence ;
    sh:datatype xsd:double ;
    sh:minInclusive 0.0 ;
    sh:maxInclusive 1.0 ;
    sh:minCount 1 ; sh:maxCount 1 ;
  ] ;
  sh:property [
    sh:path pkg:knowledgeClass ;
    sh:in ( "explicit" "inferred" "confirmed" "assumed" "unknown" ) ;
    sh:minCount 1 ; sh:maxCount 1 ;
  ] ;
  sh:property [
    sh:path prov:hasProvenance ;
    sh:node prov:ProvenanceShape ;
    sh:minCount 1 ;
  ] .
```

5. Edge Shape

```turtle
pkg:EdgeShape a sh:NodeShape ;
  sh:targetClass pkg:Edge ;
  sh:property [
    sh:path pkg:edgeId ;
    sh:datatype xsd:string ;
    sh:pattern "^urn:genesis:edge:[0-9a-fA-F-]+$" ;
    sh:minCount 1 ; sh:maxCount 1 ;
  ] ;
  sh:property [
    sh:path pkg:source ;
    sh:node pkg:NodeShape ;
    sh:minCount 1 ; sh:maxCount 1 ;
  ] ;
  sh:property [
    sh:path pkg:target ;
    sh:node pkg:NodeShape ;
    sh:minCount 1 ; sh:maxCount 1 ;
  ] ;
  sh:property [
    sh:path pkg:predicate ;
    sh:nodeKind sh:IRI ;
    sh:minCount 1 ; sh:maxCount 1 ;
    sh:class go:Relationship ;
  ] ;
  sh:property [
    sh:path pkg:confidence ;
    sh:datatype xsd:double ;
    sh:minInclusive 0.0 ; sh:maxInclusive 1.0 ;
  ] .
```

6. Character Node Specialization

```turtle
pkg:CharacterShape a sh:NodeShape ;
  sh:targetClass go:Character ;
  sh:property [
    sh:path pkg:hasCoreMotivation ;
    sh:datatype xsd:string ;
    sh:minCount 1 ; sh:maxCount 1 ;
    sh:message "Every character must declare a core motivation." ;
  ] ;
  sh:property [
    sh:path pkg:hasArc ;
    sh:datatype xsd:string ;
    sh:minCount 1 ;
  ] ;
  sh:property [
    sh:path pkg:hasRelationship ;
    sh:node pkg:EdgeShape ;
  ] .
```

7. Scene Node Specialization

```turtle
pkg:SceneShape a sh:NodeShape ;
  sh:targetClass go:Scene ;
  sh:property [
    sh:path pkg:hasBeat ;
    sh:minCount 1 ;
    sh:message "A scene must contain at least one beat." ;
  ] ;
  sh:property [
    sh:path pkg:hasFocalParticipant ;
    sh:minCount 1 ; sh:maxCount 1 ;
    sh:node pkg:NodeShape ;
  ] ;
  sh:property [
    sh:path pkg:producesKnowledgeDelta ;
    sh:minCount 1 ;
    sh:message "Every scene must produce a knowledge delta (GFS-000 §6)." ;
  ] .
```

8. Provenance Shape

```turtle
prov:ProvenanceShape a sh:NodeShape ;
  sh:targetClass prov:Provenance ;
  sh:property [
    sh:path prov:agent ; sh:minCount 1 ; sh:maxCount 1 ;
    sh:nodeKind sh:IRI ;
  ] ;
  sh:property [
    sh:path prov:session ; sh:minCount 1 ; sh:maxCount 1 ;
    sh:nodeKind sh:IRI ;
  ] ;
  sh:property [
    sh:path prov:decisionId ; sh:minCount 1 ; sh:maxCount 1 ;
    sh:nodeKind sh:IRI ;
  ] ;
  sh:property [
    sh:path prov:evidence ;
    sh:datatype xsd:string ;
  ] .
```

9. Validation Procedure

1. Serialize the PKG to RDF/Turtle per GSS-301.
2. Load the PKG graph and this shapes graph into a SHACL engine (pySHACL,
   TopBraid, or rdflib-shacl).
3. Run `sh:validate` over `pkg:GraphShape`, `pkg:NodeShape`, `pkg:EdgeShape`,
   and every specialization shape.
4. Emit a validation report; non-conformant nodes are returned to the
   originating agent for repair.

```bash
genesis validate pkg --pkg <pkg-id> --shapes gss-201
```

10. Severity Policy

- `sh:Violation` blocks sealing the Production Knowledge Package.
- `sh:Warning` flags for human review but does not block.
- `sh:Info` is advisory only.

11. Relationship to Other Schemas

- Pairs with GSS-205 (Ontology SHACL Constraints) which validates the ontology
  files themselves.
- Reads from GSS-301 (PKG RDF Serialization).
- Read by GSPEC-COMP-001 (Ontology Compiler) during the validate phase.

12. Revision History

- 1.0.0 — Initial draft. Derived from GSS-001 v1.0.0 and GO-001 v1.0.0.