#!/usr/bin/python

import socket

class Net():
    def __init__(self):
        self.IP = '152.1.150.32'
        self.port = 22022
        self.buffer_size = 1024
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect_to_acoustics(self):
        self.sock.connect((self.IP, self.port))

    def send(self, msg):
        self.sock.send(msg)
        
        

def main():
    port = Net()

    port.connect_to_acoustics()
    port.send('hello')

main()