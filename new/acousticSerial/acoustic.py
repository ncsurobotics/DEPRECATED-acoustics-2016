#importing the picomodule
import pico_module as pm

#importing the fft/toa calc code
from fft import calcOrientation

#importing numpy
import numpy as np
import csv
import time


#import hub
import seawolf as sw
sw.loadConfig("../../../seawolf/conf/seawolf.conf");
sw.init("Acoustics : Main");


DB = True

#connecting to picotec 1 is db 0 is no db
pico = pm.pico_init(0)#1 if DB else 0)
pf = 22 * 10**3
#entering data loop
try:
  while True:
    #getting data and making frequency right
    dataO = pm.pico_get_data(pico)
    Fs = (1.0 / pm.pico_get_sample_interval()) * 10**9
    #transposing data and making numpy array
    data = np.array(zip(*dataO))
    yaw, pitch, good = calcOrientation(data, Fs, pf, DB)
    out="Yaw:%s Pitch:%s FS:%s" % (str(yaw), str(pitch), Fs)
    sw.var.set("Acoustics.Pitch", pitch)
    sw.var.set("Acoustics.Yaw", yaw)
    if DB and good:
      print "++++++++++++++++++++++++++++++++++"
      print out
      writeCSV(out, dataO)
      raw_input("press enter to get next data set")
    
    
#closing pico at end
finally:
  pm.pico_close(pico)
  

def writeCSV(fname, data):
  f = open(fname+str(time.time()) + ".csv", "w")
  csv.writer(f, delimeter = ',')
  wr.writerows(data)
  f.close()
  
