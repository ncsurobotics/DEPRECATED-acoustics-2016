import numpy as np

SAMPLES_PER_CONV = 2


def main(adc, plt, recent=False, ask=False):

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

    if y == None:
        print("quickplot: Trigger failed. Aborting plot")
    else:
        plot_output(adc, y, plt)

    # snippet reflects that if user sets recent to false (and thus is grabbing
    # fresh data), he is unable to control the ready state of the ADC, so this
    # snippet of code does that for him.
    if recent == False:
        adc.unready()
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
    legend_list = [''] * adc.n_channels
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
    plt.pause(0.1)
