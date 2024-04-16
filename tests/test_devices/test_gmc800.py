import types

import pytest

import pygmc

from ..data import data_gmc800
from ..mocks import MockConnection

actions_conn = MockConnection(data_gmc800.actions_cmd_response_map)
# reuse data from GMC300S since we don't have a source
gc800 = pygmc.GMC800(port=None, baudrate=123, connection=actions_conn)


parametrize_data = [(gc800, x) for x in data_gmc800.actions_device_test_cases]


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
