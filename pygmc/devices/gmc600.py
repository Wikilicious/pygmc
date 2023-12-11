import serial

from ..connection import Connection
from .device_rfc1801 import DeviceRFC1801


class GMC600(DeviceRFC1801):
    """GMC-600"""

    def __init__(self, connection):
        """
        Represent a GMC-600 device.

        Parameters
        ----------
        connection : pygmc.Connection
            An connection interface to the USB device.
        """
        super().__init__(connection)

    @staticmethod
    def connect(port, baudrate=115200):
        """
        Connect to GMC-600.

        Parameters
        ----------
        port: str
            Exact port (device dev path / com) e.g. '/dev/ttyUSB0'.
        baudrate: int
            Device baudrate.

        Returns
        -------
        GMC600
            An gmc device with initialized connection ready to use.

        """
        usb_serial = serial.Serial(port=port, baudrate=baudrate, timeout=5)
        connection = Connection()
        connection.connect_user_provided(usb_serial)
        gc = GMC600(connection)
        return gc


class GMC600Plus(DeviceRFC1801):
    """GMC-600+"""

    def __init__(self, connection):
        """
        Represent a GMC-600+ device.

        Parameters
        ----------
        connection : pygmc.Connection
            An connection interface to the USB device.
        """
        super().__init__(connection)

    @staticmethod
    def connect(port, baudrate=115200):
        """
        Connect to GMC-600+.

        Parameters
        ----------
        port: str
            Exact port (device dev path / com) e.g. '/dev/ttyUSB0'.
        baudrate: int
            Device baudrate.

        Returns
        -------
        GMC600Plus
            An gmc device with initialized connection ready to use.

        """
        usb_serial = serial.Serial(port=port, baudrate=baudrate, timeout=5)
        connection = Connection()
        connection.connect_user_provided(usb_serial)
        gc = GMC600Plus(connection)
        return gc
