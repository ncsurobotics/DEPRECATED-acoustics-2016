import numpy as np
import itertools
import source

from tools3d import Phys_Obj

K_HAT = np.array([[0, 0, 1]])
DIM1 = 0


class Array(Phys_Obj):

    def __init__(self):
        super(Array, self).__init__()

        # Define hydrophones
        self.hydrophones = Phys_Obj()

        # Define Pinger_Contours
        self.pinger_contours = []

        # Define unknown variables
        self.last_known_pinger_location = None
        self.last_known_pinger_direction = None

    def define(self, locations):
        """Specify the hydrophone configuration by passing an Nx3 numpy
        array, where each row is an XYZ coordinate representing a coordinate
        location of a hydrophone with respect to the array origin.
        """
        self.hydrophones.set_XYZ(XYZ=locations)

        # Generate immediate parameters
        self.n_elements = locations.shape[0]

        # Make a list of all relative hydrophone locations
        self.element_pos = locations

        # Enumerate all pair combinations
        self.pairs = [
            ID for ID in itertools.combinations(range(self.n_elements), 2)
        ]

        # compute pair properties
        self.d = []
        self.COM = []
        self.d_vect = []
        self.norm_uvect = []
        self.pair_y_rot = []
        for (ID0, ID1) in self.pairs:
            # General basic paremeters
            l0 = self.element_pos[ID0]
            l1 = self.element_pos[ID1]

            # compute vectorized distance between pairs
            d_vect = l1 - l0
            self.d_vect.append(d_vect)

            # absolute distance between each pair
            self.d.append(np.linalg.norm(l0 - l1))

            # determine center of mass for each pair
            self.COM.append(l0 + (l1 - l0) / 2)

            # Get nNormal for each pair
            norm_vect = np.array([[-d_vect[2], 0, d_vect[0]]])
            norm_uvect = norm_vect / np.linalg.norm(norm_vect)
            self.norm_uvect.append(norm_uvect)

            # Get y_based rotation
            abs_y_rot = np.arccos(np.dot(norm_vect[DIM1], K_HAT[DIM1]) / np.linalg.norm(norm_vect))
            if (norm_uvect[DIM1, 0] < 0):
                y_rot = -abs_y_rot
            else:
                y_rot = abs_y_rot

            self.pair_y_rot.append(y_rot)

    def compute_D1minusD2(self, Dx):
        self.ddoa = []
        for (ID_a, ID_b) in self.pairs:
            ddoa = Dx[ID_a] - Dx[ID_b]
            (self.ddoa).append(ddoa)

    def compute_ab_coefficients(self):
        n_pairs = len(self.pairs)

        i = 0
        self.ab = []
        for i in range(n_pairs):
            ab = dd_to_hyperboloid_coe(self.ddoa[i], self.d[i])
            (self.ab).append(ab)

    def bulk_compute_ab_from_distances(self, Dx):
        self.compute_D1minusD2(Dx)
        self.compute_ab_coefficients()

    def get_direction(self, doa):
        """
        Takes a list of distances of arrival (doa) values corresponding to each
        hydrophone element and uses
        such information to generate a pinger location
        """
        self.bulk_compute_ab_from_distances(doa)
        # ^^ Updates self.ddoa and self.ab

        self.last_known_pinger_direction = 0

    def re_build(self, locations):
        self.__init__(locations)

    def refresh_data(self):
        pass

    def print_drawing(self):
        pass


class Hydrophones(Phys_Obj):

    def __init__(self):
        super(Hydrophones, self).__init__()

# ##################################
############# Functions ##########
##################################

def generate_yaw_array_definition(d):
    coordinate_locations = np.array([[-d/2.0, 0, 0],[d/2.0, 0, 0]])
    return coordinate_locations


def dd_to_hyperboloid_coe(D1minusD2, element_spacing):
    d = element_spacing / 2

    # Get "a" coefficient
    a = D1minusD2 / 2

    #
    if (abs(a) > d):
        # Limit given the spacing of the hydrophone elements has been
        # exceed. To prevent error in the next step, we'll clip purposely
        # clip the signal
        a = d * (-1 * (a < 0) + 1 * (a >= 0))
        print("get_heading: Warning, Angle is Clipped at max/min value. "
              + "Pay attention to this a make sure you're not running into "
              + "spatial aliasing territory.")

    # get "b" coefficient
    b = np.sqrt(d**2 - a**2)
    return a, b
