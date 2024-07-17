import argparse
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

import pygmc
from pygmc import cli

from .data import data_gmc800, data_history_parser
from .mocks import MockConnection


def _get_gc_for_save_hist_tests():
    # From: test_device_get_history.py  (D.R.Y. be dammed)
    # How to create cmd input for test:
    # start_s = struct.pack(">I", 0)[1:]  # 0=start position
    # size_s = struct.pack(">H", 110)  # 110=end position
    # cmd = b"<SPIR" + start_s + size_s + b">>"
    # and set flash-mem read size to 110
    cmd_response_map = {
        b"<SPIR\x00\x00\x00\x00n>>": data_history_parser.raw_history_with_notes1,
        b"<SPIR\x00\x00\x00\x00\xd3>>": data_history_parser.raw_history_with_notes2,
        b"<SPIR\x00\x00\x00\x00\n>>": b"\xff" * 10,
        # break reading when page is all \xff
    }

    # Mock the connection to a device
    # Uses recorded responses device
    mock_connection = MockConnection(cmd_response_map)

    mock_device = pygmc.devices.BaseDevice(mock_connection)
    # Override mem/read size
    mock_device._flash_memory_size_bytes = 110
    mock_device._flash_memory_page_size_bytes = 110

    return mock_device


def _get_gc_for_live_tests():
    cmd_response_map = data_gmc800.cmd_response_map.copy()
    # This one is tricky... can only test count=1
    cmd_response_map[b"<HEARTBEAT1>>"] = b"\x00\x00\x00'"  # 39
    mock_connection = MockConnection(cmd_response_map)
    mock_device = pygmc.devices.GMC800(None, connection=mock_connection)
    return mock_device


def test_help_command(capsys):
    """GRC check - this actually checks a lot!"""
    help_msg = "usage: cli.py [-h] [-p PORT] [-b BAUDRATE] {usb,live,save}"
    with pytest.raises(SystemExit):
        cli.main(["--help"])
        captured = capsys.readouterr()
        assert "usage: cli.py" in captured.out  # simpleton check
        assert help_msg in captured.out


def test_name_main(capsys):
    """GRC check - this actually checks a lot!"""
    help_msg = "usage: cli.py [-h] [-p PORT] [-b BAUDRATE] {usb,live,save}"
    with pytest.raises(SystemExit):
        cli.main(["--help"])
        captured = capsys.readouterr()
        assert "usage: cli.py" in captured.out  # simpleton check
        assert help_msg in captured.out


@patch("pathlib.Path.exists", raises=FileExistsError)
def test_save_raises_exception_on_file_exists(mock_file):
    """Easier to change a file name than to recover a replaced file"""
    with pytest.raises(FileExistsError):
        cli.main(["save", "-f", "file_already_exists.csv"])


@patch(
    "argparse.ArgumentParser.parse_args",
    return_value=argparse.Namespace(
        port=None,
        baudrate=None,
        actions="save",
        file_name=Path("hist.csv"),
        raw=False,
    ),
)
def test_save_history(mock_args):
    mock_device = _get_gc_for_save_hist_tests()

    patcher_gc = patch("pygmc.cli._get_gc", return_value=mock_device)
    patcher_gc.start()

    with patch("builtins.open", mock_open()) as mock_file:
        cli.main()
        print(mock_file.mock_calls)
        # use position to test hist was saved correctly
        # [call(PosixPath('hist.csv'), 'w', newline=''),
        #  call().__enter__(),
        #  call().write('datetime,count,unit,mode,reference_datetime,notes\r\n'),
        #  call().write(
        #      '2020-07-26 12:45:55,66,CPM,every minute,2020-07-26 12:44:55,\r\n'),
        # ...]

        mock_file.assert_called_once_with(Path("hist.csv"), "w", newline="")

        header = mock_file.mock_calls[2].args[0]
        expected_header = "datetime,count,unit,mode,reference_datetime,notes\r\n"
        assert header == expected_header

        has_a_notes_entry = False
        tidy_count = len(data_history_parser.raw_history_with_notes1_tidy)
        for i in range(tidy_count):
            call = mock_file.mock_calls[i + 3]  # +3 to offset open, enter, header calls
            # eg '2020-07-26 13:01:26,63,CPM,every minute,2020-07-26 13:00:26,&5ABC\r\n'
            data_list = call.args[0].split(",")
            data_count = int(data_list[1])

            tidy = data_history_parser.raw_history_with_notes1_tidy[i]
            expected_count = tidy[1]
            assert data_count == expected_count, print(f"{i=}")

            if tidy[5] is not None:
                # e.g. '&5ABC\r\n'
                data_notes = data_list[5].strip()  # remove return carriage & new line
                assert tidy[5] == data_notes, print(f"{i=}")
                has_a_notes_entry = True  # cross-test

        assert has_a_notes_entry, print("Was expecting at least one notes entry")

    patcher_gc.stop()


@patch(
    "argparse.ArgumentParser.parse_args",
    return_value=argparse.Namespace(
        port=None,
        baudrate=None,
        actions="save",
        file_name=Path("hist.bin"),
        raw=True,
    ),
)
def test_save_raw_history(mock_args):
    mock_device = _get_gc_for_save_hist_tests()

    patcher_gc = patch("pygmc.cli._get_gc", return_value=mock_device)
    patcher_gc.start()

    with patch("builtins.open", mock_open()) as mock_file:
        cli.main()
        print(mock_file.mock_calls)
        mock_file.assert_called_once_with(Path("hist.bin"), "wb")
        data_write = mock_file.mock_calls[2].args[0]
        assert data_write == data_history_parser.raw_history_with_notes1

    patcher_gc.stop()


@patch(
    "argparse.ArgumentParser.parse_args",
    return_value=argparse.Namespace(
        port=None,
        baudrate=None,
        actions="live",
        time=1,
    ),
)
def test_live(mock_args, capsys):
    # This test could be improved a bit
    mock_device = _get_gc_for_live_tests()

    patcher_gc = patch("pygmc.cli._get_gc", return_value=mock_device)
    patcher_gc.start()

    cli.main()

    captured = capsys.readouterr()
    assert "GMC-800" in captured.out  # the print ver
    assert "39" in captured.out  # the CPS value

    patcher_gc.stop()
