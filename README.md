# PyGMC
[![PyPI - Version](https://img.shields.io/pypi/v/pygmc?logo=python&color=green)](https://pypi.org/project/pygmc/)
[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/Wikilicious/pygmc/python-app.yml?branch=master&logo=github&label=Tests)](https://github.com/Wikilicious/pygmc/tree/master/tests)
[![Read the Docs](https://img.shields.io/readthedocs/pygmc?logo=readthedocs)](https://pygmc.readthedocs.io/)
[![codecov](https://codecov.io/gh/Wikilicious/pygmc/graph/badge.svg?token=9X2V5CWPDM)](https://codecov.io/gh/Wikilicious/pygmc)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/pygmc?logo=pypi)](https://pypi.org/project/pygmc/)

PyGMC is a Python API for Geiger–Müller Counters (GMCs) / Geiger Counters.
It has just one dependency (pyserial) and works on multiple operating
systems: Windows, OSX, Linux. PyGMC aims to be a minimalistic interface -
lowering the installation requirements and allowing the user to build their
own tools on top of a stable package.

- [PYPI](https://pypi.org/project/pygmc/)
- [Documentation](https://pygmc.readthedocs.io/)

## Installation 
```shell
pip install pygmc
```

## Example Usage

#### Jupyter Notebook
<img src="https://github.com/Wikilicious/pygmc/blob/master/pygmc_usage_example_0.9.1.gif" width=500>

#### Auto discover connected GMC, auto identify baudrate, and auto select correct device.
```pycon
import pygmc

gc = pygmc.connect()

ver = gc.get_version()
print(ver)

cpm = gc.get_cpm()
print(cpm)
```

#### Connect to specified GMC device with exact USB port/device/com.
```pycon
import pygmc

gc = pygmc.GMC320('/dev/ttyUSB0')

cpm = gc.get_cpm()
print(cpm)
```

#### Read device history into DataFrame
```pycon
import pandas as pd
import pygmc

gc = pygmc.GMC320('/dev/ttyUSB0')

history = gc.get_history_data()
df = pd.DataFrame(history[1:], columns=history[0])
```
| datetime            |   count | unit   | mode         | reference_datetime   | notes   |
|:--------------------|--------:|:-------|:-------------|:---------------------|:--------|
| 2023-04-19 20:37:18 |      11 | CPM    | every minute | 2023-04-19 20:36:18  |         |
| 2023-04-19 20:38:18 |      20 | CPM    | every minute | 2023-04-19 20:36:18  |         |
| 2023-04-19 20:39:18 |      19 | CPM    | every minute | 2023-04-19 20:36:18  |         |
| 2023-04-19 20:40:18 |      23 | CPM    | every minute | 2023-04-19 20:36:18  |         |
| 2023-04-19 20:41:18 |      20 | CPM    | every minute | 2023-04-19 20:36:18  |         |

### Devices
| Device | Brand | Notes          |
| ------ | ----- |----------------|
| GMC-300S ✔️ | GQ Electronics | A little picky |
| GMC-300E+ / GMC-300E Plus | GQ Electronics |
| GMC-320+ / GMC-320 Plus ✔️ |GQ Electronics | Works smoothly |
| GMC-320S | GQ Electronics |
| GMC-500 | GQ Electronics |
| GMC-500+ / GMC-500 Plus ✔️ | GQ Electronics | Works smoothly |
| GMC-600 | GQ Electronics |
| GMC-600+ / GMC-600 Plus | GQ Electronics |
| GMC-800 | GQ Electronics |
| GMC-SE ✔️ | GQ Electronics | RFC1201 |

(✔️=physically confirmed works)  
Theoretically, any GQ GMC device following communication protocol RFC1201 or RFC1801 should work (e.g. the old GMC-280 )

![](https://www.gqelectronicsllc.com/comersus/store/catalog/300s%20main.jpg)
![](https://www.gqelectronicsllc.com/comersus/store/catalog/GMC-320-Plus_350.png)
![](https://www.gqelectronicsllc.com/comersus/store/catalog/GMC-500HV_350.png)

### Contributors

- ![Thomaz (Owner/Dev)](https://github.com/Wikilicious)
- ![Huy](https://github.com/huyndao)

### Notes
- Alternative Python projects for GQ GMC:
  - [GeigerLog](https://sourceforge.net/projects/geigerlog/)
  - gq-gmc-control
  - gmc
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
