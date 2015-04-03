import logging
logging.basicConfig(level=logging.info, format='%(asctime)s - %(levelname)s - %(message)s')

import getHeading

def main(ADC,plt=None):
	"""Assume adc is already loaded"""
	
	"Establish various parameters"
	fs = ADC.
	
	"Arm the ADC."
	ADC.Ready_PRUSS_For_Burst()
	
	"Loop sample collection and processing"
	while(1):
	
		"Exit gracefully when user ctrl-D"
		try:
	
			"capture a set of samples
			y,t = ADC_Obj.Burst()
			
			"process simultaneous channels"
			angle = getHeading.calculate_heading(y[0],y[1])	
			
			"print computation to the user
			logging.info(
		
	
		except KeyboardInterrupt:
			print("Quitting program")
			user_input = 'q'