import numpy as np

class BiHydrophoneArray:
	def __init__(self):
		self.d = None #meters
		self.origin = None
		self.src_loc = None
		self.signalDict = None
		self.mediumModel = None
		self.maxSpread = None
		
	def Capture(self, x, t, channelModel):
		dt = t[1]-t[0]
		Hyd_loc = [0,0]
		dist = [0,0]
		DM = [0,0]
		y = [np.zeros(t.size), np.zeros(t.size)]
		Hyd_loc[0] = self.origin + np.array([-self.d/2,0])
		Hyd_loc[1] = self.origin + np.array([self.d/2,0])
		dist[0] = np.linalg.norm(Hyd_loc[0]-self.src_loc)
		dist[1] = np.linalg.norm(Hyd_loc[1]-self.src_loc)
		
		timeDiff = (dist[0] - dist[1])/self.mediumModel.c
		if timeDiff > self.maxSpread:
			print("Rx: Warning! Fold-over has occured!")
		
		if (4*dist[0]/self.mediumModel.c > t[-1]-t[0]) or (4*dist[1]/self.mediumModel.c > t[-1]-t[0]):
			print("Rx: Warning! Delay exceeds time boundaries. please increase time span or reduce delay.")
			
		dm = int(timeDiff/dt)
		
		if dm < 100:
			print("Rx: Warning! dm = %d, which is a bit small (<100). Maybe try increasing dt in the host program."
					% dm)
		
		# compute data for hydrophone 0
		DM[0] = int(dist[0]/self.mediumModel.c/dt)
		for i in range(DM[0],t.size):
			m = t.size - i
			y[0][m] = x[m-DM[0]]
			
		# compute data for hydrophone 1
		DM[1] = int(dist[1]/self.mediumModel.c/dt)
		for i in range(DM[1],t.size):
			m = t.size - i
			y[1][m] = x[m-DM[1]]
			
		
		return y