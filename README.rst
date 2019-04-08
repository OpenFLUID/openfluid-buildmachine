OpenFLUID BuildMachine
======================

Tool for automatically build, test and package the OpenFLUID modelling platform.

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

