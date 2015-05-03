import logging

import getHeading

logging.basicConfig(level=logging.info, format='%(asctime)s - %(levelname)s - %(message)s')


TARGET_FREQ = 22e3  # hz


def main(adc, plt=None, dearm=True):
    # Assume adc is already loaded

    # Establish various parameters
    fs = adc.sampleRate

    # capture a set of samples
    y = adc.get_data()

    # process simultaneous channels
    angle = getHeading.calculate_heading(TARGET_FREQ, fs, y[0], y[1])

    # print computation to the user
    logging.info("pinger is %d degrees right" % angle)

    # dearm if user doesn't assert otherwise
    if dearm:
        adc.unready()
