#
# Provides a single class, LabelMap, that implements methods for mapping term
# labels to term IRIs in a given ontology.
#

# Java imports.
from org.semanticweb.owlapi.model import AxiomType
from org.semanticweb.owlapi.model import OWLLiteral, IRI


class LabelMap:
    """
    Maintains a lookup table for an ontology that maps term labels to their
    associated term IRIs.
    """
    def __init__(self, ontology):
        self.lmap = self._makeMap(ontology)

    def lookupIRI(self, label):
        return self.lmap[label]

    def add(self, label, termIRI):
        if label not in self.lmap:
            self.lmap[label] = termIRI
        else:
            if not(self.lmap[label].equals(termIRI)):
                raise RuntimeError(
                    'The label "' + label +
                    '" is used for more than one IRI in the ontology.'
                )

    def _makeMap(self, ontology):
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

