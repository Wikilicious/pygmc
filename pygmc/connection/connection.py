"""
Represent a USB connection to a GMC.

This is the communication class.
"""
import inspect
import logging
import time

# pypi
import serial
from serial.tools import list_ports as serial_list_ports

from .const import BAUDRATES

logger = logging.getLogger("pygmc.connection")


class Connection:
    """
    Represent a connection to a GMC device.

    A wrapper around pyserial with common operations for a GMC device.
    """

    def __init__(self, port, baudrate, timeout=5, serial_connection=None):
        """
        Represent a connection to a GMC device.

        Parameters
        ----------
        port: str
            Dev device, port, com to connect to.
            On linux, it's usually /dev/ttyUSB0 and on windows, it's usually COM3.
        baudrate: int
            Speed of communication over serial USB. Must be a compatible value.
        timeout : int, optional
            Serial connection timeout, seconds, by default 5
        serial_connection: serial.Serial
            An initialized Serial instance.
        """
        # pyserial has a breaking change from 3.4 to 3.5
        # TypeError:
        #     SerialBase.read_until() got an unexpected keyword argument 'expected'
        # 'terminator' for serial==3.4, 'expected' for serial==3.5
        # Doing ape logic below to resolve pyserial smooth brain breaking change
        try:
            s = inspect.signature(serial.SerialBase.read_until)
            params = list(s.parameters.keys())  # e.g. ['self', 'terminator', 'size']
            self._read_until_param_name = params[
                1
            ]  # 'terminator' for serial==3.4, 'expected' for serial==3.5
        except Exception as e:  # noqa
            logger.exception("Unable to resolve read_until param name")
            self._read_until_param_name = "expected"  # just guess

        # The connection
        if serial_connection:
            logger.debug("User provided serial connection.")
            self._con = serial_connection
        else:
            if baudrate not in BAUDRATES:
                logger.error(f"Input baudrate={baudrate} not in known compatible rates.")
                logger.error(f"Known compatible baudrates={BAUDRATES}")
                logger.error("To force baudrate, pass in your own serial_connection")
            self._con = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)

    def __repr__(self):
        """Use pyserial __repr__"""
        if self._con:
            return self._con.__repr__()
        return super().__repr__()

    def __str__(self):
        """Use pyserial __repr__"""
        # maybe a nicer str?
        return str(self.__repr__())

    def get_connection_details(self) -> dict:
        """
        Get connection details.

        Values of None means not available or not applicable.

        Returns
        -------
        dict

        """
        deets = {
            "port": None,
            "baudrate": None,
            "is_open": None,
            "in_waiting": None,
            "out_waiting": None,
            "name": None,
            "timeout": None,
        }

        for key in list(deets):
            if hasattr(self._con, key):
                deets[key] = getattr(self._con, key)

        usb_info = {
            "description": None,
            "hwid": None,
            "location": None,
            "pid": None,
            "usb_device_path": None,
            "vid": None,
        }

        deets_port = deets["port"]
        ports = []
        port_info = None
        if deets_port:
            ports = list(
                serial_list_ports.grep(regexp=f"^{deets_port}$", include_links=True)
            )
        if deets_port is None and len(ports) != 1:
            # port_info will be None which won't hasattr i.e. returns all None.
            logger.warning(f"Unable to identify USB info for {deets_port}")
        else:
            port_info = ports[0]

        for key in list(usb_info):
            if hasattr(port_info, key):
                usb_info[key] = getattr(port_info, key)

        deets.update(usb_info)

        return deets

    def close_connection(self) -> None:
        """Close connection."""
        if self._con is None:
            pass
        else:
            logger.info(f"Close connection: {self._con}")
            self._con.close()

    def reset_buffers(self) -> None:
        """
        Reset input & output buffers on pyserial connection.

        reset_input_buffer(): Clear input buffer, discarding all that is in the buffer.
        reset_output_buffer(): Clear output buffer, aborting the current output and
        discarding all that is in the buffer.
        """
        # Clear input buffer, discarding all that is in the buffer.
        logger.debug("reset_input_buffer")
        self._con.reset_input_buffer()
        # Clear output buffer,
        # aborting the current output and discarding all that is in the buffer.
        logger.debug("reset_output_buffer")
        self._con.reset_output_buffer()

    def write(self, cmd: bytes) -> None:
        """
        Write command to device.

        Parameters
        ----------
        cmd : bytes
            Write command e.g. <GETVER>>
        """
        logger.debug(f"write='{cmd}'")
        self._con.write(cmd)
        self._con.flush()

    def read(self, wait_sleep=0.3) -> bytes:
        """
        Read all available data.

        Which may be incomplete. (noob/newbie method)

        Parameters
        ----------
        wait_sleep : float, optional
            Time to sleep to give device time to write, by default 0.3

        Returns
        -------
        bytes
            Device response
        """
        # return everything currently in device buffer
        # i.e. may be incomplete so wait a bit before read
        time.sleep(wait_sleep)
        # in pyserial==3.5 method added .read_all()
        # Read all bytes currently available in the buffer of the OS.
        # BUT... not available in pyserial==3.4
        # ADDITIONALLY, https://pyserial.readthedocs.io/en/latest/index.html
        # says latest yet refers to 3.4
        # SO... lets make this requirement 3.4 and manually implement read_all()
        if hasattr(self._con, "read_all"):
            logger.debug("read_all")
            result = self._con.read_all()
        else:
            # in_waiting - Return the number of bytes currently in the input buffer.
            logger.debug("read(in_waiting)")
            result = self._con.read(self._con.in_waiting)

        if len(result) <= 50:
            logger.debug(f"response={result}")
        else:
            # reading history data pollutes the logs with T.M.I.
            # seeing response is as easy as: logging.basicConfig(level=9)
            msg = f"response-len={len(result)} (set log level=9 to log full response)"
            logger.debug(msg)
            logger.log(level=9, msg=f"response={result}")

        return result

    def read_until(self, size=None, expected=b"") -> bytes:
        r"""
        Read device data until expected LF is reached or expected result size is reached.

        Waits until conditions met or timeout.
        Some data has '\n' which causes reading to stop.
        default changed from b'\n' to b''

        Parameters
        ----------
        size : None | int, optional
            Length of expected bytes, by default None
        expected : bytes, optional
            Expected end character, by default b''

        Returns
        -------
        bytes
            Device response
        """
        logger.debug(f"read_until(size={size}, expected={expected})")
        # This is to resolve pyserial breaking change. See __init__ above.
        params = {self._read_until_param_name: expected, "size": size}
        result = self._con.read_until(**params)
        if len(result) <= 50:
            logger.debug(f"response={result}")
        else:
            # reading history data pollutes the logs with T.M.I.
            # seeing response is as easy as: logging.basicConfig(level=9)
            msg = f"response-len={len(result)} (set log level=9 to log full response)"
            logger.debug(msg)
            logger.log(level=9, msg=f"response={result}")
        return result

    def read_at_least(self, size, wait_sleep=0.05) -> bytes:
        """
        Read at least <size> bytes then wait <wait_sleep> and read the buffer.

        i.e. Wait as long as needed to get at-least <size> bytes then wait <wait_sleep>
        seconds and read whatever else is ready in the buffer.

        Parameters
        ----------
        size: int
            Minimum size expected to read or timeout.
        wait_sleep: float | int
            Time to wait in seconds to check if there's anything remaining in the buffer.

        Notes
        -----
        This method resets the input & output buffers after; incase there was extra info
        that would've been added to the buffers.
        This is useful for ill-defined specs where there is no exact size prescribed and
        not waiting enough may result in empty/partial response and waiting too long is
        wasteful if the response was ready quickly.

        Returns
        -------
        bytes

        """
        logger.debug(f"read_at_least(size={size}, wait_sleep={wait_sleep})")

        # read until size or timeout
        min_size_result = self.read_until(size=size, expected=b"")
        extra_result = self.read(wait_sleep=wait_sleep)
        # add up results like str math
        result = min_size_result + extra_result

        if len(result) <= 50:
            logger.debug(f"combined-response={result}")
        else:
            msg = f"combined-response-len={len(result)} "
            msg += "(set log level=9 to log full response)"
            logger.debug(msg)
            logger.log(level=9, msg=f"combined-response={result}")
        self.reset_buffers()

        return result

    def get(self, cmd, wait_sleep=0.3) -> bytes:
        """
        Write command to device and get response.

        Only use in development/learning environment.
        May give incomplete/empty response if device is busy.

        Parameters
        ----------
        cmd : bytes
            Write command e.g. <GETVER>>
        wait_sleep : float, optional
            Time to sleep to give device time to write, by default 0.3

        Returns
        -------
        bytes
            Device response
        """
        logger.debug(f"get(cmd={cmd}, wait_sleep={wait_sleep})")
        self.write(cmd)
        result = self.read(wait_sleep=wait_sleep)
        logger.debug(f"response={result}")
        return result

    def get_at_least(self, cmd, size, wait_sleep=0.05) -> bytes:
        """
        Write cmd, read at least <size> bytes then wait <wait_sleep> and read the buffer.

        Parameters
        ----------
        cmd : bytes
            Write command e.g. <GETVER>>
        size: int
            Minimum size expected to read or timeout.
        wait_sleep : float, optional
            Time to sleep (seconds) to give device time to write, by default 0.05

        Notes
        -----
        The reason for this method is due to the unspecified expected length in GETVER.
        We write the command then we must wait for the device to write the response.
        For GETVER on GMC300S:
        .get() wait=0.1s, two-hundred loops took 20.4 seconds and failed 13%
        .get_at_least() wait=0.05s, two-hundred loops took 15.3 seconds and 0% failed.

        Returns
        -------
        bytes
            Device response
        """
        logger.debug(f"get(cmd={cmd}, wait_sleep={wait_sleep})")
        self.write(cmd)
        result = self.read_at_least(size=size, wait_sleep=wait_sleep)
        logger.debug(f"response={result}")
        return result

    def get_exact(self, cmd, size=None, expected=b"") -> bytes:
        """
        Write and read exact.

        Write command to device, provide expected LF or size (bytes),
        wait until either LF, size, or timeout is reached,
        then return device response.

        Parameters
        ----------
        cmd : bytes
            Write command e.g. <GETVER>>
        size : int | None, optional
            Expected response size, by default None
        expected : bytes, optional
            Expected end char, by default b''

        Returns
        -------
        bytes
            Device response
        """
        logger.debug(f"get_exact(cmd={cmd}, size={size}, expected={expected})")
        self.write(cmd)
        result = self.read_until(expected=expected, size=size)
        return result
