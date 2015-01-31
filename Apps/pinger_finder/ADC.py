import pypruss		#Python PRUSS wrapper
import mmap
import struct
import boot			#
import time			#sleep
import BBBIO		#Yields functions for working with GPIO

#Global ADC program Constants
PRU0_SR_Mem_Offset = 3
HC_SR = 0xBEBC200
fclk = 200e6

#Global Functions
def Read_Sample(user_mem, Sample_Length):
	print("ADC: Still have to write documentation about the structure of user_mem variable...")
	
	with open("/dev/mem", "r+b") as f:	# Open the physical memory device
		ddr_mem = mmap.mmap(f.fileno(), user_mem['filelen'], offset=user_mem['offset']) # mmap the right area

	y = []
	for i in range(Sample_Length):
		a = user_mem['start']+i*4
		b = a+4
		c = struct.unpack("L", ddr_mem[a:b])[0]	# Parse the data
		y = y + [c,]
		#print(c)
		
	return y
		
######################################
######    ADS7865 Class ##############
#####################################

DB_pin_table = ['P8_08','P8_09','P8_10','P8_11','P8_12','P8_13','P8_14','P8_15','P8_16','P8_17','P8_18','P8_19']
WR_pin = 'P9_11'
BUSY_pin = 'P9_12'
CS_pin = 'P9_13'
RD_pin = 'P9_14'
CONVST_pin = 'P9_15'

class ADS7865:
	def __init__(self, SR=0, L=0):
	
		#GPIO Stuff
		self.DBus = BBBIO.Port(DB_pin_table)
		self.DBus.setPortDir("out")
		
		self.WR = BBBIO.Port(WR_pin)
		self.WR.setPortDir("out")
	
		#PRUSS Stuff
		self.ddr = {}
		self.ddr['addr'] = pypruss.ddr_addr()
		self.ddr['size'] = pypruss.ddr_size()
		self.ddr['start'] = 0x10000000
		self.ddr['filelen'] = self.ddr['size']+0x10000000
		self.ddr['offset'] = self.ddr['addr']-0x10000000
		self.ddr['end'] =  0x10000000+self.ddr['size']
		
		print("ADS7865: Allowing one 32bit memory block per sample, it is "
			+ "possible to collect %.1fK Samples in a single burst. These "
			% (self.ddr['size']/1000)
			+ "sample points are stored in DDRAM, which is found at the "
			+ "address range starting at %s" % (hex(self.ddr['addr'])))
		
		self.sampleRate = SR
		self.sampleLength = L
		
		#Load overlays
		boot.load()
		
	############################
	#### GPIO Commands  #######
	############################
	def Config(self, cmd_list):
		# Callee save the port direction
		callee_sPD = self.DBus.portDirection
		
		# 
		for cmd in cmd_list:
			self.WR.writeToPort(0)		#Open ADC's input Latch
			self.DBus.setPortDir("out")	#Latch open, safe to make DB pins an out
			self.DBus.writeToPort(cmd)	#Write the value to the DB pins
			print('ADS7865: Databus cmd %s has been sent.' % self.DBus.readStr())
			self.WR.writeToPort(1)		#Latch down the input
		
		self.DBus.setPortDir(callee_sPD)#Return DB pins back to inputs.
	
	def EZConfig(self, sel):
		#NOTES TO USER
		#--At powerup, sequencer_register=0x000
		#--Capturing one channel (non-pair) in isolation is doable by selecting sel=0
		#or sel=1 (since ADS7865 resets the data_output pointer at the beginning of every
		#CONVST), but the user must also take the extra precaution to disable the
		#"sub-sampling" portion of the PRUSS code in order for it to work.
	
		#Single channel (pair) enable
		if sel==0:
			#User has chosen to sample the 0a/0b differential channel pair.
			self.Config([0x100])
		elif sel==1:
			#User has chosen to sample the 1a/1b differential channel pair.
			self.Config([0x300])

		#Single channel (pair) enable with sequencer reinitialization
		elif sel==2:
			#User has chosen to sample the 0a/0b differential channel pair 
			#while disabling the sequencer register
			self.Config([0x101,0x000])
		elif sel==3:
			#User has chosen to sample the 0a/0b differential channel pair 
			#while disabling the sequencer register
			self.Config([0x301,0x000])
			
		#Dual channel (pair) enable
		elif sel==4:
			#User has chosen to sample the 0a/0b -> 1a/1b in FIFO style
			self.Config([0x101,0x230])
		elif sel==5:
			#User has chosen to sample the 1a/1b -> 0a/0b in FIFO style
			self.Config([0x101,0x2c0])
	
	############################
	#### PRUSS Commands  #######
	############################
	def Ready_PRUSS_For_Burst(self, SR=None):
		# Initialize variables
		if SR is None:
			SR = self.sampleRate
			
		if SR == 0:
			print("SR currently set to 0. Please specify a sample rate.")
			exit(1)
			
		SR_BITECODE = int(round(1.0/SR*fclk)) # Converts user SR input to Hex.
		
		# Initialize evironment
		pypruss.modprobe()	
		pypruss.init()		# Init the PRU
		pypruss.open(0)		# Open PRU event 0 which is PRU0_ARM_INTERRUPT
		pypruss.pruintc_init()  # Init the interrupt controller

		# INIT PRU Registers	
		pypruss.exec_program(0, "./init0.bin") # Cleaning the registers
		pypruss.exec_program(1, "./init1.bin") # Cleaning the registers	
		pypruss.pru_write_memory(0, 0x0000, [0x0,]*0x0800) # clearing pru0 ram
		pypruss.pru_write_memory(0, 0x0800, [0x0,]*0x0800) # clearing pru1 ram
		pypruss.pru_write_memory(0, 0x4000, [0x0,]*300) # clearing ack bit from pru1
		pypruss.pru_write_memory(0, PRU0_SR_Mem_Offset, [SR_BITECODE,]) # Setting samplerate
		
		pypruss.exec_program(1, "./pru1.bin") 		# Load firmware on PRU1
		
		# end readying process by arming the PRUs
		boot.arm()

	def Reload(self):
		print 'Reload: "I do nothing."'
	
	def Burst(self, length=None):
		if length is None:				#Optional argument for sample length
			length = self.sampleLength
			
		#Share DDR RAM Addr with PRU0
		pypruss.pru_write_memory(0, 1, [self.ddr['addr'],])
		
		#Share SL with PRU0
		pypruss.pru_write_memory(0, 2, [length*4-8,])
		
		#Launch the Sample collection program
		a = time.time()
		pypruss.exec_program(0, "./ADS7865_sample.bin") # Load firmware on PRU0
		
		# Wait for PRU to finish its job.
		pypruss.wait_for_event(0)# Wait for event 0 which is conn to PRU0_ARM_INTERUPT	
		b = time.time()
		t = b-a

		#Once signal has been received, clean up house
		#pypruss.clear_event(0)	# Clear the event
		#pypruss.exit()			# Exit PRU
		
		# Read the memory
		y = Read_Sample(self.ddr, length)
			
		return y,t