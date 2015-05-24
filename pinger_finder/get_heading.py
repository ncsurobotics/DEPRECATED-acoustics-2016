import math
from cmath import phase

from scipy.fftpack import fft

"""
Phase_diff = phase_a - phase_b.
  ^^^ Thus, a positive phase_diff means that signal "a" leads signal
  "b". In most familiar terms, this means that a signal struck reciever
  "a" before it struck receiver "b".
"""


def phase_diff_to_x_and_y(phase_diff, fundamental_freq):
    # Parameters
    v = 1473  # Speed of sound in water (m/s)
    d = (27.7e-3) / 2  # half_distance between hydrophone elements

    # Compute wavelength of signal
    wavelength = v / fundamental_freq  # meters

    # Compute delta D amongst hydrophones
    D1minusD2 = (phase_diff / math.pi / 2) * wavelength  # meters

    # Generate vector components
    x = D1minusD2 / 2  # meters
    if (x > d):
        # Limit given the spacing of the hydrophone elements has been
        # exceed. To prevent error in the next step, we'll clip purposely
        # clip the signal
        x = d
        print("get_heading: Warning, Angle is Clipped at max/min value.")
        
    y = math.sqrt(d**2 - x**2)

    return (x, y)


def relative_wraparound(host_angle, guest_angle):
    if (guest_angle < host_angle - math.pi):
        # add 2pi
        guest_angle += 2 * math.pi

    elif (guest_angle > host_angle + math.pi):
        # subtract 2pi
        guest_angle -= 2 * math.pi

    return guest_angle


def calculate_heading(target_freq, fs, a, b):
    """
    Takes a pair of signal vs. time data "a" and "b", and computes an angle 
    pointing towards the signal source relative to the "b" direction. 
    Args:
        target_freq: frequency of signal emitted by source
        fs: Sampling frequency used to capture signals "a" and  "b"
        a: numpy array of sinusoidal signal data for channel a
        b: numpy array of sinusoidal signal data for channel b
        
    Notes: "One important parameter is the physical distance between
    the two elements used to capture the signal data in the first place.
    Rather than pass it in as an argument, it's more reasonable to 
    hard code a constant. To change this constant, simple change the
    "d" constant used in the phase_diff_to_x_and_y function.
    """

    # sample rate (Hz)
    sample_rate = fs

    # Highest frequency captured - limited by sample rate (Hz)
    high_freq_bound = sample_rate / 2

    # Number samples (bins)
    sample_number = len(a)

    # Signal freq held in each index of arrays (Hz/bin)
    scale = sample_rate / sample_number

    # Index of arrays for complex number we want (bin)
    index = target_freq / scale

    # Update target frequency to one that matches scale of fft
    target_freq = scale * index

    # Getting our phases (radians)
    a_phase = phase(fft(a)[index])
    b_phase = phase(fft(b)[index])
    b_phase = relative_wraparound(a_phase, b_phase)
    print("a_phase = %f pi radians" % (a_phase / math.pi))
    print("b_phase = %f pi radians" % (b_phase / math.pi))

    # Compute phase difference
    phase_diff = a_phase - b_phase
    print("a leads b by %fpi radians" % (phase_diff / math.pi))

    # Get proportional x and y components (meters)
    (y, x) = phase_diff_to_x_and_y(phase_diff, target_freq)
    print("x=%f meters and y=%f meters." % (x, y))

    # Calculate and return heading using tan-1(y/x)
    return math.atan2(y, x) * 180 / math.pi
    
def get_phase_diff(target_freq, fs, a, b):
    # sample rate (Hz)
    sample_rate = fs

    # Highest frequency captured - limited by sample rate (Hz)
    high_freq_bound = sample_rate / 2

    # Number samples (bins)
    sample_number = len(a)

    # Signal freq held in each index of arrays (Hz/bin)
    scale = sample_rate / sample_number

    # Index of arrays for complex number we want (bin)
    index = target_freq / scale

    # Update target frequency to one that matches scale of fft
    target_freq = scale * index

    # Getting our phases (radians)
    a_phase = phase(fft(a)[index])
    b_phase = phase(fft(b)[index])
    b_phase = relative_wraparound(a_phase, b_phase)
    print("a_phase = %f pi radians" % (a_phase / math.pi))
    print("b_phase = %f pi radians" % (b_phase / math.pi))

    # Compute phase difference
    phase_diff = a_phase - b_phase
    print("a leads b by %fpi radians" % (phase_diff / math.pi))
    
def phasediff_2_timediff(phase_diff, period):
    return target_period * phase_diff / (2 * np.pi)
    
def compute_time_diff(target_freq, fs, a, b):
    """
    Takes a pair of signal vs. time data "a" and "b", and computes time 
    difference relative to b signal.
    
        target_freq: frequency of signal emitted by source
        fs: Sampling frequency used to capture signals "a" and  "b"
        a: numpy array of sinusoidal signal data for channel a
        b: numpy array of sinusoidal signal data for channel b
        
    """
    # get phase
    phase_diff = get_phase_diff(target_freq, fs, a, b)
    
    # phase_diff to distance
    target_period = 1/target_freq
    ta_minus_tb = phasediff_2_timediff(phase_diff, target_period)
    
    return ta_minus_tb
    
# ############################
### System level function ####
##############################

def compute_relative_delay_times(adc, target_freq):
    """
    Computes the relative delay times for each hydrophone pair
    """
    # Initialize parameters
    n = adc.n_channels
    y = adc.y
    delay = np.array([0]*n)
    
    # get relative delays for each comb
    for el in range(1,n):
        delay[el] = compute_time_diff(
            target_freq, 
            adc.sample_rate, 
            adc.y[el], 
            adc.y[0])
        
    # print delay for debugging purposes
    print(delay)
    
    # Adjust for sampling delays
    delay = delay - np.array(adc.delay)
    delay = delay - np.amin(delay)
    
    # Return values
    return delay
    