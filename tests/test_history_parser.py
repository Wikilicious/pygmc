import pygmc

from .data import data_history_parser


def test_history_parser_save_modes():
    h = pygmc.HistoryParser(data=data_history_parser.raw_history_with_save_modes)
    tidy_data = h.get_data()
    assert tidy_data == data_history_parser.raw_history_with_save_modes_tidy


def test_history_parser_note_decode_exception():
    raw_data = b"\xff" * 6 + b"\x55\xaa\x02\x01\x80"
    h = pygmc.HistoryParser(data=raw_data)
    assert h.get_data() == []


def test_history_parser_count_same_as_cmd():
    # consider improving parser to include 85 when it is last byte
    # currently it doesn't make it into tidy data

    raw_data = b"U\xaa\x00\x18\x01\x19\x15\x05\x0cU\xaa\x02\x55"
    h = pygmc.HistoryParser(data=raw_data)
    assert h.get_data() == []

    raw_data += b"\x12"  # add an 18 count to trigger adding 85 and 18
    h = pygmc.HistoryParser(data=raw_data)
    tidy_data = h.get_data()
    assert tidy_data[0][1] == 85
    assert tidy_data[1][1] == 18
