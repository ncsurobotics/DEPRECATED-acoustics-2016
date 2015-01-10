import numpy as np

class ADS7865:
	def __init__(self):
		self.fs = None
		
	def Sample(self, y, t):
		dt = t[1] - t[0]
		ts = 1/self.fs
		
		
		
		#create sampling array based on number of samples possible
		spdt = int(ts/dt)
		samp_sel = np.arange(0,t.size,spdt)
		
		#create an m array too
		new_len = int(t.size/spdt)
		m = np.arange(new_len)
		
		#sample the signals
		y_adc = np.zeros( (len(y),samp_sel.size) )
		for i in range(len(y)):
			y_adc[i] = y[i][samp_sel]
			
			
		return y_adc
		