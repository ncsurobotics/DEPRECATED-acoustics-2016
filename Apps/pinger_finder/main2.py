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

def UI():
	# Generate location expressions
	loc = {'list': [],
		'curr': '',
		'text': ''
	}
	
	HOME = "HOME"
	loc['list'].append(HOME)

	# Print introductory text
	response(loc['list'][-1], "Welcome! Please, type in a command:")

	q = 0
	while(q == 0):
		# build environment variables
		loc['str'] = '>'.join(loc['list'])
		loc['curr'] = loc['list'][-1]

		# build status variables

		# query user for input
		user_input = query(loc['str'])

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
			pass

		elif 'arm_semi' == user_input:
			pass

		elif 'arm_oneshot' == user_input:
			pass

		elif 'dearm_adc' == user_input:
			pass

		else:
			response(loc['curr'], "Not a recognized command! Try again.")

def exit_app():
	print("Goodbye!")

def response(loc, s):
	"""response: a means of generating a system response.
	Takes a string s and outputs it with the current location in 
	the program, as designated by the string loc."""
	print(loc +": "+s)

def query(loc):
	"""query: a means of getting user input. 
	This function Takes a string loc and uses it to inform the user
	where he is located while the being asked for his input."""

	request = raw_input("{%s} >>" % loc)

	return request		
		

main()
