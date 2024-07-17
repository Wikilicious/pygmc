"""PyGMC CLI - Command-Line-Interface"""

import argparse
import datetime
from pathlib import Path

try:
    from .connection import (
        Discovery,
        get_all_usb_devices,
        get_gmc_usb_devices,
    )
    from .connection.udev_rule_check import UDevRuleCheck
    from .devices import (
        auto_get_device_from_discovery_details as _auto_get_device_class,
    )
except ImportError:
    # Most likely error while trying 'python ./some_path/pygmc/cli.py --help'
    # ImportError: attempted relative import beyond top-level package
    # The issue is pygmc/history.py is at same level as pygmc/cli.py
    print("See documentation for correct usage.")
    raise


# Would've liked this in a function... but...
# don't know how to auto-document cli w/o parser out in the open like this... welp...
parser = argparse.ArgumentParser()

parser.add_argument(
    "-p",
    "--port",
    type=str,
    help="The USB port/com/dev e.g. /dev/ttyUSB0 Default=None will auto detect a port.",
    metavar=None,
)
parser.add_argument(
    "-b",
    "--baudrate",
    type=int,
    help="USB communication baudrate Default=None will auto detect the baudrate.",
    metavar=None,
)

subparsers = parser.add_subparsers(
    title="Actions",
    help="PyGMC CLI Actions:" "Common actions for PyGMC",
    dest="actions",
)

# ACTION - list usb's
parser_usb = subparsers.add_parser(
    "usb", help="List USB devices found - filtered for GMC devices"
)
parser_usb.add_argument(
    "--all", action="store_true", help="List all USBs i.e. unfiltered"
)

# ACTION - live cps
parser_live = subparsers.add_parser("live", help="a help")
parser_live.add_argument(
    "-t", "--time", type=int, default=10, help="Time is seconds to live print"
)

# ACTION - save history
parser_history = subparsers.add_parser(
    "save", help="Save device history. Default is a tidy csv file."
)
parser_history.add_argument(
    "-f",
    "--file-name",
    type=Path,
    required=True,
    help="File path. e.g. ~/hist.csv (save history as csv in linux home dir)",
)
parser_history.add_argument(
    "--raw", action="store_true", help="Save raw as-is/unmodified device history."
)


def _list_usb_flow(show_all=False):
    """Print simple information on USB devices."""
    if show_all:
        usbs = get_all_usb_devices()
    else:
        usbs = get_gmc_usb_devices()
    for usb in usbs:
        # would be nice to drop python3.7 support and use f"{value=}" formatting
        print(f"device={usb.device} description={usb.description} hwid={usb.hwid}")


def _get_gc(args):
    """Get geiger-counter-class with provided info from pygmc Discovery."""
    # Ugh... violating D.R.Y.
    discover = Discovery(port=args.port, baudrate=args.baudrate, timeout=5)
    discovered_devices = discover.get_all_devices()
    if len(discovered_devices) == 0:
        # Give user direction in case of brltty udev rule blocking GMC USB device
        brltty_udev_rule_check = UDevRuleCheck()
        # line below logs & prints info for user to resolve USB connection issue
        brltty_udev_rule_check.get_offending_brltty_rules()
        raise ConnectionError("No GMC devices found.")

    device_details = discovered_devices[0]
    device_class = _auto_get_device_class(device_details)
    gc = device_class(
        port=device_details.port, baudrate=device_details.baudrate, timeout=5
    )
    return gc


def _live_flow(args):
    """Print live data (heartbeat)."""
    gc = _get_gc(args)
    print("PyGMC - Live GMC Heartbeat")
    ver = gc.get_version()
    print(f"{ver}")
    datetime_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Start={datetime_str} counts={args.time:,}")
    gc.heartbeat_live_print(count=args.time)

    datetime_finish_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Finish={datetime_finish_str}")


def _cli_flow_save(args):
    """Save device history as tidy CSV or raw data."""
    if args.file_name.exists():
        # Rather give user an error than the alternative... (why you edit my file)
        raise FileExistsError(f"File exists: {args.file_name}")
    gc = _get_gc(args)
    if not args.raw:
        # user want's pygmc tidy data... good Lad or Lass or
        # Shklee or Shklim or Shkler (Futurama)
        gc.save_history_csv(args.file_name)
    else:
        # user is hotshot and want's it raw...
        gc.save_history_raw(args.file_name)


def main(argv=None) -> None:
    """
    CLI entry point.

    Parameters
    ----------
    argv: None | list
        Default=None for correct behavior. Main purpose is for unit-tests.

    Returns
    -------
    None

    """
    args = parser.parse_args(argv)

    if args.actions == "usb":
        _list_usb_flow(show_all=args.all)
    elif args.actions == "live":
        _live_flow(args)
    elif args.actions == "save":
        _cli_flow_save(args)


if __name__ == "__main__":
    main()  # pragma: no cover
