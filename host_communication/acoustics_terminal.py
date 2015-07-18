from os import path

# Get variables for navigating the file system.
root_directory = path.dirname(path.dirname(path.realpath(__file__)))
hc_directory = path.join(root_directory, "host_communication")
pf_directory = path.join(root_directory, "pinger_finder")

# Add important directories to path
import sys
sys.path.insert(0, hc_directory)
sys.path.insert(0, pf_directory)

import serial as s
import sys
import select
import uart  # enable_uart()
import oneclk
from acoustics import Acoustics
import time

# Flush stout so that system logging file can update with information
sys.stdout.flush()

# ######################
### Global Constants ###
#########################


def define_commlink():
    uart.enable_uart()
    print("Opening Port %s." % PORT_NAME)
    return s.Serial(PORT_NAME, 9600, timeout=1)


PORT_NAME = "/dev/ttyO5"
acoustics = Acoustics()  # Acoustics Control Object

# load global config settings
config = acoustics.pass_config_module()

pAC = define_commlink()  # Acoustics communication port
log = acoustics.logger

data_dict = ('')

# ######################
### Other definitions ##
#######################


def init_acoustics():
    acoustics.preset(101)


def send(msg):
    pAC.write(msg + '\n')


def read():
    input = pAC.readline()
    if input:
        if (input[-1] != '\n'):
            print("String is missing \\n terminator!")

        return input.rstrip('\n')

    return None


def usage(port):
    pass


def process_input(port):
    input = port.readline()
    if input:
        # Show input as a means of debugging output
        print("Acoustics: RX'd %r." % input)

        if (input == "locate pinger"):
            # Recieve cmd from seawolf requesting location of pinger
            val = oneclk.main('competition')
            if val == None:
                print("Unable to get data")
                pAC.write('None\n')
            else:
                print(val)
                pAC.write(str(val) + '\n')

        elif (input == "help"):
            usage(pAC)

        else:
            print("Acoustics: RX'd %r, an unrecognized cmd!!!" % input)
            usage(pAC)


def task_manager(input):
    # Other logic for input
    if (input == "get_data"):
        # Initialize
        data_dictionary = create_data_dictionary()

        # Get data
        acoustics.log_ready('srp')
        (data_dictionary['data']['heading'], epoch) = acoustics.get_last_measurement()

        #
        if data_dictionary['data']['heading'] == None:
            data_dictionary['data']['epoch'] = None
            data_dictionary['txt'] = 'have not located pinger yet'
            data_dictionary['error'] = 1
        else:
            data_dictionary['data']['epoch'] = time.time() - epoch

        # Convert response into string
        str_response = str(data_dictionary)
        print(str_response)
        pAC.write(str_response + '\n')

    elif "change_pinger_freq" in input:
        # Takes input in the form "change_pinger_freq,23e3"
        # parse user input for desired frequency
        (_, desired_freq) = input.split(',')
        desired_freq = float(desired_freq) # will throw up error if not float

        # write data to config file
        config.set('Acoustics', 'pinger_frequency', str(desired_freq))
        with open(root_directory+'/config.ini', 'wb') as configfile:
            config.write(configfile)

    elif "change_hydrophone_spacing" in input:
        # Takes input in the form "change_hydrophone_spacing,23.4e-2"
        # parse user input for desired frequency
        (_, desired_spacing) = input.split(',')
        desired_spacing = float(desired_spacing) # will throw up error if not float

        # write data to config file
        config.set('Acoustics', 'array_spacing', str(desired_spacing))
        with open(root_directory+'/config.ini', 'wb') as configfile:
            config.write(configfile)

    elif input == "locate pinger":

        # Get data
        acoustics.log_ready('srp')
        angle_to_pinger = acoustics.compute_pinger_direction()

        # Send data back to seawolf
        send(str(angle_to_pinger))

    elif input == "locate pinger2":

        # Get data
        acoustics.log_ready('srp')
        angle_to_pinger = acoustics.compute_pinger_direction2()

        # Send data back to seawolf
        send(str(angle_to_pinger))

    elif input == "hello":
        send("Hello to you too, Seawolf.")

    else:
        send("Unknown command! Please enter 'locate pinger' or 'hello'.")


def main_loop():
    # Settings
    viewer_active = config.getboolean('Terminal', 'viewer_active')
    if config.getboolean('Terminal', 'log_at_start'):
        log.tog_logging()
    
    # Start the timer
    cycle_start = time.time()

    while 1:
        sys.stdout.flush()
        int_signal = ''
        try:
            # Try reading and acting upon seawolf's input first
            input = read()
            #input = 'get_data'
            if input:
                # Process user input
                print("RX: {0}".format(input))
                task_manager(input)
            else:
                print("I got nothin.")

            # Run acoustics in the background
            acoustics.refresh_config()
            if (time.time() - cycle_start > config.getfloat('Terminal', 'sampling_interval')):
                # Perform sample capture
                acoustics.log_ready('s')
                acoustics.update_measurement()

                # Plots output for debugging purposes
                if viewer_active:
                    acoustics.plot_recent(fourier=True)

                # Restart the timer
                cycle_start = time.time()
            else:
                pass

            # Now see if someone is trying to do something on the backend
            if config.getboolean('Terminal', 'debugging'):
                while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                    int_signal = sys.stdin.readline().rstrip('\n')
            
            # Enter debug mode if backend user asks to
            if int_signal == 'g':
                print('')
                print("Acoustics debug mode activated.")
                print("Please enter one of the following commands:")
                list_of_cmds = ("l: log latest recorded data.\n"
                                + "g: Change gain of input filters.\n"
                                + "c: continue terminal program.\n"
                                + "p: Plot last sample collection.\n"
                                + "test_config: Load the acoustic test config\n"
                                + "tog_aut: Toggle autonomous condition mode\n"
                                + "tog_viewer: Toggle feature that plots captured signal to debugger on every cycle\n"
                                + "tog_log: Toggle logger activity\n"
                                + "q: Quit this app.\n")
                print(list_of_cmds)
                int_input = raw_input(">> ")

                # Log stuff
                if (int_input == 'l'):
                    log.logit(acoustics)

                # Increase gain
                elif (int_input == 'g'):
                    acoustics.filt.gain_mode()

                # plot what just happend
                elif (int_input == 'p'):
                    acoustics.plot_recent()

                # Continue
                elif (int_input == 'c'):
                    pass

                # Load the te
                elif (int_input == "test_config"):
                    acoustics.preset(101)

                elif (int_input == "tog_aut"):
                    acoustics.auto_update = not acoustics.auto_update

                elif (int_input == "tog_viewer"):
                    viewer_active = not viewer_active

                elif (int_input == "tog_log"):
                    log.tog_logging()

                # Quit prog
                elif (int_input == 'q'):
                    print("Closing Port %s." % PORT_NAME)
                    pAC.close()
                    acoustics.close()
                    break

                else:
                    pass

        # except IOError:
        #    pass

        except KeyboardInterrupt:
            print("Closing Port %s." % PORT_NAME)
            pAC.close()
            acoustics.close()
            break

# ######################
#### Data Dictionary ###
########################


def create_data_dictionary():
    data = {
        'heading': None,  # Hydrophone pair measurements
        'epoch': None,  # time since last measurement
    }

    base = {
        'data': data,
        'txt': '',
        'error': 0
    }

    return base


def main():
    # Initialize Components
    init_acoustics()

    # Listen for texts and process them
    print("Acoustics: UART(5) echo-terminal active. "
          + "Currently listening for any data that comes in from the FT232RL")

    # Run the main loop
    main_loop()

if __name__ == '__main__':
    main()
