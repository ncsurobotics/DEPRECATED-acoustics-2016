import sys
sys.path.insert(0, '../host_communication')

import serial as s
import uart         #

DEV_AC = "/dev/ttyUSB0"
DEV_SW = "/dev/ttyO5"
AC = "acoustics"
SW = "seawolf"


def init():
    uart.enable_uart()


def main():
    # Ask user to setup for test
    print("Please do the following:\n"
          + " 1. Using the modified USB cable, connect FT232RL to the USB port on the Beaglebone.\n"
          + " 2. Connect BBB 5V power to the FT232RL board (modified USB cable has power pins removed).\n"
          + " 3. Connect FT232RL(RX,TX) to BBB_UART5(TX,RX), respectively.\n")

    raw_input("Press ENTER when you're ready to begin the test: ")

    # Initialize ports
    init()
    pAC = s.Serial(DEV_AC, 9600, timeout=0.1)
    pSW = s.Serial(DEV_SW, 9600, timeout=0.1)

    # Send and read hello in one direction
    test_word1 = "Hello Acoustics\n"
    pSW.write(test_word1)
    print('\n' + SW + " TX'd %r" % (test_word1))

    response1 = pAC.readline()
    print(AC + " RX'd %r" % (response1))

    if test_word1 == response1:
        print("Success! The USB---->Acoustics link works!")
    else:
        print("Failure. USB--x-->Acoustics!")

    # Send and read hello in the other direction
    test_word2 = "Hello Seawolf\n"
    pAC.write(test_word2)
    print('\n' + AC + " TX'd %r" % (test_word2))

    response2 = pSW.readline()
    print(SW + " RX'd %r" % (response2))

    if test_word2 == response2:
        print("Success! The Acoustics---->USB link works!")
    else:
        print("Failure. Acoustics--x-->USB!")


if __name__ == '__main__':
    main()
