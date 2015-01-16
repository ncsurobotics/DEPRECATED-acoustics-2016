import ADC
import time
from sys import argv

def Shoot(ADC,len):
	# Used ADC to collect samples
	y,t = ADC.Burst(len)

	# Interpret data
	samples = len - 1
	print("main2: %d samples were captured in %.2e seconds. That's %.2f us/sample" % (samples, t, 1e6*t/samples))

	# Return the raw y incase needed for more analysis.
	return y

len = int(argv[1])
ADS7865 = ADC.ADS7865()
ADS7865.Ready_PRUSS_For_Burst()
y = Shoot(ADS7865,len)
