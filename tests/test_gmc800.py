import datetime

import pytest

from pygmc import devices

from .mocks import MockConnection

cmd_response_map = {
    b"<GETVER>>": b"GMC-800Re1.08",
    b"<GETSERIAL>>": b"\x03\x00H671\x06",
    b"<GETCPM>>": b"\x00\x00\t\xbf",
    b"<GETCPS>>": b"\x00\x00\x00'",
    b"<GETDATETIME>>": b"\x18\x03\t\x0f!:\xaa",
    b"<GETCFG>>": b"\x00\x00\xff\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\xff\xff\xff\xff\xff\x01\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x01\xff\xff\xff\xff\xff\xff\xff\x00\n\xff\xff\xff\xff\xff\x00\x01\xff\xff\xff\xff\xff\xff\xff\xff\x03\xff\x0f,\x00\x00\x06\x02\x00\x00<\x14\x00\x00x(\x00\x01,d\x00\x02X\xc8\x00\x04\xb1\x90A \x00\x00B\xc8\x00\x00CH\x00\x00C\xfa\x00\x00Dz\x00\x00D\xfa\x00\x00\x00\x00\x01\x01\x00\x00\x00d\x00\xff\x06\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff",
    b"<POWERON>>": b"",
    b"<POWEROFF>>": b"",
    b"<KEY0>>": b"",
    b"<REBOOT>>": b"",
}


device_result_map = {
    "get_config": {
        "Power": 0,
        "Save_Mode": 1,
        "Power_Saving_Mode": 1,
        "LCD_Backlight_Level": 10,
        "LED": 1,
        "Fast_Estimate_Time": 3,
        "Alarm_Volume": 15,
        "Tube_Voltage": 44,
        "Calibration_CPM_1": 1538,
        "Calibration_CPM_2": 15380,
        "Calibration_CPM_3": 30760,
        "Calibration_CPM_4": 76900,
        "Calibration_CPM_5": 153800,
        "Calibration_CPM_6": 307600,
        "Calibration_USV_1": 10.0,
        "Calibration_USV_2": 100.0,
        "Calibration_USV_3": 200.0,
        "Calibration_USV_4": 500.0,
        "Calibration_USV_5": 1000.0,
        "Calibration_USV_6": 2000.0,
        "Click_Sound": 0,
        "Speaker_Volume": 0,
        "Vibration": 1,
        "Alarm_CPM": 100,
        "Theme": 0,
    },
    "get_cpm": 2495,
    "get_cps": 39,
    "get_datetime": datetime.datetime(2024, 3, 9, 15, 33, 58),
    "get_serial": "03004836373106",
    "get_usv_h": 16.222366710013002,
    "get_version": "GMC-800Re1.08",
    "power_on": None,
    "power_off": None,
    "reboot": None,
}


parametrize_data = [(k, v) for k, v in device_result_map.items()]


# Mock the connection to a device
# Uses recorded responses device
mock_connection = MockConnection(cmd_response_map)


# Use our fake/mock connection in our real device class
mock_device = devices.DeviceSpec404(mock_connection)


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
    assert isinstance(type(device), type(devices.GMC800))


def test_reset_buffers(capfd):
    mock_device.get_config()
    out, err = capfd.readouterr()
    assert "reset_buffers" in out
