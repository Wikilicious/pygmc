"""
Python interface/API for GQ GMC Geiger Counter.

github: https://github.com/Wikilicious/pygmc
pypi: https://pypi.org/project/pygmc/
readthedocs: https://pygmc.readthedocs.io/
Thomaz - 2023
"""
__version__ = "0.9.0"
__author__ = "Thomaz"
__license__ = "MIT"


import logging
import time

from pygmc.connection import Connection, Discovery
from pygmc.devices import (
    GMC300,
    GMC300S,
    GMC320,
    GMC500,
    GMC600,
    GMC800,
    GMC300EPlus,
    GMC320Plus,
    GMC320PlusV5,
    GMC500Plus,
    GMC600Plus,
)
from pygmc.devices import (
    auto_get_device_from_discovery_details as _auto_get_device_class,
)
from pygmc.history import HistoryParser

logger = logging.getLogger(__name__)


def connect(
    port=None,
    baudrate=None,
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

    Raises
    ------
    ConnectionError
        Unable to connect to device.
    """
    discover = Discovery(port=port, baudrate=baudrate)
    discovered_devices = discover.get_all_devices()

    if len(discovered_devices) == 0:
        raise ConnectionError("No GMC devices found.")

    device_details = discovered_devices[0]

    logger.debug(f"Selecting: {device_details}")

    device_class = _auto_get_device_class(device_details)

    gc = device_class(port=device_details.port, baudrate=device_details.baudrate)

    return gc
