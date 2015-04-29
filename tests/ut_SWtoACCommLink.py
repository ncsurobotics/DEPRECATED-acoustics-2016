import sys
sys.path.insert(0, '../host_communication')

import serial as s
import uart         # 

DEVICE1 = "/dev/ttyUSB0"
DEVICE2 = "/dev/ttyO5"

def INIT():
    uart.enable_uart()

def main():
    # Initialize ports
    INIT()
    P1 = s.Serial(DEVICE1, 9600)
    P2 = s.Serial(DEVICE2, 9600)

    # Send and read hello in one direction
    test_word1 = "Hello Acoustics\n"
    P1.write(test_word1)
    response1 = P2.readline()

    if (test_word1==response1):
        print("Success!")
    else:
        print("Failure")


    # Send and read hello in the other direction

if __name__ == '__main__':
    main()
