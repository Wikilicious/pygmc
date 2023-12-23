import logging

# pypi
from serial.tools import list_ports as serial_list_ports

logger = logging.getLogger("pygmc.connection")


def get_available_usb_devices(regexp=None, include_links=True) -> list:
    """
    Get all available USB devices.

    Parameters
    ----------
    regexp : None | str, optional
        Search for ports using a regular expression. Port name, description and
        hardware ID are searched.
        hardwareID example ('USB VID:PID=1A86:7523 LOCATION=2-1')
        Default=None, find all.
    include_links : bool, optional
        include symlinks under /dev when they point to a serial port, by default True

    Returns
    -------
    list
        available ports, type [serial.tools.list_ports_linux.SysFS]
    """
    logger.debug(
        f"_get_available_usb_devices(regexp={regexp}, include_links={include_links})"
    )
    if not regexp:
        ports = serial_list_ports.comports(include_links=include_links)
    else:
        # cast as list because it's a generator and I want an easy return type
        # How many USB devices could a user possibly have?
        ports = list(serial_list_ports.grep(regexp=regexp, include_links=include_links))

    logger.debug(f"All ports/dev-devices found: {[(x.device, x.hwid) for x in ports]}")

    return ports
