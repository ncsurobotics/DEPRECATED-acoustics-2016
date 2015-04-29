import sys
sys.path.insert(0, '../host_communication')

import serial as s
import uart #enable_uart()

DEVICE1 = "/dev/ttyUSB0"
TEST_WORD = "Hello"

def INIT():
    uart.enable_uart()

def main():
    # Ask user to setup for test
    print("Please do the following:\n"
    + " 1. Connect the FT232RL to the USB port on the Beaglebone.\n"
    + " 2. Short the RX and TX terminals together on the FT232RL board.\n"
    + " 3. Ensure that the FT232RL has 5V power.\n")
    raw_input("Press ENTER when you're ready to begin the test: ")

    # Initialize ports
    P1 = s.Serial(DEVICE1, 9600, timeout=0.1)

    # Send and read hello in one direction
    P1.write(TEST_WORD)
    print("Tx'ed %r" % (TEST_WORD))
    result = P1.readline()

    # Check value
    print("Rx'ed %r" % result)
    if (result == TEST_WORD):
        print("SUCCESS! The board is working!")
    else:
        print("FAILURE!!! Something on the FT232RL is not working.")

if __name__ == '__main__':
    main()
