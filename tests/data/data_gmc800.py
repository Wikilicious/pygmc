import datetime

# GET CMDS
#########################################################################################
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
    "get_cpm": 2495,
    "get_cps": 39,
    "get_datetime": datetime.datetime(2024, 3, 9, 15, 33, 58),
    "get_serial": "03004836373106",
    "get_usv_h": 16.222366710013002,
    "get_version": "GMC-800Re1.08",
    "power_on": None,
    "power_off": None,
    "reboot": None,
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
}


# SET & ACTION CMDS
#########################################################################################
actions_cmd_response_map = {
    # datetime.datetime(2024, 1, 8, 17, 54, 57, 662848)
    b"<SETDATETIME\x18\x01\x08\x1169>>": b"\xaa",
    b"<KEY0>>": b"",
    b"<REBOOT>>": b"",
    b"<POWEROFF>>": b"",
    b"<POWERON>>": b"",
    b"<HEARTBEAT1>>": b"\x00\x00\x00\x13",  # 19
    b"<HEARTBEAT0>>": b"",
}


# voluptuous schema would be nice here... but do we want the overhead/dependency?
actions_device_test_cases = [
    {
        "test_name": "set datetime",
        "method": "set_datetime",
        "args": (),
        "kwargs": {"datetime_": datetime.datetime(2024, 1, 8, 17, 54, 57, 662848)},
        "return": None,
        "expected_write": b"<SETDATETIME\x18\x01\x08\x1169>>",
        "expected_read": b"\xaa",
        "raises": None,
    },
    {
        "test_name": "set datetime to invalid year - 1999",
        "method": "set_datetime",
        "args": (),
        "kwargs": {"datetime_": datetime.datetime(1999, 1, 8, 17, 54, 57, 662848)},
        "return": None,
        "expected_write": b"",
        "expected_read": b"",
        "raises": ValueError,
    },
    {
        "test_name": "set datetime to invalid year - 3000",
        "method": "set_datetime",
        "args": (),
        "kwargs": {"datetime_": datetime.datetime(3000, 1, 8, 17, 54, 57, 662848)},
        "return": None,
        "expected_write": b"",
        "expected_read": b"",
        "raises": ValueError,
    },
    {
        "test_name": "send key",
        "method": "send_key",
        "args": (),
        "kwargs": {"key_number": 0},
        "return": None,
        "expected_write": b"<KEY0>>",
        "expected_read": b"",
        "raises": None,
    },
    {
        "test_name": "send bad key",
        "method": "send_key",
        "args": (),
        "kwargs": {"key_number": 4},
        "return": None,
        "expected_write": b"",
        "expected_read": b"",
        "raises": ValueError,
    },
    {
        "test_name": "reboot",
        "method": "reboot",
        "args": (),
        "kwargs": {},
        "return": None,
        "expected_write": b"<REBOOT>>",
        "expected_read": b"",
        "raises": None,
    },
    {
        "test_name": "power on",
        "method": "power_on",
        "args": (),
        "kwargs": {},
        "return": None,
        "expected_write": b"<POWERON>>",
        "expected_read": b"",
        "raises": None,
    },
    {
        "test_name": "power off",
        "method": "power_off",
        "args": (),
        "kwargs": {},
        "return": None,
        "expected_write": b"<POWEROFF>>",
        "expected_read": b"",
        "raises": None,
    },
    {
        "test_name": "heartbeat on",
        "method": "_heartbeat_on",
        "args": (),
        "kwargs": {},
        "return": None,
        "expected_write": b"<HEARTBEAT1>>",
        "expected_read": b"",
        "raises": None,
    },
    {
        "test_name": "heartbeat off",
        "method": "_heartbeat_off",
        "args": (),
        "kwargs": {},
        "return": None,
        "expected_write": b"<HEARTBEAT0>>",
        "expected_read": b"",
        "raises": None,
    },
    # TODO: investigate WTF!
    # AH! hb calls hb-off after calling on! ugh! duh!
    {
        "test_name": "heartbeat live WTFFFFFFFFFFFFFFFFFFFFFFFFFFFFF",
        "method": "heartbeat_live",
        "args": (),
        "kwargs": {"count": 1},
        "return": 19,
        "expected_write": b"<HEARTBEAT0>>",  # WTF! Why is this passing!
        "expected_read": b"",
        "raises": None,
    },
    {
        "test_name": "heartbeat live",
        "method": "heartbeat_live",
        "args": (),
        "kwargs": {"count": 1},
        "return": 19,
        "expected_write": b"<HEARTBEAT1>>",
        "expected_read": b"",
        "raises": None,
    },
    # Same as heartbeat_live, just prints instead
    # TODO: add print check
    {
        "test_name": "heartbeat live print",
        "method": "heartbeat_live_print",
        "args": (),
        "kwargs": {"count": 1},
        "return": None,
        "expected_write": b"<HEARTBEAT1>>",
        "expected_read": b"",
        "raises": None,
    },
]
