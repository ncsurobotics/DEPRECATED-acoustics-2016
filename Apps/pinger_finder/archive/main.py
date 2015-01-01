import pypruss
import mmap
import struct
import time
import boot

def init_pruss_env():
	# Initialize evironment
	pypruss.modprobe()	
	pypruss.init()		# Init the PRU
	pypruss.open(0)		# Open PRU event 0 which is PRU0_ARM_INTERRUPT
	pypruss.pruintc_init()  # Init the interrupt controller
	
	# INIT PRU Registers	
	pypruss.exec_program(0, "./init.bin") # Cleaning the registers
	pypruss.exec_program(1, "./init.bin") # Cleaning the registers	
	pypruss.pru_write_memory(0, 0x0000, [0x0,]*0x2000) # clearing ack bit from pru1
	pypruss.pru_write_memory(0, 0x2000, [0x0,]*0x2000) # clearing ack bit from pru1
	pypruss.pru_write_memory(0, 0x10000, [0x0,]*0x2EE0) # clearing ack bit from pru1
	#time.sleep(1)
	
def write_dst_to_PRU_mem(mem):
	pypruss.pru_write_memory(0, 1, [mem['addr'],])

def main():
	#Init variables
	ddr = {'addr': pypruss.ddr_addr(),
	       'size': pypruss.ddr_size(),
	}
	ddr['start'] = 0x10000000
	ddr['filelen'] = ddr['size']+0x10000000
	ddr['offset'] = ddr['addr']-0x10000000
	ddr['end'] =  0x10000000+ddr['size']
	

	# Load overlays
	boot.load()
	

	# initialize env
	init_pruss_env()
	write_dst_to_PRU_mem(ddr)
	

	# arm the device
	boot.arm()
	print("HLO")

	# Execute the PRU program
	a = time.time()
	pypruss.exec_program(1, "./pru1.bin") 		# Load firmware on PRU1
	pypruss.exec_program(0, "./ADS7865_sample.bin") # Load firmware on PRU0

	# Wait for PRU to finish its job.
	pypruss.wait_for_event(0)# Wait for event 0 which is conn to PRU0_ARM_INTERUPT
	loop_time = time.time() - a

	# Once signal has been received, clean up house
	pypruss.clear_event(0)	# Clear the event
	pypruss.exit()		# Exit PRU
	
	# Read the memory
	with open("/dev/mem", "r+b") as f:	# Open the physical memory device
		ddr_mem = mmap.mmap(f.fileno(), ddr['filelen'], offset=ddr['offset']) # mmap the right area
	
	for i in range(10):
		a = ddr['start']+i*4
		b = a+4
		read_back = struct.unpack("L", ddr_mem[a:b])[0]	# Parse the data
		print(read_back)
		
	print("That's a %ds loop you have there." % loop_time)
	print("done")
	import pdb; pdb.set_trace()

print("-"*50)
main()
