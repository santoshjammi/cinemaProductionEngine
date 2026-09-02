Genesis Schema Specification (GSS)
GSS-402 — Narrative OWL Ontology

Document ID: GSS-402
Title: Narrative OWL Ontology
Version: 1.0.0
Status: Schema Specification
Authority: Derived from GO-001, GO-101 (Narrative Ontology)

1. Purpose

This document provides the OWL2/RDF representation of the Narrative Ontology
(GO-101). GO-101 extends the Core Ontology (GO-001 / GSS-401) with
domain-specific concepts for story structure, dramatic units, narrative
mechanics, and storytelling devices. This file is reasoner-first; the
authoritative human-readable source is GO-101.

2. Imports

```turtle
@prefix :       <urn:genesis:ontology:narrative#> .
@prefix go:     <urn:genesis:ontology:> .
@prefix narr:   <urn:genesis:ontology:narrative:> .
@prefix rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:   <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl:    <http://www.w3.org/2002/07/owl#> .
@prefix xsd:    <http://www.w3.org/2001/XMLSchema#> .
@prefix dct:    <http://purl.org/dc/terms/> .

<urn:genesis:ontology:GO-101> a owl:Ontology ;
  dct:identifier "GO-101" ;
  dct:title "Narrative Ontology" ;
  dct:hasVersion "1.0.0" ;
  go:status "Published" ;
  go:authority "Derived from GO-001" ;
  owl:imports <urn:genesis:ontology:GO-001> ;
  rdfs:comment "Domain ontology for narrative structure and dramatic units." .
```

3. Structural Concepts

```turtle
narr:Act a owl:Class ; rdfs:subClassOf go:Sequence .
narr:Sequence a owl:Class ; rdfs:subClassOf go:Sequence .
narr:Scene a owl:Class ; rdfs:subClassOf go:Event .
narr:Beat a owl:Class ; rdfs:subClassOf go:Event .
narr:Frame a owl:Class ; rdfs:subClassOf go:Event .
narr:Plotline a owl:Class ; rdfs:subClassOf go:Plot .
narr:Subplot a owl:Class ; rdfs:subClassOf go:Plot .

narr:hasAct a owl:ObjectProperty ;
  rdfs:domain narr:ActStructure ; rdfs:range narr:Act .
narr:hasSequence a owl:ObjectProperty ;
  rdfs:domain narr:Act ; rdfs:range narr:Sequence .
narr:hasScene a owl:ObjectProperty ;
  rdfs:domain narr:Sequence ; rdfs:range narr:Scene .
narr:hasBeat a owl:ObjectProperty ;
  rdfs:domain narr:Scene ; rdfs:range narr:Beat .

# Containment is strictly hierarchical.
[ a owl:TransitiveProperty ; owl:equivalentProperty go:Contains ] .
```

4. Dramatic Units

```turtle
narr:IncitingIncident a owl:Class ; rdfs:subClassOf narr:Beat .
narr:RisingAction a owl:Class ; rdfs:subClassOf narr:Beat .
narr:Midpoint a owl:Class ; rdfs:subClassOf narr:Beat .
narr:Crisis a owl:Class ; rdfs:subClassOf narr:Beat .
narr:Climax a owl:Class ; rdfs:subClassOf narr:Beat .
narr:Resolution a owl:Class ; rdfs:subClassOf narr:Beat .
narr:Denouement a owl:Class ; rdfs:subClassOf narr:Beat .

# A Climax must be preceded (in story-time) by a Crisis.
narr:Climax rdfs:subClassOf [
  a owl:Restriction ;
  owl:onProperty narr:precededBy ;
  owl:someValuesFrom narr:Crisis
] .
```

5. Conflict Model

```turtle
narr:ConflictType a owl:Class .
narr:InternalConflict a owl:Class ; rdfs:subClassOf narr:ConflictType .
narr:InterpersonalConflict a owl:Class ; rdfs:subClassOf narr:ConflictType .
narr:SocietalConflict a owl:Class ; rdfs:subClassOf narr:ConflictType .
narr:CosmicConflict a owl:Class ; rdfs:subClassOf narr:ConflictType .

[ a owl:AllDisjointClasses ;
  owl:members ( narr:InternalConflict narr:InterpersonalConflict
                narr:SocietalConflict narr:CosmicConflict ) ] .

narr:hasConflict a owl:ObjectProperty ;
  rdfs:domain narr:Scene ; rdfs:range go:Conflict .
narr:conflictType a owl:ObjectProperty ;
  rdfs:domain go:Conflict ; rdfs:range narr:ConflictType .
```

6. Arc and Transformation

