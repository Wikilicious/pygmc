"""
Python interface/API for GQ GMC Geiger Counter.

github: https://github.com/Wikilicious/pygmc
pypi: https://pypi.org/project/pygmc/
readthedocs: https://pygmc.readthedocs.io/
Thomaz - 2023
"""
__version__ = "0.7.0"
__author__ = "Thomaz"
__license__ = "MIT"


import logging
import time

from pygmc.connection import Connection
from pygmc.devices import auto_get_device
from pygmc.history import HistoryParser

logger = logging.getLogger(__name__)


def connect(
    port=None,
    baudrate=None,
    vid=None,
    pid=None,
    description=None,
    hardware_id=None,
):
    """
    Connect to device.

    If all parameters are None, _auto_connect() flow is used which attempts to connect
    to all available ports.
    If ANY parameter is given; it's used to refine the search, any matches are
    considered.
    Parameters are used as an OR search.

    Parameters
    ----------
    port : str | None, optional
        Exact port (device dev path / com port) e.g. '/dev/ttyUSB0'
        If port is specified, the following kwargs are ignored: vid, pid, description,
        hardware_id.
    baudrate: int | None
        Device baudrate. Leave None to auto-detect baudrate. Only applicable when port
        is specified.
    vid : str | None, optional
        Device vendor ID as hex, by default None
    pid : str | None, optional
        Device product ID as hex, by default None
    description : str | None, optional
        Device description, by default None
    hardware_id : str | None, optional
        Device hwid, by default None
        e.g. 'USB VID:PID=1A86:7523 LOCATION=2-1'
        Use hex for vid:pid input

    Raises
    ------
    ConnectionError
        Unable to connect to device.
    """
    connection = Connection()
    connection.connect(
        port=port,
        baudrate=baudrate,
        vid=vid,
        pid=pid,
        description=description,
        hardware_id=hardware_id,
    )

    device = auto_get_device(connection)

    # The GMC300S is main reason for sleep/delay...
    time.sleep(0.2)
    ver = device.get_version()
    msg = f"Connected device={ver}"
    print(msg)  # print for newbies w/o logger knowledge
    logger.info(msg)

    return device
