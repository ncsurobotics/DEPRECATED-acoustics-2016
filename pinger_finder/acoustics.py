from sys import argv
import ConfigParser
import datetime

from bbb.ADC import ADS7865
from bbb.LTC1564 import LTC1564
import locate_pinger
import numpy as np
import quickplot2

from environment import hydrophones

from os import path
LOG_DIR = path.join(path.dirname(path.realpath(__file__)), "saved_data/")

# ##############################################
#### Settings ##################################
################################################

WORLD_ORIGIN = np.array([[0,0,0]])

ARRAY_DEFAULT_LOCATION = WORLD_ORIGIN

# Specify hydrophone locations relative to array origin
HYDROPHONE_3_DEFAULT_LOCATIONS = np.array([
    [-15e-3,0,(-15e-3)/2],
    [ 15e-3,0,(-15e-3)/2], 
    [     0,0,(15e-3)/2]
])

TARGET_FREQ = 22e3 # Frequency of the pinger in hertz

# ##############################################
#### General Purpose Functions #################
################################################

def load_matplotlib():
    """Loads the matplotlib module
    so that we can plot stuff.
    """
    print("Loading Matplotlib library...")
    import matplotlib

    matplotlib.use('GTK')

    import matplotlib.pyplot as plt

    plt.ion()
    plt.hold(False)
    plt.close()
    print("...done.")

    return plt
    
def init_figure(plt, fignum):
    fig = plt.figure(fignum)
    return fig
    
def get_dual_axes(fig):
    ax_list = fig.get_axes()
    
    if len(ax_list) != 2:
        # Clear the subplots
        for ax in ax_list:
            fig.delaxes(ax)
        
        # Make t and f subplots
        t_ax = fig.add_subplot(2,1,1, label='time')
        f_ax = fig.add_subplot(2,1,2, label='freq')
        
    else:
        t_ax = ax_list[0]
        f_ax = ax_list[1]
        
    return (t_ax, f_ax)
    
        

def get_t_axis(fig):
    ax_list = fig.get_axes()
    
    if len(ax_list) != 1:
        # Clear the subplots
        for ax in ax_list:
            fig.delaxes(ax)
        
        # Make t and f subplots
        t_ax = fig.add_subplot(1,1,1, label='time')
        
    else:
        t_ax = ax_list[0]
        
    return t_ax 


# ##################################
#### Acoustics Class ###############
####################################