```turtle
narr:CharacterArc a owl:Class ; rdfs:subClassOf go:Arc .
narr:PositiveArc a owl:Class ; rdfs:subClassOf narr:CharacterArc .
narr:FlatArc a owl:Class ; rdfs:subClassOf narr:CharacterArc .
narr:NegativeArc a owl:Class ; rdfs:subClassOf narr:CharacterArc .

[ a owl:AllDisjointClasses ;
  owl:members ( narr:PositiveArc narr:FlatArc narr:NegativeArc ) ] .

narr:hasWound a owl:ObjectProperty ; rdfs:domain go:Character ; rdfs:range narr:Wound .
narr:hasGhost a owl:ObjectProperty ; rdfs:domain go:Character ; rdfs:range narr:Ghost .
narr:hasLie a owl:ObjectProperty ; rdfs:domain go:Character ; rdfs:range narr:Lie .
narr:hasTruth a owl:ObjectProperty ; rdfs:domain go:Character ; rdfs:range narr:Truth .

narr:Wound a owl:Class ; rdfs:subClassOf go:Event .
narr:Ghost a owl:Class ; rdfs:subClassOf go:Event .
narr:Lie a owl:Class ; rdfs:subClassOf go:Belief .
narr:Truth a owl:Class ; rdfs:subClassOf go:Belief .

# Lie and Truth are disjoint within the same character.
narr:Lie owl:disjointWith narr:Truth .
```

7. Temporal Mechanics

```turtle
narr:StoryTime a owl:Class ; rdfs:subClassOf go:Time .
narr:DiscourseTime a owl:Class ; rdfs:subClassOf go:Time .
narr:ScreenTime a owl:Class ; rdfs:subClassOf go:Time .

narr:order a owl:ObjectProperty ; rdfs:range [
  a owl:DataRange ; owl:oneOf ( "chronological" "anachronic" "achronic" )
] .
narr:duration a owl:DatatypeProperty ; rdfs:range xsd:integer .
narr:frequency a owl:DatatypeProperty ; rdfs:range xsd:integer .
```

8. Scene-Level Constraints

```turtle
# Every scene must have exactly one focal participant.
narr:Scene rdfs:subClassOf [
  a owl:Restriction ;
  owl:onProperty narr:hasFocalParticipant ;
  owl:cardinality "1"^^xsd:nonNegativeInteger
] .

# Every scene must produce at least one knowledge delta.
narr:Scene rdfs:subClassOf [
  a owl:Restriction ;
  owl:onProperty narr:producesKnowledgeDelta ;
  owl:minCardinality "1"^^xsd:nonNegativeInteger
] .
```

9. Devices

```turtle
narr:FramingDevice a owl:Class ; rdfs:subClassOf go:Thing .
narr:EpistolaryDevice a owl:Class ; rdfs:subClassOf narr:FramingDevice .
narr:Voiceover a owl:Class ; rdfs:subClassOf narr:FramingDevice .
narr:Flashback a owl:Class ; rdfs:subClassOf narr:FramingDevice .
narr:FlashForward a owl:Class ; rdfs:subClassOf narr:FramingDevice .
narr:MacGuffin a owl:Class ; rdfs:subClassOf go:Object .
narr:Motif a owl:Class ; rdfs:subClassOf go:Thing .
narr:Symbol a owl:Class ; rdfs:subClassOf go:Thing .

narr:usesDevice a owl:ObjectProperty ;
  rdfs:domain narr:Scene ; rdfs:range narr:FramingDevice .
```

10. Reasoning Rules

```turtle
# A scene whose beat is a Climax must be the climax scene of its sequence.
[ a swrl:Imp ;
  swrl:body ( [ swrl:argument1 ?s ; swrl:classPredicate narr:Scene ]
              [ swrl:argument1 ?s ; swrl:argument2 ?b ; swrl:propertyPredicate narr:hasBeat ]
              [ swrl:argument1 ?b ; swrl:classPredicate narr:Climax ] ) ;
  swrl:head ( [ swrl:argument1 ?s ; swrl:classPredicate narr:ClimaxScene ] )
] .

# If a scene has a Climax beat and no Crisis beat, raise inconsistency.
narr:ClimaxScene rdfs:subClassOf [
  a owl:Restriction ;
  owl:onProperty narr:hasBeat ;
  owl:someValuesFrom narr:Crisis
] .
```

11. Loading

```bash
genesis reason load --ontology gss-402 --reasoner hermit
genesis reason infer --ontology gss-402
```

12. Relationship to Other Schemas

- Extends GSS-401 (Genesis Core OWL Ontology).
- Source of truth: GO-101.
- Validated by GSS-205 (Ontology SHACL Constraints).
- Consumed by GSS-103 (Scene Specification YAML Schema).

13. Revision History

- 1.0.0 — Initial draft. Mirrors GO-101 v1.0.0.