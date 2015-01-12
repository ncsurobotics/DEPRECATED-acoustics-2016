import numpy as np

def Isolate(y):
	#Initialize parameters
	buf = 0
	thr = 0.02
	
	#Initialize parameters for start point
	v = 0
	m = -1
	
	#Compute start point
	while v < thr:
		m += 1
		v = y[m]
	start = m-buf
	
	#Initialize parameters for end point
	v=0
	m=y.size
	
	#Compute endpoint
	while v < thr:
		m -= 1
		v = y[m]
	end = m+buf
	
	return (start,end)
	
		
def FFT(x,fs):
	# Initialize parameters
	M = x.size
	Theta_s = 2*np.pi/M
	X = [0]*M
	for k in range(M):
		DFT = 0
		
		for m in range(M):
			a = x[m]*np.exp(1j*m*Theta_s*k)
			DFT += a
		
		X[k] = DFT/M
		
			
	

class BBB:
	def __init__(self):
		pass
	
	def Vectorize1(self,y,fs):
		n = y.shape[0] #n elements/channels
		y_slice = [0]*n
		
		# Let's see if we can get the ball rolling by obtaining the phase of just one channel
		# Slice channels to particular length base on pulse length
		(start,end) = Isolate(y[0])
		y_slice[0] = y[0][start:end]
		
		# FFT
		FFT(y_slice[0],fs)
		
		# Determine phase of 22khz signal
		
		
		
		