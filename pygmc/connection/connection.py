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

logger = logging.getLogger("pygmc.connection")


class Connection:
    """
    Represent a connection to a GMC device.

    Either user provided parameters or a best-guess auto-connect.
    Effectively a wrapper for pyserial for GMC specific tasks.
    """

    def __init__(self, timeout=5):
        """
        Represent a connection to a GMC device.

        Parameters
        ----------
        timeout : int, optional
            serial connection timeout, seconds, by default 5
        """
        # on windows, it's usually COM3
        # on linux, it's usually /dev/ttyUSB0
        # http://www.gqelectronicsllc.com/downloads/ to look for updates?
        # AIR-760 has no protocol docs :(
        # baudrates from GQ-RFC1201 & GQ-RFC1801
        # http://www.gqelectronicsllc.com/download/GQ-RFC1201.txt
        # http://www.gqelectronicsllc.com/download/GQ-RFC1801.txt
        self._baudrates = [
            115200,
            57600,
            38400,
            28800,
            19200,
            14400,
            9600,
            4800,
            2400,
            1200,
        ]
        logger.debug(f"Connection timeout={timeout}")
        self._timeout = timeout  # seconds
        self._baudrate = 115200  # default
        self._con = None

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

    def _test_con(self) -> bool:
        """
        Test connection cavemen style... Write cmd and check if there was a response.

        Not sure at all if this is a good test.
        No prescribed method of confirming a GMC device in specs :(

        Would've liked to use <GETVER>> as test but...
        spec GQ-RFC1201 says return is 14 bytes.
        spec GQ-RFC1801 doesn't specify.
        Picking <GETSERIAL>> as it's specified in both specs; 7 bytes

        Returns
        -------
        bool
            True: validated connection. False: unexpected response.
        """
        self.reset_buffers()
        try:
            serial_number = self.get_exact(b"<GETSERIAL>>", size=7)
        except Exception as e:
            # Unsure of exception types.
            logger.warning(f"{e}", exc_info=True)
            return False
        # timeout error if wrong
        if len(serial_number) == 7:
            # Not 100% sure... no prescribed method of confirming
            # we're connected to a GMC device in specs
            logger.debug(f"Test connection serial: {serial_number}")
            return True
        else:
            logger.warning(f"Unexpected response: {serial_number}")
            return False

    def _check_baudrate(self, con):
        # perhaps always turn off heartbeat when connecting
        # because that messes with the output buffer
        con.reset_input_buffer()
        con.reset_output_buffer()
        cmd = b"<GETSERIAL>>"
        con.write(cmd)
        con.flush()
        # This is to resolve pyserial breaking change. See __init__ above.
        params = {self._read_until_param_name: b"", "size": 7}
        result = con.read_until(**params)
        if len(result) == 7:
            logger.debug("Baudrate successfully wrote and read data.")
            return True
        logger.debug(f"Baudrate check returned unexpected result: {result}")
        return False

    def _find_correct_baudrate(self, port: str) -> bool:
        """
        Given a successful port, attempt/confirm a baudrate works.

        Parameters
        ----------
        port : str
            Device port

        Returns
        -------
        bool
            True: successful connection
            False: some error
        """
        for br in self._baudrates:
            logger.debug(f"Checking baudrate={br} for port={port}")
            try:
                # A successful connection doesn't mean the baudrate can read/write.
                con = serial.Serial(port, baudrate=br, timeout=1)
                if self._check_baudrate(con):
                    con.close()
                    self._baudrate = br
                    logger.debug(f"Baudrate={br} wrote and read data.")
                    return True
                con.close()
            except (OSError, serial.SerialException) as e:
                # SerialException
                # In case the device can not be found or can not be configured.
                logger.warning(f"{e}", exc_info=True)
        return False

    @staticmethod
    def _get_available_usb_devices(regexp=None, include_links=True) -> list:
        """
        Get all available USB devices.

        Parameters
        ----------
        regexp : None | str, optional
            Search for ports using a regular expression. Port name, description and
            hardware ID are searched.
            hardwareID example ('USB VID:PID=1A86:7523 LOCATION=2-1')
            Default=None, find all.
        include_links : bool, optional
            include symlinks under /dev when they point to a serial port, by default True

        Returns
        -------
        list
            available ports, type [serial.tools.list_ports_linux.SysFS]
        """
        logger.debug(
            f"_get_available_usb_devices(regexp={regexp}, include_links={include_links})"
        )
        if not regexp:
            _ports = serial_list_ports.comports(include_links=include_links)
        else:
            # cast as list because it's a generator and I want an easy return type
            # How many USB devices could a user possibly have?
            _ports = list(
                serial_list_ports.grep(regexp=regexp, include_links=include_links)
            )

        logger.debug(f"All ports found: {[(x.device, x.hwid) for x in _ports]}")
        ports = []
        for port in _ports:
            hwid = port.hwid
            # Filter out non-usb ports
            if hasattr(hwid, "startswith") and hwid.startswith("USB"):
                # e.g. hwid='USB VID:PID=1A86:7523 LOCATION=2-1'
                ports.append(port)

        logger.debug(
            f"USB ports/dev-devices found: {[(x.device, x.hwid) for x in ports]}"
        )
        return ports

    def connect(
        self,
        port=None,
        baudrate=None,
        vid=None,
        pid=None,
        description=None,
        hardware_id=None,
    ) -> None:
        """
        Connect to device.

        If all parameters are None, _auto_connect() flow is used which attempts to
        connect to all available ports.
        If ANY parameter is given; it refines the search, any matches are considered.
        Parameters are used as an OR search.

        Parameters
        ----------
        port : str | None, optional
            Exact port (device dev path / com port) e.g. '/dev/ttyUSB0'
            If port is specified, the following kwargs are ignored: vid, pid,
            description, hardware_id.
        baudrate: int | None
            Device baudrate. Leave None to auto-detect baudrate. Only applicable when
            port is specified.
        vid : str | None, optional
            Device vendor ID as hex, by default None
        pid : str | None, optional
            Device product ID as hex, by default None
        description : str | None, optional
            Device description, by default None
        hardware_id : str | None, optional
            Device hwid, by default None
            e.g. 'USB VID:PID=1A86:7523 LOCATION=2-1'
            Use hex for vid:pid input

        Raises
        ------
        ConnectionError
            _description_
        """
        if port and baudrate:
            self.connect_exact(port, baudrate)
        elif port:
            works = self._find_correct_baudrate(port=port)
            if works:
                self._con = serial.Serial(
                    port=port, baudrate=self._baudrate, timeout=self._timeout
                )
                logger.info(f"Connected to {self._con.port}")
            else:
                raise ConnectionError(f"Unable to connect to: {port}")

        else:
            # ANY match, first match, becomes the device
            inputs = [vid, pid, description, hardware_id]
            if not any(v is not None for v in inputs):
                # no user info to go on... let's see what we can do...
                ports = self._get_available_usb_devices()
            else:
                regexp = "|".join([x for x in inputs if x])
                logger.debug(f"serial.tools.list_ports.grep({regexp})")
                ports = self._get_available_usb_devices(regexp=regexp)

            works = False
            for avail_port in ports:
                port = avail_port.device  # e.g. /dev/ttyUSBO
                logger.debug(port)
                works = self._find_correct_baudrate(port=port)
                if works:
                    self._con = serial.Serial(
                        port=port, baudrate=self._baudrate, timeout=self._timeout
                    )
                    logger.info(f"Connected to {self._con.port}")
                    break
            if not works:
                raise ConnectionError()
            logger.info(f"Connected: {self._con}")

    def connect_exact(self, port, baudrate) -> None:
        """
        Connect with exact user provided parameters.

        No searching port, no searching baudrate. i.e. fast.

        Parameters
        ----------
        port : str
            Port. e.g. linux /dev/ttyUSB0 or windows COM3
        baudrate : int
            Baudrate e.g. 115200
        """
        logger.debug(f"Exact connect attempt: port={port} baudrate={baudrate}")
        logger.log(level=9, msg="User knows their #2")  # level lower than DEBUG=10
        self._con = serial.Serial(port=port, baudrate=baudrate, timeout=self._timeout)
        logger.info(f"Connected: {self._con}")

    def connect_user_provided(self, connection) -> None:
        """
        User does their own thing and gives a serial.Serial like class.

        Parameters
        ----------
        connection : serial.Serial
            A serial.Serial like class (pyserial)
        """
        # instance of serial.Serial
        logger.log(level=9, msg="User knows their #2^2")  # level lower than DEBUG=10
        logger.info(f"User provided connection: {connection}")
        self._con = connection  # good luck
        logger.info(f"Connected: {self._con}")

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

        logger.debug(f"response={result}")
        return result

    def read_until(self, expected=b"", size=None) -> bytes:
        r"""
        Read device data until expected LF is reached or expected result size is reached.

        Waits until conditions met or timeout.
        Some data has '\n' which causes reading to stop.
        default changed from b'\n' to b''

        Parameters
        ----------
        expected : bytes, optional
            Expected end character, by default b''
        size : None | int, optional
            Length of expected bytes, by default None

        Returns
        -------
        bytes
            Device response
        """
        logger.debug(f"read_until(expected={expected}, size={size})")
        # This is to resolve pyserial breaking change. See __init__ above.
        params = {self._read_until_param_name: expected, "size": size}
        result = self._con.read_until(**params)
        logger.debug(f"response={result}")
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

    def get_exact(self, cmd, expected=b"", size=None) -> bytes:
        """
        Write and read exact.

        Write command to device, provide expected LF or size (bytes),
        wait until either LF, size, or timeout is reached,
        then return device response.

        Parameters
        ----------
        cmd : bytes
            Write command e.g. <GETVER>>
        expected : bytes, optional
            Expected end char, by default b''
        size : int | None, optional
            Expected response size, by default None

        Returns
        -------
        bytes
            Device response
        """
        logger.debug(f"get_exact(cmd={cmd}, expected={expected}, size={size})")
        self.write(cmd)
        result = self.read_until(expected=expected, size=size)
        return result
