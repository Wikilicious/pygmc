import datetime
import logging
import struct
from typing import Generator

from .device import BaseDevice

logger = logging.getLogger("pygmc.devices.spec404")


class DeviceSpec404(BaseDevice):
    """Device class representing an un-documented Spec"""

    def __init__(self, connection):
        """
        Represent a GMC device that doesn't follow RFC1201 nor RFC1801.

        A nod to 404 (page not found) this is a best-effort made-up specification
        for the GMC-800 which claimed to follow RFC1201 as of 2024.

        Parameters
        ----------
        connection : pygmc.Connection
            An connection interface to the USB device.
        """
        super().__init__(connection)

        # Redefine BaseDevice because it's completely different
        self._cfg_spec_map = {
            "Power": {
                # You can communicate with a device while it's off
                "index": 0,
                "size": 1,
                "description": "0=ON, 1=OFF (YES, ZERO MEANS ON.)",
                "type": "B",
            },
            "Save_Mode": {
                "index": 32,
                "size": 1,
                "description": "0=Off, 1=Every-Second, 2=Every-Minute, 3=Every-Hour)",
                "type": "B",
            },
            "Power_Saving_Mode": {
                "index": 44,
                "size": 1,
                "description": "0=Dim, 1=Turns-off, 2=Disabled (why is 0 not disable?)",
                "type": "B",
            },
            "LCD_Backlight_Level": {
                "index": 53,
                "size": 1,
                "description": "Screen brightness. 0=DIMMEST (but still on), 30=Max",
                "type": "B",
            },
            "LED": {
                "index": 60,
                "size": 1,
                "description": "LED counter indicator. 0=OFF, 1=ON",
                "type": "B",
            },
            "Fast_Estimate_Time": {
                "index": 69,
                "size": 1,
                "description": "3=Dynamic, (60, 30, 20, 10, 5)=Seconds",
                "type": "B",
            },
            "Alarm_Volume": {
                "index": 71,
                "size": 1,
                "description": "Alarm volume. 0=OFF, 15=Max",
                "type": "B",
            },
            "Tube_Voltage": {  # ?
                "index": 72,
                "size": 1,
                "description": "Tube voltage level. (default=44)",
                "type": "B",
            },
            "Calibration_CPM_1": {
                "index": 73,
                "size": 4,
                "description": "",
                "type": ">I",
            },
            "Calibration_CPM_2": {
                "index": 77,
                "size": 4,
                "description": "",
                "type": ">I",
            },
            "Calibration_CPM_3": {
                "index": 81,
                "size": 4,
                "description": "",
                "type": ">I",
            },
            "Calibration_CPM_4": {
                "index": 85,
                "size": 4,
                "description": "",
                "type": ">I",
            },
            "Calibration_CPM_5": {
                "index": 89,
                "size": 4,
                "description": "",
                "type": ">I",
            },
            "Calibration_CPM_6": {
                "index": 93,
                "size": 4,
                "description": "",
                "type": ">I",
            },
            "Calibration_USV_1": {
                "index": 97,
                "size": 4,
                "description": "",
                "type": ">f",
            },
            "Calibration_USV_2": {
                "index": 101,
                "size": 4,
                "description": "",
                "type": ">f",
            },
            "Calibration_USV_3": {
                "index": 105,
                "size": 4,
                "description": "",
                "type": ">f",
            },
            "Calibration_USV_4": {
                "index": 109,
                "size": 4,
                "description": "",
                "type": ">f",
            },
            "Calibration_USV_5": {
                "index": 113,
                "size": 4,
                "description": "",
                "type": ">f",
            },
            "Calibration_USV_6": {
                "index": 117,
                "size": 4,
                "description": "",
                "type": ">f",
            },
            "Click_Sound": {
                "index": 121,
                "size": 1,
                "description": "Counter clicking sound. 0=OFF, 1=ON",
                "type": "B",
            },
            "Speaker_Volume": {
                "index": 122,
                "size": 1,
                "description": "Volume (for voice?). 0=OFF, 15=Max",
                "type": "B",
            },
            "Vibration": {
                "index": 123,
                "size": 1,
                "description": "Vibration (for alarm?) . 0=OFF, 1=ON",
                "type": "B",
            },
            "Alarm_CPM": {
                "index": 125,
                "size": 4,
                "description": "Alarm threshold",
                "type": ">I",
            },
            "Theme": {
                "index": 129,
                "size": 1,
                "description": "Display theme 0=dark-mode-ON (0 means on, ugh)",
                "type": "B",
            },
        }

    def get_cpm(self) -> int:
        """
        Get CPM counts-per-minute data.

        Returns
        -------
        int
            Counts per minute
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
                (self._config["Calibration_CPM_1"], self._config["Calibration_USV_1"]),
                (self._config["Calibration_CPM_2"], self._config["Calibration_USV_2"]),
                (self._config["Calibration_CPM_3"], self._config["Calibration_USV_3"]),
                (self._config["Calibration_CPM_4"], self._config["Calibration_USV_4"]),
                (self._config["Calibration_CPM_5"], self._config["Calibration_USV_5"]),
                (self._config["Calibration_CPM_6"], self._config["Calibration_USV_6"]),
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
