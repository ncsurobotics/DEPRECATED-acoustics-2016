from sys import argv
from ConfigParser import SafeConfigParser
import datetime
import time
import csv
import math
print "MAKE SURE SCIPY.fftpack.fft is equivalent to numpy.fft.fft"
#from scipy.fftpack import fft
from numpy.fft import fft
import glob
#from scipy.signal import argrelextrema

from bbb.ADC import ADS7865
from bbb.ADC import ADC_Tools
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
PINGER_FINDER_DIR = path.dirname(path.realpath(__file__))
BASE_DIR = path.dirname(path.dirname(path.realpath(__file__)))


# ##############################################
#### Settings ##################################
################################################
class.

WORLD_ORIGIN = np.array([[0, 0, 0]])
PINGER_CYCLE_TIME = 2  # seconds

ARRAY_DEFAULT_LOCATION = WORLD_ORIGIN

# Specify hydrophone locations relative to array origin
HYDROPHONE_3_DEFAULT_LOCATIONS = np.array([
    [-15e-3, 0, (-15e-3) / 2],
    [15e-3, 0, (-15e-3) / 2],
])

TARGET_FREQ = 22e3  # Frequency of the pinger in hertz

env = Environment()
adc_tools = ADC_Tools()

# Config parser
config = SafeConfigParser()
config.read(BASE_DIR + '/config.ini')

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
        t_ax = fig.add_subplot(2, 1, 1, label='time')
        f_ax = fig.add_subplot(2, 1, 2, label='freq')

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
        t_ax = fig.add_subplot(1, 1, 1, label='time')

    else:
        t_ax = ax_list[0]

    return t_ax


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

        # Initialize Data buffer
        self.data_buffer = (None, None, None, None)

        # Initialize pinger frequency via config file
        self.pinger_freq = config.getfloat('Acoustics', 'pinger_frequency')

        # Initialize abstract hydrophone object
        self.array = hydrophones.Array()

        # Define hydrophone locations
        self.array.move(ARRAY_DEFAULT_LOCATION)
        d = config.getfloat('Acoustics','array_spacing')
        array_conf = config.get('Acoustics', 'array_configuration')
        if array_conf == 'yaw':
            self.array.define( hydrophones.generate_yaw_array_definition(d) )
        elif array_conf == 'dual':
            self.array.define( hydrophones.generate_yaw_pitch_dual_array_definition(d,d) )
        else:
            raise IOError("Unrecognized hydrophone array configuration (%s)."
            % array_conf)

        # Various parameter used later in this class
        self.valid_signal_flg = ''
        self.fig = None

        # Init logging class
        self.logger = Logging()

    def get_data(self):
        """Performs all steps necessary to collect a good set of data for processing,
        or to determine a "good data unavailable" condition, which can also be
        processed. Generally, if a ping of the correct frequency and expected
        power occurs within a known cycle time, then this code will capture
        such a ping the instant it happens. Else, it will adjust ADC settings
        for better results the next time it's called.

        GENERAL PSUEDO CODE
        # Perform Sample Capture
            # Measure elapsed time if applicable
            # if TOF: Adjust gain; next_state = exit/fail
            # if !TOF: next_state = FFT Analysis

        # Perform FFT Analysis
            # if pinger_detected: next_state = exit/success
            # if !pinger_detected:
                # if timer_expired: next_state = exit/fail
                # if !timer_expired: next_state = sample_capture
        """
        # begins process by initializing loop counter and timer
        loop_counter = 0
        watchdog_timer = 0 # seconds 
        capture_flg = False
        
        # adjust sampling parameters (condition) if a sample captures has been
        # previously performed. Otherwise, just perform a sample capture.
        if self.adc.y != None: next_state='condition'
        else: next_state='sample_capture'   
        
        while (next_state != 'exit'):

            if next_state == 'condition':
                self.condition(passive=True)
                next_state='sample_capture'  
            
            elif next_state == 'sample_capture':
                y = self.adc.get_data()
                
                if self.adc.TOF == 1:
                    # Signal was not strong enough to pass trigger. increase
                    # gain of system and exit
                    next_state = 'exit'

                elif self.adc.TOF == 0:
                    # Signal passed trigger. Check timer if for timeout.
                    if (capture_flg == False): 
                        timer_start = time.time()
                        capture_flg = True
                    else: watchdog_timer =  time.time() - timer_start
                    
                    # Print watchdog timer for diagnostic purposes
                    print('acoustics: watchdog_timer = %.2f' % watchdog_timer)

                    # Timer logic passed. Move on to FFT analysis
                    if watchdog_timer < PINGER_CYCLE_TIME * 1.1:
                        next_state = 'fft_analysis'
                    else:
                        # Watchdog timer expired. data is void.
                        # erase data and exit loop
                        y = None
                        next_state = 'exit'

            elif next_state == 'fft_analysis':
                print("acoustics: Conducting FFT analysis")
                # Identify trigger channel
                trg_ch_idx = self.adc.TRG_CH

                # generate typical fft-based parameters
                fs = self.adc.sample_rate  # hz
                M = y[trg_ch_idx].size     # bins
                df = fs / M                # hz/bin

                # generate fft string on trigger ch
                print("acoustics: y.size = %d" % len(y))
                print("acoustics: abs( fft(y[trg_ch_idx]) ) and idx = %d" % trg_ch_idx)
                Y_abs = abs(fft(y[trg_ch_idx])) / M

                # generate peak search parameters
                noise_floor = config.getfloat('ADC', 'noise_floor')  # units???
                #peak_tol = 500  # Hertz - 1/2 minimum frequency band to discern again
                peak_tol = 22e3  # REMOVE after Nov 1st.
                pinger_frequency = config.getfloat('Acoustics', 'pinger_frequency')  # units???

                # Generate Warning if expectations are too generous
                if df > 2 * peak_tol:
                    print("Acoustics: WARNING - peak tol = %f Hz" % peak_tol
                          + "Which means you can discern a signal "
                          + "%f Hz away from target freq, " % peak_tol
                          + "though your sampling parameters allow for "
                          + "a minimum peak tol of %f Hz" % (df / 2)
                          + "You should change your sampling parameters.")

                    print("Acoustics: OVERIDING peak toleranace")
                    peak_tol = df / 2.0

                # search for peaks above noise floor
                Y_abs = np.clip(Y_abs, noise_floor, 10e3)
                peaks = adc_tools.find_local_maxima(Y_abs)

                if peaks:
                    # print list of peaks for diagnosticd purposes
                    print('acoustics: Found peaks at.. ')
                    i = 0
                    for pk in peaks:
                        print('acoustics: found peak at %.2f KHz' % (pk * df / 1000))
                        i += 1

                    # see if first maxima within rang
                    if pinger_frequency - peak_tol <= peaks[0] * df <= pinger_frequency + peak_tol:
                        print("acoustics: peak is within targeted freq range. Passing sample forward")
                        next_state = 'exit'
                    else:
                        # correct pinger was not detected. Recapturing sample.
                        # time.sleep(2)
                        next_state = 'sample_capture'
                else:
                    # No peaks detected at all
                    print("acoustics: Woah!!! no data peaks detected, check yourself.")
                    next_state = 'sample_capture'

            else:
                print('acoustics: state "%s" is unknown. ' % next_state
                      + 'quiting pinger sense loop/machine.')

            # Try to adjust for any problems before leaving this loop
            if next_state == 'exit': 
                pass
                
            # Increment loop counter
            loop_counter += 1
            # ^^ END OF LOOP
            
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

        if val == None:
            return None
        else:
            return val

    def compute_pinger_direction2(self, ang_ret=False):
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
        toa_dists = tdoa_times * env.c
        info_string = self.array.get_direction(toa_dists)

        # Report angles if applicable
        if ang_ret:
            angles = [(-math.atan2(b, a) * 180 / math.pi + 90) for (a, b) in self.array.ab]

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

    def compute_pinger_direction3(self, ang_ret=False):
        # Helpful index definitions
        idx_pair_ab = 0
        idx_pair_cd = 5
        idx_tri_ra = 0
        idx_tri_rb = 1
        idx_tri_ab = 2
        
        # Grab a sample of pinger data
        y = self.get_data()

        if y:
            # (detour) log data if applicable
            self.logger.process(self.adc, self.filt)

            # Estimate pinger location: Get a value that represents the
            # time delay of arrival for each individual hydrophone
            tdoa_times = get_heading.compute_relative_delay_times(self.adc,
                                                                  self.pinger_freq,
                                                                  self.array,
                                                                  env.c)

            # Get direction
            toa_dists = tdoa_times * env.c
            info_string = self.array.get_direction(toa_dists)

            # Report angles if applicable
            if ang_ret:
                angles = [(-math.atan2(b, a) * 180 / math.pi + 90) for (a, b) in self.array.ab]

                n = self.array.n_elements
                if n == 2:
                    return {'ab': angles[idx_pair_ab], 'cd': None}

                elif n == 3:
                    return {'ra': angles[0],
                            'rb': angles[1],
                            'ab': angles[2]
                            }
                            
                elif n == 4:
                    return {'ab': angles[idx_pair_ab], 'cd': angles[idx_pair_cd]}
                else:
                    raise IOError('%d hydrophone elements was not expected' % n)
        else:
            # Did not get an acceptable sample. Return None.
            return None

    def _refresh_array_spacing(self):
        """Following refresh of config file, the array model must be
        updated.
        """
        # set update tolerance
        tol = 0.001e-3

        # update if necessary
        d = config.getfloat('Acoustics', 'array_spacing') # Assumes Config has been refreshed
        
        if not (-tol < d-self.array.d[0] < tol):
            # User has supplied a new value of hydrophone distance
            print("acoustics.py: update array with %.2fcm spacing" % (d *100.0))
            self.array.define( hydrophones.generate_yaw_array_definition(d) )

    def update_measurement(self):
        # Use code that a) collects a new measurment and b) returns a result
        # if the signal was good (of otherwise makes adjustments for next
        # time) to get data
        result = self.compute_pinger_direction3(ang_ret=True)

        # Use logic to decide whether or not to update data buffer
        update_occured = False
        if result == None:
            # Data was not captured. Do not update buffer...
            
            # but still record data if logger is active
            self.log_ready('s')
            self.logger.process(self.adc, self.filt)
        else:
            # Data was captured. Update buffer.
            (dynamic_ss, raw_vpp) = self.compute_last_signal_strength()
            self.data_buffer = (result, time.time(),dynamic_ss,raw_vpp)
            import pdb;pdb.set_trace()
            update_occured = True
            
            # Record data that says a ping was captured
            self.log_ready('sp')
            self.logger.process(self.adc, self.filt, pinger_data=result['ab'])

        return update_occured

    def compute_last_signal_strength(self):
        # initial parameters
        full_scale_range = 5.0 #volts
        
        # Generate intermediate values
        dynamic_vpp = np.amax(adc_tools.meas_vpp(self.adc))
        LTC1563_gain = (self.filt.Gval + 1)
        
        # Compute signal strengths
        dynamic_ss = dynamic_vpp/full_scale_range
        raw_vpp = dynamic_vpp / (self.adc.digital_gain*LTC1563_gain)
        
        return (dynamic_ss, raw_vpp)
        
    
    def get_last_measurement(self):
        return self.data_buffer

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
        max_vpp = 2.5
        clip_vpp = 4.7
        min_vpp = 2 * self.adc.threshold * 1.1 # 10% overhead at min
        
        # check if autoupdate is on
        if self.auto_update is False:
            return

        # grab a sample of data if active
        if not passive:
            self.adc.get_data()

        # (detour) log data if applicable
        self.logger.process(self.adc, self.filt)
        
        # grab some sample metadata
        vpp = np.amax(adc_tools.meas_vpp(self.adc))
        print("acoustics.py: signal vpp is %.2f, min_vpp is %.2f " % (vpp, min_vpp)
            + ", max_vpp is %.2f" % max_vpp)
        old_gain_LTC = self.filt.Gval + 1   # V/V
        old_gain_ADC = self.adc.digital_gain
        old_gain_total = old_gain_LTC*old_gain_ADC
        raw_vpp = vpp / old_gain_total       # Volts
        
        
        i = 0
        change_gain_flag = False
        if  vpp < min_vpp:
            # Signal is too weak. Determine a new gain value to boost
            # the signal in order to put it inside the window we'd like.
            new_gain_total = min_vpp/raw_vpp
            change_gain_flag = True
                    
        elif vpp > max_vpp:
            # Signal is too strong. Determine a new gain value to attenuate
            # the signal in orer to put it inside the window we'd like
            if vpp >= clip_vpp:
                # Signal is clipping. Must bring it down quickly
                new_gain_total = min_vpp/raw_vpp
            else:
                # Signal is not clipping
                new_gain_total = max_vpp/raw_vpp
                
            change_gain_flag = True
                
        else:
            # Current gain is appropiate. Do nothing and move on.
            pass
            
        if change_gain_flag:
            self.change_gain(new_gain_total)
            
        return

    def change_gain(self, desired_gain):
        LTC_gain = None
        digital_gain = None
        max_filt_gain = self.filt.get_n_gain_states()
        
        if desired_gain > max_filt_gain:
            # Desired gain is above the capability of the analog electronics.
            # max out the analog gain.
            LTC_gain = max_filt_gain
            
            # Determine how much additional digital gain is needed
            digital_gain = desired_gain / LTC_gain
            
        elif desired_gain < 1:
            # Desired gain is beneath the capability of the analog electronics.
            # set the analog gain to unity
            LTC_gain = 1
            
            # Determine how much additional compensation is needed
            digital_gain = desired_gain / LTC_gain
            
            
        else:
            # Desired gain is within the capability of the analog electronics.
            # Set analog gain accordingly
            LTC_gain = int(round(desired_gain)) 
            
            # Set digital gain to unity
            digital_gain = 1
            
        # END LOGIC: LTC and digital gain have been determined
        
        # update analog gain
        self.filt.gain_mode(LTC_gain-1)
        
        # update digital gain. Clip if exceeds maximum
        max_digital_gain = config.getfloat('ADC', 'max_digital_gain')
        if digital_gain > max_digital_gain:
            print("Acoustics: Clipping gain at %f" % max_digital_gain)
            digital_gain = max_digital_gain
            
        self.adc.update_digital_gain(digital_gain)
    
    def plot_recent(self, fourier=False):
        """Shows the user a plot of the most recent data that
        was collected.
        """
        if self.plt == None:
            self.plt = load_matplotlib()

        if not self.plt.fignum_exists(1):
            self.primary_fig = init_figure(self.plt, 1)

        if fourier:
            (t_ax, f_ax) = get_dual_axes(self.primary_fig)
            quickplot2.main(self.adc, [t_ax, f_ax], recent=True)
        else:
            t_ax = get_t_axis(self.primary_fig)
            quickplot2.main(self.adc, [t_ax], recent=True)
            
        t_ax.set_title('Fs = %.2f kHz, ' % (self.adc.sample_rate/1000)
            + 'LTC_Gain = %d, ' % (self.filt.Gval+1)
            + 'ADC_Gain = %.1f' % self.adc.digital_gain)
            
        self.plt.pause(0.1)

    def preset(self, sel):
        """configures electronics quickly based on the
        sel (int) that the uses supplies. See ADC.py's
        very own preset function for a more detailed
        description of each preset."""
        print("acoustics: Loading preset %d" % sel)

        # Configure the ADC
        self.adc.preset(sel)

        # Configure other parameters
        if sel == 0:
            self.filt.gain_mode(0)
            self.filt.filter_mode(2)
            self.auto_update = True

        if sel == 1:
            self.filt.gain_mode(0)
            self.auto_update = True

        elif sel == 100:
            self.filt.gain_mode(15)
            self.auto_update = False

        elif sel == 101:
            self.filt.gain_mode(0)
            self.filt.filter_mode(3)
            self.auto_update = True

    def set_auto_update(self, bool):
        self.auto_update = bool

    def log_ready(self, cmds):
        self.logger.cmd_buffer += cmds

    def close(self):
        self.adc.unready()

    def pass_config_module(self):
        """Returns object representing the config file, as instanced
        by SafeConfigParser for use in external programs.
        """
        return config
    def _refresh_pinger_freq(self):
        self.pinger_freq = config.getfloat('Acoustics','pinger_frequency')

    def refresh_config(self):
        config.read(BASE_DIR + '/config.ini')
        self._refresh_array_spacing()
        self._refresh_pinger_freq()

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
        self.active = False
        self.log_sig = False
        self.log_rec = False
        self.log_ping = False

        # cmd buffer
        self.cmd_buffer = ''

    def _parse_cmd_buffer(self):
        for i in range(len(self.cmd_buffer)):
            cmd = self.cmd_buffer[i]

            if cmd == 's':
                self.log_sig = True

            elif cmd == 'r':
                self.log_rec = True

            elif cmd == 'p':
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
            header = adc.ch[0:n] + ["timestamp", 'AGain', 'DGain', 'sample rate', 'ping_loc']
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
                row.append(adc.digital_gain)
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
            header = ["timestamp", 'AGain', 'DGain', 'sample rate', 'ping_loc']
            writer.writerow(header)

        row = []
        row.append(timestamp)
        row.append(filt.Gval)
        row.append(adc.digital_gain)
        row.append(adc.sample_rate)
        row.append(pinger_data)

        # Write data to csv file
        writer.writerow(row)

    def process(self, adc, filt, pinger_data=None):
        exit = False
        while exit == False:

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
            # ENDIF
        # ENDWHILE
        
        # Wipe the cmd buffer
        self.cmd_buffer = ''
        return

    def start_logging(self, data_filename):
        # Get base path name
        self.base_name = data_filename
        
        # Check if test is anywhere else in directory
        MAX_DUPS = 100
        n = 0; exit = False
        claimed_filename = None
        while (n < MAX_DUPS) and (exit == False):
            suggested_filename = self.base_name + str(n)
            if glob.glob(self.base_path + suggested_filename + '*.csv'):
                # Duplicate found. incr n
                n += 1
            else:
                # Found a good name
                exit = True
                claimed_filename = suggested_filename

        # Signals user that his operation was unsuccessful
        if claimed_filename == None:
            return None
            
        # Or keep on going with the aqcuired filename
        else:
            self.base_name = claimed_filename
            
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
        self.active = True

        # print confirmation
        print("acoustics.py: Logging is now enabled. Opening '%s' csv files" % self.base_name)

    def stop_logging(self):
        # Release base name
        saved_name = self.base_name
        self.base_name = None

        # Close files
        self.sig_f.close()
        self.rsig_f.close()
        self.ping_f.close()

        # set flag
        self.active = False

        # print confirmation
        print("acoustics.py: Logging disabled. Closing '%s' csv files" % saved_name)

    def tog_logging(self):

        if self.log_active:
            self.stop_logging()

        else:
            self.start_logging()

    def logit(self, acoustics):
        # Create filename for log
        filename = raw_input("Logging: Give me a name for this data:")
        txtfn = path.join(LOG_DIR, filename + ".txt")
        csvfn = path.join(LOG_DIR, filename + ".csv")

        # Create file for log to write to
        with open(txtfn, 'w') as f:

            # dump data in file
            # f.write(acoustics.adc.adc_status())
            f.write(str(acoustics.adc.y))

        print("Data saved to %s" % txtfn)

    def close(self):
        self.adc.unready()
