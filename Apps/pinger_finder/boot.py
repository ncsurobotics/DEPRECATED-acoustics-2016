import os

# enable all pins to be used as io
os.system("config-pin overlay cape-universal")
os.system("config-pin overlay cape-univ-hdmi")

os.system("config-pin P8.27 pruin")
os.system("config-pin P8.28 pruin")
os.system("config-pin P8.29 pruin")
os.system("config-pin P8.39 pruin")
os.system("config-pin P8.40 pruin")
os.system("config-pin P8.41 pruin")
os.system("config-pin P8.42 pruin")
os.system("config-pin P8.43 pruin")
os.system("config-pin P8.44 pruin")
os.system("config-pin P8.45 pruin")
os.system("config-pin P8.46 pruin")

os.system("config-pin P9.31 pruin")


os.system("config-pin P8.11 pruout") # bCONVST
os.system("config-pin P8.12 pruout") # bWR

os.system("config-pin P8.15 pruin") # BUSY
