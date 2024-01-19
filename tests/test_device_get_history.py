import pytest

import pygmc

from .data import data_history_parser
from .mocks import MockConnection

# How to create cmd input for test:
# start_s = struct.pack(">I", 0)[1:]  # 0=start position
# size_s = struct.pack(">H", 110)  # 110=end position
# cmd = b"<SPIR" + start_s + size_s + b">>"
# and set flash-mem read size to 110
cmd_response_map = {
    b"<SPIR\x00\x00\x00\x00n>>": data_history_parser.raw_history_with_notes1,
}

# device get_history includes columns as first row
tidy_result = data_history_parser.raw_history_with_notes1_tidy
tidy_result.insert(
    0, ["datetime", "count", "unit", "mode", "reference_datetime", "notes"]
)

device_result_map = {
    "get_history_data": tidy_result,
}

parametrize_data = [(k, v) for k, v in device_result_map.items()]


# Mock the connection to a device
# Uses recorded responses device
mock_connection = MockConnection(cmd_response_map)


# Use our fake/mock connection in our real device class
mock_device = pygmc.devices.BaseDevice(mock_connection)

# Override mem/read size
mock_device._flash_memory_size_bytes = 110
mock_device._flash_memory_page_size_bytes = 110


@pytest.mark.parametrize("cmd,expected", parametrize_data)
def test_expected_results(cmd, expected):
    """
    Test that the method/cmd in the device actually returns the expected value in the device_result_map dict.
    @pytest.mark.parametrize just calls this function for each item in the dictionary.
    """
    # e.g. getattr(mock_device, 'get_cpm') --> mock_device.get_cpm
    result = getattr(mock_device, cmd)()
    assert result == expected
    print(f"{cmd=}")
    print(f"{expected=}")
    print(f"{result=}")
