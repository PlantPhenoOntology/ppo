## Customize Makefile settings for ppo
## 
## If you need to customize your Makefile, make
## changes here rather than in the main Makefile


# ----------------------------------------
# Overwrite import modules
# ----------------------------------------
$(IMPORTDIR)/merged_import.owl: $(MIRRORDIR)/merged.owl $(IMPORTDIR)/merged_terms_combined.txt
	if [ $(IMP) = true ]; then $(ROBOT) merge -i $< \
		extract -T $(IMPORTDIR)/merged_terms_combined.txt --force true --copy-ontology-annotations true --individuals include --method BOT \
		remove $(patsubst %, --term %, $(ANNOTATION_PROPERTIES)) -T $(IMPORTDIR)/merged_terms_combined.txt --select "self parents" --select "self equivalents" --select complement \
		query --update ../sparql/inject-subset-declaration.ru --update ../sparql/inject-synonymtype-declaration.ru --update ../sparql/postprocess-module.ru \
		$(ANNOTATE_CONVERT_FILE); fi


# Original:
# remove $(patsubst %, --term %, $(ANNOTATION_PROPERTIES)) -T $(IMPORTDIR)/merged_terms_combined.txt --select complement --select annotation-properties \
#
# CPONT:
# remove $(patsubst %, --term %, $(OBJECT_PROPERTIES)) $(patsubst %, --term %, $(ANNOTATION_PROPERTIES)) -T $(IMPORTDIR)/merged_terms_combined.txt --select "self descendants" --select "self equivalents" --select complement \