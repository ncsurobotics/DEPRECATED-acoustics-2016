from sys import argv
import ConfigParser
import datetime
import time
import csv
import math
from scipy.fftpack import fft
from scipy.signal import argrelextrema

from bbb.ADC import ADS7865
from bbb.LTC1564 import LTC1564
import locate_pinger
import numpy as np
import quickplot2
import get_heading

from environment import hydrophones
from environment.tools3d import Environment
from environment import source

from os import path
LOG_DIR = path.join(path.dirname(path.realpath(__file__)), "saved_data/")


# ##############################################
#### Settings ##################################
################################################

WORLD_ORIGIN = np.array([[0,0,0]])
PINGER_CYCLE_TIME = 5 # seconds

ARRAY_DEFAULT_LOCATION = WORLD_ORIGIN

# Specify hydrophone locations relative to array origin
HYDROPHONE_3_DEFAULT_LOCATIONS = np.array([
    [-15e-3,0,(-15e-3)/2],
    [ 15e-3,0,(-15e-3)/2], 
    #[     0,0,(15e-3)/2]
])

TARGET_FREQ = 22e3 # Frequency of the pinger in hertz

env = Environment()

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
        self.config = ConfigParser.SafeConfigParser()
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
        self.logger = Logging()
        
    def _digital_boost(self):
        """Applied digital gain to signal in a manner that reflects more sensitive
        trigger action and plotted data points.
        """
        pass
        
    def get_data(self):
        # begins process by initiating a sample capture and initializing
        # loop counter
        next_state = 'sample_capture'
        loop_counter = 0
        watchdog_timer = 0 # seconds
        
        # BEGIN LOOP
        """
        GENERAL PSUEDO CODE
        # Perform Sample Capture
            # Measure elapsed time if applicable
            # if TOF: Adjust gain; next_state = exit
            # if !TOF: next_state = FFT Analysis
            
        # Perform FFT Analysis
            # if pinger_detected: next_state = compute_heading
            # if !pinger_detected:
                # if timer_expired: next_state = exit
                # if !timer_expired: next_state = sample_capture
        """
        
        while (next_state != 'exit'):

            if next_state == 'sample_capture':
                y = self.adc.get_data()
                
                if adc.TOF == 1:
                    # Signal was not strong enough to pass trigger. increase
                    # gain of system and exit
                    next_state = 'exit'
                    
                elif adc.TOF == 0:
                    # Signal passed trigger. Check timer if for timeout.
                    if (loop_counter == 0): timer_start = time.time()
                    else: watchdog_timer += timer_start - time.time()
                    
                    # Print watchdog timer for diagnostic purposes
                    print('acoustics: watchdog_timer = %.2s' % watchdog_timer)
                    
                    # Timer passed. Move on to FFT analysis
                    if watchdog_timer < PINGER_CYCLE_TIME*0.1:
                        next_state = 'fft_analysis'
                    else:
                        # Watchdog timer expired. data is void.
                        # erase data and exit loop 
                        y = None
                        next_state = 'exit'
                    
            elif next_state == 'fft_analysis':
                # Identify trigger channel
                trg_ch_idx = self.adc.TFLG_CH
                
                # generate fft string on trigger ch
                Y_abs = abs( fft(y[trg_ch_idx]) )
                
                # generate typical fft-based parameters
                fs  = self.adc.sample_rate  # hz
                M   = Y_abs.size            # bins
                df  = fs / M                # hz/bin
                
                # generate peak search parameters
                noise_floor = self.config.getfloat('ADC', 'noise_floor') # units???
                peak_tol = 3*df
                pinger_frequency = self.config.getfloat('Acoustics', 'pinger_frequency') # units???
                
                # search for peaks above noise floor
                Y_abs = np.clip(Y_abs, noise_floor, 10e3)
                peaks = argrelextrema(Y_abs, np.greater)
                
                # print list of peaks for diagnosticd purposes
                print('acoustics: Found peaks at.. ')
                i = 0
                for pk in peaks:
                    print('acoustics: %.2f KHz' % pk*df/1000 )
                    if i==0: print('\b << fundamental')
                    i += 1
 
                # see if first maxima within rang
                if pinger_frequency-peak_tol <= peaks[0]*df <= pinger_frequency+peak_tol:
                    next_state = 'exit'
                else: 
                    # correct pinger was not detected. Recapturing sample.
                    next_state = 'sample_capture'
 
            else:
                print('acoustics: state "%s" is unknown. ' % next_state
                    + 'quiting pinger sense loop/machine.')
                    
            # Try to adjust for any problems before leaving this loop
            if next_state == 'exit': condition(passive=True)
                
            # Increment loop counter
            loop_counter += 1
            # END OF LOOP
            
        return y # is None if signal does not pass criteria
        
    def compute_pinger_direction(self):
        """
        output value represents direction to pinger in degrees.
        """
        val = locate_pinger.main(self.adc, dearm=False)
        Vpp = np.amax(self.adc.y[0]) - np.amin(self.adc.y[0])
        print("The that last signal was %.2f Vpp" % Vpp)
        
        # (detour) log data if applicable
        self.logger.process(self.adc, self.filt, pinger_data=val)
        
        if val==None:
            return None
        else:
            return val

    def compute_pinger_direction2(self,ang_ret=False):
        # Grab a sample of pinger data
        self.adc.get_data()
        
        # (detour) log data if applicable
        self.logger.process(self.adc, self.filt)
        
        # Estimate pinger location: Get a value that represents the
        # time delay of arrival for each individual hydrophone
        tdoa_times = get_heading.compute_relative_delay_times(self.adc, 
            TARGET_FREQ, 
            self.array,
            env.c)
        
        # Get direction
        toa_dists = tdoa_times*env.c
        info_string = self.array.get_direction(toa_dists)
        
        # Report angles if applicable
        if ang_ret:
            angles = [(-math.atan2(b,a)*180/math.pi+90) for (a,b) in self.array.ab]
            
            n = self.array.n_elements
            if n == 2:
                return {'ab': angles[0]}
                
            elif n == 3:
                return {'ra': angles[0],
                    'rb': angles[1],
                    'ab': angles[2]
                }
            else:
                raise IOError('%d hydrophone elements was not expected' % n)
            
    def calibrate(self):
        cal_data = config.get(acoustics, 'cal_data')
        
        # Print cal data for diagnostic purposes
        print("acoustics.py: Currently, the following delays are "
            + "applied to the system:")
        for ch_cal in cal_data:
            print(" ch {0} is offset by {1} ".format(self.adc.ch[i], ch_cal)
                + "seconds.")
                
        # Loop in getting samples until the us
    
    def condition(self, passive=False):
        """Automatically determines the correct amount of gain to
        apply to the signal, and configures the LTC1564s accordingly. Also,
        due to the nature of the trigger used on the ADC, this function
        has the side effect of maximizing gain and incrementally bringing it down 
        to the correct level over time... which may make for faster initialization than
        if it just started incrementally going up in the first place.
        """
        # Class level flag reset
        self.valid_signal_flg = False
        
        # Basic variables
        ovr_head = 0.1
        max_vpp = 4.5
        min_vpp = 2 * self.adc.threshold * (1 + ovr_head)
        max_gain = self.filt.get_n_gain_states()
        
        # check if autoupdate is on
        if self.auto_update is False:
            return
        
        # grab a sample of data if active
        if !passive():
            self.adc.get_data()
        
        # (detour) log data if applicable
        self.logger.process(self.adc, self.filt)
        
        # grab some metasample data
        vpp = np.amax(self.adc.y[0]) - np.amin(self.adc.y[0])
        print("acoustics.py: pp is %.2f, min_vpp is %.2f" % (vpp, min_vpp))
        old_gain = self.filt.Gval + 1   # V/V
        raw_vpp = vpp / old_gain        # Volts
        
        
        i = 0
        found_gain = False
        if vpp < min_vpp:
            # Signal is too weak. Determine a new gain value to boost
            # the signal in order to put it inside the window we'd like.
            # If the signal never falls in the window, we'll just use maximum
            # gain.
            while (i+old_gain < max_gain):
                i += 1
                if raw_vpp * (old_gain+i) >= min_vpp:
                    
                    # Raise flag saying signal is valid
                    self.valid_signal_flg = True
                    
                    # exit section
                    break
                    
            # This will be the new analog gain value. If the break
            # Gain will be set to the maximum V/V value, but the
            # valid_signal_flg will remain set to false.
            new_gain = old_gain + i
                    
        elif vpp > max_vpp:
            # Signal is too strong. Determine a new gain value to attenuate
            # the signal in orer to put it inside the window we'd like.
            # If the signal never fall in the window, we'll just use minimum
            # gain.
            while (old_gain-i > 1):
                i += 1
                if raw_vpp * (old_gain-i) <= max_vpp:
                    
                    # Raise flag saying signal is valid
                    self.valid_signal_flg = True
                    
                    # exit section
                    break
                    
            # This will be the new analog gain value. If the break
            # statement is not passed, then gain will be set to
            # the minimum V/V value, but the valid_signal_flg will
            # remain set to false.
            new_gain = old_gain-i
                
        else:
            # Analog system gain is incapable of achieving desired system gain
            self.valid_signal_flg = True
            new_gain = old_gain
            
            # Space reserved for digital gain code if necessary
            # # <<>>> # #
            # "May need to write function to artificially reduce
            # threshold value for the PRU assembly code, as a sort of means
            # to maintain consistent behavior while allowing the trigger to
            # work properly.
            
            return
            
        self.filt.gain_mode(new_gain-1)

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
        
        # Configure the ADC
        self.adc.preset(sel)
        
        # Configure other parameters
        if sel == 0:
            self.filt.gain_mode(0)
            self.auto_update = True
            
        if sel == 1:
            self.filt.gain_mode(0)
            self.auto_update = True

        elif sel == 100:
            self.filt.gain_mode(15)
            self.auto_update = False

        elif sel == 101:
            self.filt.gain_mode(0)
            self.auto_update = True
    
    def set_auto_update(self, bool):
        self.auto_update = bool
        
    def log_ready(self, cmds):
        self.logger.cmd_buffer += cmds
        
    def close(self):
        self.adc.unready()
        
