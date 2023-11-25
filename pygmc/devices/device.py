import logging
import struct

logger = logging.getLogger("pygmc.device")


class BaseDevice:
    def __init__(self, connection):
        """
        Represent a base GMC device.

        Can be used with:
        GMC-300, GMC-320, GMC-500, GMC-500+, GMC-600, GMC-600+

        Parameters
        ----------
        connection : pygmc.Connection
            An connection interface to the USB device.
        """
        self.connection = connection

        # the config under the hood, initialize empty and lazily create
        self._config = dict()

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
                "description": "1=Once per minute?",
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

    def _heartbeat_on(self) -> None:
        """
        Turn heartbeat ON.

        CPS data is automatically written to the buffer every second.
        """
        self.connection.write(b"<HEARTBEAT1>>")
        logger.debug("Heartbeat ON")

    def _heartbeat_off(self) -> None:
        """
        Turn heartbeat OFF.

        Stop writing data to buffer every second.
        """
        self.connection.write(b"<HEARTBEAT0>>")
        self.connection.reset_buffers()
        logger.debug("Heartbeat OFF")

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
        result = self.connection.get(cmd)
        return result.decode("utf8")

    def get_serial(self) -> str:
        """Get serial."""
        cmd = b"<GETSERIAL>>"
        self.connection.reset_buffers()
        result = self.connection.get_exact(cmd, size=7)
        return result.hex()
