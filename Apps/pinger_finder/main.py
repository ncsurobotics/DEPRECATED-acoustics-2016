import ADC
import boot
import time
from sys import argv
import numpy as np


def shoot(ADC, length, CR):
    # Initialize empty variables
    sum = 0
    SAMP_PER_CONV = 2
    SAMP_PER_CYCLE = ADC.n_channels / 2

    # Used ADC to collect samples
    raw_input("Hit enter when you're ready...")
    y, t = ADC.Burst(length, fmt_volts=0)

    # Interpret data

    if ADC.n_channels > 1:
        samples = length
        Ts = t / ((samples / 2) - 1)
        print("")
        print("main: %d samples were captured in %.2e seconds "
              % (samples, t) + "(the first 2 samples are usually a freebies). "
              + "That's %.2f us/samplePair (not counting the freebie pair). "
                % (1e6 * Ts) + "That's a %.2fHz experiment." % (1 / Ts))
        print("")
        print("main: also, (1 - Actual_Rate/Intended_Rate) = %.2f%%."
              % ((1 - (1 / Ts) / CR) * 100))

    ans = raw_input("\nWould you like to see some details about your sample data?\n>>: ")
    if ("y" in ans):
        for chan in range(ADC.n_channels):
            print("Channel %d = %s.\n" % (chan, y[chan]))

    ans = raw_input("\n would you like to plot the data?\n>>: ")

    if ("y" in ans):
        # Load plotting program
        print("Loading Matplotlib library...")
        import matplotlib
        matplotlib.use('GTK')
        import matplotlib.pyplot as plt
        print("...done.")

        # Setup info
        ADC.convRate = eval(raw_input("Warning, actual sample rate may be different than what you specified. Please type in the actuall sample rate if you measured it:\n>> "))
        throughput = ADC.convRate / float(SAMP_PER_CYCLE)  # Hz per channel
        Ts_per_samp = 1 / throughput
        Samps_per_channel = ADC.sampleLength / float(ADC.n_channels)
        time = np.arange(0, Ts_per_samp * Samps_per_channel, Ts_per_samp)

        # Generate plots
        fig, ax = plt.subplots()

        # write n plots to matplotlib
        for n in range(ADC.n_channels):
            ax.plot(time, y[n])

        ax.axis(xmin=0,
                xmax=None,
                ymin=-2**11,
                ymax=2**11)

        ax.set_xlabel('time (seconds)', fontsize=18)
        ax.set_ylabel('code', fontsize=18)
        ax.set_title("%d channel signal capture" % ADC.n_channels, fontsize=18)
        plt.show()

    # Return the raw y incase needed for more analysis.
    return y

########################
#### MAIN PROGRAM ######
########################

# Parse user input: Aquire sample length
Samp_len = int(argv[1])

# Parse user input: Acquire conversion rate
if len(argv) < 3:
    print("main: You did not specify a conversion rate")
    CR = input("Please enter a conversion rate (samps/sec): ")
else:
    CR = float(argv[2])

# Configure there ADC
# create an object for ADS7865
ADS7865 = ADC.ADS7865()
ADS7865.n_channels = 4
"""Instantiating the ADS7865 also ran code for building in attributes for
running commands relevent to the ADC"""
if len(argv) > 3:
    # Configure settings
    # ADS7865.Config([0xF0F,])
    # ADS7865.Config([0xF0F,0x0F0])
    ADS7865.EZConfig(4)
    # ADS7865.Read_Seq()
else:
    print("\nmain: user did not give 4th argument. I will skip over any configuration steps.")

# All settings have been configured. Beaglebone is ready for arming.
ADS7865.Ready_PRUSS_For_Burst(CR)
"""At this point pruss module has been initialized, PRUSS-RAM has been
wiped, and PRU1 firmware is loaded and running (PRU1 will idle until PRU0
comes online to recognize and clear a CINT bit)."""
y = shoot(ADS7865, Samp_len, CR)
boot.dearm()
ADS7865.Close()
