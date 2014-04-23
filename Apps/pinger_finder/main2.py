import ADC
import os
import watch_for_dead_bits
import ADS7865_Sampler

help_text = """quit: quit the program.
help: display this help text."""

# 1. #####################################
##################### Main Sequence ######
##########################################

def main():
	# Display title sequence
	title()

	# Bring up user interface
	UI()
	
	# User is finished. Print Closing sequence
	exit_app()



	
# 2. #####################################
##################### Host Menu  ######
##########################################
	
def UI():
	# Generate location expressions
	HOME = "HOME"
	ADC_APP = "ADC_APP"
	ADC_CONF = "CONFIG"
	loc = location(HOME)

	# Print introductory text
	response(loc.curr, "Welcome! Please, type in a command:")

	q = 0
	ADC_active = False
	while(q == 0):
		# build status variables

		# query user for input
		user_input = query(loc.path)

		# Log user response
		pass
		
		# a ############################
		###### Global Command class ####
		################################

		# respond to user input
		if ('quit' == user_input) or ('q' == user_input):
			q = 1

		elif ('help' == user_input) or ('h' == user_input):
			print('-'*50)
			print(help_text)
			print('-'*50)
			
		# b ############################
		########### ADC cmd Class ######
		################################

		elif ('adc_status' == user_input) or ('s' == user_input):
			if ADC_active:
				report_adc_status(ADS7865)
			else:
				response(loc.curr, "Please run 'load_adc_app' first")
			
		elif ('load_adc_app' == user_input) or ('l' == user_input):
			ADC_active = True
			ADC_app_splash();
			loc.push(ADC_APP)
			response(loc.curr, "Loading ADC app...")
			ADS7865 = ADC.ADS7865()
			response(loc.curr, "Done loading app. Entering environment...")
			
		elif ('unload_adc_app' == user_input) or ('u'==user_input):
			response(loc.curr, "Closing app...")
			ADS7865.Close()
			loc.pop()
			
		elif ('adc_debug_wizard' == user_input) or ('d' == user_input):
			if ADC_active:
				adc_debug_wizard(ADS7865)
			else:
				response(loc.curr, "Please run 'load_adc_app' first")
				
		elif ('adc_collect_data' == user_input) or ('data' == user_input):
			if ADC_active:
				ADS7865_Sampler.main(ADS7865)
			else:
				response(loc.curr, "Please run 'load_adc_app' first")
			
		elif ('adc_conf' == user_input) or ('o' == user_input):
			loc.push(ADC_CONF)
			adc_config(ADS7865, loc)
			loc.pop()
			
		# c ############################
		########### utility cmd Class ##
		################################
		
		elif 'EOF' == user_input:
			response(loc.curr, "End of input file reached")

		else:
			response(loc.curr, "Not a recognized command! Try again.")
			usage()
	
# 3. #####################################
########### ADC function repository ######
##########################################
def report_adc_status(ADC_object):
	sr = ADC_object.sampleRate
	sl = ADC_object.sampleLength
	armed = ADC_object.arm_status
	_RD = eval(ADC_object._RD.readStr())
	_WR = eval(ADC_object._RD.readStr())
	
	print("\tsl:\t%d samples" % sl)
	print("\tsr:\t%d samples/sec" % sr)
	print("\tarmed:\t%s" % armed)
	print("\t_RD:\t%d" % _RD)
	print("\t_WR:\t%d" % _WR)

def adc_debug_wizard(ADC_object):
	keys = ['watch_for_dead_bits', 
			'read_DBus',
			'check_DBus', 
			'dummy_read_seq', 
			'dummy_read_dac',
			'read_seq',
			'read_dac',
			'q']
	
	q = 0
	while (q != 1):
		# Print status
		print("current status:")
		report_adc_status(ADC_object); print("")
		
		# Print debug options
		print("enter one of the following debugging commands")
		printDebugs(keys); print("")
		
		# Take user input
		user_input = query('adc_debug_wizard')
		
		# route user
		if 'q' == user_input:
			q = 1
		elif ('watch_for_dead_bits' == user_input) or ('1' == user_input):
			watch_for_dead_bits.main(ADC_object)
			
		elif('3' == user_input): #check_DBus
			temp = ADC_object.DBus.readStr()
			print("debug_wizard: DBus = %s" % temp)
			
		elif('6' == user_input):
			ADC_object.Read_Seq()
			
		elif ('7' == user_input):
			ADC_object.Read_Dac()
		
		
def printDebugs(keys):
	row = 1
	for key in keys:
		print("\t%d: %s" % (row,key))
		row += 1
		
		
def adc_config(ADC_OBJ, loc):
	response(loc.curr, "You have entered the ADC config mode")
	q = 0
	response(loc.curr, "Please enter a sample length")
	SL = query(loc.curr)
	response(loc.curr, "Please enter a sample rate")
	SR = query(loc.curr)
	ADC_OBJ.sampleLength = int(eval(SL))
	ADC_OBJ.sampleRate = eval(SR)
	response(loc.curr, "Exiting ADC config mode")
	
# 4. #####################################
##################### Elements ###########
##########################################

def title():
	bar = '-'*50

	print(bar)
	print(" "*15 + " PINGER FINDER")
	print(bar)
	
def exit_app():
	print("Goodbye!")

def ADC_app_splash():
	bar = '- '*15
	os.system("clear")
	print(bar)
	print('v-'*15)

def usage():
	text = ["  (h)elp: Get help.\n",
		"  (q)uit: quit this program.\n",
		"  adc_(s)tatus: prints data regarding the adc.\n",
		"  (l)oad_adc_app: Startup the adc enviroment.\n",
		"  (u)nload_adc_app: Close adc environment.\n",
		"  adc_c(o)nf: Change Settings of the ADC.\n",
		"  adc_(d)ebugger: pull up the debugging menu"]
	print(''.join(text) )

class location():
	def __init__(self, init):
		self.list = [init]
		self.refresh()

	def push(self, new_loc):
		"""push: method for updating the loc object with
		new_loc, a string"""
		(self.list).append(new_loc)
		self.refresh()
	
	def pop(self):
		"""pop: method for stepping back a location."""
		self.list.pop()
		self.refresh()

	def refresh(self):
		"""refresh: method for updating several attribute of this
		class. primarily designed for internal use."""
		self.curr = self.list[-1]
		self.path = '>'.join(self.list)



def response(loc, s):
	"""response: a means of generating a system response.
	Takes a string s and outputs it with the current location in 
	the program, as designated by the string loc."""
	print('\n' +loc +": "+s)

def query(loc):
	"""query: a means of getting user input. 
	This function Takes a string loc and uses it to inform the user
	where he is located while the being asked for his input."""

	request = raw_input("{%s} >>" % loc)

	return request		


main()
