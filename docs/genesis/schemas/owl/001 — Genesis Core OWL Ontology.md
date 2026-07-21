Genesis Schema Specification (GSS)
GSS-401 — Genesis Core OWL Ontology

Document ID: GSS-401
Title: Genesis Core OWL Ontology
Version: 1.0.0
Status: Schema Specification
Authority: Derived from GFS-000 through GFS-009, GO-001

1. Purpose

This document provides the OWL2/RDF representation of the Genesis Core
Ontology (GO-001). It translates GO-001's conceptual domains, concepts, and
relationships into a machine-processable Web Ontology Language ontology that
can be loaded by reasoners (HermiT, Pellet, ELK, Stardog), used by SHACL
engines, and merged with domain ontologies.

OWL is the formal layer beneath GO-001. The Markdown document is human-first;
this OWL file is reasoner-first. Where the two disagree, GO-001 prevails and
this file must be corrected.

2. Namespaces

```turtle
@prefix :       <urn:genesis:ontology:core#> .
@prefix go:     <urn:genesis:ontology:> .
@prefix gfs:    <urn:genesis:constitution:> .
@prefix rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:   <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl:    <http://www.w3.org/2002/07/owl#> .
@prefix xsd:    <http://www.w3.org/2001/XMLSchema#> .
@prefix dct:    <http://purl.org/dc/terms/> .
```

3. Ontology Declaration

```turtle
<urn:genesis:ontology:GO-001> a owl:Ontology ;
  dct:identifier "GO-001" ;
  dct:title "Genesis Core Ontology" ;
  dct:hasVersion "1.0.0" ;
  go:status "Published" ;
  go:authority "Derived from GFS-000 through GFS-009" ;
  rdfs:comment "Canonical semantic vocabulary of the Genesis Engine." .
```

4. Universal Root

```turtle
go:Thing a owl:Class ;
  rdfs:label "Thing" ;
  rdfs:comment "Universal root concept. Every ontology concept derives from Thing." ;
  go:stableIdentifier "go:Thing" ;
  go:canonicalName "Thing" .
```

5. Identity Domain

```turtle
go:Identity a owl:Class ; rdfs:subClassOf go:Thing .
go:Alias a owl:Class ; rdfs:subClassOf go:Thing .
go:Identifier a owl:Class ; rdfs:subClassOf go:Thing .
go:Version a owl:Class ; rdfs:subClassOf go:Thing .
go:State a owl:Class ; rdfs:subClassOf go:Thing .
go:Lifecycle a owl:Class ; rdfs:subClassOf go:Thing .
go:Context a owl:Class ; rdfs:subClassOf go:Thing .

go:hasIdentity a owl:ObjectProperty ;
  rdfs:domain go:Thing ; rdfs:range go:Identity .
```

6. Knowledge Domain

```turtle
go:KnowledgeObject a owl:Class ; rdfs:subClassOf go:Thing .
go:Evidence a owl:Class ; rdfs:subClassOf go:Thing .
go:Observation a owl:Class ; rdfs:subClassOf go:Thing .
go:Information a owl:Class ; rdfs:subClassOf go:Thing .
go:Knowledge a owl:Class ; rdfs:subClassOf go:Thing .
go:Understanding a owl:Class ; rdfs:subClassOf go:Thing .
go:Decision a owl:Class ; rdfs:subClassOf go:Thing .
go:Assumption a owl:Class ; rdfs:subClassOf go:Thing .
go:Unknown a owl:Class ; rdfs:subClassOf go:Thing .
go:Confidence a owl:Class ; rdfs:subClassOf go:Thing .
go:Traceability a owl:Class ; rdfs:subClassOf go:Thing .
go:Lineage a owl:Class ; rdfs:subClassOf go:Thing .

go:hasConfidence a owl:DatatypeProperty ;
  rdfs:domain go:KnowledgeObject ;
  rdfs:range xsd:double .

go:knowledgeClass a owl:DatatypeProperty ;
  rdfs:range [
    a owl:DataRange ;
    owl:oneOf ( "explicit" "inferred" "confirmed" "assumed" "unknown" )
  ] .
```

7. Narrative Domain

