import numpy as np
import acoustics
import hydrophones

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
    ax.plot_wireframe(o.X, o.Y, o.Z, rstride=2, cstride=2)
    
def plot_object(obj, ax):
    o = obj
    ax.scatter(o.X,o.Y,o.Z,c='y')


def generate_pinger_location():
    # Init environment
    env = acoustics.Environment()
    
    # Init objects
    hlocs = np.mat([[-15e-3,0,(-15e-3)/2],[15e-3,0,(-15e-3)/2], [0,15e-3,(15e-3)/2]])
    array = hydrophones.Array(hlocs)
    pinger = acoustics.Phys_Obj()
    

    # Plug pinger location in the evironment
    pinger_contour = acoustics.Pinger_Contour()
    pinger_contour2 = acoustics.Pinger_Contour()
    plt = load_matplotlib()
    
    # Init Plotting Environment
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
    pinger.move(np.array([[5,40,-10]]))
    
    # show available objects on plot
    plot_object(pinger, ax)
    
    # Load Raw time data
    time_vals = acoustics.generate_arrival_times(env, array, pinger)
    print("Printing time vals vvv")
    print(time_vals)
    
    # plot something
    array.bulk_compute_ab_from_distances(time_vals*env.c)
    idx = 0
    ab = (array.ab[idx][0], array.ab[idx][1])
    pinger_contour.coe_generate_contour(ab, idx, array)
    
    #pinger_contour.xform_rotate(np.array([[0,np.pi/3,0]]))
    plot_contour(pinger_contour, ax)
    
    #pinger_counter2.move(array.COM[1])
    #pinger_contour2.coe_generate_contour(array.ab[1][0], array.ab[1][1])
    #plot_contour(pinger_contour2, ax)
    
    # 
    
    # Compute convert time data to pinger location
    # acoustics.process_times_for_pinger_loc(time_vals, array, env)
    
    # Plug pinger location in the evironment
    
    plt.show()
    
generate_pinger_location()
