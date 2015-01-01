import os

def load():
	# enable all pins to be used as io
	os.system("config-pin overlay cape-universal")
	os.system("config-pin overlay cape-univ-hdmi")
	
def arm():
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
	
def dearm():
	os.system("config-pin P8.27 gpio")
	os.system("config-pin P8.28 gpio")
	os.system("config-pin P8.29 gpio")
	os.system("config-pin P8.39 gpio")
	os.system("config-pin P8.40 gpio")
	os.system("config-pin P8.41 gpio")
	os.system("config-pin P8.42 gpio")
	os.system("config-pin P8.43 gpio")
	os.system("config-pin P8.44 gpio")
	os.system("config-pin P8.45 gpio")
	os.system("config-pin P8.46 gpio")

	os.system("config-pin P9.31 gpio")

	os.system("config-pin P8.11 gpio") # bCONVST
	os.system("config-pin P8.12 gpio") # bWR

	os.system("config-pin P8.15 gpio") # BUSY
