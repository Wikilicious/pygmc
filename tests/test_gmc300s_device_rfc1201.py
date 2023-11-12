"""
Mock the connection class to deterministically return results recorded from GMC-300S.
Structured in a novice friendly manner.
"""
import datetime

import pytest

from pygmc import devices

from .mocks import MockConnection

cmd_response_map = {
    b"<GETVER>>": b"GMC-300SRe 1.14",
    b"<GETSERIAL>>": b"\xf7\xf4\xc5x\x13\x9d\x08",
    b"<GETCPM>>": b"\x00\x17",
    b"<GETGYRO>>": b"\xc0\xc0\xfe\xc0\x06\x80\xaa",
    b"<GETVOLT>>": b"*",
    b"<GETDATETIME>>": b"\x17\x0b\n\x0c\x0f\x05\xaa",
    b"<GETCFG>>": b"\x00\x01\x00\x00\x01\x01\x00d\x06O\x00\x00 A?\x16\x00\x00\xc8B~,\x00\x00HC\x00\x00\x00\x00?\x00\x01\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\x00\x01\x00x\x15\x00%<\x00\x02\xff\x01\x00\xfc\n\x00\x01\n\x00d\x00\x00\x00\x00?\x03\x00\n\x11\x00\x00\x06O\x00\x00?\x16\x00\x00~,\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00 A\x00\x00\xc8B\x00\x00HC\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x17\x0b\t\x0e:\x10\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff",
}

device_result_map = {
    "get_version": "GMC-300SRe 1.14",
    "get_serial": "f7f4c578139d08",
    "get_cpm": 23,
    "get_gyro": (-16192, -320, 1664),
    "get_voltage": 4.2,
    "get_datetime": datetime.datetime(2023, 11, 10, 12, 15, 5),
    "get_usv_h": 0.14241486068111456,
    "get_config": {
        "Power": 0,
        "Alarm": 1,
        "Speaker": 0,
        "CalibrationCPM_0": 1615,
        "CalibrationCPM_1": 16150,
        "CalibrationCPM_2": 32300,
        "SaveDataType": 1,
        "MaxCPM": 37,
        "Baudrate": 252,
        "BatteryType": 0,
        "ThresholdMode": 0,
        "ThresholdCPM": 100,
        "Calibration_uSv_0": 10.0,
        "Calibration_uSv_1": 100.0,
        "Calibration_uSv_2": 200.0,
        "IdleTextState": 0,
        "AlarmValue_uSv": 0.5,
        "Threshold_uSv": 0.5,
    },
}
parametrize_data = [(k, v) for k, v in device_result_map.items()]


# Mock the connection to a device
# Uses recorded responses device
mock_connection = MockConnection(cmd_response_map)


# Use our fake/mock connection in our real device class
mock_device = devices.DeviceRFC1201(mock_connection)


@pytest.mark.parametrize("cmd,expected", parametrize_data)
def test_expected_results(cmd, expected):
    """
    Test that the method/cmd in the device actually returns the expected value in the device_result_map dict.
    @pytest.mark.parametrize just calls this function for each item in the dictionary.
    """
    # e.g. getattr(mock_device, 'get_cpm') --> mock_device.get_cpm
    result = getattr(mock_device, cmd)()
    assert result == expected
    print(f"{cmd=}")
    print(f"{expected=}")
    print(f"{result=}")


def test_auto_device():
    device = devices.auto_get_device(mock_connection)
    assert isinstance(device, devices.DeviceRFC1201)


def test_reset_buffers(capfd):
    mock_device.get_config()
    out, err = capfd.readouterr()
    assert "reset_buffers" in out
