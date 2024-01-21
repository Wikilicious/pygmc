import sys
import tempfile

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
    b"<SPIR\x00\x00\x00\x00\xd3>>": data_history_parser.raw_history_with_notes2,
    b"<SPIR\x00\x00\x00\x00\n>>": b"\xff" * 10,  # break reading when page is all \xff
}

# device get_history includes columns as first row
tidy_result = data_history_parser.raw_history_with_notes1_tidy
tidy_result.insert(
    0, ["datetime", "count", "unit", "mode", "reference_datetime", "notes"]
)

# Expect same data for mock_device2
device_result_map = {
    "get_history_data": tidy_result,
}

device_result_map3 = {
    "get_history_data": [
        ["datetime", "count", "unit", "mode", "reference_datetime", "notes"],
    ],
}


# Mock the connection to a device
# Uses recorded responses device
mock_connection = MockConnection(cmd_response_map)


# Use our fake/mock connection in our real device class
mock_device = pygmc.devices.BaseDevice(mock_connection)
mock_device2 = pygmc.devices.BaseDevice(mock_connection)
mock_device3 = pygmc.devices.BaseDevice(mock_connection)

# Override mem/read size
mock_device._flash_memory_size_bytes = 110
mock_device._flash_memory_page_size_bytes = 110

# tests exiting after 100 counts of 255
mock_device2._flash_memory_size_bytes = 110 + 101
mock_device2._flash_memory_page_size_bytes = 110 + 101

# Tests exit pagination condition
mock_device3._flash_memory_size_bytes = 100
mock_device3._flash_memory_page_size_bytes = 10


parametrize_data = [(mock_device, k, v) for k, v in device_result_map.items()]
parametrize_data.extend([(mock_device2, k, v) for k, v in device_result_map.items()])
parametrize_data.extend([(mock_device3, k, v) for k, v in device_result_map3.items()])


@pytest.mark.parametrize("mock_dev,cmd,expected", parametrize_data)
def test_expected_results(mock_dev, cmd, expected):
    """
    Test that the method/cmd in the device actually returns the expected value in the
    device_result_map dict.
    @pytest.mark.parametrize just calls this function for each item in the dictionary.
    """
    # e.g. getattr(mock_dev, 'get_cpm') --> mock_dev.get_cpm
    result = getattr(mock_dev, cmd)()
    print(f"expected-len={len(expected)} | result-len={len(result)}")
    print(result)
    assert result == expected
    print(f"{cmd=}")
    print(f"{expected=}")
    print(f"{result=}")


@pytest.mark.skipif(sys.platform == "win32", reason="does not run on windows")
def test_history_parser_with_file():
    # TypeError: expected str, bytes or os.PathLike object, not _TemporaryFileWrapper
    # Ugh, windows
    f = tempfile.TemporaryFile()
    f.write(b"\xff" * 101)
    h = pygmc.HistoryParser(filename=f)
    assert h.get_data() == []


@pytest.mark.skipif(sys.platform == "win32", reason="does not run on windows")
def test_history_parser_with_file_path():
    # PermissionError on Windows
    f = tempfile.NamedTemporaryFile()
    f.write(b"\xff" * 1)
    fn = f.name
    h = pygmc.HistoryParser(filename=fn)
    assert h.get_data() == []
