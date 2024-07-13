import pytest

# import pygmc
from pygmc import cli

# from .mocks import MockConnection
# from .data import data_history_parser

# @mock.patch(
#     "argparse.ArgumentParser.parse_args",
#     return_value=argparse.Namespace(
#         port=None, baudrate=None, actions="save", file_name=Path("a")
#     ),
# )
# def test_command(mock_args):
#     cli.main()


def test_help_command(capsys):
    """GRC check - this actually checks a lot!"""
    help_msg = "usage: cli.py [-h] [-p PORT] [-b BAUDRATE] {usb,live,save}"
    with pytest.raises(SystemExit):
        cli.main(["--help"])
        captured = capsys.readouterr()
        assert "usage: cli.py" in captured.out  # simpleton check
        assert help_msg in captured.out


# def test_save_history():
#     # From: test_device_get_history.py  (D.R.Y. be dammed)
#     # How to create cmd input for test:
#     # start_s = struct.pack(">I", 0)[1:]  # 0=start position
#     # size_s = struct.pack(">H", 110)  # 110=end position
#     # cmd = b"<SPIR" + start_s + size_s + b">>"
#     # and set flash-mem read size to 110
#     cmd_response_map = {
#         b"<SPIR\x00\x00\x00\x00n>>": data_history_parser.raw_history_with_notes1,
#         b"<SPIR\x00\x00\x00\x00\xd3>>": data_history_parser.raw_history_with_notes2,
#         b"<SPIR\x00\x00\x00\x00\n>>": b"\xff" * 10,
#         # break reading when page is all \xff
#     }
#     # device get_history includes columns as first row
#     tidy_result = data_history_parser.raw_history_with_notes1_tidy
#     tidy_result.insert(
#         0, ["datetime", "count", "unit", "mode", "reference_datetime", "notes"]
#     )
#
#     # Mock the connection to a device
#     # Uses recorded responses device
#     mock_connection = MockConnection(cmd_response_map)
#
#     mock_device = pygmc.devices.BaseDevice(mock_connection)
#
#     with unittest.mock.patch("")
