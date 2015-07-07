import numpy as np
from scipy.fftpack import fft

SAMPLES_PER_CONV = 2

def main(adc, ax_list, recent=False, ask=False):

    # If desired, user will be prompted to hit the Enter key
    # before this snippet of code actually runs.
    if ask:
        print("ADC is armed and ready.")
        raw_input("Press enter when ready...")

    # grabs data. If user set recent to False, the app will run the all
    # the sample collection code involving the PRUSS and trigger logic in
    # order to grab a fresh sample. If user sets recent to True, he is
    # indicating that he has already performed sample collection, and just
    # wants to view the data sitting in the ADC's data storage buffer.
    if recent:
        y = adc.y
    else:
        y = adc.get_data()

    # Plots data
    if len(ax_list) == 1:
        plot_t(adc, y, ax_list[0])
        
    elif len(ax_list) == 2:
        plot_t(adc, y, ax_list[0])
        plot_f(adc, y, ax_list[1])
        
    else:
        raise ValueError("must supply a list of 1 or 2 axes")
    
    # snippet reflects that if user sets recent to false (and thus is grabbing
    # fresh data), he is unable to control the ready state of the ADC, so this
    # snippet of code does that for him.
    if recent==False:
        adc.unready()
        
    # return y


def plot_t(adc, y, ax):
    # get plotting objects
    ax.cla()
    ax.hold(True)

    # Compute parameters
    n = adc.n_channels
    M = y[0].size

    fs = adc.sample_rate

    t = adc.gen_matching_time_array(M)

    # Plot the data
    legend_list = [''] * adc.n_channels
    for chan in range(adc.n_channels):
        ax.plot(t, y[chan])
        legend_list[chan] = adc.ch[chan]
        
    #ax.xlabel('time (seconds)')
    #ax.ylabel('Voltage')
    #ax.title('Voltage vs Time, Fs=%dKHz' % (fs / 1000))

    ax.axis(xmin=0,
            xmax=None,
            ymin=-2.5,
            ymax=2.5)

    ax.legend(legend_list)

def plot_f(adc, y, ax):
    # clear axis and assert hold
    ax.cla()
    ax.hold(True)
        
    # grab all low hanging variables
    fs = adc.sample_rate
    M = adc.sample_length / adc.n_channels
    f_delta = fs / M
    f = np.arange(0, M * f_delta, f_delta)
    
    # Process simultaneous channels
    for chan in range(adc.n_channels):
        
        print("Done. Plotting #2")
        ax.plot(f, abs(fft(y[chan]))/M)

    print("Done Plotting")
    
    ax.axis(xmin=f_delta,
            xmax=fs/2,
            ymin=0,
            ymax=1)
    ax.set_xscale('log')