```turtle
go:Story a owl:Class ; rdfs:subClassOf go:Thing .
go:Narrative a owl:Class ; rdfs:subClassOf go:Thing .
go:Theme a owl:Class ; rdfs:subClassOf go:Thing .
go:Conflict a owl:Class ; rdfs:subClassOf go:Thing .
go:Plot a owl:Class ; rdfs:subClassOf go:Thing .
go:Arc a owl:Class ; rdfs:subClassOf go:Thing .
go:Event a owl:Class ; rdfs:subClassOf go:Thing .
go:Sequence a owl:Class ; rdfs:subClassOf go:Thing .
go:Timeline a owl:Class ; rdfs:subClassOf go:Thing .
go:Emotion a owl:Class ; rdfs:subClassOf go:Thing .
go:Motivation a owl:Class ; rdfs:subClassOf go:Thing .
go:Objective a owl:Class ; rdfs:subClassOf go:Thing .

go:expresses a owl:ObjectProperty ; rdfs:domain go:Narrative ; rdfs:range go:Theme .
go:evokes a owl:ObjectProperty ; rdfs:domain go:Theme ; rdfs:range go:Emotion .
go:hasArc a owl:ObjectProperty ; rdfs:domain go:Character ; rdfs:range go:Arc .
```

8. Character Domain

```turtle
go:Character a owl:Class ; rdfs:subClassOf go:Thing .
go:Persona a owl:Class ; rdfs:subClassOf go:Thing .
go:Relationship a owl:Class ; rdfs:subClassOf go:Thing .
go:Goal a owl:Class ; rdfs:subClassOf go:Thing .
go:Need a owl:Class ; rdfs:subClassOf go:Thing .
go:Fear a owl:Class ; rdfs:subClassOf go:Thing .
go:Belief a owl:Class ; rdfs:subClassOf go:Thing .
go:Transformation a owl:Class ; rdfs:subClassOf go:Thing .
go:Behavior a owl:Class ; rdfs:subClassOf go:Thing .

go:Protagonist a owl:Class ; rdfs:subClassOf go:Character .
go:Antagonist a owl:Class ; rdfs:subClassOf go:Character .

go:hasGoal a owl:ObjectProperty ; rdfs:domain go:Character ; rdfs:range go:Goal .
go:hasMotivation a owl:ObjectProperty ; rdfs:domain go:Character ; rdfs:range go:Motivation .
go:hasFear a owl:ObjectProperty ; rdfs:domain go:Character ; rdfs:range go:Fear .
go:hasTransformation a owl:ObjectProperty ;
  rdfs:domain go:Character ; rdfs:range go:Transformation .
```

9. World Domain

```turtle
go:World a owl:Class ; rdfs:subClassOf go:Thing .
go:Environment a owl:Class ; rdfs:subClassOf go:Thing .
go:Location a owl:Class ; rdfs:subClassOf go:Thing .
go:Region a owl:Class ; rdfs:subClassOf go:Thing .
go:Object a owl:Class ; rdfs:subClassOf go:Thing .
go:Culture a owl:Class ; rdfs:subClassOf go:Thing .
go:Rule a owl:Class ; rdfs:subClassOf go:Thing .
go:Resource a owl:Class ; rdfs:subClassOf go:Thing .
go:History a owl:Class ; rdfs:subClassOf go:Thing .
go:Time a owl:Class ; rdfs:subClassOf go:Thing .

go:hasLocation a owl:ObjectProperty ; rdfs:domain go:World ; rdfs:range go:Location .
go:hasRule a owl:ObjectProperty ; rdfs:domain go:World ; rdfs:range go:Rule .
```

10. Relationship Domain

```turtle
go:IsA a owl:ObjectProperty ; rdfs:subPropertyOf owl:topObjectProperty .
go:HasA a owl:ObjectProperty ; rdfs:subPropertyOf owl:topObjectProperty .
go:PartOf a owl:ObjectProperty .
go:DependsOn a owl:ObjectProperty .
go:References a owl:ObjectProperty .
go:Supports a owl:ObjectProperty .
go:Opposes a owl:ObjectProperty .
go:EvolvesInto a owl:ObjectProperty .
go:Influences a owl:ObjectProperty .
go:Contains a owl:ObjectProperty .
go:Requires a owl:ObjectProperty .
go:Creates a owl:ObjectProperty .
go:Validates a owl:ObjectProperty .
go:Represents a owl:ObjectProperty .

go:PartOf owl:inverseOf go:Contains .
go:Supports owl:inverseOf go:Requires .
```

