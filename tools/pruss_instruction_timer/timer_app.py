import pypruss
import mmap
import struct
import time


def main():
    # Initialize evironment
    pypruss.modprobe()
    pypruss.init()		# Init the PRU
    pypruss.open(0)		# Open PRU event 0 which is PRU0_ARM_INTERRUPT
    pypruss.pruintc_init()  # Init the interrupt controller

    # Configure PRU Registers
    pypruss.pru_write_memory(0, 0, [0, ])

    # Execute the PRU program
    a = time.time()
    pypruss.exec_program(0, "./bin/timer_app.bin")  # Load firmware on PRU0

    # Wait for PRU to finish its job.
    pypruss.wait_for_event(0)  # Wait for event 0 which is conn to PRU0_ARM_INTERUPT
    loop_time = time.time() - a

    # Once signal has been received, clean up house
    pypruss.clear_event(0)  # Clear the event
    pypruss.exit()		# Exit PRU

    print("That's a %ds loop you have there." % loop_time)
    print("Test completed: PRU was successfully opened and closed.")

print("-" * 50)
print("timer_app.py: Timing a dummy loop...")

if __name__ == '__main__':
    main()
