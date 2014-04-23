#!/usr/bin/python
import sys
sys.path.append('../pinger_finder/')
import socket
import time

import serial

from bbb.ADC import ADS7865
from bbb.LTC1564 import LTC1564

class Net():
    def __init__(self):
        self.sock = socket.socket()
        self.IP = '192.168.1.3'
        self.port = 22022

        self.conn = None
        self.addr = None

    def connect_to_client(self):
        self.sock.bind((self.IP, self.port))
        self.sock.listen(5)

        print("listine")
        (self.conn, self.addr) = self.sock.accept()
        print("listine")
        time.sleep(5)

    def read_msg(self):
        return None
        

class UART():
    def __init__(self):
        pass

def enter_program1(port):
    # setup components
    adc = ADS7865()
    filt = LTC1564()

    # config circuits
    #TODO

    while 1:
        # wait for command to get data
        msg = port.read_msg(timeout = 1)

        if msg=='get data':
            #adc.get_data
            #strem
            pass
        elif msg == None:
            print("got nothing")
        elif msg=='exit':
            break




def main():
    #TODO: throw in argparse for more usability

    port = Net()
    #TODO: port = UART() if no internet connection
    
    port.connect_to_client() # blocking

    # parse client messages
    while 1:
        # collect user input
        msg = port.read_msg()
        print(msg)

        if msg == None:
            print("Exiting")
            break

        elif msg == 'stream':
            enter_program1(port)
        
main()