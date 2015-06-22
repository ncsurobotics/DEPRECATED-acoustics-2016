import serial as s
from time import sleep

PORT_NAME = "/dev/ttyUSB0"

# ######################################
##### Simulated Serial Comm ############
########################################

def fake_acoustics(read_msg):
    # All of this is fake data.
    
    if read_msg == "get_data":
        sleep(10)
        data = {
            'heading': {'ra': 20.000232, 'rb': 2.0444, 'ab':-20.022204}, # Hydrophone pair measurements
            'epoch': 2.3, # time since last measurement
        }
        
        send_msg = {
            'data': data,
            'txt': '',
            'error': 0
        }

    else:
        data = {
            'heading': {'ra': None, 'rb': None, 'ab':None}, # Hydrophone pair measurements
            'epoch': None, # time since last measurement
        }
        
        send_msg = {
            'data': data,
            'txt': "'%s' is an invalid command" % read_msg,
            'error': 1
        }
        
    return send_msg
    
def fake_send(msg):
    # pUSB.write(msg + '\n')
    pass # do nothing since this is a fake program
    
def fake_read(msg):
    raw_msg = fake_acoustics(msg)
    # input =  pUSB.readline()
    
    # ----
    # stuff to parse the input
    processed_msg = raw_msg
    # ----
    
    return processed_msg
    
# ###########################
##### Acoustics  ############
#############################

class Acoustics:
    def __init__(self):
        # Designate Port object
        print("Opening Port %s." % PORT_NAME)
        # pUSB = s.Serial(PORT_NAME, 9600, timeout=10)
        # ^^^ Off because this is a fake program
        
        # Listen for texts and echo them ba
        print("USB terminal active. Any data you enter will be sent "
        + "out over serial via the FT232RL.")
        
    def get_data(self):
        input = 'get_data'
        fake_send(input)
        
        # Read the data back in
        result = fake_read(input)
        if not (result):
            print("TIMEOUT!!!!")
    
        return result
        
    def close(self):
        print("Closing Port %s." % PORT_NAME)
        # pUSB.close()
        # No real usb port used in this program