.. PyGMC documentation master file, created by
   sphinx-quickstart on Sat Nov 18 14:57:14 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


.. meta::
   :google-site-verification: 5IzQYkf392uzYxd2VkHCwupUJF8F_HlGag1_f4wILY0


PyGMC Documentation
===================

PyGMC is a Python API for Geiger–Müller Counters, GMC, Geiger Counters.
It has just one dependency (pyserial) and works on multiple operating
systems: Windows, OSX, Linux. PyGMC aims to be a minimalistic interface -
lowering the installation requirements and allowing the user to build their
own tools on top of a stable package.

Why use PyGMC:
    * Has tests required to deploy (`See Tests <https://github.com/Wikilicious/pygmc/tree/master/tests>`_)
    * Has documentation (You're looking at it)
    * Easily installable via `pip install pygmc` from `PYPI <https://pypi.org/project/pygmc/>`_
    * Follows PEP8 standards & common linting standards
    * Source code on GitHub: https://github.com/Wikilicious/pygmc


Install PyGMC
-------------

Install PyGMC from PYPI: https://pypi.org/project/pygmc/

.. code-block:: bash

   pip install pygmc

Install PyGMC from Conda-Forge: https://anaconda.org/conda-forge/pygmc

.. code-block:: bash

   conda install conda-forge::pygmc

Conda version may lag latest pypi version.


Example Usage
-------------

.. image:: image/pygmc_usage_example_0.9.1.gif
   :width: 800


Auto discover connected GMC, auto identify baudrate, and auto select correct device.

.. code-block:: python

    import pygmc

    gc = pygmc.connect()

    ver = gc.get_version()
    print(ver)

    cpm = gc.get_cpm()
    print(cpm)


Connect to specified GMC device with exact USB port/device/com.

.. code-block:: python

    import pygmc

    gc = pygmc.GMC320('/dev/ttyUSB0')

    cpm = gc.get_cpm()
    print(cpm)


Supported Devices
-----------------

+------------------------------+----------------+------------------+
| Device                       | Brand          | Notes            |
+==============================+================+==================+
| GMC-300S ✔️✔️                | GQ Electronics | A little picky   |
+------------------------------+----------------+------------------+
| GMC-300E+ / GMC-300E Plus    | GQ Electronics |                  |
+------------------------------+----------------+------------------+
| GMC-320+ / GMC-320 Plus ✔️✔️ | GQ Electronics | Works smoothly   |
+------------------------------+----------------+------------------+
| GMC-320S                     | GQ Electronics |                  |
+------------------------------+----------------+------------------+
| GMC-500                      | GQ Electronics |                  |
+------------------------------+----------------+------------------+
| GMC-500+ / GMC-500 Plus ✔️✔️ | GQ Electronics | Works smoothly   |
+------------------------------+----------------+------------------+
| GMC-600                      | GQ Electronics |                  |
+------------------------------+----------------+------------------+
| GMC-600+ / GMC-600 Plus ✔️✔️ | GQ Electronics |                  |
+------------------------------+----------------+------------------+
| GMC-800 ✔️✔️                 | GQ Electronics | *Finally Working |
+------------------------------+----------------+------------------+
| GMC-SE ✔️                    | GQ Electronics | RFC1201          |
+------------------------------+----------------+------------------+


✔️✔️=physically confirmed works

✔️=user confirmed works

*Incorrect documentation caused incorrect implementation with `pygmc<=0.10.0`


.. image:: https://www.gqelectronicsllc.com/comersus/store/catalog/300s%20main.jpg
.. image:: https://www.gqelectronicsllc.com/comersus/store/catalog/GMC-320-Plus_350.png
.. image:: https://www.gqelectronicsllc.com/comersus/store/catalog/GMC-500HV_350.png


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   devices
   connection
   history
   cli
   examples
   knownissues


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. Notes: for table, copy README.md and use
   https://tableconvert.com/markdown-to-restructuredtext to auto-gen table
   select "Force separate lines"
