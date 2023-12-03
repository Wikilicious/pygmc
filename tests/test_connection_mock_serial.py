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


parametrize_data = [(k, v) for k, v in device_result_map.items()]


def get_mock_gc():
    """Lazily import mock_serial to avoid ModuleError in Windows"""
    mock_serial = pytest.importorskip("mock_serial", reason="Doesn't work on Win")
    # Mock device
    mock_dev = mock_serial.MockSerial()
    mock_dev.open()
    for cmd, resp in cmd_response_map.items():
        mock_dev.stub(receive_bytes=cmd, send_bytes=resp)

    # We turn heartbeat off before many ops... need to instruct mock_dev to ignore
    mock_dev.stub(receive_bytes=b"<HEARTBEAT0>>", send_bytes=b"")

    mock_dev_serial = Serial(mock_dev.port)

    connection = pygmc.connection.Connection()
    connection.connect_user_provided(mock_dev_serial)

    gc = pygmc.devices.DeviceRFC1801(connection)

    return gc


# mock_serial only works on Linux
if not sys.platform.startswith("linux"):
    pytest.skip("skipping tests - not running linux", allow_module_level=True)
else:
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


def test_connection_method():
    """Tests connection tester flow."""
    # returns true
    assert gc.connection._test_con()


def test_baudrate_method():
    """Tests baudrate check flow."""
    # returns true
    assert gc.connection._check_baudrate(gc.connection._con)
