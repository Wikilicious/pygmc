import csv
import logging
import struct

from ..history import HistoryParser

logger = logging.getLogger("pygmc.device")


class BaseDevice:
    """Base device class which all devices inherit from."""

    def __init__(self, connection):
        """
        Represent a base GMC device.

        Parameters
        ----------
        connection : pygmc.Connection
            An connection interface to the USB device.
        """
        self.connection = connection

        self._flash_memory_size_bytes = 2**20  # 1 MiB
        self._flash_memory_page_size_bytes = 2**11  # 2048 B

        # the config under the hood, initialize empty and lazily create
        self._config = dict()

        # µSv calibration (max_cpm, slope, intercept)
        self._usv_calibration_tuple = tuple()

        # Best effort interpretation from:
        #     https://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=4948
        # self-documenting code to interpret config data
        # type=None means treat byte literally. e.g. b'\x00'[0] -> 0
        # type is a string means struct.unpack type
        self._cfg_spec_map = {
            "Power": {
                "index": 0,
                "size": 1,
                "description": "0=ON, 1=OFF... Backwards for reasons beyond comprehension.",
                "type": None,
            },
            "Alarm": {
                "index": 1,
                "size": 1,
                # Somehow this is not backwards like Power
                "description": "0=OFF, 1=ON",
                "type": None,
            },
            "Speaker": {
                "index": 2,
                "size": 1,
                "description": "0=OFF, 1=ON",
                "type": None,
            },
            "CalibrationCPM_0": {
                "index": 8,
                "size": 2,
                "description": "",
                "type": ">H",
            },
            "CalibrationCPM_1": {
                "index": 14,
                "size": 2,
                "description": "",
                "type": ">H",
            },
            "CalibrationCPM_2": {
                "index": 20,
                "size": 2,
                "description": "",
                "type": ">H",
            },
            "SaveDataType": {
                "index": 32,
                "size": 1,
                "description": "History data; 0=off, 1=CPS, 2=CPM, 3=CPM(avg/hr)",
                "type": None,
            },
            "MaxCPM": {
                "index": 49,
                "size": 2,
                "description": "MaxCPM Hi + Lo Byte",
                "type": ">H",
            },
            "Baudrate": {
                "index": 57,
                "size": 1,
                # coded differently for 300 and 500/600 series
                # see https://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=4948 reply#12
                "description": "see https://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=4948 reply#12",
                "type": None,
            },
            "BatteryType": {
                "index": 56,
                "size": 1,
                "description": "0=rechargeable, 1=non-rechargeable",
                "type": None,
            },
            "ThresholdMode": {
                "index": 64,
                "size": 1,
                "description": "0=CPM, 1=µSv/h, 2=mR/h",
                "type": None,
            },
            "ThresholdCPM": {
                "index": 62,
                "size": 2,
                "description": "",
                "type": ">H",
            },
        }

        # will likely save someone a lot of time
        # heartbeat-on keeps writing to buffer making other functionality un-parsable
        self._heartbeat_off()

        logger.debug("Initialize BaseDevice")

    def _heartbeat_off(self) -> None:
        """
        Turn heartbeat OFF.

        Stop writing data to buffer every second.
        """
        self.connection.write(b"<HEARTBEAT0>>")
        self.connection.reset_buffers()
        logger.debug("Heartbeat OFF")

    def _heartbeat_on(self) -> None:
        """
        Turn heartbeat ON.

        CPS data is automatically written to the buffer every second.
        """
        self.connection.write(b"<HEARTBEAT1>>")
        logger.debug("Heartbeat ON")

    def _read_history_position(self, start_position, chunk_size) -> bytes:
        # http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=4445
        # don't need spir fix because... reset read/write buffer.
        start_s = struct.pack(">I", start_position)[1:]
        size_s = struct.pack(">H", chunk_size)

        cmd = b"<SPIR" + start_s + size_s + b">>"
        data = self.connection.get_exact(cmd, size=chunk_size)

        # MUST reset buffers... or deal with the bug
        # device with bug returns chunk_size + 1
        # if we read chunk_size, then there is one byte left in buffer
        # which will throw off all further commands
        self.connection.reset_buffers()

        return data

    def _parse_cfg(self, cfg_bytes: bytes) -> None:
        """
        Parses config bytes and sets self._config.

        Parameters
        ----------
        cfg_bytes: bytes
            Device <GETCFG>>

        Returns
        -------
        None

        """
        cfg_map = self._cfg_spec_map
        for name, d in cfg_map.items():
            i = d["index"]
            e = i + d["size"]
            raw = cfg_bytes[i:e]

            if d["type"] and d["type"] != "tbd":
                value = struct.unpack(d["type"], raw)[0]
            elif d["type"] is None:
                value = raw[0]
            else:
                logger.warning(f"config={name} not understood")
                value = None

            self._config[name] = value

    def _set_usv_calibration(self, calibrations: list) -> None:
        """
        Set µSv calibration from config.

        See https://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=10435
        User can convert Sievert (an SI unit of ionizing radiation) to Roentgen
        (a legacy/retired/deprecated unit of ionizing radiation)

        Parameters
        ----------
        calibrations: list
            List of tuples(int, float|int) representing max_cpm and uSv.

        Returns
        -------
        None

        """
        usv_range_slope_intercept = []  # max_cpm, slope, intercept

        # insert dummy calibration point to generalize to y=mx+b
        calibrations.insert(0, (0, 0))

        for i in range(len(calibrations) - 1):
            # *_s = start *_e = end
            calib_s = calibrations[i]
            calib_e = calibrations[i + 1]
            logger.debug(f"calib_s={calib_s} calib_e={calib_e}")

            cpm_s = calib_s[0]
            usv_s = calib_s[1]

            cpm_e = calib_e[0]
            usv_e = calib_e[1]

            dy = usv_e - usv_s
            dx = cpm_e - cpm_s

            m = dy / dx  # slope
            b = -(m * cpm_e) + usv_e  # intercept

            # The previous calib may have a max_cpm larger than the current one
            # This is actually the case in the default calibration for GMC-500+
            if cpm_e > cpm_s:
                calib = (cpm_e, m, b)
                usv_range_slope_intercept.append(calib)

        self._usv_calibration_tuple = tuple(usv_range_slope_intercept)

    def get_raw_history(self) -> bytes:
        """
        Get device history data.

        Stops reading when read entire page contains empty data.
        Full 1 MiB read takes ~5 minutes on the slower 57,600 baudrate

        Returns
        -------
        bytes
            Raw history data.

        """
        i = 0
        hist = b""
        for start_position in range(
            0, self._flash_memory_size_bytes, self._flash_memory_page_size_bytes
        ):
            data = self._read_history_position(
                start_position, self._flash_memory_page_size_bytes
            )

            if data.count(b"\xff") == self._flash_memory_page_size_bytes:
                logger.debug("Entire read block '\\xff' stop reading history")
                break
            hist += data

            i += 1
            logger.debug("Read history page {} done".format(i))

        return hist

    def save_history_raw(self, file_path) -> None:
        """
        Save raw device history to file.

        Parameters
        ----------
        file_path: str
            Path to save.

        """
        data = self.get_raw_history()
        with open(file_path, "wb") as f:
            f.write(data)

    def get_history_data(self) -> list:
        """
        Get tidy device memory history in a list of tuples.

        First row is column names.
        Columns: "datetime", "count", "unit", "mode", "reference_datetime", "notes"

        Returns
        -------
        list:
            List of tuples, first row is column names.

        """
        data = self.get_raw_history()
        h = HistoryParser(data=data)
        data = [h.get_columns()]
        data.extend(h.get_data())
        return data

    def save_history_csv(self, file_path: str) -> None:
        """
        Save device history as a CSV file.

        Parameters
        ----------
        file_path: str
            Path to save.

        """
        data = self.get_history_data()

        with open(file_path, "w", newline="") as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=",")
            csv_writer.writerows(data)

    def get_version(self) -> str:
        """
        Get version of device.

        Has a sleep wait to read as spec RFC1801 doesn't specify end char nor byte size.
        i.e. SLOW.

        Returns
        -------
        str
            Device version
        """
        cmd = b"<GETVER>>"
        self.connection.reset_buffers()
        result = self.connection.get_at_least(cmd=cmd, size=7, wait_sleep=0.05)
        return result.decode("utf8")

    def get_serial(self) -> str:
        """Get serial."""
        cmd = b"<GETSERIAL>>"
        self.connection.reset_buffers()
        result = self.connection.get_exact(cmd, size=7)
        return result.hex()

    def get_connection_details(self) -> dict:
        """
        Get connection details from pyserial.

        Returns
        -------
        dict

        """
        return self.connection.get_connection_details()
