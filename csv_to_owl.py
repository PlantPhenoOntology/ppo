#!/usr/bin/env jython

import csv
import sys, glob

# The easiest way to get the java libraries on which the OWL API depends is to
# extract them from the OWL API distribution jar file.  Unzip the jar file,
# then merge everything in the "lib" directory of the jar file into the
# "javalib" directory of the PPO source tree.  Finally, make sure that the OWL
# API main jar file is also in the "javalib" folder.

# Get the paths to all of the java libraries needed by the OWL API and add them
# to the classpath.
libpaths = glob.glob('javalib/*.jar')
for libpath in libpaths:
    sys.path.append(libpath)

from java.io import File
from org.semanticweb.owlapi.apibinding import OWLManager
from org.semanticweb.owlapi.model import OWLOntologyManager, AxiomType
from org.semanticweb.owlapi.model import OWLLiteral, IRI


ontman = OWLManager.createOWLOntologyManager()
ontfile = File('src/ppo-base.owl')
ppobase = ontman.loadOntologyFromOntologyDocument(ontfile)

# Create a dictionary that maps term labels to their IRIs.
labelmap = {}
for annotation_axiom in ppobase.getAxioms(AxiomType.ANNOTATION_ASSERTION, True):
    avalue = annotation_axiom.getValue()
    aproperty = annotation_axiom.getProperty()
    asubject = annotation_axiom.getSubject()
    if aproperty.isLabel():
        if isinstance(avalue, OWLLiteral) and isinstance(asubject, IRI):
            literalval = avalue.getLiteral()
            if literalval not in labelmap:
                labelmap[literalval] = asubject
            else:
                if not(labelmap[literalval].equals(asubject)):
                    raise Exception('The label "' + literalval + '" is used for more than one IRI in the source ontology.')

print labelmap


exit()

with open('class_definitions/stage_definitions.csv') as fin:
    reader = csv.DictReader(fin)
    for line in reader:
        print line

