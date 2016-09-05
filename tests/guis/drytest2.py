import sys
sys.path.append("../../pinger_finder/")
import threading
import time

import gui_curses

def create_hydrophone_array(config, gui):
    """Draws a hydrophone array in the gui.
    ARGS:
      * config: string representing what kind of
      config is desired.
      * gui: curses gui handler.
      
    RETURN:
      a dictionary consisting of hydrophone GUI elements,
      which can be used as reference for pulsing them"""

    # create a subframe to hold everything
    subframe_name = 'hydrophone_array'
    gui.add_subframe(subframe_name, [0,0])

    # draw a config on
    if config == 'demo':
        hlocs = ( (5, 5),
                  (9,5),
                  (7,7),
                  (7,9) )

        for (i,hloc) in enumerate(hlocs):
            gui.add_blip(subframe_name, hloc)

        blips = gui.get_blips()

    elif config == 'standard':
        gui.add_blip(subframe_name, (5,5), name='CHA1')
        gui.add_blip(subframe_name, (9,5), name='CHB1')
        gui.add_blip(subframe_name, (7,9), name='CHA0')
        gui.add_blip(subframe_name, (7,7), name='CHB0')
        blips = gui.get_blips()

    else:
        raise ValueError("Unknown config %s" % config)

    return blips

def demo(gui):
    """demo to show off how the gui works"""

    hydrophones = gui.get_blips().keys()
    while 1:
        for hydrophone in hydrophones:
            gui.pulse_blip(hydrophone, 0.5)
            time.sleep(1)

def test(adc, gui):
    """code for testing hydrophones. uses curses GUI module"""

    # get blip array
    hydrophones = gui.get_blips()

    while 1:
        # perform a sample capture
        adc.get_data()

        # print trigger ch
        timeout_flag = adc.TOF
        #import pdb; pdb.set_trace()
        if timeout_flag:
            pass
        else:
            # capture pinged channel name
            ping = adc.TRG_CH
            print "adc trig = {}".format(ping)
            pinged_ch = adc.ch[ping]

            for hydrophone_name in hydrophones:
                if pinged_ch[0:4] in hydrophone_name:
                    gui.pulse_blip(hydrophone_name, 5)
                    print "pulsed {}".format(pinged_ch)

        



def startup_ADC():
    from bbb.ADC import ADS7865
    from bbb.LTC1564 import LTC1564

    adc = ADS7865()
    filt = LTC1564()

    filt.gain_mode(15)
    filt.filter_mode(3)
    adc.ez_config(5)

    adc.update_deadband_ms(0*0.5e3)    # dead time
    adc.set_sample_len(1e3)            # sample length
    adc.update_sample_rate(300e3)      # sample rate
    adc.update_threshold(0.1)          # trigger threshold

    return adc


def main2():
    # get GUI object
    gui = gui_curses.Curses_GUI()

    # draw the hydrophone array
    hydrophones = create_hydrophone_array('demo', gui)

    # create a processing thread
    process_thread = threading.Thread(target=demo, args=(gui,) )
    process_thread.start()

    # run the gui
    gui.mainloop()

def main1():
    # get GUI object
    gui = gui_curses.Curses_GUI()

    # draw the hydrophone array
    hydrophones = create_hydrophone_array('standard', gui)

    # create a processing thread
    adc = startup_ADC()
    #test(adc,gui)
    process_thread = threading.Thread(target=test, args=(adc,gui) )
    process_thread.start()

    # run the gui
    gui.mainloop()

main1()
