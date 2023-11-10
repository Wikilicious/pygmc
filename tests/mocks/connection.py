# from ...pygmc import connection
from pygmc import connection


class MockConnection(connection.Connection):
    def __init__(self, cmd_response_map):
        super().__init__()
        self._cmd_response_map = cmd_response_map
        self._cmd = None

    def reset_buffers(self):
        print("reset_buffers")

    def write(self, cmd):
        self._cmd = cmd
        print(cmd)

    def read(self, wait_sleep):
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
