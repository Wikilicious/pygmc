"""
This mocks a device at a lower level and allows us to test pygmc.Connection()
We just need to test one device because all we really want is to test pygmc.Connection()
mock_serial only works on Linux, so skip test if not on Linux.
"""

import sys  # noqa: I001
import pytest
from serial import Serial

# D.R.Y. import from test_gmc500_plus_device_rfc_1801
from .test_gmc500_plus_device_rfc_1801 import (  # noqa: I001
    cmd_response_map,
    device_result_map,
)
import pygmc
from pygmc.connection.const import BAUDRATES


if not sys.platform.startswith("linux"):
    # TODO: can we define mock_serial after this?
    pytest.skip("skipping tests - not running linux", allow_module_level=True)


parametrize_data = [(k, v) for k, v in device_result_map.items()]


def get_mock_dev():
    """Lazily import mock_serial to avoid ModuleError in Windows"""
    mock_serial = pytest.importorskip("mock_serial", reason="Doesn't work on Win")
    # Mock device
    mock_dev = mock_serial.MockSerial()
    mock_dev.open()
    for cmd, resp in cmd_response_map.items():
        mock_dev.stub(receive_bytes=cmd, send_bytes=resp)

    # We turn heartbeat off before many ops... need to instruct mock_dev to ignore
    mock_dev.stub(receive_bytes=b"<HEARTBEAT0>>", send_bytes=b"")

    return mock_dev


def get_mock_gc():
    mock_dev = get_mock_dev()
    mock_dev_serial = Serial(mock_dev.port)

    connection = pygmc.connection.Connection(
        port="dummy", baudrate=123, serial_connection=mock_dev_serial
    )

    gc = pygmc.devices.DeviceRFC1801(connection)

    return gc


# mock_serial only works on Linux
if not sys.platform.startswith("linux"):
    pytest.skip("skipping tests - not running linux", allow_module_level=True)
else:
    mock_dev = get_mock_dev()
    mock_dev_serial = Serial(mock_dev.port)
    gc = get_mock_gc()


@pytest.mark.parametrize("cmd,expected", parametrize_data)
def test_expected_results(cmd, expected):
    """
    Test that the method/cmd in the device actually returns the expected value in the
    device_result_map dict.
    @pytest.mark.parametrize just calls this function for each item in the dictionary.
    """
    # e.g. getattr(mock_device, 'get_cpm') --> mock_device.get_cpm
    result = getattr(gc, cmd)()
    assert result == expected
    print(f"{cmd=}")
    print(f"{expected=}")
    print(f"{result=}")


def test_main_entry():
    mock_dev = get_mock_dev()
    gc = pygmc.connect(mock_dev.port)
    assert gc.get_version()[0:7] == "GMC-500"


def test_utils():
    assert isinstance(pygmc.connection.get_gmc_usb_devices(), list)
    assert isinstance(pygmc.connection.get_all_usb_devices(), list)


def test_conn_details():
    mock_dev = get_mock_dev()
    gc = pygmc.connect(mock_dev.port)
    deets = gc.get_connection_details()
    print(f"conn deets: {deets}")


def test_close_connection():
    mock_dev = get_mock_dev()
    mock_dev_serial = Serial(mock_dev.port)

    connection = pygmc.connection.Connection(
        port="dummy", baudrate=123, serial_connection=mock_dev_serial
    )
    connection.close_connection()
    connection.close_connection()  # yes, twice


def test_str_and_repr():
    mock_dev = get_mock_dev()
    mock_dev_serial = Serial(mock_dev.port)

    connection = pygmc.connection.Connection(
        port="dummy", baudrate=123, serial_connection=mock_dev_serial
    )
    print(connection)  # test __repr__ & __str__
    # disconnect to test super().__repr__
    connection._con = None
    connection.close_connection()
    print(connection)  # test super().__repr__


def test_connection_port_method():
    mock_dev = get_mock_dev()

    pygmc.connection.Connection(port=mock_dev.port, baudrate=BAUDRATES[0])


def test_connection_bad_baudrate():
    # this just enters block with warning loggers
    mock_dev = get_mock_dev()

    pygmc.connection.Connection(port=mock_dev.port, baudrate=123)


parametrize_device_conns = [
    pygmc.GMC300,
    pygmc.GMC300S,
    pygmc.GMC300EPlus,
    pygmc.GMC320,
    pygmc.GMC320Plus,
    pygmc.GMC320PlusV5,
    pygmc.GMC500,
    pygmc.GMC500Plus,
    pygmc.GMC600,
    pygmc.GMC600Plus,
    pygmc.GMC800,
    pygmc.GMCSE,
]


@pytest.mark.parametrize("dev", parametrize_device_conns)
def test_device_connection_port_method(dev):
    dev(mock_dev.port)


@pytest.mark.parametrize("dev", parametrize_device_conns)
def test_device_connection_serial_method(dev):
    connection = pygmc.connection.Connection(port=mock_dev.port, baudrate=123)
    dev(None, connection=connection)


@pytest.mark.parametrize("dev", parametrize_device_conns)
def test_device_connection_error(dev):
    with pytest.raises(ConnectionError) as excinfo:
        print(excinfo)
        dev(None)


def test_long_response_logger():
    mock_serial = pytest.importorskip("mock_serial", reason="Doesn't work on Win")
    mock_dev = mock_serial.MockSerial()
    mock_dev.open()

    mock_dev.stub(receive_bytes=b"<CONY>>", send_bytes=b"X" * 51)
    mock_dev_serial = Serial(mock_dev.port)

    connection = pygmc.connection.Connection(
        port="dummy", baudrate=123, serial_connection=mock_dev_serial
    )

    # stupid... but can't wait_sleep=0 because it fails
    # ugh, it's gonna be a non-deterministic test, fluck!
    # passes with sleep=0.000001, pad the number for github ci actions???
    response = connection.get(cmd=b"<CONY>>", wait_sleep=0.0005)
    assert len(response) == 51

    response = connection.get_at_least(cmd=b"<CONY>>", size=51, wait_sleep=0.0005)
    assert len(response) == 51
