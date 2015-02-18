import serial
from sys import argv
import platform

def cmd_send():
    device = "/dev/ttyUSB0"
    ser = serial.Serial(device, 9600)
    user_input = raw_input('Test if works ---> ')
    ser=serial.Serial(device,9600)
    ser.write(user_input)


cmd_send()

