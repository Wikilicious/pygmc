# from ...pygmc import connection
from pygmc import connection


class MockConnection(connection.Connection):
    """
    Mock Connection class.
    Limitation is it doesn't mock the buffer. That limits the testing of get_at_least.
    """
    def __init__(self, cmd_response_map):
        super().__init__(port="dummy", baudrate=123, serial_connection="DUMMY")
        self._cmd_response_map = cmd_response_map
        self._cmd = None

    def reset_buffers(self):
        print("reset_buffers")

    def write(self, cmd):
        self._cmd = cmd
        print(cmd)

    def read(self, wait_sleep=0.3):
        return self._cmd_response_map[self._cmd]

    def read_until(self, expected=b"", size=None):
        response = self._cmd_response_map[self._cmd]
        cut_off_index = -1
        if expected and size:
            if expected in response:
                expected_index = (
                    response.index(expected) + 1
                )  # pyserial includes the expected value
                cut_off_index = min(expected_index, size)
            else:
                cut_off_index = size
        elif expected:
            if expected in response:
                expected_index = response.index(expected)
                cut_off_index = expected_index
        elif size:
            cut_off_index = size

        return response[0:cut_off_index]

    def read_at_least(self, size, wait_sleep=0.05) -> bytes:
        response = self.read()
        if size > len(response):
            raise TimeoutError(f"{size=} > len({response=}) | would've timed out.")
        return response
