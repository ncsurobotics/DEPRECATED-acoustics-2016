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
import led


# Live viewer for the 4 ADC inputs
def DC_signal_strength(stdscr):
    # setup
    display_controller = Display_controller(stdscr)
    
    # Initialize Acoustics Environment
    acoustics = bbb.Acoustics()

    acoustics.filt.gain_mode(0)
    acoustics.filt.filter_mode(2)
    
    # Setup custom ADC/Filt parameters
    acoustics.filt.gain_mode(0)
    acoustics.filt.filter_mode(14)
    
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
            msg = "%s = %8.4f" % (acoustics.adc.ch[chan], avg)
            stdscr.addstr(chan, 0, msg)
        stdscr.addstr(chan+2, 0, 'cycle = ' + str(n))
        n += 1
        
        stdscr.refresh()
        s = stdscr.getch()
        
# Live viewer for the 4 ADC inputs
def AC_signal_strength(stdscr=None):
    # Initialize curses environment
    display_controller = Display_controller(stdscr)
    
    # Initialize data data_frame
    data_frame = Data_frame()
    
    
    # Initialize Acoustics Environment
    acoustics = bbb.Acoustics()
    
    # Setup custom ADC/Filt parameters
    acoustics.filt.gain_mode(15)
    acoustics.filt.filter_mode(3)
    acoustics.adc.update_deadband_ms(0)
    acoustics.adc.set_sample_len(1e3)
    acoustics.adc.update_sample_rate(300e3)
    acoustics.adc.update_threshold(.5)
    acoustics.adc.ez_config(4)
    
    # Setup display parameters
    data_frame.set_labels(acoustics.adc.ch)
    

    n = 0
    s = -1
    while s == -1:
        
        # Get some data
        acoustics.adc.get_data()
        data_frame.update(acoustics.adc.y)
        
        # Information Controller
        vis_output = data_frame.generate_ac_sig_data(acoustics)

        # Screen Controller
        s = display_controller.update(vis_output)
        
def display_parameters(a):
    return a
        
# Check the DAC setting on the ADC. Alot of times, you
# can use this to see if the ADC is responding at all
# or whether or not all the pins are connected. If every
# thing is good, the DAC should output
# 0b001111111111, or 2.49612 Volts.
def check_dac():
    acoustics = bbb.Acoustics()
    USR0 = led.USR0_LED()
    while 1:
        acoustics.adc.read_dac()
        if acoustics.adc.dac_voltage > 2:
            USR0.brightness(1)
            USR0.brightness(0)
    
# A more "deliberate" version of check_dac.
def check_data_pins():
    acoustics = bbb.Acoustics()

    # You are supposed to use pdb and freeze right when
    # all the data pins go high. Then you can probe each
    # data pin on the ADC to see if the signal is actually
    # reaching the ADC, or if there's a break somewhere in
    # the trace.
    import pdb; pdb.set_trace()
    acoustics.adc.config([0xFFF])
    
    
### ##### ########
# Classes ########
### ##### ########
class Data_frame:
    def __init__(self):
        # programming related
        self.type = None
        
        # memory related
        self.buf = 5
        
        # timing related
        self.T_hold = 1 #seconds
        
        # data related
        self.y      = None
        self.y_max  = create_list_vector(self.buf)
        
        # ID related
        self.labels = None
        
    def set_labels(self,labels):
        self.labels = labels
        
    def update(self, y):
        # update the y attribute
        self.y = y
        
        # Update the y_max attribute
        self.y_max.insert(0, []) # insert a new blank entry

        ptr = self.y_max[0] # Update the new entry
        for i in range(len(y)): 
            ptr.append( np.amax(y[i]) )
            
        self.y_max.pop() # pop off the last entry
        
    def generate_ac_sig_data(self,acoustics=None):
        # 
        msg_list = []
        
        # 
        for chan in range(len(self.labels)):
            # Do calculations
            avg = np.mean(self.y[chan]) #average value
            pk_list = []                     #pk value
            for i in range(self.buf):
                ptr = self.y_max[i]
                if ptr != []:
                    pk_list.append(ptr[chan])
                    pk = max(pk_list)
            
            # Generate message
            msg = "%s-- pk: %.3f, avg: %8.3f" % (self.labels[chan], pk, avg)
            if acoustics != None:
                if acoustics.adc.TRG_CH == chan:
                    msg = msg +"*"
            msg_list.append(msg)
            
        return msg_list
        
    
    
class Display_controller:
    def __init__(self,curses_obj):
        if curses_obj == None:
            print("No Curses object being used")
        
        # Define display
        self.display = curses_obj
        
        if curses_obj == None:
            return
            
        # Setup display environment
        self.display.nodelay(1)
        
    def update(self,lines):
        s = -1
        if self.display != None:
            # Clear the display
            self.display.clear()
        
            # Write to the display
            n = 0
            for line in lines:
                self.display.addstr(n, 0, line)
                n += 1
            
            # Refresh the display
            self.display.refresh()
            s = self.display.getch()
        else:
            for line in lines:
                print(line)
            
        return s
### ##### ############
# Helper Functions ###
### ##### ############
def create_list_vector(n_entries=1):
    vector = []
    for i in range(n_entries):
        vector.append([])
    return vector
        
### ##### ########
# Main Program ###
### ##### ########

# Check for correct call
if len(sys.argv) > 2:
    raise NameError('Can\'t have more than one argument!')
elif len(sys.argv) < 2:
    raise NameError('Must have at least one argument!')
    
call = sys.argv[1]
if call == 'signal_strength':
    signal_strength()
elif call == 'signal_strength_gui':
    curses.wrapper(DC_signal_strength)
elif call == 'AC_signal_strength_gui':
    curses.wrapper(AC_signal_strength)
    #AC_signal_strength()
elif call == 'check_dac':
    check_dac()
elif call == 'check_data_pins':
    check_data_pins()
else:
    raise NameError(call + ' is not a recognized command!')

