import datetime

import pytest
from freezegun import freeze_time

import pygmc

from ..mocks import MockConnection


@freeze_time(datetime.datetime(2024, 1, 8, 17, 54, 57))
def test_set_datetime_now():
    """Test set_datetime issues cmd of current datetime"""
    actions_cmd_response_map = {
        # datetime.datetime(2024, 1, 8, 17, 54, 57, 662848)
        b"<SETDATETIME\x18\x01\x08\x1169>>": b"\xaa",
    }
    actions_conn = MockConnection(actions_cmd_response_map)
    gc_rfc1201 = pygmc.devices.DeviceRFC1201(actions_conn)
    gc_rfc1201.set_datetime()
    assert actions_conn.get_cmd_calls(b"<SETDATETIME\x18\x01\x08\x1169>>") == 1


def test_raises_set_datetime():
    """Test set_datetime raises RuntimeError if response if wrong"""
    actions_cmd_response_map = {
        # datetime.datetime(2024, 1, 8, 17, 54, 57, 662848)
        b"<SETDATETIME\x18\x01\x08\x1169>>": b"\xab",  # Note the last char!
    }
    actions_conn = MockConnection(actions_cmd_response_map)
    gc_rfc1201 = pygmc.devices.DeviceRFC1201(actions_conn)
    dt = datetime.datetime(2024, 1, 8, 17, 54, 57)
    with pytest.raises(RuntimeError):
        # This is the main test
        gc_rfc1201.set_datetime(datetime_=dt)

    # This is GRC that the cmd was even called
    assert actions_conn.get_cmd_calls(b"<SETDATETIME\x18\x01\x08\x1169>>") == 1
