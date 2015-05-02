from __future__ import print_function

import os
import sys


def batchLookupGPIO(pinList):
    """ Given a list of pin names, returns a list of pin numbers
    """

    # Generate list of len(pinList) None's
    GPIOList = [None for pin in pinList]

    lookupTable = {
        'P8_03': 38,
        'P8_04': 39,
        'P8_05': 34,
        'P8_06': 35,
        'P8_07': 66,
        'P8_08': 67,
        'P8_09': 69,
        'P8_10': 68,
        'P8_11': 45,
        'P8_12': 44,
        'P8_13': 23,
        'P8_14': 26,
        'P8_15': 47,
        'P8_16': 46,
        'P8_17': 27,
        'P8_18': 65,
        'P8_19': 22,
        'P8_20': 63,
        'P8_21': 62,
        'P8_22': 37,
        'P8_23': 36,
        'P8_24': 33,
        'P8_25': 32,
        'P8_26': 61,
        'P8_27': 86,
        'P8_28': 88,
        'P8_29': 87,
        'P8_30': 89,
        'P8_31': 10,
        'P8_32': 11,
        'P8_33': 9,
        'P8_34': 81,
        'P8_35': 8,
        'P8_36': 80,
        'P8_37': 78,
        'P8_38': 79,
        'P8_39': 76,
        'P8_40': 77,
        'P8_41': 74,
        'P8_42': 75,
        'P8_43': 72,
        'P8_44': 73,
        'P8_45': 70,
        'P8_46': 71,

        'P9_11': 30,
        'P9_12': 60,
        'P9_13': 31,
        'P9_14': 50,
        'P9_15': 48,
        'P9_16': 51,
        'P9_17': 5,
        'P9_18': 4,
        'P9_19': 13,
        'P9_20': 12,
        'P9_21': 3,
        'P9_22': 2,
        'P9_23': 49,
        'P9_24': 15,
        'P9_25': 117,
        'P9_26': 14,
        'P9_27': 115,
        'P9_28': 113,
        'P9_29': 111,
        'P9_30': 112,
        'P9_31': 110,
        #'P9_41': 41???
        #'P9_42': ????
    }

    try:
        for i, pin in enumerate(pinList):
            GPIOList[i] = lookupTable[pin]

    except KeyError:
        print("BBBIO: Uh oh. pin '{pin}\' does not exist in the BBBIO.py\'s database. Check your spelling or update the lookup table.".format(pin=pin))
        sys.exit(1)

    return GPIOList


class GPIO:

    """ Each instance of GPIO represents a pin on the beaglebone.
    The pin which it represents is given as an input argument when
    the object is first instantiated
    """

    def __init__(self, gpio_pin):
        """ Establishes all of the components neccessary in order to treat a
        single pin as an object with configurable settings.

        Args:
            gpio_pin: An integer corresponding with the
                GPIO pin ID, which will range from 0 to +117.
        """

        self.gpio_pin = gpio_pin
        self.gpio_base = "/sys/class/gpio/"
        self.gpio_path = "/sys/class/gpio/gpio%d/" % gpio_pin

        # generate the sysFS string
        os.system("echo %d > %sexport" % (gpio_pin, self.gpio_base))
        with open(self.gpio_path + "direction") as f:
            self.direction = f.read().rstrip("\n")

        # update known value of pin
        self.read()

    def reInit(self):
        """
        """
        self.__init__(self.gpio_pin)

    def setDirection(self, targetState):
        """ Sets a pin as an output or an input, also updates
        (str)self.direction

        Args:
            targetState: A string dictating the state the user wants for the
                pin, either 'out' or 'in'
        """

        if (targetState == "out") or (targetState == "in"):
            os.system("echo %s > %sdirection" % (targetState, self.gpio_path))
            with open(self.gpio_path + "direction") as f:
                self.direction = f.read().rstrip("\n")
        else:
            print("pin{pin}: {state} is not a valid direction".format(pin=self.gpio_pin, state=targetState))

    def write(self, value):
        """ Outputs "value" on the pin, also updates (int)self.value

        NOTE: This method will only work if the pin is configured as an
        output before hand, done using the setDirection method.

        Args:
            value: Integer 0 or 1
        """

        if self.direction == "out":
            os.system("echo %d > %svalue" % (value, self.gpio_path))
            self.value = value
        else:
            print("pin{pin} is not an output. You cannot set it's value.".format(pin=self.gpio_pin))

    def read(self):
        """ Returns the state of an input/output, either a 0 or 1
        Also updates (str)self.value
        """

        # read op involve uneccessary \n char. Must take
        # extra step to remove it.
        with open(self.gpio_path + "value") as f:
            self.value = int(f.read().rstrip("\n"))

        return self.value

    def help(self):
        """ Prints all the methods and attributes which the caller will have
        access to. Useful when writing new code or debugging a program
        using this class
        """

        print("You can call the following attributes: ")
        for item in self.__dict__.keys():
            print("  *.{}".format(item))

        print()
        print("You also have access to the following methods: ")
        for item in [method for method in dir(self) if callable(getattr(self, method))]:
            print("  *.{}()".format(item))
        print()

    def close(self):
        """ Deactivates a pin by ensuresing that the pin is an input
        and unexporting the GPIO ID from sysFS.  Pin can be reactivated
        with reInit() method
        """

        self.setDirection("in")
        os.system("echo %d >%sunexport" % (self.gpio_pin, self.gpio_base))


