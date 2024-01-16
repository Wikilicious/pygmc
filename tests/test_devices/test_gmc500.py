import types
import pytest

import pygmc
from ..mocks import MockConnection
from ..data import data_gmc500_plus


actions_conn = MockConnection(data_gmc500_plus.actions_cmd_response_map)
gc = pygmc.GMC500(port=None, baudrate=123, connection=actions_conn)


@pytest.mark.parametrize("case", data_gmc500_plus.actions_device_test_cases)
def test_expected_results(case):
    print(f"Test case: {case['test_name']}")

    if case["raises"]:
        with pytest.raises(case["raises"]) as excinfo:
            getattr(gc, case["method"])(*case["args"], **case["kwargs"])
        return

    expected_calls = actions_conn.get_cmd_calls(case["expected_write"]) + 1
    response = getattr(gc, case["method"])(*case["args"], **case["kwargs"])
    if isinstance(response, types.GeneratorType):
        response = next(iter(response))
    assert response == case["return"]
    assert actions_conn.get_cmd_calls(case["expected_write"]) == expected_calls
