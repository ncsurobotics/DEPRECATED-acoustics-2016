import sys
sys.path.insert(0, '../')

import serial as s
import uart #enable_uart()

PORT_NAME = "/dev/ttyUSB0"

def INIT():
    pass

def main():
    # Initialize ports
    print("Opening Port %s." % PORT_NAME)
    pUSB = s.Serial(PORT_NAME, 9600, timeout=0.2)

    # Listen for texts and echo them ba
    print("USB terminal active. Any data you enter will be sent"
    + "Out over serial via the FT232RL.")
    while 1:
        try:
            input = raw_input()
            pUSB.write(input)
            
            # Read the data back in
            result = pUSB.readline()
            if not (result):
                print("TIMEOUT!!!!")
            else:
                print("Returned message: %s" % result)
                
        except KeyboardInterrupt:
            print("Closing Port %s." % PORT_NAME)
            pUSB.close()
            break
            


if __name__ == '__main__':
    main()