import tempfile
from pathlib import Path

from pygmc.connection.udev_rule_check import UDevRuleCheck

text_brltty_commented_out = """
# Device: 16C0:05E1
# Canute [all models]
ENV{PRODUCT}=="16c0/5e1/*", ENV{BRLTTY_BRAILLE_DRIVER}="cn", GOTO="brltty_usb_run"

# Device: 1A86:7523
# Baum [NLS eReader Zoomax (20 cells)]
# ENV{PRODUCT}=="1a86/7523/*", ENV{BRLTTY_BRAILLE_DRIVER}="bm", GOTO="brltty_usb_run"

# Device: 1C71:C004
# BrailleNote [HumanWare APEX]
ENV{PRODUCT}=="1c71/c004/*", ENV{BRLTTY_BRAILLE_DRIVER}="bn", GOTO="brltty_usb_run"
"""


text_brltty_match = """
# Device: 16C0:05E1
# Canute [all models]
ENV{PRODUCT}=="16c0/5e1/*", ENV{BRLTTY_BRAILLE_DRIVER}="cn", GOTO="brltty_usb_run"

# Device: 1A86:7523
# Baum [NLS eReader Zoomax (20 cells)]
ENV{PRODUCT}=="1a86/7523/*", ENV{BRLTTY_BRAILLE_DRIVER}="bm", GOTO="brltty_usb_run"

# Device: 1C71:C004
# BrailleNote [HumanWare APEX]
ENV{PRODUCT}=="1c71/c004/*", ENV{BRLTTY_BRAILLE_DRIVER}="bn", GOTO="brltty_usb_run"
"""


def test_non_match_brltty_check():
    udrc = UDevRuleCheck()
    with tempfile.NamedTemporaryFile(mode="w") as fp:
        fp.write(text_brltty_commented_out)
        fp.seek(0)
        p = Path(fp.name)
        p_dir = p.parent
        p_name = p.name

        udrc._main_udev_rules_dir = p_dir  # override to tempfile dir '/tmp'
        udrc._brltty_path_glob = str(p_name)

        offending_udev = udrc.get_offending_brltty_rules()
        assert len(offending_udev) == 0

        fp.close()


def test_match_brltty_check():
    udrc = UDevRuleCheck()
    with tempfile.NamedTemporaryFile(mode="w") as fp:
        fp.write(text_brltty_match)
        fp.seek(0)
        p = Path(fp.name)
        p_dir = p.parent
        p_name = p.name

        udrc._main_udev_rules_dir = p_dir  # override to tempfile dir '/tmp'
        udrc._brltty_path_glob = str(p_name)

        offending_udev = udrc.get_offending_brltty_rules()
        assert len(offending_udev) == 1

        fp.close()
