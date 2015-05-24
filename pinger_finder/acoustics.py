from sys import argv

from bbb.ADC import ADS7865
from bbb.LTC1564 import LTC1564
import locate_pinger
import numpy as np
import quickplot

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


# ##################################
#### Acoustics Class ###############
####################################

class Acoustics():

    def __init__(self):
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

    def compute_pinger_direction(self):
        val = locate_pinger.main(self.adc, dearm=False)
        Vpp = np.amax(self.adc.y[0]) - np.amin(self.adc.y[0])
        print("The that last signal was %.2f Vpp" % Vpp)
        
        if val==None:
            return None
        else:
            return val

    def compute_pinger_direction2(self):
        # Grab a sample of pinger data
        self.adc.get_data()
        
        # Estimate pinger location
        delays = compute_relative_delay_times(self.adc, TARGET_FREQ)
        info_string = self.array.get_direction(times[0:3])
                                
    def condition(self):
        """Automatically determines the correct amount of gain to
        apply to the signal, and configures the LTC1564s accordingly. Also,
        due to the nature of the trigger used on the ADC, this function
        has the side effect of maximizing gain and incrementally bringing it down 
        to the correct level over time... which may make for faster initialization than
        if it just started incrementally going up in the first place.
        """
        max = 4.5
        min = 4
        max_gain = self.filt.get_n_gain_states()
        
        # check if autoupdate is on
        if self.auto_update is False:
            return
        
        # grab a sample of data
        self.adc.get_data()
        
        # grab some metasample data
        vpp = np.amax(self.adc.y[0]) - np.amin(self.adc.y[0])
        old_gain = self.filt.Gval+1
        raw_vpp = vpp/old_gain
        
        
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
                    new_gain = old_gain+i
                    break
                    
        elif vpp > max:
            # Signal is too strong. Determine a new gain value to attenuate
            # the signal in orer to put it inside the window we'd like.
            # If the signal never fall in the window, we'll just use minimum
            # gain.
            while (old_gain-i > 1):
                i += 1
                if raw_vpp * (old_gain-i) <= max:
                    new_gain = old_gain-i
                    break
                
        else:
            return
            
        self.filt.gain_mode(new_gain)

    def plot_recent(self):
        """Shows the user a plot of the most recent data that
        was collected.
        """
        if self.plt==None:
            self.plt = load_matplotlib()
        
        quickplot.main(self.adc, self.plt, recent=True)
                
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
        
class Logging():
    def __init__(self):
        pass
        
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
    
    