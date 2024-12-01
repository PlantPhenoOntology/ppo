---
layout: ontology_detail
id: ppo
title: Plant Phenology Ontology
jobs:
  - id: https://travis-ci.org/PlantPhenoOntology/ppo-odk
    type: travis-ci
build:
  checkout: git clone https://github.com/PlantPhenoOntology/ppo-odk.git
  system: git
  path: "."
contact:
  email: 
  label: 
  github: 
description: Plant Phenology Ontology is an ontology...
domain: stuff
homepage: https://github.com/PlantPhenoOntology/ppo-odk
products:
  - id: ppo.owl
    name: "Plant Phenology Ontology main release in OWL format"
  - id: ppo.obo
    name: "Plant Phenology Ontology additional release in OBO format"
  - id: ppo.json
    name: "Plant Phenology Ontology additional release in OBOJSon format"
  - id: ppo/ppo-base.owl
    name: "Plant Phenology Ontology main release in OWL format"
  - id: ppo/ppo-base.obo
    name: "Plant Phenology Ontology additional release in OBO format"
  - id: ppo/ppo-base.json
    name: "Plant Phenology Ontology additional release in OBOJSon format"
dependencies:
- id: bco
- id: bfo
- id: go
- id: iao
- id: obi
- id: pato
- id: po
- id: ro
- id: uberon

tracker: https://github.com/PlantPhenoOntology/ppo-odk/issues
license:
  url: http://creativecommons.org/licenses/by/3.0/
  label: CC-BY
activity_status: active
---

Enter a detailed description of your ontology here. You can use arbitrary markdown and HTML.
You can also embed images too.

