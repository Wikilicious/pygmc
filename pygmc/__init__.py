__version__ = "0.1.1"
__author__ = "Thomaz"
__license__ = "MIT"


import logging
from pygmc.connection import Connection
from pygmc.devices import auto_get_device

logger = logging.getLogger(__name__)


def connect(port=None, vid="1A86", pid="7523", description=None, hardware_id=None):
    """
    Connect to device.
    If all parameters are None, _auto_connect() flow is used which attempts to connect to all available ports.
    If ANY parameter is given; it's used to refine the search, any matches are considered.
    Parameters are used as an OR search.

    Parameters
    ----------
    port : str | None, optional
        Device port, by default None
        e.g. 'USB0' or 'COM3' or '/dev/ttyUSB*'
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
        port=port, vid=vid, pid=pid, description=description, hardware_id=hardware_id
    )

    device = auto_get_device(connection)

    ver = device.get_version()
    msg = f"Connected device={ver}"
    print(msg)  # print for newbies w/o logger knowledge
    logger.info(msg)

    return device
