import serial

from ..connection import Connection
from .device_rfc1201 import DeviceRFC1201


class GMC320(DeviceRFC1201):
    """GMC-320"""

    def __init__(self, connection):
        """
        Represent a GMC-320 device.

        Parameters
        ----------
        connection : pygmc.Connection
            An connection interface to the USB device.
        """
        super().__init__(connection)

    @staticmethod
    def connect(port, baudrate=115200):
        """
        Connect to GMC-320.

        Parameters
        ----------
        port: str
            Exact port (device dev path / com) e.g. '/dev/ttyUSB0'.
        baudrate: int
            Device baudrate.

        Returns
        -------
        GMC320
            An gmc device with initialized connection ready to use.

        """
        usb_serial = serial.Serial(port=port, baudrate=baudrate, timeout=5)
        connection = Connection()
        connection.connect_user_provided(usb_serial)
        gc = GMC320(connection)
        return gc


class GMC320Plus(DeviceRFC1201):
    """GMC-320+"""

    def __init__(self, connection):
        """
        Represent a GMC-320+ device.

        Parameters
        ----------
        connection : pygmc.Connection
            An connection interface to the USB device.
        """
        super().__init__(connection)

    @staticmethod
    def connect(port, baudrate=115200):
        """
        Connect to GMC-320+.

        Parameters
        ----------
        port: str
            Exact port (device dev path / com) e.g. '/dev/ttyUSB0'.
        baudrate: int
            Device baudrate.

        Returns
        -------
        GMC320Plus
            An gmc device with initialized connection ready to use.

        """
        usb_serial = serial.Serial(port=port, baudrate=baudrate, timeout=5)
        connection = Connection()
        connection.connect_user_provided(usb_serial)
        gc = GMC320Plus(connection)
        return gc


class GMC320PlusV5(DeviceRFC1201):
    """GMC-320+V5"""

    def __init__(self, connection):
        """
        Represent a GMC-320+V5 device.

        Parameters
        ----------
        connection : pygmc.Connection
            An connection interface to the USB device.
        """
        super().__init__(connection)

    @staticmethod
    def connect(port, baudrate=115200):
        """
        Connect to GMC-320+V5.

        Parameters
        ----------
        port: str
            Exact port (device dev path / com) e.g. '/dev/ttyUSB0'.
        baudrate: int
            Device baudrate.

        Returns
        -------
        GMC320PlusV5
            An gmc device with initialized connection ready to use.

        """
        usb_serial = serial.Serial(port=port, baudrate=baudrate, timeout=5)
        connection = Connection()
        connection.connect_user_provided(usb_serial)
        gc = GMC320PlusV5(connection)
        return gc
