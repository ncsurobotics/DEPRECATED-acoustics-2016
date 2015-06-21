import sys
sys.path.insert(0, '../')

import serial as s
from time import sleep

# ###########################
##### Global Constants ######
#############################

# vvv Set to appropiate usb terminal
PORT_NAME = "/dev/ttyUSB0"

# Designate Port object
print("Opening Port %s." % PORT_NAME)
# pUSB = s.Serial(PORT_NAME, 9600, timeout=10)
# ^^^ Off because this is a fake program

HELP_TEXT = ("List of valid commands: acoustics,heading,1 ;acoustics,heading,2 ;" 
    + "acoustics,diversity ; help;")

# ###########################
##### Global Functions ######
#############################

def send(msg):
    # pUSB.write(msg + '\n')
    pass # do nothing since this is a fake program


def read(msg):
    input = fake_acoustics(msg)
    # input =  pUSB.readline()
    
    if input:
        if (input[-1] != '\n'):
            print("String is missing \\n terminator!")
        
        return input.rstrip('\n')
    
    return None
    

def main():

    # Listen for texts and echo them ba
    print("USB terminal active. Any data you enter will be sent "
    + "out over serial via the FT232RL.")
    
    while 1:
        try:
            input = raw_input('>> ')
            send(input)
            
            # Read the data back in
            result = read(input)
            if not (result):
                print("TIMEOUT!!!!")
            else:
                print("%s" % result)
                
        except KeyboardInterrupt:
            print("Closing Port %s." % PORT_NAME)
            # pUSB.close()
            # No real usb port used in this program
            break
            
# ###########################
##### Global Functions ######
#############################
def fake_acoustics(read_msg):
    # All of this is fake data.
    
    if read_msg == "acoustics,heading,1":
        sleep(10)
        send_msg = -31.30020304 # angle to pinger in degrees
    elif read_msg == "acoustics,heading,2":
        sleep(10)
        send_msg = 80.993202002 # angle to pinger in degrees
    elif read_msg == "acoustics,diversity":
        sleep(10)
        send_msg = 1 # Indication of which hydrophone pair has a stronger signal
    elif read_msg == "help":
        send_msg = HELP_TEXT
    else:
        send_msg = "'%s' is an invalid command" % read_msg
        
    return str(send_msg) + '\n'

if __name__ == '__main__':
    main()
