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

class OWLOntologyBuilder:
    """
    Builds an OWL ontology using Python dictionaries that describe new classes
    to add to an existing "base" ontology.  Typically, the new class
    descriptions will correspond with rows in an input CSV file.
    """
    # Define some IRI constants.
    # The base IRI for all new classes.
    OBO_BASE_IRI = 'http://purl.obolibrary.org/obo/'
    # The IRI for the property for definition annotations.
    DEFINITION_IRI = IRI.create(OBO_BASE_IRI + 'IAO_0000115')

    def __init__(self, base_ontology):
        self.base_ontology = base_ontology

        self.labelmap = self.makeLabelMap(base_ontology)
        #print self.labelmap

        # Create an OWL data factory and Manchester Syntax parser.
        self.df = OWLManager.getOWLDataFactory()
        self.mparser = ManchesterSyntaxTool(base_ontology)

    def makeLabelMap(self, ontology):
        """
        Constructs a dictionary for a given ontology that maps class labels
        (i.e., the values of rdfs:label axioms) to their corresponding class
        IRIs.  This function verifies that none of the labels are ambiguous;
        that is, that no label is used for more than one IRI.
        """
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
    
    def addClass(self, classdesc):
        """
        Adds a new class to the ontology, based on a class description provided
        as the dictionary classdesc (i.e., the single explicit argument).
        """
        # Create the new class.
        classIRI = IRI.create(
                self.OBO_BASE_IRI + classdesc['ID'].replace(':', '_')
        )
        newclass = self.df.getOWLClass(classIRI)
        declaxiom = self.df.getOWLDeclarationAxiom(newclass)
        ontman.applyChange(AddAxiom(base_ontology, declaxiom))
        
        # Add the annotations.
        annotations = self._getAnnotationsFromDesc(classdesc)
        for annotation in annotations:
            annotaxiom = self.df.getOWLAnnotationAssertionAxiom(classIRI, annotation)
            ontman.applyChange(AddAxiom(base_ontology, annotaxiom))
            # If this is a label annotation, update the label lookup dictionary.
            if annotation.getProperty().isLabel():
                self.labelmap[annotation.getValue().getLiteral()] = classIRI
        
        # Get the OWLClass object of the parent class, making sure that it is
        # actually defined.
        parentIRI = self._getParentIRIFromDesc(classdesc)
        parentclass = self.df.getOWLClass(parentIRI)
        # The method below of checking for class declaration does not work for
        # classes from imports.  TODO: Find another way to do this.
        #if (base_ontology.getDeclarationAxioms(parentclass).size() == 0):
        #    raise RuntimeError('The parent class for ' + classdesc['ID'] + ' (row '
        #            + str(rowcnt) + ') could not be found.')
        
        # Add the subclass axiom to the ontology.
        newaxiom = self.df.getOWLSubClassOfAxiom(newclass, parentclass)
        ontman.applyChange(AddAxiom(base_ontology, newaxiom))
    
        # Add the formal definition (specified as a class expression in
        # Manchester Syntax), if we have one.
        formaldef = classdesc['Formal definition'].strip()
        if formaldef != '':
            cexp = self.mparser.parseManchesterExpression(formaldef)
            ecaxiom = self.df.getOWLEquivalentClassesAxiom(cexp, newclass)
            ontman.applyChange(AddAxiom(base_ontology, ecaxiom))


    def _getParentIRIFromDesc(self, classdesc):
        """
        Parses a superclass (parent) IRI from a class description dictionary.
        The parent class information should have the key "Parent class".
        Either a class label, ID, or both can be provided.  The general format
        is: "'class label' (CLASS_ID)".  For example:
        "'whole plant' (PO:0000003)".  If both a label and ID are provided,
        this method will verify that they correspond.
        """
        tdata = classdesc['Parent class'].strip()
        if tdata == '':
            raise RuntimeError('No parent class was provided.')
    
        # Check if we have a class label.
        if tdata.startswith("'"):
            if tdata.find("'") == tdata.rfind("'"):
                raise RuntimeError('Missing closing quote in parent class specification: '
                            + tdata + '".')
            label = tdata.split("'")[1]
            labelIRI = self.labelmap[label]
    
            # See if we also have an ID.
            if tdata.find('(') > -1:
                tdID = tdata.split('(')[1]
                if tdID.find(')') > -1:
                    tdID = tdID.rstrip(')')
                    tdIRI = IRI.create(self.OBO_BASE_IRI + tdID.replace(':', '_'))
                else:
                    raise RuntimeError('Missing closing parenthesis in parent class specification: '
                            + tdata + '".')
        else:
            # We only have an ID.
            labelIRI = None
            tdIRI = IRI.create(self.OBO_BASE_IRI + tdata.replace(':', '_'))
    
        if labelIRI != None:
            if tdIRI != None:
                if labelIRI.equals(tdIRI):
                    return labelIRI
                else:
                    raise RuntimeError('Class label does not match ID in parent class specification: '
                            + tdata + '".')
            else:
                return labelIRI
        else:
            return tdIRI
    
    def _getAnnotationsFromDesc(self, classdesc):
        """
        Processes annotation information in a class description dictionary.
        Currently, only label and definition annotations are supported.  The
        results are returned as a list of OWLAnnotation objects.
        """
        annotations = []
    
        # Make sure we have a label and add it to the new class.
        labeltext = classdesc['Label'].strip()
        if labeltext == '':
            raise RuntimeError('No label was provided for ' + classdesc['ID']
                    + '.')
        labelannot = self.df.getOWLAnnotation(
            self.df.getRDFSLabel(), self.df.getOWLLiteral(classdesc['Label'], 'en')
        )
        annotations.append(labelannot)
        
        # Add the text definition to the class, if we have one.
        textdef = classdesc['Text definition'].strip()
        if textdef != '':
            defannot = self.df.getOWLAnnotation(
                self.df.getOWLAnnotationProperty(self.DEFINITION_IRI),
                self.df.getOWLLiteral(textdef)
            )
            annotations.append(defannot)
    
        return annotations


# Load the base ontology.
ontman = OWLManager.createOWLOntologyManager()
ontfile = File(args.base_ontology)
base_ontology = ontman.loadOntologyFromOntologyDocument(ontfile)

ontbuilder = OWLOntologyBuilder(base_ontology)

# Process each source CSV file.
for termsfile in args.termsfiles:
    with open(termsfile) as fin:
        reader = csv.DictReader(fin)
        rowcnt = 1
        for csvrow in reader:
            rowcnt += 1
            if not(csvrow['Ignore'].strip().startswith('Y')):
                try:
                    ontbuilder.addClass(csvrow)
                except RuntimeError as err:
                    print('\nError encountered in class description in row '
                            + str(rowcnt) + ' of "' + termsfile + '":')
                    print err
                    print

ontbuilder.mparser.dispose()

# Write the ontology to the output file.
foutputstream = FileOutputStream(File(args.output))
ontman.saveOntology(base_ontology, foutputstream)
foutputstream.close()

