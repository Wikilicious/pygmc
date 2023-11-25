import datetime
import logging
import struct
from typing import Generator, Tuple

from .device import BaseDevice

logger = logging.getLogger("pygmc.devices.rfc1201")


class DeviceRFC1201(BaseDevice):
    def __init__(self, connection):
        """
        A GMC device. Can be used with:
        GMC-280, GMC-300, GMC-320

        Parameters
        ----------
        connection : pygmc.Connection
            An connection interface to the USB device.
        """
        super().__init__(connection)

        # Overwrites from BaseConfig & adds 1801 specific items
        self._cfg_spec_map.update(
            {
                "Calibration_uSv_0": {
                    "index": 10,
                    "size": 4,
                    "description": "",
                    "type": "<f",
                },
                "Calibration_uSv_1": {
                    "index": 16,
                    "size": 4,
                    "description": "",
                    "type": "<f",
                },
                "Calibration_uSv_2": {
                    "index": 22,
                    "size": 4,
                    "description": "",
                    "type": "<f",
                },
                "IdleTextState": {
                    "index": 26,
                    "size": 1,
                    "description": "??",
                    "type": None,
                },
                "AlarmValue_uSv": {
                    "index": 27,
                    "size": 4,
                    "description": "",
                    "type": "<f",
                },
                "Baudrate": {
                    "index": 57,
                    "size": 1,
                    # see https://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=4948 reply#12
                    "description": "64=1200,160=2400,208=4800,232=9600,240=14400,244=19200,248=28800,250=38400,252=57600,254=115200",
                    "type": None,
                },
                "Threshold_uSv": {
                    "index": 65,
                    "size": 4,
                    "description": "",
                    "type": "<f",
                },
            }
        )

    def get_cpm(self) -> int:
        """
        Get CPM counts-per-minute data

        Returns
        -------
        int
            Counts per minute
        """
        # A 16 bit unsigned integer is returned.
        # In total 2 bytes data return from GQ GMC unit.
        # The first byte is MSB byte data and second byte is LSB byte data.
        # 	  e.g.: 00 1C     the returned CPM is 28.

        cmd = b"<GETCPM>>"
        result = self.connection.get_exact(cmd, expected=b"", size=2)
        count = struct.unpack(">H", result)[0]
        return count

    def get_usv_h(self) -> float:
        """
        Get µSv/h
        Uses device calibration config.

        Returns
        -------
        float
            µSv/h

        """
        # lazily load config... i.e. don't load it until it's needed.
        if not self._config:
            self.get_config()

        # Not 100% sure on this...
        # µSv/h = (CPM / CalibrationCPM_1) * Calibration_uSv_1
        usv_h = (self.get_cpm() / self._config["CalibrationCPM_1"]) * self._config[
            "Calibration_uSv_1"
        ]
        return usv_h

    def get_gyro(self) -> Tuple[int, int, int]:
        """
        Get gyroscope data.
        No units specified in spec RFC1801 nor RFC1201 :(

        Returns
        -------
        Tuple[int, int, int]
            (X, Y, Z) gyroscope data
        """
        cmd = b"<GETGYRO>>"
        # Return: Seven bytes gyroscope data in hexdecimal:
        #   BYTE1,BYTE2,BYTE3,BYTE4,BYTE5,BYTE6,BYTE7
        # Here: BYTE1,BYTE2 are the X position data in 16 bits value.
        #   The first byte is MSB byte data and second byte is LSB byte data.
        # BYTE3,BYTE4 are the Y position data in 16 bits value.
        #   The first byte is MSB byte data and second byte is LSB byte data.
        # BYTE5,BYTE6 are the Z position data in 16 bits value.
        #   The first byte is MSB byte data and second byte is LSB byte data.
        # BYTE7 always 0xAA
        result = self.connection.get_exact(cmd, expected=b"", size=7)
        x, y, z, dummy = struct.unpack(">hhhB", result)
        return x, y, z

    def get_voltage(self) -> float:
        """
        Get device voltage

        Returns
        -------
        float
            Device voltage in volts

        """
        cmd = b"<GETVOLT>>"
        result = self.connection.get_exact(cmd, expected=b"", size=1)
        # result example: b'*'.hex() -> '2a' -> int('2a', 16) -> 42 -> 4.2V
        result = int(result.hex(), 16) / 10
        return result

    def get_datetime(self) -> datetime.datetime:
        """
        Get device datetime

        Returns
        -------
        datetime.datetime
            Device datetime
        """
        # Return: Seven bytes data: YY MM DD HH MM SS 0xAA
        cmd = b"<GETDATETIME>>"
        data = self.connection.get_exact(cmd, expected=b"", size=7)
        year = int("20{0:2d}".format(data[0]))
        month = int("{0:2d}".format(data[1]))
        day = int("{0:2d}".format(data[2]))
        hour = int("{0:2d}".format(data[3]))
        minute = int("{0:2d}".format(data[4]))
        second = int("{0:2d}".format(data[5]))
        return datetime.datetime(year, month, day, hour, minute, second)

    def get_config(self) -> dict:
        """
        Get device config

        Returns
        -------
        dict

        """
        cmd = b"<GETCFG>>"
        self.connection.reset_buffers()
        cfg_bytes = self.connection.get_exact(cmd, expected=b"", size=256)
        self._parse_cfg(cfg_bytes)
        return self._config

    def heartbeat_live(self, count=60) -> Generator[int, None, None]:
        """
        Get live CPS data, as a generator. i.e. yield (return) CPS as available.

        Parameters
        ----------
        count : int, optional
            How many CPS counts to return (default=60). Theoretically, 1 count = 1 second.
            Wall-clock time can be a bit higher or lower.

        Yields
        ------
        int
            CPS
        """
        self.connection.reset_buffers()
        try:
            self._heartbeat_on()
            for i in range(count):
                raw = self.connection.read_until(expected=b"", size=2)
                # only first 14 bits are used, because why not complicate things
                cps = struct.unpack(">H", raw)[0] & 0x3FFF
                yield cps
        finally:
            self._heartbeat_off()

    def heartbeat_live_print(self, count=60) -> None:
        """
        Print live CPS data.

        Parameters
        ----------
        count : int, optional
            How many CPS counts to return (default=60). Theoretically, 1 count = 1 second.
            Wall-clock time can be a bit higher or lower.

        """
        max_ = 0
        i = 0
        for cps in self.heartbeat_live(count=count):
            i += 1
            if cps > max_:
                max_ = cps
            # empty leading space for terminal cursor
            msg = f" cps={cps:<2} | max={max_:<2} | loop={i:<10,}"
            print(msg, end="\r")  # Carriage return - update line we just printed
        print("", end="\n")  # empty print to move carriage return to next line
