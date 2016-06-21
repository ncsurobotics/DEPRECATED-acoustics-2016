import sys
sys.path.append("../pinger_finder/")
import socket
import math
import argparse

import numpy as np

from environment import hydrophones
from bbb.ADC import ADS7865
from bbb.LTC1564 import LTC1564
import get_heading



WORLD_ORIGIN = np.array([[0,0,0]])

TCP_PORT = 22022
BUFFER_SIZE = 1024
C_SOUND = 1473

YAW = 0
PITCH = 1

class Port():
    def __init__(self):
        # IP address
        self.IP = '192.168.1.3'
        self.port = 22022
        self.buffer_size = 20

        # loop functions
        self.loop_function = None
        self.loop_fargs = None



    def set_loop_function(self,func,*args):
        self.loop_function = func
        self.loop_fargs = args

    def connect(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((TCP_IP, TCP_PORT))
        

    
    def stream(self,func=None, *args):
        s.listen(1)
        print("waiting for client to connect")
        (conn, addr) = s.accept() # this is a blocking call

        while 1:
            data = conn.recv(self.buffer_size)
            if not data: break

"""
outputs a heading in degrees. 
RETURN:
    0degrees represents straight ahead. 
    90degrees represent to the right. 
    -90degrees represents to the left.
"""
def ab2heading(a,b):
    rad2deg = 180/math.pi
    return 90 - math.atan2(b, a)*rad2deg

def setup_parser():
    parser = argparse.ArgumentParser(description="Stream heading data for testing purposes")

    parser.add_argument('-a', '--array', action='store', default=['yaw'],
                        nargs='+', dest='array_config',
                        choices=['yaw', 'pitch'],
                        help='specify the hydrophone array configuration. Defaults to just yaw.')

    parser.add_argument('--stream', action='store_true', default=False,
                        dest='stream_on', help='stream data over TCP connection')
                        

    return parser

def create_hydrophone_pair(spacing):
    array = hydrophones.Array()
    array.move(WORLD_ORIGIN)
    array.define( hydrophones.generate_yaw_array_definition( spacing ) )

    return array

def generate_array_settings(name, id, hydrophone_pair, preset, elem0_ChADC, elem1_ChADC):
    out = {}
    out['name'] = name
    out['id'] = id
    out['hydrophone_pair'] = hydrophone_pair
    out['heading'] = None
    out['ADC_config'] = preset
    out['elem2adc_mapping'] = [elem0_ChADC, elem1_ChADC]

    return out

def compute_heading(hydrophone_pair, adc, pattern):
    # capture theta for sub array
    tdoa_times = get_heading.compute_relative_delay_times(adc, 22e3, hydrophone_pair, c=C_SOUND,pattern=[(0,1)],elem2adc=pattern)
    doas = tdoa_times * C_SOUND
    hydrophone_pair.get_direction(doas)

    unpack = 0
    (a,b) = hydrophone_pair.ab[unpack]
    theta_center = ab2heading(a,b)

    return theta_center

def main():
    # parse arguments
    parser = setup_parser()
    args = parser.parse_args()

    array_config    = args.array_config
    stream_on       = args.stream_on

    # generate empty variables
    total_array = {}

    # create and define hydrophone array
    #if ('yaw' in array_config) and ('pitch' in array_config):
    if 'yaw' in array_config:
        yaw_array = create_hydrophone_pair(23.4e-3)
        total_array['yaw'] = generate_array_settings('yaw', 'ab', yaw_array, 1, 0, 1)

    if 'pitch' in array_config:
        pitch_array = create_hydrophone_pair(23.4e-3)
        total_array['pitch'] = generate_array_settings('pitch', 'cd', pitch_array, 0, 0, 1)

    # initialize acoustic circuits
    adc = ADS7865()
    filt = LTC1564()

    # configure acoustic filter circuits
    filt.gain_mode(15)
    filt.filter_mode(3)

    # configure acoustic ADC circuit
    if len(array_config) == 2:
        # set ADC to 2x2, dual sampling configuration
        adc.ez_config(5)

        # offset the pitch array to match the ADC's 2x2 configuration
        total_array['pitch']['elem2adc_mapping'] = [2,3]

    elif len(array_config) == 1:
        selected_pair = array_config[0]
        print('config= %d' % total_array[selected_pair]['ADC_config'])
        adc.ez_config( total_array[selected_pair]['ADC_config'] )

    # configure general part of the ADC circuit
    adc.update_deadband_ms(0*0.5e3)    # dead time
    adc.set_sample_len(1e3)            # sample length
    adc.update_sample_rate(300e3)      # sample rate
    adc.update_threshold(0.1)          # trigger threshold
    while 1:
        adc.get_data()
        
        for sub_array in total_array.values():
            print("--running %s" % sub_array['name'])
            pattern = sub_array['elem2adc_mapping']
            
            theta_center = compute_heading(sub_array['hydrophone_pair'], adc, pattern)
            
            sub_array['heading'] = theta_center

        # print values
        if len(array_config) == 2:
            print("--Pinger: yaw=%ddeg, pitch =%ddeg" % (total_array['yaw']['heading'], total_array['pitch']['heading']))


        elif len(array_config) == 1:
            selected_pair = array_config[0]
            print("--Pinger: %s=%ddeg" % (selected_pair, total_array[selected_pair]['heading']))

main()