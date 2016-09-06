#
# Provides a single class, OWLOntologyBuilder, that implements methods for
# parsing descriptions of ontology classes (e.g., from CSV files) and
# converting them into classes in an OWL ontology.
#

# Python imports.
import re
import urlparse
import os
from labelmap import LabelMap

# Java imports.
from java.io import File, FileOutputStream
from org.semanticweb.owlapi.apibinding import OWLManager
from org.semanticweb.owlapi.model import IRI, AddAxiom, OWLOntologyID
from org.semanticweb.owlapi.model import SetOntologyID
from org.obolibrary.macro import ManchesterSyntaxTool
from org.semanticweb.owlapi.manchestersyntax.renderer import ParserException
from org.semanticweb.owlapi.formats import RDFXMLDocumentFormat
from com.google.common.base import Optional


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

    def __init__(self, base_ont_path):
        # Load the base ontology.
        self.ontman = OWLManager.createOWLOntologyManager()
        ontfile = File(base_ont_path)
        self.ontology = self.ontman.loadOntologyFromOntologyDocument(ontfile)

        self.labelmap = LabelMap(self.ontology)

        # Create an OWL data factory and Manchester Syntax parser.
        self.df = OWLManager.getOWLDataFactory()
        self.mparser = ManchesterSyntaxTool(self.ontology)

    def getOntology(self):
        """
        Returns the ontology contained by this OWLOntologyBuilder.
        """
        return self.ontology

    def addClass(self, classdesc, expanddef=True):
        """
        Adds a new class to the ontology, based on a class description provided
        as the dictionary classdesc (i.e., the single explicit argument).  If
        expanddef is True, then term labels in the text definition for the new
        class will be expanded to include the terms' OBO IDs.
        """
        # Create the new class.
        classIRI = IRI.create(
                self.OBO_BASE_IRI + classdesc['ID'].replace(':', '_')
        )
        newclass = self.df.getOWLClass(classIRI)
        declaxiom = self.df.getOWLDeclarationAxiom(newclass)
        self.ontman.applyChange(AddAxiom(self.ontology, declaxiom))
        
        # Add the annotations.
        annotations = self._getAnnotationsFromDesc(classdesc, expanddef)
        for annotation in annotations:
            annotaxiom = self.df.getOWLAnnotationAssertionAxiom(classIRI, annotation)
            self.ontman.applyChange(AddAxiom(self.ontology, annotaxiom))
            # If this is a label annotation, update the label lookup dictionary.
            if annotation.getProperty().isLabel():
                self.labelmap.add(annotation.getValue().getLiteral(), classIRI)
        
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
        self.ontman.applyChange(AddAxiom(self.ontology, newaxiom))
    
        # Add the formal definition (specified as a class expression in
        # Manchester Syntax), if we have one.
        formaldef = classdesc['Formal definition'].strip()
        if formaldef != '':
            try:
                cexp = self.mparser.parseManchesterExpression(formaldef)
            except ParserException as err:
                raise RuntimeError('Error parsing "' + err.getCurrentToken()
                        + '" at line ' + str(err.getLineNumber()) + ', column '
                        + str(err.getColumnNumber())
                        + ' of the formal term definition (Manchester Syntax expected).')
            ecaxiom = self.df.getOWLEquivalentClassesAxiom(cexp, newclass)
            self.ontman.applyChange(AddAxiom(self.ontology, ecaxiom))

    def setOntologyID(self, iri_str):
        """
        Sets the ID for the ontology (i.e., the value of the "rdf:about"
        attribute).  The argument iri_str should be an IRI string.
        """
        ont_iri = IRI.create(iri_str)
        newoid = OWLOntologyID(Optional.fromNullable(ont_iri), Optional.absent())
        self.ontman.applyChange(SetOntologyID(self.ontology, newoid))

    def saveOntology(self, filepath):
        """
        Saves the ontology to a file.
        """
        oformat = RDFXMLDocumentFormat()
        foutputstream = FileOutputStream(File(filepath))
        self.ontman.saveOntology(self.ontology, oformat, foutputstream)
        foutputstream.close()

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
            try:
                labelIRI = self.labelmap.lookupIRI(label)
            except KeyError as err:
                raise RuntimeError('The parent class label, "' + label + '", could not be matched to a term IRI.')
    
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
    
    def _getAnnotationsFromDesc(self, classdesc, expanddef):
        """
        Processes annotation information in a class description dictionary.
        Currently, only label and definition annotations are supported.  The
        results are returned as a list of OWLAnnotation objects.  If expanddef
        is True, term labels in the text definition for the new class will be
        expanded to include the terms' OBO IDs.
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
            if expanddef:
                textdef = self._expandDefinition(textdef)

            defannot = self.df.getOWLAnnotation(
                self.df.getOWLAnnotationProperty(self.DEFINITION_IRI),
                self.df.getOWLLiteral(textdef)
            )
            annotations.append(defannot)
    
        return annotations
    
    def _termIRIToOboID(self, termIRI):
        """
        Converts an IRI for an ontology term into an OB ID; that is, a string
        of the form "PO:0000003".
        """
        termIRIstr = termIRI.toString()
        IRIpath = urlparse.urlsplit(termIRIstr).path
        rawID = os.path.split(IRIpath)[1]

        return rawID.replace('_', ':')
    
    def _expandDefinition(self, deftext):
        """
        Modifies a text definition for an ontology term by adding OBO IDs for
        all term labels in braces ('{' and '}') in the definition.  For
        example, if the definition contains the text "A {whole plant} that...",
        it will be converted to "A whole plant (PO:0000003) that...".
        """
        labelre = re.compile(r'(\{[A-Za-z _]+\})')
        defparts = labelre.split(deftext)

        newdef = ''
        for defpart in defparts:
            if labelre.match(defpart) != None:
                label = defpart.strip("{}")
                try:
                    labelIRI = self.labelmap.lookupIRI(label)
                except KeyError as err:
                    raise RuntimeError('The term label "' + label + '" in the text definition could not be matched to a term IRI.')

                labelID = self._termIRIToOboID(labelIRI)
                newdef += label + ' (' + labelID + ')'
            else:
                newdef += defpart

        if len(defparts) == 0:
            newdef = deftext

        return newdef

