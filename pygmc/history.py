import datetime
import logging
import struct
from io import BufferedIOBase

logger = logging.getLogger(__name__)


class HistoryParser:
    """Parse GQ GMC device history data."""

    def __init__(self, data=None, filename=None):
        """
        Parse GMC flash memory saved history data.

        Parameters
        ----------
        data: bytes | None
            Input raw bytes of history
            If left None, filename must be provided.
        filename: str | BufferedIOBase | None
            Path to file to open or an BufferedIOBase i.e. open(file, 'rb')
            data takes priority over filename.

        """
        if isinstance(data, bytes):
            self._raw = _BinFile(data)
        elif isinstance(filename, BufferedIOBase):
            self._raw = filename
        elif filename:
            self._raw = open(filename, "rb")
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
        if len(com_str) == 1:
            value = struct.unpack(">B", com_str)[0]
        elif len(com_str) == 2:
            value = struct.unpack(">H", com_str)[0]
        elif len(com_str) == 3:
            # 3 byte data... 2**24 = 16,777,216 max
            value = int.from_bytes(com_str, "big")
            # value = struct.unpack(">I", com_str)[0]
        elif len(com_str) == 4:
            # 4 byte data... really?! Ok, sure
            value = int.from_bytes(com_str, "big")
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
        """The core parser flow."""
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
                        elif com3 == 3:
                            # three byte count number
                            # max CPM 16,777,216 (including 0) 2^24
                            data = self._raw.read(3)
                            n = self._get_count_data(data)
                            self._add_to_df(n)
                        elif com3 == 4:
                            # four byte count number? 2^32
                            # The last number you'll see! Guaranteed!
                            data = self._raw.read(4)
                            n = self._get_count_data(data)
                            self._add_to_df(n)
                        elif com3 == 5:
                            # tube selection: 0=both
                            tube = self._raw.read(1)
                            # My GMC-500+ had instances where it failed to record tube
                            if tube == b"U":
                                # An unknown bug... start of cmd w/o tube specified
                                # was expecting \x00 (both) or 1 or 2
                                i = self._raw.tell()  # current read position
                                self._raw.seek(i - 1)  # go back one byte
                                # have to read more than 1 byte to get here i.e. not neg
                            # perhaps add tube selection as column?
                        else:
                            # Whoa! You just hit a rare event
                            # Counts: 85 then 170 then not 0, 1, 2, 3, 4, 5
                            # Though a low number here would be a suspicious undocumented
                            # feature/cmd... let's still treat them as counts to raise
                            # the attention of a user to file an issue.
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
        if self._eof_check > 0:
            # list[:-0] is empty
            return self._data[: -self._eof_check]
        return self._data

    def get_columns(self):
        """Get column names."""
        return self._columns


class _BinFile:
    """A dummy class so raw bytes and BufferedIOBase can be treated the same."""

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

    def tell(self):
        """Return current stream position."""
        return self._i

    def seek(self, i):
        """
        Change stream position.

        Change the stream position to the given byte offset. The offset is
        interpreted relative to the position indicated by whence.  Values
        for whence are:

        * 0 -- start of stream (the default); offset should be zero or positive
        * 1 -- current stream position; offset may be negative
        * 2 -- end of stream; offset is usually negative

        Return the new absolute position.

        Parameters
        ----------
        i int
            Position to offset to.

        Returns
        -------

        """
        self._i = i
        return self._i
