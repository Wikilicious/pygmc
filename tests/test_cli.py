from pygmc import cli

import argparse
from pathlib import Path
from unittest import mock


# @mock.patch(
#     "argparse.ArgumentParser.parse_args",
#     return_value=argparse.Namespace(
#         port=None, baudrate=None, actions="save", file_name=Path("a")
#     ),
# )
# def test_command(mock_args):
#     cli.main()
