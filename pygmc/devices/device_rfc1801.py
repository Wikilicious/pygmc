import datetime
import getpass
import logging
import struct
from typing import Generator, Tuple

from .device import BaseDevice

logger = logging.getLogger("pygmc.devices.rfc1801")


class DeviceRFC1801(BaseDevice):
    """Device class representing Spec RFC1801"""

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

    def get_usv_h(self, cpm=None) -> float:
        """
        Get µSv/h as is displayed by the device. See notes below.

        cpm: int | None
            Counts per minute to be converted to µSv/h.
            Default=None polls device for live cpm to convert.
            If cpm is provided, user input is used instead.

        Notes
        -----
        Uses device calibration config.
        GQ does not have an official source documentation for device configuration nor
        cpm-to-µSv/h formula. A revision firmware update by GQ may change the config
        bytes and is often not announced.
        Treat the output as a best effort convenience.

        Returns
        -------
        float
            µSv/h

        """
        if cpm is None:
            cpm = self.get_cpm()

        # lazily load config... i.e. don't load it until it's needed.
        if not self._config:
            self.get_config()

        if not self._usv_calibration_tuple:
            calibrations = [
                (self._config["CalibrationCPM_0"], self._config["Calibration_uSv_0"]),
                (self._config["CalibrationCPM_1"], self._config["Calibration_uSv_1"]),
                (self._config["CalibrationCPM_2"], self._config["Calibration_uSv_2"]),
            ]
            self._set_usv_calibration(calibrations)

        usv_h = None
        for calib in self._usv_calibration_tuple:
            calib_max_cpm, calib_slope, calib_intercept = calib
            if cpm <= calib_max_cpm:
                usv_h = cpm * calib_slope + calib_intercept
                break

        # if usv is still None... extrapolate from last _usv_calibration_tuple point
        # which is implicitly the highest cpm calibration via _set_usv_calibration
        if usv_h is None:
            calib_max_cpm, calib_slope, calib_intercept = self._usv_calibration_tuple[-1]
            usv_h = cpm * calib_slope + calib_intercept

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
        total = 0
        for i, cps in enumerate(self.heartbeat_live(count=count)):
            if cps > max_:
                max_ = cps
            total += cps
            # more than 4 digits for cps is scary... but let's stick to specs
            # From https://www.gqelectronicsllc.com/support/GMC_Selection_Guide.htm
            # highest cpm value is "999,999" (a strange number, unlike 65,535)
            # perhaps due to screen width limitations. let's use same for cps
            # 10 spaces (with commas) per sec... like 3 years
            # total uses 11 spaces... if you're doing more than 10 cps for three years
            # ...

            # Why the leading empty space?
            # Because the cursor blinker takes up one space and blocks view.
            msg = f" cps={cps:<7,} | max={max_:<7,} | total={total:<11,} | loop={i:<10,}"
            print(msg, end="\r")  # Carriage return - update line we just printed
        # Why extra print \n? Because \r at end causes prompt to end-up shifted at end
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

        if datetime_.year < 2000 or datetime_.year >= 3000:
            # welp... device has year hardcoded 20xx
            raise ValueError("Device has year hardcoded 20xx can't set given year.")

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

    def set_wifi_on(self) -> None:
        """Set WiFi On"""
        cmd = b"<WiFiON>>"
        result = self.connection.get_exact(cmd, size=1)
        if result != b"\xaa":
            raise RuntimeError("Unexpected response: {}".format(result))

    def set_wifi_off(self) -> None:
        """Set WiFi Off"""
        cmd = b"<WiFiOFF>>"
        result = self.connection.get_exact(cmd, size=1)
        if result != b"\xaa":
            raise RuntimeError("Unexpected response: {}".format(result))

    def set_wifi_ssid(self, ssid, bytes_encoding: str = "utf8") -> None:
        r"""
        Set WiFi SSID (Access point name)

        Parameters
        ----------
        ssid: str
            WiFi SSID access point name.
        bytes_encoding: str
            Encoding to cast to bytes. Realize it's not about the WiFi spec it's about
            the GQ & ESP8266 spec. (undocumented in GQ-RFC1801)

        Raises
        ------
        RuntimeError:
            GQ spec specifies a b"\xaa" response for success.
            RuntimeError for Unexpected response.

        """
        cmd = b"<SETSSID" + bytes(ssid, encoding=bytes_encoding) + b">>"
        result = self.connection.get_exact(cmd, size=1)
        if result != b"\xaa":
            raise RuntimeError("Unexpected response: {}".format(result))

    def set_wifi_password(self, password=None, bytes_encoding: str = "utf8"):
        r"""
        Set WiFi password

        Parameters
        ----------
        password: str | None
            Set WiFi password. Default=None prompts the user with interactive Python
            built-in getpass; to discretely input the variable. Optionally, the user can
            use the parameter to set the variable with their own method.
        bytes_encoding: str
            Encoding to cast to bytes. Realize it's not about the WiFi spec it's about
            the GQ & ESP8266 spec. (undocumented in GQ-RFC1801)

        Raises
        ------
        RuntimeError:
            GQ spec specifies a b"\xaa" response for success.
            RuntimeError for Unexpected response.

        """
        if password is None:
            # enter password via Python's getpass built-in library
            password = getpass.getpass()
        cmd = b"<SETWIFIPW" + bytes(password, encoding=bytes_encoding) + b">>"
        # don't log usb write command
        self.connection.write(cmd, log=False)
        # confirm success
        result = self.connection.read_until(size=1)
        if result != b"\xaa":
            raise RuntimeError("Unexpected response: {}".format(result))

    def set_gmcmap_user_id(self, user_id: str) -> None:
        r"""
        Set User-Id for gmcmap.com

        See: https://gmcmap.com/

        Parameters
        ----------
        user_id: str
            User-Id on gmcmap.com

        Raises
        ------
        RuntimeError:
            GQ spec specifies a b"\xaa" response for success.
            RuntimeError for Unexpected response.

        """
        cmd = b"<SETUSERID" + bytes(user_id, encoding="utf8") + b">>"
        result = self.connection.get_exact(cmd, size=1)
        if result != b"\xaa":
            raise RuntimeError("Unexpected response: {}".format(result))

    def set_gmcmap_counter_id(self, counter_id: str):
        r"""
        Set Counter-Id for currently connected GQ GMC for gmcmap.com

        Parameters
        ----------
        counter_id: str
            Counter-Id for gmcmap.com

        Raises
        ------
        RuntimeError:
            GQ spec specifies a b"\xaa" response for success.
            RuntimeError for Unexpected response.

        """
        cmd = b"<SETCOUNTERID" + bytes(counter_id, encoding="utf8") + b">>"
        result = self.connection.get_exact(cmd, size=1)
        if result != b"\xaa":
            raise RuntimeError("Unexpected response: {}".format(result))
