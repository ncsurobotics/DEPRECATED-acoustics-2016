from sys import argv

from bbb.ADC import ADS7865
import QikSampNPlt
import locate_pinger


def main():
    cmd = argv[1]

    if (cmd == 'competition'):
        # Load ADC Stuff
        adc = ADS7865()
        adc.preset(1)
        locate_pinger.main(adc, dearm=False)

        # Dearm ADC outside of locate_pinger.py.
        adc.unready()

    elif (cmd == 'competition-cont'):
        # Load ADC Stuff
        adc = ADS7865()
        adc.preset(1)

        # Locate pinger
        while True:
            # Exits on CTRL-C
            try:
                locate_pinger.main(adc, dearm=False)
            except KeyboardInterrupt:
                print("Quitting program")
                break

        # Dearm ADC outside of locate_pinger.py.
        adc.unready()

    elif (cmd == 'plt'):
        # Load plotting stuff
        plt = load_matplotlib()

        # Load ADC Stuff
        adc = ADS7865()
        adc.preset(0)
        QikSampNPlt.main(adc, plt)


def load_matplotlib():
    print("Loading Matplotlib library...")
    import matplotlib

    matplotlib.use('GTK')

    import matplotlib.pyplot as plt

    plt.ioff()
    plt.hold(False)
    plt.close()
    print("...done.")

    return plt

if __name__ == '__main__':
    main()
