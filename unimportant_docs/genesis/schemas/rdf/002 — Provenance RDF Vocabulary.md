Genesis Schema Specification (GSS)
GSS-302 — Provenance RDF Vocabulary

Document ID: GSS-302
Title: Provenance RDF Vocabulary
Version: 1.0.0
Status: Schema Specification
Authority: Derived from GFS-000 §8, GO-001 §7, GSS-301

1. Purpose

This document defines the Genesis Provenance RDF vocabulary. Per the Charter
(GFS-000 §8), every decision must be traceable to its origin, supporting
evidence, dependent decisions, affected domains, confidence, and revision
history. This vocabulary makes that requirement machine-enforceable inside
the PKG.

The vocabulary extends W3C PROV-O where possible and adds Genesis-specific
terms for confidence, knowledge class, and decision lineage.

2. Namespaces

```turtle
@prefix prov:   <urn:genesis:provenance:> .
@prefix wprov:  <http://www.w3.org/ns/prov#> .
@prefix go:     <urn:genesis:ontology:> .
@prefix dec:    <urn:genesis:decision:> .
@prefix ag:     <urn:genesis:agent:> .
@prefix sess:   <urn:genesis:session:> .
@prefix ev:     <urn:genesis:evidence:> .
@prefix rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:   <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl:    <http://www.w3.org/2002/07/owl#> .
@prefix xsd:    <http://www.w3.org/2001/XMLSchema#> .
@prefix dct:    <http://purl.org/dc/terms/> .
```

3. Alignment with PROV-O

Genesis prov: terms map to PROV-O as follows. Where PROV-O already provides a
suitable term, Genesis uses PROV-O directly. Genesis-specific terms are
declared only when PROV-O is insufficient.

| Genesis term | PROV-O term | Note |
|---|---|---|
| `prov:agent` | `prov:wasAssociatedWith` | agent that produced a decision |
| `prov:session` | (none) | Genesis-specific |
| `prov:decisionId` | `prov:wasInformedBy` | links to the decision record |
| `prov:evidence` | `prov:used` | supporting evidence |
| `prov:timestamp` | `prov:atTime` | decision time |

4. Core Classes

```turtle
prov:Provenance a owl:Class ;
  rdfs:subClassOf wprov:Entity ;
  rdfs:comment "Provenance record attached to a PKG node or edge." .

ag:Agent a owl:Class ;
  rdfs:subClassOf wprov:Agent ;
  rdfs:comment "A Genesis agent that produced or reviewed a decision." .

sess:Session a owl:Class ;
  rdfs:comment "A single agent execution session." .

dec:DecisionRecord a owl:Class ;
  rdfs:subClassOf wprov:Activity ;
  rdfs:comment "A recorded decision with alternatives and confidence." .

ev:Evidence a owl:Class ;
  rdfs:subClassOf wprov:Entity ;
  rdfs:comment "Supporting evidence for a decision." .
```

5. Agent Class Hierarchy

```turtle
ag:OrchestratorAgent a owl:Class ; rdfs:subClassOf ag:Agent .
ag:ArchitectAgent a owl:Class ; rdfs:subClassOf ag:Agent .
ag:EngineerAgent a owl:Class ; rdfs:subClassOf ag:Agent .
ag:ValidatorAgent a owl:Class ; rdfs:subClassOf ag:Agent .
ag:DiscoveryAgent a owl:Class ; rdfs:subClassOf ag:Agent .
ag:ReasoningAgent a owl:Class ; rdfs:subClassOf ag:Agent .
```

6. Decision Record

```turtle
dec:DecisionRecord rdfs:subClassOf [
  a owl:Restriction ;
  owl:onProperty dec:hasQuestion ; owl:minCardinality "1"^^xsd:nonNegativeInteger
] ;
  rdfs:subClassOf [
  a owl:Restriction ;
  owl:onProperty dec:hasChosenOption ; owl:cardinality "1"^^xsd:nonNegativeInteger
] ;
  rdfs:subClassOf [
  a owl:Restriction ;
  owl:onProperty dec:hasConsideredOption ; owl:minCardinality "1"^^xsd:nonNegativeInteger
] .

dec:hasQuestion a owl:ObjectProperty ; rdfs:range ev:Evidence .
dec:hasChosenOption a owl:ObjectProperty ; rdfs:range dec:Option .
dec:hasConsideredOption a owl:ObjectProperty ; rdfs:range dec:Option .
dec:hasConfidence a owl:DatatypeProperty ;
  rdfs:range xsd:double ;
  rdfs:comment "Confidence in [0,1]." .
dec:hasRationale a owl:DatatypeProperty ; rdfs:range xsd:string .
dec:hasAffectedDomain a owl:ObjectProperty ; rdfs:range go:Thing .
dec:dependsOnDecision a owl:ObjectProperty ; rdfs:range dec:DecisionRecord .

dec:Option a owl:Class ;
  rdfs:comment "A possible answer considered for a decision." .
```

