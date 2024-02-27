import types

import pytest

import pygmc
from pygmc import devices

from ..data import data_gmcse
from ..mocks import MockConnection

actions_conn = MockConnection(data_gmcse.actions_cmd_response_map)
gcse = pygmc.GMCSE(port=None, baudrate=123, connection=actions_conn)

parametrize_data = [(gcse, x) for x in data_gmcse.actions_device_test_cases]

# Mock the connection to a device
# Uses recorded responses device
mock_connection = MockConnection(data_gmcse.cmd_response_map)

# Use our fake/mock connection in our real device class
mock_device = devices.DeviceRFC1201(mock_connection)


@pytest.mark.parametrize("gc,case", parametrize_data)
def test_expected_results(gc, case):
    print(f"Test case: {case['test_name']}")

    if case["raises"]:
        with pytest.raises(case["raises"]) as excinfo:
            print(excinfo)
            getattr(gc, case["method"])(*case["args"], **case["kwargs"])
        return

    expected_calls = actions_conn.get_cmd_calls(case["expected_write"]) + 1
    response = getattr(gc, case["method"])(*case["args"], **case["kwargs"])
    if isinstance(response, types.GeneratorType):
        response = next(iter(response))
    assert response == case["return"]
    assert actions_conn.get_cmd_calls(case["expected_write"]) == expected_calls


def test_auto_device():
    device = devices.auto_get_device_from_connection(mock_connection)
    assert isinstance(type(device), type(devices.GMCSE))


def test_reset_buffers(capfd):
    mock_device.get_config()
    out, err = capfd.readouterr()
    assert "reset_buffers" in out
