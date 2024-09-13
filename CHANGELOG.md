# PyGMC - Change Log

## Unreleased
- Added model & firmware revision (from device version) to device Discovery
- [BUG] History Parser can now handle 3 and 4 byte counts.
  - Validated 3-byte count via smoke detector with americium-241.
  - The 4-byte count... contact me if you can validate that.
- [BUG] History Parser can now understand tube selection and faulty tube selection.

## 0.14.0 (2024-07-21)
- Separate get_usv_h from get_cpm.
  - Can now pass in a cpm value or leave None for default behavior.
- Added timeout parameter in pygmc.connect & devices.
  - Previously hardcoded to 5 seconds - now a kwarg in all devices and pygmc.connect.
  - Added more unittests - to guarantee kwarg consistency.
- Added command-line-interface (CLI)
  - `pygmc save --file-name hist.csv`
  - `pygmc live`
  - `pygmc --help` (for more usage docs)

## 0.13.0 (2024-05-11)
- Added WiFi commands
  - set_wifi_on, set_wifi_off, set_wifi_ssid, set_wifi_password
- gmcmap.com commands
  - set_gmcmap_user_id, set_gmcmap_counter_id
- Added check for brltty udev rule that blocks USB on Ubuntu.
  - Gives user direction to fix Ubuntu issue connecting to GMC device.
- Reduced scope of get_connection_details()
  - Removed details not available in pyserial connection object.
- Bug fixes
  - Re-added all optional baudrates after learning the default can be modified.

## 0.12.0 (2024-04-16)
- Added save_history_csv()
  - Useful for those wanting to plot their data in Excel. 
- Renamed 'save_history()' to 'save_history_raw()'
- Bug fix: get_usv_h()
  - Added test cases for edge cases.
- Added test cases for GMC800

## 0.11.2 (2024-04-15)
- Bug fix: get_usv_h() now considers all calibration points.
  - Via interpreted empirical data. (Tedious process)
  - https://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=10435
  - Possible edge cases not yet considered due to lacking documentation & dev burnout.

## 0.11.0 (2024-03-09)
- GMC-800 now supported! (This time it's working)
  - Company had incorrect documentation which led to incorrect implementation.
  - Personally purchased device to add support.

## 0.10.0 (2024-02-26)
- Added support for GMC-SE (by: https://github.com/huyndao)

## 0.9.1 (2024-01-20)

## 0.9.0 (2024-01-07)

## 0.8.1 (2023-12-23)

## 0.8.0 (2023-12-10)

## 0.7.1 (2023-12-03)

## 0.7.0 (2023-11-29)

## 0.6.0 (2023-11-25)

## 0.5.4 (2023-11-24)

## 0.5.3 (2023-11-19)

## 0.5.2 (2023-11-12)

## 0.5.1 (2023-11-12)

## 0.4.0 (2023-11-11)

## 0.3.0 (2023-11-10)

## 0.2.2 (2023-11-08)

## 0.2.0 (2023-11-05)

## 0.1.2 (2023-10-28)

## 0.1.1 (2023-10-28)
