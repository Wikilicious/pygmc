import logging
import re

# pypi
from serial.tools import list_ports as serial_list_ports

logger = logging.getLogger("pygmc.connection")


def get_all_usb_devices(regexp=None, include_links=True) -> list:
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


def get_gmc_usb_devices(
    vid="1A86", pid="7523", description=".*", include_links=True
) -> list:
    """
    Get a list of GMC USB devices.

    Default parameters are best known parameters that
    matches GMC USB devices.

    Parameters
    ----------
    vid: str | int
        Hexadecimal string or int to exact match the Vendor-ID vid.
        e.g. '0x1A86' or '1A86' or 6790 will all match.
    pid: str | int
        Hexadecimal string or int to exact match the Product-ID pid.
        e.g. '0x7523' or '7523' or 29987 will all match. (Note '7523' is considered a hex
        as a string)
    description: str
        Regex to match usb device description. (case-insensitive flag used)
        Known descriptions: 'USB2.0-Serial' & 'USB-Serial'
    include_links : bool
        Include symlinks under /dev when they point to a serial port, by default True

    Returns
    -------
    list
        List of GMC devices.

    """
    # vid = "1A86"  # 6790
    # pid = "7523"  # 29987

    if isinstance(vid, str):
        vid = int(vid, base=16)

    if isinstance(pid, str):
        pid = int(pid, base=16)

    logger.debug(
        f"get_available_usb_devices({vid}, {pid}, {description}, {include_links}"
    )

    all_devices = serial_list_ports.comports(include_links=include_links)
    logger.debug(f"All devices: {[(x.device, x.hwid) for x in all_devices]}")
    matched_devices = []
    for device in all_devices:
        vid_m = vid == device.vid
        pid_m = pid == device.pid
        description_m = re.match(
            description, str(device.description), flags=re.IGNORECASE
        )
        if all([vid_m, pid_m, description_m]):
            matched_devices.append(device)
    logger.debug(f"Matched devices: {[(x.device, x.hwid) for x in matched_devices]}")

    return matched_devices
