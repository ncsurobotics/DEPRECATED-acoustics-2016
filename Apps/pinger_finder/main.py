import ADC
import boot
import time
from sys import argv
#import matplotlib
#matplotlib.use('GTK')

#import matplotlib.pyplot as plt

def Shoot(ADC,len,SR):
	# Initialize empty variables
	sum = 0
	

	# Used ADC to collect samples
	raw_input("Hit enter when you're ready...")
	y,t = ADC.Burst(len)

	# Interpret data
	
	if ADC.n_channels == 2:
		samples = len - 1
		Ts = t/ ((samples/2)-1)
		print("")
		print("main: %d samples were captured in %.2e seconds "
			% (samples,t) + "(the first 2 samples are usually a freebies). "
			+ "That's %.2f us/samplePair (not counting the freebie pair). "
			% (1e6*Ts) + "That's a %.2fHz experiment." % (1/Ts))
		print("")
		print("main: also, (1 - Actual_Rate/Intended_Rate) = %.2f%%." 
			% ((1-(1/Ts)/SR)*100))

	ans = raw_input("\nWould you like to see some details about your sample data?\n>>: ") 
	if ("y" in ans):
		for chan in range(ADC.n_channels):
			print("Channel %d = %s.\n" % (chan, y[chan]))

	ans = raw_input("\n would you like to plot the data?\n>>: ")

	if ("y" in ans):
		fig,ax = plt.subplots()
		ax.plot(y[0])
		ax.plot(y[1])
		ax.axis(xmin=0,
				xmax=None,
				ymin=-2**11,
				ymax=2**11)
				
		
		plt.show()

	# Return the raw y incase needed for more analysis.
	return y

########################
#### MAIN PROGRAM ######
########################

# Parse user input: Aquire sample length
Samp_len = int(argv[1])

# Parse user input: Acquire sampling rate
if len(argv) < 3:
	print("main: You did not specify a sample rate")
	SR = input("Please enter a sample rate (samps/sec): ")
else:
	SR = int(argv[2])

### Configure there ADC
# create an object for ADS7865
ADS7865 = ADC.ADS7865()
ADS7865.n_channels = 4
"""Instantiating the ADS7865 also ran code for building in attributes for 
running commands relevent to the ADC"""
if len(argv) > 3:
	# Configure settings
	#ADS7865.Config([0xF0F,])
	#ADS7865.Config([0xF0F,0x0F0])
	for i in range(1,11):
		print(11-i)
		time.sleep(.1)
	print("configuring")
	ADS7865.EZConfig(4)
	#ADS7865.Read_Seq()
else:
	print("\nmain: user did not give 4th argument. I will skip over any configuration steps.")

# All settings have been configured. Beaglebone is ready for arming.
ADS7865.Ready_PRUSS_For_Burst(SR)
"""At this point pruss module has been initialized, PRUSS-RAM has been
wiped, and PRU1 firmware is loaded and running (PRU1 will idle until PRU0
comes online to recognize and clear a CINT bit)."""
y = Shoot(ADS7865,Samp_len,SR)
boot.dearm()
ADS7865.Close()
