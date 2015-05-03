import logging

import getHeading
from bbb import boot

logging.basicConfig(level=logging.info, format='%(asctime)s - %(levelname)s - %(message)s')

TARGET_FREQ = 22e3  # hz


def main(ADC, plt=None):
    # Assume adc is already loaded

    # Establish various parameters
    fs = ADC.sampleRate

    # Arm the ADC
    ADC.ready_pruss_for_burst()

    # Loop sample collection and processing
    while(1):

        # Exit gracefully on CTRL-D
        try:

            # capture a set of samples
            y, _ = ADC.burst()

            # process simultaneous channels
            angle = getHeading.calculate_heading(TARGET_FREQ, fs, y[0], y[1])

            # print computation to the user
            logging.info("pinger is %d degrees right" % angle)

        except KeyboardInterrupt:
            print("Quitting program")
            break

    boot.dearm()
