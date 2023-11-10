# PYGMC
Python Geiger–Müller Counter (GMC) USB interface for GQ Electronics brand & others soon™.  

### Installation 
```shell
pip install pygmc
```
[PyGMC on PYPI](https://pypi.org/project/pygmc/)


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
- GMC-300S (confirmed works)
- GMC-300E Plus / GMC-300E+
- GMC-320 Plus / GMC-320+ (confirmed works)
- GMC-320S
- GMC-500
- GMC-500 Plus / GMC-500+ (confirmed works)

Any GQ GMC device following communication protocol RFC1201 or RFC1801.

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