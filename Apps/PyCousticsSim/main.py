"""
Major data structs:
	* env: Contains data about the environment... primarily anything related
	to time. list of variables include 
		df -
		dt -
		t_start -
		t_end -
		t -
		loc_pinger - 
		loc_HY - 
	
	* sig: Contains data about the signal itself. 
		f - 
		x - 
		group - 
		group_adc - 
		
		
Major Class structures:
	* Medium:
		.c - speed of sound in medium
		.name - Describes the medium
		
	* Rx:
		.d - spacing between the multiple receiving elements
		.origin - (x,y) coordinate of the array's origin
		.src_loc - (x,y) coordinate of the sound source
		.mediumModel - model containing various parameters for calculating the signal's delay.
"""

import SignalGen
import Rx
import DSP
import Medium
import ADC

import numpy as np
import matplotlib.pyplot as plt
print('-'*50)

env = {}
sig = {}

env['df']	= 30e6 #Hz
env['dt']	= 1/env['df']
env['t_start']	= -1e-3 #seconds
env['t_end']	= 40e-3 #seconds
env['t']		= np.arange(env['t_start'],env['t_end'], env['dt']) #seconds

print("Diagnostics: Analog time domain consists of %d samples from %gs to %gs."
		% (env['t'].size, env['t_start'], env['t_end']))
		
# Specify coordinate for various things
env['loc_pinger'] = np.array([2,10]) #meters
env['loc_HY'] = np.array([0,0]) 
		

#################################################
################ Signal Generator ###############
#################################################
SG = SignalGen.SG()

# Init SG parameters
sig['f'] = 22e3 #Hz
	#Using defaults for start and end time

# Generate the test signal
sig['x'] = SG.Sin(sig['f'],env['t'])
print("Diagnostics: %gkHz test signal. Current config yields %g samples per period."
		% (sig['f']/1000, env['df']/sig['f']))

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
HY = Rx.BiHydrophoneArray()

# Init Rx
HY.d = .03 #meters
HY.origin = env['loc_HY']
HY.src_loc = env['loc_pinger']
HY.mediumModel = MD
HY.maxSpread = 1/sig['f'] #seconds

# Compute the data capture for each channel
sig['group'] = HY.Capture(sig['x'],env['t'],MD)

# Plot the data so far
f1,ax = plt.subplots(2, sharex=True)
ax[0].set_title('Pinger Signal Emission')
ax[1].set_title('Hydrophone input')
ax[0].plot(env['t'],sig['x'])
ax[1].plot(env['t'],sig['group'][0])
ax[1].plot(env['t'],sig['group'][1])

#################################################
###################### ADC ######################
#################################################
ADC = ADC.ADS7865()

ADC.fs = 400e3 #Hz
sig['group_adc'] = ADC.Sample(sig['group'], env['t'])

f2,ax = plt.subplots()
ax.plot(sig['group_adc'][0])
ax.plot(sig['group_adc'][1])
plt.show()
import pdb; pdb.set_trace()
#plt.show()

#################################################
###################### DSP ######################
#################################################