# Importing terms from external source ontologies

## Overview

The files in this directory define which terms the PPO imports from other ontologies.  The procedure for adding terms to import is as follows.

1. Make sure there is a row for the external ontology in `imported_ontologies.csv`.
2. Create a CSV file for the source ontology (if it does not already exist).  The CSV file name must correspond to the name of the ontology file; e.g., `po_ppo_terms.csv` for the Plant Ontology, `pato_ppo_terms.csv` for PATO.
3. Add the terms to import to the CSV file for the source ontology.

When the PPO is built, `process_ontology_imports.py` will read the ontology-specific CSV files and use them, along with OWLTools, to generate syntactic locality import modules for each source ontology, using the STAR method implemented by the OWL API's [SyntacticLocalityModuleExtractor](http://owlapi.sourceforge.net/javadoc/uk/ac/manchester/cs/owlapi/modularity/SyntacticLocalityModuleExtractor.html).


## CSV file formats

### imported_ontologies.csv

This file contains only two columns and should be self-explanatory:

* `name` (The name of the ontology; this can be any string but it should not include any HTTP URLs.)
* `IRI` (The location of the ontology; this must be a functional HTTP URL.)


### Ontology terms CSV files (e.g., po_ppo_terms.csv)

These files should have three columns:

* `label` (The label for the term.)
* `ID` (The OBO ID for the term.)
* `seed_subclasses` (Whether to include subclasses in the seed set.)

The column `seed_subclasses` specifies how to construct the seed set of terms (i.e., the signature) for generating the import module.  If, for a given term, `seed_subclasses` is set to "T" (or "t", "True", "Yes", "y", etc.), then all subclasses of the term will be included in the seed set.  Otherwise, no subclasses will explicitly be included in the seed set (although they could end up in the final import module anyway).

