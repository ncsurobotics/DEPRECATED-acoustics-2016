import pypruss
import mmap
import struct


def main():
	#Initialize evironment
	pypruss.modprobe()
	
	pypruss.init()		# Init the PRU
	pypruss.open(0)		# Open PRU event 0 which is PRU0_ARM_INTERRUPT
	pypruss.pruintc_init()  # Init the interrupt controller
	pypruss.exec_program(0, "./hello_pru.bin") # Load firmware on PRU0
	pypruss.wait_for_event(0)# Wait for event 0 which is conn to PRU0_ARM_INTERUPT
	pypruss.clear_event(0)	# Clear the event
	pypruss.exit()		# Exit PRU

	print("Test completed: PRU was successfully opened and closed.")

print("-"*50)
print("test.py: testing basic functionality...")
main()
