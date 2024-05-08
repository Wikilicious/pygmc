import re
from pathlib import Path
import logging


logger = logging.getLogger("pygmc.connection.udev_rule_check")


class UDevRuleCheck:
    def __init__(self):
        # path to do .rglob on
        self._main_udev_rules_dir = Path("/usr/lib/udev/")
        # other possible paths
        self._other_udev_rules_dirs = [
            Path("/etc/udev/rules.d"),
            Path("/lib/udev/rules.d"),
            Path("/run/udev/rules.d"),
            Path("/var/run/udev/rules.d"),
        ]
        # the offending path e.g. /usr/lib/udev/rules.d/85-brltty.rules
        self._brltty_path_glob = "*brltty*"
        # the \n in front is because re.search and we want to match the line
        # if it's not commented out
        self._brltty_re = '\nENV{PRODUCT}=="1a86/7523/\*", ENV{BRLTTY_BRAILLE_DRIVER}="bm", GOTO="brltty_usb_run"'

        self._brltty_user_msg = """
        There is a linux 'udev' rule matching a GQ GMC device that is blocking the GMC
        from being accessed. It's a popular Ubuntu bug. See: 
        https://askubuntu.com/questions/1403705/dev-ttyusb0-not-present-in-ubuntu-22-04
        
        Solutions are listed below from easiest to more involved.
        1) Run the command `sudo apt remove brltty`
            - If you are able to see, this will remove the braille (for the blind) display
            program that Ubuntu is blindly mapping the GMC to.
        2) Find the following line and comment it out.
            - ENV{PRODUCT}=="1a86/7523/*", ENV{BRLTTY_BRAILLE_DRIVER}="bm", GOTO="brltty_usb_run"
            - Most commonly found in: /usr/lib/udev/rules.d/85-brltty.rules
        """

    @staticmethod
    def finditer_with_line_numbers(pattern: str, paths, flags: int = 0):
        """
        Get (path, lineno, re-match) from a list of files and pattern.

        Parameters
        ----------
        pattern: str
            The regex pattern.
        paths: list
            List of pathlib.Path - paths to search for regex.
        flags: int
            Python re flags

        Returns
        -------
        generator
            Tuple of (path, lineno, re-match)

        """
        # modified copy from
        # https://stackoverflow.com/questions/16673778/python-regex-match-in-multiline-but-still-want-to-get-the-line-number

        if len(paths) == 0:
            return []

        for path in paths:
            if not path.exists():
                continue
            if not path.is_file():
                continue

            try:
                string = path.read_text(encoding="utf8")
            except UnicodeError as e:  # noqa
                continue

            matches = list(re.finditer(pattern, string, flags))
            if not matches:
                continue

            end = matches[-1].start()
            # -1 so a failed 'rfind' maps to the first line.
            newline_table = {-1: 0}
            for i, m in enumerate(re.finditer("\\n", string), 1):
                # Don't find newlines past our last match.
                offset = m.start()
                if offset > end:
                    break
                newline_table[offset] = i

            # Failing to find the newline is OK, -1 maps to 0.
            for m in matches:
                newline_offset = string.rfind("\n", 0, m.start())
                line_number = newline_table[newline_offset]
                yield path, line_number, m

    def get_offending_brltty_rules(self):
        paths = self._main_udev_rules_dir.rglob(self._brltty_path_glob)
        # yields (path, line_number, m)
        offending_matches = self.finditer_with_line_numbers(
            pattern=self._brltty_re, paths=paths
        )
        for match in offending_matches:
            msg = f"Found {self._brltty_re} in \n{match[0]} \nline#: {match[1]}"
            msg += "\n\n"
            msg += self._brltty_user_msg
            print(msg)
            logger.error(msg)
