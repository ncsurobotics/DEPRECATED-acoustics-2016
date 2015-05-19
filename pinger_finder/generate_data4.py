from __future__ import division
import matplotlib
matplotlib.use('TKAgg')
import numpy as np
import acoustics
from environment import hydrophones, tools3d, source 
from matplotlib import animation
from mpl_toolkits.mplot3d.art3d import juggle_axes

# ############################
###### Global Parameters ####
############################
dt = 0.1 # Speed of time passage. units = sec/frame
HYDROPHONE_DEFAULT_LOCATIONS = np.array([
    [-15e-3,0,(-15e-3)/2],
    [ 15e-3,0,(-15e-3)/2], 
    [     0,0,(15e-3)/2]
])
PINGER_DEFAULT_LOCATION = np.array([[20,40,-50]])

# ############################
##### Init Functions ########
############################

def load_matplotlib():
    # Load modules
    print("Loading Matplotlib library...")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    
    
    # Configure settings
    print("...done.")

    return plt
    
def init_3D_plotting_view(ax):
    # Hold for multiple object plotting
    ax.hold(True)
    
    # Set Plotting limits
    lim = 50
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_zlim(-lim, lim)
    ax.autoscale(False)

# ############################
## Graphics Functions #######
############################

def plot_contour(contour_obj, ax):
    o = contour_obj
    contour = ax.plot_wireframe(o.X, o.Y, o.Z, rstride=1, cstride=1, color=np.random.rand(3,1))
    return contour
    
def plot_object(phys_obj, ax=None):
    """Takes an instance of the physical object class, and plots it's current
    X, Y, and Z values such that a matplotlib figure can update whatever group
    of particles in the figure that correspond to phys_obj. This function doesn't 
    return anything, rather it saves the particle data in <obj>.pdata. This 
    means that any time a matplotlib figure object needs data, just give it 
    <obj>.pdata.
    """
    o = phys_obj
    
    if (o.pdata == None) and (ax == None):
        raise SyntaxError(
        "Didn't supply an axis, but there is no particle data embedded in the "
        + "object to work off of. Please fix either issue.")
    
    if (o.pdata != None) and (ax == None):
        # the 3D way for doing <matplotlib_line>.set_data(...)
        o.pdata._offsets3d = juggle_axes(o.X, o.Y, o.Z, 'z')

    else:
        # initialize matplotlib figure entity, and update <obj>.pdata with
        # the returned particle data object.
        o.pdata = ax.scatter(o.X,o.Y,o.Z,c='y')
        
def plot_object2(phys_obj, ax=None):
    """Takes an instance of the physical object class, and plots it's current
    X, Y, and Z values such that a matplotlib figure can update whatever group
    of particles in the figure that correspond to phys_obj. This function doesn't 
    return anything, rather it saves the particle data in <obj>.pdata. This 
    means that any time a matplotlib figure object needs data, just give it 
    <obj>.pdata.
    """
    o = phys_obj
    
    if (o.pdata == None) and (ax == None):
        raise SyntaxError(
        "Didn't supply an axis, but there is no particle data embedded in the "
        + "object to work off of. Please fix either issue.")
    
    if (o.pdata != None) and (ax == None):
        # the 3D way for doing <matplotlib_line>.set_data(...)
        o.pdata._offsets3d = juggle_axes(o.X, o.Y, o.Z, 'z')

    else:
        # initialize matplotlib figure entity, and update <obj>.pdata with
        # the returned particle data object.
        o.pdata = ax.scatter(o.X,o.Y,o.Z,c='y')

    
# #############################
##### Time Functions #########
#############################
def pinger_path_function(t):
    """Creates a list of datapoints for hydrophone data.
    """
    def heaviside(x):
        return 0.5 * (np.sign(x) + 1)
        
    def arc(t, t0, t1, ampl, w, phase,offset):
        """computes values of a time domain sinusoid starting at offset/t0 and
        ending at t1
        """
        val = (ampl*(sin(w*(t-t0) - phase) - sin(-phase)) + offset) * (heaviside(t-t0)-heaviside(t-t1))
        return val
        
    base_array = PINGER_DEFAULT_LOCATION
        
    XYZ = (base_array + 
        2*(heaviside(t-1)-heaviside(t-6))
    )
    
    return XYZ

    
# ############################
##### World Class ###########
############################
class World(object):
    # Initialize single objects
    env = tools3d.Environment()
    pinger = tools3d.Phys_Obj()
    array = hydrophones.Array()
    array.define(HYDROPHONE_DEFAULT_LOCATIONS)
    
    # Initialize grouped objects
    pinger_contour = []
    for i in range(array.n_elements):
        pinger_contour.append(source.Pinger_Contour())
        
    
    
    def __init__(self, ax=None):
        # Initialize axes and plotting object
        self.ax = ax
        self.hlocs = self.array.element_pos
        self.reset_objects()
        
        
    def reset_objects(self):
        # Move pinger to some place in the world
        self.pinger.move(PINGER_DEFAULT_LOCATION)
        

    def update_pinger_measurement(self):
        pass

        # plot something
        pass
            
    def init_animation(self):
        # Get objects plotted
        plot_object(self.array.hydrophones, self.ax)
        plot_object(self.pinger, self.ax)
        
        # Return line 
        return self.array.hydrophones.pdata
        #return self.pinger.pdata
    
    def update_animation(self, i):
        # Generate new location
        plot_object(self.array.hydrophones)
        
        self.pinger.move(pinger_path_function(i*dt))
        plot_object(self.pinger, self.ax)
        
        return self.array.hydrophones.pdata
        #return self.pinger.pdata
        
        
    
class Worldmember(object):
    pass
    
# ###########################
########## Main Program ####
###########################

def simulate_pinger_location():
    # Initializing graphics backend
    plt = load_matplotlib()
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    init_3D_plotting_view(ax)
    
    # Initializing world
    world = World(ax)
    
    ani = animation.FuncAnimation(fig, world.update_animation,
        init_func=world.init_animation,
        interval=5, frames=100)
    plt.show()
    
simulate_pinger_location()
