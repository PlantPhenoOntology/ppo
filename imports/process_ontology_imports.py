#!/usr/bin/python

import csv
import subprocess
import os
from argparse import ArgumentParser


# This is used to define unique values of the ontology ID, the default xmlns
# attribute, and the xml:base attribute for the generated OWL file.  If these
# are not set, Protege does not seem to be able to deal with the imports, at
# least not reliably.
IRI_BASE = "https://raw.githubusercontent.com/PlantPhenoOntology/PPO/master/ontology/import_modules/"

argp = ArgumentParser(description='Processes a single CSV file of \
terms/entities to extract from a source ontology.  The results are written to \
an output file in OWL format.')
argp.add_argument('-s', '--source', type=str, required=True, help='A source \
ontology file.')
argp.add_argument('-o', '--output', type=str, required=True, help='A name to \
use for the results file.')
argp.add_argument('-t', '--termsfile', type=str, required=True, help='A CSV \
file containing the terms to import.')
args = argp.parse_args()

# Verify that the source ontology file exists.
if not(os.path.isfile(args.source)):
    raise RuntimeError('The source ontology could not be found.')

# Define the strings that indicate TRUE in the CSV files.  Note that variants
# of these strings with different casing will also be recognized.
true_strs = ['t', 'true', 'y', 'yes']

# Build two lists of the IDs of all terms to import: one for terms that define
# the full seed set, and one for terms whose subclasses will also be pulled
# into the seed set.
termIDs = []
termIDs_to_expand = []
with open(args.termsfile) as filein:
    reader = csv.DictReader(filein)

    for row in reader:
        if row['seed_subclasses'].strip().lower() in true_strs:
            termIDs_to_expand.append(row['ID'])
        else:
            termIDs.append(row['ID'])

# Use OWLTools to generate temporary import modules for each list of terms, and
# keep a list of the generated temporary import modules.
temp_modules = []

ont_IRI = IRI_BASE + args.output

# Terms for which we don't explicitly add subclasses to the seed set.
if len(termIDs) > 0:
    tmpname = args.output + '-tmp0.owl'
    command = ['owltools', args.source, '--extract-module', '-m', 'STAR']
    command += termIDs + ['--set-ontology-id', ont_IRI, '-o', tmpname]
    subprocess.call(command)
    temp_modules.append(tmpname)

# Terms for which we explicitly add subclasses to the seed set.
if len(termIDs_to_expand) > 0:
    tmpname = args.output + '-tmp1.owl'
    command = ['owltools', args.source, '--extract-module', '-d', '-m', 'STAR']
    command += termIDs_to_expand + ['--set-ontology-id', ont_IRI, '-o', tmpname]
    subprocess.call(command)
    temp_modules.append(tmpname)

# Generate the final import module.
if len(temp_modules) == 1:
    # Only one temporary module was created, so just rename it.
    os.rename(temp_modules[0], args.output)
elif len(temp_modules) > 1:
    # Merge the temporary modules.
    command = ['owltools'] + temp_modules + ['--merge-support-ontologies']
    command += ['--set-ontology-id', ont_IRI, '-o', args.output]
    subprocess.call(command)
else:
    raise RuntimeError('No terms to import were found in the terms file.')

