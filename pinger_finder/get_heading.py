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


def compute_relative_delay_times(adc, target_freq, array, c):
    """
    Computes the relative delay times for each hydrophone pair
    """
    # Initialize parameters
    n_ch = adc.n_channels
    n_times = array.n_elements
    y = adc.y

    # Check if user has ADC Configured correctly
    if n_ch < n_times:
        msg = ("You have requested to use an hydrophone array model with %d" % (n_times)
               + " hydrophone elements, but the ADC is configured to use only"
               + " %d channels. Please increase the number of active ADC" % (n_ch)
               + " channels or decrease the number of hydrophones involved"
               + " in the array model")
        raise IOError(msg)

    # Check if user has hydrophone array spaced correctly

    # User can set the pattern or tdoa assignment here. Basically, each tuple takes on
    # the format (ref_element, target_element), but the ref_element
    # in this case should not be confused whatever is the reference element
    # of the array. Rather, this 'pattern' can be any arbitrary combination
    # that yield's a leap in distance less than half a wavelength per pair.
    # whether the reference element is used first, last, or etc. does not
    # matter.

    if n_times == 2:    # for a 2 element array
        pattern = [(0, 1)]
    elif n_times == 3:  # for a 3 element array
        pattern = [(1, 0), (0, 2)]
    elif n_times == 4:  # for a 4 element array
        pattern = [(0, 1), (1, 2), (2, 3)]

    # get relative delays for each combination, but ladder step along the way
    toa = [0] * n_times
    for (el_a, el_b) in pattern:

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
            adc.y[el_a],
            adc.y[el_b])

        toa[el_b] = tdoa - toa[el_a]

    # print delay for debugging purposes
    #import pdb; pdb.set_trace()

    # Adjust for sampling delays
    toa = np.array(toa) - np.array(adc.delay)[0:n_times]

    toa_relative = toa - np.amin(toa)
    print("relative toa's for each hydrophone = %s" % toa_relative)

    # Return values
    return toa_relative
