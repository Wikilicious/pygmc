# PyGMC
[![](https://img.shields.io/pypi/v/pygmc.svg)](https://pypi.org/project/pygmc/)
[![Read the Docs](https://img.shields.io/readthedocs/pygmc)](https://pygmc.readthedocs.io/)
[![](https://github.com/Wikilicious/pygmc/workflows/Python%20application/badge.svg)](https://github.com/Wikilicious/pygmc/actions)
[![GitHub](https://img.shields.io/github/license/Wikilicious/pygmc)](https://github.com/Wikilicious/pygmc/blob/master/LICENSE)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/pygmc)](https://pypi.org/project/pygmc/)

PyGMC is a Python API for Geiger–Müller Counters (GMCs) / Geiger Counters.
It has just one dependency (pyserial) and works on multiple operating
systems: Windows, OSX, Linux. PyGMC aims to be a minimalistic interface -
lowering the installation requirements and allowing the user to build their
own tools on top of a stable package.

- [PYPI](https://pypi.org/project/pygmc/)
- [Documentation](https://pygmc.readthedocs.io/)

### Installation 
```shell
pip install pygmc
```


### Example Usage
```pycon
import pygmc

gc = pygmc.connect()

ver = gc.get_version()
print(ver)

cpm = gc.get_cpm()
print(cpm)
```

### Devices
| Device | Brand | Notes |
| ------ | ----- | ----- |
| GMC-300S ✔️ | GQ Electronics | Required lower baudrate to work |
| GMC-300E+ / GMC-300E Plus | GQ Electronics |
| GMC-320+ / GMC-320 Plus ✔️ |GQ Electronics | Works smoothly |
| GMC-320S | GQ Electronics |
| GMC-500 | GQ Electronics |
| GMC-500+ / GMC-500 Plus ✔️ | GQ Electronics | Works smoothly |
| GMC-600 | GQ Electronics |
| GMC-600+ / GMC-600 Plus | GQ Electronics |
| GMC-800 | GQ Electronics |

(✔️=physically confirmed works)  
Theoretically, any GQ GMC device following communication protocol RFC1201 or RFC1801 should work (e.g. the old GMC-280 )

![](https://www.gqelectronicsllc.com/comersus/store/catalog/300s%20main.jpg)
![](https://www.gqelectronicsllc.com/comersus/store/catalog/GMC-320-Plus_350.png)
![](https://www.gqelectronicsllc.com/comersus/store/catalog/GMC-500HV_350.png)


### Notes
- Alternative Python projects for GQ GMC:
  - [GeigerLog](https://sourceforge.net/projects/geigerlog/)
  - [gq-gmc-control](https://github.com/chaim-zax/gq-gmc-control)
  - [gmc](https://gitlab.com/slippers/gmc)
- Device website [GQ Electronics](https://gqelectronicsllc.com/) Seattle, WA
  - Not affiliated in any way.


---
#### Known Issues
- Ubuntu Issue
    - Ubuntu requires fixing a bug to be able to connect to any GQ GMC device.  
USB devices use VID (vendor ID) and PID (Divice ID)... It is common for unrelated devices to use a common manufacture for their USB interface.
The issue with Ubuntu is that it assumes `1A86:7523` is a "Braille" device (for the blind) and, ironically, blindly treats it as such. 
    - This causes the GQ GMC device to not connect. 
- Ubuntu fix
  - The fix is to comment out the `udev` rule that does this. The text file may be in two places.
    - `/usr/lib/udev/85-brltty.rules`
    - `/usr/lib/udev/rules.d/85-brltty.rules`
  - Find the line below and comment it out.
    - `ENV{PRODUCT}=="1a86/7523/*", ENV{BRLTTY_BRAILLE_DRIVER}="bm", GOTO="brltty_usb_run"`
  - We see Ubuntu assumes `1A86:7523` is a `Baum [NLS eReader Zoomax (20 cells)]` device.
