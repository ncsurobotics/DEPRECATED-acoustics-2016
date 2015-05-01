import time
import math
from cmath import phase

import numpy as np
from scipy.fftpack import fft

import boot


def main(ADC, plt):
    # Initialize plotting evironment
    plt.figure()
    plt.subplot(212)
    plt.subplot(211)
    plt.hold(True)

    # Query user to select a channel
    ADC.ADC_Status()

    s = raw_input("Please enter a comma-separated list of chans"
                  + " you want to watch (any # from 0 - 3): ")
    ch_list = map(int, s.split(','))

    # low hanging variables
    fs = ADC.sampleRate
    M = ADC.sampleLength / ADC.n_channels
    fdelta = fs / M
    f = np.arange(0, M * fdelta, fdelta)

    import pdb
    pdb.set_trace()

    # Arm the ADC
    ADC.Ready_PRUSS_For_Burst()

    # Loop sample collection and processing
    while True:

        # Stop gracefully on CTRL+D
        try:

            # Capture a set of samples
            y, t = ADC.Burst()

            # Process simultanous channels
            for ch in ch_list:
                plt.subplot(211)
                plt.plot(y[ch])

                plt.subplot(212)
                plt.plot(f, abs(fft(y[ch])))

            plt.draw()
            time.sleep(0.05)
            plt.subplot(211)
            plt.cla()
            plt.subplot(212)
            plt.cla()

        except KeyboardInterrupt:
            print("Quitting program")
            break

    boot.dearm()
