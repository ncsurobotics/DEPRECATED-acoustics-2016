import numpy as np
import acoustics
import hydrophones


def generate_pinger_location():
    # Init environment
    env = acoustics.Environment()
    
    # Init objects
    hlocs = np.mat([[-15e-3,0,0],[15e-3,0,0], [0,15e-3,0]])
    array = hydrophones.Array(hlocs)
    pinger = acoustics.Phys_Obj()
    
    # Move object to appropiate locations
    pinger.move(np.array([[1,10,5]]))
    
    # Load Raw time data
    time_vals = acoustics.generate_arrival_times(env, array, pinger)
    print time_vals
    
    # Compute convert time data to pinger location
    
    # Plug pinger location in the evironment