import serial

from ..connection import Connection
from .device_rfc1201 import DeviceRFC1201


class GMC300(DeviceRFC1201):
    """GMC-300"""

    def __init__(self, connection):
        """
        Represent a GMC-300 device.

        Parameters
        ----------
        connection : pygmc.Connection
            An connection interface to the USB device.
        """
        super().__init__(connection)
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
        gc = GMC300(connection)
        return gc


class GMC300S(DeviceRFC1201):
    """GMC-300S"""

    def __init__(self, connection):
        """
        Represent a GMC-300S device.

        Parameters
        ----------
        connection : pygmc.Connection
            An connection interface to the USB device.
        """
        super().__init__(connection)
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
        gc = GMC300S(connection)
        return gc


class GMC300EPlus(DeviceRFC1201):
    """GMC-300E+"""

    def __init__(self, connection):
        """
        Represent a GMC-300E+ device.

        Parameters
        ----------
        connection : pygmc.Connection
            An connection interface to the USB device.
        """
        super().__init__(connection)
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
        gc = GMC300EPlus(connection)
        return gc
