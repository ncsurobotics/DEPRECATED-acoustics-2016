from sys import argv

from bbb.ADC import ADS7865
import QikSampNPlt
import locPinger


def main():
    cmd = argv[1]

    if (cmd == 'competition'):
        # Load ADC Stuff
        ADC = ADS7865()
        ADC.preset(1)
        locPinger.main(ADC, dearm=False)

        # Dearm ADC outside of locPinger.py.
        ADC.unready()

    elif (cmd == 'competition-cont'):
        # Load ADC Stuff
        ADC = ADS7865()
        ADC.preset(1)

        # Locate pinger
        while True:
            # Exits on CTRL-C
            try:
                locPinger.main(ADC, dearm=False)
            except KeyboardInterrupt:
                print("Quitting program")
                break

        # Dearm ADC outside of locPinger.py.
        ADC.unready()

    elif (cmd == 'plt'):
        # Load plotting stuff
        plt = load_matplotlib()

        # Load ADC Stuff
        ADC = ADS7865()
        ADC.preset(0)
        QikSampNPlt.main(ADC, plt)


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