7. Evidence

```turtle
ev:Evidence rdfs:subClassOf [
  a owl:Restriction ;
  owl:onProperty ev:sourceUri ; owl:minCardinality "1"^^xsd:nonNegativeInteger
] .

ev:sourceUri a owl:DatatypeProperty ; rdfs:range xsd:string .
ev:sourceType a owl:DatatypeProperty ;
  rdfs:range [ a owl:DataRange ; owl:oneOf (
    "brief_line" "ontology_clause" "pkg_node" "pkg_edge"
    "external_reference" "agent_output" "user_input"
  ) ] .
ev:excerpt a owl:DatatypeProperty ; rdfs:range xsd:string .
ev:weight a owl:DatatypeProperty ;
  rdfs:range xsd:double ;
  rdfs:comment "Relative weight of this evidence in the decision." .
```

8. Revision History

```turtle
dec:hasRevision a owl:ObjectProperty ;
  rdfs:domain dec:DecisionRecord ;
  rdfs:range dec:Revision .

dec:Revision a owl:Class ;
  rdfs:comment "A historical state of a decision." .

dec:revisionNumber a owl:DatatypeProperty ; rdfs:range xsd:integer .
dec:revisionTimestamp a owl:DatatypeProperty ; rdfs:range xsd:dateTime .
dec:revisionAgent a owl:ObjectProperty ; rdfs:range ag:Agent .
dec:revisionReason a owl:DatatypeProperty ; rdfs:range xsd:string .
dec:supersedes a owl:ObjectProperty ; rdfs:domain dec:Revision ; rdfs:range dec:Revision .
```

9. Provenance Attached to PKG Nodes

```turtle
<urn:genesis:node:<n1>> prov:hasProvenance <urn:genesis:provenance:<p1>> .

<urn:genesis:provenance:<p1>> a prov:Provenance ;
  prov:agent <urn:genesis:agent:character-architect> ;
  prov:session <urn:genesis:session:<s1>> ;
  prov:decisionId <urn:genesis:decision:<d1>> ;
  prov:evidence "Brief line 14: 'reluctant warrior'" ;
  prov:confidence "0.92"^^xsd:double ;
  prov:timestamp "2026-07-19T10:14:00Z"^^xsd:dateTime .
```

10. Decision Lineage Queries

Find all upstream decisions a given decision depends on (transitive closure):

```sparql
PREFIX dec: <urn:genesis:decision:>
SELECT ?upstream WHERE {
  ?this dec:dependsOnDecision+ ?upstream .
}
```

Find every PKG node affected by a decision:

```sparql
PREFIX prov: <urn:genesis:provenance:>
PREFIX node: <urn:genesis:node:>
SELECT ?node WHERE {
  ?node prov:hasProvenance/prov:decisionId <urn:genesis:decision:<d1> .
}
```

11. Validation Rules

- Every `prov:Provenance` MUST have `prov:agent`, `prov:session`, and
  `prov:decisionId`.
- `prov:confidence` MUST be in [0, 1].
- Every `dec:DecisionRecord` MUST have at least one `dec:hasConsideredOption`
  distinct from `dec:hasChosenOption`.
- Every `dec:Revision` other than the first MUST `dec:supersedes` the previous
  revision.

12. Tooling

```bash
genesis provenance trace --node <urn:genesis:node:<uuid>>
genesis provenance decisions --pkg <pkg-id>
genesis provenance lineage --decision <urn:genesis:decision:<uuid>>
```

13. Relationship to Other Schemas

- Consumed by GSS-301 (PKG RDF Serialization) for `prov:hasProvenance`.
- Consumed by GSS-201 (PKG SHACL Constraints) for the ProvenanceShape.
- Read by the Discovery and Reasoning agents (GAS-007, GAS-008).

14. Revision History

- 1.0.0 — Initial draft. Aligned with PROV-O and GO-001 §7.