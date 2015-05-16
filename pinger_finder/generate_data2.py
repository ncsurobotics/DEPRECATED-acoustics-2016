import numpy as np
import acoustics
from environment import hydrophones, tools3d, source 

def load_matplotlib():
    # Load modules
    print("Loading Matplotlib library...")
    import matplotlib
#    matplotlib.use('GTK')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    
    # Configure settings
    print("...done.")

    return plt

def plot_contour(contour_obj, ax):
    o = contour_obj
    ax.plot_wireframe(o.X, o.Y, o.Z, rstride=1, cstride=1, color=np.random.rand(3,1))
    
def plot_object(obj, ax):
    o = obj
    ax.scatter(o.X,o.Y,o.Z,c='y')
    
# ############################
##### World Class ###########
############################
class World(object):
    def __init__(self, ax=None):
        # Initialize axes and plotting object
        self.ax = ax
        
        # Initialize single objects
        self.env = tools3d.Environment()
        self.array =
        self.pinger =
        
        # Initialize grouped objects
        self.pinger_contour = 
        self.hydrophone = 
        
    
class Worldmember(object):
    
# ###########################
########## Main Program ####
###########################

def generate_pinger_location():
    # Initializing env, array, pinger, hydrophone objects
    # Init environment
    env = tools3d.Environment()
    
    # Init objects
    hlocs = np.mat([[-15e-3,0,(-15e-3)/2],[15e-3,0,(-15e-3)/2], [0,0,(15e-3)/2]])
    array = hydrophones.Array(hlocs)
    pinger = tools3d.Phys_Obj()
    
    

    # Plug pinger location in the evironment
    pinger_contour = []
    hydrophone = []
    for i in range(array.n_elements):
        pinger_contour.append(source.Pinger_Contour())
        hydrophone.append(tools3d.Phys_Obj())
    
    # Init Plotting Environment
    plt = load_matplotlib()
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.hold(True)
    ax.autoscale(False)
    
    # Set Plotting limits
    lim = 50
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_zlim(-lim, lim)
    
    # Move object to appropiate locations
    pinger.move(np.array([[20,40,-50]]))
    
    # show available objects on plot
    plot_object(pinger, ax)
    
    # Load Raw time data
    time_vals = acoustics.generate_arrival_times(env, array, pinger)
    print("Printing time vals vvv")
    print(time_vals)
    
    # plot something
    array.bulk_compute_ab_from_distances(time_vals*env.c)
    
    for idx in range(array.n_elements):
        ab = (array.ab[idx][0], array.ab[idx][1])
        pinger_contour[idx].coe_generate_contour(ab, idx, array)
    
        #pinger_contour.xform_rotate(np.array([[0,np.pi/3,0]]))
        plot_contour(pinger_contour[idx], ax)
        
        hydrophone[idx].move(hlocs[idx])
        plot_object(hydrophone[idx], ax)
    
    #pinger_counter2.move(array.COM[1])
    #pinger_contour2.coe_generate_contour(array.ab[1][0], array.ab[1][1])
    #plot_contour(pinger_contour2, ax)
    
    # 
    
    # Compute convert time data to pinger location
    # acoustics.process_times_for_pinger_loc(time_vals, array, env)
    
    # Plug pinger location in the evironment
    
    plt.show()
    
generate_pinger_location()
