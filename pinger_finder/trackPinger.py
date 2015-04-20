import logging
logging.basicConfig(level=logging.info, format='%(asctime)s - %(levelname)s - %(message)s')

import getHeading
import boot

TARGET_FREQ = 22e3  # hz


def main(ADC, plt=None):
    """ Assume adc is already loaded """

    # Establish various parameters
    fs = ADC.sampleRate

    # Arm the ADC
    ADC.Ready_PRUSS_For_Burst()

    # Loop sample collection and processing
    while(1):

        # Exit gracefully on CTRL-D
        try:

            # capture a set of samples
            y, t = ADC.Burst()

            # process simultaneous channels
            angle = getHeading.calculate_heading(TARGET_FREQ, fs, y[0], y[1])

            # print computation to the user
            logging.info("pinger is %d degrees right" % angle)

        except KeyboardInterrupt:
            print("Quitting program")
            break

    boot.dearm()
