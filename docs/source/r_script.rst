Write a R Run Script
====================

In this discussion, we will examine the development of a R Run Script (RRS). Firstly, a thorough list of requirements will be outlined. Following this, all available support tools will be introduced.

RRS Requirements
----------------

A RRS must be a callable R script. This RRS is a script that must accepts two arguments: the input file path and the output file path. Please refer to the :doc:`executing_scripts` document for information on the file formats of the output and input files.

Available support
-----------------

ChemDoE is able to provide assistance with the development of a RRS. In order to use the assistance, it is necessary to install the PyPI package of ChemDoE (See :ref:`sec-install`.).

The configuration of an RRS can be facilitated by using a graphical user interface (GUI). Alternatively, a RRS can also be configured/reorganised via the CLI command of the ChemDoE to facilitate this process.

In addition, this script tests whether the process works according to the requirements. It provides the R script with test inputs and outputs

.. code-block:: console

    ChemDoE add_python_script -src "/full/path/to/main.R" -o json -i json

Simple examples
---------------

.. literalinclude:: examples/json_sample.R
   :language: R