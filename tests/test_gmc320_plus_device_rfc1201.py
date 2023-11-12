"""
Mock the connection class to deterministically return results recorded from GMC-320+.
Structured in a novice friendly manner.
"""
import datetime

import pytest

from pygmc import devices

from .mocks import MockConnection

cmd_response_map = {
    b"<GETVER>>": b"GMC-320Re 4.26",
    b"<GETSERIAL>>": b"\xf4\x88\x00g\x1cB\xc2",
    b"<GETCPM>>": b"\x01\xb6",
    b"<GETGYRO>>": b"\xff\x04\x00\x10\x00L\xaa",
    b"<GETVOLT>>": b"*",
    b"<GETDATETIME>>": b"\x17\x0b\n\x10.6\xaa",
    b"<GETCFG>>": b"\x00\x00\x00\x01\x1e\x01\x00d\x00<\x14\xae\xc7>\x00\xf0\x14\xae\xc7?\x03\xe8\x00\x00\xd0@\x05\x00\x00\x00?\x00\x01\x02\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\x00\x01\x00x\x15\x01\xbc<\x00\x08\xff\x01\x00\xfe\n\x00\x01\n\x00<\x00\x14\xae\xc7>\x17\x0b\n\x10.6\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff",
}

device_result_map = {
    "get_version": "GMC-320Re 4.26",
    "get_serial": "f48800671c42c2",
    "get_cpm": 438,
    "get_gyro": (-252, 16, 76),
    "get_voltage": 4.2,
    "get_datetime": datetime.datetime(2023, 11, 10, 16, 46, 54),
    "get_usv_h": 2.846999895572662,
    "get_config": {
        "Power": 0,
        "Alarm": 0,
        "Speaker": 0,
        "CalibrationCPM_0": 60,
        "CalibrationCPM_1": 240,
        "CalibrationCPM_2": 1000,
        "SaveDataType": 1,
        "MaxCPM": 444,
        "Baudrate": 254,
        "BatteryType": 0,
        "ThresholdMode": 0,
        "ThresholdCPM": 60,
        "Calibration_uSv_0": 0.38999998569488525,
        "Calibration_uSv_1": 1.559999942779541,
        "Calibration_uSv_2": 6.5,
        "IdleTextState": 5,
        "AlarmValue_uSv": 0.5,
        "Threshold_uSv": 0.38999998569488525,
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
