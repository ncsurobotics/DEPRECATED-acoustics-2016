import time
import math
from cmath import phase

import numpy as np
from scipy.fftpack import fft

from bbb import boot


def main(adc, plt):
    # Initialize plotting environment
    fig,axes = plt.subplots(2,1)
    axes[0].hold(True)
    axes[1].hold(True)

    # Query user to select a channel
    adc.adc_status()

    s = raw_input("Please enter a comma-separated list of channels"
                  + " you want to watch (any # from 0 - 3): ")
    ch_list = map(int, s.split(','))

    # low hanging variables
    fs = adc.sample_rate
    M = adc.sample_length / adc.n_channels
    fdelta = fs / M
    f = np.arange(0, M * fdelta, fdelta)

    # Arm the ADC
    adc.ready_pruss_for_burst()

    # Loop sample collection and processing
    while True:
        # Stop gracefully on CTRL+D
        try:
            # Capture a set of samples
            y, _ = adc.burst()

            # Process simultanous channels
            for ch in ch_list:
                print("Plotting #1")
                axes[0].plot(y[ch])
                
                print("Done. Plotting #2")
                axes[1].plot(f, abs(fft(y[ch])))
                plt.pause(0.01)
    
            #import pdb; pdb.set_trace()
            print("Done Plotting")
            axes[0].cla()
            axes[1].cla()

        except KeyboardInterrupt:
            print("Quitting program")
            break

    boot.dearm()
