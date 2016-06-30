#!/usr/bin/python
import sys
sys.path.append('../pinger_finder/')
import socket
import time
import struct

import serial

from bbb.ADC import ADS7865
from bbb.LTC1564 import LTC1564

class Net():
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.IP = '192.168.1.3'
        self.port = 22022

        self.conn = None
        self.addr = None

    def connect_to_client(self):

        self.sock.bind((self.IP, self.port))
        self.sock.listen(5)

        print("Waiting for client to connect...")
        (self.conn, self.addr) = self.sock.accept()
        print("client at %s connected!" % str(self.addr))
        time.sleep(1)

    def read_msg(self):
        print "Reading msg from client..."
        msg = self.conn.recv(1024)
        return msg

    def send(self, msg):
        """sends a message over the network"""
        self.conn.send(msg)

    def pack_and_send_np(self, data, n_ch):
        """receives a numpy vector, and sends it over IP
        according to the custom protocol"""

        # tell user how many channels to collect
        self.send(str(n_ch))

        # collect number of values, and inform the client
        n = data[0].shape[0]
        self.send(str(n))

        # pack the data
        for vector in data:
            self.conn.recv(2) # wait for enter
            pack_fmt = 'f'*n
            data_binary = struct.pack(pack_fmt,  *list(vector))

            # send the data
            self.send(data_binary)
            print("sent %d values of data using %d bytes" %(n, struct.calcsize(pack_fmt)))
        

class UART():
    def __init__(self):
        pass

def enter_program1(port):
    # setup components
    adc = ADS7865()
    filt = LTC1564()

    # config circuits
    adc.ez_config(5)
    adc.update_deadband_ms(0*0.5e3)    # dead time
    adc.set_sample_len(1e3)            # sample length
    adc.update_sample_rate(400e3)      # sample rate
    adc.update_threshold(0.04)          # trigger threshold
    filt.gain_mode(15)
    filt.filter_mode(14)
    

    while 1:
        # wait for command to get data
        msg = port.read_msg()

        if msg=='get data':
            #adc.get_data
            #strem
            print("Getting data")
            adc.get_data()
            port.pack_and_send_np(adc.y, len(adc.y))
            pass

        elif msg == '':
            print("disconnect detected. quiting stream.")
            break

        elif msg=='exit':
            break




def main():
    # basic parameters
    error_count = 0
    
    #TODO: throw in argparse for more usability

    port = Net()
    #TODO: port = UART() if no internet connection
    
    port.connect_to_client() # blocking

    # parse client messages
    while 1:
        # collect user input
        msg = port.read_msg()
        #print("client message: |%s|" % str(msg))

        if msg is None:
            error_count += 1
            print("nothing received")
            if error_count > 10:
                print("Exiting")
                break

        elif msg == 'stream':
            enter_program1(port)

        elif msg == '':
            print("Client disconnected!!!")
            print("Exiting.")
            break
        
        else:
            print("unhandled msg type!!!")
            print(type(msg), ":", str(msg), ":")
        
main()