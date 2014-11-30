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
	
	
	# program
	io = {'PortDB': BBBIO.Port(),
		'/WR':BBBIO.Port(WR_pin),
		'BUSY': BBBIO.Port(BUSY_pin),
		'/CS': BBBIO.Port(CS_pin),
		'/RD': BBBIO.Port(RD_pin)
	}

	# Deprecated... should remove and use the new format.	
	io['PortDB'].createPort(DB_pin_table)

	# ADC initialization
	ADS7865 = ADC.ADS7865(io)
	ADS7865.Init_ADC()
	import pdb; pdb.set_trace()

	ADS7865.Close()
main()
