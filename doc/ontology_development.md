# Ontology development

## Overview

PPO classes are defined in a set of CSV files in the directory `src/`, with names that match `src/*definitions.csv`.  Each file contains a table of PPO classes, where each row in the table contains the information needed to define a single PPO class.  These CSV files are, effectively, the "source code" that is used to compile the complete PPO.  The file `src/ppo-base.owl` contains the "base" PPO ontology, which is simply an empty ontology except for all imports from external ontologies.  The Jython program `bin/csv_to_owl.py` is used to compile the PPO by adding the PPO classes defined in the source CSV files to the empty ontology in `src/ppo-base.owl`.  This is most easily done by invoking `make` with the build target "ontology", which is also the default build target.


## The format of the source CSV files

Each source CSV file must contain a table with 6 columns: "ID", "Label", "Parent class", "Text definition", "Formal definition", and "Ignore".  The source tables can also contain additional columns; they will simply be ignored when compiling the PPO.  Here is a short example of a valid source table.

ID | Label | Parent class | Text definition | Formal definition | Ignore
-- | ----- | ------------ | --------------- | ----------------- | ------
PPO:0000000 | plant phenological stage | 'spatiotemporal region' (BFO:0000011) | A {spatiotemporal region} that encompasses some part of the life of a plant part, a {whole plant}, or a population of whole plants and is part of a {plant growth cycle}. |
PPO:0000001 | whole plant phenological stage | 'plant phenological stage' (PPO:0000000) | A {plant phenological stage} that has as participant exactly one {whole plant}. | 'plant phenological stage' THAT 'has participant' EXACTLY 1 'whole plant' |
PPO:? | experimental class | A PPO class that is in development. | | Y

Below, each column in the table is documented in detail; "required" indicates that for a given row, a value for this column must be provided, while "optional" indicates that the table cell may be empty.

### ID

The OBO ID for the PPO term (**required**).

### Label

A string value for the `rdfs:label` property (**required**).

### Parent class

The parent class of the PPO term (**required**).  This can be specified as either a class label, an OBO ID, or both.  Class labels should be contained in single quotes.  If both a label and an ID are provided, they should be in the format `'class label' (OBO_ID)`.

### Text definition

A string value for the IAO "definition" property (IAO:0000115) (**optional**).  During compilation, class labels in definition strings can be automatically expanded so that the OBO ID for the term is included in the definition.  To enable this, place the class label(s) inside braces (`{` and `}`).  For example, if a definition contains the text "A {whole plant} that...", it will be converted to "A whole plant (PO:0000003) that...".

### Formal definition

A logical definition for the PPO class, written using Manchester Syntax (**optional**).  The anonymous class defined by the Manchester Syntax definition will be linked to the new PPO class by an equivalency axiom.

### Ignore

Whether to include the row in the compiled PPO (**optional**).  If the value of this column is "Y" (or "Yes", "y", "yes", etc.), then the row will be ignored during compilation.  If the column contains any other values or is empty, the row will be included in the compiled ontology.


## Compiling the PPO

To compile the PPO, you can run `csv_to_owl.py` directly, but it is easiest to just run `make`.  If you want to use `csv_to_owl.py`, run

```
$ bin/csv_to_owl.py -h
```

to see documentation for the program's command-line interface.

To use `make`, see the detailed instructions for [building_the_ppo.md](building the PPO).

