import serial
from sys import argv

print('-'*50)
print("Acoustics Client Communication App")


def main():
	# Initialize connection
	ser = serial.Serial("/dev/tty.usbserial-A5025L80", 9600)
	
	# Check if successful
	cmd_helloBBB()
	response = ser.readline()
	if hello in response:
		print(response)
	else:
		print("main: Hmmm. I didn't get any response from the beaglebone... Check your connections.")
		exit(1)
		
	# Connection successful. No going to run through a list of things the BBB should be able to handle.
	cmd_echo('string')
	cmd_burst(30)
	cmd_burst()
	cmd_seekAndBurst(30)
	cmd_seekAndBurst()
	cmd_configure('burst_size')
	cmd_readDataBlock()

# Set up the program, or grant user help if he needs it.
argc = len(argv)
if argc == 2:
	if 'h' in argv[1]:
		print("help text.")
		exit(1)

main
