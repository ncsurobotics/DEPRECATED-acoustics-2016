import serial
from sys import argv
import platform

print('-' * 50)
print("Acoustics Client Communication App")

# Connect to the UART-to-USB device
if "bone" in platform.platform():
    device = "/dev/ttyUSB0"
    ser = serial.Serial("/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A5025L80-if00-port0", 9600)
else:
    print("Com_App: I'm not sure what" +
          " the device is called on " +
          "your system, so I'm assuming " +
          "/dev/tty.usbserial-A5025L80")
    device = "/dev/tty.usbserial-A5025L80"


ser = serial.Serial(device, 9600)


def cmd_listen():
    print("listening...")

    while True:
        print repr(ser.readline()[0:-2])


def cmd_unit_test():
    cmd_echo('string')
    cmd_burst(30)
    cmd_burst()
    cmd_seekAndBurst(30)
    cmd_seekAndBurst()
    cmd_configure('burst_size')
    cmd_readDataBlock()


def main():
    # Initialize connection

    cmd_listen()
    exit(1)

    # Check if successful
    cmd_helloBBB()
    response = ser.readline()
    if "hello" in response:
        print(response)
    else:
        print("main: Hmmm. I didn't get any response from the" +
              " beaglebone... Check your connections.")
        exit(1)

    # Connection successful. Now going to run through a list of things
    #  the BBB should be able to handle.
    cmd_unit_test()

#########################################
########  System Call Handline   ########
########################################

# Set up the program, or grant user help if he needs it.
argc = len(argv)
if argc == 2:
    if 'h' in argv[1]:
        print("--insert helpful text here--")
        exit(1)

if __name__ == '__main__':
    main()
