import types

import pytest

import pygmc

from ..data import data_gmc500_plus
from ..mocks import MockConnection

actions_conn = MockConnection(data_gmc500_plus.actions_cmd_response_map)
gc500 = pygmc.GMC500(port=None, baudrate=123, connection=actions_conn)
gc500plus = pygmc.GMC500(port=None, baudrate=123, connection=actions_conn)


# Do both GMC500 and GMC500+ together
parametrize_data = [(gc500, x) for x in data_gmc500_plus.actions_device_test_cases]
parametrize_data.extend(
    [(gc500plus, x) for x in data_gmc500_plus.actions_device_test_cases]
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
