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

from java.io import File, FileOutputStream
from org.semanticweb.owlapi.apibinding import OWLManager
from org.semanticweb.owlapi.model import OWLOntologyManager, AxiomType
from org.semanticweb.owlapi.model import OWLLiteral, IRI, AddAxiom


def getParentIRIFromTable(tdata, rowcnt):
    tdata = tdata.strip()
    if tdata == '':
        raise Exception('No parent class was provided in row ' + str(rowcnt) + '.')

    # Check if we have a class label.
    if tdata.startswith("'"):
        if tdata.find("'") == tdata.rfind("'"):
            raise Exception('Missing closing quote in parent class specification in row '
                        + str(rowcnt) + ': "' + tdata + '".')
        label = tdata.split("'")[1]
        labelIRI = labelmap[label]

        # See if we also have an ID.
        if tdata.find('(') > -1:
            tdID = tdata.split('(')[1]
            if tdID.find(')') > -1:
                tdID = tdID.rstrip(')')
                tdIRI = IRI.create(OBO_BASE_IRI + tdID.replace(':', '_'))
            else:
                raise Exception('Missing closing parenthesis in parent class specification in row '
                        + str(rowcnt) + ': "' + tdata + '".')
    else:
        # We only have an ID.
        labelIRI = None
        tdIRI = IRI.create(OBO_BASE_IRI + tdata.replace(':', '_'))

    if labelIRI != None:
        if tdIRI != None:
            if labelIRI.equals(tdIRI):
                return labelIRI
            else:
                raise Exception('Class label does not match ID in parent class specification in row '
                        + str(rowcnt) + ': "' + tdata + '".')
        else:
            return labelIRI
    else:
        return tdIRI


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

#print labelmap

OBO_BASE_IRI = 'http://purl.obolibrary.org/obo/'
DEFINITION_IRI = IRI.create(OBO_BASE_IRI + 'IAO_0000115')
df = OWLManager.getOWLDataFactory()

with open('src/PPO_supporting_class_definitions.csv') as fin:
    reader = csv.DictReader(fin)
    rowcnt = 0
    for line in reader:
        if line['Ignore'].strip().startswith('Y'):
            continue

        rowcnt += 1
        classIRI = IRI.create(OBO_BASE_IRI + line['ID'].replace(':', '_'))
        #print classIRI
        newclass = df.getOWLClass(classIRI)

        # Add the label to the new class (and make sure we have a label).
        labeltext = line['Label'].strip()
        if labeltext == '':
            raise Exception('No label was provided for ' + line['ID']
                    + ' (row ' + str(rowcnt) + ').')
        labelannot = df.getOWLAnnotation(
            df.getRDFSLabel(), df.getOWLLiteral(line['Label'], 'en')
        )
        labelaxiom = df.getOWLAnnotationAssertionAxiom(classIRI, labelannot)
        ontman.applyChange(AddAxiom(ppobase, labelaxiom))

        # Update the label lookup dictionary.
        labelmap[line['Label']] = classIRI

        # Add the text definition to the class, if we have one.
        textdef = line['Text definition'].strip()
        if textdef != '':
            defannot = df.getOWLAnnotation(
                df.getOWLAnnotationProperty(DEFINITION_IRI),
                df.getOWLLiteral(textdef)
            )
            defaxiom = df.getOWLAnnotationAssertionAxiom(classIRI, defannot)
            ontman.applyChange(AddAxiom(ppobase, defaxiom))

        # Get the OWLClass object of the parent class, making sure that it is
        # actually defined.
        parentIRI = getParentIRIFromTable(line['Parent class'], rowcnt)
        parentclass = df.getOWLClass(parentIRI)
        # The method below of checking for class declaration does not work for
        # classes from imports.  TODO: Find another way to do this.
        #if (ppobase.getDeclarationAxioms(parentclass).size() == 0):
        #    raise Exception('The parent class for ' + line['ID'] + ' (row '
        #            + str(rowcnt) + ') could not be found.')

        # Add the new class to the ontology.
        newaxiom = df.getOWLSubClassOfAxiom(newclass, parentclass)
        ontman.applyChange(AddAxiom(ppobase, newaxiom))


# Write the ontology to the output file.
outputfile = 'test_output.owl'

foutputstream = FileOutputStream(File(outputfile))
ontman.saveOntology(ppobase, foutputstream)
foutputstream.close()

