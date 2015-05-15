import numpy as np
import itertools
from acoustics import Phys_Obj

def dd_to_hyperboloid_coe(D1minusD2, element_spacing):
    d = element_spacing/2
    
    # Get "a" coefficient
    a = D1minusD2/2
    
    #
    if (a > d):
        # Limit given the spacing of the hydrophone elements has been
        # exceed. To prevent error in the next step, we'll clip purposely
        # clip the signal
        a = d
        print("get_heading: Warning, Angle is Clipped at max/min value.")
        
    # get "b" coefficient
    b = np.sqrt(d**2 - a**2)
    return a,b
    

class Array(Phys_Obj):
    def __init__(self, locations):
        super(Array, self).__init__()

        # Generate immediate parameters
        self.n_elements = locations.shape[0]
        
        # Make a list of all relative hydrophone locations
        self.element_pos = locations
        
        # Enumerate all pair combinations
        self.pairs = [ID for ID in 
            itertools.combinations(range(self.n_elements), 2)]

        print(self.pairs)
        

        # compute pair properties
        self.d = []
        self.COM = []
        for (ID0,ID1) in self.pairs:
            # General basic paremeters
            l0 = self.element_pos[ID0]
            l1 = self.element_pos[ID1]
            
            # distance between each pair
            self.d.append( np.linalg.norm(l0 - l1) )
            
            # determine center of mass for each pair
            self.COM.append(l0+(l1-l0)/2)
            
    
    def compute_D1minusD2(self, Dx):
        self.ddoa = []
        for (ID0,ID1) in self.pairs:
            ddoa = Dx[ID0] - Dx[ID1]
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
        
    def re_build(self, locations):
        self.__init__(locations)
            
    def refresh_data(self):
        pass
        
    def print_drawing(self):
        pass