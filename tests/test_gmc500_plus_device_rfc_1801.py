"""
Mock the connection class to deterministically return results recorded from GMC-500+.
Structured in a novice friendly manner.
"""

import datetime
import getpass

import pytest

from pygmc import devices

from .mocks import MockConnection

cmd_response_map = {
    b"<GETVER>>": b"GMC-500+Re 2.22",
    b"<GETSERIAL>>": b"00!W!W\xf6",
    b"<GETCPM>>": b"\x00\x00\x04\xba",
    b"<GETCPS>>": b"\x00\x00\x00\x13",
    b"<GETMAXCPS>>": b'\x00\x00\x00"',
    b"<GETCPMH>>": b"\x00\x00\x00\x05",
    b"<GETCPML>>": b"\x00\x00\x05\xdc",
    b"<GETGYRO>>": b"\xff\xf9\xff\x0e\x00%\xaa",
    b"<GETVOLT>>": b"4.0v\x00",
    b"<GETDATETIME>>": b"\x17\x0b\n\x12!\x04\xaa",
    b"<GETCFG>>": b"\x00\x00\x00\x00\x1f\x00\x00d\x00d?&ffu0CC\x00\x00\x00\x19@\x9b33\x00?\x00\x00\x00\x00\x02\x03\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\x00\x01\x00x\n\x05\xe1<\x00\n\xff\x00\x00\x00\n\x00\x01\n\x00d\x00?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00wangshaofei\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00log2.asp\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00www.gmcmap.com\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00log2.asp\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x02\x03\x00@<\x02\x00\x00\x01\x00x\x00\xc8\x002\x00d\x05\x01\x01\xa2\xa1\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x17\x0b\n\x12!\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff",  # noqa
}

device_result_map = {
    "get_version": "GMC-500+Re 2.22",
    "get_serial": "303021572157f6",
    "get_cpm": 1210,
    "get_cps": 19,
    "get_max_cps": 34,
    "get_cpmh": 5,
    "get_cpml": 1500,
    "get_gyro": (-7, -242, 37),
    "get_voltage": 4.0,
    "get_datetime": datetime.datetime(2023, 11, 10, 18, 33, 4),
    "get_usv_h": 7.864999977043251,
    "get_config": {
        "Power": 0,
        "Alarm": 0,
        "Speaker": 0,
        "CalibrationCPM_0": 100,
        "CalibrationCPM_1": 30000,
        "CalibrationCPM_2": 25,
        "SaveDataType": 2,
        "MaxCPM": 1505,
        "Baudrate": 0,
        "BatteryType": 0,
        "ThresholdMode": 0,
        "ThresholdCPM": 100,
        "Calibration_uSv_0": 0.6499999761581421,
        "Calibration_uSv_1": 195.0,
        "Calibration_uSv_2": 4.849999904632568,
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
mock_device = devices.DeviceRFC1801(mock_connection)


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


def test_auto_device():
    device = devices.auto_get_device_from_connection(mock_connection)
    assert isinstance(type(device), type(devices.GMC500))


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
    mock_device_usv = devices.DeviceRFC1801(mock_connection_usv)

    mock_device_usv._config = calib_config

    print(f"{cpm=} {expected=} | {calib_config=}")

    mock_device_usv.get_cpm = lambda: cpm
    usv = mock_device_usv.get_usv_h()
    usv_from_input = mock_device_usv.get_usv_h(cpm=cpm)

    assert usv == expected, "uSv does not match expected config calibration"
    assert usv == usv_from_input, "manual input cpm does not match equivalent get_cpm"


def test_getpass_password_input(monkeypatch):
    cmd_response_map_usv = {b"<SETWIFIPWDawkins>>": b"\xaa"}
    mock_connection_pswd = MockConnection(cmd_response_map_usv)

    monkeypatch.setattr(getpass, "getpass", lambda: "Dawkins")

    mock_device_pswd = devices.DeviceRFC1801(mock_connection_pswd)
    mock_device_pswd.set_wifi_password()  # empty input to test our monkeypatch getpass

    cmd_called_count = mock_connection_pswd.get_cmd_calls(b"<SETWIFIPWDawkins>>")

    assert cmd_called_count == 1
