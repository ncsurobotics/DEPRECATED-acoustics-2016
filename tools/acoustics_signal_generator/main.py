import AcSigGen
from getHeading import calculate_heading

def main():
	# Setup param
	target_freq = 22e3
	
	# Load test signal
	sig = AcSigGen.main()
	
	# Get the heading
	heading = calculate_heading(target_freq,sig[0],sig[1])
	
	# Print the heading
	print("pinger is %d degrees to the right." % heading)
	
main()