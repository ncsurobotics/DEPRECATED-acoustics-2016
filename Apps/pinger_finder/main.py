import ADC
import time
from sys import argv

def Shoot(ADC,len):
	# Used ADC to collect samples
	y,t = ADC.Burst(len)

	# Interpret data
	samples = len - 1
	print("main: %d samples were captured in %.2e seconds. That's %.2f us/sample" % (samples, t, 1e6*t/samples))

	# Return the raw y incase needed for more analysis.
	return y

Samp_len = int(argv[1])

# create an object for ADS7865
ADS7865 = ADC.ADS7865()

"""Instantiating the ADS7865 also ran code for arming all PRU
IO on the beaglebone, as well some built in attributes for 
running commands relevent to the ADC"""


if len(argv) < 3:
	print("main: You did not specify a sample rate")
	SR = input("Please enter a sample rate (samps/sec): ")
else:
	SR = int(argv[2])
ADS7865.Ready_PRUSS_For_Burst(SR)

"""At this point pruss module has been initialized, PRUSS-RAM has been
wiped, and PRU1 firmware is loaded and running (PRU1 will idle until PRU0
comes online to recognize and clear a CINT bit)."""
y = Shoot(ADS7865,Samp_len)
