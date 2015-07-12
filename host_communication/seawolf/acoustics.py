import sys
import os
import serial
from ConfigParser import SafeConfigParser
import glob

PORT_BASE = "/dev/ttyUSB"

# ###########################
# Global Settings ###########
#############################
# Load parser
config = SafeConfigParser()
config.read('./sw_config.ini')

def list_ports():
    # Detect if running on a supported platform
    if sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        ports = glob.glob('/dev/tty[A-Za-z]*')
    else:
        raise EnvironmentError('Unsupported platform')
        
    # Search for USB like ports
    result = []
    for port in ports:
        if 'USB' in port:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
    
    # Return a list of all acceptable ports that were found.
    return result


# ###########################
#### Main Class #############
#############################
class Acoustics:
    def __init__(self):
        # Show human user list of possible acoustics ports
        print('Active ports potentially connected to acoustics:')
        print( '\n'.join(list_ports()) )
        
        # Query user to pick the right port
        print("\nPlease identify which usb port is the correct one for acoustics")
        port_num = raw_input('  >> '+PORT_BASE)
        
        # Parse user query
        port_name = PORT_BASE+port_num
        
        # Open the specified port
        print("Opening Port %s." % port_name)
        self.s_port = serial.Serial(port_name, 9600, timeout=10)
        
        # Listen for texts and echo them ba
        print("USB terminal active. Any data you enter will be sent "
        + "out over serial via the FT232RL.")
        
    def send(self, msg):
        self.s_port.write(msg + '\n')
        
    def read(self):
        # Read the raw data
        input =  self.s_port.readline()
        
        if input:
            # Catch exception when user (BBB) forgets to append newline to msg
            if (input[-1] != '\n'):
                print("String is missing \\n terminator!")
        
            # return successfully with msg
            return input.rstrip('\n')
    
        # readline function timed out. No msg to read. return
        # None in response
        return None
        
    def get_data(self):
        self.send('get_data')
        data = self.read()
        return data
        
def test():
    # Clear the screen
    os.system('clear')
    
    print("BEGGINING ACOUSTICS TEST")
    acoustics = Acoustics()
    data = acoustics.get_data()
    print data
    print("ENDING ACOUSTICS TEST")
    