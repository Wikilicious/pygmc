import logging
import sys

import pytest
from serial import Serial

import pygmc

if not sys.platform.startswith("linux"):
    pytest.skip("skipping tests - not running linux", allow_module_level=True)


def get_mock_dev(cmd_response_map):
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


def test_setting_password_does_not_log(caplog):
    cmd_response_map = {b"<SETWIFIPWDawkins>>": b"\xaa"}
    mock_dev = get_mock_dev(cmd_response_map)
    mock_dev_serial = Serial(mock_dev.port)

    connection = pygmc.connection.Connection(
        port="dummy", baudrate=123, serial_connection=mock_dev_serial
    )

    gc = pygmc.devices.GMC500Plus("dummy", 123, connection=connection)

    assert not mock_dev.stubs[b"<SETWIFIPWDawkins>>"].called, "Unexpected cmd call"

    with caplog.at_level(logging.DEBUG, logger="pygmc"):
        gc.set_wifi_password("Dawkins")

    assert mock_dev.stubs[b"<SETWIFIPWDawkins>>"].called, "Expected cmd call"

    # We are checking if connection.write() is called with log=False so that the
    # password is not logged
    assert "writing cmd" in caplog.text, "Expected log message not found"
    # GRC the password isn't in any log message
    assert "Dawkins" not in caplog.text, "Password found in log message"


# pytest can't delattr read_all? what?
# def test_pyserial_read_all_fix_for_34(monkeypatch):
#     """
#     pyserial==3.5 has method .read_all
#     pyserial==3.4 does not
#
#     pygmc checks hasattr else it manually gets 'in_waiting' bytes and uses it in .read()
#     """
#     cmd_response_map = {b"MATH": b"YES"}
#     mock_dev = get_mock_dev(cmd_response_map)
#     mock_dev_serial = Serial(mock_dev.port)
#
#     connection = pygmc.connection.Connection(
#         port="dummy", baudrate=123, serial_connection=mock_dev_serial
#     )
#
#     # let's fake pyserial==3.4
#     monkeypatch.delattr(connection._con, "read_all")
#     # The true test is getting a response with read_all deleted
#     response = connection.get(b"MATH", wait_sleep=0)
#     assert response == b"YES", "Unexpected response"
