import logging
import re

from .device import BaseDevice
from .device_rfc1201 import DeviceRFC1201
from .device_rfc1801 import DeviceRFC1801
from .gmc300 import GMC300, GMC300S, GMC300EPlus
from .gmc320 import GMC320, GMC320Plus, GMC320PlusV5
from .gmc500 import GMC500, GMC500Plus
from .gmc600 import GMC600, GMC600Plus
from .gmc800 import GMC800

logger = logging.getLogger("pygmc.device")

_device_map = {
    "GMC-280": DeviceRFC1201,
    "GMC-300": DeviceRFC1201,
    "GMC-320": DeviceRFC1201,
    "GMC-500": DeviceRFC1801,
    "GMC-600": DeviceRFC1801,
    # seemed like bigger number would use newer rfc spec until GMC-800
    # listed as RFC1201 in https://www.gqelectronicsllc.com/GMC-800UserGuide.pdf
    "GMC-800": DeviceRFC1201,
}


# Match regex to device. Order matters. First match is used.
_regex_device_match_list = [
    # GMC300's
    {
        "match": r"GMC-300S",
        "device": GMC300S,
        "example": "GMC-300SRe 1.14",
    },
    {
        # Not sure...
        "match": r"GMC-300E\+",
        "device": GMC300EPlus,
        # Open Issue on PyGMC github... make a PR... Provide an example
        "example": "",
    },
    {
        # Does this model exist?
        "match": r"GMC-300",
        "device": GMC300,
        # Open Issue on PyGMC github... make a PR... Provide an example
        "example": "",
    },
    # GMC320's
    {
        "match": r"GMC-320\+V5",
        "device": GMC320PlusV5,
        # Open Issue on PyGMC github... make a PR... Provide an example
        "example": "",
    },
    {
        "match": r"GMC-320\+",
        "device": GMC320Plus,
        # My 2019 GC says GMC320 Plus however <GETVER>> doesn't.
        "example": "GMC-320Re 4.26",
    },
    {
        "match": r"GMC-320",
        "device": GMC320,
        # My 2019 GC says GMC320 Plus however <GETVER>> doesn't.
        "example": "GMC-320Re 4.26",
    },
    # GMC500's
    {
        "match": r"GMC-500\+",
        "device": GMC500Plus,
        "example": "GMC-500+Re 2.22",
    },
    {
        "match": r"GMC-500",
        "device": GMC500,
        # Open Issue on PyGMC github... make a PR... Provide an example
        "example": "",
    },
    # GMC600's
    {
        "match": r"GMC-600\+",
        "device": GMC600Plus,
        "example": "",
    },
    {
        "match": r"GMC-600",
        "device": GMC600,
        # Open Issue on PyGMC github... make a PR... Provide an example
        "example": "",
    },
    # GMC800's
    {
        "match": r"GMC-800",
        "device": GMC800,
        # Open Issue on PyGMC github... make a PR... Provide an example
        "example": "",
    },
]


def auto_get_device(connection):
    """
    Auto get device class.
    Given a connection, use device's version response to identify the best matching
    device class.

    Parameters
    ----------
    connection: pygmc.connection.Connection

    Returns
    -------
    pygmc.devices.BaseDevice

    """
    cmd = b"<GETVER>>"
    connection.reset_buffers()
    # TODO: evaluate switching to the .read_at_least() e.g. handle timeout exception
    version = connection.get(cmd).decode("utf8")
    logger.debug(f"Device={version}")

    for device_re in _regex_device_match_list:
        pattern = device_re["match"]
        m = re.match(pattern=pattern, string=version)
        if m:
            logger.debug(f"pattern={pattern} matched version={version}")
            return device_re["device"](port=None, connection=connection)

    logger.debug("No device regex matched. Trying lower level base version.")

    base_version = version[0:7]

    if base_version not in _device_map:
        logger.warning(f"Unable to auto assign device to Device={version}")
        logger.warning("Assuming newer device. Manually specify device if incorrect.")
        return DeviceRFC1801(connection)

    return _device_map[base_version](connection)
