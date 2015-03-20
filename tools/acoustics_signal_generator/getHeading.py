import math
from scipy.fftpack import fft
from cmath import phase
	
def phase_diff_to_x_and_y(phase_diff, fundamental_freq):
	#Parameters
	v = 1473 #Speed of sound in water (m/s)
	d = (33.7e-3)/2 #half_distance between hydrophone elements
	
	#Compute wavelength of signal
	wavelength = v/fundamental_freq #meters
	
	
	#Compute delta D amongst hydrophones 
	D1minusD2 = (phase_diff/math.pi/2)*wavelength #meters
	
	#Compute delta t between hydrophones
	deltaT = D1minusD2/v #seconds
	
	#Generate vector components
	x = D1minusD2/2 #meters
	y = math.sqrt(d**2 - x**2)
	
	return (x,y)
	
def relative_wraparound(host_angle, guest_angle):
	if (guest_angle < host_angle-math.pi):
		#add 2pi
		guest_angle += 2*math.pi
	elif (guest_angle > host_angle+math.pi):
		#subtract 2pi
		guest_angle -= 2*math.pi

	return guest_angle
	
	
		

def calculate_heading(target_freq, a, b):
    
    #200 kHz sample rate (Hz)
    sample_rate = 200e3

    #Highest frequency captured - limited by sample rate (Hz)
    high_freq_bound = sample_rate / 2

    #Number samples (bins)
    sample_number = len(a)

    #Signal freq held in each index of arrays (Hz/bin)
    scale = sample_rate / sample_number

    #Index of arrays for complex number we want (bin)
    index = target_freq / scale
    
    #Update target frequency to one that matches scale of fft
    target_freq = scale*index

    #Getting our phases (radians)
    a_phase = phase(fft(a)[index])
    b_phase = phase(fft(b)[index])
    b_phase = relative_wraparound(a_phase, b_phase)
    print("a_phase = %f pi radians" % (a_phase/math.pi))
    print("b_phase = %f pi radians" % (b_phase/math.pi))
    
    #Compute phase difference
    phase_diff = a_phase-b_phase
    print("a leads b by %fpi radians" % (phase_diff/math.pi))
    
    #Get proportional x and y components (meters)
    (y,x) = phase_diff_to_x_and_y(phase_diff, target_freq)
    print("x=%f meters and y=%f meters." % (x,y))

    #Calculate and return heading using tan-1(phase_diffs)
    return (math.atan2(y, x))*180/math.pi
