import sys
sys.path.insert(0, '../')

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
    P1.write("Hello\n")
    P2.readline()

    # Send and read hello in the other direction

if __name__ == '__main__':
    main()