class Acoustics():

    def __init__(self):
        # load config file
        config = ConfigParser.ConfigParser()
        config_file = open("config.ini", "a")
        
        # Initialize aquisition/behavior part of acoustics system
        self.adc = ADS7865()
        self.filt = LTC1564()
        self.plt = None
        self.auto_update = None
        
        # Initialize abstract hydrophone object
        self.array = hydrophones.Array() 
        
        # Define hydrophone locations
        self.array.move(ARRAY_DEFAULT_LOCATION)
        self.array.define(HYDROPHONE_3_DEFAULT_LOCATIONS)
        
        # Various parameter used later in this class
        self.valid_signal_flg = ''
        self.fig = None
        
        # Init logging class

    def compute_pinger_direction(self):
        val = locate_pinger.main(self.adc, dearm=False)
        Vpp = np.amax(self.adc.y[0]) - np.amin(self.adc.y[0])
        print("The that last signal was %.2f Vpp" % Vpp)
        
        # (detour) log data if applicable
        self.log.process(self, self.adc)
        
        if val==None:
            return None
        else:
            return val

    def compute_pinger_direction2(self):
        # Grab a sample of pinger data
        self.adc.get_data()
        
        # (detour) log data if applicable
        self.log.process(self, self.adc)
        
        # Estimate pinger location
        delays = compute_relative_delay_times(self.adc, TARGET_FREQ)
        info_string = self.array.get_direction(times[0:3])
        
    def calibrate(self):
        cal_data = config.get(acoustics, 'cal_data')
        
        # Print cal data for diagnostic purposes
        print("acoustics.py: Currently, the following delays are "
            + "applied to the system:")
        for ch_cal in cal_data:
            print(" ch {0} is offset by {1} ".format(self.adc.ch[i], ch_cal)
                + "seconds.")
                
        # Loop in getting samples until the us
    
    def condition(self):
        """Automatically determines the correct amount of gain to
        apply to the signal, and configures the LTC1564s accordingly. Also,
        due to the nature of the trigger used on the ADC, this function
        has the side effect of maximizing gain and incrementally bringing it down 
        to the correct level over time... which may make for faster initialization than
        if it just started incrementally going up in the first place.
        """
        max = 4.5
        min = self.adc.threshold
        max_gain = self.filt.get_n_gain_states()
        
        # check if autoupdate is on
        if self.auto_update is False:
            return
        
        # grab a sample of data
        self.adc.get_data()
        
        # (detour) log data if applicable
        self.log.process(self, self.adc)
        
        # grab some metasample data
        vpp = np.amax(self.adc.y[0]) - np.amin(self.adc.y[0])
        old_gain = self.filt.Gval + 1
        raw_vpp = vpp / old_gain
        
        
        i = 0
        found_gain = False
        if vpp < min:
            # Signal is too weak. Determine a new gain value to boost
            # the signal in order to put it inside the window we'd like.
            # If the signal never falls in the window, we'll just use maximum
            # gain.
            while (i+old_gain < max_gain):
                i += 1
                if raw_vpp * (old_gain+i) >= min:
                
                    # This will be the new analog gain value
                    new_gain = old_gain+i
                    
                    # Raise flag saying signal is valid
                    self.valid_signal_flg = True
                    
                    # exit section
                    break
                    
        elif vpp > max:
            # Signal is too strong. Determine a new gain value to attenuate
            # the signal in orer to put it inside the window we'd like.
            # If the signal never fall in the window, we'll just use minimum
            # gain.
            while (old_gain-i > 1):
                i += 1
                if raw_vpp * (old_gain-i) <= max:
                
                    # This will be the new analog gain value
                    new_gain = old_gain-i
                    
                    # Raise flag saying signal is valid
                    self.valid_signal_flg = True
                    
                    # exit section
                    break
                
        else:
            # Analog system gain is incapable of achieving desired system gain
            self.valid_signal_flg = False
            
            # Space reserved for digital gain code if necessary
            # # <<>>> # #
            # "May need to write function to artificially reduce
            # threshold value for the PRU assembly code, as a sort of means
            # to maintain consistent behavior while allowing the trigger to
            # work properly.
            
            return
            
        self.filt.gain_mode(new_gain)

    def plot_recent(self, fourier=False):
        """Shows the user a plot of the most recent data that
        was collected.
        """
        if self.plt==None:
            self.plt = load_matplotlib()
            
        if not self.plt.fignum_exists(1):
            self.primary_fig = init_figure(self.plt, 1)
            
        if fourier:
            (t_ax, f_ax) = get_dual_axes(self.primary_fig)
            quickplot2.main(self.adc, [t_ax, f_ax], recent=True)
        else:
            t_ax = get_t_axis(self.primary_fig)
            quickplot2.main(self.adc, [t_ax], recent=True)
            
        self.plt.pause(0.1)
        
        
                
    def preset(self, sel):
        """configures electronics quickly based on the
        sel (int) that the uses supplies. See ADC.py's 
        very own preset function for a more detailed
        description of each preset."""
        if sel == 0:
            self.adc.preset(0)
            self.filt.gain_mode(0)
            self.auto_update = True

        elif sel == 100:
            self.adc.preset(100)
            self.filt.gain_mode(15)
            self.auto_update = False

        elif sel == 101:
            self.adc.preset(101)
            self.filt.gain_mode(0)
            self.auto_update = True
    
    def set_auto_update(self, bool):
        self.auto_update = bool
        
    def close(self):
        self.adc.unready()
        
# ##################################
#### Logging Tool ##################
####################################

def get_date_str():
    return str(datetime.datetime.now()).split('.')[0]
        
class Logging():
    self.base_path = LOG_DIR
    self.base_name = None
    
    def __init__(self):
        pass
        
    def process(self, adc):
        exit = False
        while exit==False:
            
            # If fp is none, user has not started the logging tool yet
            if self.base_name is None:
                return
                
            elif self.base_name:
                # Determine whether to 
                
    def start_logging(self):
        # Get base path name
        self.base_name = get_date_str()
        
        # Create filenames
        self.sig_fn = path.join(base_name.fp, " - sig.csv")
        self.rsig_fn = path.join(base_name.fp, " - rsig.csv")
        self.ping_fn = path.join(base_name.fp, " - ping.csv")
        
        # Create file for signals (w/ record markers), recorded signals,
        # and direction data.
        self.sig_f = open(path.join(self.base_path, self.sig_fn), 'w')
        self.rsig_f = open(path.join(self.base_path, self.rsig_fn), 'w')
        self.ping_f = open(path.join(self.base_path, self.ping_fn), 'w')
        
        # set flag
        self.log_active = True
        
        # print confirmation
        print("acoustics.py: Logging is now disabled")

        
    def stop_logging(self):
        # Release base name
        self.base_name = None
        
        # Close files
        self.sig_f.close()
        self.rsig_f.close()
        self.ping_f.close()
        
        # set flag
        self.log_active = False
        
        # print confirmation
        print("acoustics.py: Logging is now enabled")
        
        
    def tog_logging(self):
    
        if self.log_active:
            self.stop_logging()
            
        else:
            self.start_logging()
        
        
    def logit(self, acoustics):
        # Create filename for log
        filename = raw_input("Logging: Give me a name for this data:")
        txtfn = path.join(LOG_DIR, filename+".txt")
        csvfn = path.join(LOG_DIR, filename+".csv")
        
        # Create file for log to write to
        with open(txtfn, 'w') as f:
        
            # dump data in file
            #f.write(acoustics.adc.adc_status())
            f.write(str(acoustics.adc.y))
        
        print("Data saved to %s" % txtfn)
        
    def close(self):
        self.adc.unready()
    
    