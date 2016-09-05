#
# This package initialization script does two things:
#
#   1. Adds all required java library jar files to the classpath.
#   2. Adds classes in package modules to the package's top-level scope.
#
# The directory "../../javalib" contains all of the java libraries on which the
# OWL API depends.  The easiest way to get all of these library jar files is to
# extract them from the OWL API distribution jar file.  Unzip the jar file,
# then merge everything in the "lib" directory of the jar file into the
# "javalib" directory of the PPO source tree.  Finally, make sure that the OWL
# API main jar file is also in the "javalib" folder.
#

import os, glob, sys


# Get the paths to all of the java libraries needed by the OWL API and add them
# to the classpath.
scriptdir = os.path.dirname(os.path.realpath(__file__))
jlibdir = os.path.realpath(
        os.path.join(scriptdir, '..', '..', 'javalib', '*.jar')
    )
jlibpaths = glob.glob(jlibdir)
for jlibpath in jlibpaths:
    sys.path.append(jlibpath)

# Add classes of contained modules to the package's top-level scope.
from labelmap import LabelMap
from owlontologybuilder import OWLOntologyBuilder

