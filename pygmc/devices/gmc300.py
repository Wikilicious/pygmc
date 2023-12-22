"""
GQ Electronics GMC-3XX series Geiger Counter Devices.
"""
import serial

from ..connection import Connection
from .device_rfc1201 import DeviceRFC1201


class GMC300(DeviceRFC1201):
    """GMC-300"""

    def __init__(
        self,
        port,
        baudrate=57600,
        connection=None,
    ):
        """
        Represent a GMC-300 device.

        Parameters
        ----------
        port: None | str
            Exact port (device dev path / com port) e.g. '/dev/ttyUSB0'
            If None, a Connection object is required.
        baudrate: int
            Device baudrate. Default value is the best-known value for the device.
        connection : pygmc.Connection
            An initialized pygmc connection interface to the USB device.
            Overrides port & baudrate.
        """
        if isinstance(connection, Connection):
            super().__init__(connection)
        elif port and isinstance(baudrate, int):
            conn = Connection(timeout=5)
            conn.connect(port=port, baudrate=baudrate)
            super().__init__(conn)
        else:
            raise ConnectionError(f"Unable to connect port={port} baudrate={baudrate}")
        self._flash_memory_size_bytes = 2**16
        self._baudrate = 57600

    @staticmethod
    def connect(port, baudrate=57600):
        """
        Connect to GMC-300.

        Parameters
        ----------
        port: str
            Exact port (device dev path / com) e.g. '/dev/ttyUSB0'.
        baudrate: int
            Device baudrate.

        Returns
        -------
        GMC300S
            An gmc device with initialized connection ready to use.

        """
        usb_serial = serial.Serial(port=port, baudrate=baudrate, timeout=5)
        connection = Connection()
        connection.connect_user_provided(usb_serial)
        gc = GMC300(port=None, connection=connection)
        return gc


class GMC300S(DeviceRFC1201):
    """GMC-300S"""

    def __init__(
        self,
        port,
        baudrate=57600,
        connection=None,
    ):
        """
        Represent a GMC-300S device.

        Parameters
        ----------
        port: None | str
            Exact port (device dev path / com port) e.g. '/dev/ttyUSB0'
            If None, a Connection object is required.
        baudrate: int
            Device baudrate. Default value is the best-known value for the device.
        connection : pygmc.Connection
            An initialized pygmc connection interface to the USB device.
            Overrides port & baudrate.
        """
        if isinstance(connection, Connection):
            super().__init__(connection)
        elif port and isinstance(baudrate, int):
            conn = Connection(timeout=5)
            conn.connect(port=port, baudrate=baudrate)
            super().__init__(conn)
        else:
            raise ConnectionError(f"Unable to connect port={port} baudrate={baudrate}")
        self._baudrate = 57600

    @staticmethod
    def connect(port, baudrate=57600):
        """
        Connect to GMC-300S.

        Parameters
        ----------
        port: str
            Exact port (device dev path / com) e.g. '/dev/ttyUSB0'.
        baudrate: int
            Device baudrate.

        Returns
        -------
        GMC300S
            An gmc device with initialized connection ready to use.

        """
        usb_serial = serial.Serial(port=port, baudrate=baudrate, timeout=5)
        connection = Connection()
        connection.connect_user_provided(usb_serial)
        gc = GMC300S(port=None, connection=connection)
        return gc


class GMC300EPlus(DeviceRFC1201):
    """GMC-300E+"""

    def __init__(
        self,
        port,
        baudrate=57600,
        connection=None,
    ):
        """
        Represent a GMC-300E+ device.

        Parameters
        ----------
        port: None | str
            Exact port (device dev path / com port) e.g. '/dev/ttyUSB0'
            If None, a Connection object is required.
        baudrate: int
            Device baudrate. Default value is the best-known value for the device.
        connection : pygmc.Connection
            An initialized pygmc connection interface to the USB device.
            Overrides port & baudrate.
        """
        if isinstance(connection, Connection):
            super().__init__(connection)
        elif port and isinstance(baudrate, int):
            conn = Connection(timeout=5)
            conn.connect(port=port, baudrate=baudrate)
            super().__init__(conn)
        else:
            raise ConnectionError(f"Unable to connect port={port} baudrate={baudrate}")
        self._baudrate = 57600

    @staticmethod
    def connect(port, baudrate=57600):
        """
        Connect to GMC-300E+.

        Parameters
        ----------
        port: str
            Exact port (device dev path / com) e.g. '/dev/ttyUSB0'.
        baudrate: int
            Device baudrate.

        Returns
        -------
        GMC300EPlus
            An gmc device with initialized connection ready to use.

        """
        usb_serial = serial.Serial(port=port, baudrate=baudrate, timeout=5)
        connection = Connection()
        connection.connect_user_provided(usb_serial)
        gc = GMC300EPlus(port=None, connection=connection)
        return gc
