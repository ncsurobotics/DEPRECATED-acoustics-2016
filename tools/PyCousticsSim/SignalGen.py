import numpy as np


class SG:
    """
    """

    def __init__(self, end=1e-3):
        self.tstart = 0
        self.tend = end

    def Sin(self, f, t):
        """ Delivers a sinusoidal pulse of set length based on a starting time
        and an end time.
        """
        # Initialize constants
        pi = np.pi
        w = 2 * pi * f

        # Initialize base array [0,0,0...1,1,1...0,0,0]
        base = np.ones(t.size)
        for i in range(t.size):
            if t[i] < self.tstart:
                base[i] = 0
            elif t[i] > self.tend:
                base[i] = 0
            else:
                pass

        # Create pulse by masking sinusoid with base array.
        y = np.sin(w * t - pi) * base

        return y
