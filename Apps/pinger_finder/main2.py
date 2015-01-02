import ADC
import time
from sys import argv

def Shoot(ADC,len):
	y,t = ADC.Burst(len)
	print("That took %s seconds. That's %s s/sample" % (t, t/(len-1)))
	return y

len = int(argv[1])
ADS7865 = ADC.ADS7865()
ADS7865.Ready_PRUSS_For_Burst()
y = Shoot(ADS7865,len)