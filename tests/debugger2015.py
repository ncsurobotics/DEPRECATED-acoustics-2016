from os import path
import curses

# Get variables for navigating the file system.
root_directory = path.dirname(path.dirname(path.realpath(__file__)))
hc_directory = path.join(root_directory, "host_communication")
pf_directory = path.join(root_directory, "pinger_finder")

# Add important directories to path
import sys
sys.path.insert(0, hc_directory)
sys.path.insert(0, pf_directory)

#####
#####
####

import numpy as np
import acoustics as bbb

def signal_strength(stdscr):
    # setup
    stdscr.nodelay(1)
    
    acoustics = bbb.Acoustics()
    acoustics.filt.gain_mode(0)
    acoustics.adc.update_deadband_ms(0)
    acoustics.adc.set_sample_len(1e3)
    acoustics.adc.update_sample_rate(300e3)
    acoustics.adc.update_threshold(0)
    acoustics.adc.ez_config(4)

    n = 0
    s = -1
    while s == -1:
        # Clear screen
        stdscr.clear()
        
        # Get some data
        acoustics.adc.get_data()
    
        # 
        print(n)
        for chan in range(acoustics.adc.n_channels):
            avg = np.mean(acoustics.adc.y[chan])
            msg = "%s = %8.2f" % (acoustics.adc.ch[chan], avg)
            stdscr.addstr(chan, 0, msg)
        stdscr.addstr(chan+2, 0, 'cycle = ' + str(n))
        n += 1
        
        stdscr.refresh()
        s = stdscr.getch()
        
def check_dac():
    acoustics = bbb.Acoustics()
    acoustics.adc.read_dac()
    
# Check for correct call
if len(sys.argv) > 2:
    raise NameError('Can\'t have more than one argument!')
elif len(sys.argv) < 2:
    raise NameError('Must have at least one argument!')
    
call = sys.argv[1]
if call == 'signal_strength':
    signal_strength()
elif call == 'signal_strength_gui':
    curses.wrapper(signal_strength)
elif call == 'check_dac':
    check_dac()
else:
    raise NameError(call + ' is not a recognized command!')

