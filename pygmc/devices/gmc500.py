"""GMC-500 Devices."""

from ..connection import Connection
from .device_rfc1801 import DeviceRFC1801


class GMC500(DeviceRFC1801):
    """GMC-500"""

    def __init__(
        self,
        port,
        baudrate=115200,
        timeout=5,
        connection=None,
    ):
        """
        Represent a GMC-500 device.

        Parameters
        ----------
        port: None | str
            Exact port (device dev path / com port) e.g. '/dev/ttyUSB0'
            If None, a Connection object is required.
        baudrate: int
            Device baudrate. Default value is the best-known value for the device.
        timeout: int
            Time limit for pyserial to raise timeout.
        connection : pygmc.Connection
            An initialized pygmc connection interface to the USB device.
            Overrides port & baudrate.
        """
        if isinstance(connection, Connection):
            super().__init__(connection)
        elif port and isinstance(baudrate, int):
            conn = Connection(port=port, baudrate=baudrate, timeout=timeout)
            super().__init__(conn)
        else:
            raise ConnectionError(f"Unable to connect port={port} baudrate={baudrate}")


class GMC500Plus(DeviceRFC1801):
    """GMC-500+"""

    def __init__(
        self,
        port,
        baudrate=115200,
        timeout=5,
        connection=None,
    ):
        """
        Represent a GMC-500+ device.

        Parameters
        ----------
        port: None | str
            Exact port (device dev path / com port) e.g. '/dev/ttyUSB0'
            If None, a Connection object is required.
        baudrate: int
            Device baudrate. Default value is the best-known value for the device.
        timeout: int
            Time limit for pyserial to raise timeout.
        connection : pygmc.Connection
            An initialized pygmc connection interface to the USB device.
            Overrides port & baudrate.
        """
        if isinstance(connection, Connection):
            super().__init__(connection)
        elif port and isinstance(baudrate, int):
            conn = Connection(port=port, baudrate=baudrate, timeout=timeout)
            super().__init__(conn)
        else:
            raise ConnectionError(f"Unable to connect port={port} baudrate={baudrate}")
