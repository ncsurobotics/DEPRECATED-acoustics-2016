import csv
import matplotlib.pyplot as plt
import numpy as np

# Initialize a few constants
ref=0; h1=1; h2=2; h3=3;
GLOBAL_PHASE_FACTOR = 1/22e3	 

def main():
	# User Accessible Settings
	PLOT_STUFF = 0 #0 for off. 1 for on.
	
	SEL_REC = 1 			# int from 0 to 3... selects lab recording	
	SAMPLE_RATE = 200e3 	#Hz
	SAMPLE_LENGTH = 64 		# <----- Not used
	
	MAX_TIME_SHIFT = 0.1e-3	#seconds
	PHASE_DELAY = 0.5
	PHASE_DIFF = {'H1': -.4,  #<--- any value from -1 to 1...
			      'H2': 0.4,
				  'H3': -2} #<--- ...but also -2 disables hydrophone.
				  
	PHASE = {'MAX_TIME_SHIFT': MAX_TIME_SHIFT,
		'DELAY': PHASE_DELAY,
		'PHASE_FACTOR': GLOBAL_PHASE_FACTOR,
		'DIFF': PHASE_DIFF}
		


	################################
	######## MAIN CODE ############
	################################
	
	# load recording of hydrophone
	(raw_recording, sampling_interval) =  import_real_data(SEL_REC, SAMPLE_RATE)
	"""raw_recording is an array of voltage values collected over time.
	It represents the signal that the hydrophone array will be receiving"""

	# plot the data
	if PLOT_STUFF:
		plot([raw_recording], "raw_data")
		plt.show()
	
	# Delay the signal according to user's preference
	hydrophone_recording = phase_shift_signals(raw_recording,
		sampling_interval,
		PHASE)
	"""hydrophone_recording is a list of arrays, where as each array is a
	time delayed sampling of raw_recording. For instance:
	---raw_recording[ref]= recording with the reference hydrophone
	---raw_recording[h1]= recording with hydrophone1
	---raw_recording[h2]= recording with hydrophone2
	---raw_recording[h3]= recording with hydrophone3
	"""
	
	if PLOT_STUFF:
		plot(hydrophone_recording, "Output")
		plt.show()
	
	# return data
	return hydrophone_recording
	
	

################################
######## FUNCTIONS ############
################################
	
def import_real_data(SEL, SR):
	#### Determine where .csv file is located
	PATH = "./csv_repo/"
	HEADER_ROW = 3
	FCN_NAME = "import_real_data"
	
	if SEL==0:
		FILE = "07-30--URC-Lab--MiscHpTest5.csv"
	elif SEL==1:
		FILE = "07-30--URC-Lab--MiscHpTest3.csv"
	elif SEL==2:
		FILE = "URC_Lab--ResponseTest--004-2.csv"
	elif SEL==3:
		FILE = "PingerSample--Recording2.csv"
		# This is an ideal sample 
	else:
		print("\n%s: I do not recognize preset %d.\n" % (FCN_NAME, SEL))
		exit(1)
		
	#### parse csv file
	y = []
	t = []
	i = 0
	with open(PATH+FILE) as csvfile:
		readCSV = csv.reader(csvfile,delimiter=',')
	
		for (time, voltage, empty) in readCSV:
			if i > HEADER_ROW:
				y.append(eval(voltage))
				t.append(eval(time))
			i += 1
	
	#### Compute SR equivalent
	Ts = t[1] - t[0]
	fs = 1/Ts
	print("\n%s: This data was collected at %.2eHz.\n" % (FCN_NAME, fs))
	
	index_skip_value = int(round(fs/SR))
	
	y = y[0::index_skip_value]
	
	print("\n%s: Per your request, I was able to parse this " % FCN_NAME
			+ " data as if it was collected at %dKHz sample rate." % (fs/index_skip_value/1000)
			+ " This should be close enough.\n")
	
	return (y, Ts*index_skip_value)
	
def plot(y_list,TITLE):
	fig1,ax1 = plt.subplots()
	ax1.set_title(TITLE)
	for chan in y_list:
		plt.plot(chan)
		
def phase_shift_signals(raw_recording, Ts, PHASE):
	FCN_NAME = "phase_shift_signals"
	
	# Generate n array for turning on and off channels
	n = [0]*4
	y = [0]*4
	n[ref] = 1
	if (PHASE['DIFF']['H1'] <= 1 and PHASE['DIFF']['H1'] >= -1):
		n[h1] = 1
		
		
	if (PHASE['DIFF']['H2'] <= 1 and PHASE['DIFF']['H2'] >= -1):
		n[h2] = 1
		
	if (PHASE['DIFF']['H3'] <= 1 and PHASE['DIFF']['H3'] >= -1):
		n[h3] = 1
		
	# calc ref phase shift
	shift_index_o = shift_indexer(PHASE['DELAY'], PHASE, Ts)
	print("shift = " + str(shift_index_o))
		
	# create beginning and end indices for chopping off the ends of raw data
	n_samples_input = len(raw_recording)
	max_index_shift_value = int(PHASE['MAX_TIME_SHIFT']/Ts)
	
	a = max_index_shift_value + shift_index_o
	b = n_samples_input - max_index_shift_value + shift_index_o - 1
	
	print("\n%s: for y[0:%d], a = %d and b = %d.\n" % (FCN_NAME, n_samples_input, a, b))
	
	print("\n%s: This data was collected at %.2eKHz." % (FCN_NAME, 1/Ts/1000)
		+ " Proceding to shift signals accordingly.\n")
	
	
	# Generate mother array that is ref hydrophone and apl
	y[0] = raw_recording[a:b]
	
	# Generate other arrays relative to ref hydrophone
	for chan in range(h1, h3+1):
		shift_index_chan = shift_indexer(PHASE['DIFF']['H'+str(chan)],PHASE, Ts)
		a_chan = a + shift_index_chan
		b_chan = b + shift_index_chan
		clip = raw_recording[a_chan:b_chan]
		
		y[chan] = n[chan]*np.array(clip)
		if n[chan]:
			print("\n%s: Signal %d was shifted by %d" % (FCN_NAME, chan, shift_index_chan))
		
	return y
		
	

		
def shift_indexer(factor, PHASE, Ts):
	"""shift_indexer: function for getting a shifting index value... for
	shifting discrete signals. 
	- - - factor = decimal number from -1 to 1.
	- - - PHASE['PHASE_FACTOR'] = float represent time shift when PHASE['DELAY'] = 1
	- - - Ts = Sampling interval of data you want to shift."""
	
	return int(  (factor * PHASE['PHASE_FACTOR']) / Ts   )
		
