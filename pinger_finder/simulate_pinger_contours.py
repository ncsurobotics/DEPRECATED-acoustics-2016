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
PINGER_DEFAULT_LOCATION = np.array([[0,60,-50]])

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
    #contour = ax.plot_wireframe(o.X, o.Y, o.Z, rstride=1, cstride=1, color=np.random.rand(3,1))
    contour = ax.plot_wireframe(o.X, o.Y, o.Z, rstride=1, cstride=1)
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
        
def generate_contours(env, array, pinger, pinger_contour, ax):
    # Measure channel length for each hydrophone
    time_vals = generate_arrival_times(env, array, pinger)
    
    # plot something
    array.bulk_compute_ab_from_distances(time_vals*env.c)
    
    for idx in range(array.n_elements):
            ab = (array.ab[idx][0], array.ab[idx][1])
            pinger_contour[idx].coe_generate_contour(ab, idx, array)
            
            plot_contour(pinger_contour[idx], ax)
    
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
        val = (ampl*(np.sin(w*(t-t0) - phase) - np.sin(-phase)) + offset) * (heaviside(t-t0)-heaviside(t-t1))
        return val
        
    base_array = PINGER_DEFAULT_LOCATION
        
    XYZ = base_array + np.array([[
        arc(t,1,8,25,2,0,0),
        0,
        arc(t,1,8,25,1,np.pi/2,0)
    ]])
    
    return XYZ

def generate_arrival_times(env,array,pinger):
    n = array.n_elements
    dist = []
    for el in range(n):
        element_position = array.position+array.element_pos[el]
        dist.append( np.linalg.norm(pinger.position - element_position) )
    
    times = np.array(dist)/env.c
    
    return times - np.amin(times)


        
def process_times_for_pinger_loc(time_vals, array, env):
    xyz = None
    
    # Make distance
    dists = time_vals*env.c
    
    # Generate a and b coefficients
    # amongst every pair of hydrophones
    array.bulk_compute_ab_from_distances(dists)
    
    # solve either with linear lines or hyperbolas

    return xyz
    
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
        self.ax.cla()
        
        # Plot Hydrophones
        plot_object(self.array.hydrophones, self.ax)
        
        # Plot (moving) pinger
        self.pinger.move(pinger_path_function(i*dt))
        plot_object(self.pinger, self.ax)
        
        # Compute times
        generate_contours(self.env, self.array, self.pinger, self.pinger_contour, self.ax)
            
        # Set Plotting limits
        lim = 50
        self.ax.set_xlim(-lim, lim)
        self.ax.set_ylim(-lim, lim)
        self.ax.set_zlim(-lim, lim)
        
        # Print for analytical purposes
        if i == 50:
            print("Printing data")
            with open("./saved_data/ArrayData.txt", 'w') as f:
                f.write("For contour #1\n")
                print_like_nparray(f,self.pinger_contour[0].X)
                f.write("\n\n")
                print_like_nparray(f,self.pinger_contour[0].Y)
                f.write("\n\n")
                print_like_nparray(f,self.pinger_contour[0].Z)
                
                f.write("\n\n")
                f.write("For contour #2\n")
                print_like_nparray(f,self.pinger_contour[1].X)
                f.write("\n\n")
                print_like_nparray(f,self.pinger_contour[1].Y)
                f.write("\n\n")
                print_like_nparray(f,self.pinger_contour[1].Z)
                
                f.write("\n\n")
                f.write("For contour #3\n")
                print_like_nparray(f,self.pinger_contour[2].X)
                f.write("\n\n")
                print_like_nparray(f,self.pinger_contour[2].Y)
                f.write("\n\n")
                print_like_nparray(f,self.pinger_contour[2].Z)
                
                
                
     
        return (self.array.hydrophones.pdata, self.pinger.pdata)
        #return self.pinger.pdata
        
        
def print_like_nparray(f, data):
    shape = data.shape
    f.write('[')
    for r in range(shape[0]):
        f.write('[') 
        
        for c in range(shape[1]):
            f.write('%.3f' % data[r,c])
            if c < (shape[1]-1):
                f.write(', ')
            else:
                f.write(']')
            
        if r < (shape[0]-1):
            f.write(',\n')
        else:
            f.write(']')
                

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
        interval=100, frames=100)
    plt.show()
    
simulate_pinger_location()
