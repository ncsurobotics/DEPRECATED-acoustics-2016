import numpy as np


class BiHydrophoneArray:

    def __init__(self):
        self.d = None  # meters
        self.origin = None
        self.src_loc = None
        self.signalDict = None
        self.mediumModel = None
        self.maxSpread = None
        self.n_elements = 2

    def BuildArray(self):
        # Initialize placeholders
        coor_system = 2
        n = self.n_elements
        self.Hyd_loc = [0] * n  # meters

        if coor_system == 2:
            for i in range(n):
                sign = (-1)**(i + 1)
                self.Hyd_loc[i] = self.origin + np.array([sign * self.d / 2, 0])
        elif coor_system == 3:
            for i in range(n):
                sign = (-1) ^ (i + 1)
                self.Hyd_loc[i] = self.origin + np.array([sign * self.d / 2, 0, 0])
        else:
            print("BuildArray: Something went wrong")
            exit(1)

    def Capture(self, x, t, channelModel):
        # Initialize placeholders
        coor_system = 2
        n = self.n_elements
        dist = [0] * n  # meters
        DM = [0] * n  # samples
        y = [0] * n
        for i in range(n):
            y[i] = np.zeros(t.size)  # [placeholder]

        # Initialize constants
        dt = t[1] - t[0]  # sec

        # Compute distance of pinger to hydrophone
        for i in range(n):
            dist[i] = np.linalg.norm(self.Hyd_loc[i] - self.src_loc)

        # Compute TDOA just for diagnostic purposes
        timeDiff = (dist[0] - dist[1]) / self.mediumModel.c
        if timeDiff > self.maxSpread:
            print("Rx: Warning! Fold-over has occured!")

        # Check is resolution of TDOA is too smal... for diagnostic purposes
        dm = int(timeDiff / dt)
        if dm < 100:
            print("Rx: Warning! dm = %d, which is a bit small (<100). Maybe try increasing dt in the host program."
                  % dm)

        # Check is delay is too long
        if (4 * dist[0] / self.mediumModel.c > t[-1] - t[0]) or (4 * dist[1] / self.mediumModel.c > t[-1] - t[0]):
            print("Rx: Warning! Delay may be too large and may clip time. please increase time span or reduce delay.")

        for el in range(n):
            # compute data for hydrophone 0
            DM[el] = int(dist[el] / self.mediumModel.c / dt)
            for i in range(DM[el], t.size):
                m = t.size - i
                y[el][m] = x[m - DM[el]]

        return y
