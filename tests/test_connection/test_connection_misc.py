import logging
import sys
from unittest import mock

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


def test_connection_timeout_msg(caplog):
    with caplog.at_level(logging.DEBUG, logger="pygmc"):

        with mock.patch("serial.Serial") as mock_serial:
            mock_serial.side_effect = TimeoutError

            with pytest.raises(TimeoutError):
                pygmc.connection.Connection("dummy", baudrate=123)

    assert "consider reconnecting USB" in caplog.text
