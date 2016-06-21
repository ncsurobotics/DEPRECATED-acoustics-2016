from .port import Port

CS_PIN = ''
F_PINS = ['P9_18', 'P9_17', 'P9_16', 'P9_15'] # [lsb,...,msb]
G_PINS = ['P9_14','P9_13','P9_12','P9_11'] # [lsb,...,msb]

DEFAULT_F = 0
DEFAULT_G = 0
DEFAULT_CS = 1


class LTC1564():

    """
    """

    def __init__(self):
        # Init all pins
        if F_PINS:
            self.F = Port(F_PINS)
            self.F.set_port_dir('out')
            self.F.write_to_port(DEFAULT_F)

        self.G = Port(G_PINS)
        self.G.set_port_dir('out')
        self.G.write_to_port(DEFAULT_G)

        if CS_PIN:
            self._CS = Port(CS_PIN)
            self._CS.set_port_dir('out')
            self._CS.write_to_port(DEFAULT_CS)

        # Init metadata
        if F_PINS:
            self.Fval = DEFAULT_F

        self.Gval = DEFAULT_G

        # Metadata attributes

    def gain_mode(self, mode=None):
        """ Configures gain of the input stage.

            Args:
                mode: int
        """

        n = self.get_n_gain_states()
        if (mode is None):
            print("LTC1564: Give me a value from 0 to %d for gain mode" % (n - 1))
            mode = int(str(raw_input(">> ")))

        if 0 <= mode <= n - 1:  # n-1 is the max bit value that can be used
            print("LTC1564: Writing %d to gain stage." % mode)

            # Assert _CS if applicable
            if CS_PIN:
                self._CS.write_to_port(0)

            # Bitbang Gain value
            self.G.write_to_port(mode)

            # Deassert _CS if applicable
            if CS_PIN:
                self._CS.write_to_port(1)

            # Save change to user accessible attribute
            self.Gval = mode
        else:
            print("LTC1564: mode %s is outside the range of possible gain states" % mode)

    def get_n_gain_states(self):
        """gets the maximum number of value possible "Gain" given the
        number of pins that are allocated for it. For instance, allocating
        4 pins to control Gain gives us 16 possible gain states (from 0 to 15)
        """
        return 2 ** self.G.length

    def filter_mode(self, mode):
        """ Configures Fc of the input stage

            Args:
                mode: int
        """

        if 0 <= mode <= 15:
            print("LTC1564: Writing %d to filt stage." % mode)

            if CS_PIN:
                self._CS.write_to_port(0)

            self.F.write_to_port(mode)

            if CS_PIN:
                self._CS.write_to_port(1)

            self.Fval = mode
        else:
            print("LTC1564: mode %s is outside the range of possible filt states" % mode)

    def terminate(self):
        """ Terminates control of the LTC1564.

        WARNING: Careless use of this cmd is rather discouraged unless
        user wishes to physically move control of the LTC1564 to
        a new set of BBB pins... reason being that although this
        method will turn the BBB pins to inputs, the level shifting
        circuit will always act as an output. It makes some sense to
        just remove the level shifters pins from the board whenever this
        subsystem is not in use
        """

        # unexport pins
        self.F.close()
        self.G.close()
        self._CS.close()
