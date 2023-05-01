import glob
import sys
import platform
import time
import logging
import typing

# pypi
import serial


logger = logging.getLogger("pygmc.connection")


class Connection:
    def __init__(self, port=None, baudrate=None, timeout=5):
        self._port = port
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
        self._baudrate = baudrate
        self._timeout = timeout
        self.con = None
        self._ver = None
        self._device_serial_number = None

    def _get_available_ports(self):
        # https://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python
        """Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
        """
        if sys.platform.startswith("win"):
            ports = ["COM%s" % (i + 1) for i in range(256)]
        elif sys.platform.startswith("linux") or sys.platform.startswith("cygwin"):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob("/dev/tty[A-Za-z]*")
        elif sys.platform.startswith("darwin"):
            ports = glob.glob("/dev/tty.*")
        else:
            raise EnvironmentError("Unsupported platform")

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)

            except (OSError, serial.SerialException) as e:
                if "FileNotFoundError" in str(e):
                    # nothing  here
                    pass
                elif "PermissionError" in str(e):
                    print(
                        "PermissionError opening port: {} - Likely connected somewhere else...".format(
                            port
                        )
                    )
        return result

    def _default_port(self):
        system = platform.system()
        if system == "Windows":
            return "COM3"
        else:
            return "/dev/ttyUSB0"

    def _test_con(self):
        # UGH! Would've liked to use <GETVER>> as test but...
        # spec GQ-RFC1201 says return is 14 bytes.
        # spec GQ-RFC1801 doesn't specify
        # Don't want to do dumb sleep and slow user down.
        # Picking <GETSERIAL>> as it's specified in both specs; 7 bytes

        self.reset_buffers()
        serial_number = self.get_exact(b"<GETSERIAL>>", size=7)
        # timeout error if wrong
        if len(serial_number) > 0:
            # Not 100% sure... no prescribed method of confirming
            # we're connected to a GMC device in specs
            self._device_serial_number = serial_number
            return True
        else:
            return False

    def _find_correct_baudrate(self):
        for br in self._baudrates:
            self._baudrate = br
            try:
                self.con = serial.Serial(self._port, baudrate=br, timeout=self._timeout)
            except (OSError, serial.SerialException) as e:
                self.con = None
                self._baudrate = None
                # make this DEBUG logging
                print(e)
                return False
            if not self._test_con():
                self.con.close()
                print("con attempt failed")
                self.con = None
            else:
                return True
        return False

    def _auto_connect_flow(self):
        # happy path - the default params work
        self._port = self._default_port()
        connected = self._find_correct_baudrate()
        # non-happy path... connected to another port?
        for port in self._get_available_ports():
            self._port = port
            connected = self._find_correct_baudrate()
            if connected:
                break

    def connect(self):
        if self._baudrate is not None and self._port is not None:
            print("wow user knows their #2")
            self.con = serial.Serial(
                self._port, baudrate=self._baudrate, timeout=self._timeout
            )
            if not self._test_con():
                raise ConnectionError
        elif self._port is not None:
            print("have port find baud")
            self._find_correct_baudrate()
        else:
            print("have nada")
            self._auto_connect_flow()
        if self.con is None:
            self._baudrate = None
            self._port = None
            raise ConnectionError
        else:
            print(
                "Connected to port {} with baudrate {}".format(self._port, self._baudrate)
            )

    def close_connection(self):
        if self.con is None:
            pass
        else:
            self.con.close()
            self._device_serial_number = None
            self._baudrate = None
            self._port = None

    def reset_buffers(self):
        # Clear input buffer, discarding all that is in the buffer.
        self.con.reset_input_buffer()
        # Clear output buffer, aborting the current output and discarding all that is in the buffer.
        self.con.reset_output_buffer()

    def write(self, cmd):
        self.con.write(cmd)
        self.con.flush()

    def read(self, wait_sleep=0.1):
        # return everything currently in device buffer i.e. may be incomplete so wait a bit before read
        time.sleep(wait_sleep)
        # in pyserial==3.5 method added .read_all()
        # Read all bytes currently available in the buffer of the OS.
        # BUT... not availible in pyserial==3.4
        # ADDITIONALLY, https://pyserial.readthedocs.io/en/latest/index.html says latest yet refers to 3.4
        # SO... lets make this requirement 3.4 and manually implement read_all()
        if hasattr(self.con, "read_all"):
            return self.con.read_all()
        else:
            # in_waiting - Return the number of bytes currently in the input buffer.
            return self.con.read(self.con.in_waiting)

    def read_until(self, expected=serial.LF, size=None):
        return self.con.read_until(expected=expected, size=size)

    def get(self, cmd, wait_sleep=0.2):
        self.write(cmd)
        result = self.read(wait_sleep=wait_sleep)
        return result

    def get_exact(self, cmd, expected=serial.LF, size=None):
        self.write(cmd)
        result = self.read_until(expected=expected, size=size)
        return result
