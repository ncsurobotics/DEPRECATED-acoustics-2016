import numpy as np

class SG:
	def __init__(self,end=1e-3):
		self.tstart = 0
		self.tend = end
		
	def Sin(self,f,t):
		pi = np.pi
		base= np.ones(t.size)

		for i in range(t.size):
			if t[i] < self.tstart:
				base[i] = 0
			elif t[i] > self.tend:
				base[i] = 0
			else:
				pass
			
		w= 2*pi*f
		y = np.sin(w*t-pi)*base
		
		return y