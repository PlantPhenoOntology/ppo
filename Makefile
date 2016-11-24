# Builds the ontology.  This Makefile is intended for out-of-source builds and
# will refuse to run if executed from the root of the source directory.  To
# build the ontoogy, create a separate build directory and run make from within
# this directory.  E.g., if the source directory is the current directory:
#
# $ mkdir build
# $ cd build
# $ make -f ../Makefile
#


#--------
# IMPORTANT: Customize the variables in this section to configure the ontology
# build process.
#--------

# Ontology terms source CSV files (REQUIRED).  These are the names of the terms
# source files that you wish to compile into the final ontology.  Note that
# these need to be specified manually because the order in which they are
# processed often matters.  As long as your project follows the suggested
# directory structure, you only need to provide the names of the files here,
# not full paths.
termsfiles := PPO_trait_properties.csv PPO_trait_classes.csv PPO_supporting_classes.csv PPO_non-reproductive_stages.csv PPO_reproductive_stages.csv

# The IRI (ID) for the compiled ontology (REQUIRED).  The name of the final,
# compiled ontology file will be extracted from this IRI.  If you wish to use a
# custom name for this file, set the value of the variable "ontology_file" in
# the section "Variables for ontology compilation."  This IRI is also used to
# generate the suffix for import ontology module file names; if you wish to
# customize the import module suffix, set the value of "import_mod_suffix" in
# the section "Variables for processing ontology import modules."
ontology_IRI := https://raw.githubusercontent.com/PlantPhenoOntology/PPO/master/ontology/ppo.owl

# The location of the ontobuilder executables (OPTIONAL).  By default, the
# build process assumes that the location of the build executables has been
# added to the search path, but if that is not the case, you must provide their
# location as the value of the variable "ontobuilder_bin".
#ontobuilder_bin := ../../ontobuilder/bin
ontobuilder_bin := 


#--------
# NOTE: Unless you have a non-standard source structure (e.g., you are not
# following the suggested directory structure), you should not need to modify
# anything else in the rest of this Makefile.
#--------


#--------
# Initial configuration for the build process and error checks.
#--------

# Get the location of the root of the ontology source tree.
srcroot = $(realpath $(dir $(lastword $(MAKEFILE_LIST))))

# Check if make is being run from the source directory; if so, quit.
cwd = $(realpath $(shell pwd))
ifeq ($(srcroot),$(cwd))
  $(error Error: The ontology should not be built inside the source tree. \
      Please run make from a separate build directory)
endif

# If the location of the ontobuilder executables was not explicity provided,
# try to get it from the search path.
ifeq ($(ontobuilder_bin),)
  ontobuilder_bin := $(realpath $(dir $(shell which build_import_modules.py)))
endif

# Make sure we got the location of the ontobuilder executables.
ifeq ($(ontobuilder_bin),)
  $(error Error: The ontobuilder executables could not be located.  Please \
      add them to the search path or specify their location by setting the \
      the value of the variable "ontobuilder_bin" in this Makefile)
endif


#--------
# Variables for ontology compilation.
#--------

# The location of the ontology source files.
srcdir := $(srcroot)/src

# Generate full paths to the ontology terms source CSV files.
termsfilepaths := $(addprefix $(srcdir)/terms/,$(termsfiles))

# Get the name of the base ontology file.  This is taken to be the first file
# in the source directory that matches the pattern *-base.owl.  If this does
# not work with your source naming conventions, you will need to customize the
# value of this variable.
base_ontology_file := $(wildcard $(srcdir)/*-base.owl)
#$(info $(base_ontology_file))

# Extract the name of the final ontology file from the ontology IRI.
ontology_file := $(notdir $(ontology_IRI))
#$(info $(ontology_file))


#--------
# Variables for processing ontology import modules.
#--------

# The location of the source files for imports.
importdir := $(srcroot)/src/imports

# The top-level imports source file.  This is the file that lists the
# ontologies from which terms should be imported.
imports_source := $(importdir)/imported_ontologies.csv

# Construct the base IRI to use when generating IRIs for the OWL module files.
ont_IRI_dir := $(dir $(ontology_IRI))
mod_baseIRI := $(patsubst %/master/ontology/,%/master/import_modules/,$(ont_IRI_dir))
#$(info $(mod_baseIRI))

# Generate the suffix to use for naming the import module OWL files generated
# by extracting terms from external ontologies.
import_mod_suffix := _$(basename $(ontology_file))_import_module.owl
#$(info $(import_mod_suffix))


#--------
# Build rule definitions for the import modules.
#--------

.PHONY: imports
imports: $(imports_source)
	$(ontobuilder_bin)/build_import_modules.py --importsfile $(imports_source) \
	    --outputsuffix $(import_mod_suffix) --baseIRI $(mod_baseIRI)


#--------
# Build rule definitions for the ontology.
#--------

.PHONY: ontology
ontology: $(ontology_file)

$(ontology_file): $(base_ontology_file) $(termsfilepaths)
	$(ontobuilder_bin)/build_ontology.py -b $(base_ontology_file) -i $(ontology_IRI) \
	    -o $(ontology_file) $(termsfilepaths)


# Set "ontology" as the default build goal.
.DEFAULT_GOAL := ontology

