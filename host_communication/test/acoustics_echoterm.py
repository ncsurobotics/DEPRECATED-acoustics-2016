import sys
sys.path.insert(0, '../')

import serial as s
import uart #enable_uart()

PORT_NAME = "/dev/ttyO5"

def INIT():
    uart.enable_uart()

def main():
    # Initialize ports
    INIT()
    print("Opening Port %s." % PORT_NAME)
    pAC = s.Serial(PORT_NAME, 9600, timeout=0.1)

    # Listen for texts and echo them ba
    print("Acoustics: UART(5) echo-terminal active. Currently listening for any data"
    + " that comes in from the FT232RL.")
    while 1:
        try:
            input = pAC.readline()
            if input:
                print("Acoustics: RX'd %r. Echoing it back out." % input)
                pAC.write(input+'\n')
                
        except KeyboardInterrupt:
            print("Closing Port %s." % PORT_NAME)
            pAC.close()
            break
            


if __name__ == '__main__':
    main()