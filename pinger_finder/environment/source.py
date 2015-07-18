import numpy as np
from tools3d import Phys_Obj


class Pinger(Phys_Obj):

    def __init__(self):
        super(Pinger, self).__init__()


class Pinger_Contour(Phys_Obj):

    def __init__(self):
        super(Pinger_Contour, self).__init__()

        # Initialize locations
        self.X = None
        self.Y = None
        self.Z = None

        self.max_distance = 50  # meters
        self.pts = 20  # data point

    def coe_generate_contour(self, ab, array_pair_idx, array):
        """takes the hydrophone_location data from "array" at idx "array_pair_idx",
        and the ab coefficient data corresponding to that pair, and generates matrix
        of data points drawing the hyperbolic contour of possible hydrophone locations.
        This function also takes care of aligning/orienting the contour data to the
        orientation of the hydrophone pair (using data contained in the array object).
        """
        a = ab[0]
        b = ab[1]

        # Generate Y and Z meshgrid
        lim = self.max_distance
        Y = np.linspace(-lim, lim, self.pts)
        Z = Y
        Y, Z = np.meshgrid(Y, Z)

        # Generate X
        temp = a
        a = abs(a)
        X = np.sqrt((2 * a + (Z / b)**2 + (Y / b)**2)) * a

        # get "a" back
        a = temp

        # Save values to internal attributes
        if a < 0:
            self.X = -X
        else:
            self.X = X
        self.Y = Y
        self.Z = Z

        # Final step is to orient the contour to the hydrophone pair
        self.match_contour_to_pair(array_pair_idx, array)

    def match_contour_to_pair(self, array_pair_idx, array):
        # vector param
        j = 1
        idx = array_pair_idx

        # Rotate accordingly
        self.xform_rotate(np.array([[0, array.pair_y_rot[idx], 0]]))

        # Move accordingly
        self.xform_translate(array.COM[idx])
