
# A list of IRIs for the source ontologies from which the PPO imports.
ont_IRIs = http://purl.obolibrary.org/obo/po.owl

# Generate a list of import module file names, with each module file name
# derived from the IRI of its source ontology.
module_names = $(addsuffix _import_module.owl, $(basename $(notdir $(ont_IRIs))))
#$(info $(module_names))

# A macro to generate rules for "building" (i.e., downloading) local copies of
# all of the source ontologies that the PPO needs to import.  The macro expects
# a single argument, which should be the IRI of the source ontology.
define import_ont_rule =
$(notdir $(1)):
	wget $(1)
endef


.PHONY: all
all: $(module_names)

# Generate the rules for getting the source ontologies.
import_ont_rules = $(foreach IRI,$(ont_IRIs),$(call import_ont_rule,$(IRI)))
#$(info $(import_ont_rules))
$(eval $(import_ont_rules))

# A pattern rule for generating import modules.  For a given import module to
# be built, both a matching CSV terms file *and* a local copy of the matching
# source ontology must be available, which means a rule for downloading the
# source ontology must be defined.
%_import_module.owl: %_terms.csv %.owl
	./process_ontology_imports.py --source $(*).owl --output $@ --termsfile $(*)_terms.csv

