"""
Python interface/API for GQ GMC Geiger Counter.

github: https://github.com/Wikilicious/pygmc
pypi: https://pypi.org/project/pygmc/
readthedocs: https://pygmc.readthedocs.io/
Thomaz - 2023
"""

__version__ = "0.14.0"
__author__ = "Thomaz"
__license__ = "MIT"


import logging

from pygmc.connection import Connection, Discovery
from pygmc.connection.udev_rule_check import UDevRuleCheck
from pygmc.devices import (
    GMC300,
    GMC300S,
    GMC320,
    GMC500,
    GMC600,
    GMC800,
    GMCSE,
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
    timeout=5,
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
    timeout: int
        Time limit for pyserial to raise timeout.

    Raises
    ------
    ConnectionError
        Unable to connect to device.
    """
    # Difficult choice... Discovery is temporary... and is nearly always instant or
    # requires user action to dis/re-connect USB. (i.e. nothing pygmc can do)
    # So why make a long timeout? Fail fast but override Discovery timeout or fail slow
    # and use user provided timeout?
    discover = Discovery(port=port, baudrate=baudrate, timeout=timeout)
    discovered_devices = discover.get_all_devices()

    if len(discovered_devices) == 0:
        # Give user direction in case of brltty udev rule blocking GMC USB device
        brltty_udev_rule_check = UDevRuleCheck()
        # line below logs & prints info for user to resolve USB connection issue
        brltty_udev_rule_check.get_offending_brltty_rules()
        raise ConnectionError("No GMC devices found.")

    device_details = discovered_devices[0]

    logger.debug(f"Selecting: {device_details}")

    device_class = _auto_get_device_class(device_details)

    gc = device_class(
        port=device_details.port, baudrate=device_details.baudrate, timeout=timeout
    )

    return gc
