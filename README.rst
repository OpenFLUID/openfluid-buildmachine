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
The report.json is used for wrapping cases, to allow the quick processing of the buildmachine run results by an automatic supervisor.
The report.html is more suited for human reading and gives a quick access to log files.