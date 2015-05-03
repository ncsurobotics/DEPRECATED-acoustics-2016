import numpy as np

from bbb import boot

SAMPLES_PER_CONV = 2


def main(adc, plt):
    adc.ready_pruss_for_burst()

    print("ADC is armed and ready.")
    raw_input("Press enter when ready...")

    # grab data
    (y, _) = adc.burst()

    if plt:
        user_input = raw_input("Would you like to plot the data?")
        if "y" == user_input:
            plot_output(adc, y, plt)

    boot.dearm()
    return y


def plot_output(adc, y, plt):
    # get plotting objects
    fig, ax = plt.subplots()
    ax.hold(True)

    # Compute parameters
    n = adc.n_channels
    M = y[0].size

    fs = adc.sample_rate

    t = adc.gen_matching_time_array(M)

    # Plot the data
    legend_list = ['' for channel in range(adc.n_channels)]

    for chan in range(adc.n_channels):
        ax.plot(t, y[chan])
        legend_list[chan] = adc.ch[chan]
        plt.xlabel('time (seconds)')
        plt.ylabel('Voltage')
        plt.title('Voltage vs Time, Fs=%dKHz' % (fs / 1000))

    ax.axis(xmin=0,
            xmax=None,
            ymin=-2.5,
            ymax=2.5)

    ax.legend(legend_list)
    plt.show()
