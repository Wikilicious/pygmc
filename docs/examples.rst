Usage Examples
==============

Auto-Connect
------------
.. code-block:: python

    import pygmc

    gc = pygmc.connect()

    ver = gc.get_version()
    print(ver)

    cpm = gc.get_cpm()
    print(cpm)


Under the hood, pygmc searches through all available USB ports (dev devices, com).
For each port it will try to connect with the highest baudrate and check if the
device can communicate. It will attempt every baudrate. It sends a `<GETVER>>`
command and checks if the output is in the list of expected devices. The first
successful device is used.


Connect With Exact Port
-----------------------
.. code-block:: python

    import pygmc

    gc = pygmc.connect(port="/dev/ttyUSB0")

    ver = gc.get_version()
    print(ver)

    cpm = gc.get_cpm()
    print(cpm)

Under the hood, pygmc will connect to that exact port/dev-device/com and attempt to
communicate with different baudrates until it gets a successful response.


Get DataFrame From Device History
---------------------------------
.. code-block:: python

    import pygmc
    import pandas as pd  # not needed to install PYGMC

    gc = pygmc.connect()

    history = gc.get_history_data()

    df = pd.DataFrame(history[1:], columns=history[0])

The device records readings in it's memory. PyGMC can read the raw history data and
parse it into tidy data that you can use for a pandas DataFrame.
Note: `pandas` is not required to install `pygmc` but if you do have pandas, you can
create a DataFrame from history data.