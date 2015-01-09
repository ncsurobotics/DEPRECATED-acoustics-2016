"""
Major data structs:
	* env: Contains data about the environment... primarily anything related
	to time. list of variables include 
		df -
		dt -
		t_start -
		t_end -
		t -
	
	* sig: Contains data about the signal itself. 
		f - 
		x - 
		
		
Major Class structures:
	* Medium:
		.c - speed of sound in medium
		.name - Describes the medium
"""

import SignalGen
import Hydrophones
import DSP
import Medium

import numpy as np
import matplotlib.pyplot as plt
print('-'*50)

env = {}
sig = {}

env['df']	= 0.5e6 #Hz
env['dt']	= 1/env['df']
env['t_start']	= -1000 * env['dt']
env['t_end']	= 80e-3 #seconds
env['t']		= np.arange(env['t_start'],env['t_end'], env['dt']) #seconds

print("Diagnostics: Analog time domain consists of %d samples from %gs to %gs."
		% (env['t'].size, env['t_start'], env['t_end']))
		

#################################################
################ Signal Generator ###############
#################################################
SG = SignalGen.SG()

# Init SG parameters
sig['f'] = 22e3 #Hz
	#Using defaults for start and end time

# Generate the test signal
sig['x'] = SG.Sin(sig['f'],env['t'])

#DEBUG plt.plot(env['t'],sig['x'])
#DEBUG plt.show()

#################################################
#################### Medium #####################
#################################################
MD = Medium.Water()

# Init medium parameters
print("Medium: c_%s = %g m/s." % (MD.name, MD.c))

#################################################
################# Hydrophone Rx #################
#################################################
HY = Rx.2HydrophoneArray()

# Init Rx
