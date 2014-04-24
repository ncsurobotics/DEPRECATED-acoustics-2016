import BBBIO
import ADC

def main():
	# settings
	scope = 'FULL'	
	DB_pin_table = ['P8_03','P8_04','P8_05','P8_06','P8_07','P8_08','P8_09','P8_10','P8_11','P8_12','P8_13','P8_14']
	WR_pin = 'P8_15'
	BUSY_pin = 'P8_16'
	CS_pin = 'P8_17'
	
	
	# program
	io = {'PortDB': BBBIO.Port(),
		'/WR':BBBIO.Port(WR_pin),
		'BUSY': BBBIO.Port(BUSY_pin),
		'/CS': BBBIO.Port(CS_pin)
	}

	
	io['PortDB'].createPort(DB_pin_table)
	
	ADS7865 = ADC.ADS7865(io)
	import pdb; pdb.set_trace()
main()
