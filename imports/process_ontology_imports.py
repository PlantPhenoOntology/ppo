#!/usr/bin/python

import csv
import subprocess
from argparse import ArgumentParser


argp = ArgumentParser(description='Processes a single CSV file of \
terms/entities to extract from a source ontology.  The results are written to \
an output file in OWL format.')
argp.add_argument('-s', '--source', type=str, required=True, help='A source \
ontology file.')
argp.add_argument('-o', '--output', type=str, required=True, help='A prefix \
to use for the results file.')
argp.add_argument('-t', '--termsfile', help='A CSV file containing the terms \
to import.')
args = argp.parse_args()

# Build a list of the IDs of all terms to import.
termIDs = []
with open(args.termsfile) as filein:
    reader = csv.DictReader(filein)

    for row in reader:
        termIDs.append(row['ID'])

# Use OWLTools to generate the import module.
command = ['owltools', args.source, '--extract-module', '-m', 'STAR']
command += termIDs + ['-o', args.output + '.owl']
subprocess.call(command)

