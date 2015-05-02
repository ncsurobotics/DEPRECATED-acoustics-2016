from __future__ import print_function

import os
import sys

LOOKUP_TABLE = {
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


def batch_lookup(pin_list):
    """ Given a list of pin names, returns a list of pin numbers
    """
    # Generate list of len(pinList) None's
    GPIOList = [None for pin in pin_list]

    try:
        for i, pin in enumerate(pin_list):
            GPIOList[i] = LOOKUP_TABLE[pin]

    except KeyError:
        print("BBBIO: Uh oh. pin '{pin}\' does not exist in the BBBIO.py\'s database. Check your spelling or update the lookup table.".format(pin=pin))
        sys.exit(1)

    return GPIOList


class GPIO():

    """ Represents a pin on the beaglebone, which is given as an argument at instantiation
    """

    def __init__(self, gpio_pin):
        """ Establishes all of the components neccessary in order to treat a
        single pin as an object with configurable settings.

        Args:
            gpio_pin: An integer corresponding with the
                GPIO pin ID, which will range from 0 to +117
        """

        self.gpio_pin = gpio_pin
        self.gpio_base = "/sys/class/gpio/"
        self.gpio_path = "/sys/class/gpio/gpio%d/" % gpio_pin

        # generate the sysFS string
        os.system("echo %d > %sexport" % (gpio_pin, self.gpio_base))

        with open(os.path.join(self.gpio_path, "direction")) as f:
            self.direction = f.read().rstrip("\n")

        # update known value of pin
        self.read()

    def reInit(self):
        """
        """
        self.__init__(self.gpio_pin)

    def set_direction(self, targetState):
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
        """ Outputs [value] on the pin and updates (int)self.value

        NOTE: This method will only work if the pin is configured as an
        output before hand, done using the set_direction method.

        Args:
            value: Integer 0 or 1
        """

        if self.direction == "out":
            os.system("echo %d > %svalue" % (value, self.gpio_path))
            self.value = value
        else:
            print("pin{pin} is not an output. You cannot set it's value.".format(pin=self.gpio_pin))

    def read(self):
        """ Returns the state of an input/output (integer 0 or 1)
        and updates (str)self.value
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
        """ Deactivates a pin by ensuring that the pin is an input
        and unexporting the GPIO ID from sysFS.  Pin can be reactivated
        with reInit() method
        """

        self.set_direction("in")
        os.system("echo %d >%sunexport" % (self.gpio_pin, self.gpio_base))
