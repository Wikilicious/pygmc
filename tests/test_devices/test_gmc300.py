import types

import pytest

import pygmc

from ..data import data_gmc300s
from ..mocks import MockConnection

actions_conn = MockConnection(data_gmc300s.actions_cmd_response_map)
# reuse data from GMC300S since we don't have a source
gc300 = pygmc.GMC300(port=None, baudrate=123, connection=actions_conn)
gc300s = pygmc.GMC300S(port=None, baudrate=123, connection=actions_conn)
gc300e_plus = pygmc.GMC300EPlus(port=None, baudrate=123, connection=actions_conn)


# Do both GMC500 and GMC500+ together
parametrize_data = [(gc300, x) for x in data_gmc300s.actions_device_test_cases]
parametrize_data.extend([(gc300s, x) for x in data_gmc300s.actions_device_test_cases])
parametrize_data.extend(
    [(gc300e_plus, x) for x in data_gmc300s.actions_device_test_cases]
)


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
