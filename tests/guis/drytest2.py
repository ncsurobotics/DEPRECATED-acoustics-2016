import sys
sys.path.append("../../pinger_finder/")
import threading
import time

#from bbb.ADC import ADS7865
#from bbb.LTC1564 import LTC1564

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

    else:
        raise ValueError("Unknown confige %s" % config)

    return blips

def demo(gui):
    """demo to show off how the gui works"""

    hydrophones = gui.get_blips().keys()
    while 1:
        for hydrophone in hydrophones:
            gui.pulse_blip(hydrophone, 0.5)
            time.sleep(1)

def main():
    # 
    gui = gui_curses.Curses_GUI()

    # draw the hydrophone array
    hydrophones = create_hydrophone_array('demo', gui)

    # create a processing thread
    #import pdb; pdb.set_trace()
    #import pdb; pdb.set_trace()
    process_thread = threading.Thread(target=demo, args=(gui,) )
    process_thread.start()

    # run the gui
    gui.mainloop()

main()