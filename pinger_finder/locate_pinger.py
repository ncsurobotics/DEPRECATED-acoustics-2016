import logging

import get_heading

logging.basicConfig(level=logging.info, format='%(asctime)s - %(levelname)s - %(message)s')


TARGET_FREQ = 22e3  # hz


def main(adc, plt=None, dearm=True):
    # Assume adc is already loaded

    # Establish parameters from ADC
    fs = adc.sample_rate

    # capture a set of samples
    y = adc.get_data()
    
    if y ==None:
        print("locate pinger: Unable to compute pinger location")
        return None

    # process simultaneous channels
    angle = get_heading.calculate_heading(TARGET_FREQ, fs, y[0], y[1])

    # print computation to the user
    logging.info("pinger is %d degrees right" % angle)

    # dearm if user doesn't assert otherwise
    if dearm:
        adc.unready()

    return angle