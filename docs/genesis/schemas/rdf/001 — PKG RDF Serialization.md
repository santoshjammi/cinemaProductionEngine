Genesis Schema Specification (GSS)
GSS-301 — PKG RDF Serialization

Document ID: GSS-301
Title: PKG RDF Serialization
Version: 1.0.0
Status: Schema Specification
Authority: Derived from GFS-010, GSS-001, GSS-401

1. Purpose

This document specifies how the Production Knowledge Graph (PKG) is serialized
as RDF triples. RDF is the canonical interchange format for cross-tool,
cross-engine, and cross-language reasoning. JSON (GSS-001) is the human/tool
authoring format; RDF is the semantic interchange format.

2. Design Goals

- Round-trip safe: PKG → RDF → PKG MUST preserve semantics.
- Reasoner-ready: loadable by HermiT, Pellet, ELK, Stardog, rdflib.
- SHACL-validatable against GSS-201.
- Streams: support Turtle, N-Triples, TriG, JSON-LD.

3. Namespaces

```turtle
@prefix pkg:    <urn:genesis:pkg:> .
@prefix node:   <urn:genesis:node:> .
@prefix edge:   <urn:genesis:edge:> .
@prefix go:     <urn:genesis:ontology:> .
@prefix prov:   <urn:genesis:provenance:> .
@prefix rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:   <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:    <http://www.w3.org/2001/XMLSchema#> .
@prefix dct:    <http://purl.org/dc/terms/> .
```

4. Graph Root

```turtle
<urn:genesis:pkg:<pkg-uuid>> a pkg:ProductionKnowledgeGraph ;
  dct:identifier "urn:genesis:pkg:<pkg-uuid>" ;
  pkg:productionId "urn:genesis:prod:<prod-uuid>" ;
  pkg:version "1.0.0" ;
  pkg:createdAt "2026-07-19T00:00:00Z"^^xsd:dateTime ;
  pkg:hasNode <urn:genesis:node:<n1-uuid>> ;
  pkg:hasNode <urn:genesis:node:<n2-uuid>> ;
  pkg:hasEdge <urn:genesis:edge:<e1-uuid>> .
```

5. Node Serialization

Each PKG node becomes an RDF subject with type from the Genesis OWL ontology.

```turtle
<urn:genesis:node:<n1-uuid>> a pkg:Node, go:Character ;
  pkg:nodeId "urn:genesis:node:<n1-uuid>" ;
  pkg:conceptType go:Character ;
  pkg:canonicalName "Arjuna" ;
  pkg:confidence "0.92"^^xsd:double ;
  pkg:knowledgeClass "confirmed" ;
  go:hasGoal <urn:genesis:node:<goal-uuid>> ;
  prov:hasProvenance <urn:genesis:provenance:<p1-uuid>> .
```

6. Edge Serialization

Edges are reified so they can carry confidence, provenance, and metadata.

```turtle
<urn:genesis:edge:<e1-uuid>> a pkg:Edge ;
  pkg:edgeId "urn:genesis:edge:<e1-uuid>" ;
  pkg:source <urn:genesis:node:<arjuna-uuid>> ;
  pkg:target <urn:genesis:node:<krishna-uuid>> ;
  pkg:predicate go:seeks_guidance_from ;
  pkg:confidence "0.88"^^xsd:double ;
  pkg:knowledgeClass "inferred" ;
  prov:hasProvenance <urn:genesis:provenance:<p2-uuid>> .
```

Optionally, a direct triple may also be emitted for reasoner convenience:

```turtle
<urn:genesis:node:<arjuna-uuid>> go:seeks_guidance_from <urn:genesis:node:<krishna-uuid>> .
```

The reified form is canonical; the direct form is a derived view.

7. Provenance Serialization

```turtle
<urn:genesis:provenance:<p1-uuid>> a prov:Provenance ;
  prov:agent <urn:genesis:agent:character-architect> ;
  prov:session <urn:genesis:session:<sess-uuid>> ;
  prov:decisionId <urn:genesis:decision:<dec-uuid>> ;
  prov:evidence "Brief line 14: 'reluctant warrior'" ;
  prov:timestamp "2026-07-19T10:14:00Z"^^xsd:dateTime .
```

8. Subgraph Serialization

```turtle
<urn:genesis:pkg:<pkg-uuid>> pkg:hasSubgraph [
  a pkg:Subgraph ;
  pkg:name "act_two" ;
  pkg:nodeIds ( <n:uuid1> <n:uuid2> ) ;
  pkg:edgeIds ( <e:uuid1> <e:uuid2> )
] .
```

9. JSON-LD Form

```json
{
  "@context": {
    "pkg": "urn:genesis:pkg:",
    "go": "urn:genesis:ontology:",
    "node": "urn:genesis:node:",
    "edge": "urn:genesis:edge:",
    "prov": "urn:genesis:provenance:",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "xsd": "http://www.w3.org/2001/XMLSchema#"
  },
  "@id": "urn:genesis:pkg:<uuid>",
  "@type": "pkg:ProductionKnowledgeGraph",
  "pkg:version": { "@value": "1.0.0", "@type": "xsd:string" },
  "pkg:hasNode": [
    { "@id": "urn:genesis:node:<n1>", "@type": ["pkg:Node", "go:Character"] }
  ]
}
```

10. Serialization Rules

1. Identifiers MUST be URNs of form `urn:genesis:<kind>:<uuid>`.
2. Every node MUST declare `pkg:nodeId`, `rdf:type`, `pkg:conceptType`,
   `pkg:confidence`, `pkg:knowledgeClass`, and a provenance link.
3. Every edge MUST declare `pkg:edgeId`, `pkg:source`, `pkg:target`,
   `pkg:predicate`.
4. The `pkg:conceptType` MUST be a subclass of `go:Thing`.
5. The `pkg:predicate` MUST be a `go:Relationship` or one of its subclasses.
6. All `xsd:dateTime` values MUST be ISO-8601 UTC.

11. Round-Trip Contract

| PKG JSON field | RDF predicate |
|---|---|
| `id` | `dct:identifier` |
| `version` | `pkg:version` |
| `nodes[*].id` | `pkg:nodeId` |
| `nodes[*].type` | `rdf:type` |
| `nodes[*].concept_type` | `pkg:conceptType` |
| `nodes[*].confidence` | `pkg:confidence` |
| `nodes[*].knowledge_class` | `pkg:knowledgeClass` |
| `edges[*].id` | `pkg:edgeId` |
| `edges[*].source` | `pkg:source` |
| `edges[*].target` | `pkg:target` |
| `edges[*].predicate` | `pkg:predicate` |

12. Tooling

```bash
genesis serialize pkg --pkg <pkg-id> --format turtle
genesis serialize pkg --pkg <pkg-id> --format json-ld
genesis serialize pkg --pkg <pkg-id> --format n-triples
genesis import pkg --input pkg.ttl --format turtle
```

13. Validation

After serialization, run GSS-201 (PKG SHACL Constraints) to validate the graph
before sealing the Production Knowledge Package.

14. Relationship to Other Schemas

- Consumes GSS-401 (Genesis Core OWL Ontology) and GSS-402 (Narrative OWL
  Ontology) for `rdf:type` and `pkg:predicate` values.
- Validated by GSS-201 (PKG SHACL Constraints).
- Imported/exported by GSPEC-COMP-001 (Ontology Compiler).

15. Revision History

- 1.0.0 — Initial draft. Derived from GSS-001 v1.0.0.