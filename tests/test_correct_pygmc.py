import pathlib

import pygmc


def test_pygmc_path():
    """Sanity check - we're testing the dev package i.e. not some pygmc in our PATH"""
    pygmc_path = pathlib.Path(pygmc.__file__).parent.parent
    test_path = pathlib.Path(__file__).parent.parent
    assert pygmc_path == test_path
