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
    b"<GETTEMP>>": b"\x14\x06\x00\xaa",
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
    "get_temp": 20.6,  # only exists in RFC1201
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
    Test that the method/cmd in the device actually returns the expected value in the
    device_result_map dict.
    @pytest.mark.parametrize just calls this function for each item in the dictionary.
    """
    # e.g. getattr(mock_device, 'get_cpm') --> mock_device.get_cpm
    result = getattr(mock_device, cmd)()
    assert result == expected
    print(f"{cmd=}")
    print(f"{expected=}")
    print(f"{result=}")


def test_negative_temperature():
    """This is just to test the 1 line that flips the sign to a negative temperature."""
    mock_connection_temp = MockConnection({b"<GETTEMP>>": b"\x14\x06\x01\xaa"})
    mock_device_temp = devices.DeviceRFC1201(mock_connection_temp)

    temp = mock_device_temp.get_temp()
    assert temp == -20.6


def test_auto_device():
    device = devices.auto_get_device_from_connection(mock_connection)
    assert isinstance(type(device), type(devices.GMC300S))


def test_reset_buffers(capfd):
    mock_device.get_config()
    out, err = capfd.readouterr()
    assert "reset_buffers" in out


# uSv Tests
config_calib0 = {
    "CalibrationCPM_0": 100,
    "CalibrationCPM_1": 200,
    "CalibrationCPM_2": 300,
    "Calibration_uSv_0": 1,
    "Calibration_uSv_1": 10,
    "Calibration_uSv_2": 100,
}

# Tests edge case of non-increasing config cpm
config_calib1 = {
    "CalibrationCPM_0": 100,
    "CalibrationCPM_1": 25,
    "CalibrationCPM_2": 300,
    "Calibration_uSv_0": 1,
    "Calibration_uSv_1": 55,
    "Calibration_uSv_2": 100,
}

# Tests edge case of last config not being the largest (GMC-500+ default is like this)
config_calib2 = {
    "CalibrationCPM_0": 100,
    "CalibrationCPM_1": 30000,
    "CalibrationCPM_2": 25,
    "Calibration_uSv_0": 0.6499999761581421,
    "Calibration_uSv_1": 195.0,
    "Calibration_uSv_2": 4.849999904632568,
}

parametrize_calib_data = [
    # config, cpm, expected_result
    (config_calib0, 10, 0.1),
    (config_calib0, 100, 1),
    (config_calib0, 101, 1.0899999999999999),
    (config_calib0, 150, 5.5),
    (config_calib0, 200, 10),
    (config_calib0, 201, 10.900000000000006),
    (config_calib0, 250, 55),
    (config_calib0, 299, 99.10000000000002),
    (config_calib0, 300, 100),
    (config_calib0, 350, 145),  # tests extrapolation
    # edge cases
    (config_calib1, 25, 0.25),
    (config_calib1, 99, 0.99),
    (config_calib1, 101, 67.43636363636364),
    (config_calib1, 250, 91.81818181818181),
    (config_calib1, 300, 100),
    (config_calib1, 350, 108.18181818181819),
    # more edge cases
    (config_calib2, 50, 0.32499998807907104),
    (config_calib2, 1210, 7.864999977043251),
    (config_calib2, 20000, 129.99999999202615),
    (config_calib2, 30000, 195),
    (config_calib2, 35000, 227.50000000398694),
]


@pytest.mark.parametrize("calib_config,cpm,expected", parametrize_calib_data)
def test_usv(calib_config, cpm, expected):
    cmd_response_map_usv = {}
    mock_connection_usv = MockConnection(cmd_response_map_usv)

    # Use our fake/mock connection in our real device class
    mock_device_usv = devices.DeviceRFC1201(mock_connection_usv)

    mock_device_usv._config = calib_config

    print(f"{cpm=} {expected=} | {calib_config=}")

    mock_device_usv.get_cpm = lambda: cpm
    usv = mock_device_usv.get_usv_h()
    usv_from_input = mock_device_usv.get_usv_h(cpm=cpm)

    assert usv == expected, "uSv does not match expected config calibration"
    assert usv == usv_from_input, "manual input cpm does not match equivalent get_cpm"
