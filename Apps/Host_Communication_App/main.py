import serial
from sys import argv

print('-'*50)
print("Acoustics Client Communication App")


def main():
	

# Set up the program, or grant user help if he needs it.
argc = len(argv)
if argc == 2:
	if 'h' in argv[1]:
		print("help text.")
		exit(1)

main
