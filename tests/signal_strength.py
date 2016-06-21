from os import path

# Get variables for navigating the file system.
root_directory = path.dirname(path.dirname(path.realpath(__file__)))
hc_directory = path.join(root_directory, "host_communication")
pf_directory = path.join(root_directory, "pinger_finder")

# Add important directories to path
import sys
sys.path.insert(0, hc_directory)
sys.path.insert(0, pf_directory)

#####
#####
####

import numpy as np
from acoustics import Acoustics

acoustics = Acoustics()
acoustics.filt.gain_mode(0)
acoustics.filt.filter_mode(1)
acoustics.adc.update_deadband_ms(0)
acoustics.adc.set_sample_len(4e3)
acoustics.adc.update_sample_rate(300e3)
acoustics.adc.update_threshold(0)
acoustics.adc.ez_config(4)

n = 0
while 1:
    # Get some data
    acoustics.adc.get_data()
    
    # 
    for chan in range(acoustics.adc.n_channels):
        max = np.amax(acoustics.adc.y[chan])
        print("%s = %f" % (acoustics.adc.ch[chan], max))
    n += 1
