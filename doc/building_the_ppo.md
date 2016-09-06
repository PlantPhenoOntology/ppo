# Building the PPO

## Prerequisites

To build the PPO, you need to first make sure that the following software is installed on your system.

* [OWLTools](https://github.com/owlcollab/owltools) (currently only required for building the import modules).
* Python 2.7.
* [Jython](http://www.jython.org/).
* [GNU make](https://www.gnu.org/software/make/) (other versions of make might not work).  Note that you need to have a modern release of make; at least version 4.0.  Recent GNU/Linux and Cygwin releases should work out of the box.  If you use OSX, you probably have a very old version of make, in which case you should use homebrew to install an up-to-date make (which will be called gmake).


## Running make

The PPO build process is designed to support out-of-source builds.  That is, the Makefile should not be run from the root of the main source tree; instead, you should first create a separate build directory (which can be located anywhere) and then run make from within the build directory.  For example:

```
$ cd /location/of/PPO/sources
$ mkdir build
$ cd build
$ make -f ../Makefile ontology
```

The Makefile defines two top-level build targets: "imports" and "ontology" (the default).  Build "imports" to generate the external ontology import modules, and build "ontology" to compile the complete PPO.


### Building the import modules

To build the import modules, make the build directory your working directory and then run:

```
$ make -f ../Makefile imports
```

### Compiling the PPO

To compile the PPO, make the build directory your working directory and then run:

```
$ make -f ../Makefile ontology
```

Or, because "ontology" is the default build target, you can just run:

```
$ make -f ../Makefile
```

