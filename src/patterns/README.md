# DOSDP patterns - editors docs

To use DOS-DP patterns, when you set up the repo using ODK, be sure to specify `use_dosdps: true` in https://github.com/PlantPhenoOntology/ppo/blob/odk-conversion/src/ontology/ppo-odk.yaml. 

The pattern files aren't listed anywhere in the project yaml file (unlike the robot template files, which must be listed). Instead, need to include `use_dosdps: true`. When you do so, updating the repo creates the pattern/dosdp directory under src with an example in it. You should remove the example file and add your own yaml files.

YAML files describing each pattern go under https://github.com/PlantPhenoOntology/ppo/tree/odk-conversion/src/patterns/dosdp-patterns.

Corresponding .tsv files with the values for the variables in the pattern go in https://github.com/PlantPhenoOntology/ppo/tree/odk-conversion/src/patterns/data/default

When you use `sh run.sh make patterns dosdp` it will run through each yaml file firt to validate the yaml than to make sure the input (tsv) files are correct, then to build the definitions.owl file and pattern.owl file (still figuring out what pattern.owl is for).
