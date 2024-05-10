import logging
import re
from pathlib import Path

logger = logging.getLogger("pygmc.connection.udev_rule_check")


class UDevRuleCheck:
    """Check for offending Ubuntu udev rule blocking access to the GMC."""

    def __init__(self):
        """User troubleshooting class to identify offending Ubuntu udev rules."""
        # path to do .rglob on
        self._main_udev_rules_dir = Path("/usr/lib/udev/")
        # other possible paths - perhaps future expanded udev rule check?
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
        self._brltty_re = '\nENV{PRODUCT}=="1a86/7523/\\*", ENV{BRLTTY_BRAILLE_DRIVER}="bm", GOTO="brltty_usb_run"'

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


        TLDR: Run cmd `sudo apt remove brltty`
        """

    def get_offending_brltty_rules(self):
        """Get offending brltty udev rules."""
        paths = self._main_udev_rules_dir.rglob(self._brltty_path_glob)
        offending_brltty_udev_paths = []

        for path in paths:
            m = re.search(self._brltty_re, path.read_text())
            if not m:
                continue  # i.e. go to next path

            logger.debug(m)
            offending_brltty_udev_paths.append(str(path))

            msg = f"Found offending brltty udev rule in path:\n{path}"
            msg += "\n\n"
            msg += self._brltty_user_msg
            print(msg)  # petty enough to additionally print?
            logger.error(msg)

        return offending_brltty_udev_paths
