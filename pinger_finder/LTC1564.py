import BBBIO

CS_PIN = 'P9_11'
F_PINS = 'P9_12'
G_PINS = ['P9_13', 'P9_14']

DEFAULT_F = 0
DEFAULT_G = 0
DEFAULT_CS = 1


class LTC1564():

    """
    """

    def __init__(self):
        # Init all pins
        self.F = BBBIO.Port(F_PINS)
        self.F.setPortDir('out')
        self.F.writeToPort(DEFAULT_F)

        self.G = BBBIO.Port(G_PINS)
        self.G.setPortDir('out')
        self.G.writeToPort(DEFAULT_G)

        self._CS = BBBIO.Port(CS_PIN)
        self._CS.setPortDir('out')
        self._CS.writeToPort(DEFAULT_CS)

        # Init parameter
        self.Fval = DEFAULT_F
        self.Gval = DEFAULT_G

    def GainMode(self, mode):
        """ Configures gain of the input stage.

            Args:
                mode: int
        """

        if 0 <= mode <= 3:
            print("LTC1564: Writing %d to gain stage." % mode)

            self._CS.writeToPort(0)
            self.G.writeToPort(mode)
            self._CS.writeToPort(1)

            self.Gval = mode

        else:
            print("LTC1564: mode %s is outside the range of possible gain states" % mode)

    def FiltMode(self, mode):
        """ Configures Fc of the input stage

            Args:
                mode: int
        """

        if 0 <= mode <= 1:
            print("LTC1564: Writing %d to filt stage." % mode)

            self._CS.writeToPort(0)
            self.F.writeToPort(mode)
            self._CS.writeToPort(1)

            self.Fval = mode
        else:
            print("LTC1564: mode %s is outside the range of possible filt states" % mode)

    def Terminate(self):
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
