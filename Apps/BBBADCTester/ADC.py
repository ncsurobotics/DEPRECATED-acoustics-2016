import BBBIO
import time

class ADS7865:
	adcInit1p1 = 260 # 0x104
	adcInit1p2 = 384 # 0x900
	WAIT_TIME = 1

	def __init__(self,io):
		self.state = 'happy!'
		self.PortDB = io['PortDB']
		self.WR = io['/WR']
		self.BUSY = io['BUSY']
		self.CS = io['/CS']

	def pulseWR(self):
		callee_s = self.WR.value
		self.WR.write(1)
		time.sleep(WAIT_TIME)
		self.WR.write(0)
		time.sleep(WAIT_TIME)
		self.WR.write(callee_s)

	def Init_ADC(self,io):
		self.PortDB.setPortDirection('in')
		self.WR.setPortDirection('out')
		self.BUSY.setPortDirection('in')
		self.CS.setPortDirection('out')
		self.WR.write(1)
		self.CS.write(0)

		self.WriteOnDB(adcInit1p1) # 0x104;
		io['PortDB'].write(adcInit1p2) # 0x900
		self.WR.write(1)

	def WriteOnDB(cmd):
		callee_sPD = self.PortDB.portDirection
		callee_sWR = self.WR.value
		
		self.WR.write(0)
		self.PortDB.setPortDir("out")
		self.PortDB.write(cmd)
		self.PortDB.read()

		sleep(WAIT_TIME)
		self.WR.write(1)		
		self.PortDB.setPortDir(callee_sPD)

	def Close():
		self.PortDB.close()
		self.WR.close()
		self.BUSY.close()
		self.CS.close()
