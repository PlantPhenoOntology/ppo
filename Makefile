# Builds the PPO.  This Makefile is intended for out-of-source builds and will
# refuse to run if executed from the root of the source directory.  To build
# the PPO, create a separate build directory and run make from within this
# directory.  E.g., if the source directory is the current directory:
#
# $ mkdir build
# $ cd build
# $ make -f ../Makefile
#
# Currently, this Makefile only builds the OWL import modules
# for the external source ontologies that the PPO imports.


# Get the location of the root of the PPO source tree.
srcroot = $(realpath $(dir $(lastword $(MAKEFILE_LIST))))

# Check if make is being run from the source directory; if so, quit.
cwd = $(realpath $(shell pwd))
ifeq ($(srcroot),$(cwd))
  $(error Error: The PPO should not be built inside the source tree.  Please \
    run make from a separate build directory)
endif

# The location of build executables.
bindir := $(srcroot)/bin


##
# Variables and macros for processing ontology import modules.
##

# The location of the source files for imports.
importdir := $(srcroot)/src/import_modules_src

# Get a list of IRIs for the source ontologies from which the PPO imports.
# Note the use of "$$" to pass a single '$' to sed.
ont_IRIs := $(shell \
  tail -n +2 $(importdir)/imported_ontologies.csv | sed "s|.*,\(http://.*\)$$|\1|" \
)
#$(info $(ont_IRIs))

# A macro to generate rules for "building" (i.e., downloading) local copies of
# all of the source ontologies that the PPO needs to import.  The macro expects
# a single argument, which should be the IRI of the source ontology.
define import_ont_rule =
$(notdir $(1)):
	wget $(1)
endef

# Generate a list of import module file names, with each module file name
# derived from the IRI of its source ontology.  E.g., if the source IRI is
# http://purl.obolibrary.org/obo/po.owl, the generated import module file name
# will be po_import_module.owl.
module_names = $(addsuffix _ppo_import_module.owl, $(basename $(notdir $(ont_IRIs))))
#$(info $(module_names))


##
# Variables and macros for ontology compilation.
##

# The location of the ontology source files.
srcdir := $(srcroot)/src

# Ontology terms source CSV files.  Note that these need to be specified
# manually because the order in which they are processed matters.
termsfiles := $(addprefix $(srcdir)/,PPO_supporting_class_definitions.csv PPO_stage_definitions.csv)

# The IRI (ID) for the compiled PPO.
ppo_iri := 'https://raw.githubusercontent.com/PlantPhenoOntology/PPO/ontology/ppo.owl'


##
# Build rule definitions for the import modules.
##

.PHONY: imports
imports: $(module_names)

# Generate the rules for getting the source ontologies.
$(foreach IRI,$(ont_IRIs),$(eval $(call import_ont_rule,$(IRI))))
#$(foreach IRI,$(ont_IRIs),$(info $(call import_ont_rule,$(IRI))))

# A pattern rule for building import modules.  For a given import module to be
# built, both a matching CSV terms file *and* a local copy of the matching
# source ontology must be available, which means a rule for downloading the
# source ontology must be defined.
%_ppo_import_module.owl: $(importdir)/%_ppo_terms.csv %.owl
	$(bindir)/import_module_builder.py --source $*.owl --output $@ \
	  --termsfile $(importdir)/$*_ppo_terms.csv


##
# Build rule definitions for the ontology.
##

.PHONY: ontology
ontology: ppo.owl

ppo.owl: $(srcdir)/ppo-base.owl $(termsfiles)
	$(bindir)/csv_to_owl.py -b $(srcdir)/ppo-base.owl -i $(ppo_iri) -o ppo.owl $(termsfiles)


# Set "ontology" as the default build goal.
.DEFAULT_GOAL := ontology

