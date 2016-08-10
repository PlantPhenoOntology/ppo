# Creating new releases of the PPO

## Overview

We use "[semantic versioning](http://semver.org/)" for keeping track of PPO release versions.  In brief, we use three-part version names constructed as *major_version*.*minor_version*.*patch_number*.  Each component is an integer starting at 0, where *major_version* is incremented for changes that break backward compatibility, *minor_version* is incremented for changes that preserve backward compatibility while adding new features, and *patch_number* is incremented for changes that are primarily bug fixes.  Version 1.0.0 is reserved for when the PPO is considered feature-complete; all releases prior to this are named 0.x.x.

Git's [tagging feature](https://git-scm.com/book/en/v2/Git-Basics-Tagging) is used to publish PPO releases.  Always use annotated tags, not lightweight tags.


## Making a new release

The steps to create a new release are as follows.

1. Set the `version IRI` for the ontology to match the version name for the new release.  This is most easily done from the "Active Ontology" tab in Protege.  E.g., for the 0.1.0 release, the value of `version IRI` would be `https://raw.githubusercontent.com/PlantPhenoOntology/PPO/master/ontology/ppo.owl/0.1.0`.

2. Commit the updated ontology file to the git repository.

3. Create the release tag.  This can be done from the command line, but it is probably easiest to [do it from GitHub](https://help.github.com/articles/creating-releases/) since GitHub's interface will generate both the git tag and an endpoint for downloading the released version.  To conform with standard git practice, the tag name should begin with "v"; e.g., "v0.1.0".

