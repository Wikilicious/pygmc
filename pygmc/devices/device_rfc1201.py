import datetime
import logging
import struct
from typing import Generator, Tuple

from .device import BaseDevice

logger = logging.getLogger("pygmc.devices.rfc1201")


class DeviceRFC1201(BaseDevice):
    """Device class representing Spec RFC1201"""

    def __init__(self, connection):
        """
        Represent a GMC device.

        Can be used with:
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
                    # see https://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=4948
                    # reply#12
                    "description": "64=1200,160=2400,208=4800,232=9600,240=14400,"
                    "244=19200,248=28800,250=38400,252=57600,254=115200",
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
        Get CPM counts-per-minute data.

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
                # valid range calibration exit condition
                break

        # if usv is still None... extrapolate from last _usv_calibration_tuple point
        # which is implicitly the highest cpm calibration via _set_usv_calibration
        if usv_h is None:
            calib_max_cpm, calib_slope, calib_intercept = self._usv_calibration_tuple[-1]
            usv_h = cpm * calib_slope + calib_intercept

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
        Get device voltage.

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
        cfg_bytes = self.connection.get_exact(cmd, expected=b"", size=256)
        self._parse_cfg(cfg_bytes)
        return self._config

    def get_temp(self) -> float:
        """
        Get device temperature in Celsius.

        Notes
        -----
        Seems a bit temperamental. GMC-300S initially returned 0, then 86, then
        stabilized to 20.7 (which is about the room temperature when measured).
        i.e. call the method a few times until it stabilizes.

        Returns
        -------
        float
            Device temperature is celsius.

        """
        result = self.connection.get_exact(b"<GETTEMP>>", size=4)
        sign = 1
        if result[2] != 0:
            sign = -1
        temp = sign * float("{}.{}".format(result[0], result[1]))
        return temp

    def heartbeat_live(self, count=60) -> Generator[int, None, None]:
        """
        Get live CPS data, as a generator. i.e. yield (return) CPS as available.

        Parameters
        ----------
        count : int, optional
            How many CPS counts to return (default=60). Theoretically, 1count = 1second.
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
