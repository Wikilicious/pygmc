PyGMC CLI
=========


**The preferred method.**

PyGMC has a command-line-interface CLI that becomes available after installed.
Installing pygmc adds an `entry point <https://setuptools.pypa.io/en/latest/userguide/entry_point.html>`_
console script that becomes available as `pygmc` when the python environment is activated.
You can find the script in `<your_venv_path>/bin/pygmc`.



.. code-block:: bash

   pygmc --help

----

**The discouraged method**

If you simply copied the code or git clone (instead of installing pygmc) you should
consider installing it. However, if you absolutely need an alternative method...
you can go in the directory where `pygmc` lives and use the cli with the code below.

.. code-block:: bash

   python -m pygmc.cli --help


.. autoprogram:: pygmc.cli:parser
   :prog: pygmc
