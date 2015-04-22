import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

import numpy as np

def gain_test(ADC,filt,plt): "Testing gain"
	"Init some empty data structures"
	legend_list = [''] * ADC_obj.n_channels
	Vpp	= [0] * ADC_obj.n_channels

	print("ut_filters: Gain test. Be sure to:\n"
	+ "  * Attach an input sinusoid on all four channels.\n"
	+ "  * Input frequency is low compared to the cutoff frequency.\n"
	+ "  * Input signal amplitude < 156mV.\n"
	+ "  * Ensure settings are correct on ADC.\n")
	
	"Arm the ADC"
	ADC.Ready_PRUSS_For_Burst()
	
	"get user confirmation"
	u = raw_input("ut_filters: Hit enter to begin the test. Or q to quit.\n>> ")
	if (u is 'q'):
		return;
		
	"activate plotting option if available"
	if plt:
		plt.ioff()
		fig,axes = plt.subplots(4,4,sharex=True)
	
	"Iterate analysis 16 times"
	for (n in range(16)): #16=num of possible gain values
		if plt:
			"hold the axis"
			ax.hold(True)
			
		"Select gain mode
		filt.GainMode(n)
		
		"Get samples"
		y = ADC.Burst()
			
		"Analyze each sample"
		for chan in range(ADC.n_channels):
			"Compute amplitude"
			Vpp[chan] = np.amax(y[chan]) - np.amin(y[chan])
		
			"Compute plot"
			if plt:
				"Generate time array
				if chan is 0:
					M = y[0].size
					t = ADC_obj.Generate_Matching_Time_Array(M)
		
				"Record plot name"
				legend_list[chan] = ADC.ch[chan]
				
				"plot
				plt.plot(t,y[chan])
		
		"Show off math"
		print("ut_filters: Your amplitudes for G = %d were:" % n)
		for chan in range(ADC.n_channels):
			print("  %s: %.2fV " % (ADC.ch[chan], Vpp[chan]))
		print("")
		
		"slap on the plot legend & name"
		ax.title('Signal at G = %d' % n)
		ax.legend(legend_list)
		
	"Show plt"
	if plt:
		plt.ion()
		plt.show()
	
	return:
		
		
	

def test(ADC=None, filt=None, plt=None):
	if ADC is None:
		print("ut_filters: You haven't activated your ADC yet!")
		return;

	if filt is None:
		print("ut_filters: You haven't activated your LTC1564s yet!")
		return;
		
	u = raw_input('Testing (g)ain ctrl or (f)requency ctrl?\n>> ')
	
	if (u is 'g'):
		gain_test(ADC,filt,plt)
			
		
		