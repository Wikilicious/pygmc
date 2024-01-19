import datetime

# GET CMDS
#########################################################################################
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


# SET & ACTION CMDS
#########################################################################################
actions_cmd_response_map = {
    # datetime.datetime(2024, 1, 8, 17, 54, 57, 662848)
    b"<SETDATETIME\x18\x01\x08\x1169>>": b"\xaa",
    b"<KEY0>>": b"",
    b"<REBOOT>>": b"",
    b"<POWEROFF>>": b"",
    b"<POWERON>>": b"",
    b"<HEARTBEAT1>>": b"\x01\xb6",  # 438
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
        "return": 438,
        "expected_write": b"<HEARTBEAT0>>",
        "expected_read": b"",
        "raises": None,
    },
    {
        "test_name": "heartbeat live check turns on",
        "method": "heartbeat_live",
        "args": (),
        "kwargs": {"count": 1},
        "return": 438,
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
