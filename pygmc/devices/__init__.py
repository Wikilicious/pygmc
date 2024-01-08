import logging

from .auto_get_device import (
    auto_get_device_from_connection,
    auto_get_device_from_discovery_details,
)
from .device import BaseDevice
from .device_rfc1201 import DeviceRFC1201
from .device_rfc1801 import DeviceRFC1801
from .gmc300 import GMC300, GMC300S, GMC300EPlus
from .gmc320 import GMC320, GMC320Plus, GMC320PlusV5
from .gmc500 import GMC500, GMC500Plus
from .gmc600 import GMC600, GMC600Plus
from .gmc800 import GMC800

logger = logging.getLogger("pygmc.device")
