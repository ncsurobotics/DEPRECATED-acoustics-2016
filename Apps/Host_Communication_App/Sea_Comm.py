import serial
from sys import argv
import platform
import uart_loader #enable_uart(), disable_uart()

DEVICE = "/dev/ttyUSB0"
TTY_BANG = "\n" # Terminal processing look for this command
		# in order to print data to screen.

def main():	
	uart_loader.enable_uart() # Enables uart w/ stty and config-pin cmds
   	ser = serial.Serial(DEVICE, 9600)
	while(1):
		cmd_send(ser)
		theta = cmd_read(ser)
		print("Sea_Comm: theta = %d" % eval(theta))

def cmd_send(ser_obj):
    user_input = raw_input('Test if works ---> ')
    ser_obj.write(user_input + TTY_BANG)

def cmd_read(ser_obj):
	x = ser_obj.readline()
	x = x.rstrip(TTY_BANG)
	return x

main()
