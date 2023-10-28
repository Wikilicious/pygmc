# PYGMC
Python Geiger–Müller Counter package for GQ Electronics brand.  

### Example Usage
```pycon
import pygmc

gc = pygmc.connect(vid="1A86", pid="7523")

ver = gc.get_version()
print(ver)
```


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