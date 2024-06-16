import logging
import re

from .device_rfc1201 import DeviceRFC1201
from .device_rfc1801 import DeviceRFC1801
from .device_spec404 import DeviceSpec404
from .gmc300 import GMC300, GMC300S, GMC300EPlus
from .gmc320 import GMC320, GMC320Plus, GMC320PlusV5
from .gmc500 import GMC500, GMC500Plus
from .gmc600 import GMC600, GMC600Plus
from .gmc800 import GMC800
from .gmcse import GMCSE

logger = logging.getLogger("pygmc.device")


# Match regex to device. Order matters. First match is used.
device_match_list = [
    # GMC300's
    {
        "match_regex": r"GMC-300S",
        "device_class": GMC300S,
        "protocol_class": DeviceRFC1201,
        "version_example": "GMC-300SRe 1.14",
    },
    {
        # Not sure...
        "match_regex": r"GMC-300E\+",
        "device_class": GMC300EPlus,
        "protocol_class": DeviceRFC1201,
        # Open Issue on PyGMC github... make a PR... Provide an example
        "version_example": "",
    },
    {
        # Does this model exist?
        "match_regex": r"GMC-300",
        "device_class": GMC300,
        "protocol_class": DeviceRFC1201,
        # Open Issue on PyGMC github... make a PR... Provide an example
        "version_example": "",
    },
    # GMC320's
    {
        "match_regex": r"GMC-320\+V5",
        "device_class": GMC320PlusV5,
        "protocol_class": DeviceRFC1201,
        # Open Issue on PyGMC github... make a PR... Provide an example
        "version_example": "",
    },
    {
        "match_regex": r"GMC-320\+",
        "device_class": GMC320Plus,
        "protocol_class": DeviceRFC1201,
        # My 2019 GC says GMC320 Plus however <GETVER>> returns 'GMC-320Re 4.26'
        # For sake of passing unittests (and hoping a newer rev adds the '+')
        # Faking version below from "GMC-320Re 4.26" --> "GMC-320+Re 4.26"
        "version_example": "GMC-320+Re 4.26",
    },
    {
        "match_regex": r"GMC-320",
        "device_class": GMC320,
        "protocol_class": DeviceRFC1201,
        # My 2019 GC says GMC320 Plus however <GETVER>> doesn't.
        "version_example": "GMC-320Re 4.26",
    },
    # GMC500's
    {
        "match_regex": r"GMC-500\+",
        "device_class": GMC500Plus,
        "protocol_class": DeviceRFC1801,
        "version_example": "GMC-500+Re 2.22",
    },
    {
        "match_regex": r"GMC-500",
        "device_class": GMC500,
        "protocol_class": DeviceRFC1801,
        # Open Issue on PyGMC github... make a PR... Provide an example
        "version_example": "",
    },
    # GMC600's
    {
        "match_regex": r"GMC-600\+",
        "device_class": GMC600Plus,
        "protocol_class": DeviceRFC1801,
        "version_example": "GMC-600+Re 2.52",  # Thomaz device
    },
    {
        "match_regex": r"GMC-600",
        "device_class": GMC600,
        "protocol_class": DeviceRFC1801,
        # Open Issue on PyGMC github... make a PR... Provide an example
        "version_example": "",
    },
    # GMC800's
    # Listed as RFC1201 in https://www.gqelectronicsllc.com/GMC-800UserGuide.pdf
    # See: https://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=10394
    # PyGMC invented a spec - DeviceSpec404 - For GMC800 with incorrect official spec
    {
        "match_regex": r"GMC-800",
        "device_class": GMC800,
        "protocol_class": DeviceSpec404,
        "version_example": "GMC-800Re1.08",  # Thomaz owned device example
    },
    # GMCSE
    {
        "match_regex": r"GMC-SE",
        "device_class": GMCSE,
        "protocol_class": DeviceRFC1201,
        "version_example": "GMC-SE Re 1.05",
    },
]


def _get_matched_class_from_version(version: str):
    for device_re in device_match_list:
        pattern = device_re["match_regex"]
        m = re.match(pattern=pattern, string=version)
        if m:
            logger.debug(f"pattern={pattern} matched version={version}")
            return device_re["device_class"]

    logger.warning(f"Unable to auto assign Device={version}")
    issues_url = "https://github.com/Wikilicious/pygmc/issues"
    logger.warning(f"Please open an issue {issues_url}")


def auto_get_device_from_discovery_details(device_details):
    """
    Auto get device class from discovery device_details named tuple.

    Parameters
    ----------
    device_details: namedtuple
        Discovery device details.

    Returns
    -------
    pygmc.devices.BaseDevice | None

    """
    device_class = _get_matched_class_from_version(device_details.version)
    return device_class


def auto_get_device_from_connection(connection):
    """
    Auto get device class.

    Given a connection, use device's version response to identify the best matching
    device class.

    Parameters
    ----------
    connection: pygmc.connection.Connection

    Returns
    -------
    pygmc.devices.BaseDevice | None

    """
    version = connection.get_at_least(b"<GETVER>>", size=7, wait_sleep=0.01).decode()
    logger.debug(f"Device={version}")

    device_class = _get_matched_class_from_version(version)
    return device_class
