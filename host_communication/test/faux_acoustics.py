import serial as s
from time import sleep

PORT_NAME = "/dev/ttyUSB0"

N_ELEMENTS = 2
N_ARRAYS = 1

# ######################################
##### Simulated Serial Comm ############
########################################

def fake_acoustics(read_msg):
    # All of this is fake data.
    
    if read_msg == "get_data":
        sleep(10)
        
        # Fill in the common data format
        data = {
            'heading': None, # Hydrophone pair measurements
            'epoch': None, # time since last measurement
        }
        
        # Determine heading format based on element count
        if N_ELEMENTS == 2:
            data['heading'] = {'ab':-85.004555101}
            # ^^ Hydrophone pair measurements
          
        elif N_ELEMENTS == 3:
            data['heading'] = {'ra': 20.000232, 'rb': 2.0444, 'ab':-20.022204}
            # ^^ Hydrophone pair measurements
            
        elif N_ELEMENTS == 4:
            if N_ARRAYS == 1:
                data['heading'] = {'ab':74.53490170540681, 'ac'-35.489026400235716:, 'ad':79.24839863340534, 
                    'bc':4.161718729022823, 'bd':83.14890670723108,
                    'cd':17.885814599402877,
                }
                # ^^ Hydrophone pair measurements
                
            elif N_ARRAYS == 2:
                data['heading'] = [{'ab':-20.022204}, {'ab': 80.0043}]
                # ^^ Hydrophone pair measurements
                
                
        # Fill in common parts of the data dictionary
        data['epoch'] = 2.3, # time since last measurement
        
        # Complete the overall dictionary
        send_msg = {
            'data': data,
            'txt': '',
            'error': 0
        }

    else:
        pass
        
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