11. Creative Intent Domain

```turtle
go:Vision a owl:Class ; rdfs:subClassOf go:Thing .
go:Mission a owl:Class ; rdfs:subClassOf go:Thing .
go:Audience a owl:Class ; rdfs:subClassOf go:Thing .
go:Experience a owl:Class ; rdfs:subClassOf go:Thing .
go:Purpose a owl:Class ; rdfs:subClassOf go:Thing .
go:Message a owl:Class ; rdfs:subClassOf go:Thing .
go:CreatorIntent a owl:Class ; rdfs:subClassOf go:Thing .
go:CreativeConstraint a owl:Class ; rdfs:subClassOf go:Thing .
```

12. Production Domain

```turtle
go:Production a owl:Class ; rdfs:subClassOf go:Thing .
go:Phase a owl:Class ; rdfs:subClassOf go:Thing .
go:Deliverable a owl:Class ; rdfs:subClassOf go:Thing .
go:Milestone a owl:Class ; rdfs:subClassOf go:Thing .
go:Dependency a owl:Class ; rdfs:subClassOf go:Thing .
go:Specification a owl:Class ; rdfs:subClassOf go:Thing .
go:Blueprint a owl:Class ; rdfs:subClassOf go:Thing .
go:Workflow a owl:Class ; rdfs:subClassOf go:Thing .
go:Review a owl:Class ; rdfs:subClassOf go:Thing .
go:Approval a owl:Class ; rdfs:subClassOf go:Thing .
```

13. Governance Domain

```turtle
go:Standard a owl:Class ; rdfs:subClassOf go:Thing .
go:Registry a owl:Class ; rdfs:subClassOf go:Thing .
go:Role a owl:Class ; rdfs:subClassOf go:Thing .
go:Responsibility a owl:Class ; rdfs:subClassOf go:Thing .
go:DecisionRecord a owl:Class ; rdfs:subClassOf go:Thing .
go:Policy a owl:Class ; rdfs:subClassOf go:Thing .
go:Audit a owl:Class ; rdfs:subClassOf go:Thing .
go:Compliance a owl:Class ; rdfs:subClassOf go:Thing .
```

14. Reasoning Rules (SWRL-style)

```turtle
# If a Character has a Goal and the Goal supports a Narrative,
# then the Character participates in that Narrative.
[ a swrl:Imp ;
  swrl:body ( [ swrl:argument1 ?c ; swrl:classPredicate go:Character ]
              [ swrl:argument1 ?c ; swrl:argument2 ?g ; swrl:propertyPredicate go:hasGoal ]
              [ swrl:argument1 ?g ; swrl:argument2 ?n ; swrl:propertyPredicate go:Supports ] ) ;
  swrl:head ( [ swrl:argument1 ?n ; swrl:argument2 ?c ; swrl:propertyPredicate go:hasParticipant ] )
]
```

15. Consistency Axioms

```turtle
# Knowledge class disjointness (GFS-000 §6).
[ a owl:AllDisjointClasses ;
  owl:members ( go:Knowledge go:Assumption go:Unknown ) ] .

# Confidence range.
go:hasConfidence rdfs:range [ a owl:Restriction ;
  owl:onDatatype xsd:double ;
  owl:withRestrictions ( [ xsd:minInclusive 0.0 ] [ xsd:maxInclusive 1.0 ] ) ] .
```

16. Loading

```bash
genesis reason load --ontology gss-401 --reasoner hermit
genesis reason infer --ontology gss-401
genesis reason check --ontology gss-401 --shapes gss-205
```

17. Relationship to Other Schemas

- Source of truth: GO-001 (Markdown).
- Domain ontologies: GSS-402 (Narrative OWL Ontology) and others extend this
  file via `owl:imports`.
- Validated by GSS-205 (Ontology SHACL Constraints).
- Serialized into PKG nodes via GSS-301 (PKG RDF Serialization).

18. Revision History

- 1.0.0 — Initial draft. Mirrors GO-001 v1.0.0.