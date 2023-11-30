import datetime
import logging
import struct
from io import BufferedIOBase

logger = logging.getLogger(__name__)


class HistoryParser:
    """Parse GQ GMC device history data."""

    def __init__(self, data):
        """
        Parse GMC flash memory saved history data.

        Parameters
        ----------
        data: bytes | str | BufferedIOBase
            Input raw bytes of history, or file path as str, or an BufferedIOBase
            i.e. open(file, 'rb')

        """
        if isinstance(data, bytes):
            self._raw = _BinFile(data)
        elif isinstance(data, str) and len(data) < 32_767:
            # Ugh...
            self._raw = open(data, "rb")
        elif isinstance(data, BufferedIOBase):
            self._raw = data
        else:
            raise TypeError

        self._datetime = None
        self._unit = None
        self._mode = None
        self._columns = [
            "datetime",
            "count",
            "unit",
            "mode",
            "reference_datetime",
            "notes",
        ]
        self._data = []
        # notes = [(datetime, notes), ...]
        self._notes = []
        # context = [(reference_datetime, unit, mode)]
        self._context_history = []
        # reference time
        self._last_reference_datetime = None
        # last notes - add to next data input and reset to blank
        self._last_note = None
        self._eof_check = 0

        # parse
        self._parse()

    def _get_count_data(self, com_str):
        if len(com_str) > 4:
            # Not sure what my thinking was here... remove?
            return None
        if len(com_str) == 1:
            value = struct.unpack(">B", com_str)[0]
        elif len(com_str) == 2:
            value = struct.unpack(">H", com_str)[0]
        else:
            msg = "Unexpected len for count data: len={}".format(len(com_str))
            raise ValueError(msg)

        # we may be at end of file...
        # treat several consecutive 255 as end of file
        if value == 255:
            self._eof_check += 1
        else:
            self._eof_check = 0
        return value

    def _get_context(self, data):
        save_mode = data[8]
        if save_mode == 0:
            unit = "OFF"
            mode_str = "off"
        elif save_mode == 1:
            unit = "CPS"
            mode_str = "every second"
        elif save_mode == 2:
            unit = "CPM"
            mode_str = "every minute"
        elif save_mode == 3:
            unit = "CPM"
            mode_str = "every hour"
        elif save_mode == 4:
            unit = "CPS"
            mode_str = "every second - threshold"
        elif save_mode == 5:
            unit = "CPM"
            mode_str = "every minute - threshold"
        else:
            msg = "Unknown save mode: {}".format(save_mode)
            logger.error(msg)
            return None, "Unknown", "Unknown"

        year = int("20{0:2d}".format(data[0]))
        month = int("{0:2d}".format(data[1]))
        day = int("{0:2d}".format(data[2]))
        hour = int("{0:2d}".format(data[3]))
        minute = int("{0:2d}".format(data[4]))
        second = int("{0:2d}".format(data[5]))
        ref_dt = datetime.datetime(year, month, day, hour, minute, second)
        self._last_reference_datetime = ref_dt
        logger.debug(
            "Context: unit={} mode={} reference_time={}".format(unit, mode_str, ref_dt)
        )
        return ref_dt, unit, mode_str

    def _set_context(self, ref_dt, unit, mode):
        self._datetime = ref_dt
        self._unit = unit
        self._mode = mode
        self._context_history.append((ref_dt, unit, mode))

    def _add_to_df(self, count):
        # It appears that a ref time is dumped out then the next data entry
        # is put in after <mode> time so we add a time delta before recording
        # the entry in the df
        # BUT... it's useful to be able to match context timestamp to df!!! change?
        if self._datetime is None:
            # add count data with other fields as None?
            return
        if "threshold" in self._mode:
            # really hope GMC outputs reference time for every threshold output
            # TODO: investigate.
            pass
        if "second" in self._mode:
            self._datetime += datetime.timedelta(seconds=1)
        elif "minute" in self._mode:
            self._datetime += datetime.timedelta(minutes=1)
        elif "hour" in self._mode:
            self._datetime += datetime.timedelta(hours=1)

        # header=["datetime", "count", "unit", "mode", "reference_datetime", "note"]
        if self._last_note:
            note = self._last_note
            # i.e. add note to very next count data
            self._last_note = None
        else:
            note = None

        data = (
            self._datetime,
            count,
            self._unit,
            self._mode,
            self._last_reference_datetime,
            note,
        )
        self._data.append(data)

        # check suspicious 255 values
        # Ok, Hubert Farnsworth, Rick Sanchez...
        # Only you two are capable of making 100 contiguous counts of 255
        if self._eof_check > 100:
            logger.debug("EOFError raised - 100 contiguous counts of 255")
            raise EOFError

    def _add_notes(self, note):
        # um... guessing here
        try:
            note = note.decode("utf8")
            self._notes.append((self._datetime, note))
            self._last_note = note
        except UnicodeDecodeError:
            if self._eof_check > 5:
                logger.warning(
                    "Possible end of file... unable to decode note: {}".format(note)
                )

    def _parse(self):
        # The meat of the matter...
        try:
            while True:
                # command
                com_str = self._raw.read(1)
                if len(com_str) == 0:
                    # nothing left to read...
                    # use raise as exit ship...
                    raise EOFError  # noqa

                com = ord(com_str)
                # 0x55 (85) Could be context, 2-byte count, notes, OR a regular count
                if com == 85:
                    com_str2 = self._raw.read(1)
                    com2 = ord(com_str2)
                    # 0xaa (170)
                    if com2 == 170:
                        com_str3 = self._raw.read(1)
                        com3 = ord(com_str3)
                        # 0x00 (0)
                        # context data - save mode & datetime
                        if com3 == 0:
                            data = self._raw.read(9)
                            ref_dt, unit, mode = self._get_context(data)
                            self._set_context(ref_dt, unit, mode)
                        # 0x01 (1)
                        elif com3 == 1:
                            # two byte count number
                            # so... max CPM is 65,535?
                            data = self._raw.read(2)
                            self.example = data
                            n = self._get_count_data(data)
                            self._add_to_df(n)
                        # 0x02 (2)
                        elif com3 == 2:
                            # Notes flag
                            # bytes size of notes (so max notes size is 255?)
                            data = self._raw.read(1)
                            size = ord(data)
                            notes = self._raw.read(size)
                            self._add_notes(notes)
                        else:
                            # Whoa! You just hit a rare event
                            # Counts: 85 then 170 then not 0 nor 1 nor 2.
                            # Treat them as counts
                            n = self._get_count_data(com_str)
                            self._add_to_df(n)
                            n = self._get_count_data(com_str2)
                            self._add_to_df(n)
                            n = self._get_count_data(com_str3)
                            self._add_to_df(n)
                    else:
                        # Turns out com=85 was a count and not a command flag
                        # Need to log them as counts, then
                        n = self._get_count_data(com_str)
                        self._add_to_df(n)
                        n = self._get_count_data(com_str2)
                        self._add_to_df(n)
                else:
                    n = self._get_count_data(com_str)
                    self._add_to_df(n)
        except EOFError:
            # we hit end of file
            logger.info("End of history data")
            self._raw.close()

    def get_data(self):
        """Get parsed data."""
        return self._data

    def get_columns(self):
        """Get column names."""
        return self._columns


class _BinFile:
    def __init__(self, data):
        self.data = data
        self._i = 0
        self._len_data = len(data)

    def read(self, size):
        tmp = self.data[self._i : self._i + size]
        self._i += size
        if self._i > self._len_data:
            raise EOFError
        return tmp

    def close(self):
        pass
