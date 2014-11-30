import BBBIO
import time

class ADS7865:
	adcInit1p1 = 4095 # 0x104
	adcInit1p2 = 0 # 0x900
	WAIT_TIME = 1

	def __init__(self,io):
		self.state = 'happy!'
		self.PortDB = io['PortDB']
		self.WR = io['/WR']
		self.BUSY = io['BUSY']
		self.CS = io['/CS']
		self.RD = io['/RD']

	def pulseWR(self):
		callee_s = self.WR.value
		self.WR.writeToPort(1)
		time.sleep(self.WAIT_TIME)
		self.WR.writeToPort(0)
		time.sleep(self.WAIT_TIME)
		self.WR.writeToPort(callee_s)

	def Init_ADC(self):
		self.PortDB.setPortDir('in')
		self.WR.setPortDir('out')
		self.BUSY.setPortDir('in')
		self.CS.setPortDir('out')
		self.WR.writeToPort(1)
		self.CS.writeToPort(0)

		self.WriteOnDB(self.adcInit1p1) # 0x104;
		self.WriteOnDB(self.adcInit1p2) # 0x900
		print('ADS7865: Initialization complete.')

	def WriteOnDB(self,cmd):
		callee_sPD = self.PortDB.portDirection
		callee_sWR = self.WR.value
		
		self.WR.writeToPort(0)
		self.PortDB.setPortDir("out")
		self.PortDB.writeToPort(cmd)
		print('ADS7865: Databus cmd %s has been sent.' % self.PortDB.readStr())

		time.sleep(self.WAIT_TIME)
		self.WR.writeToPort(1)		
		self.PortDB.setPortDir(callee_sPD)

	def Close(self):
		self.PortDB.close()
		self.WR.close()
		self.BUSY.close()
		self.CS.close()
		self.RD.close()
