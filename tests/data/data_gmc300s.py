import datetime

# GET CMDS
#########################################################################################
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


# SET & ACTION CMDS
#########################################################################################
actions_cmd_response_map = {
    # datetime.datetime(2024, 1, 8, 17, 54, 57, 662848)
    b"<SETDATETIME\x18\x01\x08\x1169>>": b"\xaa",
    b"<KEY0>>": b"",
    b"<REBOOT>>": b"",
    b"<POWEROFF>>": b"",
    b"<POWERON>>": b"",
    b"<HEARTBEAT1>>": b"\x00\x17",  # 23
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
    # TODO: rethink test
    {
        "test_name": "heartbeat live check turns off",
        "method": "heartbeat_live",
        "args": (),
        "kwargs": {"count": 1},
        "return": 23,
        "expected_write": b"<HEARTBEAT0>>",
        "expected_read": b"",
        "raises": None,
    },
    {
        "test_name": "heartbeat live check turns on",
        "method": "heartbeat_live",
        "args": (),
        "kwargs": {"count": 1},
        "return": 23,
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