# ##################################
#### Logging Tool ##################
####################################

def get_date_str():
    return str(datetime.datetime.now()).split('.')[0]
        
class Logging():
    
    def __init__(self):
        # Init path names
        self.base_path = LOG_DIR
        self.base_name = None
        
        # logging logic
        self.log_active = False
        self.log_sig = False
        self.log_rec = False
        self.log_ping = False
        
        # cmd buffer
        self.cmd_buffer = ''
        
    def _parse_cmd_buffer(self):
        for i in range(len(self.cmd_buffer)):
            cmd = self.cmd_buffer[i]
            
            if cmd=='s':
                self.log_sig = True
                
            elif cmd=='r':
                self.log_rec = True
                
            elif cmd=='p':
                self.log_ping = True
                
        # Clear command buffer
        self.cmd_buffer = ''
        
    def _log_signal(self, file, adc, filt, pinger_data=None):
        # init csv writer
        writer = csv.writer(file)
        
        # init variables
        n = adc.n_channels
        timestamp = get_date_str()
        
        # File is empty. Write headers at top.
        if file.tell() == 0:
            header = adc.ch[0:n] + ["timestamp", 'Gain', 'sample rate', 'ping_loc']
            writer.writerow(header)
        
        for sample in range(len(adc.y[0])):
            
            # Create a row of sample data
            row = []
            for ch in range(n):
                row.append(adc.y[ch][sample])
        
            # Grab time stamp
            if sample == 0:
                row.append(timestamp)
                row.append(filt.Gval)
                row.append(adc.sample_rate)
                row.append(pinger_data)
            
            # Write data to csv file    
            writer.writerow(row)
            
    def _log_ping(self, file, adc, filt, pinger_data):
        # init csv writer
        writer = csv.writer(file)
        
        # init variables
        timestamp = get_date_str()
        
        # File is empty. Write headers at top.
        if file.tell() == 0:
            header = ["timestamp", 'Gain', 'sample rate', 'ping_loc']
            writer.writerow(header)
        
        row = []
        row.append(timestamp)
        row.append(filt.Gval)
        row.append(adc.sample_rate)
        row.append(pinger_data)
        
        # Write data to csv file    
        writer.writerow(row)
        
    def process(self, adc, filt, pinger_data=None):
        exit = False
        while exit==False:
            
            # If fp is none, user has not started the logging tool yet
            if self.base_name is None:
                exit = True
                
            elif self.base_name:
                # Determine whether to capture signal data or pinger data
                self._parse_cmd_buffer()
                
                # Log the signal if desirable
                if self.log_sig:
                    self._log_signal(self.sig_f, adc, filt, pinger_data)
                    self.log_sig = False
                    
                # Log the recorded signal if desirable
                elif self.log_rec:
                    self._log_signal(self.rsig_f, adc, filt, pinger_data)
                    self.log_rec = False
                    
                # Log the ping data if desirable
                elif self.log_ping:
                    self._log_ping(self.ping_f, adc, filt, pinger_data)
                    self.log_ping = False
                else:
                    exit = True
        return
        
                
    def start_logging(self):
        # Get base path name
        self.base_name = get_date_str()
        #self.base_name = "test"
        
        # Create filenames
        self.sig_fn = self.base_name + " - sig.csv"
        self.rsig_fn = self.base_name + " - rsig.csv"
        self.ping_fn = self.base_name + " - ping.csv"
        
        # Create file for signals (w/ record markers), recorded signals,
        # and direction data.
        self.sig_f = open(path.join(self.base_path, self.sig_fn), 'w')
        self.rsig_f = open(path.join(self.base_path, self.rsig_fn), 'w')
        self.ping_f = open(path.join(self.base_path, self.ping_fn), 'w')
        
        # set flag
        self.log_active = True
        
        # print confirmation
        print("acoustics.py: Logging is now enabled")

        
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
        print("acoustics.py: Logging is now disables")
        
        
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
    
    
