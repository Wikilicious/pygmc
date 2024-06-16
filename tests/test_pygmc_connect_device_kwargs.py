"""
Motivation for these tests were adding kwarg 'timeout' and only GMC500Plus failed.
All devices should've failed.
Tests below capture this case.
"""

import pytest
import serial

import pygmc

parametrize_data = [
    x["device_class"] for x in pygmc.devices.auto_get_device.device_match_list
]


@pytest.mark.parametrize("device", parametrize_data)
def test_device_kwargs(device):
    keyword_arguments = {
        "port": "/dummy",
        "baudrate": 57600,
        "timeout": 5,
        "connection": None,
    }
    try:
        device(**keyword_arguments)
    except serial.serialutil.SerialException:
        # Exception example
        # serial.serialutil.SerialException: [Errno 2] could not open port /dummy:
        # [Errno 2] No such file or directory: '/dummy'
        # Test is aiming to catch "unexpected keyword argument 'timeout'" or similar
        pass
