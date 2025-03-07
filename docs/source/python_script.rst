Write a Python Run Script
=========================

In this discussion, we will examine the development of a Python Run Script (PRS). Firstly, a thorough list of requirements will be outlined. Following this, all available support tools will be introduced.

PRS Requirements
----------------

A PRS must be a callable script. Ideally, this can is a Python file that has a

.. code-block:: python

    if __name__ == '__main__':
        ...

block or at least executable code if the script is called as Python.

A PRS is a script that must accepts two arguments: the input file path and the output file path. Please refer to the :doc:`executing_scripts` document for information on the file formats of the output and input files.


The development should be completed to the point where it can support Python versions greater than 3.12.

Available support
-----------------

ChemDoE is able to provide assistance with the development of a PRS. In order to use the assistance, it is necessary to install the PyPI package of ChemDoE (See :ref:`sec-install`.).

1. Pytests
++++++++++

Let us assume you have a script **'main.py'**

.. code-block:: python
    :caption: ./project/src/main.py

    import sys

    def read_input(path):
        ...

    def calculate_variations(doe_table):
        ...

    def write_output(variation_table, out_path):
        ...

    if __name__ == '__main__':
        doe_table = read_input(sys.argv[1])
        variation_table = calculate_variations(doe_table)
        write_output(variation_table, sys.argv[2])

then you can use the test assistance if you make a **'test.py'**

.. code-block:: python
    :caption: ./project/src/test.py

    from json import JSONDecodeError
    from ChemDoE.registery import check_doe_script


    @check_doe_script('json', 'json')
    def test_creat_script():
        import main


.. code-block:: none
    :caption: Project tree

    project/
    ├──
    ├── src/
    │   ├── main.py
    │   ├── tests.py
    ├── README.md
    ├── setup.py


2. Register PRS programmatically
++++++++++++++++++++++++++++++++

The configuration of a PRS can be facilitated through the utilisation of a GUI (Graphical User Interface). Alternatively, to facilitate this process, a PRS can also be configured/reorganised programmatically.

.. code-block:: python
    :caption: ./project/src/register.py

    from ChemDoE.registration import register_python_doe_script

    register_python_doe_script('main', 'json', 'json')


This code segment is intended to register a configuration entry in the ChemDoE, provided that the main script returns a correct result.

.. code-block:: none
    :caption: Project tree

    project/
    ├──
    ├── src/
    │   ├── main.py
    │   ├── tests.py
    │   ├── register.py
    ├── README.md
    ├── setup.py


3. Register PRS from console
++++++++++++++++++++++++++++

Alternatively to  the registration of the PRS programmatically it is possible to use the CLI command of the ChemDoE:

.. code-block:: console

    ChemDoE add_python_script -src "/full/path/to/main.py" -i json -o json



Simple examples
---------------

.. literalinclude:: examples/json_sample.py
   :language: python


.. literalinclude:: examples/csv_sample.py
   :language: python