class Port():

    """ Each instance of Port represents a group of pins on the beaglebone.
    This group of pins is actually a group of GPIO instances. The Caller
    may specify this group during instantiation, or afterwards with the
    (self).createPort(...) method.
    """

    def __init__(self, assignment=None):
        """
        Args:
            assignment (optional): in case the caller would like to define the port during
        instantiation. See: the pinNameList argument of the createPort() method
        """

        self.en = True
        self.pins = []
        self.direction = []
        self.portDirection = ''
        self.value = []
        self.nValue = 0
        self.length = 0
        if assignment:
            self.createPort(assignment)

    def createPort(self, pinNameList):
        """ Assigns a port, which is just a group of pins.

        Args:
            pinNameList: Represents a list of strings specifying BBB pins from
                the end user's POV. The format of this specification is "Px_y",
                whereas x is the header number on the BBB, y is the pin number
                on that particular header (including leading zeros). Thus,
                strings such as "P8_01", "P8_46", "P9_02" are valid.

                pinNameList[0] must represent the LSB,
                pinNameList[-1] must represent the MSB
        """

        # If user supplies a string (which is convenient if he
        # only wants to allocate one pin), then convert that string
        # to a list with one element because that's the type that
        # works with self.batchLookupGPIO(...)
        if isinstance(pinNameList, basestring):
            pinNameList = [pinNameList]

        GPIOList = batchLookupGPIO(pinNameList)
        for pin in GPIOList:
            # print(pinNameList) ; print(GPIOList)

            obj_pin = GPIO(pin)
            self.pins.append(obj_pin)  # self.pins
            (self.direction).append(obj_pin.direction)  # self.direction
            (self.value).append(obj_pin.value)  # self.value

        self.length = len(self.pins)  # self.length

    def readStr(self):
        """ Reads values of all pins that make up a port (self) and returns a
        binary string with the MSB on the left and the LSB on the right
        """

        s = ""
        i = 0
        for pin in self.pins:
            a = pin.read()
            s = str(a) + s
            self.value[i] = a
        return s

    def writeToPort(self, value):
        """ Takes the integer 'value' and converts it to a
        string formated in binary representation, which is parsed in
        the for loop in order to configure each pin on the port.
        """

        portLength = len(self.pins)
        binaryVal = ('{0:0' + str(portLength) + 'b}').format(value)  # generate binary string from value arg

        for i in range(portLength):
            s_i = (portLength - 1) - i
            b = int(binaryVal[s_i])
            self.pins[i].write(b)

    def setPortDir(self, direction):
        """ Sets all pins on a port to a direction and updates
        self.portDirection and self.direction accordingly.

        Args:
            direction: String "in" or "out", to update
        """

        i = 0
        for pin in self.pins:
            pin.setDirection(direction)
            self.direction[i] = pin.direction
            i += 1

        self.portDirection = direction

    def close(self):
        """ Closes every pin on a port. See: close() method on GPIO
        """

        for pin in self.pins:
            pin.close()

    def help(self):
        """ Prints a list of all available attributes and methods
        """

        print("You can call the following attributes: ")
        for item in self.__dict__.keys():
            print("  *.{}".format(item))

        print()
        print("You also have access to the following methods: ")
        for item in [method for method in dir(self) if callable(getattr(self, method))]:
            print("  *.{}()".format(item))
        print()
