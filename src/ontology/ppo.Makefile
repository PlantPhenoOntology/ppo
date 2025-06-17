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
		remove $(patsubst %, --term %, $(ANNOTATION_PROPERTIES)) -T $(IMPORTDIR)/merged_terms_combined.txt --select "self ancestors" --select "self equivalents" --select complement \
		query --update ../sparql/inject-subset-declaration.ru --update ../sparql/inject-synonymtype-declaration.ru --update ../sparql/postprocess-module.ru \
		$(ANNOTATE_CONVERT_FILE); fi


# ----------------------------------------
# Custom reports
# ----------------------------------------

# Create a report listing all the phenological traits and their superclasses.
.PHONY: trait-list
trait-list: $(REPORTDIR)/traits.tsv

$(REPORTDIR)/traits.tsv: $(RELEASEDIR)/ppo.owl $(SPARQLDIR)/list-trait-superclasses.sparql
	$(ROBOT) query -i $< --query $(SPARQLDIR)/list-trait-superclasses.sparql $@
