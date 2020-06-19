OpenFLUID BuildMachine
======================

Tool for automatically build, test and package the OpenFLUID modelling platform. 
Also handles building and testing of PyOpenFLUID and ROpenFLUID repositories.

It is written in Python 3.



Installation
============

from PyPI
---------

*TODO*


from sources
------------

Classic installation (main usage)

.. code-block:: shell

    pip3 install .


Installation linked to the current sources (usually for development purposes)

.. code-block:: shell

     pip3 install -e .



Usage
=====

OFBM
----

Build machine automaton for OpenFLUID building, testing and installing

ofbm [-h] [--temp-dir TEMP_DIR] [--build-jobs BUILD_JOBS] [--shell]
            [--openfluid-repos OPENFLUID_REPOS]
            {package,test} ...
            
Options for packaging:
ofbm package [-h] [--run-examples RUN_EXAMPLES]
                    [--ropenfluid-repos ROPENFLUID_REPOS]
                    [--pyopenfluid-repos PYOPENFLUID_REPOS]
                    [--openfluidjs-repos OPENFLUIDJS_REPOS]
RUN_EXAMPLES can be a list of referenced examples in Firespread,MHYDAS_Roujan,Primitive,Manhattan separated by commas, 
                    or * to run every example.
Each ..._REPOS can be a github partial url or "default" to target the OpenFLUID reference repository for each language.
For github repositories, branch can be precised by adding the branch to checkout after the repo url with a "#" inbetween (for example: "OpenFLUID/openfluid#develop")


MBM
---

Wrapper for OFBM on several contexts, following a yaml configuration file

mbm [-h] [--conf-file CONF_FILE] [--out-dir OUT_DIR] [--try-image-build] [--shell]

Caution: OUT_DIR must be an absolute path (but not necessary existing)
If option "try-image-build" is added and a missing image is targetted, the system will create it. 
Shell option is optional and redirects every mbm-level log to the shell instead of log file. 
(Not affecting the "shell" output behaviour of the ofbm)

Precisions about try-image-build: 

- this can only work if the Dockerfile is found
- a check is done to estimate if this build can fit in the available space on given volume, preventing the build when the space is not sufficient. 
- stay vigilant about disk space

MBM-Env
-------

Structured wrapper for MBM

openfluid-mbm [-h] {create,run} [path/to/env]

"create" command generates a standalone folder with scripts and structure for runs
"run" command triggers the multi-buildmachine inside this standalone folder, according its "config.yaml" settings, and create an "exec..." folder for the current run.

Development
===========


Run the following commands from the root of the sources tree.


Check
-----

.. code-block:: shell

   python3 setup.py check


Packaging
---------

.. code-block:: shell

   python3 setup.py sdist bdist



Internals
=========


1) OFBM

The target directory will have the following structure :

TMP_DIR
-------
  [of_source]
  _build/
  Log/
    0_prepare.txt
    [1_fetch.txt]
    2_configure.txt
    3_build.txt
    4_package.txt|4_test.txt
    ...
  report.json
  report.html


Log file structure
------------------

By default, all logs (output and errors) are saved in files corresponding to the step in the Log directory. 
Each message is timestamped and a line "End of command." is added after each command to track the end of each command.


Report structure
----------------

Reports summarize status for every major step. If any substep failed, the global step will also considered as failing.
The report.json is used for interoperability.
It allows the quick processing of the buildmachine run results by an automatic supervisor.
The report.html is more suited for human reading and gives a quick access to log files.


2) Multi-BuildMachine

CONFIGURATION FILE
------------------

Yaml format, required key:
.. code-block:: yaml
     active-setups (list)

Organised with a list of :
- contexts (docker images or local system)
- setups (depending on build types, context and other parameters)

which can be accessed via variables following the YAML syntax: 
  &VAR to set the variable
  *VAR to access the variable content

Each setup have mandatory parameters:
- build-type: value is test or package
- temp-dir: location for build generation and logs output
- contexts: list of local system and/or built docker images

Each parameter used in the ofbm command can also be set (optional) in any setup:
- build-jobs
- openfluid-repos
- pyopenfluid-repos, ...
- run-examples: "*" (Caution, use example name separated by commas or "*" to run all referenced examples)