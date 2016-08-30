#!/usr/bin/env jython

# Standard Python library imports.
import csv
import sys, os, glob
from argparse import ArgumentParser


# Define and process the command-line arguments.
argp = ArgumentParser(description='Compiles an OWL ontology from a base \
ontology file and one or more CSV term description tables.')
argp.add_argument('-b', '--base_ontology', type=str, required=True, help='An \
OWL ontology file to use as a base for compiling the final ontology.')
argp.add_argument('-o', '--output', type=str, required=True, help='A path to \
use for the compiled ontology file.')
argp.add_argument('termsfiles', type=str, nargs='*', help='One or more CSV \
files that contain tables defining the new ontology terms.')
args = argp.parse_args()


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

# Java imports.
from java.io import File, FileOutputStream
from org.semanticweb.owlapi.apibinding import OWLManager
from org.semanticweb.owlapi.model import OWLOntologyManager, AxiomType
from org.semanticweb.owlapi.model import OWLLiteral, IRI, AddAxiom
from org.obolibrary.macro import ManchesterSyntaxTool


# Verify that the base ontology file exists.
if not(os.path.isfile(args.base_ontology)):
    raise RuntimeError(
        'The source ontology could not be found: ' + args.base_ontology + '.'
    )

# Verify that the terms CSV files exist.
for termsfile in args.termsfiles:
    if not(os.path.isfile(termsfile)):
        raise RuntimeError(
            'The input CSV file could not be found: ' + termsfile + '.'
        )

def makeLabelMap(ontology):
    # Create a dictionary that maps term labels to their IRIs.
    labelmap = {}
    for annotation_axiom in ontology.getAxioms(AxiomType.ANNOTATION_ASSERTION, True):
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
                        raise RuntimeError(
                            'The label "' + literalval +
                            '" is used for more than one IRI in the source ontology.'
                        )

    return labelmap

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


# Load the base ontology.
ontman = OWLManager.createOWLOntologyManager()
ontfile = File(args.base_ontology)
base_ontology = ontman.loadOntologyFromOntologyDocument(ontfile)

labelmap = makeLabelMap(base_ontology)
#print labelmap

OBO_BASE_IRI = 'http://purl.obolibrary.org/obo/'
DEFINITION_IRI = IRI.create(OBO_BASE_IRI + 'IAO_0000115')
df = OWLManager.getOWLDataFactory()

mparser = ManchesterSyntaxTool(base_ontology)

for termsfile in args.termsfiles:
    with open(termsfile) as fin:
        reader = csv.DictReader(fin)
        rowcnt = 0
        for line in reader:
            rowcnt += 1
            if line['Ignore'].strip().startswith('Y'):
                continue
    
            # Create the new class.
            classIRI = IRI.create(OBO_BASE_IRI + line['ID'].replace(':', '_'))
            newclass = df.getOWLClass(classIRI)
            declaxiom = df.getOWLDeclarationAxiom(newclass)
            ontman.applyChange(AddAxiom(base_ontology, declaxiom))
    
            # Make sure we have a label and add it to the new class.
            labeltext = line['Label'].strip()
            if labeltext == '':
                raise Exception('No label was provided for ' + line['ID']
                        + ' (row ' + str(rowcnt) + ').')
            labelannot = df.getOWLAnnotation(
                df.getRDFSLabel(), df.getOWLLiteral(line['Label'], 'en')
            )
            labelaxiom = df.getOWLAnnotationAssertionAxiom(classIRI, labelannot)
            ontman.applyChange(AddAxiom(base_ontology, labelaxiom))
    
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
                ontman.applyChange(AddAxiom(base_ontology, defaxiom))
    
            # Get the OWLClass object of the parent class, making sure that it is
            # actually defined.
            parentIRI = getParentIRIFromTable(line['Parent class'], rowcnt)
            parentclass = df.getOWLClass(parentIRI)
            # The method below of checking for class declaration does not work for
            # classes from imports.  TODO: Find another way to do this.
            #if (base_ontology.getDeclarationAxioms(parentclass).size() == 0):
            #    raise Exception('The parent class for ' + line['ID'] + ' (row '
            #            + str(rowcnt) + ') could not be found.')
    
            # Add the subclass axiom to the ontology.
            newaxiom = df.getOWLSubClassOfAxiom(newclass, parentclass)
            ontman.applyChange(AddAxiom(base_ontology, newaxiom))

            # Add the formal definition (specified as a class expression in
            # Manchester Syntax), if we have one.
            formaldef = line['Formal definition'].strip()
            if formaldef != '':
                cexp = mparser.parseManchesterExpression(formaldef)
                ecaxiom = df.getOWLEquivalentClassesAxiom(cexp, newclass)
                ontman.applyChange(AddAxiom(base_ontology, ecaxiom))

mparser.dispose()

# Write the ontology to the output file.
foutputstream = FileOutputStream(File(args.output))
ontman.saveOntology(base_ontology, foutputstream)
foutputstream.close()

