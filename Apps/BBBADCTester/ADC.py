import BBBIO
import time

class ADS7865:
	WAIT_TIME = 1

	def __init__(self,io):
		self.state = 'happy!'
		self.PortDB = io['PortDB']
		self.WR = io['/WR']
		self.BUSY = io['BUSY']
		self.CS = io['/CS']
		self.RD = io['/RD']
		self._CONVST = io['/CONVST']

	def PulseWR(self):
		callee_s = self.WR.value
		self.WR.writeToPort(1)
		time.sleep(self.WAIT_TIME)
		self.WR.writeToPort(0)
		time.sleep(self.WAIT_TIME)
		self.WR.writeToPort(callee_s)

	def Init_ADC(self):
		self.PortDB.setPortDir('in')
		self.WR.setPortDir('out')
		self.WR.writeToPort(1)
		self.BUSY.setPortDir('in')
		self.RD.setPortDir('out')
		self.RD.writeToPort(1)
		self._CONVST.setPortDir('out')
		self._CONVST.writeToPort(1)
		self.CS.setPortDir('out')
		self.CS.writeToPort(0)

		print('ADS7865: Initialization complete.')

	def Configure(self,cmd):
		callee_sPD = self.PortDB.portDirection
		
		self.WR.writeToPort(0)
		self.PortDB.setPortDir("out")
		self.PortDB.writeToPort(cmd)
		print('ADS7865: Databus cmd %s has been sent.' % self.PortDB.readStr())

		time.sleep(self.WAIT_TIME)
		self.WR.writeToPort(1)		
		self.PortDB.setPortDir(callee_sPD)

	def StartConv(self):
		#a = time.time()
		self._CONVST.writeToPort(0)
		self._CONVST.writeToPort(1)
		#b = time.time()
		#print("_CONVST signal was low for %f seconds." % (b-a))

	def ReadConv(self):
		self.RD.writeToPort(0)
		result = self.PortDB.readStr()
		self.RD.writeToPort(1)
		return result

	def Close(self):
		self.CS.writeToPort(1)
		self.PortDB.close()
		self.WR.close()
		self.BUSY.close()
		self.CS.close()
		self.RD.close()
		self._CONVST.close()
