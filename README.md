# PPO

## Building the PPO

### Prerequisites

To build the PPO, you need to first make sure that the following software is installed on your system.

* [OWLTools](https://github.com/owlcollab/owltools)
* Python 2.7
* [GNU make](https://www.gnu.org/software/make/) (other versions of make might not work)


### Running make

The PPO build process is designed to support out-of-source builds.  That is, the Makefile should not be run from within the main source tree; instead, you should first create a separate build directory (which can be located anywhere) and then run make from within the build directory.  For example:

```
$ cd /location/of/PPO/sources
$ mkdir build
$ cd build
$ make -f ../Makefile
```


