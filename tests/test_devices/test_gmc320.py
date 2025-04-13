import types

import pytest

import pygmc

from ..data import data_gmc320
from ..mocks import MockConnection

actions_conn = MockConnection(data_gmc320.actions_cmd_response_map)
gc320 = pygmc.GMC320(port=None, baudrate=123, connection=actions_conn)
gc320s = pygmc.GMC320S(port=None, baudrate=123, connection=actions_conn)
gc320plus = pygmc.GMC320Plus(port=None, baudrate=123, connection=actions_conn)
gc320plus_v5 = pygmc.GMC320PlusV5(port=None, baudrate=123, connection=actions_conn)


parametrize_data = [(gc320, x) for x in data_gmc320.actions_device_test_cases]
parametrize_data.extend([(gc320s, x) for x in data_gmc320.actions_device_test_cases])
parametrize_data.extend([(gc320plus, x) for x in data_gmc320.actions_device_test_cases])
parametrize_data.extend(
    [(gc320plus_v5, x) for x in data_gmc320.actions_device_test_cases]
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
