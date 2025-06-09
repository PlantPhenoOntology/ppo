## Customize Makefile settings for ppo
## 
## If you need to customize your Makefile, make
## changes here rather than in the main Makefile


# Create a report of all the phenological traits and their superclasses.
.PHONY: trait-list
trait-list: $(REPORTDIR)/traits.tsv

$(REPORTDIR)/traits.tsv: $(RELEASEDIR)/ppo.owl $(SPARQLDIR)/list-trait-superclasses.sparql
	$(ROBOT) query -i $< --query $(SPARQLDIR)/list-trait-superclasses.sparql $@