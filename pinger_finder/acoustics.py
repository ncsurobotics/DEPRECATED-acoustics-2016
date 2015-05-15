from sys import argv

from bbb.ADC import ADS7865
from bbb.LTC1564 import LTC1564
import locate_pinger
import numpy as np
import quickplot

from os import path
LOG_DIR = path.join(path.dirname(path.realpath(__file__)), "saved_data/")

def load_matplotlib():
    print("Loading Matplotlib library...")
    import matplotlib

    matplotlib.use('GTK')

    import matplotlib.pyplot as plt

    plt.ion()
    plt.hold(False)
    plt.close()
    print("...done.")

    return plt


class Acoustics():

    def __init__(self):
        self.adc = ADS7865()
        self.filt = LTC1564()
        self.plt = None
        
    def close(self):
        self.adc.unready()
        
    def preset(self, sel):
        """configures electronics quickly based on the
        sel (int) that the uses supplies. See ADC.py's 
        very own preset function for a more detailed
        description of each preset."""
        if sel == 0:
            self.adc.preset(0)
            self.filt.gain_mode(0)

        elif sel == 100:
            self.adc.preset(100)
            self.filt.gain_mode(15)

        elif sel == 101:
            self.adc.preset(101)
            self.filt.gain_mode(0)

    def compute_pinger_direction(self):
        val = locate_pinger.main(self.adc, dearm=False)
        Vpp = np.amax(self.adc.y[0]) - np.amin(self.adc.y[0])
        print("The that last signal was %.2f Vpp" % Vpp)
        
        if val==None:
            return None
        else:
            return val
    
    def plot_recent(self):
        if self.plt==None:
            self.plt = load_matplotlib()
        
        quickplot.main(self.adc, self.plt, recent=True)
        
class Logging():
    def __init__(self):
        pass
        
    def logit(self, acoustics):
        # Create filename for log
        filename = raw_input("Logging: Give me a name for this data:")
        txtfn = path.join(LOG_DIR, filename+".txt")
        csvfn = path.join(LOG_DIR, filename+".csv")
        
        # Create file for log to write to
        with open(txtfn, 'w') as f:
        
            # dump data in file
            #f.write(acoustics.adc.adc_status())
            f.write(str(acoustics.adc.y))
        
        print("Data saved to %s" % txtfn)
        
    def close(self):
        self.adc.unready()

class Environment():
    def __init__(self):
        self.c = 1473 # m/s. The speed of sound in water. 
        
class Phys_Obj(object):
    all_objects = []
    
    def __init__(self):
        self.position = np.array([[0,0,0]])
        self.orientation = None
        Phys_Obj.all_objects.append(self)
        
        self.X = 0
        self.Y = 0
        self.Z = 0
        
    def move(self, coordinates):
        if coordinates.size != 3:
            print("acoustics: 3 dimensional coordinates please!")
            return None
            
        self.position = coordinates

        self.X = coordinates[0,0]
        self.Y = coordinates[0,1]
        self.Z = coordinates[0,2]
        
    def xform_translate(self, shift_vals):
        if shift_vals.size != 3:
            print("acoustics: 3 dimensional coordinates please!")
            return None
            
        new_position = shift_vals + self.position
        self.move(new_position)



    def rotate(self, new_normal_vector):
        self.orientation = new_normal_vector
        self.position = coordinates
        
    def xform_translate(self, shift_values):
        new_location = self.position + shift_values
        self.move(new_location)
        
    def xform_rotate(self, rot_values):
        rot_x = rot_values[0,0]
        rot_y = rot_values[0,1]
        rot_z = rot_values[0,2]
        
        mat_xrot = np.array([[1,0,0],
            [0,np.cos(rot_x),-np.sin(rot_x)],
            [0,np.sin(rot_x),np.cos(rot_x)]])
            
        mat_yrot = np.array([[np.cos(rot_y),0,np.sin(rot_y)],
            [0,1,0],
            [-np.sin(rot_y),0,np.cos(rot_y)]])
            
        mat_zrot = np.array([[np.cos(rot_z),-np.sin(rot_z),0],
            [np.sin(rot_z),np.cos(rot_z),0],
            [0,0,1]])
            
            
        # Do X axis rotation
        old_xyz = np.array([self.X, self.Y, self.Z])
        new_xyz = [0]*3
        for r in range(3):
            for c in range(3):
                new_xyz[r] = new_xyz[r] + mat_xrot[r][c]*old_xyz[c]
        
        self.X = new_xyz[0]
        self.Y = new_xyz[1]
        self.Z = new_xyz[2]
        
        # Do Y axis rotation
        old_xyz = np.array([self.X, self.Y, self.Z])
        new_xyz = [0]*3
        for r in range(3):
            for c in range(3):
                new_xyz[r] = new_xyz[r] + mat_yrot[r][c]*old_xyz[c]
        
        self.X = new_xyz[0]
        self.Y = new_xyz[1]
        self.Z = new_xyz[2]
        
        # Do Z axis rotation
        old_xyz = np.array([self.X, self.Y, self.Z])
        new_xyz = [0]*3
        for r in range(3):
            for c in range(3):
                new_xyz[r] = new_xyz[r] + mat_zrot[r][c]*old_xyz[c]
        
        self.X = new_xyz[0]
        self.Y = new_xyz[1]
        self.Z = new_xyz[2]
        
class Pinger_Contour(Phys_Obj):
    def __init__(self):
        super(Pinger_Contour, self).__init__()
        
        self.X = None
        self.Y = None
        self.Z = None
        
        self.max_distance = 50 # meters
        self.pts = 20 # data point
        
        
    def coe_generate_contour(self,ab, array_pair_idx, array):
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
        X = np.sqrt((2*a + (Z/b)**2 + (Y/b)**2))*a 
        
        # get "a" back
        a = temp
        
        # Save values to internal attributes
        if a < 0:
            self.X = -X
        else:
            self.X = X
        self.Y = Y
        self.Z = Z
        
        self.match_contour_to_pair(array_pair_idx, array)
        
    def match_contour_to_pair(self, array_pair_idx, array):
        # vector param
        import pdb; pdb.set_trace()
        j = 1;
        idx = array_pair_idx
        
        # Determine amount of rotation (y component rotation)
        p = -(array.COM[idx] - array.position)
        if P < 1e-6:
            y_rot
        P = np.linalg.norm(p)
        y_rot = np.arccos(p[j]/P)
        
        # Rotate accordingly
        self.xform_rotate(0,y_rot,0)
        
        # Move accordingly
        self.move(array.COM[idx])
        

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
    
    