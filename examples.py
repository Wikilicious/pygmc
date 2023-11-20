import pygmc

gc = pygmc.connect()

ver = gc.get_version()
print(f"{ver=}")

serial = gc.get_serial()
print(f"{serial=}")

cpm = gc.get_cpm()
print(f"{cpm=}")

voltage = gc.get_voltage()
print(f"{voltage=}")

gyro = gc.get_gyro()
print(f"{gyro=}")

datetime = gc.get_datetime()
print(f"{datetime=}")

# heartbeat
gc.heartbeat_on()  # turn on (runs on device until turned off)
seconds = 5
for count in gc.heartbeat_live(seconds):
    print(count)
gc.heartbeat_off()
