import math
from cmath import phase
import numpy as np

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
    phase_diff = b_phase - a_phase
    print("b leads a by %fpi radians" % (phase_diff / math.pi))

    return phase_diff


def phasediff_2_timediff(phase_diff, period):
    return period * phase_diff / (2 * np.pi)


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
    target_period = 1 / target_freq
    tb_minus_ta = phasediff_2_timediff(phase_diff, target_period)

    return tb_minus_ta

# ############################
### System level function ####
##############################

"""
Computes the relative delay times for each hydrophone pair"""
def compute_relative_delay_times(adc, target_freq, array, c, pattern=None, elem2adc=None):
    
    """
    args: 
        dict_set-- a list integers wheras element at index n is supposed
        to represent the ADC channel corresponding to hydrophone n."""

    def check_if_one_to_one(dict_set):
        used = []
        for item in dict_set:
            value = item
            #import pdb; pdb.set_trace()
            if value in used:
                raise ValueError("non 1-to-1 mapping used!")
            else:
                used.append(value)

    # Initialize parameters
    n_ch = adc.n_channels
    y = adc.y
    n_times = array.n_elements



    # perform some error checking on pattern
    if pattern != None:
        for each_pair in pattern:
            try:
                if len(each_pair) != 2:
                    raise ValueError("invalid format: each pair in pattern must consist of two elements")
                else:
                    pass
            except TypeError:
                raise TypeError('Please ensure "pattern" argument is a list of 2-element tuples. The tuple elements must be integers.')

    # perform error checking on elem2adc
    if elem2adc != None:
        check_if_one_to_one(elem2adc)



    # assign adc 2 hydrophone-element mappings. if not specified just go
    # with 1-by-1 to the ADC.
    if pattern==None:
        elem2adc = []
        for i in range(n_ch):
            adc_ch = i
            elem2adc.append(adc_ch)
    

    # Check if user has ADC Configured correctly
    if n_ch < n_times:
        msg = ("You have requested to use an hydrophone array model with %d" % (n_times)
               + " hydrophone elements, but the ADC is configured to use only"
               + " %d channels. Please increase the number of active ADC" % (n_ch)
               + " channels or decrease the number of hydrophones involved"
               + " in the array model")
        raise IOError(msg)

    # Check if user has hydrophone array spaced correctly
    pass

    # User can set the pattern or tdoa assignment here. Basically, each tuple takes on
    # the format (ref_element, target_element), but the ref_element
    # in this case should not be confused as whatever is the reference element
    # of the array. Rather, this 'pattern' can be any arbitrary combination
    # that yield's a leap in distance less than half a wavelength per pair.
    # whether the reference element is used first, last, or etc. does not
    # matter. This allows the user to continue using the phase detection method
    # on arrays that are even larger than the 1/2 the source signals wavelength.
    # One can visulize this like rungs on a ladder, where the climber can climb
    # a great vertical distance so long as there are intermediate rungs along the way.
    # This is meant to increase the usefulness of triangular (or even arbitrary 
    # polygonal) arrays. Every additional hydrophone element adds 2 addition
    # degrees of freedom. In other words, an n-polygonal array has 1+2(n-1) degrees
    # of freedom. So a 5 point hydrophone array has up to 9 degrees
    # of freedom so long as the user can come up with a sequence where each pair of 
    # of elements is not more than 1/2 wavelength apart.
    if pattern==None:
        if n_times == 2:    # for a 2 element array
            pattern = [(0, 1)]
        elif n_times == 3:  # for a 3 element array
            pattern = [(1, 0), (0, 2)]
        elif n_times == 4:  # for a 4 element array
            pattern = [(0, 1), (1, 2), (2, 3)]
    #^else, pattern is already specified

    # get relative delays for each combination, but ladder step along the way
    toa = [0] * n_times
    for (el_a, el_b) in pattern:
        
        # utilize mappings
        cha = elem2adc[el_a]
        chb = elem2adc[el_b]

        # check if user has h-phone array spaced correctly
        max_dist = c / target_freq
        el_dist = np.linalg.norm(array.element_pos[el_a] - array.element_pos[el_b])
        if max_dist < el_dist:
            print("get_heading.py: Warning! Array elements "
                  + " %d and %d" % (el_a, el_b)
                  + " are %.2f cm apart, which is more than" % (el_dist * 100)
                  + " 1 wavelength apart (%.2f cm) for the" % (max_dist * 100)
                  + " given target signal of %.2fKHz." % (target_freq / 1000)
                  + " Please fix this.")

        # Compute toa for each element.
        tdoa = compute_time_diff(
            target_freq,
            adc.sample_rate,
            adc.y[cha],
            adc.y[chb])

        toa[el_b] = tdoa - toa[el_a]

    # print delay for debugging purposes
    #import pdb; pdb.set_trace()

    # Adjust for sampling delays
    toa = np.array(toa) - np.array(adc.delay)[0:n_times]

    toa_relative = toa - np.amin(toa)
    print("relative toa's for each hydrophone = %s" % toa_relative)

    # Return values
    return toa_relative
