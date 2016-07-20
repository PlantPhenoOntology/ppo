# Methods for importing terms from a source ontology

These are notes from an investigation of different approaches to extracting sets of terms from a source ontology so that they can be imported to a target ontology (PPO, in this case).  OntoFox's implementation of the MIREOT method appears to be widely used, but has significant limitations.  Most seriously: 1) OntoFox does not always seem to preserve annotations (see results below); 2) OntoFox seems to not always preserve the hierarchy of the target class(es) (again, see results below); and 3) OntoFox is not easily scriptable, which makes automated builds impractical.  Here, I provide usage notes for two alternatives, ROBOT (https://github.com/ontodev/robot) and OWLTools (https://github.com/owlcollab/owltools), and compare their output to that of OntoFox.

* [Installation notes](#installation_notes)
* [Using ROBOT to generate extracts of source ontologies](#using-robot-to-generate-extracts-of-source-ontologies)
* [Using OWLTools to generate extracts of source ontologies](#using-owltools-to-generate-extracts-of-source-ontologies)
* [Using ROBOT or OWLTools to duplicate the output of OntoFox](#using-robot-or-owltools-to-duplicate-the-output-of-ontofox)
* [Conclusions](#conclusions)


## Installation notes

If you use a symlink to add the ROBOT launch script to the search path (as is common in \*nix), the launch script will no longer work.  To fix this, substitute the following lines for line 9 in the launch script.

```bash
# A modified command to get the script path that correctly follows links.
# In my (BJS) testing, it works just fine regardless of whether symlinks are
# involved, so it is a complete replacement for the original line.  I have only
# tested this on Linux.
DIR=$(cd $(dirname $(readlink -f $0)) && pwd)
```

You are likely to encounter the same problem when installing OWLTools, in which case the same technique can be used to fix the OWLTools launch script.


## Using ROBOT to generate extracts of source ontologies

First, note that even though the ROBOT command-line interface includes an option to specify a source ontology by its IRI, as of version 0.0.1+00464da, this does not work (at least not in my testing).  This means that source ontologies must first be downloaded to a local file.  The examples in this document all use the plant ontology (PO,  http://purl.obolibrary.org/obo/po.owl).

The key ROBOT command for importing terms from source ontologies is `extract`, but very little user documentation is currently available for `extract`.  In the following, I provide a detailed summary of what `extract` does and how to use it.  While writing this, I frequently referenced the ROBOT source code to figure out exactly what was going on, so I believe this should be fairly accurate.

The `extract` command supports four extraction methods, which ROBOT calls "STAR", "TOP", "BOT", and "MIREOT".  The extraction method is specified via the command-line option `--method`.  If no method is specified, MIREOT is used by default.


### Syntactic locality methods

The extract methods STAR, TOP, and BOT each require a minimum of one term from the source ontology.  The term(s) to extract can be provided directly at the command line via the command-line option `--term` (`-t`), or by using `--term-file` (`-T`) and an input text file containing IRIs for the terms to extract, one per row.

The following example extracts the "flower" class (PO_0009046) from the PO.

```
$ robot extract --method STAR --input po.owl --term http://purl.obolibrary.org/obo/PO_000904 --output test.owl
```

To specify multiple terms, repeat `--term` as many times as needed.

~~However, the `--terms` option does not work in the current version of Robot.  Instead, a term file must be provided:~~

Alternatively, a file containing the term(s) to extract can be provided.

```
$ robot extract --method STAR --input po.owl --term-file terms.txt --output test.owl
```

ROBOT's `STAR` method is built on top of the STAR syntactic locality module extraction method, as implemented by the SyntacticLocalityModuleExtractor component of the OWL API.  The STAR method was described by Sattler et al. (http://ceur-ws.org/Vol-477/paper_33.pdf for the published version; http://www.dcs.bbk.ac.uk/~michael/insepDL.pdf for an extended version).


### MIREOT

The extract method `MIREOT` requires either: a) a minimum of *two* terms from the source ontology, provided via the command-line options `--upper-term` (`-u`) and `--lower-term` (`-l`); or b) a single term provided with the `--branch-from-term` (`-b`) option.  The MIREOT method will crash with an uninformative error message if only `--terms` (`-t`) is used.  This is not explained in the ROBOT documentation, but a look at the source code confirms that this is how it works.

The following example extracts the PO class hierarchy from "collective plant organ structure" (PO_0025007) to "flower".

```
$ robot extract --method MIREOT --input po.owl --upper-term http://purl.obolibrary.org/obo/PO_0025007 --lower-term http://purl.obolibrary.org/obo/PO_0009046 --output test.owl
```

This can be made more concise by using the `--prefix` (`-p`) option.

```
$ robot --prefix "obo: http://purl.obolibrary.org/obo/" extract --method MIREOT --input po.owl --upper-term obo:PO_0025007 --lower-term obo:PO_0009046 --output test.owl
```

To get the complete "branch" of the PO that begins with "shoot system", use this command.

```
$ robot --prefix "obo: http://purl.obolibrary.org/obo/" extract --method MIREOT --input po.owl --branch-from-term obo:PO_0009006 --output test.owl
```

To get a single class, set `--upper-term` and `--lower-term` to the same IRI (in this case, "flower").

```
$ robot --prefix "obo: http://purl.obolibrary.org/obo/" extract --method MIREOT --input po.owl --upper-term obo:PO_0009046 --lower-term obo:PO_0009046 --output test.owl
```


## Using OWLTools to generate extracts of source ontologies

OWLTools provides another way to extract subsets of ontologies.  OWLTools, like ROBOT, implements module extraction on top of SyntacticLocalityModuleExtractor.  Consequently, the results of ROBOT's STAR extraction method are easily duplicated with OWLTools.  For example, this OWLTools command:

```
$ owltools po.owl --extract-module -m STAR http://purl.obolibrary.org/obo/PO_0009046 -o output.owl
```

produces the same module as this ROBOT command:

```
$ robot extract --method STAR --input po.owl --term-file terms.txt --output test.owl
```

OWLTools is more flexible than ROBOT, though.  For one thing, you can specify terms using only their ID or their label:

```
$ owltools po.owl --extract-module -m STAR PO:0009046 -o output.owl
```
```
$ owltools po.owl --extract-module -m STAR flower -o output.owl
```

You can use a remote IRI for the source ontology:

```
$ owltools http://purl.obolibrary.org/obo/po.owl --extract-module -m STAR flower -o output.owl
```

It is also easy to specify a class (or property), then add all of its subclasses (or subproperties) to the seed set (i.e., the signature):

```
$ owltools po.owl --extract-module -d -m STAR flower -o output.owl
```


## Using ROBOT or OWLTools to duplicate the output of OntoFox

Here, I examine the results of various OntoFox extractions and discuss how to duplicate or approximate those results using ROBOT or OWLTools.  Throughout this section, I use ROBOT, but as discussed above, the use of ROBOT could easily be replaced with OWLTools in many cases.


### Methods for comparing ontology extracts

To compare the output of ROBOT commands with the output from OntoFox, I used ecco (https://github.com/rsgoncalves/ecco) and ROBOT to "diff" the generated ontology extracts.  Unfortunately, ecco has very little user documentation.  To use ecco, the sources need to be downloaded and compiled, which requires a Java 1.8 SDK and Maven.  Running `ecco.sh` will automatically launch the build process.  A typical ecco run looks like this:

```
$ ./ecco.sh -ont1 /path/to/extract1.owl -ont2 /path/to/extract2.owl -t
```

The `-t` option tells ecco to generate HTML output.  With the current version of ecco, however, the HTML output seems to be incorrect.  In that case eccoLog.csv provides the most useful summary of the results.

ROBOT's diff command looks like this:

```
robot diff --left extract1.owl --right extract2.owl
```

Note that ecco only seems to compare classes, not annotations.


### Extracting a single class.

The extract generated by this OntoFox input file:

```
[URI of the OWL(RDF/XML) output file]


[Source ontology]
PO

[Low level source term URIs]
http://purl.obolibrary.org/obo/PO_0009046 #flower

[Top level source term URIs and target direct superclass URIs]


[Source term retrieval setting]
includeNoIntermediates

[Source annotation URIs]
includeAllAnnotationProperties

[Source annotation URIs to be excluded]
```

is essentially identical to the extract produced by this ROBOT command:

```
$ robot --prefix "obo: http://purl.obolibrary.org/obo/" extract --method MIREOT --input po.owl --upper-term obo:PO_0009046 --lower-term obo:PO_0009046 --output test.owl
```

The only differences seem to be due to OntoFox losing some of the annotation details (which is not good!).


### Extracting a class hierarchy

The extract generated by this OntoFox input file:

```
[URI of the OWL(RDF/XML) output file]


[Source ontology]
PO

[Low level source term URIs]
http://purl.obolibrary.org/obo/PO_0009046 #flower

[Top level source term URIs and target direct superclass URIs]
http://purl.obolibrary.org/obo/PO_0025007 #collective plant organ structure

[Source term retrieval setting]
includeAllIntermediates

[Source annotation URIs]
includeAllAnnotationProperties

[Source annotation URIs to be excluded]
```

is essentially identical to the extract produced by this ROBOT command:

```
$ robot --prefix "obo: http://purl.obolibrary.org/obo/" extract --method MIREOT --input po.owl --upper-term obo:PO_0025007 --lower-term obo:PO_0009046 --output test.owl
```

Again, the only differences seem to be due to OntoFox losing some of the annotation details.


### Extracting a class + its direct axioms

This OntoFox input file will extract a class and all of its direct axioms.

```
[URI of the OWL(RDF/XML) output file]


[Source ontology]
PO

[Low level source term URIs]
http://purl.obolibrary.org/obo/PO_0009046 #flower

[Top level source term URIs and target direct superclass URIs]


[Source term retrieval setting]
includeAllIntermediates

[Source annotation URIs]
includeAllAxioms

[Source annotation URIs to be excluded]
```

There does not appear to be any way to exactly duplicate this with ROBOT, and I don't know if it's easily done with OWLTools, either.  However, it would be relatively easy to duplicate by using the OWL API directly.


### Extract a class and a recursive set of its axioms

This OntoFox input file is supposed to extract a class and a recursive set of its axioms.

```
[URI of the OWL(RDF/XML) output file]


[Source ontology]
PO

[Low level source term URIs]
http://purl.obolibrary.org/obo/PO_0009046 #flower

[Top level source term URIs and target direct superclass URIs]


[Source term retrieval setting]
includeAllIntermediates

[Source annotation URIs]
includeAllAxiomsRecursively

[Source annotation URIs to be excluded]
```

It seems to make some mistakes, though.  Most importantly, it loses the class hierarchy for the target class.  In this case, that means that "flower" is no longer the direct subclass of anything else.

This ROBOT command comes close to approximating the behavior of OntoFox (The IRI for "flower" must be in terms.txt):

```
$ robot extract --method STAR --input po.owl --term-file terms.txt --output test.owl
```

The results include all of the relationships extracted by OntoFox but also include more.  In particular: 1) The class hierarchy for "flower" remains intact; and 2) ROBOT extracts the "participates_in" and "has_part" relationships of "flower"; OntoFox completely misses these.  Based on this simple test, the results from ROBOT seem superior to those from OntoFox.  I also compared the results of the above methods when extracting the class "shoot system" (PO:0009006), and the results were identical (the result contains only the single, extracted class).


## Conclusions

ROBOT and OWLTools together make a powerful suite of tools for extracting sets of terms from source ontologies.  In many cases, they can completely replace OntoFox, and the results of ROBOT/OWLTools are often superior to those of OntoFox, especially if the STAR extraction method is used.  These results suggest that a good strategy for extracting terms from a target ontology is to identify all terms needed by the target ontology, then use this set of terms as the seed set (i.e., the signature) to generate a syntactic locality module using the STAR method.

