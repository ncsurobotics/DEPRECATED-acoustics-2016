

import serial
import export
from time import sleep

def AckRoutine(ser):
	print('Link established with AVR device.')
	ser.write(bytes('A','UTF-8'))
	
def MainDataProgram(ser, MODE):
	# Due to the previous 'W' command, python is expecting a packet containing
	# info about how many bytes to collect.
	
	nBytes = ser.read()[0] # This byte determines the number of working data points
	data = CollectData(ser, nBytes)
	
	if MODE == 'export':
		ExportData(data)
		print("ALL DONE!!!!")
		exit(0)
	elif MODE == 'monitor':
		print(data)

def CSVExporter(data):
	export.RunCSVExport(data)
	print(data)

def CollectData(ser, nBytes):
	ser.write(bytes('W','UTF-8'))
	data = list(ser.read(nBytes))
	return data

def ExportData(data):
	print("This is the data I collected:")
	CSVExporter(data)
	


def main():
	# Settings
	DEVICE = "/dev/tty.usbserial-A5025L80"
	MODE = 'monitor'
	
	# Main program
	ser = serial.Serial(DEVICE, 9600)
	print('')
	
	while True:
		byte = ser.read() #Read byte 1
		
		if byte.decode()=='A':
			AckRoutine(ser)
			
		elif byte.decode()=='W':
			MainDataProgram(ser, MODE);
			
		else:
			print(byte)
					
	print("Whoops! You exited the loop somehow...")
			
	
	

main()