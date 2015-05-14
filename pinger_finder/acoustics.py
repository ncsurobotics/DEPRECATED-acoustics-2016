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
        
    def move(self, coordinates):
        if coordinates.size != 3:
            print("acoustics: 3 dimensional coordinates please!")
            return None
            
        self.position = coordinates
    
    def rotate(self, new_normal_vector):
        self.orientation = new_normal_vector
        self.position = coordinates
        
def generate_arrival_times(env,array,pinger):
    n = array.n_elements
    dist = []
    for el in range(n):
        element_position = array.position+array.element_pos[el]
        dist.append( np.linalg.norm(pinger.position - element_position) )
    
    times = np.array(dist)/env.c
    
    return times - np.amin(times)
        
    