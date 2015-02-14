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
	HOME = "HOME: "

	# Print introductory text
	raw_input(HOME + "Welcome! Please, type in a command: \n>>")

def exit_app():
	print("Goodbye!")

		
		

main()
