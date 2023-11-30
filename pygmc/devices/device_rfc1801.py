import datetime
import logging
import struct
from typing import Generator, Tuple

from .device import BaseDevice

logger = logging.getLogger("pygmc.devices.rfc1801")


class DeviceRFC1801(BaseDevice):
    def __init__(self, connection):
        """
        Represent a GMC device.

        Can be used with:
        GMC-500, GMC-500+, GMC-600, GMC-600+

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
                    "type": ">f",
                },
                "Calibration_uSv_1": {
                    "index": 16,
                    "size": 4,
                    "description": "",
                    "type": ">f",
                },
                "Calibration_uSv_2": {
                    "index": 22,
                    "size": 4,
                    "description": "",
                    "type": ">f",
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
                    "type": ">f",
                },
                "Baudrate": {
                    "index": 57,
                    "size": 1,
                    # see https://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=4948
                    # reply#14
                    "description": "0=115200, 1=1200, 2=2400, 3=4800, 4=9600, 5=14400, "
                    "6=19200, 7=28800, 8=38400, 9=57600",
                    "type": None,
                },
                "Threshold_uSv": {
                    "index": 65,
                    "size": 4,
                    "description": "",
                    "type": ">f",
                },
            }
        )

    def get_cpm(self) -> int:
        """
        Get CPM counts-per-minute data.

        Specs don't provide how CPM is computed nor if both high/low tubes are used.

        Returns
        -------
        int
            Counts per minute (GMC has 2 tubes, assumed cpm accounts for both?)
        """
        # A 32 bit unsigned integer is returned.
        # In total 4 bytes data return from GQ GMC unit.
        # The first byte is MSB byte data and fourth byte is LSB byte data.
        # e.g.: 00 00 00 1C     the returned CPM is 28. big-endian
        cmd = b"<GETCPM>>"
        result = self.connection.get_exact(cmd, expected=b"", size=4)
        count = struct.unpack(">I", result)[0]
        return count

    def get_usv_h(self) -> float:
        """
        Get µSv/h.

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

    def get_cps(self) -> int:
        """
        Get CPS counts-per-second.

        Returns
        -------
        int
            Counts per second
        """
        cmd = b"<GETCPS>>"
        result = self.connection.get_exact(cmd, expected=b"", size=4)
        count = struct.unpack(">I", result)[0]
        return count

    def get_max_cps(self) -> int:
        """
        Get the maximum counts-per-second since the device POWERED ON.

        Returns
        -------
        int
            Max counts per second observed
        """
        cmd = b"<GETMAXCPS>>"
        result = self.connection.get_exact(cmd, expected=b"", size=4)
        count = struct.unpack(">I", result)[0]
        return count

    def get_cpmh(self) -> int:
        """
        Get CPM of the high dose tube.

        Only GMC-500+ supported (spec RFC1801)

        Returns
        -------
        int
            Counts per minute on high dose tube (GMC has 2 tubes)
        """
        #
        # A 32 bit unsigned integer is returned.
        # In total 4 bytes data return from GQ GMC unit.
        # The first byte is MSB byte data and fourth byte is LSB byte data.
        # e.g.: 00 00 00 1C     the returned CPM is 28. big-endian
        cmd = b"<GETCPMH>>"
        result = self.connection.get_exact(cmd, expected=b"", size=4)
        count = struct.unpack(">I", result)[0]
        return count

    def get_cpml(self) -> int:
        """
        Get CPM of the low dose tube.

        Only GMC-500+ supported (spec RFC1801)

        Returns
        -------
        int
             Counts per minute on low dose tube (GMC has 2 tubes)
        """
        cmd = b"<GETCPML>>"
        result = self.connection.get_exact(cmd, expected=b"", size=4)
        count = struct.unpack(">I", result)[0]
        return count

    def get_datetime(self) -> datetime.datetime:
        """
        Get device datetime.

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
        Get device voltage.

        Returns
        -------
        float
            Device voltage in volts

        Notes
        -----
        Device only has resolution to tenth of a volt despite example in spec RFC1801.

        """
        # Device only has resolution to tenth of a volt despite example in spec RFC1801.
        cmd = b"<GETVOLT>>"
        result = self.connection.get_exact(cmd, expected=b"", size=5)
        # result example: b'4.8v\x00'
        result = float(result[0:3])  # e.g. float(b'4.8')
        return result

    def get_config(self) -> dict:
        """
        Get device config.

        Returns
        -------
        dict

        """
        cmd = b"<GETCFG>>"
        self.connection.reset_buffers()
        cfg_bytes = self.connection.get_exact(cmd, expected=b"", size=512)
        self._parse_cfg(cfg_bytes)
        return self._config

    def power_off(self) -> None:
        """Power OFF device."""
        cmd = b"<POWEROFF>>"
        self.connection.reset_buffers()
        self.connection.write(cmd)

    def power_on(self) -> None:
        """Power ON device."""
        cmd = b"<POWERON>>"
        self.connection.reset_buffers()
        self.connection.write(cmd)

    def heartbeat_live(self, count=60) -> Generator[int, None, None]:
        """
        Get live CPS data, as a generator.

        i.e. yield (return) CPS as available.

        Parameters
        ----------
        count : int, optional
            How many CPS counts to return (default=60). Theoretically, 1count = 1second.
            Wall-clock time can be a bit higher or lower.

        Yields
        ------
        int
            CPS - Counts-Per-Second int

        """
        self.connection.reset_buffers()
        try:
            self._heartbeat_on()
            for i in range(count):
                raw = self.connection.read_until(expected=b"", size=4)
                cps = struct.unpack(">I", raw)[0]
                yield cps
        finally:
            self._heartbeat_off()

    def heartbeat_live_print(self, count=60) -> None:
        """
        Print live CPS data.

        Parameters
        ----------
        count : int, optional
            How many CPS counts to return (default=60). Theoretically, 1count = 1second.
            Wall-clock time can be a bit higher or lower.

        """
        max_ = 0
        i = 0
        for cps in self.heartbeat_live(count=count):
            i += 1
            if cps > max_:
                max_ = cps
            # Yea, I'd rather use f-string... just trying to make it compatible with
            # older Python versions
            # empty leading space for terminal cursor
            msg = " cps={cps:<2} | max={max_:<2} | loop={i:<10,}".format(
                cps=cps, max_=max_, i=i
            )
            print(msg, end="\r")  # Carriage return - update line we just printed
        print("", end="\n")  # empty print to move carriage return to next line

    def send_key(self, key_number) -> None:
        """
        Send key press signal to device.

        Note the power button acts as menu clicks and does not power on/off.

        Parameters
        ----------
        key_number: int
            Each number represents a key-press.
            key=0 -> S1 (back button)
            key=1 -> S2 (down button)
            key=2 -> S3 (up button)
            key=3 -> S4 (power button)
        """
        if key_number not in (0, 1, 2, 3):
            raise ValueError("key must be in (0, 1, 2, 3)")

        cmd = "<KEY{}>>".format(key_number).encode()
        self.connection.write(cmd)

    def set_datetime(self, datetime_=None) -> None:
        """
        Set datetime on device.

        Parameters
        ----------
        datetime_: None | datetime.datetime
            Datetime to set. Default=None uses current time on computer i.e.
            datetime.datetime.now()

        Raises
        ------
        ValueError
            Year value earlier than 2000.

        RuntimeError
            Unexpected response from device.

        """
        if not datetime_:
            datetime_ = datetime.datetime.now()

        if datetime_.year < 2000:
            # welp... device has year hardcoded 20xx
            raise ValueError("Device can't set year earlier than 2000")

        dt_cmd = struct.pack(
            ">BBBBBB",
            datetime_.year - 2000,
            datetime_.month,
            datetime_.day,
            datetime_.hour,
            datetime_.minute,
            datetime_.second,
        )
        cmd = b"<SETDATETIME" + dt_cmd + b">>"
        self.connection.reset_buffers()
        result = self.connection.get_exact(cmd, expected=b"", size=1)
        if not result == b"\xaa":
            raise RuntimeError("Unexpected response: {}".format(result))

    def reboot(self) -> None:
        """
        Reboot device.

        Note: Different from power off-on as it changes display to default.

        """
        cmd = b"<REBOOT>>"
        self.connection.write(cmd)

    # To-be-added soon(TM)
    # def _history(self, start_position, size):
    #     # <SPIR[A2][A1][A0][L1][L0]>>
    #     # A2,A1,A0 are three bytes address data, from MSB to LSB.
    #     # The L1,L0 are the data length requested.
    #     L1 is high byte of 16 bit integer and L0 is low byte.
    #     # \xff is end of file?
    #     start = struct.pack(">I", start_position)[1:]
    #     # 2**11 = 2048
    #     size = struct.pack(">H", size)

    #     a = bytearray(start)
    #     b = bytearray(size)
    #     self.connection._write(b"<SPIR" + a + b + b">>")
    #     for i in range(10):
    #         time.sleep(0.1 * (1 + i))
    #         data = self.connection._read()
    #         if len(data) > 0:
    #             break
    #     #         data = self.connection.get(b'<SPIR' + a + b + b'>>')
    #     return data

    # def _all_history(self):
    #     data = b""
    #     read_chunk = 2**11  # 2048
    #     max_size = 2**20  # 1MB?
    #     for start in range(0, max_size, read_chunk):
    #         kb = start / 1024
    #         print("Loading {0:,.0f} kB".format(kb), end="\r")
    #         #             print('Reading', start, end='\r')
    #         tmp = self._history(start, read_chunk)
    #         if len(tmp) == 0:
    #             print("no data")
    #             break
    #         data += tmp
    #         if tmp.count(b"\xff") >= read_chunk * 0.5:
    #             print("End of history")
    #             break
    #     return data
