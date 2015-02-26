import ADC
import os

help_text = """quit: quit the program.
help: display this help text."""

def main():
	# Display title sequence
	title()

	# Bring up user interface
	UI()
	
	# User is finished. Print Closing sequence
	exit_app()


def title():
	bar = '-'*50

	print(bar)
	print(" "*15 + " PINGER FINDER")
	print(bar)

def ADC_app_splash():
	bar = '- '*15
	os.system("clear")
	print(bar)
	print('v-'*15)

def usage():
	text = ["help: Get help.\n",
		"quit: quit this program.\n",
		"review: not encoded yet.\n",
		"load_adc_app: Startup the adc enviroment.\n",
		"unload_adc_app: Close adc environment"]
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

def UI():
	# Generate location expressions
	HOME = "HOME"
	ADC_APP = "ADC_APP"
	ADC_CONF = "CONFIG"
	loc = location(HOME)

	# Print introductory text
	response(loc.curr, "Welcome! Please, type in a command:")

	q = 0
	while(q == 0):
		# build status variables

		# query user for input
		user_input = query(loc.path)

		# Log user response
		pass

		# respond to user input
		if 'quit' == user_input:
			q = 1

		elif 'help' == user_input:
			print('-'*50)
			print(help_text)
			print('-'*50)

		elif 'review' == user_input:
			pass
			# enter_review_app()

		elif 'load' == user_input:
			pass

		elif 'load_adc_app' == user_input:
			ADC_app_splash();
			loc.push(ADC_APP)
			response(loc.curr, "Loading ADC app...")
			ADS7865 = ADC.ADS7865()
			response(loc.curr, "Done loading app. Entering environment...")
			
		elif 'adc_conf' == user_input:
			loc.push(ADC_CONF)
			enter_adc_config(ADS7865, loc)
			loc.pop()

		elif 'arm_semi' == user_input:
			pass

		elif 'arm_oneshot' == user_input:
			pass

		elif 'unload_adc_app' == user_input:
			response(loc.curr, "Closing app...")
			ADS7865.Close()
			loc.pop()
		elif 'EOF' == user_input:
			response(loc.curr, "End of input file reached")

		else:
			response(loc.curr, "Not a recognized command! Try again.")
			usage()

def exit_app():
	print("Goodbye!")

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
		
def EZ_enter_adc_config(ADC_OBJ, loc):
	response(loc.curr, "You have entered the ADC config mode")
	q = 0
	while (q != 0 ):
		response(loc, "Please enter a sample size")
		SL = query(loc)
		response(loc, "Please enter a sample rate")
		SR = 
	response(loc.curr, "Exiting ADC config mode")

main()
