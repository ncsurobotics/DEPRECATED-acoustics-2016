import math
from scipy.fftpack import fft


def calculate_heading(target_freq, ref, a, b):

    #200 kHz sample rate
    sample_rate = 200000

    #Highest frequency captured - limited by sample rate
    high_freq_bound = sample_rate / 2

    #Number samples
    sample_number = len(ref)

    #Signal freq held in each index of arrays
    scale = high_freq_bound / sample_number

    #Index of arrays for complex number we want
    index = target_freq / scale

    #Getting our phases
    ref_phase = fft(ref)[index].imag
    a_phase = fft(a)[index].imag
    b_phase = fft(b)[index].imag
    
    print(ref_phase)

    #Calculate and return heading using tan-1(phase_diffs)
    return math.atan2(b_phase - ref_phase, a_phase - ref_phase)
