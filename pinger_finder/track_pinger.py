import logging

import get_heading
from bbb import boot

logging.basicConfig(level=logging.info, format='%(asctime)s - %(levelname)s - %(message)s')

TARGET_FREQ = 22e3  # hz


def main(adc, plt=None):
    # Assume adc is already loaded

    # Establish various parameters
    fs = adc.sample_rate

    # Arm the ADC
    adc.ready_pruss_for_burst()

    # Loop sample collection and processing
    while True:
        # Exit gracefully on CTRL-D
        try:
            # capture a set of samples
            y, _ = adc.burst()

            # process simultaneous channels
            angle = get_heading.calculate_heading(TARGET_FREQ, fs, y[0], y[1])

            # print computation to the user
            logging.info("pinger is %d degrees right" % angle)

        except KeyboardInterrupt:
            print("Quitting program")
            break

    boot.dearm()
