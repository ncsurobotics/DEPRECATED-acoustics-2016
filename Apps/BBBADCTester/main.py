import BBBIO
import ADC

def main():
	# settings
	scope = 'FULL'	
	DB_pin_table = ['P8_08','P8_09','P8_10','P8_11','P8_12','P8_13','P8_14','P8_15','P8_16','P8_17','P8_18','P8_19']
	WR_pin = 'P9_11'
	BUSY_pin = 'P9_12'
	CS_pin = 'P9_13'
	RD_pin = 'P9_14'
	CONVST_pin = 'P9_15'
	
	leave = False
	
	# program
	io = {'PortDB': BBBIO.Port(DB_pin_table),
		'/WR':BBBIO.Port(WR_pin),
		'BUSY': BBBIO.Port(BUSY_pin),
		'/CS': BBBIO.Port(CS_pin),
		'/RD': BBBIO.Port(RD_pin),
		'/CONVST': BBBIO.Port(CONVST_pin),
	}

	# ADC initialization
	ADS7865 = ADC.ADS7865(io)
	ADS7865.Init_ADC()
	import pdb; pdb.set_trace()

	##########
	## LOOP ##
	##########
	while leave == False:
		# Select experiment
		experiment = 'trace CH1'		
		if experiment == 'trace CH1':
			ADS7865.Configure(256) # 0x100
		if experiment == 'trace CH1 and CH2':
			self.Configure(300) # 0x104;
			self.Configure(2304) # 0x900
			
		# Start conversion
		ADS7865.StartConv()
		
		#
		ADS7865.ReadConv()
		import pdb; pdb.set_trace()

		leave = True
	ADS7865.Close()

main()
