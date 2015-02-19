import serial
from sys import argv
import platform
import uart_loader #enable_uart(), disable_uart()

DEVICE = "/dev/ttyUSB0"
TTY_BANG = "\n" # Terminal processing look for this command
		# in order to print data to screen.

def cmd_send():
    ser = serial.Serial(DEVICE, 9600)
    user_input = raw_input('Test if works ---> ')
    ser.write(user_input + TTY_BANG)

def main():
	
	uart_loader.enable_uart()
	while(1):
		cmd_send()

main()
