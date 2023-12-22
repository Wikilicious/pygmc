import serial

from ..connection import Connection
from .device_rfc1201 import DeviceRFC1201


class GMC800(DeviceRFC1201):
    """GMC-800"""

    def __init__(
        self,
        port,
        baudrate=115200,
        connection=None,
    ):
        """
        Represent a GMC-800 device.

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
        # seemed like bigger number would use newer rfc spec until GMC-800
        # listed as RFC1201 in https://www.gqelectronicsllc.com/GMC-800UserGuide.pdf

    @staticmethod
    def connect(port, baudrate=115200):
        """
        Connect to GMC-800.

        Parameters
        ----------
        port: str
            Exact port (device dev path / com) e.g. '/dev/ttyUSB0'.
        baudrate: int
            Device baudrate.

        Returns
        -------
        GMC800
            An gmc device with initialized connection ready to use.

        """
        usb_serial = serial.Serial(port=port, baudrate=baudrate, timeout=5)
        connection = Connection()
        connection.connect_user_provided(usb_serial)
        gc = GMC800(port=None, connection=connection)
        return gc
