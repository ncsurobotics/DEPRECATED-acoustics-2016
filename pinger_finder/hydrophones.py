import numpy as np
import itertools
from acoustics import Phys_Obj

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
        
        
        
    def re_build(self, locations):
        self.__init__(locations)
            
    def refresh_data(self):
        pass
        
    def print_drawing(self):
        pass