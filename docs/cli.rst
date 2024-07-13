PyGMC CLI
=========


PyGMC has a command-line-interface CLI and can be used a few ways.
Installing pygmc adds an `entry point <https://setuptools.pypa.io/en/latest/userguide/entry_point.html>`_
console script that becomes available as `pygmc`. **The preferred method.**

.. code-block:: bash

   pygmc --help


If you simply copied the code (instead of installing pygmc) you have to supply module
path or file path. See examples in order below.

.. code-block:: bash

   python -m pygmc.cli --help

`or`

.. code-block:: bash

   python path/to/pygmc/cli.py --help




.. autoprogram:: pygmc.cli:parser
   :prog: pygmc
