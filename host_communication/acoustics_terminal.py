from os import path

# Get variables for navigating the file system.
root_directory = path.dirname(path.dirname(path.realpath(__file__)))
hc_directory = path.join(root_directory, "host_communication")
pf_directory = path.join(root_directory, "pinger_finder")

import sys
sys.path.insert(0, hc_directory)
sys.path.insert(0, pf_directory)

import serial as s
import uart #enable_uart()
import oneclk

PORT_NAME = "/dev/ttyO5"

def INIT():
    uart.enable_uart()

def main():
    # Initialize ports
    INIT()
    print("Opening Port %s." % PORT_NAME)
    pAC = s.Serial(PORT_NAME, 9600, timeout=0.1)

    # Listen for texts and echo them ba
    print("Acoustics: UART(5) echo-terminal active. "
    + " Currently listening for any data that comes in from the FT232RL")
    while 1:
        try:
            input = pAC.readline()
            if input:
                print("Acoustics: RX'd %r." % input)
                if (input == "locate pinger"):
                    # Recieve cmd from seawolf requesting location of pinger
                    val = oneclk.main('competition')
                    print(val)
                    pAC.write(str(val)+'\n')
                elif (input =="help"):
                    usage(pAC)
                else:
                    print("Acoustics: RX'd %r, an unrecognized cmd!!!" % input)
                    usage(pAC)

                
        except KeyboardInterrupt:
            print("Closing Port %s." % PORT_NAME)
            pAC.close()
            break
            

def usage(port):
    port.write("HELP TEXT~~~"
    + "The only possible cmd is <locate pinger> at the moment.\n")


if __name__ == '__main__':
    main()
