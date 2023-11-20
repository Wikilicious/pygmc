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
