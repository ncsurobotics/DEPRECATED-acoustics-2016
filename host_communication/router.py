import getAngle
import os
import serial

ser = serial.Serial('/dev/ttyO4', 9600, timeout=60)
TTY_BANG = '\n'


def main():
    x = read_input(ser)

    if (x == "getAngle.py"):
        theta = getAngle.main()
        print("Acoustics: The pinger is %d degrees left" % theta)
        write_output(ser, str(theta))

    else:
        print("What!? I don't understand")


def read_input(ser_obj):
    x = ser_obj.readline()
    x = x.rstrip(TTY_BANG)
    return x


def write_output(ser_obj, outp_string):
    ser_obj.write(outp_string + TTY_BANG)

if __name__ == '__main__':
    main()
