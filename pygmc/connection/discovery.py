"""Discover GMC devices."""
import logging
import re
from collections import namedtuple

from serial import SerialException

from .connection import Connection
from .const import BAUDRATES
from .utils import get_gmc_usb_devices

logger = logging.getLogger("pygmc.discovery")


device_details = namedtuple("Device", ["port", "baudrate", "version", "serial_number"])


class Discovery:
    """Discover GMC Devices"""

    def __init__(self, port=None, baudrate=None):
        """
        Discover GMC devices.

        Parameters
        ----------
        port: str | None
            Dev device, port, com, if known. Leave None to auto-discover all ports.
        baudrate: int | None
            Device baudrate, if known. Leave None to auto-discover correct baudrate.
        """
        self._discovered_devices = []
        self._discover_devices_flow(port=port, baudrate=baudrate)

    def _discover_devices_flow(self, port=None, baudrate=None) -> None:
        # reset discovered devices
        self._discovered_devices = []
        if port and baudrate:
            # what are you doing in discovery?
            self._validate_device(port, baudrate)
        elif port and not baudrate:
            # likely the 2nd most used
            self._discover_with_known_port(port=port)
        elif baudrate and not port:
            # Edge case...
            self._discover_with_known_baudrate(baudrate=baudrate)
        else:
            # lemme just do everything for you... likely most common case
            self._discover_all()

    @staticmethod
    def _get_gmc_usb_ports() -> list:
        devices = get_gmc_usb_devices()
        ports = [x.device for x in devices]
        # make the list intuitive
        ports = sorted(ports)
        return ports

    @staticmethod
    def _get_device_info(conn):
        if conn._con.in_waiting != 0:
            # don't intrude
            logger.debug(f"Device has non-zero bytes waiting in in-buffer ({conn._con})")
            return None
        # Device likely has heartbeat on
        if conn._con.out_waiting != 0:
            # don't intrude
            logger.debug(f"Device has non-zero bytes waiting in out-buffer ({conn._con})")
            return None

        try:
            conn.reset_buffers()
            serial_number = conn.get_exact(b"<GETSERIAL>>", size=7).hex()
            version = conn.get_at_least(b"<GETVER>>", size=7, wait_sleep=0.01).decode()
            if serial_number and version:
                return {"serial_number": serial_number, "version": version}
            else:
                return None
        except Exception as e:
            # Unsure of exception types.
            logger.warning(f"{e}", exc_info=True)
            return None
        finally:
            conn.reset_buffers()

    def _validate_device(self, port, baudrate) -> bool:
        logger.debug(f"Checking port={port} baudrate={baudrate}")
        try:
            conn = Connection(port=port, baudrate=baudrate, timeout=2)
        except SerialException as e:
            # Should a convenience method log as warning/error?
            # If only GQ Electronics would put the version/serial in USB description...
            logger.warning(f"Skipping error connecting: {e}", exc_info=True)
            return False

        info = self._get_device_info(conn)
        conn.close_connection()
        if info:
            version = info["version"]
            serial_number = info["serial_number"]
            discovered_device = device_details(
                port=port, baudrate=baudrate, version=version, serial_number=serial_number
            )
            logger.debug(f"Discovered device: {discovered_device}")
            self._discovered_devices.append(discovered_device)
            return True

        return False

    def _discover_with_known_baudrate(self, baudrate) -> None:
        ports = self._get_gmc_usb_ports()
        for port in ports:
            self._validate_device(port=port, baudrate=baudrate)

    def _discover_with_known_port(self, port) -> None:
        for baudrate in BAUDRATES:
            is_valid = self._validate_device(port=port, baudrate=baudrate)
            if is_valid:
                break

    def _discover_all(self) -> None:
        ports = self._get_gmc_usb_ports()
        for port in ports:
            # D.R.Y. (don't repeat yourself)
            self._discover_with_known_port(port=port)

    def get_device_by_serial_number(self, serial_number) -> list:
        """
        Get devices by matching serial number.

        May return more than one device if sym-links are used.

        Parameters
        ----------
        serial_number: str
            Device serial number.

        Returns
        -------
        list
            List of matching devices.

        """
        # may return more than one device if user made multiple links
        matched_devices = []
        for device in self._discovered_devices:
            if device.serial_number == serial_number:
                matched_devices.append(device)
        return matched_devices

    def get_device_by_version(self, version) -> list:
        """
        Get devices by matching version.

        Parameters
        ----------
        version: str
            Device version regex. e.g. 'GMC-5' will match any device starting with GMC-5.

        Returns
        -------
        list
            List of matching devices.

        """
        matched_devices = []
        for device in self._discovered_devices:
            if re.match(version, str(device.version), flags=re.IGNORECASE):
                matched_devices.append(device)
        return matched_devices

    def get_all_devices(self) -> list:
        """
        Get all discovered devices.

        Returns
        -------
        list
            List of all discovered devices.

        """
        return self._discovered_devices
